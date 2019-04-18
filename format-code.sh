#! /usr/bin/env sh
set -e
autoflake -r -i --remove-all-unused-imports src/
isort -rc src/
black src/

