import socket
import sys
import threading
import time
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
import cipher
import msg

f = open("enduser_public_key.pem",'r')
enduser_public_key_text = f.read()
enduser_public_key = RSA.importKey(enduser_public_key_text)
f.close()
f = open("factory_public_key.pem",'r')
factory_public_key_text = f.read()
factory_public_key = RSA.importKey(factory_public_key_text)
f.close()
f = open("kdc_private_key.pem",'r')
kdc_private_key_text = f.read()
kdc_private_key = RSA.importKey(kdc_private_key_text)
f.close()


ip_list = dict()
ip_list["enduser"] = ["localhost","20000",enduser_public_key_text]
ip_list["factory"] = ["localhost","10000",factory_public_key_text] 


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 33333)
print >> sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

sock.listen(5)

while True:

    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()
    try:
        print sys.stderr, 'connection from', client_address

        # Receive the data in small chunks and retransmit it
        while True:
            request = connection.recv(4000)
            if request:
                print("Request Receive.")
                request = msg.get_package_of_msg(request)
                target = request.split("|")[0]

                print("Target: %s" % target)                
                if target not in ip_list:
                    print("Target not in List.")
                    connection.sendall("No such target in KDC!")
                    break

                print("Encrypting Public key of %s" % target)
                message = ("%s|%s" %(ip_list[target][2], request))
                signature = cipher.sign(message, kdc_private_key)

                print("Send Public Back with Signature")
                response = msg.generate_msg(message, signature)
                connection.sendall(response)
            else:
                print >>sys.stderr, 'no more data from', client_address
                break
            
    finally:
        # Clean up the connection
        connection.close()
