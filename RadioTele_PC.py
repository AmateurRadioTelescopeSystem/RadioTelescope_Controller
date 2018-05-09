#!/usr/bin/env python3.5

from PyQt5 import QtWidgets, QtCore
from GUI_Windows import UInterface
from Stellarium import StellariumThread
from Client import ClientThread
from Server import RPiServerThread
import OperationHandler
import configData
import logging.config
import logging
import sys


logging.config.fileConfig('log_config.ini')  # Get the and apply the logger configuration


def main():
    logdata = logging.getLogger(__name__)  # Create the logger for the program
    logdata.info("Main thread started")  # Use that in debugging
    QtCore.QThreadPool.globalInstance().setMaxThreadCount(8)  # Set the global thread pool count

    app = QtWidgets.QApplication(sys.argv)  # Create a Qt application instance
    ui = UInterface.Ui_RadioTelescopeControl()  # Instantiate the class object for the main window GUI

    # Exception handling code for the XML file process
    try:
        cfgData = configData.confData("settings.xml")
    except:
        logdata.exception("There is a problem with the XML file handling. Program terminates.")
        sys.exit(1)  # Terminate the script

    # TCP Stellarium server initialization
    tcpStellThread = QtCore.QThread()  # Create a thread for the Stellarium server
    tcpStell = StellariumThread.StellThread(cfgData)  # Create the instance of the TCP client
    tcpStell.moveToThread(tcpStellThread)  # Move the Stellarium server to a thread
    tcpStell.conStatSigS.connect(ui.stellTCPGUIHandle)  # Button handling signal for Stellarium
    tcpStell.dataShowSigS.connect(ui.stellDataShow)  # Stellarium coordinate show signal
    # Connect the thread action signals
    tcpStellThread.started.connect(tcpStell.start)  # Run the start code for the thread, once it starts
    tcpStellThread.finished.connect(tcpStell.close)  # Run the stop code when a quit is requested

    # RPi communications
    # TCP server for the RPi initialization
    tcpServerThread = QtCore.QThread()  # Create a thread for the TCP client
    tcpServer = RPiServerThread.RPiServerThread(cfgData)  # Create the instance of the TCP client
    tcpServer.moveToThread(tcpServerThread)  # Move the server to a thread
    tcpServer.conStatSigR.connect(ui.rpiTCPGUIHandle)  # Connection status signal for the server
    # Connect the thread action signals
    tcpServerThread.started.connect(tcpServer.start)  # What to do upon thread start
    tcpServerThread.finished.connect(tcpServer.close)  # What to do upon thread exit

    # Initialize the TCP client thread
    tcpClientThread = QtCore.QThread()  # Create a thread for the TCP client
    tcpClient = ClientThread.ClientThread(cfgData)  # Create the instance of the TCP client
    tcpClient.moveToThread(tcpClientThread)  # Move the client to a thread
    tcpClient.conStatSigC.connect(ui.clientTCPGUIHandle)  # Connection status of the TCP client
    # Connect the thread action signals
    tcpClientThread.started.connect(tcpClient.start)  # Connect with this function upon thread start
    tcpClientThread.finished.connect(tcpClient.close)  # Connect with thsi function upon thread exit

    # Initialize the operation handler
    operHandlerThread = QtCore.QThread()  # Create a thread for the operation handler
    operHandle = OperationHandler.OpHandler(tcpClient, tcpServer, tcpStell,
                                            tcpClientThread, tcpServerThread, tcpStellThread, ui, cfgData)
    operHandle.moveToThread(operHandlerThread)  # Move the operation handler to a thread
    operHandlerThread.started.connect(operHandle.start)  # Run the start method upon thread start
    operHandlerThread.finished.connect(operHandle.appExitRequest)  # If the handler exits, then the app cloes
    operHandlerThread.finished.connect(operHandle.deleteLater)  # Wait until the run returns from the thread
    operHandlerThread.finished.connect(operHandlerThread.deleteLater)  # Finally delete the thread before exit
    operHandlerThread.start()  # Start the operations handler

    s_latlon = cfgData.getLatLon()  # First element is latitude and second element is longitude
    s_alt = cfgData.getAltitude()  # Get the altitude from the settings file

    # Show location on the GUI
    ui.mainWin.lonTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                          "vertical-align:super;\">o</span></p></body></html>" % s_latlon[1])
    ui.mainWin.latTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                          "vertical-align:super;\">o</span></p></body></html>" % s_latlon[0])
    ui.mainWin.altTextInd.setText("<html><head/><body><p align=\"center\">%sm</p></body></html>" % s_alt)

    # We quit from the operation handle thread and then we exit. All handling is done there
    app.aboutToQuit.connect(operHandlerThread.quit)

    ui.show_application()  # Render and show the GUI main window and start the application
    sys.exit(app.exec_())  # Execute the app until exit is selected


if __name__ == '__main__':
    try:
        main()  # Run the main program
    except (Exception, OSError):
        logdata.log("EXCEPT", "Some problem occurred. See the traceback below.")
