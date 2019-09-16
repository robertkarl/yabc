#!/usr/bin/env python3

import setuptools

"""
Python versions and dependencies notes:

- dateutil for 3.4 doesn't have parser accessible on the package
- previously there was a circular import issue in our formats package. This
  failed on 3.4 (but worked on later versions)
- we need the typing dep since we need the backport for 3.4
"""

setuptools.setup(
    version="0.1.12",
    name="yabc",
    python_requires=">=3.4,<=3.8",
    author="Seattle Blockchain Solutions",
    maintainer="Robert Karl",
    maintainer_email="robertkarljr@gmail.com",
    install_requires=[
        "flask==1.0.4",  # flask 1.1. drops python3.4 support
        "sqlalchemy==1.3.3",
        "delorean==1.0.0",
        "python-dateutil",  # TODO: remove, we can just use delorean
        # This package is present on 3.5+, backport required for 3.4
        "typing",
    ],
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
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
