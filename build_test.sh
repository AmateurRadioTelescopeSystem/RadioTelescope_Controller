#!/usr/bin/env bash

set -e  # Stop if any command fails

chmod +x Tests/program_tester.py  # Change execution permissions for the file
Tests/IntegratedRun.py  # Run the main program