#!/usr/bin/env python3

import os
import sys
import yaml
import logging
import logging.config
sys.path.append(os.path.abspath('.'))  # noqa
sys.path.append(os.path.abspath('../Core/'))  # noqa

import Tests.DefaultData
from PyQt5 import QtWidgets, QtCore, QtTest, QtNetwork
from Core.GUI import UInterface
from Core.Handlers import OperationHandler
from Core.Client import ClientThread
from Core.Server import RPiServerThread
from Core.Stellarium import StellariumThread
from Core.Configuration import ConfigData

# Create a virtual display for testing
#from pyvirtualdisplay import Display
#display = Display(visible=False, size=(1024, 768), color_depth=24)
#display.start()


# Required for successful operation of the pyinstaller
from Handlers import CLogFileHandler


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
            print("Logging configuration file not found. Creating the default.", file=sys.stderr)
            log_file = open(os.path.abspath('Tests/Settings/logging_settings.yaml'), "w+")  # Open file in writing mode
            log_file.write(Tests.DefaultData.log_config_str)  # Write the default dat to the file
            log_file.close()  # Close the file, since no other operation required
    except Exception as excep:
        print("There is a problem creating the configuration file. See tracback: \n%s" % excep, file=sys.stderr)
        sys.exit(-1)  # Exit the program if an error occurred

    # Check if the settings XML file exists
    try:
        if not os.path.exists(os.path.abspath('Tests/Settings/settings.xml')):
            print("Settings file not found. Creating the default.", file=sys.stderr)
            setngs_file = open(os.path.abspath('Tests/Settings/settings.xml'),
                               "w+")  # Open the settings file in writing mode
            setngs_file.write(Tests.DefaultData.settings_xml_str)  # Write the default dat to the file
            setngs_file.close()  # Close the file, since no other operation required
    except Exception as excep:
        print("There is a problem creating the settings file. See tracback: \n%s" % excep, file=sys.stderr)
        sys.exit(-1)  # Exit the program if an error occurred

    # Open the configuration and apply it on the logging module
    with open(os.path.abspath('Tests/Settings/logging_settings.yaml')) as config_file:
        dictionary = yaml.safe_load(config_file)  # Load the dictionary configuration
        logging.config.dictConfig(dictionary['Logging'])  # Select the logging settings from the dictionary


