#!/bin/bash -ex

export PYTHONUNBUFFERED=1

export PYNEST_AUTH_FILE='data/auth.yml'

export PYNEST_DB_NAME='pynest'
export PYNEST_DB_USER='pynest'
export PYNEST_DB_PASS='flats44'
export PYNEST_DB_HOST='localhost'

exec /usr/bin/python /opt/pynest/pynest.py

