#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import aioipfs
import spacy
from dataclasses import dataclass
from typing import AsyncIterable
from .convert import *

@dataclass(frozen=True)
class Worker:
    ipfs: aioipfs.AsyncIPFS
    nlp: spacy.Language

    async def _mkdir(self, path: str, ignore_existing: bool = True, **kwargs):
        if ignore_existing:
            try:
                return await self.ipfs.files.mkdir(path)
            except aioipfs.APIError as e:
                if e.message != 'file already exists':
                    raise e
        else:
            return await self.ipfs.files.mkdir(path, **kwargs)

    async def _add_str(self, text: str, **kwargs) -> CID:
        return (await self.ipfs.core.add_str(text, **kwargs))['Hash']

    async def add_triplet(
        self,
        subject_cid: CID,
        predicate: IRI,
        obj: str
    ) -> Triplet:
        predicate_cid, obj_cid = await asyncio.gather(
            self._add_str(predicate),
            self._add_str(obj),
        )

        path = obj_path(
            subject_cid,
            predicate_cid,
            obj_cid,
        )

        # print(f'''mkdir {full_predicate_path(
        #     subject_cid,
        #     predicate_cid,
        # )}''')
        await self._mkdir(full_predicate_path(
            subject_cid,
            predicate_cid,
        ))

        await self.ipfs.files.write(path, obj.encode('utf-8'), create=True)

        return path

    async def add_text(self, text: str, origin: IRI) -> AsyncIterable[Triplet]:
        cid_task = asyncio.create_task(self._add_str(text))
        doc = self.nlp(text)
        subject_cid = await cid_task 

        # print(f'mkdir {subject_path(subject_cid)}')
        await self._mkdir(subject_path(subject_cid))

        yield (await self.add_triplet(
            subject_cid,
            make_origin_predicate(),
            origin,
        ))
        for sentence in doc.sents:
            predicate = make_predicate('contains-sentence')
            triplet, obj_cid = await asyncio.gather(
                self.add_triplet(
                    subject_cid,
                    predicate,
                    sentence.text,
                ),
                self._add_str(sentence.text),
            )
            yield triplet

            yield (await self.add_triplet(
                subject_cid,
                make_index_predicate(obj_cid),
                make_number_iri(sentence.start),
            ))
            for ent in sentence.subtree:
                if ent.dep_ in ('punct',):
                    continue
                predicate = make_predicate(f'contains-word')
                triplet, obj_cid = await asyncio.gather(
                    self.add_triplet(
                        subject_cid,
                        predicate,
                        ent.text,
                    ),
                    self._add_str(ent.text),
                )
                yield triplet

                yield (await self.add_triplet(
                    subject_cid,
                    make_index_predicate(make_cid_uri(obj_cid)),
                    make_number_iri(ent.idx),
                ))
