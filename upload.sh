#!/bin/bash

git clean -xdf
# Switch to the correct directory
if [ ! -f setup.py ]; then
  cd `dirname $0`
fi

set -e

echo "starting up"
GIT_BRANCH=test
PATH=$WORKSPACE/venv/bin:/usr/local/bin:$PATH
if [ ! -d "venv" ]; then
        virtualenv venv
fi
. venv/bin/activate

# install test requirements like tox
pip install --upgrade -r requirements_develop.txt
python setup.py bdist_wheel sdist upload -r testing
