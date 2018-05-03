#!/usr/bin/env python3.5

from PyQt5 import QtWidgets
from functools import partial
from GUI_Windows import UInterface
from Stellarium import StellariumThread
from Client import ClientThread
from Server import RPiServerThread
import configData
import logData
import sys


logdata = logData.logData(__name__)  # Create the logger for the program


def main():
    app = QtWidgets.QApplication(sys.argv)  # Create a Qt application instance
    ui = UInterface.Ui_RadioTelescopeControl()  # Instantiate the class object for the main window GUI

    # Exception handling code for the XML file process
    try:
        cfgData = configData.confData("settings.xml")
    except:
        print("There is a problem with the XML file handling. See log file for the traceback of the exception.\n")
        logdata.log("EXCEPT", "There is a problem with the XML file handling. Program terminates.", __name__)
        exit(1)  # Terminate the script

    # Initialize the TCP client thread first, since it is used below
    tcpClienThread = ClientThread.ClientThread(cfgData, ui)
    tcpClienThread.conStatSig.connect(ui.clientTCPGUIHandle)  # Connect the signal to the corresponding function

    # TCP server for the RPi initialization
    tcpServerThread = RPiServerThread.RPiServerThread(cfgData)
    tcpServerThread.conStatSigR.connect(ui.rpiTCPGUIHandle)  # Connection status signal for the server

    # TCP Stellarium server initialization
    tcpStellThread = StellariumThread.StellThread(cfgData)  # Create a thread for the Stellarium server
    tcpStellThread.conStatSig.connect(ui.stellTCPGUIHandle)  # Connect the signal to the corresponding function
    tcpStellThread.dataShowSig.connect(ui.stellDataShow)  # Connect the signal to the corresponding function

    # Signal to send the command string to RPi
    tcpStellThread.sendClientConn.connect(partial(tcpClienThread.tcp.stellCommSend, thread=tcpClienThread))
    ui.stopMovingRTSig.connect(partial(tcpClienThread.tcp.stopMovingRT, thread=tcpClienThread))  # Stop any motion

    s_latlon = cfgData.getLatLon()  # First element is latitude and second element is longitude
    s_alt = cfgData.getAltitude()  # Get the altitude from the settings file
    autoconStell = cfgData.getTCPStellAutoConnStatus()  # See if auto-connection at startup is enabled
    autoconRPi = cfgData.getTCPAutoConnStatus()  # Get the auto-connection preference for the RPi

    # If auto-connection is selected for thr TCP section, then do as requested
    if autoconStell == "yes":
        tcpStellThread.start()  # Start the server thread, since auto start is enabled
    if autoconRPi == "yes":
        tcpClienThread.start()  # Start the client thread, since auto start is enabled
        tcpServerThread.start()  # Start the RPi server thread, since auto start is enabled

    # Give functionality to the buttons and add the necessary texts to fields
    ui.connectRadioTBtn.clicked.connect(tcpClienThread.connectButtonR)
    ui.serverRPiConnBtn.clicked.connect(tcpServerThread.connectButtonRPi)
    ui.connectStellariumBtn.clicked.connect(tcpStellThread.connectButton)

    # Show location on the GUI
    ui.lonTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                          "vertical-align:super;\">o</span></p></body></html>" % s_latlon[1])
    ui.latTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                          "vertical-align:super;\">o</span></p></body></html>" % s_latlon[0])
    ui.altTextInd.setText("<html><head/><body><p align=\"center\">%sm</p></body></html>" % s_alt)

    # Start the application
    ui.show_application()  # Render and show the GUI main window
    sys.exit(app.exec_())  # Execute the app until exit is selected


if __name__ == '__main__':
    try:
        main()  # Run the main program
    except (Exception, OSError):
        logdata.log("EXCEPT", "Some problem occurred. See the traceback below.")
