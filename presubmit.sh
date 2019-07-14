#! /usr/bin/env sh

# The nuclear option for code reformatting; processes every python file under
# src.  black for code formatting, isort for import sorting and autoflake to
# catch unused imports.

set -e
DIRS="src/ tests/ utils/ setup.py"
python setup.py test
autoflake -r -i --remove-all-unused-imports $DIRS
isort --thirdparty flask -rc $DIRS --skip src/yabc/__init__.py
black $DIRS
