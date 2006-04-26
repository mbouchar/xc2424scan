#!/usr/bin/python

import socket

HOST = raw_input("enter scanner ip : ")
PORT = 14882

if __name__ == "__main__":
    socks = socket.socket()
    socks.connect((HOST, PORT))
    socks.settimeout(1)
    try:
        while True:
            command = raw_input("# ")
            if command != "":
                socks.send("%s\n" % command)
            try:
                data = socks.recv(1024)
                print "Received", repr(data)
            except socket.timeout:
                pass
    except KeyboardInterrupt:
        pass
    except Exception, e:
        print e
    
    socks.close()
    print "\n"