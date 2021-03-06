# -*- coding: utf-8 -*-
# IP address regex: https://stackoverflow.com/questions/10086572/ip-address-validation-in-python-using-regex

import os
import sys
import logging
from functools import partial
from PyQt5 import QtCore, QtGui, QtWidgets, uic


class UIRadioTelescopeControl(QtCore.QObject):
    stopMovingRTSig = QtCore.pyqtSignal(name='stopRadioTele')  # Signal to stop dish's motion
    motorsDisabledSig = QtCore.pyqtSignal(name='motorsDisabledUISignal')
    setGUIFromClientSig = QtCore.pyqtSignal(str, name='setTheGUIFromClient')
    setManContStepsSig = QtCore.pyqtSignal(str, str, name='setManContSteps')
    setStyleSkyScanningSig = QtCore.pyqtSignal(tuple, name='setStylesheetForSkyScanning')
    updateCoordFieldsSig = QtCore.pyqtSignal(list, name='coordinateSetterSatelliteDialog')
    tleStatusInfoSig = QtCore.pyqtSignal(str, name='tleStatusIndicatorSignal')
    saveWaringSig = QtCore.pyqtSignal(str, name='saveWarningMessageShowSignal')
    saveSettingsSig = QtCore.pyqtSignal(str, name='notifierToSaveTheSettingsSignal')
    setTLEDataSig = QtCore.pyqtSignal(tuple, name='setTheGUIDataForTLESignal')

    def __init__(self, parent=None):
        super(UIRadioTelescopeControl, self).__init__(parent)
        self.logger = logging.getLogger(__name__)  # Create the logger for the file
        self.motor_warn_msg_shown = False

        # Load the resources binary
        resource_object = QtCore.QResource()
        resource_file = resource_object.registerResource(os.path.abspath("Core/GUI/resources.rcc"))
        if resource_file.bit_length() == 0:
            self.logger.error("Resources file could not be loaded. Program is exiting.")
            sys.exit(-1)  # Indicate an error when exiting

        # Create the main GUI window and the other windows
        self.main_win = QtWidgets.QMainWindow()  # Create the main window of the GUI
        self.ui_man_cont_win = QtWidgets.QMainWindow(parent=self.main_win)  # Create the Manual control window
        self.ui_tcp_win = QtWidgets.QMainWindow(parent=self.main_win)  # Create the TCP settings window object
        self.ui_location_win = QtWidgets.QDialog(parent=self.main_win)  # Create the location settings window object
        self.ui_calibration_win = QtWidgets.QMainWindow(parent=self.main_win)  # Create the calibration window object
        self.ui_planetary_obj_win = QtWidgets.QMainWindow(parent=self.main_win)  # Planetary object selection GUI
        self.ui_sky_scanning_win = QtWidgets.QMainWindow(parent=self.main_win)  # Sky scanning control window

        # Extra dialogs
        self.map_dialog = QtWidgets.QDialog(parent=self.ui_location_win)  # Location selection from map dialog
        self.satellite_dialog = QtWidgets.QDialog(parent=self.ui_calibration_win)  # Satellite selection dialog
        self.tle_settings_dialog = QtWidgets.QDialog(parent=self.main_win)  # Create the TLE settings widget
        self.tle_info_msg_box = QtWidgets.QMessageBox()  # Message box to show TLE retrieval status

        # Initial setup of the message box
        self.tle_info_msg_box.setVisible(False)  # No need to be visible all the time
        self.tle_info_msg_box.setAutoFillBackground(True)
        self.tle_info_msg_box.setWindowTitle("TLE Retriever")
        self.tle_info_msg_box.setStandardButtons(QtWidgets.QMessageBox.NoButton)

        try:
            self.main_widget = self.ui_loader(':/UI_Files/RadioTelescope', self.main_win)
            self.man_cont_widget = self.ui_loader(':/UI_Files/ManualControl', self.ui_man_cont_win)
            self.tcp_widget = self.ui_loader(':/UI_Files/TCPSettings', self.ui_tcp_win)
            self.location_widget = self.ui_loader(':/UI_Files/Location', self.ui_location_win)
            self.map_dialog = self.ui_loader(':/UI_Files/MapsDialog', self.map_dialog)
            self.calib_win = self.ui_loader(':/UI_Files/Calibration', self.ui_calibration_win)
            self.plan_obj_win = self.ui_loader(':/UI_Files/PlanetaryObject', self.ui_planetary_obj_win)
            self.sky_scan_win = self.ui_loader(':/UI_Files/SkyScanning', self.ui_sky_scanning_win)
            self.sat_sel_diag = self.ui_loader(':/UI_Files/SatelliteSelectionDialog', self.satellite_dialog)
            self.tle_settings_widget = self.ui_loader(':/UI_Files/TLESettingsDialog', self.tle_settings_dialog)
        except FileNotFoundError:
            self.logger.exception("Something happened when loading GUI files. See traceback")
            sys.exit(-1)  # Indicate a problematic shutdown
        self.tle_info_msg_box.setParent(self.main_widget)  # Set the main program window to be the parent
        self.tle_info_msg_box.setWindowModality(QtCore.Qt.ApplicationModal)

        # Set the icons for the GUI windows
        try:
            self.main_widget.setWindowIcon(QtGui.QIcon(':/Window_Icons/radiotelescope'))
            self.man_cont_widget.setWindowIcon(QtGui.QIcon(':/Window_Icons/manControl'))
            self.tcp_widget.setWindowIcon(QtGui.QIcon(':/Window_Icons/Net'))
            self.location_widget.setWindowIcon(QtGui.QIcon(':/Window_Icons/location'))
            self.calib_win.setWindowIcon(QtGui.QIcon(':/Window_Icons/calibration'))
            self.plan_obj_win.setWindowIcon(QtGui.QIcon(':/Window_Icons/planetary'))
            self.sky_scan_win.setWindowIcon(QtGui.QIcon(':/Window_Icons/skyScanning'))
            self.sat_sel_diag.setWindowIcon(QtGui.QIcon(':/Window_Icons/satelliteSelection'))
            self.map_dialog.setWindowIcon(QtGui.QIcon(':/Window_Icons/maps'))
            self.tle_settings_widget.setWindowIcon(QtGui.QIcon(':/Window_Icons/TLESettings'))
        except Exception:
            self.logger.exception("Problem setting window icons. See traceback below.")
        self.setup_ui()  # Call the function to make all the connections for the GUI things

        # Timer for the date and time label
        self.timer = QtCore.QTimer()  # Create a timer object
        self.timer.timeout.connect(self.date_time)  # Assign the timeout signal to date and time show
        self.timer.setInterval(1000)  # Update date and time ever second

        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))  # Change the style of the GUI

    @staticmethod
    def ui_loader(ui_resource, base=None):
        ui_file = QtCore.QFile(ui_resource)
        ui_file.open(QtCore.QFile.ReadOnly)
        try:
            parsed_ui = uic.loadUi(ui_file, base)
            return parsed_ui
        finally:
            ui_file.close()

    def setup_ui(self):
        # Make all the necessary connections
        self.main_widget.clientRPiEnableLabel.stateChanged.connect(self.check_box_tcp_client)
        self.main_widget.serverRPiEnableLabel.stateChanged.connect(self.check_box_tcp_rpi_server)
        self.main_widget.tcpStelServChkBox.stateChanged.connect(self.check_box_tcp_stel)
        self.main_widget.homePositioncheckBox.stateChanged.connect(self.check_box_return_home)
        self.main_widget.dishHaultCommandCheckBox.stateChanged.connect(self.check_box_dish_hault)
        self.main_widget.motorCommandCheckBox.stateChanged.connect(self.check_box_motors)

        self.main_widget.actionSettings.triggered.connect(self.tcp_widget.show)  # Show the TCP settings window
        self.main_widget.actionManual_Control.triggered.connect(self.man_cont_widget.show)  # Show manual control window
        self.main_widget.actionLocation.triggered.connect(self.location_widget.show)  # Show location settings dialog
        self.main_widget.actionCalibrate.triggered.connect(self.calib_win.show)
        self.main_widget.actionCalibrate.triggered.connect(self.coordinate_updater_calibration)
        self.main_widget.actionPlanetaryObject.triggered.connect(self.plan_obj_win.show)
        self.main_widget.actionSky_Scanning.triggered.connect(self.sky_scan_win.show)
        self.main_widget.actionSky_Scanning.triggered.connect(self.coordinate_updater_scanning)
        self.main_widget.actionTLE_Settings.triggered.connect(self.tle_settings_widget.show)
        self.main_widget.actionExit.triggered.connect(partial(self.close_application, objec=self.main_widget))

        self.main_widget.stopMovingBtn.clicked.connect(partial(self.stop_motion, objec=self.main_widget))
        self.main_widget.locatChangeBtn.clicked.connect(self.location_widget.show)
        self.main_widget.onTargetProgress.setVisible(False)  # Have the progrees bar invisible at first

        # Signal connections
        self.motorsDisabledSig.connect(self.motors_disabled)
        self.setGUIFromClientSig.connect(self.set_gui_from_client_command)
        self.setStyleSkyScanningSig.connect(self.style_setter_sky_scan)
        self.setManContStepsSig.connect(self.man_cont_step_setter)
        self.updateCoordFieldsSig.connect(self.set_sat_coordinates)
        self.tleStatusInfoSig.connect(self.tle_status)
        self.saveWaringSig.connect(self.save_warning)
        self.setTLEDataSig.connect(self.set_tle_data)

        # Hide the message box when not needed
        self.tle_info_msg_box.accepted.connect(partial(self.tle_info_msg_box.setVisible, False))
        self.tle_info_msg_box.rejected.connect(partial(self.tle_info_msg_box.setVisible, False))

        # Change between widgets
        self.main_widget.stellNextPageBtn.clicked.connect(lambda: self.main_widget.stackedWidget.setCurrentIndex(1))
        self.main_widget.stellPrevPageBtn.clicked.connect(lambda: self.main_widget.stackedWidget.setCurrentIndex(0))
        self.main_widget.stellariumOperationSelect.currentIndexChanged.connect(self.command_list_text)

        # Connect the functions on index change for the settings window
        self.tcp_widget.telServBox.currentIndexChanged.connect(self.ip_selection_box_rpi_server)
        self.tcp_widget.telClientBox.currentIndexChanged.connect(self.ip_selection_box_client)
        self.tcp_widget.stellIPServBox.currentIndexChanged.connect(self.ip_selection_box_stell_server)

        # Make connections for the location settings dialog
        self.location_widget.exitBtn.clicked.connect(self.location_widget.close)  # Close the settings window
        self.location_widget.locationTypeChoose.currentIndexChanged.connect(self.show_map_selection)

        # Make the webview widget for the map
        # Disabled for the moment because it gives an error on Ubuntu
        """
        self.webView = QtWebEngineWidgets.QWebEngineView(self.map_diag.widget)
        self.webView.setUrl(QtCore.QUrl("https://www.google.com/maps"))
        self.webView.setObjectName("webView")
        self.map_diag.formLayout.addWidget(self.webView)
        """

        # Create validators for the TCP port settings entries
        ip_port_validator = QtGui.QIntValidator()  # Create an integer validator
        ip_port_validator.setRange(1025, 65535)  # Set the validator range (lower than 1024 usually they are taken)
        self.tcp_widget.telescopeIPPortServ.setValidator(ip_port_validator)
        self.tcp_widget.telescopeIPPortClient.setValidator(ip_port_validator)
        self.tcp_widget.stellPortServ.setValidator(ip_port_validator)

        # Create validators for the TCP IP settings entries
        ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"  # A regular expression for one numeric IP part
        ip_addr_reg_ex = QtCore.QRegExp("^" + ip_range + "\\." + ip_range + "\\." + ip_range + "\\." + ip_range + "$")
        ip_addr_reg_ex = QtGui.QRegExpValidator(ip_addr_reg_ex)  # Regular expression validator object
        self.tcp_widget.telescopeIPAddrServ.setValidator(ip_addr_reg_ex)
        self.tcp_widget.telescopeIPAddrClient.setValidator(ip_addr_reg_ex)
        self.tcp_widget.stellServInpIP.setValidator(ip_addr_reg_ex)

        # Location settings dialog input fields validation declaration
        loc_validator = QtGui.QDoubleValidator()  # Create a double validator object
        loc_validator.setDecimals(5)
        self.location_widget.latEntry.setValidator(loc_validator)  # loc_validator.setRange(-90.0, 90.0, 5)
        self.location_widget.lonEntry.setValidator(loc_validator)  # loc_validator.setRange(-180.0, 180.0, 5)
        self.location_widget.altEntry.setValidator(loc_validator)  # loc_validator.setRange(0.0, 7000.0, 2)

        # Planetary object action window
        self.plan_obj_win.planObjectTransitGroupBox.toggled.connect(self.check_box_plan_transit)
        self.plan_obj_win.planObjectTrackingGroupBox.toggled.connect(self.check_box_plan_tracking)

        # Sky scanner initializations
        self.sky_scan_win.mapLayoutBox.setTabEnabled(1, False)  # Disable the tab at first
        self.sky_scan_win.coordinateSystemComboBx.currentTextChanged.connect(self.coordinate_updater_scanning)
        self.sky_scan_win.simulateScanningChk.toggled.connect(self.sim_enabler)
        self.sky_scan_win.listPointsCheckBox.toggled.connect(partial(self.sky_scan_win.mapLayoutBox.setTabEnabled, 1))
        self.sky_scan_win.simSpeedLabel.setVisible(False)
        self.sky_scan_win.simSpeedValue.setVisible(False)

        # Calibration GUI initializations and signal connections
        self.calib_win.coordinatSystemcomboBox.currentTextChanged.connect(self.coordinate_updater_calibration)
        self.sat_sel_diag.coordinateSystemBox.currentTextChanged.connect(self.coordinate_updater_satellite)
        self.sat_sel_diag.satSelectionList.currentTextChanged.connect(self.sat_selection_updater)
        self.sat_sel_diag.selectionButton.clicked.connect(self.sat_sel_diag.close)

        # Validate coordinate entry fields
        double_validator = QtGui.QDoubleValidator(-360.0, 360.0, 6)
        double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.sky_scan_win.point1Coord_1Field.setValidator(double_validator)
        self.sky_scan_win.point1Coord_2Field.setValidator(double_validator)
        self.sky_scan_win.point2Coord_1Field.setValidator(double_validator)
        self.sky_scan_win.point2Coord_2Field.setValidator(double_validator)
        self.sky_scan_win.point3Coord_1Field.setValidator(double_validator)
        self.sky_scan_win.point3Coord_2Field.setValidator(double_validator)
        self.sky_scan_win.point4Coord_1Field.setValidator(double_validator)
        self.sky_scan_win.point4Coord_2Field.setValidator(double_validator)

    # Function called every time the corresponding checkbox is selected
    def check_box_tcp_client(self, state):
        if state == QtCore.Qt.Checked:
            self.main_widget.connectRadioTBtn.setEnabled(True)  # And also enable the button selection
        else:
            self.main_widget.connectRadioTBtn.setEnabled(False)  # And also disable the button selection

    # Function called every time the corresponding checkbox is selected
    def check_box_tcp_rpi_server(self, state):
        if state == QtCore.Qt.Checked:
            self.main_widget.serverRPiConnBtn.setEnabled(True)  # And also enable the button selection
        else:
            self.main_widget.serverRPiConnBtn.setEnabled(False)  # And also disable the button selection

    # Function called every time the corresponding checkbox is selected
    def check_box_tcp_stel(self, state):
        if state == QtCore.Qt.Checked:
            self.main_widget.connectStellariumBtn.setEnabled(True)
        else:
            self.main_widget.connectStellariumBtn.setEnabled(False)

    # Function called when the enable/disable checkbox is pressed
    def check_box_return_home(self, state):
        if state == QtCore.Qt.Checked:
            self.main_widget.homePositionButton.setEnabled(True)
        else:
            self.main_widget.homePositionButton.setEnabled(False)

    def check_box_dish_hault(self, state):
        if state == QtCore.Qt.Checked:
            self.main_widget.stopMovingBtn.setEnabled(True)
        else:
            self.main_widget.stopMovingBtn.setEnabled(False)

    def check_box_motors(self, state):
        if state == QtCore.Qt.Checked:
            self.main_widget.motorCommandButton.setEnabled(True)
        else:
            self.main_widget.motorCommandButton.setEnabled(False)

    def check_box_plan_tracking(self, state):
        if state is True:
            self.plan_obj_win.planObjectTransitGroupBox.setChecked(False)
        else:
            self.plan_obj_win.planObjectTransitGroupBox.setChecked(True)

    def check_box_plan_transit(self, state):
        if state is True:
            self.plan_obj_win.planObjectTrackingGroupBox.setChecked(False)
        else:
            self.plan_obj_win.planObjectTrackingGroupBox.setChecked(True)

    # Set the label of the command on change
    def command_list_text(self):
        self.main_widget.commandStellIndLabel.setText(self.main_widget.stellariumOperationSelect.currentText())
        if self.main_widget.stellariumOperationSelect.currentText() == "Transit":
            self.main_widget.transitTimeValue.setEnabled(True)
            self.main_widget.transitTimeLablel.setEnabled(True)
        else:
            self.main_widget.transitTimeValue.setEnabled(False)
            self.main_widget.transitTimeLablel.setEnabled(False)

    # Change the IP fields according to choice
    def ip_selection_box_rpi_server(self):
        stat = self.tcp_widget.telServBox.currentText()
        if stat == "Localhost":
            self.tcp_widget.telescopeIPAddrServ.setText("127.0.0.1")
            self.tcp_widget.telescopeIPAddrServ.setEnabled(False)
        elif stat == "Remote":
            self.tcp_widget.telescopeIPAddrServ.setEnabled(False)
        elif stat == "Custom":
            self.tcp_widget.telescopeIPAddrServ.setEnabled(True)

    def ip_selection_box_client(self):
        if self.tcp_widget.telClientBox.currentText() == "Remote":
            self.tcp_widget.telescopeIPAddrClient.setEnabled(True)  # self.tcp_widg.telescopeIPAddrClient.setText("")
        else:
            self.tcp_widget.telescopeIPAddrClient.setEnabled(False)
            self.tcp_widget.telescopeIPAddrClient.setText("127.0.0.1")

    def ip_selection_box_stell_server(self):
        if self.tcp_widget.stellIPServBox.currentText() == "Localhost":
            self.tcp_widget.stellServInpIP.setText("127.0.0.1")  # else:  # self.tcp_widg.stellServInpIP.setText("")

    def show_map_selection(self):
        if self.location_widget.locationTypeChoose.currentText() == "Google Maps":
            self.location_widget.latEntry.setEnabled(False)
            self.location_widget.lonEntry.setEnabled(False)
            self.location_widget.altEntry.setEnabled(False)
            self.map_dialog.show()
        else:
            self.location_widget.latEntry.setEnabled(True)
            self.location_widget.lonEntry.setEnabled(True)
            self.location_widget.altEntry.setEnabled(True)

    # Handle the motion stop request
    def stop_motion(self, objec):
        choice = QtWidgets.QMessageBox.warning(objec, 'Stop Radio telescope', "Stop the currently moving dish?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            self.stopMovingRTSig.emit()  # Send the motion stop signal
        else:
            pass

    # Signal handler for GUI formatting used for the stellarium connection
    @QtCore.pyqtSlot(str, name='conStellStat')
    def stell_tcp_gui_handle(self, data: str):
        if data == "Waiting":
            self.main_widget.connectStellariumBtn.setText("Stop")  # Change user's selection
            self.main_widget.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
            self.main_widget.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                                      "color:#ffb400;\">Waiting...</span></p></body></html>")
            self.main_widget.nextPageLabel.setEnabled(False)  # Disable the next page label
            self.main_widget.stellNextPageBtn.setEnabled(False)  # Disable the button to avoid changing to next page
            self.main_widget.stackedWidget.setCurrentIndex(0)  # Stay in the same widget
        elif data == "Connected":
            self.main_widget.connectStellariumBtn.setText("Disable")  # Change user's selection
            self.main_widget.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
            self.main_widget.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                                      "color:#00ff00;\">Connected</span></p></body></html>")
            self.main_widget.nextPageLabel.setEnabled(True)  # Enable the label to indicate functionality
            self.main_widget.stellNextPageBtn.setEnabled(
                True)  # Enable next page transition, since we have a connection
            self.main_widget.stackedWidget.setCurrentIndex(1)  # Change the widget index since we are connected
        elif data == "Disconnected":
            self.main_widget.connectStellariumBtn.setText("Enable")
            self.main_widget.tcpStelServChkBox.setCheckState(QtCore.Qt.Checked)
            self.main_widget.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                                      "color:#ff0000;\">Disconnected</span></p></body></html>")
            self.main_widget.nextPageLabel.setEnabled(False)  # Disable the next page label
            self.main_widget.stellNextPageBtn.setEnabled(False)  # Disable the button to avoid changing to next page
            self.main_widget.stackedWidget.setCurrentIndex(0)
        self.main_widget.commandStellIndLabel.setText(self.main_widget.stellariumOperationSelect.currentText())
        if self.main_widget.stellariumOperationSelect.currentText() == "Transit":
            self.main_widget.transitTimeValue.setEnabled(True)
            self.main_widget.transitTimeLablel.setEnabled(True)
        else:
            self.main_widget.transitTimeValue.setEnabled(False)
            self.main_widget.transitTimeLablel.setEnabled(False)

    # Signal handler to show the received data fro Stellarium on the GUI
    @QtCore.pyqtSlot(float, float, name='dataStellShow')
    def stell_data_show(self, received_ra: float, received_dec: float):
        self.main_widget.raPosInd_2.setText("%.5fh" % received_ra)  # Update the corresponding field
        self.main_widget.decPosInd_2.setText("%.5f" % received_dec + u"\u00b0")  # Update the corresponding field

    # Signal handler to show the status of the TCP client connected to RPi
    @QtCore.pyqtSlot(str, name='conClientStat')
    def client_tcp_gui_handle(self, data: str):
        if data == "Connecting":
            self.main_widget.connectRadioTBtn.setText("Stop")  # Change user's selection
            self.main_widget.clientRPiEnableLabel.setCheckState(QtCore.Qt.Unchecked)
            self.main_widget.rpiConStatTextInd.setText("<html><head/><body><p><span style=\" "
                                                       "color:#ffb400;\">Connecting...</span></p></body></html>")
        elif data == "Connected":
            self.main_widget.connectRadioTBtn.setText("Disconnect")
            self.main_widget.clientRPiEnableLabel.setCheckState(QtCore.Qt.Unchecked)
            self.main_widget.rpiConStatTextInd.setText("<html><head/><body><p><span style=\" "
                                                       "color:#00ff00;\">Connected</span></p></body></html>")
        elif data == "Disconnected":
            self.main_widget.connectRadioTBtn.setText("Connect")  # Change user's selection
            self.main_widget.clientRPiEnableLabel.setCheckState(QtCore.Qt.Checked)
            self.main_widget.rpiConStatTextInd.setText("<html><head/><body><p><span style=\" "
                                                       "color:#ff0000;\">Disconnected</span></p></body></html>")

    # Signal handler to show the status of the RPi server on the GUI
    @QtCore.pyqtSlot(str, name='conRPiStat')
    def rpi_tcp_gui_handle(self, data: str):
        if data == "Waiting":
            self.main_widget.serverRPiConnBtn.setText("Stop")  # Change user's selection
            self.main_widget.serverRPiEnableLabel.setCheckState(QtCore.Qt.Unchecked)
            self.main_widget.servForRpiConTextInd.setText("<html><head/><body><p><span style=\" "
                                                          "color:#ffb400;\">Waiting...</span></p></body></html>")
            self.main_widget.movTextInd.setText("<html><head/><body><p><span style=\" "
                                                "color:#ff0000;\">No</span></p></body></html>")
        elif data == "Connected":
            self.main_widget.serverRPiConnBtn.setText("Disable")
            self.main_widget.serverRPiEnableLabel.setCheckState(QtCore.Qt.Unchecked)
            self.main_widget.servForRpiConTextInd.setText("<html><head/><body><p><span style=\" "
                                                          "color:#00ff00;\">Connected</span></p></body></html>")
        elif data == "Disconnected":
            self.main_widget.serverRPiConnBtn.setText("Enable")  # Change user's selection
            self.main_widget.serverRPiEnableLabel.setCheckState(QtCore.Qt.Checked)  # Set the checkbox to checked state
            self.main_widget.servForRpiConTextInd.setText("<html><head/><body><p><span style=\" "
                                                          "color:#ff0000;\">Disconnected</span></p></body></html>")
            self.main_widget.movTextInd.setText("<html><head/><body><p><span style=\" "
                                                "color:#ff0000;\">No</span></p></body></html>")

    @QtCore.pyqtSlot(float, float, name='pos_data_show')
    def pos_data_show(self, show_ra: float, show_dec: float):
        self.main_widget.raPosInd.setText("%.5fh" % show_ra)  # Show the RA of the dish on the GUI
        self.main_widget.decPosInd.setText("%.5f" % show_dec + u"\u00b0")  # Show the declination of the dish on the GUI

    @QtCore.pyqtSlot(float, name='move_progress')
    def move_progress(self, percent: float):
        self.main_widget.onTargetProgress.setValue(percent)  # Set the percentage of the progress according to position

    @QtCore.pyqtSlot(name='motorsDisabledUISignal')
    def motors_disabled(self):
        if not self.motor_warn_msg_shown:
            msg = QtWidgets.QMessageBox()  # Create the message box object
            self.motor_warn_msg_shown = True  # Set the show indicator before showing the window
            msg.warning(self.main_widget, 'Motor Warning', "<html><head/><body><p align=\"center\"><span style = \""
                                                           "font-weight:600\" style = \"color:#ff0000;\">"
                                                           "Motors are disabled!!</span></p></body></html>"
                                                           "\n<html><head/><body><p><span style = "
                                                           "\"font-style:italic\" style = \""
                                                           "color:#ffb000\">No moving operation will be "
                                                           "performed.</span></p></body></html>",
                        QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            msg.show()  # Show the message to the user
            self.motor_warn_msg_shown = False  # It gets here only after the window is closed

    @QtCore.pyqtSlot(str, name='setTheGUIFromClient')
    def set_gui_from_client_command(self, command: str):
        if command == "OK":
            self.tcp_widget.clientStatus.setText("OK")  # Set the response if the client responded correctly
        elif command == "STOPPED_MOVING":
            self.main_widget.movTextInd.setText("<html><head/><body><p><span style=\" "
                                                "color:#ff0000;\">No</span></p></body></html>")
            self.main_widget.onTargetProgress.setVisible(False)  # Make the progress bar invisible
        elif command == "STARTED_MOVING":
            self.main_widget.movTextInd.setText("<html><head/><body><p><span style=\" "
                                                "color:#00ff00;\">Yes</span></p></body></html>")
            self.main_widget.onTargetProgress.setVisible(True)  # Make the progress bar visible
        elif command == "TRACKING_STARTED":
            self.main_widget.trackTextInd.setText("<html><head/><body><p><span style=\" "
                                                  "color:#00ff00;\">Yes</span></p></body></html>")
        elif command == "TRACKING_STOPPED":
            self.main_widget.trackTextInd.setText("<html><head/><body><p><span style=\" "
                                                  "color:#ff0000;\">No</span></p></body></html>")
        elif command == "MOTORS_ENABLED":
            self.main_widget.motorStatusText.setText("<html><head/><body><p><span style=\" "
                                                     "color:#00ff00;\">Enabled</span></p></body></html>")
            self.main_widget.motorCommandButton.setText("Disable")
            self.main_widget.motorCommandCheckBox.setCheckState(QtCore.Qt.Unchecked)
        elif command == "MOTORS_DISABLED":
            self.main_widget.motorStatusText.setText("<html><head/><body><p><span style=\" "
                                                     "color:#ff0000;\">Disabled</span></p></body></html>")
            self.main_widget.motorCommandButton.setText("Enable")
            self.main_widget.motorCommandCheckBox.setCheckState(QtCore.Qt.Checked)
            self.motors_disabled()  # Call the disabled motors function

    @QtCore.pyqtSlot(str, str, name='setManContSteps')
    def man_cont_step_setter(self, axis: str, steps: str):
        if axis == "RA":
            self.man_cont_widget.raStepText.setText(steps)  # Update the manual control window
        elif axis == "DEC":
            self.man_cont_widget.decStepText.setText(steps)

    @QtCore.pyqtSlot(tuple, name='setStylesheetForSkyScanning')
    def style_setter_sky_scan(self, points: tuple):
        # Make boxes red wherever there is no input
        if points[0][0] == "":
            self.sky_scan_win.point1Coord_1Field.setStyleSheet("border: 1px solid red")
        else:
            self.sky_scan_win.point1Coord_1Field.setStyleSheet("")
        if points[1][0] == "":
            self.sky_scan_win.point2Coord_1Field.setStyleSheet("border: 1px solid red")
        else:
            self.sky_scan_win.point2Coord_1Field.setStyleSheet("")
        if points[2][0] == "":
            self.sky_scan_win.point3Coord_1Field.setStyleSheet("border: 1px solid red")
        else:
            self.sky_scan_win.point3Coord_1Field.setStyleSheet("")
        if points[3][0] == "":
            self.sky_scan_win.point4Coord_1Field.setStyleSheet("border: 1px solid red")
        else:
            self.sky_scan_win.point4Coord_1Field.setStyleSheet("")

        if points[0][1] == "":
            self.sky_scan_win.point1Coord_2Field.setStyleSheet("border: 1px solid red")
        else:
            self.sky_scan_win.point1Coord_2Field.setStyleSheet("")
        if points[1][1] == "":
            self.sky_scan_win.point2Coord_2Field.setStyleSheet("border: 1px solid red")
        else:
            self.sky_scan_win.point2Coord_2Field.setStyleSheet("")
        if points[2][1] == "":
            self.sky_scan_win.point3Coord_2Field.setStyleSheet("border: 1px solid red")
        else:
            self.sky_scan_win.point3Coord_2Field.setStyleSheet("")
        if points[3][1] == "":
            self.sky_scan_win.point4Coord_2Field.setStyleSheet("border: 1px solid red")
        else:
            self.sky_scan_win.point4Coord_2Field.setStyleSheet("")

    def coordinate_updater_scanning(self, system: str):
        if isinstance(system, str):
            system = self.sky_scan_win.coordinateSystemComboBx.currentText()
        coord_1 = "<html><head/><body><p><span style=\" font-weight:600;\">%s</span></p></body></html>"
        coord_2 = "<html><head/><body><p><span style=\" font-weight:600;\">%s</span></p></body></html>"

        # Create coordinate field validator object
        validator_coord_1 = QtGui.QDoubleValidator()
        validator_coord_2 = QtGui.QDoubleValidator()
        validator_coord_1.setNotation(QtGui.QDoubleValidator.StandardNotation)
        validator_coord_2.setNotation(QtGui.QDoubleValidator.StandardNotation)

        if system == "Horizontal":
            coord_1 = coord_1 % "Alt: "
            coord_2 = coord_2 % "Az:  "
            validator_coord_1.setRange(0.0, 90.0, 6)
            validator_coord_2.setRange(0.0, 360.0, 6)
        elif system == "Equatorial":
            coord_1 = coord_1 % "RA:  "
            coord_2 = coord_2 % "DEC: "
            validator_coord_1.setRange(0.0, 360.0, 6)
            validator_coord_2.setRange(-18.0, 18.0, 6)
        elif system == "Galactic":
            coord_1 = coord_1 % "Lat: "
            coord_2 = coord_2 % "Lon: "
            validator_coord_1.setRange(-90.0, 90.0, 6)
            validator_coord_2.setRange(0.0, 360.0, 6)
        elif system == "Ecliptical":
            coord_1 = coord_1 % "Lat: "
            coord_2 = coord_2 % "Lon: "
            validator_coord_1.setRange(-90.0, 90.0, 6)
            validator_coord_2.setRange(0.0, 360.0, 6)

        # Set first coordinate of the system
        self.sky_scan_win.point1Coord_1Label.setText(coord_1)
        self.sky_scan_win.point1Coord_1Field.setValidator(validator_coord_1)
        self.sky_scan_win.point2Coord_1Label.setText(coord_1)
        self.sky_scan_win.point2Coord_1Field.setValidator(validator_coord_1)
        self.sky_scan_win.point3Coord_1Label.setText(coord_1)
        self.sky_scan_win.point3Coord_1Field.setValidator(validator_coord_1)
        self.sky_scan_win.point4Coord_1Label.setText(coord_1)
        self.sky_scan_win.point3Coord_1Field.setValidator(validator_coord_1)
        self.sky_scan_win.stepSizeCoord1.setText(coord_1)

        # Set the second coordinate of the system
        self.sky_scan_win.point1Coord_2Label.setText(coord_2)
        self.sky_scan_win.point1Coord_2Field.setValidator(validator_coord_2)
        self.sky_scan_win.point2Coord_2Label.setText(coord_2)
        self.sky_scan_win.point2Coord_2Field.setValidator(validator_coord_2)
        self.sky_scan_win.point3Coord_2Label.setText(coord_2)
        self.sky_scan_win.point3Coord_2Field.setValidator(validator_coord_2)
        self.sky_scan_win.point4Coord_2Label.setText(coord_2)
        self.sky_scan_win.point4Coord_2Field.setValidator(validator_coord_2)
        self.sky_scan_win.stepSizeCoord2.setText(coord_2)

    def coordinate_updater_calibration(self, system: str):
        # Set the fields visible at first
        self.calib_win.calibCoord_1_Text.setVisible(True)
        self.calib_win.calibCoord_2_Text.setVisible(True)
        self.calib_win.calibCoord_2_Label.setVisible(True)

        if isinstance(system, str):
            system = self.calib_win.coordinatSystemcomboBox.currentText()
        coord_1 = "<html><head/><body><p><span style=\" font-weight:600;\">%s</span></p></body></html>"
        coord_2 = "<html><head/><body><p><span style=\" font-weight:600;\">%s</span></p></body></html>"

        # Create coordinate field validator object
        validator_coord_1 = QtGui.QDoubleValidator()
        validator_coord_2 = QtGui.QDoubleValidator()
        validator_coord_1.setNotation(QtGui.QDoubleValidator.StandardNotation)
        validator_coord_2.setNotation(QtGui.QDoubleValidator.StandardNotation)

        if system == "Horizontal":
            coord_1 = coord_1 % "Alt: "
            coord_2 = coord_2 % "Az:  "
            validator_coord_1.setRange(0.0, 90.0, 6)
            validator_coord_2.setRange(0.0, 360.0, 6)
        elif system == "Equatorial":
            coord_1 = coord_1 % "RA:  "
            coord_2 = coord_2 % "DEC: "
            validator_coord_1.setRange(0.0, 360.0, 6)
            validator_coord_2.setRange(-18.0, 18.0, 6)
        elif system == "Galactic":
            coord_1 = coord_1 % "Lat: "
            coord_2 = coord_2 % "Lon: "
            validator_coord_1.setRange(-90.0, 90.0, 6)
            validator_coord_2.setRange(0.0, 360.0, 6)
        elif system == "Ecliptic":
            coord_1 = coord_1 % "Lat: "
            coord_2 = coord_2 % "Lon: "
            validator_coord_1.setRange(-90.0, 90.0, 6)
            validator_coord_2.setRange(0.0, 360.0, 6)
        elif system == "Motor steps":
            coord_1 = coord_1 % "RA: "
            coord_2 = coord_2 % "DEC: "
            validator_coord_1 = QtGui.QIntValidator(-150000, 150000)
            validator_coord_2 = QtGui.QIntValidator(-180000, 180000)
        elif system == "Satellite":
            coord_1 = coord_1 % "Satellite..."
            self.coordinate_updater_satellite()  # Update the coordinates on the first call
            self.calib_win.calibCoord_1_Text.setVisible(False)
            self.calib_win.calibCoord_2_Text.setVisible(False)
            self.calib_win.calibCoord_2_Label.setVisible(False)
            self.sat_sel_diag.show()

        # Set first coordinate of the system
        self.calib_win.calibCoord_1_Label.setText(coord_1)
        self.calib_win.calibCoord_1_Text.setValidator(validator_coord_1)

        # Set the second coordinate of the system
        self.calib_win.calibCoord_2_Label.setText(coord_2)
        self.calib_win.calibCoord_2_Text.setValidator(validator_coord_2)

    def coordinate_updater_satellite(self, system=""):
        if system == "":
            system = self.sat_sel_diag.coordinateSystemBox.currentText()
        coord_1 = "<html><head/><body><p><span style=\" font-weight:600;\">%s</span></p></body></html>"
        coord_2 = "<html><head/><body><p><span style=\" font-weight:600;\">%s</span></p></body></html>"

        if system == "Horizontal":
            coord_1 = coord_1 % "Alt: "
            coord_2 = coord_2 % "Az:  "
        elif system == "Celestial":
            coord_1 = coord_1 % "HA:  "
            coord_2 = coord_2 % "DEC: "

        # Set first coordinate of the system
        self.sat_sel_diag.coord_1_Label.setText(coord_1)

        # Set the second coordinate of the system
        self.sat_sel_diag.coord_2_Label.setText(coord_2)

    def sat_selection_updater(self, satellite: str):
        formatter = "<html><head/><body><p><span style=\" font-weight:600;\" " \
                    "style = \"font-style:italic;\">%s</span></p></body></html>"

        self.calib_win.calibCoord_1_Label.setText(formatter % satellite)

    @QtCore.pyqtSlot(list, name='coordinateSetterSatelliteDialog')
    def set_sat_coordinates(self, coords: list):
        if self.sat_sel_diag.coordinateSystemBox.currentText() == "Horizontal":
            c_1 = coords[0][0]
            c_2 = coords[0][1]
        else:
            c_1 = coords[1][0]
            c_2 = coords[1][1]
        self.sat_sel_diag.coord_1_Value.setText(str(c_1))
        self.sat_sel_diag.coord_2_Value.setText(str(c_2))

    def sim_enabler(self, state: bool):
        if state is True:
            self.sky_scan_win.calculateScanMapBtn.setText("Simulate")
        else:
            self.sky_scan_win.calculateScanMapBtn.setText("Calculate")

    @QtCore.pyqtSlot(str, name='tleStatusIndicatorSignal')
    def tle_status(self, status: str):
        formatted_text_1 = "<html><head/><body><p align=\"center\"><span style=\" font-weight:600;\" " \
                           "style = \"font-style:italic;\">%s</span></p></body></html>"
        formatted_text_green = "<html><head/><body><p align=\"center\"><span style=\" color:#00ff00;\" " \
                               "style=\"font-weight:600;\">%s</span></p></body></html>"
        formatted_text_red = "<html><head/><body><p align=\"center\"><span style=\" color:#ff0000;\" " \
                             "style=\"font-weight:600;\">%s</span></p></body></html>"
        self.tle_info_msg_box.setText(formatted_text_1 % "Updating TLE files....")

        info = status.split("^")
        if status == "":
            self.tle_info_msg_box.setIcon(QtWidgets.QMessageBox.Information)
            self.tle_info_msg_box.setInformativeText("<html><head/><body><p align=\"center\"><span "
                                                     "style=\" font-weight:600;\" "
                                                     "style = \"color:#ffb400\">Wait...</span></p></body></html>")
            self.tle_info_msg_box.setVisible(True)  # Set the message box to visible before showing
            self.tle_info_msg_box.show()

        if info[0] == "Success":
            self.tle_info_msg_box.setIcon(QtWidgets.QMessageBox.Information)
            self.tle_info_msg_box.setInformativeText(formatted_text_green % info[1])
            self.tle_info_msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.tle_info_msg_box.setDefaultButton(QtWidgets.QMessageBox.Ok)
        elif info[0] == "Error":
            self.tle_info_msg_box.setIcon(QtWidgets.QMessageBox.Warning)
            self.tle_info_msg_box.setInformativeText(formatted_text_red % info[1])
            self.tle_info_msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.tle_info_msg_box.setDefaultButton(QtWidgets.QMessageBox.Ok)

        # Show the details regarding the error
        try:
            self.tle_info_msg_box.setDetailedText(info[2])
        except IndexError:
            self.tle_info_msg_box.setDetailedText("")

    @QtCore.pyqtSlot(tuple, name='setTheGUIDataForTLESignal')
    def set_tle_data(self, data: tuple):
        if data[0] == "yes":
            self.tle_settings_widget.autoUpdateSelection.setCheckState(QtCore.Qt.Checked)
        else:
            self.tle_settings_widget.autoUpdateSelection.setCheckState(QtCore.Qt.Unchecked)
        self.tle_settings_widget.intervalValue.setValue(int(data[2]))
        self.tle_settings_widget.tleURL.setText(data[1])

    # Handle the settings saving request
    @QtCore.pyqtSlot(str, name='saveWarningMessageShowSignal')
    def save_warning(self, objec: str):
        if objec == "TLE":
            window = self.tle_settings_widget
        elif objec == "TCP":
            window = self.tcp_widget

        choice = QtWidgets.QMessageBox.warning(window, 'Save settings', "Do you really want to save the settings?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)

        if choice == QtWidgets.QMessageBox.Yes:
            self.saveSettingsSig.emit(objec)  # Send the saving signal
            window.close()  # Close the window after saving
        else:
            pass

    # Show current date and time on the GUI
    def date_time(self):
        self.main_widget.dateAndTimeLabel.setText(QtCore.QDateTime.currentDateTimeUtc().toString())

    # Show the main GUI
    def show_application(self):
        self.timer.start()  # Start the timer for the date and time label
        self.date_time()  # Call that initially to render it on the GUI
        self.main_widget.show()  # Show the GUI window

    # Ask before exiting the GUI
    @staticmethod
    def close_application(window_object):
        choice = QtWidgets.QMessageBox.question(window_object, 'Exit', "Are you sure?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            QtCore.QCoreApplication.quit()  # If user selects "Yes", then exit from the application
        else:
            pass  # If user selects "No" then do not exit
