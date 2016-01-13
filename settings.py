'''
Created on Dec 19, 2014

@author: ericrudisill
'''
from cpSerial import CpSerialSettings
from tcpclient import tcpclientsettings
import json

class SettingsEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, (Settings, CpSerialSettings)):
            return super(SettingsEncoder, self).default(obj)
        return obj.__dict__
    
    
class Settings(object):

    def __init__(self):
        self.filename = ""
        self.cpSerial = CpSerialSettings()
        self.tcpclient = tcpclientsettings()
        
    def __str__(self):
        s = "CpSerial: " + str(self.cpSerial) + "\r\n" + "tcpclient: " + str(self.tcpclient)
        return s