import logging
from PyQt5 import QtCore, QtNetwork


class ClientThread(QtCore.QObject):
    # Create the signals to be used for data handling
    conStatSigC = QtCore.pyqtSignal(str, name='conClientStat')  # Connection indication signal
    dataRcvSigC = QtCore.pyqtSignal(str, name='dataClientRX')  # Send the received data out
    sendData = QtCore.pyqtSignal(str, name='sendDataClient')  # Data to be sent to the server
    reConnectSigC = QtCore.pyqtSignal(name='reConnectClient')  # A reconnection signal originating from a button press
    newConInitComms = QtCore.pyqtSignal(name='sendNewConCommands')  # Send the initial commands on each new connection

    def __init__(self, cfg_data, parent=None):
        super(ClientThread, self).__init__(parent)  # Get the parent of the class
        self.cfg_data = cfg_data  # Create a variable for the cfg file
        self.logger = logging.getLogger(__name__)  # Create the logger

    def start(self):
        mutex = QtCore.QMutex()  # Create a QMutex object
        mutex.lock()  # Lock the thread until it has started, to avoid any overlapping problems
        self.logger.info("Client thread started")  # Indicate thread start
        self.sock = QtNetwork.QTcpSocket()  # Create the TCP socket
        self.reConnectSigC.connect(self.connect_client)  # Do the reconnect signal connection
        self.connect_client()  # Start a connection
        mutex.unlock()  # Unlock the thread, since it has started successfully

    # The connect function is called if the signal is fired or in the start of the thread
    @QtCore.pyqtSlot(name='reConnectClient')
    def connect_client(self):
        self.logger.debug("Client connection initializer called")
        if self.sock.state() != QtNetwork.QAbstractSocket.ConnectedState:
            # Get the host and port from the settings file for the client connection
            host = self.cfg_data.get_tcp_client_host()
            port = self.cfg_data.get_tcp_client_port()

            self.sock = QtNetwork.QTcpSocket()  # Create the TCP socket
            self.sock.readyRead.connect(self._receive)  # Data que signal
            self.sock.connected.connect(self._host_connected)  # What to do when we have connected
            self.sock.error.connect(self._error)  # Log any error occurred and also perform the necessary actions
            self.sock.disconnected.connect(self._disconnected)  # If there is state change then call the function

            self.conStatSigC.emit("Connecting")  # Indicate that we are attempting a connection
            self.sock.connectToHost(QtNetwork.QHostAddress(host), int(port))  # Attempt to connect to the server

            if not self.sock.waitForConnected(msecs=1000):  # Wait a until connected (the function is waiting for 1 sec)
                self.conStatSigC.emit("Disconnected")  # Indicate that we are not connected
                self.logger.warning("Client was unable to connect to: %s:%s", host, port)

    @QtCore.pyqtSlot(str, name='sendDataClient')
    def send_c(self, data: str):
        if self.sock.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.sock.write(data.encode('utf-8'))  # Send the data to the server
            self.logger.debug("Data sent to RPi server: %s", data)

    def _receive(self):
        while self.sock.bytesAvailable() > 0:  # Read all data in que
            string = self.sock.readLine().data().decode('utf-8').rstrip('\n')  # Get the data as a string
            self.dataRcvSigC.emit(string)  # Decode the data to a string
            self.logger.debug("Client received: %s", string)

    def _disconnected(self):
        self.conStatSigC.emit("Disconnected")  # Indicate disconnection on the GUI
        self.sendData.disconnect()  # Detach the data sending signal to avoid accidental firing
        self.logger.warning("Client disconnected from server or connection broken")

    def _host_connected(self):
        self.sendData.connect(self.send_c)  # Send the data to the server when this signal is fired
        self.sendData.emit("CONNECT_CLIENT\n")  # Tell the RPi to connect the client
        self.sendData.emit("SEND_POS_UPDATE\n")  # Send the position report request
        self.sendData.emit("REPORT_MOTOR_STATUS\n")  # Send the status of the motors
        self.conStatSigC.emit("Connected")  # If we have a connection send the signal
        self.newConInitComms.emit()  # Send the signal to send the initial commands
        self.logger.info("Client connected to server")

    def _error(self):
        # Log any error occurred
        self.logger.error("Client reported an error: %s", self.sock.errorString())

    # This method is called when the thread exits
    def close(self):
        self.sock.disconnected.disconnect()  # Disconnect this signal first to avoid getting in the function
        if self.sock.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.sendData.disconnect()  # Disconnect the data send signal, since the thread is closing
            self.sock.disconnectFromHost()  # Disconnect from the host
            # self.sock.waitForDisconnected(msecs=1000)  # And wait until disconnected or timeout (default 3 seconds)
        else:
            self.sock.close()  # Close the socket before exiting
        self.reConnectSigC.disconnect()  # Thread is closing so it will not be needed any more
        self.conStatSigC.emit("Disconnected")  # Indicate a disconnected state on the GUI
        self.logger.info("Client thread closed")
