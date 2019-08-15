#!/usr/bin/env python3

import setuptools

setuptools.setup(
    version="0.1.7",
    name="yabc",
    python_requires=">=3.5,<3.8",
    author="Seattle Blockchain Solutions",
    maintainer="Robert Karl",
    maintainer_email="robertkarljr@gmail.com",
    install_requires=["flask==1.0.2", "sqlalchemy", "delorean==1.0.0"],
    test_suite="tests",
    url="https://github.com/robertkarl/yabc",
    description="A tax estimator for cryptocurrencies.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
