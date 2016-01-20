import socket
import sys
import os
import threading
import time
from Crypto.PublicKey import RSA
import msg
import cipher

AUTH_CODE = "NTUIM"
f = open("factory_private_key.pem",'r')
factory_private_key = RSA.importKey(f.read())
f.close()
f2 = open("enduser_public_key.pem",'r')
enduser_public_key = RSA.importKey(f2.read())
f2.close()

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

while(True):
    print("Type 'U': Upload New Price Data.")
    print("Type 'S': Show Price Data.")
    x = raw_input("Command:")
    
    if(x == "U"):
        update_price_data()

    if x == "S":
        show_price_data()