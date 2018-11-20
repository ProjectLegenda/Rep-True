import sys
import json
import xmlrpc.client
import time
class Smartclient():

    def __init__(self,url,waitsec = 0.2):
        self.s = xmlrpc.client.ServerProxy(url)
        self.waitsec = waitsec 

    def getDict(self,jsonfile):
        with open(jsonfile,'r') as loaded_f:
            loaded_dict = json.load(loaded_f)
            self.seq = self.s.addItemtoQueue(loaded_dict)       
            time.sleep(self.waitsec)            
            self.labels = self.s.getItemfromDict(self.seq)
        return(self.labels)    
   
    def getCached(self):
        return(self.labels)
    
    def reloadWorker(self):
        self.s.reloadWorker()

    def shutdown(self):
        self.s.shutdown()



