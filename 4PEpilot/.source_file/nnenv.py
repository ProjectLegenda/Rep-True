#!/usr/local/bin/python3
"""This is only for NN4PE project only.
The module is to read json configuration file"""
import json
import re
import os

##Read Json file in dictionary ./
def getJsonDict():
    etc_dir = os.environ.get('ALGORITHM_HOME')
    with open( str(etc_dir) + '/./etc/config.json','r') as loaded_f:
        loaded_dict = json.load(loaded_f)
    return(loaded_dict)
##def get_sqlalchemy_conn(jsonfile):

def checkKey():
    global loaded_dict 
    loaded_dict = getJsonDict()    

    ##necessary keys
    keys = ['db_connect_type','server','server_port','user','password','database','tmp_dir','auth']

##check if the necessary keys in config Json
    for item in keys:
        if not(loaded_dict.__contains__(item)):
            raise ValueError('configuration files must contain following key ' + item)

def parseValue():
    #check keys:
    checkKey()
   

 #Simple parse values for necessary keys 
    if loaded_dict['db_connect_type'] not in ['hive']:
        print('Connect type in config json : ' + loaded_dict['db_connect_type']) 
        print('The current version only support HIVE and  the connection could possiblly failed if db_connect_type is not hive')
    
    tmp_str = str(loaded_dict['server_port'])
    pattern = '^\d{1,5}$'
    match = re.match(pattern,tmp_str)        
    if match is None or int(tmp_str)<=0 or int(tmp_str)>65535:
          raise ValueError('no valid port in config json! ')     
    """
    for item in loaded_dict:
        print('Key in Json is :' + str(item) + ' and Value in Json is :' + str(loaded_dict[item]))
    """ 

#get connectable string for Pandas
def getConnectable():
    parseValue()
    connectable=loaded_dict['db_connect_type'] + '://' \
    + loaded_dict['user']\
    + ':'\
    + loaded_dict['password']\
    + '@'\
    + loaded_dict['server']\
    + ':' \
    + str(loaded_dict['server_port']) \
    + '/'\
    + loaded_dict['database']\
    + '?auth='\
    + loaded_dict['auth']
    return(connectable)

#get conn for Pandas
def getConn():
    parseValue()
    from pyhive import hive
    conn=hive.Connection(host=loaded_dict['server'],port=loaded_dict['server_port'],username=loaded_dict['user'],database=loaded_dict['database'])   
    return(conn) 


def getTmpdir():
    parseValue()
    return(loaded_dict['tmp_dir'])

def getTable(tab_name):
    parseValue() 
    ##if tab_name not in ['tab','similar','wechat','web','mappingword','stopword']:
    ##    raise ValueError('Input table must be in tag|similar|wechat|web')
    return(loaded_dict[tab_name])
