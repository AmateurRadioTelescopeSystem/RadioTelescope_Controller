#!/usr/bin/env bash

set -e  # Stop when a command fails

# Temporary, will be  automatic once tests are complete
coverage run Tests/RunTests.py
coverage report -m
