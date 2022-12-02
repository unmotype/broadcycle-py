#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='broadcycle',
    version='0.0.1',
    install_requires=[
        'sqlalchemy',
        'aioredis',
        'async-timeout<4.0,>=3.0',
        'fastapi',
        'spacy',
    ],
)
