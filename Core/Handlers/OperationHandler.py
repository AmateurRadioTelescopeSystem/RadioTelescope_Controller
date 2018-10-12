from PyQt5 import QtCore, QtNetwork
from Astronomy import Astronomy
from Handlers import SimulationHandler
from functools import partial
import logging


class OpHandler(QtCore.QObject):
    posDataShow = QtCore.pyqtSignal(float, float, name='posDataShow')

    def __init__(self, tcpClient, tcpServer, tcpStellarium, tcpClThread, tcpServThread,
                 tcpStelThread, ui, cfgData, parent=None):
        """
        Operations handler class constructor.
        :param tcpClient:
        :param tcpServer:
        :param tcpStellarium:
        :param tcpClThread:
        :param tcpServThread:
        :param tcpStelThread:
        :param ui:
        :param cfgData:
        :param parent:
        """
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
        self.astronomy = Astronomy.Calculations(cfg_data=cfgData)  # Astronomy calculations object
        self.prev_pos = ["", ""]  # The dish position is saved for change comparison
        self.motors_enabled = False  # Keep the motor status

        self.max_steps_to_targ_ra = 0
        self.max_steps_to_targ_dec = 0
        self.simStarted = False

        # Simulation thread operations
        self.simThread = QtCore.QThread()
        self.simHandler = SimulationHandler.SimulHandler(tcpStellarium)
        self.simHandler.moveToThread(self.simThread)
        self.simThread.started.connect(self.simHandler.start)
        self.simThread.finished.connect(self.simHandler.close)
        self.simThread.start()  # Start the simulation thread

        self.ui.sky_scan_win.textBrowser.setText(
            "<html><table><tbody><tr><td style=\"width: 36px;\" colspan=\"2\">"
            "<strong>System</strong></td><td style=\"width: 10px;\">&nbsp;</td>"
            "<td style=\"width: 49px;\" colspan=\"2\"><strong>Equatorial</strong>"
            "</td></tr><tr><td style=\"width: 26px;\"><strong>C1</strong></td>"
            "<td style=\"width: 10px;\"><strong>C2</strong></td><td style=\"width: 10px;\">&nbsp;</td>"
            "<td style=\"width: 20px;\"><strong>RA</strong></td><td style=\"width: 29px;\">"
            "<strong>DEC</strong></td></tr><tr><td style=\"width: 26px;\">&nbsp;</td>"
            "<td style=\"width: 10px;\">&nbsp;</td><td style=\"width: 10px;\">&nbsp;</td>"
            "<td style=\"width: 20px;\">&nbsp;</td><td style=\"width: 29px;\">&nbsp;</td></tr><tr>"
            "<td style=\"width: 26px;\">&nbsp;</td><td style=\"width: 10px;\">&nbsp;</td>"
            "<td style=\"width: 10px;\">&nbsp;</td><td style=\"width: 20px;\">&nbsp;</td>"
            "<td style=\"width: 29px;\">&nbsp;</td></tr></tbody></table><p>&nbsp;</p></html>")

    def start(self):
        """
        Initializer of the thread.
        Make all the necessary initializations when the thread starts
        :return: Nothing
        """
        self.logD.info("Operations handler thread started")
        self.signalConnections()  # Make all the necessary signal connections

        autoconStell = self.cfgData.getTCPStellAutoConnStatus()  # See if auto-connection at startup is enabled
        autoconRPi = self.cfgData.getTCPAutoConnStatus()  # Auto-connection preference for the RPi server and client

        # Try to get a new TLE, if the one we have is outdated
        self.ui.tleStatusInfoSig.emit("")  # Just initialize the widget
        tle_result = self.astronomy.tle_retriever()
        if tle_result[0] is True:
            tle_status_msg = "Success^TLE file(s) updated"
        else:
            tle_status_msg = "Error^There was a problem getting TLE file(s).^"
            tle_status_msg += tle_result[1]
        self.ui.tleStatusInfoSig.emit(tle_status_msg)
        while not self.ui.tle_info_widg.clickedButton():
            continue

        # If auto-connection is selected for thr TCP section, then do as requested
        if autoconStell == "yes":
            self.tcpStelThread.start()  # Start the server thread, since auto start is enabled
        if autoconRPi == "yes":
            self.tcpClThread.start()  # Start the client thread, since auto start is enabled
            self.tcpServThread.start()  # Start the RPi server thread, since auto start is enabled

    # Client connection button handling method
    def connectButtonR(self):
        if self.tcpClThread.isRunning() and \
                (self.ui.main_widg.connectRadioTBtn.text() == "Disconnect" or
                 self.ui.main_widg.connectRadioTBtn.text() == "Stop"):
            self.tcpClThread.quit()  # Disconnect from the client
        elif not self.tcpClThread.isRunning():
            self.tcpClThread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            self.tcpClient.reConnectSigC.emit()

    # Stellarium server connection handling method
    def connectButtonS(self):
        if self.tcpStelThread.isRunning() and \
                (self.ui.main_widg.connectStellariumBtn.text() == "Disable" or
                 self.ui.main_widg.connectStellariumBtn.text() == "Stop"):
            self.tcpStelThread.quit()  # Quit the currently running thread
        elif not self.tcpStelThread.isRunning():
            self.tcpStelThread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            self.tcpStellarium.reConnectSigS.emit()

    # RPi server connection handling method
    def connectButtonRPi(self):
        if self.tcpServThread.isRunning() and \
                (self.ui.main_widg.serverRPiConnBtn.text() == "Disable" or
                 self.ui.main_widg.serverRPiConnBtn.text() == "Stop"):
            self.tcpServThread.quit()  # Quit the currently running thread
        elif not self.tcpServThread.isRunning():
            self.tcpServThread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            self.tcpServer.reConnectSigR.emit()

    def testConnButton(self):
        if self.ui.tcp_widg.clientConTestChkBox.isChecked():
            self.tcpClient.sendData.emit("Test\n")

    def motorsEnableButton(self):
        if self.motors_enabled:
            self.tcpClient.sendData.emit("DISABLE_MOTORS\n")
        else:
            self.tcpClient.sendData.emit("ENABLE_MOTORS\n")

    @QtCore.pyqtSlot(name='sendNewConCommands')
    def initialCommands(self):
        # TODO add more commands to send, like system check reports and others
        self.tcpClient.sendData.emit("SEND_HOME_STEPS\n")  # Get the steps from home for each motor
        self.tcpClient.sendData.emit("REPORT_MOTOR_STATUS\n")  # Get the current status of the motors

    # Dta received from the client connected to the RPi server
    @QtCore.pyqtSlot(str, name='dataClientRX')
    def clientDataRx(self, data: str):
        """
        Data reception from the TCP client.
        Receive the data sent from client and decide how to act
        :param data: Data received from the client
        :return:
        """
        if data == "MOTORS_ENABLED":
            self.motors_enabled = True
        elif data == "MOTORS_DISABLED":
            self.motors_enabled = False
        else:
            splt_str = data.split("_")  # Try to split the string, and if it splits then a command is sent
            if len(splt_str) > 0:
                if splt_str[0] == "STEPS-FROM-HOME":
                    self.cfgData.setHomeSteps(splt_str[1], splt_str[2])  # Set the current away from home position steps
                    self.ui.setManContStepsSig.emit("RA", splt_str[1])
                    self.ui.setManContStepsSig.emit("DEC", splt_str[2])
                elif splt_str[0] == "MAX-STEPS-TO-DO":
                    if splt_str[1] == "RA":
                        self.max_steps_to_targ_ra = int(splt_str[2])
                        self.max_steps_to_targ_dec = 0
                    elif splt_str[1] == "DEC":
                        self.max_steps_to_targ_dec = int(splt_str[2])
                        self.max_steps_to_targ_ra = 0
            else:
                self.logD.debug("Data received from client (Connected to remote RPi server): %s" % data)
        if type(data) is str:
            self.ui.setGUIFromClientSig.emit(data)  # If it is not split yet, send the command

    @QtCore.pyqtSlot(list, name='clientCommandSendStell')
    def stellCommSend(self, radec: list):
        """
        Send the appropriate command according to the selected mode. Data is received from Stellarium (sendClientConn)
        :param radec: A list containing the data received from Stellarium
        :return: Nothing
        """
        if not self.motors_enabled:
            self.ui.motorsDisabledSig.emit()
        else:
            home_steps = self.cfgData.getHomeSteps()  # Return a list with the steps way from home position
            tr_time = int(self.ui.main_widg.transitTimeValue.text())
            if self.ui.main_widg.stellariumOperationSelect.currentText() == "Transit":
                ra_degrees = radec[0] * 15.0  # Stellarium returns right ascension is hours, so we convert to degrees
                transit_coords = self.astronomy.transit(ra_degrees, radec[1], -int(home_steps[0]), -int(home_steps[1]),
                                                        tr_time)
                command = "TRNST_RA_%.5f_DEC_%.5f\n" % (transit_coords[0], transit_coords[1])
                self.tcpClient.sendData.emit(command)  # Send the transit command to the RPi
            elif self.ui.main_widg.stellariumOperationSelect.currentText() == "Aim and track":
                ra_degrees = radec[0] * 15.0  # Stellarium returns right ascension is hours, so we convert to degrees
                trk_coords = self.astronomy.transit(ra_degrees, radec[1], -int(home_steps[0]), -int(home_steps[1]), 0)
                command = "TRK_RA_%.5f_DEC_%.5f_RA-SPEEDD_%.5f_DEC-SPEED_%.5f\n" % (trk_coords[0], trk_coords[1], 0, 0)
                self.tcpClient.sendData.emit(command)  # Send the tracking command to the RPi

    # Received data from the server that the RPi is connected as a client. Signal is (dataRxFromServ)
    @QtCore.pyqtSlot(str, name='rpiServDataRx')
    def rpiServRcvData(self, data: str):
        """
        Get the data sent from the RPi client.
        Mainly the dish position will be sent
        :param data: Data received from the TCP connection
        :return: Nothing
        """
        # TODO Remove the degree conversion for the RA, since MPU will send in degrees and not hours
        spltData = data.split("_")  # Split the string with the set delimiter
        if spltData[0] == "POSUPDATE":
            ra = self.astronomy.hour_angle_to_ra(float(spltData[2])*15.0)  # Get the RA from the received position
            dec = spltData[4]  # Get the DEC from the received position
            if not (self.prev_pos[0] == ra and self.prev_pos[1] == dec and spltData[0] != "POSUPDATE"):
                self.tcpStellarium.sendDataStell.emit(float(ra)/15.0, float(dec))  # Send the position to Stellarium
                self.posDataShow.emit(float(ra)/15.0, float(dec))  # Send the updated values if they are different
            self.prev_pos = [ra, dec]  # Save the values for later comparison
        elif spltData[0] == "DISHPOS":
            ra_degrees = self.astronomy.hour_angle_to_ra(float(spltData[2])*15.0)  # Get the RA from the received HA
            dec_degrees = spltData[4]  # Get the DEC from the received position
            ra_steps = spltData[7]
            dec_steps = spltData[9]
            self.ui.setManContStepsSig.emit("RA", ra_steps)  # Update the manual control window
            self.ui.setManContStepsSig.emit("DEC", dec_steps)
            self.tcpStellarium.sendDataStell.emit(float(ra_degrees)/15.0, float(dec_degrees))
            self.posDataShow.emit(float(ra_degrees)/15.0, float(dec_degrees))

            # Update the progress bar
            if self.max_steps_to_targ_ra is not 0:
                ratio = int(ra_steps)/self.max_steps_to_targ_ra
                self.ui.main_widg.onTargetProgress.setValue(ratio)
            elif self.max_steps_to_targ_dec is not 0:
                ratio = int(dec_steps)/self.max_steps_to_targ_dec
                self.ui.main_widg.onTargetProgress.setValue(ratio)

    # Command to stop any motion of the radio telescope dish
    @QtCore.pyqtSlot(name='stopRadioTele')
    def stopMovingRT(self):
        # TODO change the command to the appropriate one
        self.tcpClient.sendData.emit("STOP\n")  # Send the request to stop moving to the RPi server
        self.logD.warning("A dish motion halt was requested")

    # Functions to connect with the manual control widget
    # TODO add comments to the functions
    def manCont_movRA(self):
        if not self.motors_enabled:
            self.ui.motorsDisabledSig.emit()
        else:
            freq = self.ui.man_cn_widg.frequncyInputBox.text()
            step = self.ui.man_cn_widg.raStepsField.text()
            string = "MANCONT_MOVRA_%s_%s_0\n" % (freq, step)
            self.tcpClient.sendData.emit(string)

    def manCont_movDEC(self):
        if not self.motors_enabled:
            self.ui.motorsDisabledSig.emit()
        else:
            freq = self.ui.man_cn_widg.frequncyInputBox.text()
            step = self.ui.man_cn_widg.decStepsField.text()
            string = "MANCONT_MOVDEC_%s_0_%s\n" % (freq, step)
            self.tcpClient.sendData.emit(string)

    def manCont_movBoth(self):
        if not self.motors_enabled:
            self.ui.motorsDisabledSig.emit()
        else:
            freq = self.ui.man_cn_widg.frequncyInputBox.text()
            step_ra = self.ui.man_cn_widg.raStepsField.text()
            step_dec = self.ui.man_cn_widg.decStepsField.text()
            string = "MANCONT_MOVE_%s_%s_%s\n" % (freq, step_ra, step_dec)
            self.tcpClient.sendData.emit(string)

    def manCont_stop(self):
        if not self.motors_enabled:
            self.ui.motorsDisabledSig.emit()
        else:
            string = "MANCONT_STOP\n"
            self.tcpClient.sendData.emit(string)  # Send the stop request in manual control

    def TCPSettingsHandle(self):
        autoconStell = self.cfgData.getTCPStellAutoConnStatus()  # See if auto-connection at startup is enabled
        autoconRPi = self.cfgData.getTCPAutoConnStatus()  # Auto-connection preference for the RPi server and client
        clientIP = self.cfgData.getHost()
        stellIP = "127.0.0.1"
        remoteIP = "0.0.0.0"
        servRPiRemote = self.cfgData.getServRemote("TCPRPiServ")
        stellServRemote = self.cfgData.getServRemote("TCPStell")

        # If auto-connection is selected for thr TCP section, then do as requested
        if autoconStell == "yes":
            self.ui.tcp_widg.stellServAutoStartBtn.setChecked(True)
        if autoconRPi == "yes":
            self.ui.tcp_widg.teleAutoConChoice.setChecked(True)

        if clientIP == "localhost" or clientIP == "127.0.0.1":
            self.ui.tcp_widg.telClientBox.setCurrentIndex(0)
        else:
            self.ui.tcp_widg.telClientBox.setCurrentIndex(1)

        if servRPiRemote == "yes" or stellServRemote == "yes":
            for ipAddress in QtNetwork.QNetworkInterface.allAddresses():
                if ipAddress != QtNetwork.QHostAddress.LocalHost and ipAddress.toIPv4Address() != 0:
                    break  # If we found an IP then we exit the loop
                else:
                    ipAddress = QtNetwork.QHostAddress.LocalHost  # If no IP is found, assign localhost
            remoteIP = ipAddress.toString()  # Assign the IP address that wa found above

        if servRPiRemote == "no":
            self.ui.tcp_widg.telServBox.setCurrentIndex(0)
        elif servRPiRemote == "yes":
            self.ui.tcp_widg.telServBox.setCurrentIndex(1)
        elif servRPiRemote == "custom":
            self.ui.tcp_widg.telServBox.setCurrentIndex(2)

        if stellServRemote == "no":
            self.ui.tcp_widg.stellIPServBox.setCurrentIndex(0)
        else:
            stellIP = remoteIP
            self.ui.tcp_widg.stellIPServBox.setCurrentIndex(1)

        # Set all the text fields with the correct data
        # TODO handle what happens when server is not initialized at start
        self.ui.tcp_widg.telescopeIPAddrClient.setText(clientIP)
        self.ui.tcp_widg.telescopeIPPortClient.setText(self.cfgData.getPort())

        self.ui.tcp_widg.telescopeIPAddrServ.setText(remoteIP)
        self.ui.tcp_widg.telescopeIPPortServ.setText(self.cfgData.getRPiPort())

        self.ui.tcp_widg.stellServInpIP.setText(stellIP)
        self.ui.tcp_widg.stellPortServ.setText(self.cfgData.getStellPort())

        # Set the settings for the connection test tab
        if self.tcpClient.sock.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.ui.tcp_widg.clientConTestChkBox.setEnabled(True)
            self.ui.tcp_widg.clientStatLbl.setEnabled(True)
            self.ui.tcp_widg.clientStatus.setEnabled(True)
        else:
            self.ui.tcp_widg.clientConTestChkBox.setEnabled(False)
            self.ui.tcp_widg.clientStatLbl.setEnabled(False)
            self.ui.tcp_widg.clientStatus.setEnabled(False)

        if self.tcpServer.socket is not None:
            if self.tcpServer.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.ui.tcp_widg.serverConTestChkBox.setEnabled(True)
                self.ui.tcp_widg.servStatLbl.setEnabled(True)
                self.ui.tcp_widg.serverStatus.setEnabled(True)
            else:
                self.ui.tcp_widg.serverConTestChkBox.setEnabled(False)
                self.ui.tcp_widg.servStatLbl.setEnabled(False)
                self.ui.tcp_widg.serverStatus.setEnabled(False)
        else:
            self.ui.tcp_widg.serverConTestChkBox.setEnabled(False)
            self.ui.tcp_widg.servStatLbl.setEnabled(False)
            self.ui.tcp_widg.serverStatus.setEnabled(False)

        if self.tcpStellarium.socket is not None:
            if self.tcpStellarium.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.ui.tcp_widg.stellConTestChkBox.setEnabled(True)
                self.ui.tcp_widg.stellStatLbl.setEnabled(True)
                self.ui.tcp_widg.stellariumStatus.setEnabled(True)
            else:
                self.ui.tcp_widg.stellConTestChkBox.setEnabled(False)
                self.ui.tcp_widg.stellStatLbl.setEnabled(False)
                self.ui.tcp_widg.stellariumStatus.setEnabled(False)
        else:
            self.ui.tcp_widg.stellConTestChkBox.setEnabled(False)
            self.ui.tcp_widg.stellStatLbl.setEnabled(False)
            self.ui.tcp_widg.stellariumStatus.setEnabled(False)

    # Save the settings when the save button is pressed
    def saveTCPSettings(self):
        # Save the ports entered for each setting
        self.cfgData.setPort(self.ui.tcp_widg.telescopeIPPortClient.text())
        self.cfgData.setStellPort(self.ui.tcp_widg.stellPortServ.text())
        self.cfgData.setRPiPort(self.ui.tcp_widg.telescopeIPPortServ.text())

        # Save the auto start/enable option
        if self.ui.tcp_widg.teleAutoConChoice.isChecked():
            self.cfgData.TCPAutoConnEnable()
        else:
            self.cfgData.TCPAutoConnDisable()

        if self.ui.tcp_widg.stellServAutoStartBtn.isChecked():
            self.cfgData.TCPStellAutoConnEnable()
        else:
            self.cfgData.TCPStellAutoConnDisable()

        # Save the IP addresses
        if self.ui.tcp_widg.telServBox.currentText() == "Localhost":
            self.cfgData.setRPiHost("127.0.0.1")
            self.cfgData.setServRemote("TCPRPiServ", "no")
        elif self.ui.tcp_widg.telServBox.currentText() == "Remote":
            self.cfgData.setServRemote("TCPRPiServ", "yes")
            self.cfgData.setRPiHost(self.ui.tcp_widg.telescopeIPAddrServ.text())
        elif self.ui.tcp_widg.telServBox.currentText() == "Custom":
            self.cfgData.setServRemote("TCPRPiServ", "custom")
            self.cfgData.setRPiHost(self.ui.tcp_widg.telescopeIPAddrServ.text())

        if self.ui.tcp_widg.telClientBox.currentText() == "Localhost":
            self.cfgData.setHost("127.0.0.1")
            self.cfgData.setServRemote("TCP", "no")
        else:
            self.cfgData.setServRemote("TCP", "yes")
            self.cfgData.setHost(self.ui.tcp_widg.telescopeIPAddrClient.text())

        if self.ui.tcp_widg.stellIPServBox.currentText() == "Localhost":
            self.cfgData.setStellHost("127.0.0.1")
            self.cfgData.setServRemote("TCPStell", "no")
        else:
            self.cfgData.setServRemote("TCPStell", "yes")
            self.cfgData.setStellHost(self.ui.tcp_widg.stellServInpIP.text())

        # Send a reconnect signal to all TCP operations (No effect if some is not active)
        self.tcpClient.reConnectSigC.emit()
        self.tcpServer.reConnectSigR.emit()
        self.tcpStellarium.reConnectSigS.emit()

    def locationSettingsHandle(self):
        s_latlon = self.cfgData.getLatLon()  # First element is latitude and second element is longitude
        s_alt = self.cfgData.getAltitude()  # Get the altitude from the settings file

        self.ui.loc_widg.latEntry.setText(s_latlon[0])
        self.ui.loc_widg.lonEntry.setText(s_latlon[1])
        self.ui.loc_widg.altEntry.setText(s_alt)

        if self.cfgData.getMapsSelect() == "no":
            self.ui.loc_widg.locationTypeChoose.setCurrentIndex(0)

    def saveLocationSettings(self):
        coords = [self.ui.loc_widg.latEntry.text(), self.ui.loc_widg.lonEntry.text()]
        altd = self.ui.loc_widg.altEntry.text()
        self.cfgData.setLatLon(coords)
        self.cfgData.setAltitude(altd)

        if self.ui.loc_widg.locationTypeChoose.currentText() == "Google Maps":
            self.cfgData.setMapsSelect("yes")
        else:
            self.cfgData.setMapsSelect("no")

        # Show location on the GUI
        self.ui.main_widg.lonTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                                             "vertical-align:super;\">o</span></p></body></html>" % coords[1])
        self.ui.main_widg.latTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                                             "vertical-align:super;\">o</span></p></body></html>" % coords[0])
        self.ui.main_widg.altTextInd.setText("<html><head/><body><p align=\"center\">%sm</p></body></html>" % altd)

    def homePositionReturn(self):
        if not self.motors_enabled:
            self.ui.motorsDisabledSig.emit()
        else:
            self.tcpClient.sendData.emit("RETURN_HOME\n")

    def planObjCommand(self):
        if not self.motors_enabled:
            self.ui.motorsDisabledSig.emit()
        else:
            home_steps = self.cfgData.getHomeSteps()
            if self.ui.plan_obj_win.planObjectTransitGroupBox.isChecked():
                objec = self.ui.plan_obj_win.objectSelectionComboBox.currentText()
                tr_time = self.ui.plan_obj_win.transitTimeBox.value()
                transit_coords = self.astronomy.transit_planetary(objec, -int(home_steps[0]), -int(home_steps[1]),
                                                                  int(tr_time))

                command = "TRNST_RA_%.5f_DEC_%.5f\n" % (transit_coords[0], transit_coords[1])
                self.tcpClient.sendData.emit(command)  # Send the transit command to the RPi
            elif self.ui.plan_obj_win.planObjectTrackingGroupBox.isChecked():
                objec = self.ui.plan_obj_win.objectSelectionComboBox.currentText()
                track_time = self.ui.plan_obj_win.trackingtTimeBox.value()
                tracking_info = self.astronomy.tracking_planetary(objec, -int(home_steps[0]), -int(home_steps[1]))

                command = "TRK_RA_%.5f_DEC_%.5f_RA-SPEED_%.5f_DEC-SPEED_%.5f_TIME_%.2f\n" % \
                          (tracking_info[0], tracking_info[1], tracking_info[2], tracking_info[3], track_time)
                self.tcpClient.sendData.emit(command)  # Send the tracking command to the RPi

    def coordinateFormatter(self, num: float, degree: bool):
        if degree:
            formated_coord = "<html><head/><body><p>%.4f<span style=" \
                             "\" vertical-align:super;\">o</span></p></body></html>" % num
        else:
            formated_coord = "<html><head/><body><p>%.4f<span style=\" " \
                             "vertical-align:super;\">h</span></p></body></html>" % num

        return formated_coord  # Return the formatted coordinate string

    def calcScanPoints(self):
        point_1 = (self.ui.sky_scan_win.point1Coord_1Field.text(),
                   self.ui.sky_scan_win.point1Coord_2Field.text(), )
        point_2 = (self.ui.sky_scan_win.point2Coord_1Field.text(),
                   self.ui.sky_scan_win.point2Coord_2Field.text(), )
        point_3 = (self.ui.sky_scan_win.point3Coord_1Field.text(),
                   self.ui.sky_scan_win.point3Coord_2Field.text(), )
        point_4 = (self.ui.sky_scan_win.point4Coord_1Field.text(),
                   self.ui.sky_scan_win.point4Coord_2Field.text(), )
        self.ui.setStyleSkyScanningSig.emit((point_1, point_2, point_3, point_4, ))

        check_1 = point_1[0] != "" and point_1[1] != "" and point_2[0] != "" and point_2[1] != ""
        check_2 = point_3[0] != "" and point_3[1] != "" and point_4[0] != "" and point_4[1] != ""

        if (check_1 and check_2) is True:
            coord_system = self.ui.sky_scan_win.coordinateSystemComboBx.currentText()
            epoch = self.ui.sky_scan_win.epochDateSelection.date().toString("yyyy/MM/dd")
            direction = self.ui.sky_scan_win.directionSelection.currentText()

            step_x = self.ui.sky_scan_win.stepSizeBoxCoord1.value()
            step_y = self.ui.sky_scan_win.stepSizeBoxCoord2.value()
            step_size = (step_x, step_y, )  # Step size in each axis

            point_1 = (float(point_1[0]), float(point_1[1]), )
            point_2 = (float(point_2[0]), float(point_2[1]), )
            point_3 = (float(point_3[0]), float(point_3[1]), )
            point_4 = (float(point_4[0]), float(point_4[1]), )

            points = (point_1, point_2, point_3, point_4, coord_system, epoch, )
            map_points = self.astronomy.scanning_map_generator(points, step_size, direction)
            num_of_points = len(map_points[0])  # Number of points to be scanned

            if self.ui.sky_scan_win.integrationEnabler.isChecked():
                total_int_time = num_of_points * self.ui.sky_scan_win.integrationTimeEntry.value() * 60.0
                self.ui.sky_scan_win.totalIntTime.setText("%.0fs" % total_int_time)
            self.ui.sky_scan_win.totalPointsToScan.setText("%d" % num_of_points)

            if self.ui.sky_scan_win.simulateScanningChk.isChecked():
                sim_speed = self.ui.sky_scan_win.simSpeedValue.value()
                self.simHandler.simStopSig.emit()  # First stop any ongoing simulation
                self.simHandler.simStartSig.emit(map_points[0], sim_speed)  # Then send the new points

            return map_points[0]
        else:
            self.ui.sky_scan_win.pointOperationTabs.setCurrentIndex(0)

        return ()

    def skyScanStart(self):
        # TODO Add a perform calculation warning to the user
        if not self.motors_enabled:  # TODO Set the condition to the correct one
            map_points = self.calcScanPoints()  # Get the mapping points
            if map_points is not ():
                home_steps = self.cfgData.getHomeSteps()
                init_steps = (int(home_steps[0]), int(home_steps[1]), )

                step_x = self.ui.sky_scan_win.stepSizeBoxCoord1.value()
                step_y = self.ui.sky_scan_win.stepSizeBoxCoord2.value()
                step_size = (step_x, step_y,)  # Step size in each axis

                if self.ui.sky_scan_win.integrationEnabler.isChecked():
                    int_time = self.ui.sky_scan_win.integrationTimeEntry.value()
                else:
                    int_time = 0.0

                if self.ui.sky_scan_win.planetaryObjectSelectcheckBox.isChecked():
                    objec = self.ui.sky_scan_win.objectSelectionComboBox.currentText()
                else:
                    objec = None

                calc_points = self.astronomy.scanning_point_calculator(map_points, init_steps, step_size,
                                                                       int_time, objec)
                self.tcpClient.sendData.emit("SKY-SCAN_RA_%f_DEC_%f_RA-SPEED_%f_DEC-SPEED_%f_INT-TIME_%.2f"
                                             % (float(calc_points[0].split("_")[0]), float(calc_points[0].split("_")[2])
                                                , float(calc_points[1][0]), float(calc_points[1][1]), int_time))
                self.tcpClient.sendData.emit("SKY-SCAN-MAP_%s" % calc_points[0])
                print(calc_points[0])  # TODO Remove the print statement
        else:
            self.ui.motorsDisabledSig.emit()

    def calibration_reposition(self):
        if self.motors_enabled:
            system = self.calib_win.coordinatSystemcomboBox.currentText()
            home_steps = self.cfgData.getHomeSteps()  # Return a list with the steps way from home position
            if system == "Satellite" and self.ui.calib_win.calibCoord_1_Label.text() != "Satellite...":
                satellite = self.ui.sat_sel_diag.satSelectionList.currentItem().text().spli(" ")
                sat_pos = (satellite[-1][:-1], satellite[-1][-1],)
                coords = self.astronomy.geo_sat_position(sat_pos)
                coord_1 = coords[1][0]  # Get the HA
                coord_2 = coords[1][1]  # Get the DEC
                command = "TRNST_RA_%.5f_DEC_%.5f\n" % (coord_1 - float(home_steps[0]), coord_2 - float(home_steps[1]))
            else:
                coord_1 = self.ui.calib_win.calibCoord_1_Text.text()
                coord_2 = self.ui.calib_win.calibCoord_2_Text.text()
                coord_tuple = (coord_1, coord_2, )
                sys_date_tuple = (system, "Now", )

                final_coords = self.astronomy.coordinate_transform(coord_tuple, sys_date_tuple)
                transit_coords = self.astronomy.transit(final_coords[0], final_coords[1], -int(home_steps[0]),
                                                        -int(home_steps[1]), 0)
                command = "TRNST_RA_%.5f_DEC_%.5f\n" % (transit_coords[0], transit_coords[1])
            self.tcpClient.sendData.emit(command)  # Send the transit command to RPi, to set the calibration position
        else:
            self.ui.motorsDisabledSig.emit()

    def sat_coords_setter(self, satellite: str):
        sat = satellite.split(" ")
        if len(sat) == 1:
            satellite = self.ui.sat_sel_diag.satSelectionList.currentItem().text()

        coords = self.astronomy.geo_sat_position(satellite)
        self.ui.updateCoordFieldsSig.emit(coords)

    # Make all the necessary signal connections
    def signalConnections(self):
        """
        Connect all the necessary signals from the different modules.
        This function is called at the start of the Operation handling thread.
        :return: Nothing
        """
        self.tcpStellarium.sendClientConn.connect(self.stellCommSend)  # Send data from Stellarium to the RPi
        self.tcpClient.dataRcvSigC.connect(self.clientDataRx)  # Receive pending data from RPi connected client
        self.tcpClient.newConInitComms.connect(self.initialCommands)

        self.tcpServer.dataRxFromServ.connect(self.rpiServRcvData)  # Receive data from the RPi server
        self.tcpServer.clientNotice.connect(self.tcpClient.connect)  # Tell the client to reconnect

        self.ui.stopMovingRTSig.connect(self.stopMovingRT)  # Send a motion stop command, once this signal is triggered
        self.ui.main_widg.stellPosUpdtBtn.clicked.connect(partial(self.tcpClient.sendData.emit, "SEND_POS_UPDATE\n"))
        self.posDataShow.connect(self.ui.posDataShow)  # Show the dish position data, when available

        self.ui.tcp_widg.conTestBtn.clicked.connect(self.testConnButton)

        # Give functionality to the buttons
        self.ui.main_widg.connectRadioTBtn.clicked.connect(self.connectButtonR)  # TCP client connection button
        self.ui.main_widg.serverRPiConnBtn.clicked.connect(self.connectButtonRPi)  # TCP server connection button
        self.ui.main_widg.connectStellariumBtn.clicked.connect(
            self.connectButtonS)  # Stellarium TCP server connection button
        self.ui.main_widg.motorCommandButton.clicked.connect(self.motorsEnableButton)  # Enable/Disable the motors on RPi

        self.ui.man_cn_widg.movRaBtn.clicked.connect(self.manCont_movRA)
        self.ui.man_cn_widg.movDecBtn.clicked.connect(self.manCont_movDEC)
        self.ui.man_cn_widg.syncMoveBtn.clicked.connect(self.manCont_movBoth)
        self.ui.man_cn_widg.stopMotMotionBtn.clicked.connect(self.manCont_stop)

        self.ui.tcp_widg.telescopeSaveBtn.clicked.connect(self.saveTCPSettings)
        self.ui.loc_widg.saveBtn.clicked.connect(self.saveLocationSettings)

        self.ui.main_widg.actionSettings.triggered.connect(self.TCPSettingsHandle)  # Update settings each time
        self.ui.main_widg.actionLocation.triggered.connect(self.locationSettingsHandle)  # Update location fields
        self.ui.main_widg.actionManual_Control.triggered.connect(partial(self.tcpClient.sendData.emit,
                                                                         "SEND_HOME_STEPS\n"))
        self.ui.main_widg.locatChangeBtn.clicked.connect(self.locationSettingsHandle)
        self.ui.main_widg.homePositionButton.clicked.connect(self.homePositionReturn)

        self.ui.plan_obj_win.commandExecutionBtn.clicked.connect(self.planObjCommand)

        self.ui.sky_scan_win.calculateScanMapBtn.clicked.connect(self.calcScanPoints)
        self.ui.sky_scan_win.startScanBtn.clicked.connect(self.skyScanStart)

        self.ui.calib_win.repositionButton.clicked.connect(self.calibration_reposition)
        self.ui.sat_sel_diag.satSelectionList.currentTextChanged.connect(self.sat_coords_setter)
        self.ui.sat_sel_diag.coordinateSystemBox.currentTextChanged.connect(self.sat_coords_setter)

        self.logD.debug("All signal connections made")

    def appExitRequest(self):
        """
        #This function is called whenever the app is about to quit.
        First quit from the thread and then delete both the thread and the corresponding object
        Quit exits the thread and then wait is waiting for the thread exit
        deleteLater, deletes the thread object and the threaded object
        :return: Nothing
        """
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

        self.simThread.quit()
        self.simThread.wait()
        self.simHandler.deleteLater()
        self.simThread.deleteLater()
        self.logD.debug("Simulation handler thread is closed.")
