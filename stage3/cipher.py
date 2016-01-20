from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

def encrypt(plaintext, sender_private_key, receiver_public_key):
    ciphertext = (receiver_public_key.encrypt(plaintext, 24))[0]

    h = SHA.new(plaintext)
    # hashValue = h.hexdigest()

    signature = sign(h, sender_private_key)
    signature = ("% 512s" % signature)
    padding = " "*512

    header = padding + signature 
    message = header + ciphertext

    return message

def decrypt(message, sender_public_key, receiver_private_key):
    
    header = message[:1024]
    ciphertext = message[1024:]

    signature = header.strip()
    plaintext = receiver_private_key.decrypt(ciphertext)
    h = SHA.new(plaintext)
    
    if verify(h, signature, sender_public_key):
        return plaintext

    else:
        return False

def sign(message, sender_private_key):

    h = SHA.new(message)
    signer = PKCS1_v1_5.new(sender_private_key)
    signature = signer.sign(h)
    
    return signature

def verify(message, signature, sender_public_key):
    h = SHA.new(message)
    verifier = PKCS1_v1_5.new(sender_public_key)
    return verifier.verify(h, signature)
