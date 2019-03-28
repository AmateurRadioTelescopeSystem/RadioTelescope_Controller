import os
import sys
import time
import socket
import logging
import logging.config

import pytest
from PyQt5 import QtWidgets, QtCore, QtTest, QtNetwork
from Core.GUI import UInterface
from Core.Handlers import OperationHandler
from Core.Networking import ClientThread, RPiServerThread, StellariumThread
from Core.Configuration import ConfigData

# Create a virtual display for testing
from pyvirtualdisplay import Display
display = Display(visible=False, size=(1024, 768), color_depth=24)
display.start()


@pytest.fixture(scope="module")
def server():
    server_address = ('127.0.0.1', 10001)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.settimeout(60)  # Add a timeout timer for 60 seconds
    sock.listen(1)  # Set the socket to listen
    yield sock

    sock.close()


def test_integration(server):
    rpi_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

    # Test the triggered signals
    ui.show_application()  # Render and show the GUI main window and start the application

    window_shown = QtTest.QTest.qWaitForWindowExposed(ui.main_win)  # Wait until the main window is shown
    QtTest.QTest.qWait(2000)  # Wait for the retrieval of TLE file

    try:
        # Click the GUI button to proceed
        QtTest.QTest.mouseClick(ui.tle_info_msg_box.buttons()[0], QtCore.Qt.LeftButton)
    except IndexError:
        print("\nPossibly the TLE file exists. \nDouble check to make sure that there is no other error.\n")
        pass
    QtTest.QTest.qWait(1000)  # Wait for the client thread to start

    rpi_socket.connect(('localhost', 10003))
    QtTest.QTest.qWait(500)

    # Get the connection status
    client_connected = (tcp_client.sock.state() == QtNetwork.QAbstractSocket.ConnectedState)
    rpi_connected = (tcp_server.socket.state() == QtNetwork.QAbstractSocket.ConnectedState)

    # Close all the threads before exiting
    tcp_client_thread.quit()
    tcp_client_thread.wait()
    tcp_server_thread.quit()
    tcp_server_thread.wait()
    tcp_stell_thread.quit()
    tcp_stell_thread.wait()
    oper_handler_thread.quit()
    oper_handler_thread.wait()

    assert window_shown
    assert client_connected
    assert rpi_connected
