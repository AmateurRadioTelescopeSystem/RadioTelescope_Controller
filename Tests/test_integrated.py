import os
import sys
import yaml
import socket
import unittest
import logging
import logging.config
sys.path.append(os.path.abspath('.'))  # noqa
sys.path.append(os.path.abspath('../Core/'))  # noqa

import Tests.DefaultData
from PyQt5 import QtWidgets, QtCore, QtTest, QtNetwork
from Core.GUI import UInterface
from Core.Handlers import OperationHandler
from Core.Client import ClientThread
from Core.Server import RPiServerThread
from Core.Stellarium import StellariumThread
from Core.Configuration import ConfigData

# Create a virtual display for testing
from pyvirtualdisplay import Display
display = Display(visible=False, size=(1024, 768), color_depth=24)
display.start()


class TestIntegrated(unittest.TestCase):
    def setUp(self) -> None:
        server_address = ('127.0.0.1', 10001)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(server_address)
        self.sock.settimeout(10)  # Add a timeout timer for 10 seconds
        self.sock.listen(1)  # Set the socket to listen

    def tearDown(self) -> None:
        self.sock.close()

    def test_integration(self):
        # Create the directory for the log files if it does not exist already
        try:
            if not os.path.exists(os.path.abspath('Tests/logs')):
                os.makedirs(os.path.abspath('Tests/logs'))
            if not os.path.exists(os.path.abspath('Tests/Settings')):
                os.makedirs(os.path.abspath('Tests/Settings'))
            if not os.path.exists(os.path.abspath('TLE')):
                os.makedirs(os.path.abspath('TLE'))  # Make the TLE saving directory
            if not os.path.exists('Tests/Astronomy Database'):
                os.makedirs('Tests/Astronomy Database')
        except Exception as excep:
            print("There is a problem with the log directory. See tracback: \n%s" % excep, file=sys.stderr)
            sys.exit(-1)  # Exit the program if an error occurred

        # Check if the logging configuration file exists
        try:
            if not os.path.exists(os.path.abspath('Tests/Settings/logging_settings.yaml')):
                print("Logging configuration file not found. Creating the default.", file=sys.stderr)
                log_file = open(os.path.abspath('Tests/Settings/logging_settings.yaml'),
                                "w+")  # Open file in writing mode
                log_file.write(Tests.DefaultData.log_config_str)  # Write the default dat to the file
                log_file.close()  # Close the file, since no other operation required
        except Exception as excep:
            print("There is a problem creating the configuration file. See tracback: \n%s" % excep, file=sys.stderr)
            sys.exit(-1)  # Exit the program if an error occurred

        # Check if the settings XML file exists
        try:
            if not os.path.exists(os.path.abspath('Tests/Settings/settings.xml')):
                print("Settings file not found. Creating the default.", file=sys.stderr)
                setngs_file = open(os.path.abspath('Tests/Settings/settings.xml'),
                                   "w+")  # Open the settings file in writing mode
                setngs_file.write(Tests.DefaultData.settings_xml_str)  # Write the default dat to the file
                setngs_file.close()  # Close the file, since no other operation required
        except Exception as excep:
            print("There is a problem creating the settings file. See tracback: \n%s" % excep, file=sys.stderr)
            sys.exit(-1)  # Exit the program if an error occurred

        # Open the configuration and apply it on the logging module
        with open(os.path.abspath('Tests/Settings/logging_settings.yaml')) as config_file:
            dictionary = yaml.safe_load(config_file)  # Load the dictionary configuration
            logging.config.dictConfig(dictionary['Logging'])  # Select the logging settings from the dictionary

        log_data = logging.getLogger(__name__)  # Create the logger for the program
        log_data.info("Main thread started")  # Use that in debugging
        QtCore.QThreadPool.globalInstance().setMaxThreadCount(8)  # Set the global thread pool count

        app = QtWidgets.QApplication(sys.argv)  # Create a Qt application instance
        ui = UInterface.UIRadioTelescopeControl()  # Instantiate the class object for the main window GUI

        # Exception handling code for the XML file process
        try:
            cfg_data = ConfigData.ConfData(os.path.abspath('Tests/Settings/settings.xml'))
        except:
            log_data.exception("There is a problem with the XML file handling. Program terminates.")
            sys.exit(1)  # Terminate the script

        # TCP Stellarium server initialization
        tcp_stell_thread = QtCore.QThread()  # Create a thread for the Stellarium server
        tcp_stell = StellariumThread.StellThread(cfg_data)  # Create the instance of the TCP client
        tcp_stell.moveToThread(tcp_stell_thread)  # Move the Stellarium server to a thread
        tcp_stell.conStatSigS.connect(ui.stell_tcp_gui_handle)  # Button handling signal for Stellarium
        tcp_stell.dataShowSigS.connect(ui.stell_data_show)  # Stellarium coordinate show signal
        # Connect the thread action signals
        tcp_stell_thread.started.connect(tcp_stell.start)  # Run the start code for the thread, once it starts
        tcp_stell_thread.finished.connect(tcp_stell.close)  # Run the stop code when a quit is requested

        # RPi communications
        # TCP server for the RPi initialization
        tcp_server_thread = QtCore.QThread()  # Create a thread for the TCP client
        tcp_server = RPiServerThread.RPiServerThread(cfg_data)  # Create the instance of the TCP client
        tcp_server.moveToThread(tcp_server_thread)  # Move the server to a thread
        tcp_server.conStatSigR.connect(ui.rpi_tcp_gui_handle)  # Connection status signal for the server
        # Connect the thread action signals
        tcp_server_thread.started.connect(tcp_server.start)  # What to do upon thread start
        tcp_server_thread.finished.connect(tcp_server.close)  # What to do upon thread exit

        # Initialize the TCP client thread
        tcp_client_thread = QtCore.QThread()  # Create a thread for the TCP client
        tcp_client = ClientThread.ClientThread(cfg_data)  # Create the instance of the TCP client
        tcp_client.moveToThread(tcp_client_thread)  # Move the client to a thread
        tcp_client.conStatSigC.connect(ui.client_tcp_gui_handle)  # Connection status of the TCP client
        # Connect the thread action signals
        tcp_client_thread.started.connect(tcp_client.start)  # Connect with this function upon thread start
        tcp_client_thread.finished.connect(tcp_client.close)  # Connect with thsi function upon thread exit

        # Initialize the operation handler
        oper_handler_thread = QtCore.QThread()  # Create a thread for the operation handler
        oper_handle = OperationHandler.OpHandler(tcp_client, tcp_server, tcp_stell, tcp_client_thread,
                                                 tcp_server_thread, tcp_stell_thread, ui, cfg_data)
        oper_handle.moveToThread(oper_handler_thread)  # Move the operation handler to a thread
        oper_handler_thread.started.connect(oper_handle.start)  # Run the start method upon thread start
        oper_handler_thread.finished.connect(oper_handle.app_exit_request)  # If the handler exits, then the app cloes
        oper_handler_thread.finished.connect(oper_handle.deleteLater)  # Wait until the run returns from the thread
        oper_handler_thread.finished.connect(oper_handler_thread.deleteLater)  # Finally delete the thread before exit
        oper_handler_thread.start()  # Start the operations handler

        s_latlon = cfg_data.get_lat_lon()  # First element is latitude and second element is longitude
        s_alt = cfg_data.get_altitude()  # Get the altitude from the settings file

        # Show location on the GUI
        ui.main_widget.lonTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                                          "vertical-align:super;\">o</span></p></body></html>" % s_latlon[1])
        ui.main_widget.latTextInd.setText("<html><head/><body><p align=\"center\">%s<span style=\" "
                                          "vertical-align:super;\">o</span></p></body></html>" % s_latlon[0])
        ui.main_widget.altTextInd.setText("<html><head/><body><p align=\"center\">%sm</p></body></html>" % s_alt)

        # We quit from the operation handle thread and then we exit. All handling is done there
        app.aboutToQuit.connect(oper_handler_thread.quit)

        ui.show_application()  # Render and show the GUI main window and start the application

        window_show = QtTest.QTest.qWaitForWindowExposed(ui.main_win)  # Wait until the main window is shown

        QtTest.QTest.qWait(2000)  # Wait for the retrieval of TLE file

        try:
            # Click the GUI button to proceed
            QtTest.QTest.mouseClick(ui.tle_info_msg_box.buttons()[0], QtCore.Qt.LeftButton)
        except IndexError:
            print("Possibly the file exists. \nDouble check to make sure that there is no other error.")
            pass
        QtTest.QTest.qWait(1000)  # Wait for the client thread to start

        # Get the connection status
        client_connected = (tcp_client.sock.state() == QtNetwork.QAbstractSocket.ConnectedState)

        # Close all the threads before exiting
        tcp_client_thread.quit()
        tcp_client_thread.wait()
        tcp_server_thread.quit()
        tcp_server_thread.wait()
        tcp_stell_thread.quit()
        tcp_stell_thread.wait()
        oper_handler_thread.quit()
        oper_handler_thread.wait()

        self.assertTrue(window_show, "Window was not able to start.")
        self.assertTrue(client_connected, "Client did not manage to connect to the server.")


if __name__ == "__main__":
    unittest.main()
