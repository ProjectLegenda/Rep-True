from loader import load_intomysql,f_get_filelist

table_name='hcp_ts'

file_name_prefix = 'HCP_TS_'

month_list = [20200709,20200629,20200521,20200430,20200330,20200227,20200102,20191226,20191128,20191031,20190926,20190901,20190801,20190627,20190601,20190429] 


if __name__ == '__main__':
    file_list = f_get_filelist(file_name_prefix,month_list)
    load_intomysql(table_name,file_list)
