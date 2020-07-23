from sqlalchemy import create_engine
import os
import fnmatch

PATH='/home/adminiqvia/'

RAW_PREFIX='MSD/CN_MH_MSD_RawData_'

FILE_SEARCH_PREFIX= PATH + RAW_PREFIX

MYSQL_ENGINE=create_engine('mysql+pymysql://iqvia_ops:iqvia_ops@192.168.0.51:3306/msd_recdb')

def simple_search(search_list,pattern):
    final_list = []
    for d in search_list:
        for root,dirnames,filenames in os.walk(d):
            for filename in fnmatch.filter(filenames,pattern):
                final_list.append(os.path.join(root,filename))

    return(final_list)

#conn = MYSQL_ENGINE.connect()

#conn.close()
