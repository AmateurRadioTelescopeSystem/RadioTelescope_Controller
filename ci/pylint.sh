#!/usr/bin/env bash

cd Core/
find . -iname "*.py" | xargs pylint --exit-zero