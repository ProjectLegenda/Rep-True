#!/usr/local/bin/python3

import nnenv  
import nndw as nn
from sqlalchemy import create_engine
    ##initlize data engine
engine = create_engine(nnenv.getConnectable())
connection = engine.connect()
result = connection.execute('show tables')

for row in result:
    df = nn.read_table(row['tab_name'])
    df.to_csv('./resource/' + row['tab_name']+ '.csv')

