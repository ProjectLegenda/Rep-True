from loader import load_intomysql

TABLE_NAME='customer_master'

FILE_NAME_PREFIX = 'CN_MH_MSD_Customer_Master_'

month_list = [20200709,20200521,20200430,20200102,20191128,20190926,20190901,20190429]

if __name__ == '__main__':

    load_intomysql(TABLE_NAME,FILE_NAME_PREFIX,month_list)
