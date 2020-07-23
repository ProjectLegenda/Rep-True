import pandas as pd
from env import *

def f_return_union_df(final_file_list):
    
    df_final = pd.DataFrame() 

    for f in final_file_list:
            
        print(f)
        try:
            df = pd.read_csv(f)

        except UnicodeDecodeError:
            df = pd.read_csv(f,encoding='utf-16')


        print(df.columns)

        striped_column = [ column.strip() for column in df.columns.tolist()]
        df.columns = striped_column
        df_final = df_final.append(df, ignore_index=True)

    
    df_final = df_final[~df_final.duplicated()]
    return(df_final)

def f_get_filelist(file_name_prefix,month_list, file_search_prefix=FILE_SEARCH_PREFIX):
    file_name_pattern= '*' + file_name_prefix + '*'
    search_list = [ file_search_prefix + str(month) + '/' for month in month_list]
    final_list = simple_search(search_list,file_name_pattern)
    return(final_list)

def load_intomysql(table_name,final_list,engine=MYSQL_ENGINE):
    final_df = f_return_union_df(final_list)
    print(final_df.columns)
    final_df.to_sql(table_name,con=engine,if_exists='replace',index=False)

