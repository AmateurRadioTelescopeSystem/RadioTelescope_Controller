# -*- coding: utf-8 -*-
# IP address regex: https://stackoverflow.com/questions/10086572/ip-address-validation-in-python-using-regex

from PyQt5 import QtCore, QtGui, QtWidgets, uic, QtWebEngineWidgets
from functools import partial
from GUI import resources
import logging
import sys
import os


class Ui_RadioTelescopeControl(QtCore.QObject):
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
        super(Ui_RadioTelescopeControl, self).__init__(parent)
        self.logD = logging.getLogger(__name__)  # Create the logger for the file
        self.motor_warn_msg_shown = False

        # Create the main GUI window and the other windows
        self.mainWin = QtWidgets.QMainWindow()  # Create the main window of the GUI
        self.uiManContWin = QtWidgets.QMainWindow()  # Create the Manual control window
        self.uiTCPWin = QtWidgets.QMainWindow()  # Create the TCP settings window object
        self.uiLocationWin = QtWidgets.QDialog()  # Create the location settings window object
        self.uiCalibrationWin = QtWidgets.QMainWindow()  # Create the calibration window object
        self.uiPlanetaryObjWin = QtWidgets.QMainWindow()  # Create the planetary object selection window
        self.uiSkyScanningWin = QtWidgets.QMainWindow()  # Create the sky scanning control window

        # Extra dialogs
        self.mapDialog = QtWidgets.QDialog()  # Create the location selection from map dialog
        self.satelliteDialog = QtWidgets.QDialog()  # Create the satellite selection dialog
        self.tleInfoMsgBox = QtWidgets.QMessageBox()  # Message box to show TLE retrieval status
        self.tleSettingsDialog = QtWidgets.QDialog()  # Create the TLE settings widget

        # Initial setup of the message box
        self.tleInfoMsgBox.setParent(self.mainWin)  # Set the main program window to be the parent
        self.tleInfoMsgBox.setWindowTitle("TLE Retriever")
        self.tleInfoMsgBox.setWindowModality(QtCore.Qt.ApplicationModal)
        self.tleInfoMsgBox.setStandardButtons(QtWidgets.QMessageBox.NoButton)

        # Set the icons for the GUI windows
        try:
            self.mainWin.setWindowIcon(QtGui.QIcon(os.path.abspath('Icons/radiotelescope.png')))
            self.uiManContWin.setWindowIcon(QtGui.QIcon(os.path.abspath('Icons/manControl.png')))
            self.uiTCPWin.setWindowIcon(QtGui.QIcon(os.path.abspath('Icons/Net.png')))
            self.uiLocationWin.setWindowIcon(QtGui.QIcon(os.path.abspath('Icons/location.png')))
            self.uiCalibrationWin.setWindowIcon(QtGui.QIcon(os.path.abspath('Icons/calibration.png')))
            self.uiPlanetaryObjWin.setWindowIcon(QtGui.QIcon(os.path.abspath('Icons/planetary.png')))
            self.uiSkyScanningWin.setWindowIcon(QtGui.QIcon(os.path.abspath('Icons/skyScanning.png')))
            self.satelliteDialog.setWindowIcon(QtGui.QIcon(os.path.abspath('Icons/satelliteSelection.png')))
            self.mapDialog.setWindowIcon(QtGui.QIcon(os.path.abspath('Icons/maps.png')))
            self.tleSettingsDialog.setWindowIcon(QtGui.QIcon(os.path.abspath('Icons/TLESettings.png')))
        except Exception:
            self.logD.exception("Problem setting window icons. See traceback below.")

        try:
            self.main_widg = uic.loadUi(os.path.abspath('UI_Files/RadioTelescope.ui'), self.mainWin)
            self.man_cn_widg = uic.loadUi(os.path.abspath('UI_Files/ManualControl.ui'), self.uiManContWin)
            self.tcp_widg = uic.loadUi(os.path.abspath('UI_Files/TCPSettings.ui'), self.uiTCPWin)
            self.loc_widg = uic.loadUi(os.path.abspath('UI_Files/Location.ui'), self.uiLocationWin)
            self.map_diag = uic.loadUi(os.path.abspath('UI_Files/MapsDialog.ui'), self.mapDialog)
            self.calib_win = uic.loadUi(os.path.abspath('UI_Files/Calibration.ui'), self.uiCalibrationWin)
            self.plan_obj_win = uic.loadUi(os.path.abspath('UI_Files/PlanetaryObject.ui'), self.uiPlanetaryObjWin)
            self.sky_scan_win = uic.loadUi(os.path.abspath('UI_Files/SkyScanning.ui'), self.uiSkyScanningWin)
            self.sat_sel_diag = uic.loadUi(os.path.abspath('UI_Files/SatelliteSelectionDialog.ui'),
                                           self.satelliteDialog)
            self.tle_settings_widg = uic.loadUi(os.path.abspath('UI_Files/TLESettingsDialog.ui'),
                                                self.tleSettingsDialog)
        except (FileNotFoundError, Exception):
            self.logD.exception("Something happened when loading GUI files. See traceback")
            sys.exit(-1)  # Indicate a problematic shutdown
        self.setupUi()  # Call the function to make all the connections for the GUI things

        # Timer for the date and time label
        self.timer = QtCore.QTimer()  # Create a timer object
        self.timer.timeout.connect(self.dateTime)  # Assign the timeout signal to date and time show
        self.timer.setInterval(1000)  # Update date and time ever second

        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))  # Change the style of the GUI

    def setupUi(self):
        # Set the font according to the OS
        fnt = QtGui.QFont()  # Create the font object
        fnt.setStyleHint(QtGui.QFont.Monospace)  # Set the a default font in case some of the following is not found
        if sys.platform.startswith('linux'):
            fnt.setFamily("Ubuntu")  # Set the font for Ubuntu/linux
            fnt.setPointSize(11)
        elif sys.platform.startswith('win32'):
            fnt.setFamily("Segoe UI")  # Set the font for Windows
            fnt.setPointSize(8)

        # Set the font in the widgets
        self.main_widg.setFont(fnt)
        self.man_cn_widg.setFont(fnt)

        # Make all the necessary connections
        self.main_widg.clientRPiEnableLabel.stateChanged.connect(
            self.checkBoxTCPRTClient)  # Assign functionality to the checkbox
        self.main_widg.serverRPiEnableLabel.stateChanged.connect(self.checkBoxTCPRTServer)
        self.main_widg.tcpStelServChkBox.stateChanged.connect(
            self.checkBoxTCPStel)  # Assign functionality to the checkbox
        self.main_widg.homePositioncheckBox.stateChanged.connect(self.checkBoxReturnHome)
        self.main_widg.dishHaultCommandCheckBox.stateChanged.connect(self.checkBoxDishHault)
        self.main_widg.motorCommandCheckBox.stateChanged.connect(self.checkBoxMotors)

        self.main_widg.actionSettings.triggered.connect(self.uiTCPWin.show)  # Show the TCP settings window
        self.main_widg.actionManual_Control.triggered.connect(self.uiManContWin.show)  # Show the manual control window
        self.main_widg.actionLocation.triggered.connect(self.uiLocationWin.show)  # Show the location settings dialog
        self.main_widg.actionCalibrate.triggered.connect(self.uiCalibrationWin.show)
        self.main_widg.actionCalibrate.triggered.connect(self.coordinate_updater_calibration)
        self.main_widg.actionPlanetaryObject.triggered.connect(self.uiPlanetaryObjWin.show)
        self.main_widg.actionSky_Scanning.triggered.connect(self.uiSkyScanningWin.show)
        self.main_widg.actionSky_Scanning.triggered.connect(self.coordinate_updater_scanning)
        self.main_widg.actionTLE_Settings.triggered.connect(self.tle_settings_widg.show)
        self.main_widg.actionExit.triggered.connect(partial(self.close_application, objec=self.mainWin))

        self.main_widg.stopMovingBtn.clicked.connect(partial(self.stopMotion, objec=self.mainWin))
        self.main_widg.locatChangeBtn.clicked.connect(self.uiLocationWin.show)
        self.main_widg.onTargetProgress.setVisible(False)  # Have the progrees bar invisible at first

        # Signal connections
        self.motorsDisabledSig.connect(self.motorsDisabled)
        self.setGUIFromClientSig.connect(self.setGUIFromClientCommand)
        self.setStyleSkyScanningSig.connect(self.styleSetterSkyScan)
        self.setManContStepsSig.connect(self.manContStepSetter)
        self.updateCoordFieldsSig.connect(self.set_sat_coordinates)
        self.tleStatusInfoSig.connect(self.tle_status)
        self.saveWaringSig.connect(self.save_warning)
        self.setTLEDataSig.connect(self.set_tle_data)

        # Change between widgets
        self.main_widg.stellNextPageBtn.clicked.connect(lambda: self.main_widg.stackedWidget.setCurrentIndex(1))
        self.main_widg.stellPrevPageBtn.clicked.connect(lambda: self.main_widg.stackedWidget.setCurrentIndex(0))
        self.main_widg.stellariumOperationSelect.currentIndexChanged.connect(self.commandListText)

        # Connect the functions on index change for the settings window
        self.tcp_widg.telServBox.currentIndexChanged.connect(self.ipSelectionBoxRPiServer)
        self.tcp_widg.telClientBox.currentIndexChanged.connect(self.ipSelectionBoxClient)
        self.tcp_widg.stellIPServBox.currentIndexChanged.connect(self.ipSelectionBoxStellServer)

        # Make connections for the location settings dialog
        self.loc_widg.exitBtn.clicked.connect(self.uiLocationWin.close)  # Close the settings window when requested
        self.loc_widg.locationTypeChoose.currentIndexChanged.connect(self.showMapSelection)

        # Make the webview widget for the map
        # Disabled for the moment because it gives an error on Ubuntu
        '''
        self.webView = QtWebEngineWidgets.QWebEngineView(self.map_diag.widget)
        self.webView.setUrl(QtCore.QUrl("https://www.google.com/maps"))
        self.webView.setObjectName("webView")
        self.map_diag.formLayout.addWidget(self.webView)
        '''

        # Create validators for the TCP port settings entries
        ipPortValidator = QtGui.QIntValidator()  # Create an integer validator
        ipPortValidator.setRange(1025, 65535)  # Set the validator range (lower than 1024 usually they are taken)
        self.tcp_widg.telescopeIPPortServ.setValidator(ipPortValidator)
        self.tcp_widg.telescopeIPPortClient.setValidator(ipPortValidator)
        self.tcp_widg.stellPortServ.setValidator(ipPortValidator)

        # Create validators for the TCP IP settings entries
        ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"  # A regular expression for one numeric IP part
        ipAddrRegEx = QtCore.QRegExp("^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$")
        ipAddrRegEx = QtGui.QRegExpValidator(ipAddrRegEx)  # Regular expression validator object
        self.tcp_widg.telescopeIPAddrServ.setValidator(ipAddrRegEx)
        self.tcp_widg.telescopeIPAddrClient.setValidator(ipAddrRegEx)
        self.tcp_widg.stellServInpIP.setValidator(ipAddrRegEx)

        # Location settings dialog input fields validation declaration
        locValidator = QtGui.QDoubleValidator()  # Create a double validator object
        locValidator.setDecimals(5)
        self.loc_widg.latEntry.setValidator(locValidator)  # locValidator.setRange(-90.0, 90.0, 5)
        self.loc_widg.lonEntry.setValidator(locValidator)  # locValidator.setRange(-180.0, 180.0, 5)
        self.loc_widg.altEntry.setValidator(locValidator)  # locValidator.setRange(0.0, 7000.0, 2)

        # Planetary object action window
        self.plan_obj_win.planObjectTransitGroupBox.toggled.connect(self.checkBoxPlanTransit)
        self.plan_obj_win.planObjectTrackingGroupBox.toggled.connect(self.checkBoxPlanTracking)

        # Sky scanner initializations
        self.sky_scan_win.mapLayoutBox.setTabEnabled(1, False)  # Disable the tab at first
        self.sky_scan_win.coordinateSystemComboBx.currentTextChanged.connect(self.coordinate_updater_scanning)
        self.sky_scan_win.simulateScanningChk.toggled.connect(self.simEnabler)
        self.sky_scan_win.listPointsCheckBox.toggled.connect(
            partial(self.sky_scan_win.mapLayoutBox.setTabEnabled, 1))
        self.sky_scan_win.simSpeedLabel.setVisible(False)
        self.sky_scan_win.simSpeedValue.setVisible(False)

        # Calibration GUI initializations and signal connections
        self.calib_win.coordinatSystemcomboBox.currentTextChanged.connect(self.coordinate_updater_calibration)
        self.sat_sel_diag.coordinateSystemBox.currentTextChanged.connect(self.coordinate_updater_satellite)
        self.sat_sel_diag.satSelectionList.currentTextChanged.connect(self.sat_selection_updater)
        self.sat_sel_diag.selectionButton.clicked.connect(self.satelliteDialog.close)

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
    def checkBoxTCPRTClient(self, state):
        if state == QtCore.Qt.Checked:
            self.main_widg.connectRadioTBtn.setEnabled(True)  # And also enable the button selection
        else:
            self.main_widg.connectRadioTBtn.setEnabled(False)  # And also disable the button selection

    # Function called every time the corresponding checkbox is selected
    def checkBoxTCPRTServer(self, state):
        if state == QtCore.Qt.Checked:
            self.main_widg.serverRPiConnBtn.setEnabled(True)  # And also enable the button selection
        else:
            self.main_widg.serverRPiConnBtn.setEnabled(False)  # And also disable the button selection

    # Function called every time the corresponding checkbox is selected
    def checkBoxTCPStel(self, state):
        if state == QtCore.Qt.Checked:
            self.main_widg.connectStellariumBtn.setEnabled(True)
        else:
            self.main_widg.connectStellariumBtn.setEnabled(False)

    # Function called when the enable/disable checkbox is pressed
    def checkBoxReturnHome(self, state):
        if state == QtCore.Qt.Checked:
            self.main_widg.homePositionButton.setEnabled(True)
        else:
            self.main_widg.homePositionButton.setEnabled(False)

    def checkBoxDishHault(self, state):
        if state == QtCore.Qt.Checked:
            self.main_widg.stopMovingBtn.setEnabled(True)
        else:
            self.main_widg.stopMovingBtn.setEnabled(False)

    def checkBoxMotors(self, state):
        if state == QtCore.Qt.Checked:
            self.main_widg.motorCommandButton.setEnabled(True)
        else:
            self.main_widg.motorCommandButton.setEnabled(False)

    def checkBoxPlanTracking(self, state):
        if state is True:
            self.plan_obj_win.planObjectTransitGroupBox.setChecked(False)
        else:
            self.plan_obj_win.planObjectTransitGroupBox.setChecked(True)

    def checkBoxPlanTransit(self, state):
        if state is True:
            self.plan_obj_win.planObjectTrackingGroupBox.setChecked(False)
        else:
            self.plan_obj_win.planObjectTrackingGroupBox.setChecked(True)

    # Set the label of the command on change
    def commandListText(self):
        self.main_widg.commandStellIndLabel.setText(self.main_widg.stellariumOperationSelect.currentText())
        if self.main_widg.stellariumOperationSelect.currentText() == "Transit":
            self.main_widg.transitTimeValue.setEnabled(True)
            self.main_widg.transitTimeLablel.setEnabled(True)
        else:
            self.main_widg.transitTimeValue.setEnabled(False)
            self.main_widg.transitTimeLablel.setEnabled(False)

    # Change the IP fields according to choice
    def ipSelectionBoxRPiServer(self):
        stat = self.tcp_widg.telServBox.currentText()
        if stat == "Localhost":
            self.tcp_widg.telescopeIPAddrServ.setText("127.0.0.1")
            self.tcp_widg.telescopeIPAddrServ.setEnabled(False)
        elif stat == "Remote":
            self.tcp_widg.telescopeIPAddrServ.setEnabled(False)
        elif stat == "Custom":
            self.tcp_widg.telescopeIPAddrServ.setEnabled(True)

    def ipSelectionBoxClient(self):
        if self.tcp_widg.telClientBox.currentText() == "Remote":
            self.tcp_widg.telescopeIPAddrClient.setEnabled(True)
            # self.tcp_widg.telescopeIPAddrClient.setText("")
        else:
            self.tcp_widg.telescopeIPAddrClient.setEnabled(False)
            self.tcp_widg.telescopeIPAddrClient.setText("127.0.0.1")

    def ipSelectionBoxStellServer(self):
        if self.tcp_widg.stellIPServBox.currentText() == "Localhost":
            self.tcp_widg.stellServInpIP.setText("127.0.0.1")
        # else:
            # self.tcp_widg.stellServInpIP.setText("")

    def showMapSelection(self):
        if self.loc_widg.locationTypeChoose.currentText() == "Google Maps":
            self.loc_widg.latEntry.setEnabled(False)
            self.loc_widg.lonEntry.setEnabled(False)
            self.loc_widg.altEntry.setEnabled(False)
            self.mapDialog.show()
        else:
            self.loc_widg.latEntry.setEnabled(True)
            self.loc_widg.lonEntry.setEnabled(True)
            self.loc_widg.altEntry.setEnabled(True)

    # Handle the motion stop request
    def stopMotion(self, objec):
        choice = QtWidgets.QMessageBox.warning(objec, 'Stop Radio telescope', "Stop the currently moving dish?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            self.stopMovingRTSig.emit()  # Send the motion stop signal
        else:
            pass

    # Signal handler for GUI formatting used for the stellarium connection
    @QtCore.pyqtSlot(str, name='conStellStat')
    def stellTCPGUIHandle(self, data: str):
        if data == "Waiting":
            self.main_widg.connectStellariumBtn.setText("Stop")  # Change user's selection
            self.main_widg.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
            self.main_widg.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                                    "color:#ffb400;\">Waiting...</span></p></body></html>")
            self.main_widg.nextPageLabel.setEnabled(False)  # Disable the next page label
            self.main_widg.stellNextPageBtn.setEnabled(False)  # Disable the button to avoid changing to next page
            self.main_widg.stackedWidget.setCurrentIndex(0)  # Stay in the same widget
        elif data == "Connected":
            self.main_widg.connectStellariumBtn.setText("Disable")  # Change user's selection
            self.main_widg.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
            self.main_widg.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                                    "color:#00ff00;\">Connected</span></p></body></html>")
            self.main_widg.nextPageLabel.setEnabled(True)  # Enable the label to indicate functionality
            self.main_widg.stellNextPageBtn.setEnabled(True)  # Enable next page transition, since we have a connection
            self.main_widg.stackedWidget.setCurrentIndex(1)  # Change the widget index since we are connected
        elif data == "Disconnected":
            self.main_widg.connectStellariumBtn.setText("Enable")
            self.main_widg.tcpStelServChkBox.setCheckState(QtCore.Qt.Checked)
            self.main_widg.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                                    "color:#ff0000;\">Disconnected</span></p></body></html>")
            self.main_widg.nextPageLabel.setEnabled(False)  # Disable the next page label
            self.main_widg.stellNextPageBtn.setEnabled(False)  # Disable the button to avoid changing to next page
            self.main_widg.stackedWidget.setCurrentIndex(0)
        self.main_widg.commandStellIndLabel.setText(
            self.main_widg.stellariumOperationSelect.currentText())  # Set the text initially
        if self.main_widg.stellariumOperationSelect.currentText() == "Transit":
            self.main_widg.transitTimeValue.setEnabled(True)
            self.main_widg.transitTimeLablel.setEnabled(True)
        else:
            self.main_widg.transitTimeValue.setEnabled(False)
            self.main_widg.transitTimeLablel.setEnabled(False)

    # Signal handler to show the received data fro Stellarium on the GUI
    @QtCore.pyqtSlot(float, float, name='dataStellShow')
    def stellDataShow(self, ra: float, dec: float):
        self.main_widg.raPosInd_2.setText("%.5fh" % ra)  # Update the corresponding field
        self.main_widg.decPosInd_2.setText("%.5f" % dec + u"\u00b0")  # Update the corresponding field

    # Signal handler to show the status of the TCP client connected to RPi
    @QtCore.pyqtSlot(str, name='conClientStat')
    def clientTCPGUIHandle(self, data: str):
        if data == "Connecting":
            self.main_widg.connectRadioTBtn.setText("Stop")  # Change user's selection
            self.main_widg.clientRPiEnableLabel.setCheckState(QtCore.Qt.Unchecked)
            self.main_widg.rpiConStatTextInd.setText("<html><head/><body><p><span style=\" "
                                                     "color:#ffb400;\">Connecting...</span></p></body></html>")
        elif data == "Connected":
            self.main_widg.connectRadioTBtn.setText("Disconnect")
            self.main_widg.clientRPiEnableLabel.setCheckState(QtCore.Qt.Unchecked)
            self.main_widg.rpiConStatTextInd.setText("<html><head/><body><p><span style=\" "
                                                     "color:#00ff00;\">Connected</span></p></body></html>")
        elif data == "Disconnected":
            self.main_widg.connectRadioTBtn.setText("Connect")  # Change user's selection
            self.main_widg.clientRPiEnableLabel.setCheckState(QtCore.Qt.Checked)
            self.main_widg.rpiConStatTextInd.setText("<html><head/><body><p><span style=\" "
                                                     "color:#ff0000;\">Disconnected</span></p></body></html>")

    # Signal handler to show the status of the RPi server on the GUI
    @QtCore.pyqtSlot(str, name='conRPiStat')
    def rpiTCPGUIHandle(self, data: str):
        if data == "Waiting":
            self.main_widg.serverRPiConnBtn.setText("Stop")  # Change user's selection
            self.main_widg.serverRPiEnableLabel.setCheckState(QtCore.Qt.Unchecked)
            self.main_widg.servForRpiConTextInd.setText("<html><head/><body><p><span style=\" "
                                                        "color:#ffb400;\">Waiting...</span></p></body></html>")
            self.main_widg.movTextInd.setText("<html><head/><body><p><span style=\" "
                                              "color:#ff0000;\">No</span></p></body></html>")
        elif data == "Connected":
            self.main_widg.serverRPiConnBtn.setText("Disable")
            self.main_widg.serverRPiEnableLabel.setCheckState(QtCore.Qt.Unchecked)
            self.main_widg.servForRpiConTextInd.setText("<html><head/><body><p><span style=\" "
                                                        "color:#00ff00;\">Connected</span></p></body></html>")
        elif data == "Disconnected":
            self.main_widg.serverRPiConnBtn.setText("Enable")  # Change user's selection
            self.main_widg.serverRPiEnableLabel.setCheckState(QtCore.Qt.Checked)  # Set the checkbox to checked state
            self.main_widg.servForRpiConTextInd.setText("<html><head/><body><p><span style=\" "
                                                        "color:#ff0000;\">Disconnected</span></p></body></html>")
            self.main_widg.movTextInd.setText("<html><head/><body><p><span style=\" "
                                              "color:#ff0000;\">No</span></p></body></html>")

    @QtCore.pyqtSlot(float, float, name='posDataShow')
    def posDataShow(self, ra: float, dec: float):
        self.main_widg.raPosInd.setText("%.5fh" % ra)  # Show the RA of the dish on the GUI
        self.main_widg.decPosInd.setText("%.5f" % dec + u"\u00b0")  # Show the declination of the dish on the GUI

    @QtCore.pyqtSlot(float, name='moveProgress')
    def moveProgress(self, percent: float):
        self.main_widg.onTargetProgress.setValue(percent)  # Set the percentage of the progress according to position

    @QtCore.pyqtSlot(name='motorsDisabledUISignal')
    def motorsDisabled(self):
        if not self.motor_warn_msg_shown:
            msg = QtWidgets.QMessageBox()  # Create the message box object
            self.motor_warn_msg_shown = True  # Set the show indicator before showing the window
            msg.warning(self.mainWin, 'Motor Warning',
                        "<html><head/><body><p align=\"center\"><span style = \""
                        "font-weight:600\" style = \"color:#ff0000;\">"
                        "Motors are disabled!!</span></p></body></html>"
                        "\n<html><head/><body><p><span style = \"font-style:italic\" style = \""
                        "color:#ffb000\">No moving operation will be performed.</span></p></body></html>",
                        QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            msg.show()  # Show the message to the user
            self.motor_warn_msg_shown = False  # It gets here only after the window is closed

    @QtCore.pyqtSlot(str, name='setTheGUIFromClient')
    def setGUIFromClientCommand(self, command: str):
        if command == "OK":
            self.tcp_widg.clientStatus.setText("OK")  # Set the response if the client responded correctly
        elif command == "STOPPED_MOVING":
            self.main_widg.movTextInd.setText("<html><head/><body><p><span style=\" "
                                              "color:#ff0000;\">No</span></p></body></html>")
            self.main_widg.onTargetProgress.setVisible(False)  # Make the progress bar invisible
        elif command == "STARTED_MOVING":
            self.main_widg.movTextInd.setText("<html><head/><body><p><span style=\" "
                                              "color:#00ff00;\">Yes</span></p></body></html>")
            self.main_widg.onTargetProgress.setVisible(True)  # Make the progress bar visible
        elif command == "TRACKING_STARTED":
            self.main_widg.trackTextInd.setText("<html><head/><body><p><span style=\" "
                                                "color:#00ff00;\">Yes</span></p></body></html>")
        elif command == "TRACKING_STOPPED":
            self.main_widg.trackTextInd.setText("<html><head/><body><p><span style=\" "
                                                "color:#ff0000;\">No</span></p></body></html>")
        elif command == "MOTORS_ENABLED":
            self.main_widg.motorStatusText.setText("<html><head/><body><p><span style=\" "
                                                   "color:#00ff00;\">Enabled</span></p></body></html>")
            self.main_widg.motorCommandButton.setText("Disable")
            self.main_widg.motorCommandCheckBox.setCheckState(QtCore.Qt.Unchecked)
        elif command == "MOTORS_DISABLED":
            self.main_widg.motorStatusText.setText("<html><head/><body><p><span style=\" "
                                                   "color:#ff0000;\">Disabled</span></p></body></html>")
            self.main_widg.motorCommandButton.setText("Enable")
            self.main_widg.motorCommandCheckBox.setCheckState(QtCore.Qt.Checked)
            self.motorsDisabled()  # Call the disabled motors function

    @QtCore.pyqtSlot(str, str, name='setManContSteps')
    def manContStepSetter(self, axis: str, steps: str):
        if axis == "RA":
            self.man_cn_widg.raStepText.setText(steps)  # Update the manual control window
        elif axis == "DEC":
            self.man_cn_widg.decStepText.setText(steps)

    @QtCore.pyqtSlot(tuple, name='setStylesheetForSkyScanning')
    def styleSetterSkyScan(self, points: tuple):
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
        if type(system) is not str:
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
            validator_coord_2.setRange(0.0, 360.0, 6)
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

        if type(system) is not str:
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
            validator_coord_2.setRange(0.0, 360.0, 6)
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
            self.satelliteDialog.show()

        # Set first coordinate of the system
        self.calib_win.calibCoord_1_Label.setText(coord_1)
        self.calib_win.calibCoord_1_Text.setValidator(validator_coord_1)

        # Set the second coordinate of the system
        self.calib_win.calibCoord_2_Label.setText(coord_2)
        self.calib_win.calibCoord_2_Text.setValidator(validator_coord_2)

    def coordinate_updater_satellite(self, system=""):
        if system is "":
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

    def simEnabler(self, state: bool):
        if state is True:
            self.sky_scan_win.calculateScanMapBtn.setText("Simulate")
        else:
            self.sky_scan_win.calculateScanMapBtn.setText("Calculate")

    @QtCore.pyqtSlot(str, name='tleStatusIndicatorSignal')
    def tle_status(self, status: str):
        formated_text_1 = "<html><head/><body><p align=\"center\"><span style=\" font-weight:600;\" " \
                          "style = \"font-style:italic;\">%s</span></p></body></html>"
        formated_text_green = "<html><head/><body><p align=\"center\"><span style=\" color:#00ff00;\" " \
                              "style=\"font-weight:600;\">%s</span></p></body></html>"
        formated_text_red = "<html><head/><body><p align=\"center\"><span style=\" color:#ff0000;\" " \
                            "style=\"font-weight:600;\">%s</span></p></body></html>"
        self.tleInfoMsgBox.setText(formated_text_1 % "Updating TLE files....")

        info = status.split("^")
        if status == "":
            self.tleInfoMsgBox.setIcon(QtWidgets.QMessageBox.Information)
            self.tleInfoMsgBox.setInformativeText("<html><head/><body><p align=\"center\"><span "
                                                  "style=\" font-weight:600;\" "
                                                  "style = \"color:#ffb400\">Wait...</span></p></body></html>")
            self.tleInfoMsgBox.show()

        if info[0] == "Success":
            self.tleInfoMsgBox.setIcon(QtWidgets.QMessageBox.Information)
            self.tleInfoMsgBox.setInformativeText(formated_text_green % info[1])
            self.tleInfoMsgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.tleInfoMsgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
        elif info[0] == "Error":
            self.tleInfoMsgBox.setIcon(QtWidgets.QMessageBox.Warning)
            self.tleInfoMsgBox.setInformativeText(formated_text_red % info[1])
            self.tleInfoMsgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.tleInfoMsgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)

        # Show the details regarding the error
        try:
            self.tleInfoMsgBox.setDetailedText(info[2])
        except IndexError:
            self.tleInfoMsgBox.setDetailedText("")

    @QtCore.pyqtSlot(tuple, name='setTheGUIDataForTLESignal')
    def set_tle_data(self, data: tuple):
        if data[0] == "yes":
            self.tle_settings_widg.autoUpdateSelection.setCheckState(QtCore.Qt.Checked)
        else:
            self.tle_settings_widg.autoUpdateSelection.setCheckState(QtCore.Qt.Unchecked)
        self.tle_settings_widg.intervalValue.setValue(int(data[2]))
        self.tle_settings_widg.tleURL.setText(data[1])

    # Handle the settings saving request
    @QtCore.pyqtSlot(str, name='saveWarningMessageShowSignal')
    def save_warning(self, objec: str):
        if objec == "TLE":
            window = self.tle_settings_widg
        elif objec == "TCP":
            window = self.tcp_widg

        choice = QtWidgets.QMessageBox.warning(window, 'Save settings', "Do you really want to save the settings?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)

        if choice == QtWidgets.QMessageBox.Yes:
            self.saveSettingsSig.emit(objec)  # Send the saving signal
            window.close()  # Close the window after saving
        else:
            pass

    # Show current date and time on the GUI
    def dateTime(self):
        self.main_widg.dateAndTimeLabel.setText(QtCore.QDateTime.currentDateTimeUtc().toString())

    # Show the main GUI
    def show_application(self):
        self.timer.start()  # Start the timer for the date and time label
        self.dateTime()  # Call that initially to render it on the GUI
        self.mainWin.show()  # Show the GUI window

    # Ask before exiting the GUI
    def close_application(self, objec):
        choice = QtWidgets.QMessageBox.question(objec, 'Exit', "Are you sure?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            QtCore.QCoreApplication.quit()  # If user selects "Yes", then exit from the application
        else:
            pass  # If user selects "No" then do not exit
