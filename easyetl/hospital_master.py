from loader import load_intomysql,f_get_filelist
import pandas as pd

table_name='hospital_master'

file_name_prefix = 'CN_MH_MSD_Hospital_Master_'

month_list = [20200629,20191226,20191128,20191031,20190926,20190901,20190801,20190701,20190601,20190429]

if __name__ == '__main__':

    file_list = f_get_filelist(file_name_prefix,month_list)
    load_intomysql(table_name,file_list)
