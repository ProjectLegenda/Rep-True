#!/usr/local/bin/python3
"""
This module is only for NN4PE project setup
"""
import nnenv
import pandas as pd
from sklearn.externals import joblib
import numpy as np
from sqlalchemy import create_engine

def Dataframefactory(table_name,sep = ',',iotype = 'fs'):
    ##directly return Pandas dataframe
    if iotype == 'fs':
        return(pd.read_csv(nnenv.getResourcePath() + nnenv.getItem(table_name),sep=sep))
    if iotype == 'db':
        return(pd.read_sql_table(table_name=nnenv.getItem(table_name),con=nnenv.getConnectable()))  
    else:
        print('IOtype is only for db or fs')
        raise(Exception)
    
def Numpyarrayfactory(np_name):
    return(np.load(nnenv.getResourcePath() + np_name))


def Joblibfactory(vectorizer):
    return(joblib.load(nnenv.getResourcePath() + vectorizer))


def write_table(data_frame,table_name,sep = ',',iotype = 'fs',remove_tmpfile = True):
    
    if iotype == 'fs':
        data_frame.to_csv(nnenv.getResourcePath() + nnenv.getItem(table_name),sep=sep,index = False)  

    elif iotype == 'db':
         
    ##initlize data engine
        engine=create_engine(nnenv.getConnectable())
    ##write data frame to csv tmp file
        path_tmp_file=nnenv.getItem('tmp_dir') + '/' + nnenv.getItem(table_name)
        data_frame.to_csv(path_tmp_file, index=False,header=False)
    ##connect database
        conn=engine.connect() 
    ##initilize hive_sql
        hive_sql_ = 'LOAD DATA LOCAL INPATH \'' + path_tmp_file + '\' OVERWRITE INTO TABLE ' + nnenv.getItem(table_name)

    ##execute hive_sql
        result=conn.execute(hive_sql_)
        result.close()
        
    else:
        print('IOtype is only for db or fs')
        raise(Exception)

