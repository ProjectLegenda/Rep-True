from smartclient import Smartclient

import time
cc = Smartclient('http://localhost:18000')
 

start = time.time()
cc.reloadWorker()
cc.getDict('../resource/test1.json')
cc.reloadWorker()
cc.getDict('../resource/test1.json')
cc.reloadWorker()
cc.reloadWorker()
cc.getDict('../resource/test1.json')
cc.reloadWorker()
cc.reloadWorker()
cc.getDict('../resource/test1.json')
cc.reloadWorker()
cc.reloadWorker()
cc.getDict('../resource/test1.json')
cc.reloadWorker()
cc.reloadWorker()
cc.getDict('../resource/test1.json')
end = time.time()
print(end-start)
