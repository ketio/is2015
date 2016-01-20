import socket
import sys
import os
import threading
import time
import cipher
from Crypto.PublicKey import RSA
import msg
import datetime
import random

AUTH_CODE = "NTUIM"

factory_public_key_text = ""
factory_public_key ="" 
f = open("enduser_private_key.pem",'r')
enduser_private_key_text = f.read()
enduser_private_key = RSA.importKey(enduser_private_key_text)
f.close()
f = open("kdc_public_key.pem",'r')
kdc_public_key_text = f.read()
kdc_public_key = RSA.importKey(kdc_public_key_text)
f.close()

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
    server_address = ('localhost', 10001)
    print("connecting to enduser")
    sock.connect(server_address)

    try:
        ID = "enduser"
        N1 = random.randint(0,100)
        
        print("Send ID and N1 to Factory") 
        message_to_enduser = factory_public_key.encrypt("%s|%d" % (ID,N1),24)[0]
        message_to_enduser = msg.generate_msg(message_to_enduser)
        sock.sendall(message_to_enduser)

        print("Receive N1 and N2 from Factory")
        data = sock.recv(4096)
        data = msg.get_package_of_msg(data)
        check = enduser_private_key.decrypt(data)
        
        check = check.split("|")
        N2 = int(check[1])
        
        if N2 != (N1 + 1):
            print("Failed")
            # return 

        print("Send Finally Check to Factory")
        message_to_enduser = factory_public_key.encrypt("%d" % (N2),24)[0]
        message_to_enduser = msg.generate_msg(message_to_enduser)
        sock.sendall(message_to_enduser)

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()

def key_exchange_server():
    global factory_public_key_text
    global factory_public_key 

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('127.0.0.1', 20001)
    sock.bind(server_address)
    sock.listen(1)
    while True:
        # Wait for a connection
        # print >>sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()
        try:

            print("Receive ID and N1 From Factory.")
            data = connection.recv(4096)
            data = msg.get_package_of_msg(data)
            message = enduser_private_key.decrypt(data)
            message = message.split("|")
            ID = message[0]
            N1 = int(message[1])
            N2 = N1+1
            
            print("To Get Public Key of Factory")
            factory_public_key_text = get_public_key(ID)
            factory_public_key = RSA.importKey(factory_public_key_text)

            response = "%d|%d" % (N1, N2)
            encrypted_code = factory_public_key.encrypt(response,24)
            
            
            print("Send N1 and N2 to Factory")
            message = msg.generate_msg(encrypted_code[0])
            connection.sendall(message)

            print("Receive Finally Check")
            data = connection.recv(4096)
            data = msg.get_package_of_msg(data)
            

        finally:
            # Clean up the connection
            connection.close()

def upload_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', 20000)
    sock.bind(server_address)
    sock.listen(1)
    while True:
        connection, client_address = sock.accept()
        try:
            data = connection.recv(4096)
            message = msg.get_package_of_msg(data)
            print("%s" % message)
                
        finally:
            # Clean up the connection
            connection.close()

def download_price_data():
    
    print("Connect to Factory.")
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 10000)
    sock.connect(server_address)

    try:
        if not factory_public_key:
            print("[Warning!]Factory Public Key Not Fonud, Please Exchange First.")
            return
        print("Encrypting Authentication Code.")
        encrypted_code = factory_public_key.encrypt(AUTH_CODE,24)
        signature = cipher.sign(encrypted_code[0], enduser_private_key)

        # Send data
        print("Send Authentication Code with Signature.")
        message = msg.generate_msg(encrypted_code[0], signature)
        sock.sendall(message)

        # Get response
        print("Downloading New Price Data.")
        response = sock.recv(10000)

        print("Decrypting New Price Data")
        encrpted_priced = msg.get_package_of_msg(response)
        signature_of_factory = msg.get_Trail_of_msg(response)

        print("Verifying Signature")
        if not cipher.verify(encrpted_priced, signature_of_factory, factory_public_key):
            print("Verify Failed.")
            return 

        price = enduser_private_key.decrypt(encrpted_priced)

        print("New Pirce Saved.\n")
        f = open("end_user_price.txt","w")
        f.write(price)
        f.close()

    finally:
        sock.close()

def show_price_data():
    if not os.path.isfile("end_user_price.txt"):
        print("Price Data Does Not Exist.")
        return 
    f = open("end_user_price.txt","r")
    data = f.read()
    print(data)

def calculate_price():
    if not os.path.isfile("end_user_price.txt"):
        print("Price Data Does Not Exist.")
        return 
    f = open("end_user_price.txt","r")
    priceDict = dict()
    for row in csv.DictReader(f):
       priceDict[row["item"]] = float(row["price"])

    total = 0
    for item, price in priceDict.items():
        while(True):
            try:
                amount = raw_input("%s($%f) amount: " % (item, price))
                amount = float(amount)
                total += price * amount
                break
            except ValueError:
                print("Amount Must Be Number!")
                continue

    print("Total Price: %f" % total)

upload_listener_thread = threading.Thread(target = upload_listener, args = ())
upload_listener_thread.daemon = True
upload_listener_thread.start()

key_exchange_server_thread = threading.Thread(target = key_exchange_server, args = ())
key_exchange_server_thread.daemon = True
key_exchange_server_thread.start()


while(True):
    print("Type 'D': Download New Price Data.")
    print("Type 'S': Show Price Data.")
    print("Type 'C': Calculate Price.")
    print("Type 'K': Exchange Key.")
    x = raw_input("Command:")
    x = x.upper()
    if x == "D":
        download_price_data()
    if x == "S":
        show_price_data()        
    if x == "C":
        calculate_price()
    if x == "K":
        factory_public_key_text = get_public_key("factory")
        factory_public_key = RSA.importKey(factory_public_key_text)
        init_session()
        

        
