#!/usr/bin/env bash

echo -e "\e[1;32mPylava check is running\e[0m"

cd Core/
pylava -o ../ci/pylava.ini
