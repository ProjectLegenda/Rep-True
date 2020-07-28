from loader import load_intomysql
import pandas as pd

TABLE_NAME='hospital_master'

FILE_NAME_PREFIX = 'CN_MH_MSD_Hospital_Master_'

month_list = [20200629,20191226,20191128,20191031,20190926,20190901,20190801,20190701,20190601,20190429]

if __name__ == '__main__':

    load_intomysql(TABLE_NAME,FILE_NAME_PREFIX,month_list)
