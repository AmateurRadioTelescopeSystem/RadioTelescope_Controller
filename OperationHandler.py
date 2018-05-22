from PyQt5 import QtCore
from functools import partial
import logging


class OpHandler(QtCore.QObject):
    posDataShow = QtCore.pyqtSignal(float, float, name='posDataShow')

    def __init__(self, tcpClient, tcpServer, tcpStellarium, tcpClThread, tcpServThread,
                 tcpStelThread, ui, cfgData, parent=None):
        super(OpHandler, self).__init__(parent)
        self.tcpClient = tcpClient  # TCP client object
        self.tcpServer = tcpServer  # TCP RPi server object
        self.tcpStellarium = tcpStellarium  # TCP Stellarium server object

        # Create the thread varaible for the class
        self.tcpClThread = tcpClThread
        self.tcpServThread = tcpServThread
        self.tcpStelThread = tcpStelThread

        self.ui = ui  # User interface handling object
        self.cfgData = cfgData
        self.logD = logging.getLogger(__name__)  # Data logger object

    def start(self):
        self.logD.info("Operations handler thread started")

        self.prev_pos = ["", ""]  # The dish position is saved for change comparison
        self.signalConnectios()  # Make all the necessary signal connections
        self.ui.mainWin.actionSettings.triggered.connect(self.TCPSettingsHandle)  # Update settings each time

        autoconStell = self.cfgData.getTCPStellAutoConnStatus()  # See if auto-connection at startup is enabled
        autoconRPi = self.cfgData.getTCPAutoConnStatus()  # Auto-connection preference for the RPi server and client

        # If auto-connection is selected for thr TCP section, then do as requested
        if autoconStell == "yes":
            self.tcpStelThread.start()  # Start the server thread, since auto start is enabled
        if autoconRPi == "yes":
            self.tcpClThread.start()  # Start the client thread, since auto start is enabled
            self.tcpServThread.start()  # Start the RPi server thread, since auto start is enabled

    # Client connection button handling method
    def connectButtonR(self):
        if self.tcpClThread.isRunning() and \
                (self.ui.mainWin.connectRadioTBtn.text() == "Disconnect" or self.ui.mainWin.connectRadioTBtn.text() == "Stop"):
            self.tcpClThread.quit()  # Disconnect from the client
        elif not self.tcpClThread.isRunning():
            self.tcpClThread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            self.tcpClient.reConnectSigC.emit()

    # Stellarium server connection handling method
    def connectButtonS(self):
        if self.tcpStelThread.isRunning() and \
                (self.ui.mainWin.connectStellariumBtn.text() == "Disable" or self.ui.mainWin.connectStellariumBtn.text() == "Stop"):
            self.tcpStelThread.quit()  # Quit the currently running thread
        elif not self.tcpStelThread.isRunning():
            self.tcpStelThread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            self.tcpStellarium.reConnectSigS.emit()

    # RPi server connection handling method
    def connectButtonRPi(self):
        if self.tcpServThread.isRunning() and \
                (self.ui.mainWin.serverRPiConnBtn.text() == "Disable" or self.ui.mainWin.serverRPiConnBtn.text() == "Stop"):
            self.tcpServThread.quit()  # Quit the currently running thread
        elif not self.tcpServThread.isRunning():
            self.tcpServThread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            self.tcpServer.reConnectSigR.emit()

    # Dta received from the client connected to the RPi server
    @QtCore.pyqtSlot(str, name='dataClientRX')
    def clientDataRx(self, data: str):
        splt_str = data.split("_")
        if len(splt_str) > 0:
            if splt_str[0] == "RASTEPS":
                self.ui.uiManContWin.raStepText.setText(splt_str[1])
            elif splt_str[0] == "DECSTEPS":
                self.ui.uiManContWin.decStepText.setText(splt_str[1])
        else:
            self.logD.debug("Data received from client (Connected to remote RPi server): %s" % data)

    # Send the appropriate command according to the selected mode. Data is received from Stellarium (sendClientConn)
    @QtCore.pyqtSlot(list, name='clientCommandSendStell')
    def stellCommSend(self, radec: list):
        if self.ui.mainWin.stellariumOperationSelect.currentText() == "Transit":
            command = "TRNST_RA_%.5f_DEC_%.5f\n" % (radec[0], radec[1])
            self.tcpClient.sendData.emit(command)
        elif self.ui.mainWin.stellariumOperationSelect.currentText() == "Aim and track":
            command = "TRK %f %f\n" % (radec[0], radec[1])
            self.tcpClient.sendData.emit(command)

    # Received data from the server that the RPi is connected as a client. Signal is (dataRxFromServ)
    @QtCore.pyqtSlot(str, name='rpiServDataRx')
    def rpiServRcvData(self, data: str):
        spltData = data.split("_")  # Split the string with the set delimiter
        if spltData[0] == "DISHPOS" or spltData[0] == "POSUPDATE":
            ra = spltData[2]  # Get the RA from the received position
            dec = spltData[4]  # Get the DEC from the received position
            if not (self.prev_pos[0] == ra and self.prev_pos[1] == dec and spltData[0] != "POSUPDATE"):
                self.tcpStellarium.sendDataStell.emit(float(ra), float(dec))  # Send the position to Stellarium
                self.posDataShow.emit(float(ra), float(dec))  # Send the updated values if they are different
            self.prev_pos = [ra, dec]  # Save the values for later comparison

    # Functions to connect with the manual control widget
    # TODO add comments to the functions
    def manCont_movRA(self):
        freq = self.ui.uiManContWin.frequncyInputBox.text()
        step = self.ui.uiManContWin.raStepsField.text()
        string = "MANCONT_MOVRA_%s_%s_0\n" %(freq, step)
        self.tcpClient.sendData.emit(string)

    def manCont_movDEC(self):
        freq = self.ui.uiManContWin.frequncyInputBox.text()
        step = self.ui.uiManContWin.decStepsField.text()
        string = "MANCONT_MOVDEC_%s_0_%s\n" %(freq, step)
        self.tcpClient.sendData.emit(string)

    def manCont_movBoth(self):
        freq = self.ui.uiManContWin.frequncyInputBox.text()
        step_ra = self.ui.uiManContWin.raStepsField.text()
        step_dec = self.ui.uiManContWin.decStepsField.text()
        string = "MANCONT_MOVE_%s_%s_%s\n" %(freq, step_ra, step_dec)
        self.tcpClient.sendData.emit(string)

    def manCont_stop(self):
        string ="MANCONT_STOP\n"
        self.tcpClient.sendData.emit(string)  # Send the stop request in manual control

    # Command to stop any motion of the radio telescope dish
    @QtCore.pyqtSlot(name='stopRadioTele')
    def stopMovingRT(self):
        # TODO change the command to the appropriate one
        self.tcpClient.sendData.emit("STOP")  # Send the request to stop moving to the RPi server
        self.logD.warning("A dish motion halt was requested")

    def TCPSettingsHandle(self):
        autoconStell = self.cfgData.getTCPStellAutoConnStatus()  # See if auto-connection at startup is enabled
        autoconRPi = self.cfgData.getTCPAutoConnStatus()  # Auto-connection preference for the RPi server and client
        clientIP = self.cfgData.getHost()
        servRPiIP = self.cfgData.getRPiHost()
        stellServIP = self.cfgData.getStellHost()

        # If auto-connection is selected for thr TCP section, then do as requested
        if autoconStell == "yes":
            self.ui.uiTCPWin.stellServAutoStartBtn.setChecked(True)
        if autoconRPi == "yes":
            self.ui.uiTCPWin.teleAutoConChoice.setChecked(True)

        if clientIP == "localhost" or clientIP == "127.0.0.1":
            self.ui.uiTCPWin.telClientBox.setCurrentIndex(0)
        else:
            self.ui.uiTCPWin.telClientBox.setCurrentIndex(1)

        if servRPiIP == "localhost" or servRPiIP == "127.0.0.1":
            self.ui.uiTCPWin.telServBox.setCurrentIndex(0)
        elif servRPiIP == "remote":
            self.ui.uiTCPWin.telServBox.setCurrentIndex(1)
        else:
            self.ui.uiTCPWin.telServBox.setCurrentIndex(2)

        if stellServIP == "localhost" or stellServIP == "127.0.0.1":
            self.ui.uiTCPWin.stellIPServBox.setCurrentIndex(0)
        else:
            self.ui.uiTCPWin.stellIPServBox.setCurrentIndex(1)

        # Set all the text fields with the correct data
        self.ui.uiTCPWin.telescopeIPAddrClient.setText(clientIP)
        self.ui.uiTCPWin.telescopeIPPortClient.setText(self.cfgData.getPort())
        self.ui.uiTCPWin.telescopeIPAddrServ.setText(servRPiIP)
        self.ui.uiTCPWin.telescopeIPPortServ.setText(self.cfgData.getRPiPort())
        self.ui.uiTCPWin.stellServInpIP.setText(stellServIP)
        self.ui.uiTCPWin.stellPortServ.setText(self.cfgData.getStellPort())

    # Make all the necessary signal connections
    def signalConnectios(self):
        self.tcpStellarium.sendClientConn.connect(self.stellCommSend)  # Send data from Stellarium to the RPi
        self.tcpClient.dataRcvSigC.connect(self.clientDataRx)  # Receive pending data from RPi connected client

        self.tcpServer.dataRxFromServ.connect(self.rpiServRcvData)  # Receive data from the RPi server
        self.tcpServer.clientNotice.connect(self.tcpClient.connect)  # Tell the client to reconnect

        self.ui.stopMovingRTSig.connect(self.stopMovingRT)  # Send a motion stop command, once this signal is triggered
        self.ui.mainWin.stellPosUpdtBtn.clicked.connect(partial(self.tcpClient.sendData.emit, "SEND_POS_UPDATE"))
        self.posDataShow.connect(self.ui.posDataShow)  # Show the dish position data, when available

        # Give functionality to the buttons
        self.ui.mainWin.connectRadioTBtn.clicked.connect(self.connectButtonR)  # TCP client connection button
        self.ui.mainWin.serverRPiConnBtn.clicked.connect(self.connectButtonRPi)  # TCP server connection button
        self.ui.mainWin.connectStellariumBtn.clicked.connect(
            self.connectButtonS)  # Stellarium TCP server connection button

        self.ui.uiManContWin.movRaBtn.clicked.connect(self.manCont_movRA)
        self.ui.uiManContWin.movDecBtn.clicked.connect(self.manCont_movDEC)
        self.ui.uiManContWin.syncMoveBtn.clicked.connect(self.manCont_movBoth)
        self.ui.uiManContWin.stopMotMotionBtn.clicked.connect(self.manCont_stop)

        self.logD.debug("All signal connections made")

    # This function is called whenever the app is about to quit
    # First quit from the thread and then delete both the thread and the corresponding object
    # Quit exits the thread and then wait is waiting for the thread exit
    # deleteLater, deletes the thread object and the threaded object
    def appExitRequest(self):
        self.tcpClThread.quit()
        self.tcpClThread.wait()
        self.tcpClient.deleteLater()
        self.tcpClThread.deleteLater()
        self.logD.debug("Client thread is closed for sure")

        self.tcpServThread.quit()
        self.tcpServThread.wait()
        self.tcpServer.deleteLater()
        self.tcpServThread.deleteLater()
        self.logD.debug("RPi server thread is surely closed")

        self.tcpStelThread.quit()
        self.tcpStelThread.wait()
        self.tcpStellarium.deleteLater()
        self.tcpStelThread.deleteLater()
        self.logD.debug("Stellarium server thread is closed for sure and operations handler thread closed")
