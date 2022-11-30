#!/usr/bin/env python
# -*- coding: utf-8 -*-
import aioredis
import fastapi
from fastapi.middleware.cors import CORSMiddleware
import pydantic
import spacy
import aioipfs
from .convert import CID, subject_path
from .worker import Worker

ipfs = aioipfs.AsyncIPFS(maddr='/ip4/127.0.0.1/tcp/5001')
nlp = spacy.load('en_core_web_sm')

worker = Worker(ipfs=ipfs, nlp=nlp)

class Request(pydantic.BaseModel):
    text: str
    origin: str

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['POST'],
    allow_headers=['*'],
)

@app.post('/')
async def add(request: Request) -> CID:
    values = [
        triplet
        async for triplet in worker.add_text(
            request.text,
            request.origin
        )
    ]

    subject_cid = values[0].split('/')[1]
    subject_root = (await ipfs.files.stat(subject_path(subject_cid)))['Hash']

    return {
        'text': subject_cid,
        'root': subject_root,
    }

    # async def text_tree(path):
    #     stat = await ipfs.files.stat(path)
    #     path_name = stat['Hash']

    #     if stat['Type'] != 'directory':
    #         return (await ipfs.files.read(path), None)
    #         # return name
    #     else:
    #         base_name = path.split('/')[-1]
    #         base_value = await ipfs.cat(base_name)
    #         t = {}
    #         results = (await ipfs.files.ls(path))['Entries']
    #         for f in results:
    #             name = f['Name']
    #             subpath = '/'.join((path, name))
    #             key, value = await text_tree(subpath)
    #             t[key] = value

    #         return (base_value, t)

    # async def cid_tree(path):
    #     stat = await ipfs.files.stat(path)
    #     path_name = stat['Hash']

    #     if stat['Type'] != 'directory':
    #         return (path_name, None)
    #         # return name
    #     else:
    #         base_name = path.split('/')[-1]
    #         t = {}
    #         results = (await ipfs.files.ls(path))['Entries']
    #         for f in results:
    #             name = f['Name']
    #             subpath = '/'.join((path, name))
    #             key, value = await cid_tree(subpath)
    #             t[name] = value

    #         return (base_name, t)

    # text_key, text_value = await text_tree(subject_path(subject_cid))
    # cid_key, cid_value = await cid_tree(subject_path(subject_cid))
    # return {
    #     'subject': {
    #         cid_key: cid_value,
    #     },
    # }
