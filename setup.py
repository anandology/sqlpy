#! /usr/bin/env python

from setuptools import setup

setup(
    name="sqlpy",
    version="0.1-dev",
    description="The database module of web.py",
    packages=["sqlpy", "sqlpy.engines"],
    platforms=["any"],
)
