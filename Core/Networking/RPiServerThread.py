import logging
from PyQt5 import QtCore, QtNetwork


class RPiServerThread(QtCore.QObject):
    # Create the signals to be used for data handling
    conStatSigR = QtCore.pyqtSignal(str, name='conRPiStat')  # Raspberry pi connection indicator
    dataRxFromServ = QtCore.pyqtSignal(str, name='rpiServDataRx')  # Data received from the server of RPi
    reConnectSigR = QtCore.pyqtSignal(name='reConnectServer')  # A reconnection signal originating from a button press
    clientNotice = QtCore.pyqtSignal(name='clientNotice')  # Notify the client that we have a connection
    sendDataBack = QtCore.pyqtSignal(str, name='sendDtaBack')  # Send data to the RPi from the server

    def __init__(self, cfg_data, parent=None):
        super(RPiServerThread, self).__init__(parent)  # Get the parent of the class
        self.cfg_data = cfg_data  # Create the configuration file object
        self.logger = logging.getLogger(__name__)  # Create the logger

    # This method is called in every thread start and if the re-connect signal is fired
    def start(self):
        mutex = QtCore.QMutex()  # Create a QMutex object
        mutex.lock()  # Lock the thread until it has started, to avoid any overlapping problems
        self.logger.info("Raspberry Pi connection server thread started")
        self.socket = None  # Create a variable to hold the socket
        self.reConnectSigR.connect(self.connect_server)
        self.connect_server()  # Start the server
        mutex.unlock()  # Unlock the thread, since it has started successfully

    @QtCore.pyqtSlot(name='reConnectServer')
    def connect_server(self):
        # Get the saved data from the settings file
        self.host = self.cfg_data.get_rpi_host()  # Get the TCP connection host
        self.port = self.cfg_data.get_rpi_port()  # Get the TCP connection port
        rem_stat = self.cfg_data.get_server_remote("TCPRPiServ")

        if rem_stat == "no":
            self.host = QtNetwork.QHostAddress.LocalHost
        elif rem_stat == "yes":
            for ip_address in QtNetwork.QNetworkInterface.allAddresses():
                if ip_address != QtNetwork.QHostAddress.LocalHost and ip_address.toIPv4Address() != 0:
                    break  # If we found an IP then we exit the loop
                else:
                    ip_address = QtNetwork.QHostAddress.LocalHost  # If no IP is found, assign localhost
            self.host = ip_address  # Assign the IP address that wa found above
        # TODO Add the ability to incorporate custom IP addresses

        self.tcp_server = QtNetwork.QTcpServer()  # Create a server object
        self.tcp_server.newConnection.connect(self._new_connection)  # Handler for a new connection

        self.tcp_server.listen(self.host, int(self.port))  # Start listening for connections
        self.conStatSigR.emit("Waiting")  # Indicate that the server is listening on the GUI
        self.logger.debug("RPI server connection initializer called")

    # Whenever there is new connection, we call this method
    def _new_connection(self):
        if self.tcp_server.hasPendingConnections():
            self.socket = self.tcp_server.nextPendingConnection()  # Returns a new QTcpSocket for the connection

            if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.tcp_server.close()  # Stop listening for other connections
                self.conStatSigR.emit("Connected")  # Indicate that the server has a connection on the GUI
                self.clientNotice.emit()  # Tell the client that we are connected, so to attempt a connection
                self.sendDataBack.connect(self.send_rpi)  # Connect the data sending signal
                self.socket.readyRead.connect(self._receive)  # If there is pending data get it
                self.socket.error.connect(self._error)  # Log any error occurred and also perform the necessary actions
                self.socket.disconnected.connect(self._disconnected)  # Execute the appropriate code on state change
                self.logger.info("RPi server has new connection")

    # Should we have data pending to be received, this method is called
    def _receive(self):
        try:
            while self.socket.bytesAvailable() > 0:  # Read all data in que
                received_data = self.socket.readLine().data().decode('utf-8').rstrip('\n')  # Get the data as a string
                self.dataRxFromServ.emit(received_data)  # Send a signal to indicate that the server received some data
                self.logger.debug("RPi server received: %s", received_data)
        except Exception:
            # If data is sent fast, then an exception will occur
            self.logger.exception("Some problem occurred while receiving server data. See traceback")

    # If at any moment the connection state is changed, we call this method
    def _disconnected(self):
        # Do the following if the connection is lost
        self.conStatSigR.emit("Waiting")  # Indicate that the server does not have a connection on the GUI
        self.socket.readyRead.disconnect()  # Disconnect the signal to avoid double firing
        self.sendDataBack.disconnect()  # Detach the signal to avoid any accidental firing
        self.tcp_server.listen(self.host, int(self.port))  # Start listening again
        self.logger.warning("The client disconnected from us")

    def _error(self):
        # Print and log any error occurred
        self.logger.error("RPi server reported an error: %s", self.socket.errorString())

    @QtCore.pyqtSlot(str, name='sendDtaBack')
    def send_rpi(self, data: str):
        try:
            self.socket.write(data.encode('utf-8'))  # Send data back to the client
            self.socket.waitForBytesWritten()  # Wait for the data to be written
        except Exception:
            self.logger.exception("There was a problem sending the data. See traceback")

    # This method is called whenever the thread exits
    def close(self):
        if self.socket is not None:
            self.socket.disconnected.disconnect()  # Close the disconnect signal first to avoid firing
            if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:  # Check if socket is connected
                self.sendDataBack.disconnect()  # Detach the signal to avoid any accidental firing
            self.socket.close()  # Close the underlying TCP socket
        self.reConnectSigR.disconnect()  # Signal not used after thread exit (Reconnected at thread start)
        self.conStatSigR.emit("Disconnected")  # Indicate disconnection on the GUI
        self.logger.info("RPi server thread closed")
