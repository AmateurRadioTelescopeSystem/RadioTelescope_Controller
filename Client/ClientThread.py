from PyQt5 import QtCore, QtNetwork
import logData


class ClientThread(QtCore.QObject):
    # Create the signals to be used for data handling
    conStatSigC = QtCore.pyqtSignal(str, name='conClientStat')  # Connection indication signal
    dataRcvSigC = QtCore.pyqtSignal(str, name='dataClientRX')  # Send the received data out
    sendData = QtCore.pyqtSignal(str, name='sendDataClient')  # Data to be sent to the server
    reConnectSigC = QtCore.pyqtSignal(name='reConnectClient')  # A reconnection signal originating from a button press

    def __init__(self, cfgData, parent=None):
        super(ClientThread, self).__init__(parent)  # Get the parent of the class
        self.cfgData = cfgData  # Create a variable for the cfg file

    def start(self):
        self.log = logData.logData(__name__)  # Create the logger
        self.reConnectSigC.connect(self.connect)  # Do the reconnect signal connection
        self.connect()  # Start a connection

    # The connect function is called if the signal is fired or in the start of the thread
    @QtCore.pyqtSlot(name='reConnectClient')
    def connect(self):
        # Get the host and port from the settings file for the client connection
        host = self.cfgData.getHost()
        port = self.cfgData.getPort()

        self.sock = QtNetwork.QTcpSocket()  # Create the TCP socket
        self.sock.readyRead.connect(self._receive)  # Data que signal
        self.sock.connected.connect(self._hostConnected)  # What to do when we have connected
        self.sock.error.connect(self._error)  # Log any error occurred and also perform the necessary actions
        self.sock.disconnected.connect(self._disconnected)  # If there is state change then call the function

        self.conStatSigC.emit("Connecting")  # Indicate that we are attempting a connection
        self.sock.connectToHost(QtNetwork.QHostAddress(host), int(port))  # Attempt to connect to the server

        if not self.sock.waitForConnected(msecs=1000):  # Wait a until connected (the function is waiting for 1 sec)
            self.conStatSigC.emit("Disconnected")

    @QtCore.pyqtSlot(str, name='sendDataClient')
    def send(self, data: str):
        if self.sock.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.sock.write(data.encode('utf-8'))
            self.sock.waitForBytesWritten()
            print("Sent data to RPi server: %s" % data)

    def _receive(self):
        if self.sock.bytesAvailable() > 0:
            string = self.sock.readAll().data()  # Get the data from the received QByteArray object
            self.dataRcvSigC.emit(string.decode('utf-8'))  # Decode the data to a string

    def _disconnected(self):
        self.conStatSigC.emit("Disconnected")
        self.sendData.disconnect()

    def _hostConnected(self):
        self.sendData.connect(self.send)  # Send the data to the server when this signal is fired
        self.conStatSigC.emit("Connected")  # If we have a connection send the signal

    def _error(self):
        # Print and log any error occurred
        print("An error occurred in client: %s" % self.sock.errorString())
        self.log.log("WARNING", "Some error occurred in client: %s" % self.sock.errorString(), "_error")

    # This method is called when the thread exits
    def close(self):
        self.sock.disconnected.disconnect()  # Disconnect this signal first to avoid getting in the function
        if self.sock.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.sendData.disconnect(self.send)  # Disconnect the data send signal, since the thread is closing
            self.sock.disconnectFromHost()  # Disconnect from the host
            self.sock.waitForDisconnected(msecs=1000)  # And wait until disconnected or timeout (default 3 seconds)
        else:
            self.sock.close()  # Close the socket before exiting
        self.reConnectSigC.disconnect()  # Thread is closing so it will not be needed any more
        self.conStatSigC.emit("Disconnected")  # Indicate a disconnected state on the GUI
