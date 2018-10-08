#!/usr/bin/env bash

set -e  # Stop if any command fails

chmod +x Tests/program_tester.py  # Change execution permissions for the file
pyrcc5 Icons/GUI_Images/Image_Resources.qrc -o Core/GUI/resources.py  # Create the resources file
Tests/./program_tester.py  # Run the main program