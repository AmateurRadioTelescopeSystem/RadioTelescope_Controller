from PyQt5 import QtCore, QtWidgets
import logData


class OpHandler(QtCore.QObject):
    def __init__(self, tcpClient, tcpServer, tcpStellarium, tcpClThread, tcpServThread, tcpStelThread, ui, parent=None):
        super(OpHandler, self).__init__(parent)
        self.tcpClient = tcpClient  # TCP client object
        self.tcpServer = tcpServer  # TCP RPi server object
        self.tcpStellarium = tcpStellarium  # TCP Stellarium server object

        # Create the thread varaible for the class
        self.tcpClThread = tcpClThread
        self.tcpServThread = tcpServThread
        self.tcpStelThread = tcpStelThread

        self.ui = ui  # User interface handling object
        self.logD = logData.logData(__name__)  # Data logger object

    def start(self):
        self.tcpStellarium.sendClientConn.connect(self.stellCommSend)  # Send data from Stellarium to the RPi
        self.tcpClient.dataRcvSigC.connect(self.clientDataRx)  # Receive pending data from RPi connected client
        self.tcpServer.dataRxFromServ.connect(self.rpiServRcvData)  # Receive data from the RPi server
        self.ui.stopMovingRTSig.connect(self.stopMovingRT)  # Send a motion stop command, once this signal is triggered

    # Client connection button handling method
    def connectButtonR(self):
        if self.tcpClThread.isRunning() and \
                (self.ui.connectRadioTBtn.text() == "Disconnect" or self.ui.connectRadioTBtn.text() == "Stop"):
            self.tcpClThread.quit()  # Disconnect from the client
        elif not self.tcpClThread.isRunning():
            self.tcpClThread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            self.tcpClient.reConnectSigC.emit()

    # Stellarium server connection handling method
    def connectButtonS(self):
        if self.tcpStelThread.isRunning() and \
                (self.ui.connectStellariumBtn.text() == "Disable" or self.ui.connectStellariumBtn.text() == "Stop"):
            self.tcpStelThread.quit()  # Quit the currently running thread
            self.logD.log("INFO", "The thread for the server was closed", "connectButtonS")
        elif not self.tcpStelThread.isRunning():
            self.tcpStelThread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            self.tcpStellarium.reConnectSigS.emit()

    # RPi server connection handling method
    def connectButtonRPi(self):
        if self.tcpServThread.isRunning() and \
                (self.ui.serverRPiConnBtn.text() == "Disable" or self.ui.serverRPiConnBtn.text() == "Stop"):
            self.tcpServThread.quit()  # Quit the currently running thread
            self.logD.log("INFO", "The thread for the server was closed", "connectButtonRPi")
        elif not self.tcpServThread.isRunning():
            self.tcpServThread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            self.tcpServer.reConnectSigR.emit()

    # Dta received from the client connected to the RPi server
    @QtCore.pyqtSlot(str, name='dataClientRX')
    def clientDataRx(self, data: str):
        print("We are from the signal fire, testing signal in op handle")
        print(data)

    # Send the appropriate command according to the selected mode. Data is received from Stellarium (sendClientConn)
    @QtCore.pyqtSlot(list, name='clientCommandSendStell')
    def stellCommSend(self, radec: list):
        if self.ui.stellariumOperationSelect.currentText() == "Transit":
            command = "TRNST_RA_%.5f_DEC_%.5f" % (radec[0], radec[1])
            self.tcpClient.sendData.emit(command)
        elif self.ui.stellariumOperationSelect.currentText() == "Aim and track":
            command = "TRK %f %f" % (radec[0], radec[1])
            self.tcpClient.sendData.emit(command)

    # Received data from the server that the RPi is connected as a client. Signal is (dataRxFromServ)
    @QtCore.pyqtSlot(str, name='rpiServDataRx')
    def rpiServRcvData(self, data: str):
        spltData = data.split("_")  # Split the string with the set delimiter
        if spltData[0] == "DISHPOS":
            ra = spltData[2]  # Get the RA from the received position
            dec = spltData[4]  # Get the DEC from the received position
            self.tcpStellarium.sendDataStell.emit(float(ra), float(dec))  # Send the data to Stellarium

    # Command to stop any motion of the radio telescope dish
    @QtCore.pyqtSlot(name='stopRadioTele')
    def stopMovingRT(self):
        self.tcpClient.sendData.emit("STOP")  # Send the request to stop moving to the RPi server

    # This function is called whenever the app is about to quit
    def appExitRequest(self):
        # First quit from the thread and then delete both the thread and the corresponding object
        # Quit exits the thread and then wait is waiting for the thread exit
        # deleteLater, deletes the thread object and the threaded object
        self.tcpClThread.quit()
        self.tcpClThread.wait()
        self.tcpClient.deleteLater()
        self.tcpClThread.deleteLater()

        self.tcpServThread.quit()
        self.tcpServThread.wait()
        self.tcpServer.deleteLater()
        self.tcpServThread.deleteLater()

        self.tcpStelThread.quit()
        self.tcpStelThread.wait()
        self.tcpStellarium.deleteLater()
        self.tcpStelThread.deleteLater()
