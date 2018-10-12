#!/usr/local/bin/python3
"""
This module is only for NN4PE project setup
"""
import nnenv
import pandas as pd
def read_table(table_name):
    ##directly return Pandas dataframe
    return(pd.read_sql_table(table_name=table_name,con=nnenv.getConnectable()))  


def write_table(data_frame,table_name):
    ##get sqlalchey dataengine
    from sqlalchemy import create_engine
    ##initlize data engine
    engine=create_engine(nnenv.getConnectable())
    ##write data frame to csv tmp file
    path_tmp_file=nnenv.getTmpdir() + '/' + table_name
    data_frame.to_csv(path_tmp_file, index=False,header=False)
    ##connect database
    conn=engine.connect() 
    ##initilize hive_sql
    hive_sql_ = 'LOAD DATA LOCAL INPATH \'' + path_tmp_file + '\' OVERWRITE INTO TABLE ' + table_name

    ##execute hive_sql
    result=conn.execute(hive_sql_)
    result.close()

def getTable(tab_name):
    return nnenv.getTable(tab_name)
