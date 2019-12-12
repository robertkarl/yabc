#!/usr/bin/env python3

"""
Goodbye python3.4

https://discuss.python.org/t/python-download-stats-for-march-2019/1424

Usage statistics show that no single minor version X of 3.4.X has more than
.39%
"""

import setuptools

setuptools.setup(
    version="0.1.16",
    name="yabc",
    python_requires=">=3.5,<=3.8",
    author="Seattle Blockchain Solutions",
    maintainer="Robert Karl",
    maintainer_email="robertkarljr@gmail.com",
    install_requires=[
        "flask==1.1.1",
        "sqlalchemy==1.3.3",
        "delorean==1.0.0",
        "python-dateutil==2.8.0",  # TODO: remove, we can just use delorean
    ],
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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
