#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project  : EDA_RECSYS
# @FileName : eda_rec.py
# @Created  : 01 Jul 2019 12:44 PM
# @Author   : Yanxin Y
"""
from flask import Flask
import pymysql
import pandas as pd
import numpy as np
import json
import sqlalchemy
import random
import config

from flask import request

app = Flask(__name__)


'''init'''

##engine=sqlalchemy.create_engine('mysql+pymysql://mysql_usr:password@localhost:3306/eda_test')
engine = config.engine
'''
eda = pd.read_sql_table(table_name='eda_tag', con=engine)
content_tag = pd.read_sql_table('content_tag_new', con=engine)
content_brand = pd.read_sql_table('content_brand', con=engine)
content_strength_viewcnts = pd.read_sql('content_strength_viewcnts', con=engine)  # sqlp
eda_brand = pd.read_sql('eda_brand', con=engine)
'''

@app.route('/eda_rec',methods=['GET','POST'])
def rec_list():

    visiting_id = request.args['visitingid']

    content_strength_viewcnts = pd.read_sql('content_strength_viewcnts', con=engine)  # sqlp
    
    content_filtered = content_strength_viewcnts[content_strength_viewcnts['content_id'].isin([60,63,49])].reset_index()
    content_filtered['rec_articles'] = content_filtered['content_title']
    content_id_list = content_filtered['content_id'].astype(int).tolist()
    title_list = content_filtered['content_title'].tolist()

    lt = []
   
    lt = [{'content_id':content_id_list[i],'rec_articles':title_list[i]} for i in range(0,len(title_list))]
    
    ########行为数据与eda数据merge（根据page_path和eda_id）
    sql = "select * from see_behaviour_log where visiting_id ='{}'".format(visiting_id)
    vis_beh = pd.read_sql_query(sql, engine)
    if len(vis_beh) == 0:
        return(json.dumps({"visiting_id": visiting_id,'article_list':lt},ensure_ascii=False))



    eda = pd.read_sql_table(table_name='eda_tag', con=engine)
    content_tag = pd.read_sql_table('content_tag', con=engine)
    content_brand = pd.read_sql_table('content_brand', con=engine)
    eda_brand = pd.read_sql('eda_brand', con=engine)
    vis_beh = vis_beh[['id', 'user_id', 'page_path', 'page_title', 'visiting_id', 'data_id']]
    beh_merge1 = pd.merge(vis_beh, eda, left_on=['page_path', 'data_id'], right_on=['url', 'eda_id'], how='left')

    if beh_merge1['tags'].isnull().all() == True:
        list_final = []
    else:
        beh_merge1 = beh_merge1.dropna(subset=['tags'])

        ########标签处理
        beh_merge1['tags'] = beh_merge1['tags'].str.split("|")
        beh_merge1 = beh_merge1.drop(['page_path', 'data_id'], axis=1)
        beh_tag = beh_merge1.tags.apply(pd.Series).merge(beh_merge1, left_index=True, right_index=True).drop(["tags"],
                                                                                                            axis=1).melt(
            id_vars=['id', 'user_id', 'page_title', 'visiting_id', 'eda_id', 'url', 'sheet'], value_name="tags").drop(
            "variable", axis=1).dropna(subset=["tags"])

        #######标签计算 排序
        tag_num = beh_tag.groupby(['visiting_id', 'tags']).size().to_frame('per')
        percentage = (tag_num / tag_num.groupby('visiting_id').sum()).reset_index()
        percentage_rank = percentage.groupby(['visiting_id']).apply(
            lambda x: x.sort_values(['per'], ascending=False)).reset_index(drop=True)
        percentage_rank["ac"] = percentage_rank['per'].cumsum()
        percentage_rank
        ######根据累积比例 输出相应的data
        for index, row in percentage_rank.iterrows():
            if row["ac"] > 0.6:
                # rint(index)
                df = percentage_rank.loc[0:index]
                break

        # df
        #######将df与添加eda tag后的表进行merge
        df_join = pd.merge(df, beh_tag, left_on=['visiting_id', 'tags'], right_on=['visiting_id', 'tags'], how='left')
        df_join = df_join.drop_duplicates(subset=['visiting_id', 'tags', 'url'], keep='first', inplace=False)
        df_mer = pd.merge(df_join, eda_brand, left_on=['eda_id'], right_on=['eda_id'], how='left')  # 添加brand id
        #######文章库三张表进行merge
        content_merge = pd.merge(content_tag, content_brand, on='content_id', how='left')
        content_merge = content_merge.drop(['content_title'], axis=1)
        con_merge = pd.merge(content_merge, content_strength_viewcnts, on='content_id', how='left')
        con_merge = con_merge.drop_duplicates().reset_index(drop=True)
        #######文章库与处理好的行为数据进行merge
        df_final = pd.merge(df_mer, con_merge, left_on=['tags', 'brand_id'], right_on=['lv2_lb', 'brand_id'], how='left')
        #######con_merge筛选999的文章 热度排序
        con_merge_999 = con_merge[con_merge['brand_id'] == '999'].sort_values(['strength'], ascending=False)
        # # con_merge_999.sort_values(['strength'],ascending=False)
        ######计算每一条匹配到的文章个数
        df_drop = df_final[['tags', 'brand_id', 'content_id']].groupby(['tags', 'brand_id'])[
            'content_id'].count().to_frame('cnt').reset_index()
        ######补缺 finally
        if df_final['content_id'].isnull().all() == True:
            #     df_list = df_final[['brand_id']==999][0]
            list_final = con_merge_999.head(3)['content_id'].astype(int).tolist()
        else:
            df_list = df_final.dropna(subset=["content_id"])
            if len(df_list) < 3:
                list_999 = con_merge_999[~con_merge_999.content_id.isin(df_list['content_id'])].head(3 - len(df_list))[
                    'content_id'].astype(int).tolist()
                list_1 = df_list['content_id'].astype(int).tolist()
                list_final = list_999 + list_1
            else:
                list_sort = df_list.sort_values(['strength'], ascending=False).head(3)
                list_final = list_sort['content_id'].astype(int).tolist()

    title = content_strength_viewcnts[content_strength_viewcnts.content_id.isin(list_final)].sort_values(by="strength",
                                                                                                         ascending=False).content_title.tolist()

    ll = [{'content_id':list_final[i],'rec_articles':title[i]} for i in range(0,len(title))] + lt 
    ll = ll[0:3]

    data = {"visiting_id": visiting_id,'article_list':ll}

    js = json.dumps(data, ensure_ascii=False)

    return (js)

    
