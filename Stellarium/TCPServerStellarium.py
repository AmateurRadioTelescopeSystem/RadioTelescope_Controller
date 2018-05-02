import logData
import socket


class TCPStellarium(object):
    def __init__(self, cfgData):
        self.logd = logData.logData(__name__)
        self.sock_exst = False  # Indicate that a socket does not object exist
        self.sock_connected = False  # Indicate that there is currently no connection
        self.client_connected = False  # Indicate whether a client is connected or not

        self.btnStr = "Enable"  # String to hold the TCP connection button message
        self.cfgD = cfgData  # Hold the config data object

    def createSocket(self):
        host = self.cfgD.getStellHost()  # Get the TCP connection host
        port = self.cfgD.getStellPort()  # Get the TCP connection port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket
        sock.bind((host, int(port)))  # Bind to the socket
        sock.listen(1)  # Set the listening to one connection
        self.sock_exst = True  # Indicate socket creation

        return sock  # Return the socket object

    def acceptConnection(self):
        if not self.sock_exst:
            self.sock = self.createSocket()
        try:
            self.client, claddr = self.sock.accept()
            self.client_connected = True
            return claddr, self.client_connected
        except:
            self.logd.log("EXCEPT", "An exception occurred while waiting for a client to connect", "acceptConnection")
            self.sock.close()
            self.sock_exst = False
            return "", False

    def receive(self):
        if self.client_connected:
            try:
                return self.client.recv(1024)
            except ConnectionResetError:
                self.logd.log("EXCEPT", "A connected client abruptly disconnected.", "receive")
                self.client_connected = False
                return ""
        else:
            return ""

    def releaseClient(self):
        if self.client_connected and self.sock_exst:
            self.client.close()  # Detach the client
            self.sock.close()  # Close the connection socket
            self.client_connected = False
            self.sock_exst = False
        elif self.sock_exst:
            self.sock.close()  # Close the connection socket
            self.sock_exst = False
            self.client_connected = False
        else:
            self.client_connected = False
        return self.client_connected

    def sendResponse(self, response):
        if self.client_connected and self.sock_exst:
            try:
                self.client.send(response)
                return response
            except:
                self.logd.log("EXCEPT", "There was an issue sending the response to the client", "sendResponse")

    def connectButton(self, thread = None):
        if thread is not None:
            if thread.isRunning():
                thread.quit()  # Quit the currently running thread
                self.logd.log("INFO", "The thread for the server was closed", "connectButton")
            else:
                self.logd.log("INFO", "Started a thread for the server", "connectButton")
                thread.start()  # Initiate the server to its thread
