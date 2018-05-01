#!/usr/bin/env python3.5

from PyQt5 import QtWidgets, QtCore
from functools import partial
import UInterface
import configData
import logData
import TCPClient
import TCPServerStellarium
import sys
import StellariumThread


if __name__ == '__main__':
    logdata = logData.logData(__name__)  # Create the logger for the program

    app = QtWidgets.QApplication(sys.argv)  # Create a Qt application instance
    RadioTelescopeControl = QtWidgets.QMainWindow()  # Create the main window of th GUI

    # Create the contents of the windows
    ui = UInterface.Ui_RadioTelescopeControl()  # Instantiate the class object for the main window GUI
    ui.setupUi(RadioTelescopeControl)  # Call the function to make all the connections for the GUI things

    # Exception handling code for the XML file process
    try:
        cfgData = configData.confData("settings.xml")
    except:
        print("There is a problem with the XML file handling. See log file for the traceback of the exception.\n")
        logdata.log("EXCEPT", "There is a problem with the XML file handling. Program terminates.", __name__)
        exit(1)  # Terminate the script

    # Exception handling code for the TCP server initial setup
    try:
        tcpServer = TCPServerStellarium.TCPStellarium(cfgData, ui)
    except:
        print("There is a problem with the TCP server handling. See log file for the traceback of the exception.\n")
        logdata.log("EXCEPT", "There is a problem with the TCP handling. Program terminates.", __name__)
        exit(1)  # Terminate the script

    # Exception handling code for the TCP client initial setup
    try:
        tcpClient = TCPClient.TCPClient(cfgData, ui)
    except:
        print("There is a problem with the TCP client handling. See log file for the traceback of the exception.\n")
        logdata.log("EXCEPT", "There is a problem with the TCP handling. Program terminates.", __name__)
        exit(1)  # Terminate the script

    tcpStellThread = StellariumThread.StellThread(tcpServer, tcpClient, ui)  # Create a thread for the Stellarium server

    s_latlon = cfgData.getLatLon()  # First element is latitude and second element is longitude
    s_alt = cfgData.getAltitude()  # Get the altitude from the settings file
    hostport = [cfgData.getHost(), cfgData.getPort()]  # Get the saved host address or name and port of the server
    autoconServer = cfgData.getTCPStellAutoConnStatus()  # See if auto-connection at startup is enabled

    if autoconServer == "yes":
        tcpStellThread.start()  # Start the server thread, since auto start is enabled

    # Give functionality to the buttons and add the necessary texts to fields
    ui.connectRadioTBtn.clicked.connect(partial(tcpClient.connectButton, actualPress = True))
    ui.connectStellariumBtn.clicked.connect(partial(tcpServer.connectButton, thread=tcpStellThread))
    ui.lonTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                          "vertical-align:super;\">o</span></p></body></html>" % s_latlon[1])
    ui.latTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                          "vertical-align:super;\">o</span></p></body></html>" % s_latlon[0])
    ui.altTextInd.setText("<html><head/><body><p align=\"center\">%sm</p></body></html>" % s_alt)

    RadioTelescopeControl.show()  # Render and show the GUI main window
    sys.exit(app.exec_())  # Execute the app until exit is selected
