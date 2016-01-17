from Crypto.PublicKey import RSA


# factory Key 
factory_key = RSA.generate(2048)
factory_public_key = factory_key.publickey().exportKey('PEM')
factory_private_key = factory_key.exportKey('PEM')

factory_publick_key_file = open("./factory_public_key.pem", 'w')
factory_private_key_file = open("./factory_private_key.pem", 'w')

factory_publick_key_file.write(str(factory_public_key))
factory_private_key_file.write(str(factory_private_key))

# enduser Key
enduser_key = RSA.generate(2048)
enduser_public_key = enduser_key.publickey().exportKey('PEM')
enduser_private_key = enduser_key.exportKey('PEM')

enduser_publick_key_file = open("./enduser_public_key.pem", 'w')
enduser_private_key_file = open("./enduser_private_key.pem", 'w')

enduser_publick_key_file.write(str(enduser_public_key))
enduser_private_key_file.write(str(enduser_private_key))
