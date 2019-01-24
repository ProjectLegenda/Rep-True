import rec
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import sys

rec_rec = rec.rec
print(rec_rec)
rec_load = rec.load

def init_server():

    host = sys.argv[1]
    port = int(sys.argv[2])

    print(host)
    print(port) 
    global localserver

    localserver = SimpleXMLRPCServer((host,port))
    localserver.register_function(rec_rec)
    localserver.register_function(rec_load)

def run():

    localserver.serve_forever()
rec.load()
init_server()


