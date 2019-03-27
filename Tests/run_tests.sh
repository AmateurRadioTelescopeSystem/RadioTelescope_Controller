#!/usr/bin/env bash

set -e  # Stop when a command fails

# Temporary, will be  automatic once tests are complete
cd ..
python3 -m unittest Tests/test_astronomy.py
