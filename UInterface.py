# -*- coding: utf-8 -*-

# The GUI code is automatically generated from the PyQt5 package
# by running the pyuic5 command on the ui file from QtDesigner

from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import GUI_Windows.TCPSettings as TCPSettings


class Ui_RadioTelescopeControl(QtCore.QObject):
    def __init__(self):
        super(Ui_RadioTelescopeControl, self).__init__()
        # Create all other windows, except from the main one
        self.uiTCP = TCPSettings.Ui_TCPSettings()  # Create the TCP settings pop-up window

        # Create the main GUI window
        self.mainWin = QtWidgets.QMainWindow()  # Create the main window of th GUI
        self.setupUi(self.mainWin)  # Call the function to make all the connections for the GUI things

        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))  # Change the style of the GUI

    def setupUi(self, RadioTelescopeControl):
        RadioTelescopeControl.setWindowIcon(QtGui.QIcon('radiotelescope.png'))
        RadioTelescopeControl.setObjectName("RadioTelescopeControl")
        RadioTelescopeControl.setWindowModality(QtCore.Qt.NonModal)
        RadioTelescopeControl.resize(373, 468)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        RadioTelescopeControl.setFont(font)
        self.centralwidget = QtWidgets.QWidget(RadioTelescopeControl)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setStatusTip("")
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.groupBox = QtWidgets.QGroupBox(self.tab)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.frame_2 = QtWidgets.QFrame(self.groupBox)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setObjectName("frame_2")
        self.formLayout_2 = QtWidgets.QFormLayout(self.frame_2)
        self.formLayout_2.setObjectName("formLayout_2")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.rpiConnText = QtWidgets.QLabel(self.frame_2)
        self.rpiConnText.setObjectName("rpiConnText")
        self.horizontalLayout_11.addWidget(self.rpiConnText)
        self.rpiConStatTextInd = QtWidgets.QLabel(self.frame_2)
        self.rpiConStatTextInd.setObjectName("rpiConStatTextInd")
        self.horizontalLayout_11.addWidget(self.rpiConStatTextInd)
        self.formLayout_2.setLayout(0, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout_11)
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        self.label_4.setObjectName("label_4")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_5 = QtWidgets.QLabel(self.frame_2)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.raPosInd = QtWidgets.QLabel(self.frame_2)
        self.raPosInd.setObjectName("raPosInd")
        self.horizontalLayout_2.addWidget(self.raPosInd)
        self.formLayout_2.setLayout(2, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_6 = QtWidgets.QLabel(self.frame_2)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout.addWidget(self.label_6)
        self.decPosInd = QtWidgets.QLabel(self.frame_2)
        self.decPosInd.setObjectName("decPosInd")
        self.horizontalLayout.addWidget(self.decPosInd)
        self.formLayout_2.setLayout(3, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout)
        spacerItem = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout_2.setItem(4, QtWidgets.QFormLayout.LabelRole, spacerItem)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.tcpConRTChkBox = QtWidgets.QCheckBox(self.frame_2)
        self.tcpConRTChkBox.setText("")
        self.tcpConRTChkBox.setObjectName("tcpConRTChkBox")
        self.horizontalLayout_9.addWidget(self.tcpConRTChkBox)
        self.tcpConRTLabel = QtWidgets.QLabel(self.frame_2)
        self.tcpConRTLabel.setEnabled(False)
        self.tcpConRTLabel.setObjectName("tcpConRTLabel")
        self.horizontalLayout_9.addWidget(self.tcpConRTLabel)
        self.formLayout_2.setLayout(5, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout_9)
        self.connectRadioTBtn = QtWidgets.QPushButton(self.frame_2)
        self.connectRadioTBtn.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connectRadioTBtn.sizePolicy().hasHeightForWidth())
        self.connectRadioTBtn.setSizePolicy(sizePolicy)
        self.connectRadioTBtn.setAutoDefault(False)
        self.connectRadioTBtn.setDefault(False)
        self.connectRadioTBtn.setFlat(False)
        self.connectRadioTBtn.setObjectName("connectRadioTBtn")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.connectRadioTBtn)
        self.gridLayout.addWidget(self.frame_2, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.stackedWidget = QtWidgets.QStackedWidget(self.groupBox_2)
        self.stackedWidget.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.stackedWidget.setObjectName("stackedWidget")
        self.stackedWidgetPage1 = QtWidgets.QWidget()
        self.stackedWidgetPage1.setObjectName("stackedWidgetPage1")
        self.formLayout = QtWidgets.QFormLayout(self.stackedWidgetPage1)
        self.formLayout.setObjectName("formLayout")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.stellarConStatText = QtWidgets.QLabel(self.stackedWidgetPage1)
        self.stellarConStatText.setObjectName("stellarConStatText")
        self.horizontalLayout_8.addWidget(self.stellarConStatText)
        self.stellConStatText = QtWidgets.QLabel(self.stackedWidgetPage1)
        self.stellConStatText.setObjectName("stellConStatText")
        self.horizontalLayout_8.addWidget(self.stellConStatText)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout_8)
        spacerItem1 = QtWidgets.QSpacerItem(40, 2, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(2, QtWidgets.QFormLayout.LabelRole, spacerItem1)
        self.label_2 = QtWidgets.QLabel(self.stackedWidgetPage1)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.stellariumOperationSelect = QtWidgets.QComboBox(self.stackedWidgetPage1)
        self.stellariumOperationSelect.setStatusTip("")
        self.stellariumOperationSelect.setObjectName("stellariumOperationSelect")
        self.stellariumOperationSelect.addItem("")
        self.stellariumOperationSelect.addItem("")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.stellariumOperationSelect)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.tcpStelServChkBox = QtWidgets.QCheckBox(self.stackedWidgetPage1)
        self.tcpStelServChkBox.setText("")
        self.tcpStelServChkBox.setObjectName("tcpStelServChkBox")
        self.horizontalLayout_10.addWidget(self.tcpStelServChkBox)
        self.tcpStelServLabel = QtWidgets.QLabel(self.stackedWidgetPage1)
        self.tcpStelServLabel.setEnabled(False)
        self.tcpStelServLabel.setObjectName("tcpStelServLabel")
        self.horizontalLayout_10.addWidget(self.tcpStelServLabel)
        self.formLayout.setLayout(5, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout_10)
        self.connectStellariumBtn = QtWidgets.QPushButton(self.stackedWidgetPage1)
        self.connectStellariumBtn.setEnabled(False)
        self.connectStellariumBtn.setAcceptDrops(False)
        self.connectStellariumBtn.setCheckable(False)
        self.connectStellariumBtn.setObjectName("connectStellariumBtn")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.connectStellariumBtn)
        self.nextPageLabel = QtWidgets.QLabel(self.stackedWidgetPage1)
        self.nextPageLabel.setEnabled(False)
        self.nextPageLabel.setObjectName("nextPageLabel")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.nextPageLabel)
        self.stellNextPageBtn = QtWidgets.QToolButton(self.stackedWidgetPage1)
        self.stellNextPageBtn.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stellNextPageBtn.sizePolicy().hasHeightForWidth())
        self.stellNextPageBtn.setSizePolicy(sizePolicy)
        self.stellNextPageBtn.setAutoRaise(True)
        self.stellNextPageBtn.setArrowType(QtCore.Qt.RightArrow)
        self.stellNextPageBtn.setObjectName("stellNextPageBtn")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.stellNextPageBtn)
        self.stackedWidget.addWidget(self.stackedWidgetPage1)
        self.stackedWidgetPage2 = QtWidgets.QWidget()
        self.stackedWidgetPage2.setObjectName("stackedWidgetPage2")
        self.formLayout_5 = QtWidgets.QFormLayout(self.stackedWidgetPage2)
        self.formLayout_5.setObjectName("formLayout_5")
        spacerItem2 = QtWidgets.QSpacerItem(40, 5, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout_5.setItem(0, QtWidgets.QFormLayout.LabelRole, spacerItem2)
        self.label_13 = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.label_13.setObjectName("label_13")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_13)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_15 = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_6.addWidget(self.label_15)
        self.raPosInd_2 = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.raPosInd_2.setObjectName("raPosInd_2")
        self.horizontalLayout_6.addWidget(self.raPosInd_2)
        self.formLayout_5.setLayout(2, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_16 = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.label_16.setObjectName("label_16")
        self.horizontalLayout_7.addWidget(self.label_16)
        self.decPosInd_2 = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.decPosInd_2.setObjectName("decPosInd_2")
        self.horizontalLayout_7.addWidget(self.decPosInd_2)
        self.formLayout_5.setLayout(3, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout_7)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout_5.setItem(4, QtWidgets.QFormLayout.SpanningRole, spacerItem3)
        self.previousPageLabel = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.previousPageLabel.setObjectName("previousPageLabel")
        self.formLayout_5.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.previousPageLabel)
        self.stellPrevPageBtn = QtWidgets.QToolButton(self.stackedWidgetPage2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stellPrevPageBtn.sizePolicy().hasHeightForWidth())
        self.stellPrevPageBtn.setSizePolicy(sizePolicy)
        self.stellPrevPageBtn.setAutoRaise(True)
        self.stellPrevPageBtn.setArrowType(QtCore.Qt.LeftArrow)
        self.stellPrevPageBtn.setObjectName("stellPrevPageBtn")
        self.formLayout_5.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.stellPrevPageBtn)
        self.stackedWidget.addWidget(self.stackedWidgetPage2)
        self.gridLayout_2.addWidget(self.stackedWidget, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_2, 0, 1, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_3.setCheckable(False)
        self.groupBox_3.setObjectName("groupBox_3")
        self.formLayout_3 = QtWidgets.QFormLayout(self.groupBox_3)
        self.formLayout_3.setObjectName("formLayout_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_12 = QtWidgets.QLabel(self.groupBox_3)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_4.addWidget(self.label_12)
        self.latTextInd = QtWidgets.QLabel(self.groupBox_3)
        self.latTextInd.setObjectName("latTextInd")
        self.horizontalLayout_4.addWidget(self.latTextInd)
        self.formLayout_3.setLayout(0, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_10 = QtWidgets.QLabel(self.groupBox_3)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_3.addWidget(self.label_10)
        self.lonTextInd = QtWidgets.QLabel(self.groupBox_3)
        self.lonTextInd.setObjectName("lonTextInd")
        self.horizontalLayout_3.addWidget(self.lonTextInd)
        self.formLayout_3.setLayout(1, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_14 = QtWidgets.QLabel(self.groupBox_3)
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_5.addWidget(self.label_14)
        self.altTextInd = QtWidgets.QLabel(self.groupBox_3)
        self.altTextInd.setObjectName("altTextInd")
        self.horizontalLayout_5.addWidget(self.altTextInd)
        self.formLayout_3.setLayout(2, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout_5)
        self.locatChangeBtn = QtWidgets.QPushButton(self.groupBox_3)
        self.locatChangeBtn.setObjectName("locatChangeBtn")
        self.formLayout_3.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.locatChangeBtn)
        spacerItem4 = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout_3.setItem(3, QtWidgets.QFormLayout.SpanningRole, spacerItem4)
        self.gridLayout_4.addWidget(self.groupBox_3, 1, 0, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_4.setObjectName("groupBox_4")
        self.formLayout_4 = QtWidgets.QFormLayout(self.groupBox_4)
        self.formLayout_4.setObjectName("formLayout_4")
        self.label_8 = QtWidgets.QLabel(self.groupBox_4)
        self.label_8.setObjectName("label_8")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.stopMovingBtn = QtWidgets.QPushButton(self.groupBox_4)
        self.stopMovingBtn.setObjectName("stopMovingBtn")
        self.formLayout_4.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.stopMovingBtn)
        self.onTargetProgress = QtWidgets.QProgressBar(self.groupBox_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.onTargetProgress.sizePolicy().hasHeightForWidth())
        self.onTargetProgress.setSizePolicy(sizePolicy)
        self.onTargetProgress.setProperty("value", 10)
        self.onTargetProgress.setInvertedAppearance(False)
        self.onTargetProgress.setObjectName("onTargetProgress")
        self.formLayout_4.setWidget(4, QtWidgets.QFormLayout.SpanningRole, self.onTargetProgress)
        self.label_11 = QtWidgets.QLabel(self.groupBox_4)
        self.label_11.setObjectName("label_11")
        self.formLayout_4.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_11)
        self.movTextInd = QtWidgets.QLabel(self.groupBox_4)
        self.movTextInd.setObjectName("movTextInd")
        self.formLayout_4.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.movTextInd)
        spacerItem5 = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout_4.setItem(5, QtWidgets.QFormLayout.SpanningRole, spacerItem5)
        self.trackTextInd = QtWidgets.QLabel(self.groupBox_4)
        self.trackTextInd.setObjectName("trackTextInd")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.trackTextInd)
        self.gridLayout_4.addWidget(self.groupBox_4, 1, 1, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout_3.addWidget(self.tabWidget, 0, 0, 2, 1)
        RadioTelescopeControl.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(RadioTelescopeControl)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 385, 21))
        self.menubar.setObjectName("menubar")
        self.menuThis_is_a_menu = QtWidgets.QMenu(self.menubar)
        self.menuThis_is_a_menu.setObjectName("menuThis_is_a_menu")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        self.menuTCP = QtWidgets.QMenu(self.menubar)
        self.menuTCP.setObjectName("menuTCP")
        RadioTelescopeControl.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(RadioTelescopeControl)
        self.statusbar.setObjectName("statusbar")
        RadioTelescopeControl.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(RadioTelescopeControl)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSettings = QtWidgets.QAction(RadioTelescopeControl)
        self.actionSettings.setObjectName("actionSettings")
        self.actionLicense = QtWidgets.QAction(RadioTelescopeControl)
        self.actionLicense.setObjectName("actionLicense")
        self.actionAbout = QtWidgets.QAction(RadioTelescopeControl)
        self.actionAbout.setObjectName("actionAbout")
        self.actionExit = QtWidgets.QAction(RadioTelescopeControl)
        self.actionExit.setObjectName("actionExit")
        self.actionSave = QtWidgets.QAction(RadioTelescopeControl)
        self.actionSave.setObjectName("actionSave")
        self.actionCalibration = QtWidgets.QAction(RadioTelescopeControl)
        self.actionCalibration.setObjectName("actionCalibration")
        self.actionLocation = QtWidgets.QAction(RadioTelescopeControl)
        self.actionLocation.setObjectName("actionLocation")
        self.actionManual_Control = QtWidgets.QAction(RadioTelescopeControl)
        self.actionManual_Control.setObjectName("actionManual_Control")
        self.menuThis_is_a_menu.addAction(self.actionOpen)
        self.menuThis_is_a_menu.addAction(self.actionSave)
        self.menuThis_is_a_menu.addSeparator()
        self.menuThis_is_a_menu.addAction(self.actionExit)
        self.menuTools.addAction(self.actionCalibration)
        self.menuTools.addAction(self.actionLocation)
        self.menuTools.addAction(self.actionManual_Control)
        self.menuAbout.addAction(self.actionAbout)
        self.menuAbout.addAction(self.actionLicense)
        self.menuTCP.addAction(self.actionSettings)
        self.menubar.addAction(self.menuThis_is_a_menu.menuAction())
        self.menubar.addAction(self.menuTCP.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        # Make all the necessary connections
        self.tcpConRTChkBox.stateChanged.connect(self.checkBoxTCPRT)  # Assign functionality to the checkbox
        self.tcpStelServChkBox.stateChanged.connect(self.checkBoxTCPStel)  # Assign functionality to the checkbox
        self.actionSettings.triggered.connect(self.uiTCP.windShow)  # Show the TCP settings window
        self.actionExit.triggered.connect(partial(self.close_application, object=RadioTelescopeControl))

        # Change between widgets
        self.stellNextPageBtn.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(1))
        self.stellPrevPageBtn.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(0))

        self.retranslateUi(RadioTelescopeControl)
        self.tabWidget.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(RadioTelescopeControl)

    def retranslateUi(self, RadioTelescopeControl):
        _translate = QtCore.QCoreApplication.translate
        RadioTelescopeControl.setWindowTitle(_translate("RadioTelescopeControl", "Radio Telescope Control"))
        self.groupBox.setTitle(_translate("RadioTelescopeControl", "Radio Telescope"))
        self.rpiConnText.setText(_translate("RadioTelescopeControl",
                                            "<html><head/><body><p><span style=\" font-weight:600;\">Status:</span></p></body></html>"))
        self.rpiConStatTextInd.setText(_translate("RadioTelescopeControl",
                                                  "<html><head/><body><p><span style=\" color:#ff0000;\">Disconnected</span></p></body></html>"))
        self.label_4.setText(_translate("RadioTelescopeControl",
                                        "<html><head/><body><p><span style=\" font-weight:600; text-decoration: underline;\">Dish Position</span></p></body></html>"))
        self.label_5.setText(_translate("RadioTelescopeControl",
                                        "<html><head/><body><p><span style=\" font-weight:600;\">RA:</span></p></body></html>"))
        self.raPosInd.setText(_translate("RadioTelescopeControl",
                                         "<html><head/><body><p><span style=\" color:#ff0000;\">0h 0m 0s</span></p></body></html>"))
        self.label_6.setText(_translate("RadioTelescopeControl",
                                        "<html><head/><body><p><span style=\" font-weight:600;\">DEC:</span></p></body></html>"))
        self.decPosInd.setText(_translate("RadioTelescopeControl",
                                          "<html><head/><body><p><span style=\" color:#ff0000;\">0</span><span style=\" color:#ff0000; vertical-align:super;\">o</span><span style=\" color:#ff0000;\"> 0\' 0\'\'</span></p></body></html>"))
        self.tcpConRTLabel.setText(_translate("RadioTelescopeControl", "TCP Connection"))
        self.connectRadioTBtn.setText(_translate("RadioTelescopeControl", "Connect"))
        self.groupBox_2.setTitle(_translate("RadioTelescopeControl", "Stellarium"))
        self.stellarConStatText.setText(_translate("RadioTelescopeControl",
                                                   "<html><head/><body><p><span style=\" font-weight:600;\">Status:</span></p></body></html>"))
        self.stellConStatText.setText(_translate("RadioTelescopeControl",
                                                 "<html><head/><body><p><span style=\" color:#ff0000;\">Disconnected</span></p></body></html>"))
        self.label_2.setText(_translate("RadioTelescopeControl", "Slew Command"))
        self.stellariumOperationSelect.setItemText(0, _translate("RadioTelescopeControl", "Transit"))
        self.stellariumOperationSelect.setItemText(1, _translate("RadioTelescopeControl", "Aim and track"))
        self.tcpStelServLabel.setText(_translate("RadioTelescopeControl", "TCP Server"))
        self.connectStellariumBtn.setText(_translate("RadioTelescopeControl", "Enable"))
        self.nextPageLabel.setText(_translate("RadioTelescopeControl", "Next Page"))
        self.stellNextPageBtn.setText(_translate("RadioTelescopeControl", "..."))
        self.label_13.setText(_translate("RadioTelescopeControl",
                                         "<html><head/><body><p><span style=\" font-weight:600; text-decoration: underline;\">Selected Object</span></p></body></html>"))
        self.label_15.setText(_translate("RadioTelescopeControl",
                                         "<html><head/><body><p><span style=\" font-weight:600;\">RA:</span></p></body></html>"))
        self.raPosInd_2.setText(_translate("RadioTelescopeControl", "0h 0m 0s"))
        self.label_16.setText(_translate("RadioTelescopeControl",
                                         "<html><head/><body><p><span style=\" font-weight:600;\">DEC:</span></p></body></html>"))
        self.decPosInd_2.setText(_translate("RadioTelescopeControl",
                                            "<html><head/><body><p>0<span style=\" vertical-align:super;\">o</span> 0\' 0\'\'</p></body></html>"))
        self.previousPageLabel.setText(_translate("RadioTelescopeControl", "Previous Page"))
        self.stellPrevPageBtn.setText(_translate("RadioTelescopeControl", "..."))
        self.groupBox_3.setTitle(_translate("RadioTelescopeControl", "Location"))
        self.label_12.setText(_translate("RadioTelescopeControl",
                                         "<html><head/><body><p><span style=\" font-weight:600;\">Lat:</span></p></body></html>"))
        self.latTextInd.setText(_translate("RadioTelescopeControl",
                                           "<html><head/><body><p align=\"center\">0<span style=\" vertical-align:super;\">o</span> 0\' 0.00\'\'</p></body></html>"))
        self.label_10.setText(_translate("RadioTelescopeControl",
                                         "<html><head/><body><p><span style=\" font-weight:600;\">Lon:</span></p></body></html>"))
        self.lonTextInd.setText(_translate("RadioTelescopeControl",
                                           "<html><head/><body><p align=\"center\">0<span style=\" vertical-align:super;\">o</span> 0\' 0.00\'\'</p></body></html>"))
        self.label_14.setText(_translate("RadioTelescopeControl",
                                         "<html><head/><body><p><span style=\" font-weight:600;\">Alt:</span></p></body></html>"))
        self.altTextInd.setText(
            _translate("RadioTelescopeControl", "<html><head/><body><p align=\"center\">0m</p></body></html>"))
        self.locatChangeBtn.setText(_translate("RadioTelescopeControl", "Change"))
        self.groupBox_4.setTitle(_translate("RadioTelescopeControl", "State"))
        self.label_8.setText(_translate("RadioTelescopeControl",
                                        "<html><head/><body><p><span style=\" font-weight:600;\">Tracking:</span></p></body></html>"))
        self.stopMovingBtn.setText(_translate("RadioTelescopeControl", "Stop"))
        self.label_11.setText(_translate("RadioTelescopeControl",
                                         "<html><head/><body><p><span style=\" font-weight:600;\">Moving:</span></p></body></html>"))
        self.movTextInd.setText(_translate("RadioTelescopeControl",
                                           "<html><head/><body><p><span style=\" color:#ff0000;\">No</span></p></body></html>"))
        self.trackTextInd.setText(_translate("RadioTelescopeControl",
                                             "<html><head/><body><p><span style=\" color:#ff0000;\">No</span></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("RadioTelescopeControl", "Connection"))
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.tab),
                                     _translate("RadioTelescopeControl", "Connection control"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("RadioTelescopeControl", "Receiver"))
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.tab_2),
                                     _translate("RadioTelescopeControl", "Receiver control"))
        self.menuThis_is_a_menu.setTitle(_translate("RadioTelescopeControl", "File"))
        self.menuTools.setTitle(_translate("RadioTelescopeControl", "Tools"))
        self.menuAbout.setTitle(_translate("RadioTelescopeControl", "About"))
        self.menuTCP.setTitle(_translate("RadioTelescopeControl", "TCP"))
        self.actionOpen.setText(_translate("RadioTelescopeControl", "Open"))
        self.actionOpen.setStatusTip(_translate("RadioTelescopeControl", "Open a settings file"))
        self.actionOpen.setShortcut(_translate("RadioTelescopeControl", "Ctrl+O"))
        self.actionSettings.setText(_translate("RadioTelescopeControl", "Settings"))
        self.actionSettings.setStatusTip(_translate("RadioTelescopeControl", "Change the TCP settings"))
        self.actionSettings.setShortcut(_translate("RadioTelescopeControl", "Ctrl+T"))
        self.actionLicense.setText(_translate("RadioTelescopeControl", "License"))
        self.actionLicense.setStatusTip(_translate("RadioTelescopeControl", "View the application licensing"))
        self.actionAbout.setText(_translate("RadioTelescopeControl", "About..."))
        self.actionAbout.setStatusTip(_translate("RadioTelescopeControl", "View application description"))
        self.actionExit.setText(_translate("RadioTelescopeControl", "Exit"))
        self.actionExit.setStatusTip(_translate("RadioTelescopeControl", "Exit the program"))
        self.actionExit.setShortcut(_translate("RadioTelescopeControl", "Ctrl+E"))
        self.actionSave.setText(_translate("RadioTelescopeControl", "Save Settings"))
        self.actionSave.setStatusTip(_translate("RadioTelescopeControl", "Save the current program settings"))
        self.actionSave.setShortcut(_translate("RadioTelescopeControl", "Ctrl+S"))
        self.actionCalibration.setText(_translate("RadioTelescopeControl", "Calibration"))
        self.actionCalibration.setStatusTip(
            _translate("RadioTelescopeControl", "Calibrate the radio telescope\'s dish positioning"))
        self.actionLocation.setText(_translate("RadioTelescopeControl", "Location"))
        self.actionLocation.setStatusTip(
            _translate("RadioTelescopeControl", "Change the location and location settings"))
        self.actionLocation.setShortcut(_translate("RadioTelescopeControl", "Ctrl+L"))
        self.actionManual_Control.setText(_translate("RadioTelescopeControl", "Manual Control"))
        self.actionManual_Control.setStatusTip(
            _translate("RadioTelescopeControl", "Manually control the dish\'s position"))
        self.actionManual_Control.setShortcut(_translate("RadioTelescopeControl", "Ctrl+M"))

    # Function called every time the corresponding checkbox is selected
    def checkBoxTCPRT(self, state):
        if state == QtCore.Qt.Checked:
            self.tcpConRTLabel.setEnabled(True)  # Enable the label
            self.connectRadioTBtn.setEnabled(True)  # And also enable the button selection
        else:
            self.tcpConRTLabel.setEnabled(False)  # Disable the label
            self.connectRadioTBtn.setEnabled(False)  # And also disable the button selection

    # Function called every time the corresponding checkbox is selected
    def checkBoxTCPStel(self, state):
        if state == QtCore.Qt.Checked:
            self.tcpStelServLabel.setEnabled(True)
            self.connectStellariumBtn.setEnabled(True)
        else:
            self.tcpStelServLabel.setEnabled(False)
            self.connectStellariumBtn.setEnabled(False)

    @QtCore.pyqtSlot(str)
    def stellTCPGUIHandle(self, data:str):
        if data == "Waiting":
            self.connectStellariumBtn.setText("Stop")  # Change user's selection
            self.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
            self.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                             "color:#ffb400;\">Waiting...</span></p></body></html>")
            self.nextPageLabel.setEnabled(False)  # Disable the next page label
            self.stellNextPageBtn.setEnabled(False)  # Disable the button to avoid changing to next page
        elif data == "Connected":
            self.connectStellariumBtn.setText("Disable")  # Change user's selection
            self.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
            self.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                             "color:#00ff00;\">Connected</span></p></body></html>")
            self.nextPageLabel.setEnabled(True)  # Enable the label to indicate functionality
            self.stellNextPageBtn.setEnabled(True)  # Enable next page transition, since we have a connection
            self.stackedWidget.setCurrentIndex(1)
        elif data == "Disconnected":
            self.connectStellariumBtn.setText("Enable")
            self.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
            self.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                             "color:#ff0000;\">Disconnected</span></p></body></html>")
            self.nextPageLabel.setEnabled(False)  # Disable the next page label
            self.stellNextPageBtn.setEnabled(False)  # Disable the button to avoid changing to next page
            self.stackedWidget.setCurrentIndex(0)

    @QtCore.pyqtSlot(float, float, name='dataStellShow')
    def stellDataShow(self, ra: float, dec: float):
        self.raPosInd_2.setText("%.5fh" % ra)  # Update the corresponding field
        self.decPosInd_2.setText("%.5f" % dec + u"\u00b0")  # Update the corresponding field

    @QtCore.pyqtSlot(str, name='conClientStat')
    def clientTCPGUIHandle(self, data: str):
        if data == "Connecting":
            self.connectRadioTBtn.setText("Stop")  # Change user's selection
            self.tcpConRTChkBox.setCheckState(QtCore.Qt.Unchecked)
            self.rpiConStatTextInd.setText("<html><head/><body><p><span style=\" "
                                             "color:#ffb400;\">Connecting...</span></p></body></html>")
        elif data == "Connected":
            self.connectRadioTBtn.setText("Disconnect")
            self.tcpConRTChkBox.setCheckState(QtCore.Qt.Unchecked)
            self.rpiConStatTextInd.setText("<html><head/><body><p><span style=\" "
                                                  "color:#00ff00;\">Connected</span></p></body></html>")
        elif data == "Disconnected":
            self.connectRadioTBtn.setText("Connect")  # Change user's selection
            self.rpiConStatTextInd.setText("<html><head/><body><p><span style=\" "
                                                  "color:#ff0000;\">Disconnected</span></p></body></html>")

    def show_application(self):
        self.mainWin.show()

    def close_application(self, object):
        choice = QtWidgets.QMessageBox.question(object, 'Exit', "Are you sure?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            QtCore.QCoreApplication.instance().quit()  # If user selects "Yes", then exit from the application
        else:
            pass  # If user selects "No" then do not exit
