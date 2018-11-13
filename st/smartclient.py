import xmlrpc.client
import sys
import json
import datetime
import time


s = xmlrpc.client.ServerProxy('http://localhost:18000')

s2 = xmlrpc.client.ServerProxy('http://localhost:18001')

starttime = datetime.datetime.now()


with open(sys.argv[1],'r') as loaded_f:
    loaded_dict = json.load(loaded_f)
    for x in range(1,20):
        m = s.Additemtoqueue(loaded_dict)
        print(m)
        k = s2.Getitemfromdict(m)

        print(k) 
 
endtime = datetime.datetime.now()



print (endtime - starttime)



