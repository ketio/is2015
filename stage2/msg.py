def generate_msg(package,Trail=""):
    packageLen = len(package)
    header1 = " "*512
    header2 = "% 512s" % (packageLen)

    msg = header1+header2+package+Trail
    return msg

def get_package_of_msg(message):
	header = message[:1024]
	packageLen = int(header.strip())
	index = 1024+packageLen
	return message[1024:index]

def get_Trail_of_msg(message):
	header = message[:1024]
	packageLen = int(header.strip())
	index = 1024+packageLen
	return message[index:]