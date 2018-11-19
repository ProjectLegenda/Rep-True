from smartclient import Smartclient

import time
cc = Smartclient('http://localhost:18000')
 

start = time.time()
#cc.reloadWorker()
cc.getDict('../resource/test1.json')
cc.getDict('../resource/test1.json')
cc.getDict('../resource/test1.json')
cc.getDict('../resource/test1.json')
cc.getDict('../resource/test1.json')
cc.getDict('../resource/test1.json')
cc.getDict('../resource/test1.json')
cc.getDict('../resource/test1.json')
cc.getDict('../resource/test1.json')
cc.getDict('../resource/test1.json')
cc.getDict('../resource/test1.json')
cc.getDict('../resource/test1.json')
cc.getDict('../resource/test1.json')
print(cc.getDict('../resource/test1.json'))
##cc.shutdown()
end = time.time()
print(end-start)
