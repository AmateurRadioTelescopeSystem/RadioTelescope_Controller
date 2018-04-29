import UInterface as UI
import configData
import logData
import sys

if __name__ == '__main__':
    # Exception handling section for the log file code
    try:
        logdata = logData.logData(__name__)
    except:
        print(
            "There is a problem with the handling of the log file. See log file for the traceback of the exception.\n")
        exit(1)  # Terminate the script

    # Exception handling code for the XML file process
    try:
        cfgData = configData.confData("settings.xml")
    except:
        print("There is a problem with the XML file handling. See log file for the traceback of the exception.\n")
        logdata.log("EXCEPT", "There is a problem with the XML file handling. Program terminates.", __name__)
        exit(1)  # Terminate the script

    app = UI.QtWidgets.QApplication(sys.argv)  # Create a Qt application instance
    RadioTelescopeControl = UI.QtWidgets.QMainWindow()  # Create the main window of th GUI
    TCPSettings = UI.QtWidgets.QMainWindow()  # Create window for the TCP settings dialog

    # Create the contents of the windows
    ui = UI.Ui_RadioTelescopeControl()
    ui.setupUi(RadioTelescopeControl)
    uiT = UI.Ui_TCPSettings()
    uiT.setupUi(TCPSettings)

    ui.actionSettings.triggered.connect(TCPSettings.show)

    RadioTelescopeControl.show()
    sys.exit(app.exec_())
