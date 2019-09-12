#!/usr/bin/env python3

import setuptools

"""

# we do not support python3.4 in master because 
- dateutil for 3.4 doesn't have parser accessible on the package
- we need the typing backport for 3.4
- circular import issue in our formats package fails on 3.4 (but works on later versions)
- possibly more issues
"""

setuptools.setup(
    version="0.1.11",
    name="yabc",
    python_requires=">=3.4,<=3.8",
    author="Seattle Blockchain Solutions",
    maintainer="Robert Karl",
    maintainer_email="robertkarljr@gmail.com",
    install_requires=[
        "flask==1.0.4",
        "sqlalchemy==1.3.3",
        "delorean==1.0.0",
        "python-dateutil", # TODO: remove, we can just use delorean
        "typing", # This backport is required for python3.4
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
