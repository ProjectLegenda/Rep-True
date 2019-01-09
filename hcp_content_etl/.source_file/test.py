url = 'mysql+pymysql://SoftTekRead:A*USxm7BXd*&aGTS@minisitedb.chinanorth.cloudapp.chinacloudapi.cn:3306/wc_itangyi'
sql_statment = ' select distinct ln_date,ln_title,ln_content from lk_news where ln_is_valid = 1 ' 

from creator import *

creator = CreatorCreator(product_type ='sql',source='etlsource')

etlsource = creator.create()

etlsource.load(sqlalchemy_url = url,cursor_statment = sql_statment)

result = etlsource.getdata()

etlsource.getcount()

parser = FlatCreator(product_type = 'simplehtml',source = 'parser')


creator = CreatorCreator(product_type = 'ori',source = 'etlsource')

orietlsource = creator.create()

orietlsource.load([{'a':1},{'b':3}])

tmp = orietlsource.getdata()


for item in tmp:
    print(item)
'''
for x in result:
    print('---------------------------------------------------------')
    parser.feed(x['ln_content']) 
    print('_____title is ________',x.ln_title,'________dateis_______',x.ln_date)
    print(parser.getdata())
'''
