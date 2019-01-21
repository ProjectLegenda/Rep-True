from smartclient import Smartclient

import time
cc = Smartclient('http://localhost:18000')
 
#cc.Test()
start = time.time()
#cc.reloadWorker()
#print(cc.getDict('../resource/test0.json'))
#print(cc.getDict('../resource/test1.json'))
#print(cc.getDict('../resource/test2.json'))
print(cc.getDict('../resource/test1.json'))
print(cc.getDict('../resource/test4.json'))
print(cc.getDict('../resource/test5.json'))
#print(cc.getDict('../resource/test6.json'))
#print(cc.getDict('../resource/test7.json'))
#print(cc.getDict('../resource/test8.json'))
#print(cc.getDict('../resource/test9.json'))
#cc.shutdown()
cc.reloadWorker()

print(cc.Test('../resource/test1.json'))
print(cc.Test('../resource/test3.json'))
print(cc.Test('../resource/test5.json'))
cc.shutdown()
end = time.time()
print(end-start)
