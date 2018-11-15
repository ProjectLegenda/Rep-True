from smartclient import Smartclient

cc = Smartclient('http://localhost:18000')
 
print(cc.getdict('../resource/article1.json'))
