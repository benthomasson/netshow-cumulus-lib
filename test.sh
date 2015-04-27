#!/bin/bash

set -e

echo "starting up"

PATH=$WORKSPACE/venv/bin:/usr/local/bin:$PATH
if [ ! -d "venv" ]; then
        virtualenv venv
fi
. venv/bin/activate

pip install -r requirements_test.txt --download-cache=/tmp/$JOB_NAME
tox
