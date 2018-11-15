from smartclient import Smartclient

cc = Smartclient('http://192.168.100.186:19000')
 
print(cc.getdict('../resource/article1.json'))
