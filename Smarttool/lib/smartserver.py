# -*- coding: utf-8 -*-
from smartcore import *
import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from multiprocessing import Queue
from threading import RLock
import time
from multiprocessing import Process
import signal
import os
from request import Request
#halt queue
haltqueue = Queue()

#content queue
contentq = Queue()

#label queue
labelq = Queue()

#global sequence of the service
seq = 0

#lock
seqlock = RLock()

#label dict
labeldict = {}

#slave list
plist = []
pids = []
#slave count
pcnt = 2

#constant
RUNNING=1
HALTING=0


def shutdown():
    seqlock.acquire()
    request = Request(r_seq = 0,r_data = 0,r_type = 'SHUTDOWN')
    contentq.put(request,block=True)
    haltqueue.put(HALTING,block=True)
    print('[INFO]Request of Shutting down smarttool has been set to contentqueue')  
    seqlock.release()
    return(1)
    
    
def reloadWorker():
    seqlock.acquire()
    global seq
    seq = seq + 1
    request = Request(r_seq = seq,r_data = 0,r_type = 'RELOAD') 
    contentq.put(request,block=True)   
    print('[INFO]Request of reloading worker has been set to contentqueue')
    seqlock.release()
    return(1)

def addItemtoQueue(item):
    seqlock.acquire()
    global seq
    seq = seq + 1    
    request = Request(r_seq = seq,r_data = item,r_type = 'CALCULATE')
    contentq.put(request,block=True)
    print('[INFO]Request ' + str(seq) + ' sent to contentqueue')
    seqlock.release()
    return(seq)


def extractItemfromQueue(queue):
    while True:
        intuple = queue.get(block=True)
        seqlock.acquire()
        #adding timestamp to dictionary
        labeldict[intuple[0]] = (intuple[1],time.time()) 
        seqlock.release()

def getItemfromDict(sseq):
    trys = 100
    while True and trys !=0:
        if sseq in labeldict.keys():
            seqlock.acquire()
            #get dictionary
            t = labeldict[sseq][0]
            labeldict.pop(sseq)
            seqlock.release()
            print('[INFO]Sequence' + str(sseq) + 'Has been poped out from labeldict')
            return(t)
        else:
            time.sleep(0.1)
            trys = trys - 1
            print('[INFO]Remote call is waiting ')
    raise TimeoutError

def garbageCollector(timeout=100):
    while True:
        seqlock.acquire()        
        t = time.time()
        garbagekeys = []
        for x in labeldict:
            if t - labeldict[x][1] > timeout:
                garbagekeys.append(x) 
         
        for y in garbagekeys:
            labeldict.pop(y)
       
        seqlock.release()
        time.sleep(timeout)  
        endtime = time.time()
        print('[INFO] Garbage collector elapsed:',endtime - t)
        
def slaveProcess():
    for x in range(1,pcnt):
        plist.append(Process(target=Worker,args=(contentq,labelq)))

def slaveStart():
    for process in plist:
        process.daemon = True
        process.start()
        pids.append(process.pid)

def slaveJoin():
    for process in plist:
        process.join()


class ServerThread(threading.Thread):
    def __init__(self,host,port):
         threading.Thread.__init__(self)
         self.localServer = SimpleXMLRPCServer((host,port))
         self.localServer.register_function(addItemtoQueue) #just return a string
         self.localServer.register_function(getItemfromDict)
         self.localServer.register_function(reloadWorker)
         self.localServer.register_function(shutdown)
    def run(self):
         self.localServer.serve_forever()


#rpc server
def init(host,port):
    server = ServerThread(host,port)
    server.start()

    #queue extractor thread
    queueextractor = threading.Thread(target = extractItemfromQueue, args = (labelq,))
    #garbage thread
    garbagecollector = threading.Thread(target = garbageCollector,args = ())

    queueextractor.start()
    garbagecollector.start()

    slaveProcess()
    slaveStart()


    while True:
        if haltqueue.get() == HALTING:
            print('')
            slaveJoin()
            break;
    os.kill(os.getpid(), signal.SIGKILL)

