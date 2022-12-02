#!/usr/bin/env python
# -*- coding: utf-8 -*-
import aioredis
import fastapi
from fastapi.middleware.cors import CORSMiddleware
import pydantic
import spacy
from os import getenv
from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import Session
from .model import *
from .nlp import *
from .orm import *

engine = create_engine(getenv('SQL_ENGINE', 'sqlite://'), future=True)
BaseOrm.metadata.create_all(engine)
nlp_model = spacy.load(getenv('SPACY_MODEL', 'en_core_web_sm'))

class Add(pydantic.BaseModel):
    text: str
    origin: str

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['POST'],
    allow_headers=['*'],
)

@app.get('/text/{hashsum}')
async def get_text(hashsum: str) -> str | None:
    with Session(engine) as session:
        for result in session.execute(
            select(TextOrm).where(TextOrm.hashsum == bytes.fromhex(hashsum))
        ).scalars():
            return result.text

@app.get('/search')
async def search(
    subject: str | None = None,
    predicate: str | None = None,
    obj: str | None = None,
) -> list[Triplet]:
    clauses = []
    if subject:
        clauses.append(TripletOrm.subject == subject)
    if predicate:
        clauses.append(TripletOrm.predicate == predicate)
    if obj:
        clauses.append(TripletOrm.obj == obj)

    results = []
    with Session(engine) as session:
        return [
            vars(result)
            for result in session.execute(
                select(TripletOrm).where(and_(*clauses))
            ).scalars()
        ]

@app.post('/')
async def add(request: Add) -> str:
    origin = IRIText(request.origin)
    hashsum: Hashsum

    with Session(engine) as session:
        for value in Doc.parse(nlp_model, request.text, origin):
            match value:
                case DocText():
                    hashsum = value.hashsum
                    orm = TextOrm(
                        text=value.text,
                        hashsum=value.hashsum.hashsum,
                    )
                case Text():
                    orm = TextOrm(
                        text=value.text,
                        hashsum=value.hashsum.hashsum,
                    )
                case Triplet():
                    orm = TripletOrm(**vars(value))
                case _:
                    continue
            session.merge(orm)
        session.commit()

    return str(hashsum.iri)
