from PyQt5 import QtCore
import logData


class OpHandler(QtCore.QObject):
    def __init__(self, tcpClient, tcpServer, tcpStellarium, ui, parent=None):
        super(OpHandler, self).__init__(parent)
        self.tcpClient = tcpClient  # TCP client object
        self.tcpServer = tcpServer  # TCP RPi server object
        self.tcpStellarium = tcpStellarium  # TCP Stellarium server object
        self.ui = ui  # User interface handling object
        self.logD = logData.logData(__name__)  # Data logger object

    def start(self):
        self.tcpStellarium.sendClientConn.connect(self.stellCommSend)
        self.tcpClient.dataRcvSigC.connect(self.clientDataRx)
        self.ui.stopMovingRTSig.connect(self.stopMovingRT)

    # Client connection button handling method
    def connectButtonR(self, thread=None):
        if thread.isRunning() and \
                (self.ui.connectRadioTBtn.text() == "Disconnect" or self.ui.connectRadioTBtn.text() == "Stop"):
            thread.quit()  # Disconnect from the client
        elif not thread.isRunning:
            thread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            thread.quit()
            thread.wait()
            thread.start()

    # Stellarium server connection handling method
    def connectButtonS(self, thread=None):
        if thread.isRunning() and \
                (self.ui.connectStellariumBtn.text() == "Disable" or self.ui.connectStellariumBtn.text() == "Stop"):
            thread.quit()  # Quit the currently running thread
            self.logD.log("INFO", "The thread for the server was closed", "connectButtonS")
        elif not thread.isRunning:
            thread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            thread.quit()
            thread.wait()
            thread.start()

    # RPi server connection handling method
    def connectButtonRPi(self, thread=None):
        if thread.isRunning() and \
                (self.ui.serverRPiConnBtn.text() == "Disable" or self.ui.serverRPiConnBtn.text() == "Stop"):
            thread.quit()  # Quit the currently running thread
            self.logD.log("INFO", "The thread for the server was closed", "connectButtonRPi")
        elif not thread.isRunning:
            thread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            thread.quit()
            thread.wait()
            thread.start()

    @QtCore.pyqtSlot(str, name='dataClientRX')
    def clientDataRx(self, data: str):
        print("We are from the signal fire, testing signal in op handle")
        print(data)

    @QtCore.pyqtSlot(list, name='clientCommandSendStell')
    def stellCommSend(self, radec: list):
        if self.ui.stellariumOperationSelect.currentText() == "Transit":
            command = "TRNST_RA_%.5f_DEC_%.5f" % (radec[0], radec[1])
            self.tcpClient.sendData.emit(command)
        elif self.ui.stellariumOperationSelect.currentText() == "Aim and track":
            command = "TRK %f %f" % (radec[0], radec[1])
            self.tcpClient.sendData.emit(command)

    @QtCore.pyqtSlot(name='stopRadioTele')
    def stopMovingRT(self):
        self.tcpClient.sendData.emit("STOP")  # Send the request to stop moving to the RPi server


