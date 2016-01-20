import socket
import sys
import os
import threading
import time
import datetime
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
import cipher
import random
import msg

AUTH_CODE = "NTUIM"

f = open("factory_private_key.pem",'r')
factory_private_key_text = f.read()
factory_private_key = RSA.importKey(factory_private_key_text)
f.close()
f = open("kdc_public_key.pem",'r')
kdc_public_key_text = f.read()
kdc_public_key = RSA.importKey(kdc_public_key_text)
f.close()

enduser_public_key_text = ""
enduser_public_key = ""

def get_public_key(ID):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 33333)
    print("connecting to KDC")
    sock.connect(server_address)

    try:
        print("Send Request to KDC.")
        T1 = str(datetime.datetime.now())
        request = msg.generate_msg("%s|%s"%(ID,T1))

        # Send data
        sock.sendall(request)

        print("Receive Response From KDC.")
        response = sock.recv(10000)

        print("Parse Response and Get Public Key")
        key = msg.get_package_of_msg(response)
        signature_of_kdc = msg.get_Trail_of_msg(response)

        print("Verifying Signature")
        if not cipher.verify(key, signature_of_kdc, kdc_public_key):
            print("Verify Failed.")
            return                      

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()

    return key

def init_session():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 20001)
    print("connecting to enduser")
    sock.connect(server_address)

    try:
        ID = "factory"
        N1 = random.randint(0,100)
         
        print("Send ID and N1 to Enduser")
        message_to_enduser = enduser_public_key.encrypt("%s|%d" % (ID,N1),24)[0]
        message_to_enduser = msg.generate_msg(message_to_enduser)
        sock.sendall(message_to_enduser)

        print("Receive N1 and N2 from Enduser")
        data = sock.recv(4096)
        data = msg.get_package_of_msg(data)
        check = factory_private_key.decrypt(data)
        
        check = check.split("|")
        N2 = int(check[1])
        if N2 != (N1 + 1):
            print("Failed")
            # return 
        
        print("Send Finally Check to Enduser")
        message_to_enduser = enduser_public_key.encrypt("%d" % (N2),24)[0]
        message_to_enduser = msg.generate_msg(message_to_enduser)
        sock.sendall(message_to_enduser)

       
    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()

def key_exchange_server():
    global enduser_public_key_text
    global enduser_public_key

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('127.0.0.1', 10001)
    sock.bind(server_address)
    sock.listen(1)
    while True:
        # Wait for a connection
        # print >>sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()
        try:
            print("Receive ID and N1 From Enduser.")
            data = connection.recv(4096)
            data = msg.get_package_of_msg(data)
            message = factory_private_key.decrypt(data)
            message = message.split("|")
            ID = message[0]
            N1 = int(message[1])
            N2 = N1+1

            print("To Get Public Key of Enduser")
            enduser_public_key_text = get_public_key(ID)
            enduser_public_key = RSA.importKey(enduser_public_key_text)

            response = "%d|%d" % (N1, N2)
            encrypted_code = enduser_public_key.encrypt(response,24)
            
            print("Send N1 and N2 to Enduser")
            message = msg.generate_msg(encrypted_code[0])
            connection.sendall(message)

            print("Receive Finally Check")
            data = connection.recv(4096)
            data = msg.get_package_of_msg(data)
            

        finally:
            # Clean up the connection
            connection.close()


def send_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('127.0.0.1', 10000)
    sock.bind(server_address)
    sock.listen(5)
    while True:
        connection, client_address = sock.accept()
        try:
            print 'connection from', client_address

            # Receive the data in small chunks and retransmit it
            while True:

                data = connection.recv(10000)
                if data:
                    print("Get Patch Request From Enduser.")

                    encrypt_auth_code = msg.get_package_of_msg(data)
                    signature_of_enduser = msg.get_Trail_of_msg(data)
                    
                    print("Verifying Signature")
                    if not cipher.verify(encrypt_auth_code, signature_of_enduser, enduser_public_key):
                        print("Verify Failed.")
                        return 

                    print("Decrypt Request.")
                    decrypted_code = factory_private_key.decrypt(encrypt_auth_code)
                    
                    print("Check Authentication Code.")
                    if decrypted_code == AUTH_CODE: 
                        print("Check Success!")

                        print("Encrypt Price Data.")
                        if not os.path.isfile("price.txt"):
                            price_text = "item,price\n"
                        else:
                            f3 = open('price.txt','r')
                            price_text = f3.read()
                        encrypted_code = enduser_public_key.encrypt(price_text,24)
                        signature = cipher.sign(encrypted_code[0], factory_private_key)

                        print("Send Price Data to Enduser with Signature")
                        message = msg.generate_msg(encrypted_code[0],signature)
                        connection.sendall(message)

                    else:
                        print("Check Failed!")
                        connection.sendall("Code Error!")
                else:
                    break
                
        finally:
            # Clean up the connection
            connection.close()

def notifiyEndUser():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 20000)
    try:
        sock.connect(server_address)
    except socket.error:
        print("Enduser connect Failed.")
        return 

    try:
        
        # Send data
        message = '\nNew Price Upload!\n'
        message = msg.generate_msg(message)
        sock.sendall(message)

    finally:
        sock.close()

def show_price_data():
    if not os.path.isfile("price.txt"):
        print("Price Data Does Not Exist.")
        return 
    f = open("price.txt","r")
    data = f.read()
    print(data)

def update_price_data():
    print("Input exit to end.")
    priceDict = dict()
    while(True):
        try:
            item = raw_input("Please Input Item Name:")
            if item == "exit":
                break
            price = raw_input("Please Input Item Price:")
            price = float(price)
            priceDict[item] = price
        
        except ValueError:
            print("price must be number!")
            continue

    # Save price data
    price_file = open("price.txt", "w")
    price_file.write("item,price\n")
    for item, price in priceDict.items():
        price_file.write("%s,%f\n" % (item, price))
    price_file.close()

    print("Upload New Price Success, Will Notifiy EndUser!")
    notifiyEndUser()

send_server_thread = threading.Thread(target = send_server, args = ())
send_server_thread.daemon = True
send_server_thread.start()


key_exchange_server_thread = threading.Thread(target = key_exchange_server, args = ())
key_exchange_server_thread.daemon = True
key_exchange_server_thread.start()

while(True):
    print("Type 'U': Upload New Price Data.")
    print("Type 'S': Show Price Data.")
    print("Type 'K': Exchange Key.")
    x = raw_input("Command:")
    
    if(x == "U"):
        update_price_data()

    if x == "S":
        show_price_data()

    if x == "K":
        enduser_public_key_text = get_public_key("enduser")
        enduser_public_key = RSA.importKey(enduser_public_key_text)
        init_session()
        
