from sqlalchemy import create_engine
import nnenv







mysql_url_test = 'mysql+pymysql://content_db_user:qaz!#wsx$edc@10.0.2.7:3306/content_db_test'
mysql_url = 'mysql+pymysql://content_db_user:qaz!#wsx$edc@etlappnode1:3306/content_db'

p_s= 'selet count(1) from '

print('Mysql database have tables')


engine1 = create_engine(mysql_url_test)
connect1 = engine1.connect()
l = engine1.table_names()



def f_test(table_name,engine):
    t_s = 'select count(1) from  ' + table_name
    for item in engine.execute(t_s):
        print(table_name)
        print(item)
        
    

    
for item in l:
    f_test(item,connect1)


connect1.close()
