#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pydantic import BaseModel, validator
import hashlib
from dataclasses import dataclass
from typing import Any

__all__ = (
    'IRI',
    'IRIText',
    'Noun',
    'Subject',
    'Predicate',
    'Object',
    'Hashsum',
    'Text',
    'Triplet',
)

class IRI:
    iri: str

    def __str__(self):
        return f'<{self.iri}>'

    @classmethod
    def parse_iri(cls, text: str) -> str:
        if text[0] != '<' or text[-1] != '>':
            raise ValueError(text)
        return text[1:-1]

@dataclass(frozen=True)
class IRIText(IRI):
    iri: str

    @classmethod
    def parse(cls, text: str) -> 'IRI':
        return cls(cls.parse_iri(text))

class Noun(IRI): ...
class Subject(Noun): ...
class Predicate(IRI): ...
class Object(Noun): ...

@dataclass(frozen=True)
class Hashsum(IRI):
    hashsum: bytes

    @property
    def iri(self) -> str:
        return f'sha256:{self.hashsum.hex()}'

    @classmethod
    def generate_hashsum(cls, text: str, encoding: str = 'utf-8') -> bytes:
        return hashlib.sha256(text.encode(encoding)).digest()

    @classmethod
    def generate(cls, text: str, **kwargs) -> 'Hashsum':
        return cls(cls.generate_hashsum(text, **kwargs))

class Text(BaseModel):
    text: str
    hashsum: Hashsum

    @property
    def iri(self) -> Hashsum:
        return self.hashsum

    @classmethod
    def generate(cls, text: str) -> 'Text':
        return cls(text=text, hashsum=Hashsum.generate(text))

    class Config:
        orm_mode = True

class Triplet(BaseModel):
    subject: Any # Subject
    predicate: Any # Predicate
    obj: Any # Object

    class Config:
        orm_mode = True

    @validator('subject')
    def validate_subject(cls, subject: IRI) -> str:
        if isinstance(subject, IRI):
            return subject.iri
        raise TypeError(subject)

    @validator('predicate')
    def validate_predicate(cls, predicate: IRI) -> str:
        if isinstance(predicate, IRI):
            return predicate.iri
        raise TypeError(predicate)

    @validator('obj')
    def validate_obj(cls, obj: IRI) -> str:
        if isinstance(obj, IRI):
            return obj.iri
        raise TypeError(obj)
