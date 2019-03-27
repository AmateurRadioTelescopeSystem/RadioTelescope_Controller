#!/usr/bin/env bash

set -e  # Stop when a command fails

# Temporary, will be  automatic once tests are complete
python3 -m unittest Tests/test_integrated.py
find Tests/ -type f -iname "test_*.py" | xargs python3 -m unittest
