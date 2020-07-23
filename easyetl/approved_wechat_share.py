from loader import load_intomysql,f_get_filelist
from format_ import share_final_chain

table_name='mh_appwechat_share'

file_name_prefix = 'MH_MSD_AppWeChat_Share*.csv'

month_list = [20200709,20200629,20200521,20200501,20200330,20200227,20200220,20200102,20191226,20191128,20191031,20190926,20190901,20190801,20190701,20190601,20190429]


if __name__ == '__main__':

    file_list = f_get_filelist(file_name_prefix,month_list)
    print(file_list)
    

    # call os.system to convert encoding to utf-8 if possible

    import os 

    converted_file_list = []

    for file_ in file_list:

        converted_file = file_[:-3] + 'convert'

        print('convert encoding to utf-8 if possible for {}'.format(file_))
        os.system('enca -L zh_CN -x UTF-8 ' + file_)    
        print('formating file {}'.format(file_))
        share_final_chain(file_,converted_file)
        converted_file_list.append(converted_file)
    
    print(converted_file_list)
    load_intomysql(table_name,converted_file_list)
 
