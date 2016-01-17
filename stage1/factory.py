import socket
import sys
import threading
import time
from Crypto.PublicKey import RSA

AUTH_CODE = "NTUIM"
FACTORY_PRIVATE_KEY = "factory_private_key.pem"
ENDUSER_PUBLIC_KEY = "enduser_public_key.pem"

def send_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('127.0.0.1', 10000)
    print >> sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)

    sock.listen(5)

    while True:

        # Wait for a connection
        print >>sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()
        try:
            print >>sys.stderr, 'connection from', client_address

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(1000)
                print >>sys.stderr, 'received "%s"' % data
                if data:
                    print("Get Authentication Code")

                    f = open(FACTORY_PRIVATE_KEY,'r')
                    server_private_key = RSA.importKey(f.read())
                    decrypted_code = server_private_key.decrypt(data)
                    
                    if decrypted_code == AUTH_CODE:

                        f2 = open(ENDUSER_PUBLIC_KEY,'r')
                        f3 = open('price.txt','r')
                        client_public_key = RSA.importKey(f2.read())
                        encrypted_code = client_public_key.encrypt(f3.read(),24)
                        message = encrypted_code[0]
                        connection.sendall(message)
                    else:
                        connection.sendall("Code Error!")
                else:
                    print >>sys.stderr, 'no more data from', client_address
                    break
                
        finally:
            # Clean up the connection
            connection.close()
def uploader():
    while(True):
        x = raw_input("What do you want to do?")
        print(x)
        if(x == "U"):
            while(True):
                try:
                    new_price = raw_input("Please Input New Price:")
                    new_price = int(new_price)
                    break
                except ValueError:
                    continue
            price_file = open("price.txt", "w").write("%d" % new_price)

            # Create a TCP/IP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect the socket to the port where the server is listening
            server_address = ('localhost', 20000)
            print >>sys.stderr, 'connecting to %s port %s' % server_address
            sock.connect(server_address)

            try:
                
                # Send data
                message = 'New Price Upload!'
                sock.sendall(message)

                # Look for the response
                amount_received = 0
                amount_expected = len(message) * 10

                # while amount_received < amount_expected:
                #   data = sock.recv(100)
                #   amount_received += len(data)
                    # print >>sys.stderr, 'received "%s"' % data

            finally:
                print >>sys.stderr, 'closing socket'
                sock.close()



send_server_thread = threading.Thread(target = send_server, args = ())
send_server_thread.daemon = True
uploader_thread = threading.Thread(target = uploader, args = ())
uploader_thread.daemon = True

send_server_thread.start()
uploader_thread.start()

while(True):
    time.sleep(1)
