#!/usr/bin/env python3

import setuptools

setuptools.setup(
    version="0.0.2",
    name="yabc",
    python_requires="~=3.3",
    author="Robert Karl",
    install_requires=["flask", "dateutils"],
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
