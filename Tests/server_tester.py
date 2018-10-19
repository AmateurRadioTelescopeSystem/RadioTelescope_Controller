import socket
import sys
import time


serverAddress = ('127.0.0.1', 10001)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.bind(serverAddress)
except Exception as e:
    print("****Server Tester****")
    print("Can not bind to port. %s" % e, file=sys.stderr)
    print("*********************\n")

sock.settimeout(10)  # Add a timeout timer for 10 seconds
sock.listen(1)  # Set the socket to listen
print("****Server Tester****")
print("Waiting for connection...")
print("*********************\n")

connected = False

try:
    while True:
        connection, clientAddress = sock.accept()
        if connection is not None:
            connected = True
            print("****Server Tester****")
            print("Successfully connected with %s:%s" % (clientAddress[0], clientAddress[1]))
            print("*********************\n")
            break
except Exception as e:
    print("****Server Tester****")
    print("Failed to establish a connection. %s" % e)
    print("*********************\n")
cldisc = False

while True:
    if not connected:
        try:
            print("****Server Tester****")
            print("Waiting for connection...")
            print("*********************\n")
            while True:
                connection, clientAddress = sock.accept()
                if connection is not None:
                    connected = True
                    cldisc = False
                    print("****Server Tester****")
                    print("Successfully connected with %s:%s" % (clientAddress[0], clientAddress[1]))
                    print("*********************\n")
                    break
        except Exception as e:
            print("****Server Tester****")
            print("Failed to establish a connection. %s" % e)
            print("*********************\n")
            break
    else:
        rec = ""
        rec = connection.recv(1024)
        rec = rec.decode('utf-8')

        if len(rec) > 0:
            print("****Server Tester****")
            print(rec)
            print("*********************\n")
            time.sleep(10)  # Wait a bit before closing
            connection.close()
            break
