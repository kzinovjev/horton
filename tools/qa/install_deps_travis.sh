#!/usr/bin/env bash

source tools/qa/common.sh

# This script assumes that a virtualenv is created, in which pip will then automatically
# install the dependencies.

# Packages with a long compile+install time are first wheeled, i.e. a binary package
# is made, which can be cached.

# Pip is called multiple times to have more regular output, which keeps travis happy.

pip install --upgrade pip
pip install wheel

pip install --upgrade pep8
pip install --upgrade pylint
pip install --upgrade coverage
pip install --upgrade pep257

pip wheel numpy
pip install --upgrade numpy

pip wheel cython
pip install --upgrade cython

pip wheel scipy
pip install --upgrade scipy

pip wheel h5py
pip install --upgrade h5py

pip wheel matplotlib
pip install --upgrade matplotlib

pip install --upgrade sphinx
pip install --upgrade breathe
