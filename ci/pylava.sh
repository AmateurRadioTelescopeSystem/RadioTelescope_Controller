#!/usr/bin/env bash

echo -e "\033[0;34mPylava check is running\033[0m"

cd ../Core/
pylava -o ../ci/pylava.ini
