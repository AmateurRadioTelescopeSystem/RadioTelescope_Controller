#!/usr/bin/env bash

set -e  # Stop if any command fails

# Check if the configuration file exists
if [[ ! -f Core/GUI/resources.rcc ]]; then
    ./configure.sh
fi

chmod +x Core/RadioTelescopePC.py  # Change execution permissions for the file
Core/RadioTelescopePC.py  # Execute the main program file