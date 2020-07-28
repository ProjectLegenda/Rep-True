from loader import load_intomysql,f_get_filelist

TABLE_NAME='mh_appwechat_share'

FILE_NAME_PREFIX = 'MH_MSD_AppWeChat_Share*.csv'

month_list = [20200709,20200629,20200521,20200501,20200330,20200227,20200220,20200102,20191226,20191128,20191031,20190926,20190901,20190801,20190701,20190601,20190429]


if __name__ == '__main__':

    file_list = 
    load_intomysql(TABLE_NAME,FILE_NAME_PREFIX,month_list)
