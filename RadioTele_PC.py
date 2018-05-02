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

    tcpServerThread = RPiServerThread.RPiServerThread(cfgData)
    tcpServerThread.conStatSigR.connect(ui.rpiTCPGUIHandle)

    tcpStellThread = StellariumThread.StellThread(cfgData)  # Create a thread for the Stellarium server
    tcpStellThread.conStatSig.connect(ui.stellTCPGUIHandle)  # Connect the signal to the corresponding function
    tcpStellThread.dataShowSig.connect(ui.stellDataShow)  # Connect the signal to the corresponding function
    tcpStellThread.sendClientConn.connect(partial(tcpClienThread.tcp.stellCommSend, thread=tcpClienThread))  # Signal for sending the command string to RPi

    #tcpClienThread.dataShowSig.connect(ui.stellDataShow)  # Connect the signal to the corresponding function
    ui.stopMovingRTSig.connect(partial(tcpClienThread.tcp.stopMovingRT, thread=tcpClienThread))

    s_latlon = cfgData.getLatLon()  # First element is latitude and second element is longitude
    s_alt = cfgData.getAltitude()  # Get the altitude from the settings file
    hostport = [cfgData.getHost(), cfgData.getPort()]  # Get the saved host address or name and port of the server
    autoconServer = cfgData.getTCPStellAutoConnStatus()  # See if auto-connection at startup is enabled

    if autoconServer == "yes":
        tcpStellThread.start()  # Start the server thread, since auto start is enabled
    if autoconServer == "yes":
        tcpClienThread.start()  # Start the server thread, since auto start is enabled
        tcpServerThread.start()

    # Give functionality to the buttons and add the necessary texts to fields
    ui.connectRadioTBtn.clicked.connect(partial(tcpClienThread.tcp.connectButtonR, thread=tcpClienThread))
    ui.connectStellariumBtn.clicked.connect(partial(tcpStellThread.tcp.connectButton, thread=tcpStellThread))
    ui.lonTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                          "vertical-align:super;\">o</span></p></body></html>" % s_latlon[1])
    ui.latTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                          "vertical-align:super;\">o</span></p></body></html>" % s_latlon[0])
    ui.altTextInd.setText("<html><head/><body><p align=\"center\">%sm</p></body></html>" % s_alt)

    ui.show_application()  # Render and show the GUI main window
    sys.exit(app.exec_())  # Execute the app until exit is selected


if __name__ == '__main__':
    try:
        main()
    except Exception:
        logdata.log("EXCEPT", "Some problem occurred. See the traceback below.")