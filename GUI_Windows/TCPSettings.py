# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TCPSettings.ui'
#
# Created by: PyQt5 UI code generator 5.10.1

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TCPSettings(object):
    def __init__(self):
        self.tcpWindow = QtWidgets.QMainWindow()
        self.setupUi(self.tcpWindow)

    def setupUi(self, TCPSettings):
        TCPSettings.setWindowIcon(QtGui.QIcon('Icons/Net.png'))
        TCPSettings.setObjectName("TCPSettings")
        TCPSettings.setWindowModality(QtCore.Qt.ApplicationModal)
        TCPSettings.resize(282, 348)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        TCPSettings.setFont(font)
        self.centralwidget = QtWidgets.QWidget(TCPSettings)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        TCPSettings.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(TCPSettings)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 282, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        TCPSettings.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(TCPSettings)
        self.statusbar.setObjectName("statusbar")
        TCPSettings.setStatusBar(self.statusbar)
        
        extractAction = QtWidgets.QAction(QtGui.QIcon('Icons/TCP.png'), 'Python', TCPSettings)

        self.toolBar = QtWidgets.QToolBar(TCPSettings)
        self.toolBar.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolBar.sizePolicy().hasHeightForWidth())
        self.toolBar.setSizePolicy(sizePolicy)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.toolBar.setObjectName("toolBar")
        TCPSettings.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionSave = QtWidgets.QAction(TCPSettings)
        self.actionSave.setObjectName("actionSave")
        self.menuFile.addAction(self.actionSave)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(TCPSettings)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(TCPSettings)

    def retranslateUi(self, TCPSettings):
        _translate = QtCore.QCoreApplication.translate
        TCPSettings.setWindowTitle(_translate("TCPSettings", "TCP Settings"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("TCPSettings", "Telescope Client"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("TCPSettings", "Stellarium server"))
        self.menuFile.setTitle(_translate("TCPSettings", "File"))
        self.toolBar.setWindowTitle(_translate("TCPSettings", "toolBar"))
        self.actionSave.setText(_translate("TCPSettings", "Save"))
        self.actionSave.setShortcut(_translate("TCPSettings", "Ctrl+S"))

    def windShow(self):
        self.tcpWindow.show()