def main():
    logdata = logging.getLogger(__name__)  # Create the logger for the program
    logdata.info("Main thread started")  # Use that in debugging
    QtCore.QThreadPool.globalInstance().setMaxThreadCount(8)  # Set the global thread pool count

    app = QtWidgets.QApplication(sys.argv)  # Create a Qt application instance
    ui = UInterface.UIRadioTelescopeControl()  # Instantiate the class object for the main window GUI

    # Exception handling code for the XML file process
    try:
        cfgData = ConfigData.ConfData(os.path.abspath('Tests/Settings/settings.xml'))
    except:
        logdata.exception("There is a problem with the XML file handling. Program terminates.")
        sys.exit(1)  # Terminate the script

    # TCP Stellarium server initialization
    tcpStellThread = QtCore.QThread()  # Create a thread for the Stellarium server
    tcpStell = StellariumThread.StellThread(cfgData)  # Create the instance of the TCP client
    tcpStell.moveToThread(tcpStellThread)  # Move the Stellarium server to a thread
    tcpStell.conStatSigS.connect(ui.stell_tcp_gui_handle)  # Button handling signal for Stellarium
    tcpStell.dataShowSigS.connect(ui.stell_data_show)  # Stellarium coordinate show signal
    # Connect the thread action signals
    tcpStellThread.started.connect(tcpStell.start)  # Run the start code for the thread, once it starts
    tcpStellThread.finished.connect(tcpStell.close)  # Run the stop code when a quit is requested

    # RPi communications
    # TCP server for the RPi initialization
    tcpServerThread = QtCore.QThread()  # Create a thread for the TCP client
    tcpServer = RPiServerThread.RPiServerThread(cfgData)  # Create the instance of the TCP client
    tcpServer.moveToThread(tcpServerThread)  # Move the server to a thread
    tcpServer.conStatSigR.connect(ui.rpi_tcp_gui_handle)  # Connection status signal for the server
    # Connect the thread action signals
    tcpServerThread.started.connect(tcpServer.start)  # What to do upon thread start
    tcpServerThread.finished.connect(tcpServer.close)  # What to do upon thread exit

    # Initialize the TCP client thread
    tcpClientThread = QtCore.QThread()  # Create a thread for the TCP client
    tcpClient = ClientThread.ClientThread(cfgData)  # Create the instance of the TCP client
    tcpClient.moveToThread(tcpClientThread)  # Move the client to a thread
    tcpClient.conStatSigC.connect(ui.client_tcp_gui_handle)  # Connection status of the TCP client
    # Connect the thread action signals
    tcpClientThread.started.connect(tcpClient.start)  # Connect with this function upon thread start
    tcpClientThread.finished.connect(tcpClient.close)  # Connect with thsi function upon thread exit

    # Initialize the operation handler
    operHandlerThread = QtCore.QThread()  # Create a thread for the operation handler
    operHandle = OperationHandler.OpHandler(tcpClient, tcpServer, tcpStell,
                                            tcpClientThread, tcpServerThread, tcpStellThread, ui, cfgData)
    operHandle.moveToThread(operHandlerThread)  # Move the operation handler to a thread
    operHandlerThread.started.connect(operHandle.start)  # Run the start method upon thread start
    operHandlerThread.finished.connect(operHandle.app_exit_request)  # If the handler exits, then the app cloes
    operHandlerThread.finished.connect(operHandle.deleteLater)  # Wait until the run returns from the thread
    operHandlerThread.finished.connect(operHandlerThread.deleteLater)  # Finally delete the thread before exit
    operHandlerThread.start()  # Start the operations handler

    s_latlon = cfgData.get_lat_lon()  # First element is latitude and second element is longitude
    s_alt = cfgData.get_altitude()  # Get the altitude from the settings file

    # Show location on the GUI
    ui.main_widget.lonTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                                    "vertical-align:super;\">o</span></p></body></html>" % s_latlon[1])
    ui.main_widget.latTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                                    "vertical-align:super;\">o</span></p></body></html>" % s_latlon[0])
    ui.main_widget.altTextInd.setText("<html><head/><body><p align=\"center\">%sm</p></body></html>" % s_alt)

    # We quit from the operation handle thread and then we exit. All handling is done there
    app.aboutToQuit.connect(operHandlerThread.quit)

    ui.show_application()  # Render and show the GUI main window and start the application

    window_show = QtTest.QTest.qWaitForWindowExposed(ui.main_win)  # Wait until the main window is shown

    QtTest.QTest.qWait(2000)  # Wait for the retrieval of TLE file
    try:
        QtTest.QTest.mouseClick(ui.tle_info_msg_box.buttons()[0], QtCore.Qt.LeftButton)  # Click the GUI button to proceed
    except IndexError:
        print("Possibly the file exists. \nDouble check to make sure that there is no other error.")
        pass
    QtTest.QTest.qWait(1000)  # Wait for the client thread to start

    client_connected = (tcpClient.sock.state() == QtNetwork.QAbstractSocket.ConnectedState)  # Get the connection status

    if window_show and client_connected:
        exit_code = 0  # Successful test
    else:
        exit_code = -1  # Indicate some error
    tcpClientThread.quit()
    tcpClientThread.wait()
    tcpServerThread.quit()
    tcpServerThread.wait()
    tcpStellThread.quit()
    tcpStellThread.wait()
    operHandlerThread.quit()
    operHandlerThread.wait()
    sys.exit(exit_code)


if __name__ == '__main__':
    log = logging.getLogger(__name__)  # Create the logger for the program
    try:
        parse_files()
        main()  # Run the main program
    except (Exception, OSError):
        log.exception("An major error occurred. See the traceback below.")
