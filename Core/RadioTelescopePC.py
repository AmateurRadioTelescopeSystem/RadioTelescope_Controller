#!/usr/bin/env python3

import os
import sys
import logging
import logging.config

sys.path.append(os.path.abspath('.'))  # noqa

# pylint: disable=wrong-import-position

import yaml
from PyQt5 import QtWidgets, QtCore, QtGui
from Core.GUI import UInterface
from Core.Handlers import OperationHandler
from Core.Client import ClientThread
from Core.Server import RPiServerThread
from Core.Stellarium import StellariumThread
from Core.Configuration import ConfigData, DefaultData

# Required for successful operation of the pyinstaller
from Core.Handlers import CLogFileHandler

# pylint: disable=wrong-import-position


def parse_files():
    # Create the directory for the log files if it does not exist already
    try:
        if not os.path.exists('logs'):
            os.makedirs('logs')  # Create the logs directory
        if not os.path.exists('Settings'):
            os.makedirs('Settings')  # Create the settings directory
        if not os.path.exists('TLE'):
            os.makedirs('TLE')  # Make the TLE saving directory
    except Exception as exception:
        print("There is a problem creating directories. See tracback: \n%s" % exception, file=sys.stderr)
        sys.exit(-1)  # Exit the program if an error occurred

    # Check if the logging configuration file exists
    try:
        if not os.path.exists(os.path.abspath('Settings/logging_settings.yaml')):
            print("Logging configuration file not found. Creating the default.", file=sys.stderr)
            log_file = open(os.path.abspath('Settings/logging_settings.yaml'), "w+")  # Open file in writing mode
            log_file.write(DefaultData.LOG_CONFIG_DEFAULT)  # Write the default dat to the file
            log_file.close()  # Close the file, since no other operation required
    except Exception as exception:
        print("There is a problem creating the configuration file. See tracback: \n%s" % exception, file=sys.stderr)
        sys.exit(-1)  # Exit the program if an error occurred

    # Check if the settings XML file exists
    try:
        if not os.path.exists(os.path.abspath('Settings/settings.xml')):
            print("Settings file not found. Creating the default.", file=sys.stderr)
            setngs_file = open(os.path.abspath('Settings/settings.xml'), "w+")  # Open the settings file in writing mode
            setngs_file.write(DefaultData.SETTINGS_XML_DEFAULT)  # Write the default dat to the file
            setngs_file.close()  # Close the file, since no other operation required
    except Exception as exception:
        print("There is a problem creating the settings file. See tracback: \n%s" % exception, file=sys.stderr)
        sys.exit(-1)  # Exit the program if an error occurred

    # Open the configuration and apply it on the logging module
    with open(os.path.abspath('Settings/logging_settings.yaml')) as config_file:
        dictionary = yaml.safe_load(config_file)  # Load the dictionary configuration
        logging.config.dictConfig(dictionary['Logging'])  # Select the logging settings from the dictionary


