from PyQt5 import QtCore, QtNetwork
import logData


class RPiServerThread(QtCore.QObject):
    # Create the signals to be used for data handling
    conStatSigR = QtCore.pyqtSignal(str, name='conRPiStat')  # Raspberry pi connection indicator
    dataRxFromServ = QtCore.pyqtSignal(str, name='rpiServDataRx')  # Data received from the server of RPi
    reConnectSigR = QtCore.pyqtSignal(name='reConnectServer')  # A reconnection signal originating from a button press
    clientNotice = QtCore.pyqtSignal(name='clientNotice')  # Notify the client that we have a connection
    sendDataBack = QtCore.pyqtSignal(str, name='sendDtaBack')  # Send data to the RPi from the server

    def __init__(self, cfgData, parent=None):
        super(RPiServerThread, self).__init__(parent)  # Get the parent of the class
        self.cfgData = cfgData
        self.logD = logData.logData(__name__)  # Create the logger

    # This method is called in every thread start and if the re-connect signal is fired
    def start(self):
        print("RPi server thread ID: %d" % int(QtCore.QThread.currentThreadId()))  # Used in debugging
        self.socket = None  # Create a variable to hold the socket
        self.reConnectSigR.connect(self.connectServ)
        self.connectServ()  # Start the server

    @QtCore.pyqtSlot(name='reConnectServer')
    def connectServ(self):
        # Get the saved data from the settings file
        self.host = self.cfgData.getRPiHost()  # Get the TCP connection host
        self.port = self.cfgData.getRPiPort()  # Get the TCP connection port

        if self.host == "localhost" or self.host == "127.0.0.1":
            self.host = QtNetwork.QHostAddress.LocalHost
        else:
            for ipAddress in QtNetwork.QNetworkInterface.allAddresses():
                if ipAddress != QtNetwork.QHostAddress.LocalHost and ipAddress.toIPv4Address() != 0:
                    break  # If we found an IP then we exit the loop
                else:
                    ipAddress = QtNetwork.QHostAddress.LocalHost  # If no IP is found, assign localhost
            self.host = ipAddress  # Assign the IP address that wa found above

        self.tcpServer = QtNetwork.QTcpServer()  # Create a server object
        self.tcpServer.newConnection.connect(self._new_connection)  # Handler for a new connection

        self.tcpServer.listen(self.host, int(self.port))  # Start listening for connections
        self.conStatSigR.emit("Waiting")  # Indicate that the server is listening on the GUI

    # Whenever there is new connection, we call this method
    def _new_connection(self):
        if self.tcpServer.hasPendingConnections():
            self.socket = self.tcpServer.nextPendingConnection()  # Returns a new QTcpSocket for the connection

            if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.tcpServer.close()  # Stop listening for other connections
                self.conStatSigR.emit("Connected")  # Indicate that the server has a connection on the GUI
                self.clientNotice.emit()  # Tell the client that we are connected, so to attempt a connection
                self.sendDataBack.connect(self.sendRPi)  # Connect the data sending signal
                self.socket.readyRead.connect(self._receive)  # If there is pending data get it
                self.socket.error.connect(self._error)  # Log any error occurred and also perform the necessary actions
                self.socket.disconnected.connect(self._disconnected)  # Execute the appropriate code on state change

    # Should we have data pending to be received, this method is called
    def _receive(self):
        try:
            while self.socket.bytesAvailable() > 0:  # Read all data in que
                recData = self.socket.readLine().data().decode('utf-8').rstrip('\n')  # Get the data as a string
                #recData = self.socket.readAll().data().decode('utf-8')  # Get the data as a string
                self.dataRxFromServ.emit(recData)  # Send a signal to indicate that the server received some data
        except Exception:
            # If data is sent fast, then an exception will occur
            self.logD.log("EXCEPT", "Some problem occurred while receiving server data. See traceback", "_receive")

    # If at any moment the connection state is changed, we call this method
    def _disconnected(self):
        # Do the following if the connection is lost
        self.conStatSigR.emit("Waiting")  # Indicate that the server does not have a connection on the GUI
        self.socket.readyRead.disconnect()  # Disconnect the signal to avoid double firing
        self.sendDataBack.disconnect()  # Detach the signal to avoid any accidental firing
        self.tcpServer.listen(self.host, int(self.port))  # Start listening again

    def _error(self):
        # Print and log any error occurred
        print("An error occurred in RPi server: %s" % self.socket.errorString())
        self.logD.log("WARNING", "Some error occurred in RPi server: %s" % self.socket.errorString(), "_error")

    @QtCore.pyqtSlot(str, name='sendDtaBack')
    def sendRPi(self, data: str):
        try:
            self.socket.write(data.encode('utf-8'))  # Send data back to the client
            self.socket.waitForBytesWritten()  # Wait for the data to be written
        except Exception as e:
            print("RPi server send client issue: %s" % e)  # Debugging print

    # This method is called whenever the thread exits
    def close(self):
        self.tcpServer.close()  # Close the TCP server
        if self.socket is not None:
            self.socket.disconnected.disconnect()  # Close the disconnect signal first to avoid firing
            # TODO make the disconnect better so the program does not crash on exit
            self.sendDataBack.disconnect()  # Detach the signal to avoid any accidental firing
            self.socket.close()  # Close the underlying TCP socket
        self.reConnectSigR.disconnect()  # Signal not used after thread exit (Reconnected at thread start)
        self.conStatSigR.emit("Disconnected")  # Indicate disconnection on the GUI

