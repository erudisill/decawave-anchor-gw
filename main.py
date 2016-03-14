'''
Created on Dec 19, 2014

@author: ericrudisill
'''
import getopt
import sys
from settings import Settings
import jsonpickle
from cpSerial import CpSerialService
import time
from tcpclient import tcpclient

HOST, PORT = "localhost", 1337

def loadSettings(settingsFile=None):
    if not settingsFile:
        settingsFile = "settings.json"
    s = Settings()
    try:
        with open(settingsFile, "r") as f:
            j = f.read()
            s = jsonpickle.decode(j)
    except Exception, ex:
        print ex
        print "Settings file not found. Creating default template file. Add port there."
        with open(settingsFile, "w") as f:
            jsonpickle.set_encoder_options('json', indent=4)
            f.write(jsonpickle.encode(s))
        exit(2)

    s.filename = settingsFile
    
    return s


def main(argv):
    settingsFile = None
    try:
        opts, args = getopt.getopt(argv, "hs:", ["help","settings="])
    except getopt.GetoptError:
        print 'usage: bitstorm-server -s <settingsfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'usage: bitstorm-server -s <settingsfile>'
            sys.exit()
        elif opt in ("-s", "--settings"):
            settingsFile = arg
    
    settings = loadSettings(settingsFile)
    print "Loaded settings from " + settings.filename
    print str(settings)

    print "Connectiong to location server."
    client = tcpclient(settings.tcpclient);
    client.connect();

    print "Starting serial service."
    serial = CpSerialService(settings.cpSerial)
    serial.connectData(client.putData)
    client.connectData(serial.writeData)
    serial.start()
    
    print "Use Control-C to exit."
    
    do_exit = False
    while do_exit == False:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            do_exit = True
         
    serial.stop()
    
    print "\r\nDone"
    
if __name__ == '__main__':
    print "\r\nBitStorm Server"
    main(sys.argv[1:])