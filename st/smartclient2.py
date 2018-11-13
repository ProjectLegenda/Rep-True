import xmlrpc.client
import sys
import json
import datetime
import time


s2 = xmlrpc.client.ServerProxy('http://localhost:18001')

m = s2.Getitemfromdict(1000)

print(m)


