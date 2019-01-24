
import xmlrpc.client
url = 'http://localhost:18000'

s = xmlrpc.client.ServerProxy(url)

s.load()

print(s.rec('o_Ap-jriOfYVyTL0kLa7eXkTRatE'))
print( s.rec('o_Ap-jhFnOqamBa013hmVj5RDXtE'))
print( s.rec('ohKW6jjd56V9pxJi5jD6zZP79thQ'))
print( s.rec('o_Ap-jqp8VSV313yEfmjzoCt_dRY'))
print( s.rec('o_Ap-jhKfiUxydv6tl0l7BVM1A4U'))
print( s.rec('o_Ap-jqpPz_TQMNh2ITLWL9v8trY'))
print( s.rec('o_Ap-jh45NAzkr1tQqrd9GgvlvPo'))





print( s.rec('ohKW6jjd56V9pxJi5jD6zZP79thQ'))
print( s.rec('ohKW6jmsAkjofFxhKYfml6Cehz-U'))



