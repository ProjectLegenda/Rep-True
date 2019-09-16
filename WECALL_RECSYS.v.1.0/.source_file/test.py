import pandas as pd
from datetime import datetime
import nnenv
import nndw
##nndw.write_mysql_table(df,table_name='iqvia_4pe_hcp_recommendation_new',con=nnenv.getItem('mysql_con'))


from sqlalchemy import create_engine

engine=create_engine(nnenv.getItem('mysql_con'))

engine.connect()

for item in engine.execute('select count(1) from iqvia_4pe_hcp_recommendation_new'):
    print(item)


for item in engine.execute('desc iqvia_4pe_hcp_recommendation_new'):
    print(item)




for item in engine.execute('show index from iqvia_4pe_hcp_recommendation_new'):
    print(item)


from sqlalchemy import create_engine
from sqlalchemy.engine import reflection
insp = reflection.Inspector.from_engine(engine)
for name in insp.get_table_names():
    for index in insp.get_indexes(name):
        print (index)

t1 = datetime.now()

for item in engine.execute("select * from iqvia_4pe_hcp_recommendation_new where `index` = 88225 "):
    print(item)


t2 = datetime.now()

print(t2 - t1)




t1 = datetime.now()

for item in engine.execute("select count(1) from iqvia_4pe_hcp_recommendation_new where `index` between 100 and 200000"):
    print(item)


t2 = datetime.now()

print(t2 - t1)





