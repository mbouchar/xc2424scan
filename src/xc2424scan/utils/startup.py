# Use this file with PYTHONSTARTUP to debug scanlib

PORT = 14882

from xc2424scan import scanlib
scanner = scanlib.XeroxC2424()

ip = raw_input("enter scanner ip : ")
scanner.connect(ip, PORT)

def save_file(filename, data):
    f = file(filename, "w")
    f.write(data)
    f.close()
