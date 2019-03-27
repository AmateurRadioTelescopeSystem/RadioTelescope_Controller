import os
import logging
from functools import partial
from skyfield.api import Loader
from PyQt5 import QtCore, QtNetwork
from Core.Astronomy import Astronomy
from Core.Handlers import SimulationHandler
from Core.Handlers import TLEHandler


class OpHandler(QtCore.QObject):
    posDataShow = QtCore.pyqtSignal(float, float, name='pos_data_show')

    def __init__(self, tcp_client, tcp_server, tcp_stellarium, tcp_cl_thread, tcp_serv_thread, tcp_stel_thread, ui,
                 cfg_data, parent=None):
        """
        Operations handler class constructor.

        :param tcp_client:
        :param tcp_server:
        :param tcp_stellarium:
        :param tcp_cl_thread:
        :param tcp_serv_thread:
        :param tcp_stel_thread:
        :param ui:
        :param cfg_data:
        :param parent:
        """
        super(OpHandler, self).__init__(parent)
        self.tcp_client = tcp_client  # TCP client object
        self.tcp_server = tcp_server  # TCP RPi server object
        self.tcp_stellarium = tcp_stellarium  # TCP Stellarium server object

        # Create the thread varaible for the class
        self.tcp_client_thread = tcp_cl_thread
        self.tcp_server_thread = tcp_serv_thread
        self.tcp_stel_thread = tcp_stel_thread

        self.ui = ui  # User interface handling object
        self.cfg_data = cfg_data
        self.logger = logging.getLogger(__name__)  # Data logger object
        self.astronomy = Astronomy.Calculations(cfg_data=cfg_data)  # Astronomy calculations object
        self.prev_pos = ["", ""]  # The dish position is saved for change comparison
        self.motors_enabled = False  # Keep the motor status

        self.max_steps_to_target_ra = 0
        self.max_steps_to_target_dec = 0
        self.sim_started = False

        self.tle_operations = TLEHandler.TLEHandler(cfg_data)  # Create the TLE handling object

        # Simulation thread operations
        self.sim_thread = QtCore.QThread()
        self.sim_handler = SimulationHandler.SimulHandler(tcp_stellarium)
        self.sim_handler.moveToThread(self.sim_thread)
        self.sim_thread.started.connect(self.sim_handler.start)
        self.sim_thread.finished.connect(self.sim_handler.close)
        self.sim_thread.start()  # Start the simulation thread

        self.ui.sky_scan_win.textBrowser.setText("<html><table><tbody><tr><td style=\"width: 36px;\" colspan=\"2\">"
                                                 "<strong>System</strong></td><td style=\"width: 10px;\">&nbsp;</td>"
                                                 "<td style=\"width: 49px;\" colspan=\"2\"><strong>Equatorial</strong>"
                                                 "</td></tr><tr><td style=\"width: 26px;\"><strong>C1</strong></td>"
                                                 "<td style=\"width: 10px;\"><strong>C2</strong></td><td "
                                                 "style=\"width: 10px;\">&nbsp;</td>"
                                                 "<td style=\"width: 20px;\"><strong>RA</strong></td><td "
                                                 "style=\"width: 29px;\">"
                                                 "<strong>DEC</strong></td></tr><tr><td style=\"width: "
                                                 "26px;\">&nbsp;</td>"
                                                 "<td style=\"width: 10px;\">&nbsp;</td><td style=\"width: "
                                                 "10px;\">&nbsp;</td>"
                                                 "<td style=\"width: 20px;\">&nbsp;</td><td style=\"width: "
                                                 "29px;\">&nbsp;</td></tr><tr>"
                                                 "<td style=\"width: 26px;\">&nbsp;</td><td style=\"width: "
                                                 "10px;\">&nbsp;</td>"
                                                 "<td style=\"width: 10px;\">&nbsp;</td><td style=\"width: "
                                                 "20px;\">&nbsp;</td>"
                                                 "<td style=\"width: "
                                                 "29px;\">&nbsp;</td></tr></tbody></table><p>&nbsp;</p></html>")

    def start(self):
        """Initializer of the thread.
        Make all the necessary initializations when the thread starts

        :return: Nothing
        """
        self.logger.info("Operations handler thread started")
        self.signal_connections()  # Make all the necessary signal connections

        autocon_stell = self.cfg_data.get_tcp_stell_auto_conn_status()  # See if auto-connection at startup is enabled
        autocon_rpi = self.cfg_data.get_tcp_client_auto_conn_status()  # Auto-connection preference for the RPi
        # server and client

        # Try to get a new TLE, if the one we have is outdated
        tle_expiry = self.tle_operations.tle_expiry_checker()  # Check the validity of the file

        if (tle_expiry[0] is True and tle_expiry[1] is True) or (
                tle_expiry[0] is False and tle_expiry[2] == "File not found"):
            self.ui.tleStatusInfoSig.emit("")  # Just initialize the widget
            tle_result = self.tle_operations.tle_retriever()  # Get the new TLE file

            if tle_result[0] is True:
                tle_status_msg = "Success^TLE file(s) updated"
            else:
                tle_status_msg = "Error^There was a problem getting TLE file(s).^"
                tle_status_msg += tle_result[1]
        elif tle_expiry[0] is False:
            self.ui.tleStatusInfoSig.emit("")  # Just initialize the widget
            tle_status_msg = "Error^There was a problem checking TLE file(s).^"
            tle_status_msg += tle_expiry[2]
        else:
            tle_status_msg = ""

        if tle_status_msg != "":
            self.ui.tleStatusInfoSig.emit(tle_status_msg)
            while not self.ui.tle_info_msg_box.clickedButton():
                continue

        # todo: Add a user prompt to inform about upcoming download and download times
        load = Loader(os.path.abspath('Astronomy Database'), verbose=False)
        load.timescale()
        load('de421.bsp')

        # If auto-connection is selected for thr TCP section, then do as requested
        if autocon_stell == "yes":
            self.tcp_stel_thread.start()  # Start the server thread, since auto start is enabled
        if autocon_rpi == "yes":
            self.tcp_client_thread.start()  # Start the client thread, since auto start is enabled
            self.tcp_server_thread.start()  # Start the RPi server thread, since auto start is enabled

    # Client connection button handling method
    def connect_button_client(self):
        if self.tcp_client_thread.isRunning() and (
                self.ui.main_widget.connectRadioTBtn.text() == "Disconnect" or
                self.ui.main_widget.connectRadioTBtn.text() == "Stop"):
            self.tcp_client_thread.quit()  # Disconnect from the client
        elif not self.tcp_client_thread.isRunning():
            self.tcp_client_thread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            self.tcp_client.reConnectSigC.emit()

    # Stellarium server connection handling method
    def connect_button_stell(self):
        if self.tcp_stel_thread.isRunning() and (
                self.ui.main_widget.connectStellariumBtn.text() == "Disable" or
                self.ui.main_widget.connectStellariumBtn.text() == "Stop"):
            self.tcp_stel_thread.quit()  # Quit the currently running thread
        elif not self.tcp_stel_thread.isRunning():
            self.tcp_stel_thread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            self.tcp_stellarium.reConnectSigS.emit()

    # RPi server connection handling method
    def connect_button_rpi(self):
        if self.tcp_server_thread.isRunning() and (
                self.ui.main_widget.serverRPiConnBtn.text() == "Disable" or
                self.ui.main_widget.serverRPiConnBtn.text() == "Stop"):
            self.tcp_server_thread.quit()  # Quit the currently running thread
        elif not self.tcp_server_thread.isRunning():
            self.tcp_server_thread.start()  # Attempt a connection with the client
        else:
            # If the thread is running and it is not yet connected, attempt a reconnection
            self.tcp_server.reConnectSigR.emit()

    def test_conn_button(self):
        if self.ui.tcp_widget.clientConTestChkBox.isChecked():
            self.tcp_client.sendData.emit("Test\n")

    def motors_enable_button(self):
        if self.motors_enabled:
            self.tcp_client.sendData.emit("DISABLE_MOTORS\n")
        else:
            self.tcp_client.sendData.emit("ENABLE_MOTORS\n")

    @QtCore.pyqtSlot(name='sendNewConCommands')
    def initial_commands(self):
        # TODO add more commands to send, like system check reports and others
        self.tcp_client.sendData.emit("SEND_HOME_STEPS\n")  # Get the steps from home for each motor
        self.tcp_client.sendData.emit("REPORT_MOTOR_STATUS\n")  # Get the current status of the motors

    # Dta received from the client connected to the RPi server
    @QtCore.pyqtSlot(str, name='dataClientRX')
    def client_data_receive(self, data: str):
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
            split_str = data.split("_")  # Try to split the string, and if it splits then a command is sent
            if len(split_str) > 1:
                if split_str[0] == "STEPS-FROM-HOME":
                    self.cfg_data.set_home_steps(split_str[1], split_str[2])  # Set the current steps
                    self.ui.setManContStepsSig.emit("RA", split_str[1])
                    self.ui.setManContStepsSig.emit("DEC", split_str[2])
                elif split_str[0] == "MAX-STEPS-TO-DO":
                    if split_str[1] == "RA":
                        self.max_steps_to_target_ra = int(split_str[2])
                        self.max_steps_to_target_dec = 0
                    elif split_str[1] == "DEC":
                        self.max_steps_to_target_dec = int(split_str[2])
                        self.max_steps_to_target_ra = 0
            else:
                self.logger.debug("Data received from client (Connected to remote RPi server): %s", data)
        if isinstance(data, str):
            self.ui.setGUIFromClientSig.emit(data)  # If it is not split yet, send the command

    @QtCore.pyqtSlot(list, name='clientCommandSendStell')
    def stell_command_send(self, ra_dec: list):
        """
        Send the appropriate command according to the selected mode. Data is received from Stellarium (sendClientConn)

        :param ra_dec: A list containing the data received from Stellarium
        :return: Nothing
        """
        if not self.motors_enabled:
            self.ui.motorsDisabledSig.emit()
        else:
            home_steps = self.cfg_data.get_home_steps()  # Return a list with the steps way from home position
            tr_time = int(self.ui.main_widget.transitTimeValue.text())
            if self.ui.main_widget.stellariumOperationSelect.currentText() == "Transit":
                ra_degrees = ra_dec[0] * 15.0  # Stellarium returns right ascension is hours, so we convert to degrees
                transit_coords = self.astronomy.transit(ra_degrees, ra_dec[1], -int(home_steps[0]), -int(home_steps[1]),
                                                        tr_time)
                command = "TRNST_RA_%.5f_DEC_%.5f\n" % (transit_coords[0], transit_coords[1])
                self.tcp_client.sendData.emit(command)  # Send the transit command to the RPi
            elif self.ui.main_widget.stellariumOperationSelect.currentText() == "Aim and track":
                ra_degrees = ra_dec[0] * 15.0  # Stellarium returns right ascension is hours, so we convert to degrees
                trk_coords = self.astronomy.transit(ra_degrees, ra_dec[1], -int(home_steps[0]), -int(home_steps[1]), 0)
                command = "TRK_RA_%.5f_DEC_%.5f_RA-SPEEDD_%.5f_DEC-SPEED_%.5f\n" % (trk_coords[0], trk_coords[1], 0, 0)
                self.tcp_client.sendData.emit(command)  # Send the tracking command to the RPi

    # Received data from the server that the RPi is connected as a client. Signal is (dataRxFromServ)
    @QtCore.pyqtSlot(str, name='rpiServDataRx')
    def rpi_server_rx_data(self, data: str):
        """
        Get the data sent from the RPi client.
        Mainly the dish position will be sent

        :param data: Data received from the TCP connection
        :return: Nothing
        """
        # TODO Remove the degree conversion for the RA, since MPU will send in degrees and not hours
        split_data = data.split("_")  # Split the string with the set delimiter
        if split_data[0] == "POSUPDATE":
            dec_degrees = split_data[4]  # Get the DEC from the received position
            ra_degrees = self.astronomy.hour_angle_to_ra(float(split_data[2]) * 15.0, float(dec_degrees))
            if not (self.prev_pos[0] == ra_degrees and self.prev_pos[1] == dec_degrees
                    and split_data[0] != "POSUPDATE"):
                # Send the position to Stellarium
                self.tcp_stellarium.sendDataStell.emit(float(ra_degrees) / 15.0, float(dec_degrees))

                # Send the updated values if they are different
                self.posDataShow.emit(float(ra_degrees) / 15.0, float(dec_degrees))
            self.prev_pos = [ra_degrees, dec_degrees]  # Save the values for later comparison
        elif split_data[0] == "DISHPOS":
            dec_degrees = split_data[4]  # Get the DEC from the received position
            ra_degrees = self.astronomy.hour_angle_to_ra(float(split_data[2]) * 15.0, float(dec_degrees))
            ra_steps = split_data[7]
            dec_steps = split_data[9]
            self.ui.setManContStepsSig.emit("RA", ra_steps)  # Update the manual control window
            self.ui.setManContStepsSig.emit("DEC", dec_steps)
            self.tcp_stellarium.sendDataStell.emit(float(ra_degrees) / 15.0, float(dec_degrees))
            self.posDataShow.emit(float(ra_degrees) / 15.0, float(dec_degrees))

            # Update the progress bar
            if self.max_steps_to_target_ra != 0:
                ratio = int(ra_steps) / self.max_steps_to_target_ra
                self.ui.main_widget.onTargetProgress.setValue(ratio)
            elif self.max_steps_to_target_dec != 0:
                ratio = int(dec_steps) / self.max_steps_to_target_dec
                self.ui.main_widget.onTargetProgress.setValue(ratio)

    # Command to stop any motion of the radio telescope dish
    @QtCore.pyqtSlot(name='stopRadioTele')
    def stop_moving_telescope(self):
        # TODO change the command to the appropriate one
        self.tcp_client.sendData.emit("STOP\n")  # Send the request to stop moving to the RPi server
        self.logger.warning("A dish motion halt was requested")

    # Functions to connect with the manual control widget
    # TODO add comments to the functions
    def manual_cont_mov_ra(self):
        if not self.motors_enabled:
            self.ui.motorsDisabledSig.emit()
        else:
            freq = self.ui.man_cont_widget.frequncyInputBox.text()
            step = self.ui.man_cont_widget.raStepsField.text()
            string = "MANCONT_MOVRA_%s_%s_0\n" % (freq, step)
            self.tcp_client.sendData.emit(string)

    def manual_cont_mov_dec(self):
        if not self.motors_enabled:
            self.ui.motorsDisabledSig.emit()
        else:
            freq = self.ui.man_cont_widget.frequncyInputBox.text()
            step = self.ui.man_cont_widget.decStepsField.text()
            string = "MANCONT_MOVDEC_%s_0_%s\n" % (freq, step)
            self.tcp_client.sendData.emit(string)

    def manual_cont_mov_both(self):
        if not self.motors_enabled:
            self.ui.motorsDisabledSig.emit()
        else:
            freq = self.ui.man_cont_widget.frequncyInputBox.text()
            step_ra = self.ui.man_cont_widget.raStepsField.text()
            step_dec = self.ui.man_cont_widget.decStepsField.text()
            string = "MANCONT_MOVE_%s_%s_%s\n" % (freq, step_ra, step_dec)
            self.tcp_client.sendData.emit(string)

    def manual_cont_stop(self):
        if not self.motors_enabled:
            self.ui.motorsDisabledSig.emit()
        else:
            string = "MANCONT_STOP\n"
            self.tcp_client.sendData.emit(string)  # Send the stop request in manual control

    def tcp_settings_handle(self):
        autocon_stell = self.cfg_data.get_tcp_stell_auto_conn_status()  # See if auto-connection at startup is enabled
        autocon_rpi = self.cfg_data.get_tcp_client_auto_conn_status()  # Auto-connection preference for the RPi
        # server and client
        client_ip = self.cfg_data.get_tcp_client_host()
        stell_ip = "127.0.0.1"
        remote_ip = "0.0.0.0"
        serv_rpi_remote = self.cfg_data.get_server_remote("TCPRPiServ")
        stell_serv_remote = self.cfg_data.get_server_remote("TCPStell")

        # If auto-connection is selected for thr TCP section, then do as requested
        if autocon_stell == "yes":
            self.ui.tcp_widget.stellServAutoStartBtn.setChecked(True)
        if autocon_rpi == "yes":
            self.ui.tcp_widget.teleAutoConChoice.setChecked(True)

        if client_ip in ("localhost", "127.0.0.1"):
            self.ui.tcp_widget.telClientBox.setCurrentIndex(0)
        else:
            self.ui.tcp_widget.telClientBox.setCurrentIndex(1)

        if serv_rpi_remote == "yes" or stell_serv_remote == "yes":
            for ip_address in QtNetwork.QNetworkInterface.allAddresses():
                if ip_address != QtNetwork.QHostAddress.LocalHost and ip_address.toIPv4Address() != 0:
                    break  # If we found an IP then we exit the loop
                else:
                    ip_address = QtNetwork.QHostAddress.LocalHost  # If no IP is found, assign localhost
            remote_ip = ip_address.toString()  # Assign the IP address that wa found above

        if serv_rpi_remote == "no":
            self.ui.tcp_widget.telServBox.setCurrentIndex(0)
        elif serv_rpi_remote == "yes":
            self.ui.tcp_widget.telServBox.setCurrentIndex(1)
        elif serv_rpi_remote == "custom":
            self.ui.tcp_widget.telServBox.setCurrentIndex(2)

        if stell_serv_remote == "no":
            self.ui.tcp_widget.stellIPServBox.setCurrentIndex(0)
        else:
            stell_ip = remote_ip
            self.ui.tcp_widget.stellIPServBox.setCurrentIndex(1)

        # Set all the text fields with the correct data
        # TODO handle what happens when server is not initialized at start
        self.ui.tcp_widget.telescopeIPAddrClient.setText(client_ip)
        self.ui.tcp_widget.telescopeIPPortClient.setText(self.cfg_data.get_tcp_client_port())

        self.ui.tcp_widget.telescopeIPAddrServ.setText(remote_ip)
        self.ui.tcp_widget.telescopeIPPortServ.setText(self.cfg_data.get_rpi_port())

        self.ui.tcp_widget.stellServInpIP.setText(stell_ip)
        self.ui.tcp_widget.stellPortServ.setText(self.cfg_data.get_stell_port())

        # Set the settings for the connection test tab
        if self.tcp_client.sock.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.ui.tcp_widget.clientConTestChkBox.setEnabled(True)
            self.ui.tcp_widget.clientStatLbl.setEnabled(True)
            self.ui.tcp_widget.clientStatus.setEnabled(True)
        else:
            self.ui.tcp_widget.clientConTestChkBox.setEnabled(False)
            self.ui.tcp_widget.clientStatLbl.setEnabled(False)
            self.ui.tcp_widget.clientStatus.setEnabled(False)

        if self.tcp_server.socket is not None:
            if self.tcp_server.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.ui.tcp_widget.serverConTestChkBox.setEnabled(True)
                self.ui.tcp_widget.servStatLbl.setEnabled(True)
                self.ui.tcp_widget.serverStatus.setEnabled(True)
            else:
                self.ui.tcp_widget.serverConTestChkBox.setEnabled(False)
                self.ui.tcp_widget.servStatLbl.setEnabled(False)
                self.ui.tcp_widget.serverStatus.setEnabled(False)
        else:
            self.ui.tcp_widget.serverConTestChkBox.setEnabled(False)
            self.ui.tcp_widget.servStatLbl.setEnabled(False)
            self.ui.tcp_widget.serverStatus.setEnabled(False)

        if self.tcp_stellarium.socket is not None:
            if self.tcp_stellarium.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.ui.tcp_widget.stellConTestChkBox.setEnabled(True)
                self.ui.tcp_widget.stellStatLbl.setEnabled(True)
                self.ui.tcp_widget.stellariumStatus.setEnabled(True)
            else:
                self.ui.tcp_widget.stellConTestChkBox.setEnabled(False)
                self.ui.tcp_widget.stellStatLbl.setEnabled(False)
                self.ui.tcp_widget.stellariumStatus.setEnabled(False)
        else:
            self.ui.tcp_widget.stellConTestChkBox.setEnabled(False)
            self.ui.tcp_widget.stellStatLbl.setEnabled(False)
            self.ui.tcp_widget.stellariumStatus.setEnabled(False)

    # Save the settings when the save button is pressed
    def save_tcp_settings(self):
        # Save the ports entered for each setting
        self.cfg_data.set_tcp_client_port(self.ui.tcp_widget.telescopeIPPortClient.text())
        self.cfg_data.set_stell_port(self.ui.tcp_widget.stellPortServ.text())
        self.cfg_data.set_rpi_port(self.ui.tcp_widget.telescopeIPPortServ.text())

        # Save the auto start/enable option
        if self.ui.tcp_widget.teleAutoConChoice.isChecked():
            self.cfg_data.tcp_client_auto_conn_enable()
        else:
            self.cfg_data.tcp_client_auto_conn_disable()

        if self.ui.tcp_widget.stellServAutoStartBtn.isChecked():
            self.cfg_data.tcp_stell_auto_conn_enable()
        else:
            self.cfg_data.tcp_stell_auto_conn_disable()

        # Save the IP addresses
        if self.ui.tcp_widget.telServBox.currentText() == "Localhost":
            self.cfg_data.set_rpi_host("127.0.0.1")
            self.cfg_data.set_server_remote("TCPRPiServ", "no")
        elif self.ui.tcp_widget.telServBox.currentText() == "Remote":
            self.cfg_data.set_server_remote("TCPRPiServ", "yes")
            self.cfg_data.set_rpi_host(self.ui.tcp_widget.telescopeIPAddrServ.text())
        elif self.ui.tcp_widget.telServBox.currentText() == "Custom":
            self.cfg_data.set_server_remote("TCPRPiServ", "custom")
            self.cfg_data.set_rpi_host(self.ui.tcp_widget.telescopeIPAddrServ.text())

        if self.ui.tcp_widget.telClientBox.currentText() == "Localhost":
            self.cfg_data.set_tcp_client_host("127.0.0.1")
            self.cfg_data.set_server_remote("TCP", "no")
        else:
            self.cfg_data.set_server_remote("TCP", "yes")
            self.cfg_data.set_tcp_client_host(self.ui.tcp_widget.telescopeIPAddrClient.text())

        if self.ui.tcp_widget.stellIPServBox.currentText() == "Localhost":
            self.cfg_data.set_stell_host("127.0.0.1")
            self.cfg_data.set_server_remote("TCPStell", "no")
        else:
            self.cfg_data.set_server_remote("TCPStell", "yes")
            self.cfg_data.set_stell_host(self.ui.tcp_widget.stellServInpIP.text())

        # Send a reconnect signal to all TCP operations (No effect if some is not active)
        self.tcp_client.reConnectSigC.emit()
        self.tcp_server.reConnectSigR.emit()
        self.tcp_stellarium.reConnectSigS.emit()

    def location_settings_handle(self):
        lat_lon = self.cfg_data.get_lat_lon()  # First element is latitude and second element is longitude
        altitude = self.cfg_data.get_altitude()  # Get the altitude from the settings file

        self.ui.location_widget.latEntry.setText(lat_lon[0])
        self.ui.location_widget.lonEntry.setText(lat_lon[1])
        self.ui.location_widget.altEntry.setText(altitude)

        if self.cfg_data.get_maps_selection() == "no":
            self.ui.location_widget.locationTypeChoose.setCurrentIndex(0)

    def save_location_settings(self):
        coords = [self.ui.location_widget.latEntry.text(), self.ui.location_widget.lonEntry.text()]
        altitude = self.ui.location_widget.altEntry.text()
        self.cfg_data.set_lat_lon(coords)
        self.cfg_data.set_altitude(altitude)

        if self.ui.location_widget.locationTypeChoose.currentText() == "Google Maps":
            self.cfg_data.set_maps_selection("yes")
        else:
            self.cfg_data.set_maps_selection("no")

        # Show location on the GUI
        self.ui.main_widget.lonTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                                               "vertical-align:super;\">o</span></p></body></html>" % coords[1])
        self.ui.main_widget.latTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                                               "vertical-align:super;\">o</span></p></body></html>" % coords[0])
        self.ui.main_widget.altTextInd.setText("<html><head/><body><p align=\"center\">%sm</p></body></html>"
                                               % altitude)

    def home_position_return(self):
        if not self.motors_enabled:
            self.ui.motorsDisabledSig.emit()
        else:
            self.tcp_client.sendData.emit("RETURN_HOME\n")

    def plan_obj_command(self):
        if not self.motors_enabled:
            self.ui.motorsDisabledSig.emit()
        else:
            home_steps = self.cfg_data.get_home_steps()
            if self.ui.plan_obj_win.planObjectTransitGroupBox.isChecked():
                objec = self.ui.plan_obj_win.objectSelectionComboBox.currentText()
                tr_time = self.ui.plan_obj_win.transitTimeBox.value()
                transit_coords = self.astronomy.transit_planetary(objec, -int(home_steps[0]), -int(home_steps[1]),
                                                                  int(tr_time))

                command = "TRNST_RA_%.5f_DEC_%.5f\n" % (transit_coords[0], transit_coords[1])
                self.tcp_client.sendData.emit(command)  # Send the transit command to the RPi
            elif self.ui.plan_obj_win.planObjectTrackingGroupBox.isChecked():
                objec = self.ui.plan_obj_win.objectSelectionComboBox.currentText()
                track_time = self.ui.plan_obj_win.trackingtTimeBox.value()
                tracking_info = self.astronomy.tracking_planetary(objec, -int(home_steps[0]), -int(home_steps[1]))

                command = "TRK_RA_%.5f_DEC_%.5f_RA-SPEED_%.5f_DEC-SPEED_%.5f_TIME_%.2f\n" \
                          % (tracking_info[0], tracking_info[1], tracking_info[2], tracking_info[3], track_time)
                self.tcp_client.sendData.emit(command)  # Send the tracking command to the RPi

    def coordinate_formatter(self, num: float, degree: bool):
        if degree:
            formatted_coord = "<html><head/><body><p>%.4f<span style=" \
                              "\" vertical-align:super;\">o</span></p></body></html>" % num
        else:
            formatted_coord = "<html><head/><body><p>%.4f<span style=\" " \
                              "vertical-align:super;\">h</span></p></body></html>" % num

        return formatted_coord  # Return the formatted coordinate string

    def calc_scan_points(self):
        point_1 = (self.ui.sky_scan_win.point1Coord_1Field.text(), self.ui.sky_scan_win.point1Coord_2Field.text(),)
        point_2 = (self.ui.sky_scan_win.point2Coord_1Field.text(), self.ui.sky_scan_win.point2Coord_2Field.text(),)
        point_3 = (self.ui.sky_scan_win.point3Coord_1Field.text(), self.ui.sky_scan_win.point3Coord_2Field.text(),)
        point_4 = (self.ui.sky_scan_win.point4Coord_1Field.text(), self.ui.sky_scan_win.point4Coord_2Field.text(),)
        self.ui.setStyleSkyScanningSig.emit((point_1, point_2, point_3, point_4,))

        check_1 = point_1[0] != "" and point_1[1] != "" and point_2[0] != "" and point_2[1] != ""
        check_2 = point_3[0] != "" and point_3[1] != "" and point_4[0] != "" and point_4[1] != ""

        if (check_1 and check_2) is True:
            coord_system = self.ui.sky_scan_win.coordinateSystemComboBx.currentText()
            epoch = self.ui.sky_scan_win.epochDateSelection.date().toString("yyyy/MM/dd")
            direction = self.ui.sky_scan_win.directionSelection.currentText()

            step_x = self.ui.sky_scan_win.stepSizeBoxCoord1.value()
            step_y = self.ui.sky_scan_win.stepSizeBoxCoord2.value()
            step_size = (step_x, step_y,)  # Step size in each axis

            point_1 = (float(point_1[0]), float(point_1[1]),)
            point_2 = (float(point_2[0]), float(point_2[1]),)
            point_3 = (float(point_3[0]), float(point_3[1]),)
            point_4 = (float(point_4[0]), float(point_4[1]),)

            points = (point_1, point_2, point_3, point_4, coord_system, epoch,)
            map_points = self.astronomy.scanning_map_generator(points, step_size, direction)
            num_of_points = len(map_points[0])  # Number of points to be scanned

            if self.ui.sky_scan_win.integrationEnabler.isChecked():
                total_int_time = num_of_points * self.ui.sky_scan_win.integrationTimeEntry.value() * 60.0
                self.ui.sky_scan_win.totalIntTime.setText("%.0fs" % total_int_time)
            self.ui.sky_scan_win.totalPointsToScan.setText("%d" % num_of_points)

            if self.ui.sky_scan_win.simulateScanningChk.isChecked():
                sim_speed = self.ui.sky_scan_win.simSpeedValue.value()
                self.sim_handler.simStopSig.emit()  # First stop any ongoing simulation
                self.sim_handler.simStartSig.emit(map_points[0], sim_speed)  # Then send the new points

            return map_points[0]
        self.ui.sky_scan_win.pointOperationTabs.setCurrentIndex(0)

        return ()

    def sky_scan_start(self):
        # TODO Add a perform calculation warning to the user
        if not self.motors_enabled:  # TODO Set the condition to the correct one
            map_points = self.calc_scan_points()  # Get the mapping points
            if map_points is not ():
                home_steps = self.cfg_data.get_home_steps()
                init_steps = (int(home_steps[0]), int(home_steps[1]),)

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

                calc_points = self.astronomy.scanning_point_calculator(map_points, init_steps, step_size, int_time,
                                                                       objec)
                self.tcp_client.sendData.emit("SKY-SCAN_RA_%f_DEC_%f_RA-SPEED_%f_DEC-SPEED_%f_INT-TIME_%.2f"
                                              % (float(calc_points[0].split("_")[0]),
                                                 float(calc_points[0].split("_")[2]), float(calc_points[1][0]),
                                                 float(calc_points[1][1]), int_time))
                self.tcp_client.sendData.emit("SKY-SCAN-MAP_%s" % calc_points[0])
                print(calc_points[0])  # TODO Remove the print statement
        else:
            self.ui.motorsDisabledSig.emit()

    def calibration_reposition(self):
        if self.motors_enabled:
            system = self.ui.calib_win.coordinatSystemcomboBox.currentText()
            home_steps = self.cfg_data.get_home_steps()  # Return a list with the steps way from home position
            if system == "Satellite" and self.ui.calib_win.calibCoord_1_Label.text() != "Satellite...":
                coords = self.astronomy.geo_sat_position(self.ui.sat_sel_diag.satSelectionList.currentItem().text())
                coord_1 = coords[1][0]  # Get the HA
                coord_2 = coords[1][1]  # Get the DEC
                command = "TRNST_RA_%.5f_DEC_%.5f\n" % (coord_1, coord_2)
            elif system == "Motor steps":
                try:
                    coord_1 = int(self.ui.calib_win.calibCoord_1_Text.text())
                    coord_2 = int(self.ui.calib_win.calibCoord_2_Text.text())
                    command = "MANCONT_MOVE_%d_%d_%d\n" % (200, coord_1, coord_2)
                except ValueError:
                    command = ""
            else:
                try:
                    coord_1 = float(self.ui.calib_win.calibCoord_1_Text.text())
                    coord_2 = float(self.ui.calib_win.calibCoord_2_Text.text())
                    coord_tuple = (coord_1, coord_2,)
                    sys_date_tuple = (system, "Now",)

                    final_coords = self.astronomy.coordinate_transform(coord_tuple, sys_date_tuple)
                    transit_coords = self.astronomy.transit(final_coords[0], final_coords[1], -int(home_steps[0]),
                                                            -int(home_steps[1]), 0)
                    command = "TRNST_RA_%.5f_DEC_%.5f\n" % (transit_coords[0], transit_coords[1])
                except ValueError:
                    command = ""
            if command != "":
                self.tcp_client.sendData.emit(command)  # Send the transit command to set the calibration position
        else:
            self.ui.motorsDisabledSig.emit()

    def sat_coords_setter(self, satellite: str):
        sat = satellite.split(" ")
        if len(sat) == 1:
            satellite = self.ui.sat_sel_diag.satSelectionList.currentItem().text()

        coords = self.astronomy.geo_sat_position(satellite)
        self.ui.updateCoordFieldsSig.emit(coords)

    def save_tle_settings(self):
        self.cfg_data.set_tle_url(self.ui.tle_settings_widget.tleURL.text())
        self.cfg_data.set_tle_auto_update(self.ui.tle_settings_widget.autoUpdateSelection.isChecked())
        self.cfg_data.set_tle_update_interval(self.ui.tle_settings_widget.intervalValue.value())

    def show_tle_info(self):
        auto_updt = self.cfg_data.get_tle_auto_update()
        url = self.cfg_data.get_tle_url()
        interval = self.cfg_data.get_tle_update_interval()

        values = (auto_updt, url, interval)
        self.ui.setTLEDataSig.emit(values)

    @QtCore.pyqtSlot(str, name='notifierToSaveTheSettingsSignal')
    def settings_saver(self, window: str):
        if window == "TLE":
            self.save_tle_settings()

    def get_tle(self):
        self.ui.tleStatusInfoSig.emit("")  # Just initialize the widget
        tle_result = self.tle_operations.tle_retriever()  # Get the new TLE file

        if tle_result[0] is True:
            tle_status_msg = "Success^TLE file(s) updated"
        else:
            tle_status_msg = "Error^There was a problem getting TLE file(s).^"
            tle_status_msg += tle_result[1]
        self.ui.tleStatusInfoSig.emit(tle_status_msg)

    # Make all the necessary signal connections
    def signal_connections(self):
        """
        Connect all the necessary signals from the different modules.
        This function is called at the start of the Operation handling thread.

        :return: Nothing
        """
        self.tcp_stellarium.sendClientConn.connect(self.stell_command_send)  # Send data from Stellarium to the RPi
        self.tcp_client.dataRcvSigC.connect(self.client_data_receive)  # Receive pending data from RPi connected client
        self.tcp_client.newConInitComms.connect(self.initial_commands)

        self.tcp_server.dataRxFromServ.connect(self.rpi_server_rx_data)  # Receive data from the RPi server
        self.tcp_server.clientNotice.connect(self.tcp_client.connect_client)  # Tell the client to reconnect

        self.ui.stopMovingRTSig.connect(self.stop_moving_telescope)  # Send a motion stop command
        self.ui.main_widget.stellPosUpdtBtn.clicked.connect(partial(self.tcp_client.sendData.emit, "SEND_POS_UPDATE\n"))
        self.posDataShow.connect(self.ui.pos_data_show)  # Show the dish position data, when available

        self.ui.tcp_widget.conTestBtn.clicked.connect(self.test_conn_button)

        # Give functionality to the buttons
        self.ui.main_widget.connectRadioTBtn.clicked.connect(self.connect_button_client)  # TCP client connection button
        self.ui.main_widget.serverRPiConnBtn.clicked.connect(self.connect_button_rpi)  # TCP server connection button
        self.ui.main_widget.connectStellariumBtn.clicked.connect(self.connect_button_stell)  # Stellarium TCP server
        self.ui.main_widget.motorCommandButton.clicked.connect(self.motors_enable_button)  # Enable/Disable the motors

        self.ui.man_cont_widget.movRaBtn.clicked.connect(self.manual_cont_mov_ra)
        self.ui.man_cont_widget.movDecBtn.clicked.connect(self.manual_cont_mov_dec)
        self.ui.man_cont_widget.syncMoveBtn.clicked.connect(self.manual_cont_mov_both)
        self.ui.man_cont_widget.stopMotMotionBtn.clicked.connect(self.manual_cont_stop)

        self.ui.tcp_widget.telescopeSaveBtn.clicked.connect(self.save_tcp_settings)
        self.ui.location_widget.saveBtn.clicked.connect(self.save_location_settings)

        self.ui.main_widget.actionSettings.triggered.connect(self.tcp_settings_handle)  # Update settings each time
        self.ui.main_widget.actionLocation.triggered.connect(self.location_settings_handle)  # Update location fields
        self.ui.main_widget.actionManual_Control.triggered.connect(partial(self.tcp_client.sendData.emit,
                                                                           "SEND_HOME_STEPS\n"))
        self.ui.main_widget.locatChangeBtn.clicked.connect(self.location_settings_handle)
        self.ui.main_widget.homePositionButton.clicked.connect(self.home_position_return)

        self.ui.plan_obj_win.commandExecutionBtn.clicked.connect(self.plan_obj_command)

        self.ui.sky_scan_win.calculateScanMapBtn.clicked.connect(self.calc_scan_points)
        self.ui.sky_scan_win.startScanBtn.clicked.connect(self.sky_scan_start)

        self.ui.calib_win.repositionButton.clicked.connect(self.calibration_reposition)
        self.ui.sat_sel_diag.satSelectionList.currentTextChanged.connect(self.sat_coords_setter)
        self.ui.sat_sel_diag.coordinateSystemBox.currentTextChanged.connect(self.sat_coords_setter)

        self.ui.saveSettingsSig.connect(self.settings_saver)
        self.ui.tle_settings_widget.buttonBox.accepted.connect(partial(self.ui.saveWaringSig.emit, "TLE"))
        self.ui.main_widget.actionTLE_Settings.triggered.connect(self.show_tle_info)
        self.ui.tle_settings_widget.tleDownloadButton.clicked.connect(self.get_tle)  # Retrieve the TLE upon user
        # request

        self.logger.debug("All signal connections made")

    def app_exit_request(self):
        """
        This function is called whenever the app is about to quit.
        First quit from the thread and then delete both the thread and the corresponding object
        Quit exits the thread and then wait is waiting for the thread exit
        deleteLater, deletes the thread object and the threaded object

        :return: Nothing
        """
        self.tcp_client_thread.quit()
        self.tcp_client_thread.wait()
        self.tcp_client.deleteLater()
        self.tcp_client_thread.deleteLater()
        self.logger.debug("Client thread is closed for sure")

        self.tcp_server_thread.quit()
        self.tcp_server_thread.wait()
        self.tcp_server.deleteLater()
        self.tcp_server_thread.deleteLater()
        self.logger.debug("RPi server thread is surely closed")

        self.tcp_stel_thread.quit()
        self.tcp_stel_thread.wait()
        self.tcp_stellarium.deleteLater()
        self.tcp_stel_thread.deleteLater()
        self.logger.debug("Stellarium server thread is closed for sure and operations handler thread closed")

        self.sim_thread.quit()
        self.sim_thread.wait()
        self.sim_handler.deleteLater()
        self.sim_thread.deleteLater()
        self.logger.debug("Simulation handler thread is closed.")
