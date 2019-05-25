#! /usr/bin/env sh

# The nuclear option for code reformatting; processes every python file under
# src.  black for code formatting, isort for import sorting and autoflake to
# catch unused imports.

set -e
python setup.py test
autoflake -r -i --remove-all-unused-imports src/ tests/
isort -rc src/ tests/ --skip src/yabc/__init__.py
black src/ tests/ ./setup.py
