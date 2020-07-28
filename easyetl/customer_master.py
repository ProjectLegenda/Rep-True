from loader import load_intomysql,f_get_filelist

table_name='customer_master'

file_name_prefix = 'CN_MH_MSD_Customer_Master_'

month_list = [20200709,20200521,20200430,20200102,20191128,20190926,20190901,20190429]

if __name__ == '__main__':

    file_list = f_get_filelist(file_name_prefix,month_list) 
    load_intomysql(table_name,file_list)
