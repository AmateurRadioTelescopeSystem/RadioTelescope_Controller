from Stellarium import StellariumDataHandling
from PyQt5 import QtCore, QtNetwork
import logData


class StellThread(QtCore.QObject):
    # Create the signals to be used for data handling
    conStatSigS = QtCore.pyqtSignal(str, name='conStellStat')  # Stellarium connection status indication signal
    dataShowSigS = QtCore.pyqtSignal(float, float, name='dataStellShow')  # Coordinates show in the GUI
    sendClientConn = QtCore.pyqtSignal(list, name='clientCommandSendStell')  # Send the command to the radio telescope

    def __init__(self, cfgData, parent = None):
        super(StellThread, self).__init__(parent)  # Get the parent of the class
        self.cfgData = cfgData  # Settings file object
        self.logD = logData.logData(__name__)  # Create the logger

    # This method is called in every thread start
    def start(self):
        self.dataHandle = StellariumDataHandling.StellariumData()  # Data conversion object

        # Get the saved data from the settings file
        self.host = self.cfgData.getStellHost()  # Get the TCP connection host
        self.port = self.cfgData.getStellPort()  # Get the TCP connection port

        self.tcpServer = QtNetwork.QTcpServer()  # Create a server object
        self.tcpServer.newConnection.connect(self.new_connection)  # Handler for a new connection

        self.tcpServer.listen(QtNetwork.QHostAddress(self.host), int(self.port))  # Start listening for connections
        self.conStatSigS.emit("Waiting")  # Indicate that the server is listening on the GUI

    # Whenever there is new connection, we call this method
    def new_connection(self):
        if self.tcpServer.hasPendingConnections():
            self.socket = self.tcpServer.nextPendingConnection()  # Returns a new QTcpSocket

            if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.conStatSigS.emit("Connected")  # Indicate that the server has a connection on the GUI
                self.socket.readyRead.connect(self._receive)  # If there is pending data get it
                self.socket.stateChanged.connect(self._stateChange)  # Execute the appropriate code on state change
                self.tcpServer.close()  # Stop listening for other connections

    # Should we have data pending to be received, this method is called
    def _receive(self):
        try:
            if self.socket.bytesAvailable() > 0:
                recData = self.socket.readAll()  # Get the data sa a binary array
                recData = self.dataHandle.decodeStell(recData)  # Decode the Stellarium data to get coordinates
                self.dataShowSigS.emit(recData[0], recData[1])  # Send the data to be shown on the GUI widget
                self.sendClientConn.emit(recData)  # Emit the signal to send the data to the raspberry pi
        except Exception:
            # If data is sent fast, then an exception will occur
            self.logD.log("EXCEPT", "Some problem occurred while receiving Stellarium data. See traceback.", "_receive")

    # If at any moment the connection state is changed, we call this method
    def _stateChange(self):
        # Do the following if the connection is lost
        if self.socket.state() == QtNetwork.QAbstractSocket.UnconnectedState:
            self.conStatSigS.emit("Waiting")  # Indicate that the server does not have a connection on the GUI
            self.tcpServer.listen(QtNetwork.QHostAddress(self.host), int(self.port))  # Start listening again

    ''''@QtCore.pyqtSlot(float, float, name='clientCommandSendStell')
    def send(self, ra: float, dec: float):
        try:
            self.socket.write(self.dataHandle.encodeStell(ra, dec))  # Send data back to Stellarium
            self.socket.waitForBytesWritten()  # Wait for the data to be written
        except Exception as e:
            print("Stellarium send client issue")
            print(e)'''

    # This method is called whenever the thread exits
    def close(self):
        self.socket.close()  # Close the underlying TCP socket
        self.tcpServer.close()  # Close the TCP server
        self.conStatSigS.emit("Disconnected")  # Indicate disconnection on the GUI

