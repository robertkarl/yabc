# What's this?
Cost basis calculation library and HTTP API. Most useful for blockchain-backed
assets like bitcoin.

# Requirements and python deps
python3 is required. Flask is required for running the HTTP endpoints. Basis
calculation code uses dateutil.


# Running the code
Running and testing the api server in development mode from source:

```
virtualenv -p python3 venv
source ./venv/bin/activate
# Creating and activating a virtual environment above is optional and recommended
./setup.py install
python -m yabc_api.yabc_api
```

# Running the docker image
```
make build
make run
```

# Notes
File structure inspired by source and test layout of python modules sshuttle and flask.

# Distributing
```
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
```
