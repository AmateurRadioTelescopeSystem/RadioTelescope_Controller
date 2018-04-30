import UInterface as UI
import configData
import logData
import TCPClient
import sys

if __name__ == '__main__':
    app = UI.QtWidgets.QApplication(sys.argv)  # Create a Qt application instance
    RadioTelescopeControl = UI.QtWidgets.QMainWindow()  # Create the main window of th GUI

    # Create the contents of the windows
    ui = UI.Ui_RadioTelescopeControl()
    ui.setupUi(RadioTelescopeControl)

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

    # Exception handling code for the TCP initial setup
    try:
        tcpClient = TCPClient.TCPClient(cfgData, ui)
    except:
        print("There is a problem with the TCP handling. See log file for the traceback of the exception.\n")
        logdata.log("EXCEPT", "There is a problem with the TCP handling. Program terminates.", __name__)
        exit(1)  # Terminate the script

    s_latlon = cfgData.getLatLon()  # First element is latitude and second element is longitude
    s_alt = cfgData.getAltitude()  # Get the altitude from the settings file
    hostport = [cfgData.getHost(), cfgData.getPort()]  # Get the saved host address or name and port of the server


    # Give functionality to the buttons and add the necessary texts to fields
    ui.connectRadioTBtn.clicked.connect(tcpClient.connectButton)
    tcpClient.sendRequest("There")
    ui.lonTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                          "vertical-align:super;\">o</span></p></body></html>" %s_latlon[1])
    ui.latTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                          "vertical-align:super;\">o</span></p></body></html>" %s_latlon[0])
    ui.altTextInd.setText("<html><head/><body><p align=\"center\">%sm</p></body></html>" %s_alt)

    RadioTelescopeControl.show()
    sys.exit(app.exec_())
