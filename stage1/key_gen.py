from Crypto.PublicKey import RSA
import sys

def generate_rsa_key(name):

	# factory Key 
	key = RSA.generate(2048)
	public_key = key.publickey().exportKey('PEM')
	private_key = key.exportKey('PEM')

	publick_key_file = open("./%s_public_key.pem" % name, 'w')
	private_key_file = open("./%s_private_key.pem" % name, 'w')

	publick_key_file.write(str(public_key))
	private_key_file.write(str(private_key))

if __name__ == '__main__':
	argv = sys.argv
	generate_rsa_key(argv[1])