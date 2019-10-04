#! /usr/bin/env sh

# The nuclear option for code reformatting; processes every python file under
# src.  black for code formatting, isort for import sorting and autoflake to
# catch unused imports.

DIRS="src/ tests/ utils/ setup.py"
set -e

if [ "$1" != '--skip-tests' ]
then 
  PYTHONPATH=src python -m unittest discover -s tests
fi

autoflake -r -i --remove-all-unused-imports $DIRS
isort -rc $DIRS
black $DIRS
