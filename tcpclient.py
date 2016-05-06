'''
Created on Nov 12, 2015

@author: ericrudisill
'''

import sys
import socket
import threading
import re
import time

class tcpclientsettings():
    def __init__(self):
        self.ip = 0
        self.port = 0
        self.anchor_id = 0
    
    def __str__(self):
        s =  self.ip + ":" + str(self.port) + "  anchor_id: " + str(self.anchor_id)
        return s
    
class tcpclient(object):


    def __init__(self, settings):
        self.ip = settings.ip;
        self.port = settings.port;
        self.anchor_id = settings.anchor_id
        self.sequence = 0
        self._writeData = None

    def connect(self):    
        self.client_thread = threading.Thread(target=self._client_method)
        self.client_thread.daemon = True
        self.client_thread.start()
        
    
    def _client_method(self):
        while True:
            try:
                print('Connecting...')
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.ip, self.port))
                print('Connected!')
                while True:
                    response = self.sock.recv(1024)
                    if not response: 
                        break
#                     print "Received: " + response
                    self._writeData(response);
                self.sock.close()
                time.sleep(1)
            except Exception as ex:
                print("Connect Exception: ", ex)
                time.sleep(2)
        
    def putData(self, data):
#        if (data.startswith('* A')):
#            return
        if (data.startswith('*')):
#             parts = data.split(' ')
#             if (len(parts) != 6):
#                 print(data + " ==> BAD FORMAT")
#             else:
            self.sequence = self.sequence + 1
#             print("[RCV] " + data);
            try:
                self.sock.send(data + "\r\n");
            except:
                print("Could not send msg!")
        
                    
    def connectData(self, q):
        self._writeData = q                    
            
