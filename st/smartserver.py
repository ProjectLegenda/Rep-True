# -*- coding: utf-8 -*-
from smartcore import *
import threading

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

from multiprocessing import Queue
from threading import RLock

import time

contentq = Queue()
labelq = Queue()
seq = 0
seqlock = RLock()
labeldict = {}

def Additemtoqueue(item):
    seqlock.acquire()
    global seq
    seq = seq + 1    
    contentq.put((seq,item),block=True)
    seqlock.release()
    return(seq)


def Extractitemfromqueue(queue):
    while True:
        intuple = queue.get(block=True)
        seqlock.acquire()
        labeldict[intuple[0]] = intuple[1] 
        seqlock.release()

def Getitemfromdict(sseq):
    trys = 100
    while True and trys !=0:
        if sseq in labeldict.keys():
            t = labeldict[sseq]
            labeldict.pop(sseq)
            return(t)
        else:
            time.sleep(0.05)
            trys = trys - 1
            print(trys)
    raise TimeoutError

class ServerThread(threading.Thread):
    def __init__(self,target,port):
         threading.Thread.__init__(self)
         self.localServer = SimpleXMLRPCServer(("localhost",port))
         self.localServer.register_function(target) #just return a string

    def run(self):
         self.localServer.serve_forever()

serverin = ServerThread(Additemtoqueue,18000)
serverout = ServerThread(Getitemfromdict,18001)
serverin.start()
serverout.start()

from multiprocessing import Process

proc = Process(target=Worker,args=(contentq,labelq))
proc2 = Process(target=Worker,args=(contentq,labelq))
t = threading.Thread(target = Extractitemfromqueue, args = (labelq,))
proc.start()
proc2.start()
t.start()
