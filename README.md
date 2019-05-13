[![yabc on PyPI](https://img.shields.io/pypi/v/yabc.svg)](https://pypi.org/project/yabc/) ![MIT License badge](https://img.shields.io/badge/license-MIT-green.svg) [![yabc on TravisCI](https://travis-ci.org/robertkarl/yabc.svg?branch=master)](https://travis-ci.org/robertkarl/yabc)

# What's this?
Cost basis calculation library and HTTP API. Most useful for blockchain-backed
assets like bitcoin.

# Requirements and python deps
- python3.5+

pip packages:
- flask
- dateutil
- twine (for distribution only)

# Running
Running the api server in development mode from source:

```
virtualenv -p python3 venv
source ./venv/bin/activate
# Creating and activating a virtual environment above is optional and recommended
./setup.py install
make run
```

# Running the docker image
```
make build
make run_docker
```

# Notes
File structure inspired by source and test layout of python modules
[sshuttle](https://github.com/sshuttle/sshuttle) and
[flask](https://github.com/pallets/flask).
