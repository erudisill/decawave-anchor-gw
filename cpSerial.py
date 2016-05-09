import logging
import serial
import threading
import time
from binascii import hexlify
from serial.tools import list_ports

class CpSerialBytes(bytearray):
    def __str__(self, *args, **kwargs):
        hexline = hexlify(self)
        n = 2
        pairs = [hexline[i:i+n] for i in range(0, len(hexline), n)]
        final = ("[{0:03}] ".format(len(self)) + " ".join(pairs)).upper()
        return final
    
class CpSerialSettings():
    def __init__(self):
        self.timeout = 0
        self.port = ""
        self.baudrate = 38400
        self.parity = 'N'
        self.stopbits = 1
        self.bytesize = 8
        self.xonxoff = 0
        self.rtscts = 0
        self.linemode = 0
        self.token = "CDC"
    
    def __str__(self):
        s =  self.port + " " + str(self.baudrate) + " " + str(self.bytesize) + \
             self.parity + str(self.stopbits)
        if self.xonxoff != 0:
            s = s + ",xonxoff"
        elif self.rtscts != 0:
            s = s + ",rtscts"
        return s

class CpSerialService(threading.Thread):
    
    def __init__(self, settings=None, loggerName='CpSerialService'):
        threading.Thread.__init__(self)
        self.settings = settings
        self._putData = None
        self.stop_event = threading.Event()
        self.received_bytes = 0
        self.logger = logging.getLogger(loggerName)
        self.ser = serial.Serial()
        self.ser.timeout = 0
        self.ser.port = ""
        if not settings:
            self.ser.port = ""
            self.ser.baudrate = 115200
            self.ser.parity = 'N'
            self.ser.stopbits = 1
            self.ser.bytesize = 8
            self.ser.xonxoff = 0
            self.ser.rtscts = 0
            self.ser.linemode = 0
        else:
            self.ser.port = settings.port
            self.ser.baudrate = settings.baudrate
            self.ser.parity = settings.parity
            self.ser.stopbits = settings.stopbits
            self.ser.bytesize = settings.bytesize
            self.ser.xonxoff = settings.xonxoff
            self.ser.rtscts = settings.rtscts
            self.ser.linemode = settings.linemode
            
        self.records = -1
            
    def discover_port(self):
        if self.settings.port != "*":
            self.ser.open()
        else:
            while self.stop_event.is_set() == False:
                p = list(list_ports.comports())
                if len(p) > 0:
                    cdc = [c for c in p if self.settings.token in c[1]]
                    for port in cdc:
                            self.ser.port = port[0]
                            for x in range(0,4):
                                print "Trying " + str(x+1) + ": " + port[0]
                                try:
                                    self.ser.open()
                                    self.ser.read(self.ser.inWaiting())
                                    self.ser.write("v\r")
                                    time.sleep(0.25)
                                    line = self.ser.readline()
                                    print(line)
                                    if "COORDINATOR" in line:
                                        return
                                    self.ser.close()
                                    time.sleep(0.25)
                                except Exception as ex:
                                    print ex
                print "Could not connect to a coordinator on a serial port.  Trying again in a sec."
                time.sleep(1)
                
            if self.stop_event.is_set() == True:
                try:
                    self.ser.close()
                except:
                    pass

        
    def run(self):
        
        self.logger.info('starting CpSerialService...')
        if self.ser.linemode == 1:
            print('CpSerialSerivce using COBS')
            self.records = 0
        else:
            print('CpSerialSerivice in passthrough mode')
    
        
        data = bytearray()
        
        #self.ser.open()
        self.discover_port()
        self.logger.info('opened port ' + self.ser.port)
        
        while self.stop_event.is_set() == False:
            
             if self.ser.linemode == 1:
                 while self.ser.inWaiting() > 0:
                     c = self.ser.read(1)
                     self.received_bytes = self.received_bytes + 1
                     if c == '\r':
                         self.records = self.records + 1
                         if self._putData:
                             print(data.decode("utf-8"))
                             self._putData(bytearray(data))
                             del data[:]
                     else:
                         if c != '\n':
                             data.append(c)
             else:
                 del data[:]
                 if (self.ser.inWaiting() > 0):
                     data.extend(self.ser.read(self.ser.inWaiting()))
         
                 if len(data) > 0:
                     # log and signal data received
                     self.received_bytes = self.received_bytes + len(data)
                     if self._putData:
                         # send new copy of data
                         self._putData(bytearray(data))
            #time.sleep(0.005)
                    
        # shutdown the serial port
        self.ser.close() 
        
        self.logger.info('CpSerialService stopped!')

    def stop(self):
        if self.is_alive() == True:
            self.stop_event.set()
            self.join()
            
    def connectData(self, q):
        self._putData = q
        
    def writeData(self, data):
        print("[TCP] " + data)
        self.ser.write(data)
