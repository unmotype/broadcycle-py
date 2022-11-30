#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = (
    'CID',
    'IRI',
    'Triplet',
    'make_cid_uri',
    'make_full_predicate',
    'make_triple',
    'make_predicate',
    'make_number_iri',
    'make_index_predicate',
    'make_origin_predicate',
    'subject_path',
    'full_predicate_path',
    'obj_path',
)

CID = type[str]
IRI = type[str]
Triplet = tuple[CID, IRI, CID]

def make_cid_uri(cid: CID) -> IRI:
    return f'ipfs://{cid}'

def make_iri_ref(iri: IRI) -> IRI:
    return f'<{iri}>'

def make_full_predicate(subject_cid: CID, predicate: IRI) -> str:
    return ' '.join((
        make_iri_ref(make_cid_uri(subject_cid)),
        make_iri_ref(predicate)
    ))

def make_triple(subject_cid: CID, predicate: IRI, obj_cid: CID) -> str:
    return ' '.join((
        make_iri_ref(make_cid_uri(subject_cid)),
        make_iri_ref(predicate),
        make_iri_ref(make_cid_uri(obj_cid)),
        '.'
    ))

def make_predicate(predicate: str) -> IRI:
    return predicate

def make_number_iri(n: int) -> IRI:
    return f'number:{n}'

def make_index_predicate(iri: IRI) -> IRI:
    return f'start-of:{iri}'

def make_origin_predicate() -> IRI:
    return 'originates-from'

def subject_path(subject_cid: CID) -> str:
    return f'/{subject_cid}'

def full_predicate_path(subject_cid: CID, predicate_cid: CID) -> str:
    return '/'.join((
        subject_path(subject_cid),
        predicate_cid,
    ))

def obj_path(subject_cid: CID, predicate_cid: CID, obj_cid: CID) -> str:
    return '/'.join((
        full_predicate_path(subject_cid, predicate_cid),
        obj_cid
    ))
