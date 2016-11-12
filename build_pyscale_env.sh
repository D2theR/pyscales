#!/bin/bash

py_ver=3.4

sudo apt-get -y install libpq-dev python3-dev zbar-tools

virtualenv --python=python$py_ver $PWD

activate (){
	source ./bin/activate
	}

activate
pip install -r $PWD/requirements.txt
deactivate
echo Done and stuff