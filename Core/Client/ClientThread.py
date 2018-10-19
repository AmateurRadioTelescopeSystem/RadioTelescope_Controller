from PySide2 import QtCore, QtNetwork
import logging


class ClientThread(QtCore.QObject):
    # Create the signals to be used for data handling
    conStatSigC = QtCore.Signal(str, name='conClientStat')  # Connection indication signal
    dataRcvSigC = QtCore.Signal(str, name='dataClientRX')  # Send the received data out
    sendData = QtCore.Signal(str, name='sendDataClient')  # Data to be sent to the server
    reConnectSigC = QtCore.Signal(name='reConnectClient')  # A reconnection signal originating from a button press
    newConInitComms = QtCore.Signal(name='sendNewConCommands')  # Send the initial commands on each new connection

    def __init__(self, cfgData, parent=None):
        super(ClientThread, self).__init__(parent)  # Get the parent of the class
        self.cfgData = cfgData  # Create a variable for the cfg file
        self.log = logging.getLogger(__name__)  # Create the logger

    def start(self):
        mut = QtCore.QMutex()  # Create a QMutex object
        mut.lock()  # Lock the thread until it has started, to avoid any overlapping problems
        self.log.info("Client thread started")  # Indicate thread start
        self.sock = QtNetwork.QTcpSocket()  # Create the TCP socket
        self.reConnectSigC.connect(self.connectCl)  # Do the reconnect signal connection
        self.connectCl()  # Start a connection
        mut.unlock()  # Unlock the thread, since it has started successfully

    # The connect function is called if the signal is fired or in the start of the thread
    @QtCore.Slot(name='reConnectClient')
    def connectCl(self):
        self.log.debug("Client connection initializer called")
        if self.sock.state() != QtNetwork.QAbstractSocket.ConnectedState:
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
                self.conStatSigC.emit("Disconnected")  # Indicate that we are not connected
                self.log.warning("Client was unable to connect to: %s:%s" % (host, port))

    @QtCore.Slot(str, name='sendDataClient')
    def sendC(self, data: str):
        if self.sock.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.sock.write(data.encode('utf-8'))  # Send the data to the server
            self.log.debug("Data sent to RPi server: %s" % data)

    def _receive(self):
        while self.sock.bytesAvailable() > 0:  # Read all data in que
            string = self.sock.readLine().data().decode('utf-8').rstrip('\n')  # Get the data as a string
            self.dataRcvSigC.emit(string)  # Decode the data to a string
            self.log.debug("Client received: %s" % string)

    def _disconnected(self):
        self.conStatSigC.emit("Disconnected")  # Indicate disconnection on the GUI
        self.sendData.disconnect()  # Detach the data sending signal to avoid accidental firing
        self.log.warning("Client disconnected from server or connection broken")

    def _hostConnected(self):
        self.sendData.connect(self.sendC)  # Send the data to the server when this signal is fired
        self.sendData.emit("CONNECT_CLIENT\n")  # Tell the RPi to connect the client, since the local server should be running
        self.sendData.emit("SEND_POS_UPDATE\n")  # Send the position report request
        self.sendData.emit("REPORT_MOTOR_STATUS\n")  # Send the status of the motors
        self.conStatSigC.emit("Connected")  # If we have a connection send the signal
        self.newConInitComms.emit()  # Send the signal to send the initial commands
        self.log.info("Client connected to server")

    def _error(self):
        # Log any error occurred
        self.log.error("Client reported an error: %s" % self.sock.errorString())

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
        self.log.info("Client thread closed")
