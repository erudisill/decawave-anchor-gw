'''
Created on Dec 22, 2014

@author: ericrudisill
'''
import socket
from binascii import hexlify


HOST, PORT = "localhost", 1337

class CpSerialBytes(bytearray):
    def __str__(self, *args, **kwargs):
        hexline = hexlify(self)
        n = 2
        pairs = [hexline[i:i+n] for i in range(0, len(hexline), n)]
        final = ("[{0:03}] ".format(len(self)) + " ".join(pairs)).upper()
        return final
    
def client(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    while True:
        response = sock.recv(1024)
        if not response: 
            break
        print "[RCV]: " + CpSerialBytes(response)
    sock.close()
    
    
if __name__ == '__main__':
    client(HOST, PORT)