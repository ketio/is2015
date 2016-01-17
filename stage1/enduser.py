import socket
import sys
import threading
import time
from Crypto.PublicKey import RSA

AUTH_CODE = "NTUIM"
FACTORY_PUBLIC_KEY = "factory_public_key.pem"
ENDUSER_PRIVATE_KEY = "enduser_private_key.pem"

def upload_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('127.0.0.1', 20000)
    print >> sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)

    sock.listen(1)

    while True:

        # Wait for a connection
        print >>sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()
        try:
            print >>sys.stderr, 'connection from', client_address

            # Receive the data in small chunks and retransmit it 
            data = connection.recv(1000)
            print("%s" % data)
            break
                
        finally:
            # Clean up the connection
            connection.close()

upload_listener_thread = threading.Thread(target = upload_listener, args = ())
upload_listener_thread.daemon = True

upload_listener_thread.start()

while(True):
    x = raw_input("What do you want to do")

    if x == "D":
        f = open(FACTORY_PUBLIC_KEY,'r')
        server_public_key = RSA.importKey(f.read())
        encrypted_code = server_public_key.encrypt(AUTH_CODE,24)

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = ('localhost', 10000)
        print >>sys.stderr, 'connecting to %s port %s' % server_address
        sock.connect(server_address)

        try:
            
            # Send data
            message = encrypted_code[0]
            sock.sendall(message)

            # Look for the response
            amount_received = 0
            amount_expected = len(message) * 10

            data = sock.recv(1000)
            amount_received += len(data)

            f = open(ENDUSER_PRIVATE_KEY,'r')
            client_private_key = RSA.importKey(f.read())
            price = client_private_key.decrypt(data)
            print(price)
        finally:
            print >>sys.stderr, 'closing socket'
            sock.close()
