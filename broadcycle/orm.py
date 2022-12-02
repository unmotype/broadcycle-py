#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, LargeBinary, String, ForeignKey, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

__all__ = ('BaseOrm', 'TextOrm', 'TripletOrm')

BaseOrm = declarative_base()

class TextOrm(BaseOrm):
    __tablename__ = 'texts'

    hashsum = Column(LargeBinary(32), primary_key=True)
    text = Column(String(), nullable=False) # ignore unique constraint to save time

class TripletOrm(BaseOrm):
    __tablename__ = 'triplets'

    subject = Column(String, nullable=False)
    predicate = Column(String, nullable=False)
    obj = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('subject', 'predicate', 'obj'),
        PrimaryKeyConstraint('subject', 'predicate', 'obj'),
    )

