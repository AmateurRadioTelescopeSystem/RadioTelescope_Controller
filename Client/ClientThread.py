from PyQt5 import QtCore, QtNetwork


class ClientThread(QtCore.QObject):
    # Create the signals to be used for data handling
    conStatSigC = QtCore.pyqtSignal(str, name='conClientStat')  # Connection indication signal
    dataRcvSigC = QtCore.pyqtSignal(str, name='dataClientRX')  # Send the received data out
    sendData = QtCore.pyqtSignal(str, name='sendDataClient')  # Data to be sent to the server

    def __init__(self, cfgData, parent=None):
        super(ClientThread, self).__init__(parent)  # Get the parent of the class
        self.cfgData = cfgData  # Create a variable for the cfg file

    def connect(self):
        # Get the host and port from the settings file for the client connection
        host = self.cfgData.getHost()
        port = self.cfgData.getPort()

        self.sock = QtNetwork.QTcpSocket()  # Create the TCP socket
        self.sock.readyRead.connect(self._receive)  # Data que signal
        self.sock.stateChanged.connect(self._stateChange)  # If there is state change then call the function

        self.sendData.connect(self.send)  # Send the data to the server when this signal is fired

        self.conStatSigC.emit("Connecting")  # Indicate that we are attempting a connection
        self.sock.connectToHost(QtNetwork.QHostAddress(host), int(port))  # Attempt to connect to the server

        if self.sock.waitForConnected(msecs=3000):  # Wait a until connected (the function is waiting for 3 sec)
            self.conStatSigC.emit("Connected")  # If we have a connection send the signal
        else:
            self.conStatSigC.emit("Disconnected")

    def _receive(self):
        if self.sock.bytesAvailable() > 0:
            string = self.sock.readAll().data()  # Get the data from the received QByteArray object
            self.dataRcvSigC.emit(string.decode('utf-8'))  # Decode the data to a string

    def _stateChange(self):
        if self.sock.state() == QtNetwork.QAbstractSocket.UnconnectedState:
            self.conStatSigC.emit("Disconnected")
            self.sock.waitForConnected(msecs=3000)

    @QtCore.pyqtSlot(str, name='sendDataClient')
    def send(self, data: str):
        self.sock.write(data.encode('utf-8'))
        self.sock.waitForBytesWritten()

    # This method is called when the thread exits
    def close(self):
        self.sock.disconnectFromHost()  # Disconnect from the host
        self.sock.waitForDisconnected()  # And wait until disconnected or timeout (default 3 seconds)
        if self.sock.state() == QtNetwork.QAbstractSocket.UnconnectedState:
            self.sock.close()  # Close the socket before exiting
            self.conStatSigC.emit("Disconnected")  # Indicate a disconnected state on the GUI
