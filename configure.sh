#!/usr/bin/env bash

set -e  # Stop if any command fails

chmod +x run.sh  # Change execution permissions for the file
pip3 install -r requirements.txt  # Install the necessary python packages

echo "Creating the resources file....."
rcc -binary Icons/GUI_Images/Image_Resources.qrc -o Core/GUI/resources.rcc  # Create the resources file
echo "Configuration done!! You are all set and you can use the main program!!"  # Show a success message
