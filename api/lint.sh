#!/usr/bin/env bash

set -x

autoflake app
isort app
black app

autoflake tests
isort tests
black tests

vulture
