#!/usr/bin/env python3

import os
import sys
import yaml
import logging
import logging.config
sys.path.append(os.path.abspath('.'))  # noqa

import Tests.DefaultData


def parse_files():
    # Create the directory for the log files if it does not exist already
    try:
        if not os.path.exists(os.path.abspath('Tests/logs')):
            os.makedirs(os.path.abspath('Tests/logs'))
        if not os.path.exists(os.path.abspath('Tests/Settings')):
            os.makedirs(os.path.abspath('Tests/Settings'))
        if not os.path.exists(os.path.abspath('TLE')):
            os.makedirs(os.path.abspath('TLE'))  # Make the TLE saving directory
        if not os.path.exists('Tests/Astronomy Database'):
            os.makedirs('Tests/Astronomy Database')
    except Exception as excep:
        print("There is a problem with the log directory. See tracback: \n%s" % excep, file=sys.stderr)
        sys.exit(-1)  # Exit the program if an error occurred

    # Check if the logging configuration file exists
    try:
        if not os.path.exists(os.path.abspath('Tests/Settings/logging_settings.yaml')):
            print("Logging configuration file not found. Creating the default.\n", file=sys.stderr)
            log_file = open(os.path.abspath('Tests/Settings/logging_settings.yaml'), "w+")  # Open file in writing mode
            log_file.write(Tests.DefaultData.log_config_str)  # Write the default dat to the file
            log_file.close()  # Close the file, since no other operation required
    except Exception as excep:
        print("There is a problem creating the configuration file. See tracback: \n%s" % excep, file=sys.stderr)
        sys.exit(-1)  # Exit the program if an error occurred

    # Check if the settings XML file exists
    try:
        if not os.path.exists(os.path.abspath('Tests/Settings/settings.xml')):
            print("Settings file not found. Creating the default.\n", file=sys.stderr)
            settings_file = open(os.path.abspath('Tests/Settings/settings.xml'),
                                 "w+")  # Open the settings file in writing mode
            settings_file.write(Tests.DefaultData.settings_xml_str)  # Write the default dat to the file
            settings_file.close()  # Close the file, since no other operation required
    except Exception as excep:
        print("There is a problem creating the settings file. See tracback: \n%s" % excep, file=sys.stderr)
        sys.exit(-1)  # Exit the program if an error occurred

    # Open the configuration and apply it on the logging module
    with open(os.path.abspath('Tests/Settings/logging_settings.yaml')) as config_file:
        dictionary = yaml.safe_load(config_file)  # Load the dictionary configuration
        logging.config.dictConfig(dictionary['Logging'])  # Select the logging settings from the dictionary


if __name__ == "__main__":
    parse_files()  # Create the necessary files first
    os.system("pytest --cov-report=html --cov-report=term --junitxml=junit_tests.xml --cov=Core --color=yes Tests/")
