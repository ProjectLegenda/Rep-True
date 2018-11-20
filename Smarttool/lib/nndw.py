#!/usr/local/bin/python3
"""
This module is only for NN4PE project setup
"""
import nnenv
import pandas as pd
from sklearn.externals import joblib
import numpy as np

def Dataframefactory(table_name,sep = ','):
    ##directly return Pandas dataframe
    if nnenv.getIOtype() == 'fs':
        return(pd.read_csv(nnenv.getResourcePath() + table_name,sep=sep,engine='python'))
    if nnenv.getIOtype() == 'db':
        return(pd.read_sql_table(table_name=table_name,con=nnenv.getConnectable()))  

def Numpyarrayfactory(np_name):
    return(np.load(nnenv.getResourcePath() + np_name))


def Joblibfactory(vectorizer):
    return(joblib.load(nnenv.getResourcePath() + vectorizer))


def write_table(data_frame,table_name):
    ##get sqlalchey dataengine
    from sqlalchemy import create_engine
    ##initlize data engine
    engine=create_engine(nnenv.getConnectable())
    ##write data frame to csv tmp file
    path_tmp_file=nnenv.getValue('tmp_dir') + '/' + table_name
    data_frame.to_csv(path_tmp_file, index=False,header=False)
    ##connect database
    conn=engine.connect() 
    ##initilize hive_sql
    hive_sql_ = 'LOAD DATA LOCAL INPATH \'' + path_tmp_file + '\' OVERWRITE INTO TABLE ' + table_name

    ##execute hive_sql
    result=conn.execute(hive_sql_)
    result.close()

def getName(tab_name):
    return nnenv.getValue(tab_name)
