#!/usr/bin/env python3

import setuptools

setuptools.setup(
    version="0.1.1",
    name="yabc",
    python_requires=">=3.5,<3.8",
    author="Seattle Blockchain Solutions",
    install_requires=["flask==1.0.2", "sqlalchemy", "delorean==1.0.0"],
    test_suite="tests",
    description="A tax estimator for cryptocurrencies.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
