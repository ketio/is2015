import socket
import sys
import threading
import time
import csv
from Crypto.PublicKey import RSA
import os.path
import cipher
import msg


AUTH_CODE = "NTUIM"
f = open("factory_public_key.pem",'r')
factory_public_key = RSA.importKey(f.read())
f.close()

f = open("enduser_private_key.pem",'r')
enduser_private_key = RSA.importKey(f.read())
f.close()

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

while(True):
    print("Type 'D': Download New Price Data.")
    print("Type 'S': Show Price Data.")
    print("Type 'C': Calculate Price.")
    x = raw_input("Command:")
    if x == "D":
        download_price_data()
    if x == "S":
        show_price_data()        
    if x == "C":
        calculate_price()
