#!/usr/bin/env python3.5

from PyQt5 import QtWidgets, QtCore
from GUI_Windows import UInterface
from Stellarium import StellariumThread
from Client import ClientThread
from Server import RPiServerThread
import OperationHandler
import configData
import logData
import sys


logdata = logData.logData(__name__)  # Create the logger for the program


def main():
    print("\nMain thread: %d\n" % int(QtCore.QThread.currentThreadId()))  # Used in debugging
    QtCore.QThreadPool.globalInstance().setMaxThreadCount(8)  # Set the global thread pool count

    app = QtWidgets.QApplication(sys.argv)  # Create a Qt application instance
    ui = UInterface.Ui_RadioTelescopeControl()  # Instantiate the class object for the main window GUI

    # Exception handling code for the XML file process
    try:
        cfgData = configData.confData("settings.xml")
    except:
        print("There is a problem with the XML file handling. See log file for the traceback of the exception.\n")
        logdata.log("EXCEPT", "There is a problem with the XML file handling. Program terminates.", __name__)
        exit(1)  # Terminate the script

    # TCP Stellarium server initialization
    tcpStellThread = QtCore.QThread()  # Create a thread for the Stellarium server
    tcpStell = StellariumThread.StellThread(cfgData)  # Create the instance of the TCP client
    # Connect the signals from the client
    tcpStell.moveToThread(tcpStellThread)  # Move the Stellarium server to a thread
    tcpStell.conStatSigS.connect(ui.stellTCPGUIHandle)  # Connect the signal to the corresponding function
    tcpStell.dataShowSigS.connect(ui.stellDataShow)  # Connect the signal to the corresponding function
    # Connect the thread action signals
    tcpStellThread.started.connect(tcpStell.start)  # Run the start code for the thread, once it starts
    tcpStellThread.finished.connect(tcpStell.close)  # Run the stop code when a quit is requested

    # RPi communications
    # TCP server for the RPi initialization
    tcpServerThread = QtCore.QThread()  # Create a thread for the TCP client
    tcpServer = RPiServerThread.RPiServerThread(cfgData)  # Create the instance of the TCP client
    # Connect the signals from the client
    tcpServer.moveToThread(tcpServerThread)  # Move the server to a thread
    tcpServer.conStatSigR.connect(ui.rpiTCPGUIHandle)  # Connection status signal for the server
    # tcpServer.dataRcvSigC.connect(ui.signalTestrt)  # Received data signal
    # Connect the thread action signals
    tcpServerThread.started.connect(tcpServer.start)  # What to do upon thread start
    tcpServerThread.finished.connect(tcpServer.close)  # What to do upon thread exit

    # Initialize the TCP client thread
    tcpClientThread = QtCore.QThread()  # Create a thread for the TCP client
    tcpClient = ClientThread.ClientThread(cfgData)  # Create the instance of the TCP client
    # Connect the signals from the client
    tcpClient.moveToThread(tcpClientThread)  # Move the client to a thread
    tcpClient.conStatSigC.connect(ui.clientTCPGUIHandle)  # Connect the signal to the corresponding function
    # Connect the thread action signals
    tcpClientThread.started.connect(tcpClient.start)  # Connect with this function upon thread start
    tcpClientThread.finished.connect(tcpClient.close)  # Connect with thsi function upon thread exit

    # Initialize the operation handler
    operHandlerThread = QtCore.QThread()  # Create a thread for the operation handler
    operHandle = OperationHandler.OpHandler(tcpClient, tcpServer, tcpStell,
                                            tcpClientThread, tcpServerThread, tcpStellThread, ui)
    operHandle.moveToThread(operHandlerThread)  # Move the operation handler to a thread
    operHandlerThread.started.connect(operHandle.start)  # Run the start method upon thread start
    operHandlerThread.finished.connect(operHandle.appExitRequest)  # If the handler exits, then the app cloes
    operHandlerThread.finished.connect(operHandle.deleteLater)  # Wait until the run returns from the thread
    operHandlerThread.finished.connect(operHandlerThread.deleteLater)
    operHandlerThread.start()  # Start the operation handler

    s_latlon = cfgData.getLatLon()  # First element is latitude and second element is longitude
    s_alt = cfgData.getAltitude()  # Get the altitude from the settings file
    autoconStell = cfgData.getTCPStellAutoConnStatus()  # See if auto-connection at startup is enabled
    autoconRPi = cfgData.getTCPAutoConnStatus()  # Get the auto-connection preference for the RPi server and client

    # Give functionality to the buttons
    ui.connectRadioTBtn.clicked.connect(operHandle.connectButtonR)  # TCP client connection button
    ui.serverRPiConnBtn.clicked.connect(operHandle.connectButtonRPi)  # TCP server connection button
    ui.connectStellariumBtn.clicked.connect(operHandle.connectButtonS)  # Stellarium TCP server connection button

    # If auto-connection is selected for thr TCP section, then do as requested
    if autoconStell == "yes":
        tcpStellThread.start()  # Start the server thread, since auto start is enabled
    if autoconRPi == "yes":
        tcpClientThread.start()  # Start the client thread, since auto start is enabled
        tcpServerThread.start()  # Start the RPi server thread, since auto start is enabled

    # Show location on the GUI
    ui.lonTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                          "vertical-align:super;\">o</span></p></body></html>" % s_latlon[1])
    ui.latTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                          "vertical-align:super;\">o</span></p></body></html>" % s_latlon[0])
    ui.altTextInd.setText("<html><head/><body><p align=\"center\">%sm</p></body></html>" % s_alt)

    # We quit from the operation handle thread and then we exit. All handling is done there
    app.aboutToQuit.connect(operHandlerThread.quit)

    # Start the application
    ui.show_application()  # Render and show the GUI main window
    sys.exit(app.exec_())  # Execute the app until exit is selected


if __name__ == '__main__':
    try:
        main()  # Run the main program
    except (Exception, OSError):
        logdata.log("EXCEPT", "Some problem occurred. See the traceback below.")
