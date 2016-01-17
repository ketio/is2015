from Crypto.PublicKey import RSA


# Server Key 
server_key = RSA.generate(2048)
server_public_key = server_key.publickey().exportKey('PEM')
server_private_key = server_key.exportKey('PEM')

server_publick_key_file = open("server_public_key.pem", 'w')
server_private_key_file = open("server_private_key.pem", 'w')

server_publick_key_file.write(str(server_public_key))
server_private_key_file.write(str(server_private_key))

# Client Key
client_key = RSA.generate(2048)
client_public_key = client_key.publickey().exportKey('PEM')
client_private_key = client_key.exportKey('PEM')

client_publick_key_file = open("client_public_key.pem", 'w')
client_private_key_file = open("client_private_key.pem", 'w')

client_publick_key_file.write(str(client_public_key))
client_private_key_file.write(str(client_private_key))
