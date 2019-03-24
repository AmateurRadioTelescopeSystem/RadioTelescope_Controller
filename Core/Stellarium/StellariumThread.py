import logging
from PyQt5 import QtCore, QtNetwork
from Core.Stellarium import StellariumDataHandling


class StellThread(QtCore.QObject):
    # Create the signals to be used for data handling
    conStatSigS = QtCore.pyqtSignal(str, name='conStellStat')  # Stellarium connection status indication signal
    dataShowSigS = QtCore.pyqtSignal(float, float, name='dataStellShow')  # Coordinates show in the GUI
    sendClientConn = QtCore.pyqtSignal(list, name='clientCommandSendStell')  # Send the command to the radio telescope
    sendDataStell = QtCore.pyqtSignal(float, float, name='stellariumDataSend')  # Send the data to Stellarium
    reConnectSigS = QtCore.pyqtSignal(name='reConnectStell')  # A reconnection signal originating from a button press

    def __init__(self, cfg_data, parent=None):
        super(StellThread, self).__init__(parent)  # Get the parent of the class
        self.cfg_data = cfg_data  # Settings file object
        self.logger = logging.getLogger(__name__)  # Create the logger

    # This method is called in every thread start
    def start(self):
        mutex = QtCore.QMutex()  # Create a QMutex object
        mutex.lock()  # Lock the thread until it has started, to avoid any overlapping problems
        self.logger.info("Stellarium server thread started")
        self.socket = None  # Create the instance os the socket variable to use it later
        self.data_handle = StellariumDataHandling.StellariumData()  # Data conversion object
        self.reConnectSigS.connect(self.connect_stellarium)  # Connect the signal to the connection function
        self.connect_stellarium()  # Start the Stellarium server
        mutex.unlock()  # Unlock the thread, since it has started successfully

    @QtCore.pyqtSlot(name='reConnectStell')
    def connect_stellarium(self):
        # Get the saved data from the settings file
        self.host = self.cfg_data.get_stell_host()  # Get the TCP connection host
        self.port = self.cfg_data.get_stell_port()  # Get the TCP connection port

        if self.host == "localhost" or self.host == "127.0.0.1":
            self.host = QtNetwork.QHostAddress.LocalHost
        else:
            for ip_address in QtNetwork.QNetworkInterface.allAddresses():
                if ip_address != QtNetwork.QHostAddress.LocalHost and ip_address.toIPv4Address() != 0:
                    break
                else:
                    ip_address = QtNetwork.QHostAddress.LocalHost
            self.host = ip_address

        self.tcp_server = QtNetwork.QTcpServer()  # Create a server object
        self.tcp_server.newConnection.connect(self._new_connection)  # Handler for a new connection

        self.tcp_server.listen(self.host, int(self.port))  # Start listening for connections
        self.conStatSigS.emit("Waiting")  # Indicate that the server is listening on the GUI
        self.logger.debug("Stellarium server connection initializer called")

    # Whenever there is new connection, we call this method
    def _new_connection(self):
        if self.tcp_server.hasPendingConnections():
            self.socket = self.tcp_server.nextPendingConnection()  # Returns a new QTcpSocket

            if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.tcp_server.close()  # Stop listening for other connections
                self.conStatSigS.emit("Connected")  # Indicate that the server has a connection on the GUI
                self.sendDataStell.connect(self.send)  # Connect the signal trigger for data sending
                self.socket.readyRead.connect(self._receive)  # If there is pending data get it
                self.socket.error.connect(self._error)  # Log any error occurred and also perform the necessary actions
                self.socket.disconnected.connect(self._disconnected)  # Execute the appropriate code on state change
                self.logger.info("Server has new connection")

    # Should we have data pending to be received, this method is called
    def _receive(self):
        try:
            while self.socket.bytesAvailable() > 0:
                received_data = self.socket.read(20)  # Get the data as a binary array (we expect 20 bytes each time)
                received_data = self.data_handle.decode(received_data)  # Decode the Stellarium data to get coordinates
                self.dataShowSigS.emit(received_data[0], received_data[1])  # Send the data to be shown on the GUI
                self.sendClientConn.emit(received_data)  # Emit the signal to send the data to the raspberry pi
        except Exception:
            # If data is sent fast, then an exception will occur
            self.logger.exception("An exception occurred at data reception. See traceback.")

    # If at any moment the connection state is changed, we call this method
    def _disconnected(self):
        # Do the following if the connection is lost
        self.conStatSigS.emit("Waiting")  # Indicate that the server does not have a connection on the GUI
        self.socket.readyRead.disconnect()  # Close the signal since it not needed
        self.sendDataStell.disconnect()  # Detach the signal to avoid any accidental firing
        self.tcp_server.listen(self.host, int(self.port))  # Start listening again
        self.logger.warning("Stellarium client disconnected")

    def _error(self):
        # Print and log any error occurred
        self.logger.error("Stellarium server reported an error: %s", self.socket.errorString())

    # Thsi method is called whenever the signal to send data back is fired
    @QtCore.pyqtSlot(float, float, name='stellariumDataSend')
    def send(self, ra: float, dec: float):
        try:
            if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.socket.write(self.data_handle.encode(ra, dec))  # Send data back to Stellarium
                self.socket.waitForBytesWritten()  # Wait for the data to be written
                self.logger.debug("Data sent to Stellarium: RA=%.5f, DEC=%.5f", ra, dec)
        except Exception:
            self.logger.exception("Problem sending data to Stellarium. See traceback.")

    # This method is called whenever the thread exits
    def close(self):
        if self.socket is not None:
            self.socket.disconnected.disconnect()  # Close the disconnect signal first to avoid firing
            if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.sendDataStell.disconnect()  # Disconnect to avoid any accidental firing (Reconnected at start)
            self.socket.close()  # Close the underlying TCP socket
        self.reConnectSigS.disconnect()  # Not needed any more since we are closing
        self.conStatSigS.emit("Disconnected")  # Indicate disconnection on the GUI
        self.logger.info("Stellarium server thread closed")  # Indicate that we closed