def main():
    log_data = logging.getLogger(__name__)  # Create the logger for the program
    log_data.info("Main thread started")  # Use that in debugging
    QtCore.QThreadPool.globalInstance().setMaxThreadCount(8)  # Set the global thread pool count

    # Set the GUI Font according to the OS used
    font = QtGui.QFont()  # Create the font object
    font.setStyleHint(QtGui.QFont.Monospace)  # Set the a default font in case some of the following is not found
    if sys.platform.startswith('linux'):
        font.setFamily("Ubuntu")  # Set the font for Ubuntu/linux
        font.setPointSize(11)
    elif sys.platform.startswith('win32'):
        font.setFamily("Segoe UI")  # Set the font for Windows
        font.setPointSize(8)

    # Create a Qt application instance
    app = QtWidgets.QApplication(sys.argv)
    app.setFont(font)  # Set the application's font

    ui = UInterface.UIRadioTelescopeControl()  # Instantiate the class object for the main window GUI

    # Exception handling code for the XML file process
    try:
        configuration = ConfigData.Confdata(os.path.abspath('Settings/settings.xml'))
    except Exception:
        log_data.exception("There is a problem with the XML file handling. Program terminates.")
        sys.exit(1)  # Terminate the script

    # TCP Stellarium server initialization
    tcp_stell_thread = QtCore.QThread()  # Create a thread for the Stellarium server
    tcp_stell = StellariumThread.StellThread(configuration)  # Create the instance of the TCP client
    tcp_stell.moveToThread(tcp_stell_thread)  # Move the Stellarium server to a thread
    tcp_stell.conStatSigS.connect(ui.stell_tcp_gui_handle)  # Button handling signal for Stellarium
    tcp_stell.dataShowSigS.connect(ui.stell_data_show)  # Stellarium coordinate show signal
    # Connect the thread action signals
    tcp_stell_thread.started.connect(tcp_stell.start)  # Run the start code for the thread, once it starts
    tcp_stell_thread.finished.connect(tcp_stell.close)  # Run the stop code when a quit is requested

    # RPi communications
    # TCP server for the RPi initialization
    tcp_server_thread = QtCore.QThread()  # Create a thread for the TCP client
    tcp_server = RPiServerThread.RPiServerThread(configuration)  # Create the instance of the TCP client
    tcp_server.moveToThread(tcp_server_thread)  # Move the server to a thread
    tcp_server.conStatSigR.connect(ui.rpi_tcp_gui_handle)  # Connection status signal for the server
    # Connect the thread action signals
    tcp_server_thread.started.connect(tcp_server.start)  # What to do upon thread start
    tcp_server_thread.finished.connect(tcp_server.close)  # What to do upon thread exit

    # Initialize the TCP client thread
    tcp_client_thread = QtCore.QThread()  # Create a thread for the TCP client
    tcp_client = ClientThread.ClientThread(configuration)  # Create the instance of the TCP client
    tcp_client.moveToThread(tcp_client_thread)  # Move the client to a thread
    tcp_client.conStatSigC.connect(ui.client_tcp_gui_handle)  # Connection status of the TCP client
    # Connect the thread action signals
    tcp_client_thread.started.connect(tcp_client.start)  # Connect with this function upon thread start
    tcp_client_thread.finished.connect(tcp_client.close)  # Connect with thsi function upon thread exit

    # Initialize the operation handler
    operation_handler_thread = QtCore.QThread()  # Create a thread for the operation handler
    operation_handle = OperationHandler.OpHandler(tcp_client, tcp_server, tcp_stell, tcp_client_thread,
                                                  tcp_server_thread, tcp_stell_thread, ui, configuration)
    operation_handle.moveToThread(operation_handler_thread)  # Move the operation handler to a thread
    operation_handler_thread.started.connect(operation_handle.start)  # Run the start method upon thread start
    operation_handler_thread.finished.connect(operation_handle.app_exit_request)  # Close the app on handler exit
    operation_handler_thread.finished.connect(operation_handle.deleteLater)  # Wait until the thread has stopped
    operation_handler_thread.finished.connect(operation_handler_thread.deleteLater)  # Delete the thread before exiting
    operation_handler_thread.start()  # Start the operations handler

    lat_lon = configuration.get_lat_lon()  # First element is latitude and second element is longitude
    altitude = configuration.get_altitude()  # Get the altitude from the settings file

    # Show location on the GUI
    ui.main_widget.lonTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                                      "vertical-align:super;\">o</span></p></body></html>" % lat_lon[1])
    ui.main_widget.latTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                                      "vertical-align:super;\">o</span></p></body></html>" % lat_lon[0])
    ui.main_widget.altTextInd.setText("<html><head/><body><p align=\"center\">%sm</p></body></html>" % altitude)

    # We quit from the operation handle thread and then we exit. All handling is done there
    app.aboutToQuit.connect(operation_handler_thread.quit)

    ui.show_application()  # Render and show the GUI main window and start the application
    sys.exit(app.exec_())  # Execute the app until exit is selected


if __name__ == '__main__':
    parse_files()  # Parse the necessary files. All error checking is included
    log = logging.getLogger(__name__)  # Create the logger for the program

    try:
        # Redirect sterr to the logging file
        std_err_logger = logging.getLogger('STDERR')  # Create an STDERR logger
        sys.stderr = CLogFileHandler.StreamToLogger(std_err_logger,
                                                    logging.ERROR)  # Redirect stderr to the created logger
        main()  # Run the main program
    except (Exception, OSError):
        log.exception("An major error occurred. See the traceback below.")
