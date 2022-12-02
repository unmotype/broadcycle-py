#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Iterable
from .model import *

__all__ = ('Token', 'Doc', 'DocText', 'Sentence', 'Word')

@dataclass(frozen=True)
class Number(Noun):
    n: int

    @property
    def iri(self) -> str:
        return f'number:{self.n}'

@dataclass(frozen=True)
class IndexPredicate(Predicate):
    of: IRI

    @property
    def iri(self) -> str:
        return f'start-of:{self.of}'

class OriginPredicate(Predicate):
    iri: str = 'originates-from'

class ContainsSentence(Predicate):
    iri: str = 'contains-sentence'

class ContainsWord(Predicate):
    iri: str = 'contains-word'

class Token: ...

class DocText(Text): ...

class Doc(Token):
    @classmethod
    def parse(cls, nlp_model, text: str, origin: IRI) -> Iterable[Text | Triplet]:
        text_model = DocText.generate(text)
        yield text_model

        doc = nlp_model(text)

        yield Triplet(
            subject=text_model.iri,
            predicate=OriginPredicate(),
            obj=origin,
        )

        for sentence in doc.sents:
            yield from Sentence.parse(text_model.iri, sentence)

class Sentence(Token):
    @classmethod
    def parse(cls, doc_iri: IRI, sentence) -> Iterable[Text | Triplet]:
        text_model = Text.generate(sentence.text)
        yield text_model

        yield Triplet(
            subject=doc_iri,
            predicate=ContainsSentence(),
            obj=text_model.iri,
        )

        yield Triplet(
            subject=doc_iri,
            predicate=IndexPredicate(text_model.iri),
            obj=Number(sentence.start)
        )

        for ent in sentence.subtree:
            if ent.dep_ in ('punct',):
                continue
            yield from Word.parse(doc_iri, ent)

class Word(Token):
    @classmethod
    def parse(cls, doc_iri: IRI, word) -> Iterable[Text | Triplet]:
        text_model = Text.generate(word.text)
        yield text_model

        yield Triplet(
            subject=doc_iri,
            predicate=ContainsWord(),
            obj=text_model.iri,
        )

        yield Triplet(
            subject=doc_iri,
            predicate=IndexPredicate(text_model.iri),
            obj=Number(word.idx)
        )
