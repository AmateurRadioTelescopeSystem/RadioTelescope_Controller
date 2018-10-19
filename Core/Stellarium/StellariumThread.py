from Stellarium import StellariumDataHandling
from PySide2 import QtCore, QtNetwork
import logging


class StellThread(QtCore.QObject):
    # Create the signals to be used for data handling
    conStatSigS = QtCore.Signal(str, name='conStellStat')  # Stellarium connection status indication signal
    dataShowSigS = QtCore.Signal(float, float, name='dataStellShow')  # Coordinates show in the GUI
    sendClientConn = QtCore.Signal(list, name='clientCommandSendStell')  # Send the command to the radio telescope
    sendDataStell = QtCore.Signal(float, float, name='stellariumDataSend')  # Send the data to Stellarium
    reConnectSigS = QtCore.Signal(name='reConnectStell')  # A reconnection signal originating from a button press

    def __init__(self, cfgData, parent = None):
        super(StellThread, self).__init__(parent)  # Get the parent of the class
        self.cfgData = cfgData  # Settings file object
        self.logD = logging.getLogger(__name__)  # Create the logger

    # This method is called in every thread start
    def start(self):
        mut = QtCore.QMutex()  # Create a QMutex object
        mut.lock()  # Lock the thread until it has started, to avoid any overlapping problems
        self.logD.info("Stellarium server thread started")
        self.socket = None  # Create the instance os the socket variable to use it later
        self.dataHandle = StellariumDataHandling.StellariumData()  # Data conversion object
        self.reConnectSigS.connect(self.connectStell)  # Connect the signal to the connection function
        self.connectStell()  # Start the Stellarium server
        mut.unlock()  # Unlock the thread, since it has started successfully

    @QtCore.Slot(name='reConnectStell')
    def connectStell(self):
        # Get the saved data from the settings file
        self.host = self.cfgData.getStellHost()  # Get the TCP connection host
        self.port = self.cfgData.getStellPort()  # Get the TCP connection port

        if self.host == "localhost" or self.host == "127.0.0.1":
            self.host = QtNetwork.QHostAddress.LocalHost
        else:
            for ipAddress in QtNetwork.QNetworkInterface.allAddresses():
                if ipAddress != QtNetwork.QHostAddress.LocalHost and ipAddress.toIPv4Address() != 0:
                    break
                else:
                    ipAddress = QtNetwork.QHostAddress.LocalHost
            self.host = ipAddress

        self.tcpServer = QtNetwork.QTcpServer()  # Create a server object
        self.tcpServer.newConnection.connect(self._new_connection)  # Handler for a new connection

        self.tcpServer.listen(self.host, int(self.port))  # Start listening for connections
        self.conStatSigS.emit("Waiting")  # Indicate that the server is listening on the GUI
        self.logD.debug("Stellarium server connection initializer called")

    # Whenever there is new connection, we call this method
    def _new_connection(self):
        if self.tcpServer.hasPendingConnections():
            self.socket = self.tcpServer.nextPendingConnection()  # Returns a new QTcpSocket

            if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.tcpServer.close()  # Stop listening for other connections
                self.conStatSigS.emit("Connected")  # Indicate that the server has a connection on the GUI
                self.sendDataStell.connect(self.send)  # Connect the signal trigger for data sending
                self.socket.readyRead.connect(self._receive)  # If there is pending data get it
                self.socket.error.connect(self._error)  # Log any error occurred and also perform the necessary actions
                self.socket.disconnected.connect(self._disconnected)  # Execute the appropriate code on state change
                self.logD.info("Server has new connection")

    # Should we have data pending to be received, this method is called
    def _receive(self):
        try:
            while self.socket.bytesAvailable() > 0:
                recData = self.socket.read(20)  # Get the data as a binary array (we expect 20 bytes each time)
                recData = self.dataHandle.decodeStell(recData)  # Decode the Stellarium data to get coordinates
                self.dataShowSigS.emit(recData[0], recData[1])  # Send the data to be shown on the GUI widget
                self.sendClientConn.emit(recData)  # Emit the signal to send the data to the raspberry pi
        except Exception:
            # If data is sent fast, then an exception will occur
            self.logD.exception("An exception occurred at data reception. See traceback.")

    # If at any moment the connection state is changed, we call this method
    def _disconnected(self):
        # Do the following if the connection is lost
        self.conStatSigS.emit("Waiting")  # Indicate that the server does not have a connection on the GUI
        self.socket.readyRead.disconnect()  # Close the signal since it not needed
        self.sendDataStell.disconnect()  # Detach the signal to avoid any accidental firing
        self.tcpServer.listen(self.host, int(self.port))  # Start listening again
        self.logD.warning("Stellarium client disconnected")

    def _error(self):
        # Print and log any error occurred
        self.logD.error("Stellarium server reported an error: %s" % self.socket.errorString())

    # Thsi method is called whenever the signal to send data back is fired
    @QtCore.Slot(float, float, name='stellariumDataSend')
    def send(self, ra: float, dec: float):
        try:
            if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.socket.write(self.dataHandle.encodeStell(ra, dec))  # Send data back to Stellarium
                self.socket.waitForBytesWritten()  # Wait for the data to be written
                self.logD.debug("Data sent to Stellarium: RA=%.5f, DEC=%.5f" % (ra, dec))
        except Exception:
            self.logD.exception("Problem sending data to Stellarium. See traceback.")

    # This method is called whenever the thread exits
    def close(self):
        if self.socket is not None:
            self.socket.disconnected.disconnect()  # Close the disconnect signal first to avoid firing
            if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.sendDataStell.disconnect()  # Disconnect to avoid any accidental firing (Reconnected at start)
            self.socket.close()  # Close the underlying TCP socket
        self.reConnectSigS.disconnect()  # Not needed any more since we are closing
        self.conStatSigS.emit("Disconnected")  # Indicate disconnection on the GUI
        self.logD.info("Stellarium server thread closed")  # Indicate that we closed

