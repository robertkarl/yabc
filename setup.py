#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    version="0.0.1",
    name="yabc",
    python_requires='~=3.3',
    author="Robert Karl",
    install_requires=["flask", "dateutils"],
    test_suite="tests",
    description="Cost basis calculator for blockchain assets.",
    long_description=open("README.md").read(),
)
