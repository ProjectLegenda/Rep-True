import sys
import json
import xmlrpc.client

class Smarttoolclient():

    def __init__(self,url):
        self.s = xmlrpc.client.ServerProxy(url)
 
    def getdict(self,jsonfile):
        with open(jsonfile,'r') as loaded_f:
            loaded_dict = json.load(loaded_f)
            self.seq = self.s.Additemtoqueue(loaded_dict)       
            self.labels = self.s.Getitemfromdict(self.seq)
        return(self.labels)    
   
    def getcached(self):
        return(self.labels)
    
clienttest = Smarttoolclient('http://localhost:18000')

print(clienttest.getdict('../resource/article3.json'))




