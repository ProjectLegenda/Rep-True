import sys
import json
import xmlrpc.client
import time
class Smartclient():

    def __init__(self,url,waitsec = 0.5):
        self.s = xmlrpc.client.ServerProxy(url)
        self.waitsec = waitsec 

    def getdict(self,jsonfile):
        with open(jsonfile,'r') as loaded_f:
            loaded_dict = json.load(loaded_f)
            self.seq = self.s.Additemtoqueue(loaded_dict)       
            time.sleep(self.waitsec)            
            self.labels = self.s.Getitemfromdict(self.seq)
        return(self.labels)    
   
    def getcached(self):
        return(self.labels)
    





