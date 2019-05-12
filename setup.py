#!/usr/bin/env python3

import setuptools

setuptools.setup(
    version="0.0.5",
    name="yabc",
    python_requires="~=3.5",
    author="Robert Karl",
    install_requires=["flask", "dateutils", "sqlalchemy"],
    test_suite="tests",
    description="Cost basis calculator for blockchain assets.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
