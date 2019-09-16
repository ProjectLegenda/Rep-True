# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 16:20:06 2019

@author: lwang9
"""

from DataManager import DataManager
from Novo_Luxi import PopularityRecommender
from rcsys_colleague import ColleagueRcsys
from recommand_tags import recommand
import pandas as pd
from pandas.core.frame import DataFrame
import os
import nndw as nn
import time
from Transformer import Transformer
from utils import timing
iotype = 'db'

def main():
    print("Designed for WeCall Mini Progarm Article RecSys")
    print("------------------------------------------------------")
    print("Step 1: Loading necessary data")

    dm = DataManager()
    status = nn.Dataframefactory("wecall_doctor",iotype=iotype)[["code","status"]]
    status.columns = ["doctorid","status"]
    # 数据读取
    wecall_behavior = dm.get_wecall_behavior  # 行为数据读取
    wecall_content = dm.get_wecall_content_tag  # 文章库读取
    hcp_market_title = dm.get_hcp_market_title  # 读取市场地区数据
    doc_list = dm.get_wecall_doctor  # 读取医生列表
    all_behavior_data = dm.get_all_behavior
    behavior_content_tag = dm.get_behavior_content_tag
    wecall_content_tag = dm.get_wecall_content_tag
    hcp_brand = dm.get_hcp_market_mapping
    content_brand = dm.get_wecall_article_brand
    content_brand = content_brand.rename(columns={'document_id': 'content_id'})
    wecall_url = dm.get_wecall_url

    print("Step 1: Done")
    print("------------------------------------------------------")
    print("Step 2: Processing necessary data")
    # 数据处理
    all_content = wecall_content[['content_id', 'content_title']]  # 文章库有效列
    all_content = all_content.drop_duplicates(['content_id'])  # 文章去重
    wecall_behavior['content_id'] = dm.get_wecall_behavior.content_id.str.split(pat=".", n=1, expand=True)[
        0]  # 行为数据doctorid统一格式 ### may not useful

    # Computes the most popular items 得到文章库的受欢迎程度排序
    behavior_popularity_df = wecall_behavior.groupby(['doctorid', 'content_id'])['strength'].sum(). \
        sort_values(ascending=False).reset_index()
    item_popularity_df = wecall_behavior.groupby(['content_id'])['strength'].sum().sort_values(
        ascending=False).reset_index()

    # 和文章内容合并
    all_content_merge = all_content.merge(item_popularity_df, how="left", on="content_id")
    all_content_merge = all_content_merge.fillna(0)

    all_behavior_merge = all_content.merge(behavior_popularity_df, how="left", on="content_id")
    all_behavior_merge = all_behavior_merge.fillna(0)

    all_behavior_merge = all_behavior_merge.merge(content_brand, how='left', on="content_id")
    popularity_df = all_content_merge.groupby('content_id')['strength'].sum().sort_values(ascending=False).reset_index()
    popularity_df = popularity_df.merge(content_brand, how='left', on="content_id")

    print("Step 2: Done")
    print("------------------------------------------------------")
    print("Step 3: Generating Recommendation by popularity")
    ### Method 3 ---- Popularity Ranking

    start1 = time.time()
    popularity_model = PopularityRecommender(all_behavior_merge, popularity_df)  # 输入
    doctor_list = DataFrame(doc_list)  # 推荐医生的列表
    doctor_list = doctor_list.rename(columns={0: 'doctor_id'})
    doctor_list = doctor_list.merge(hcp_brand, how='left', on='doctor_id')
    method3_final = popularity_model.deliver_final(doctor_list)

    # =doctor_list['doctor_id'], brand_id= doctor_list['brand_id']
    end1 = time.time()
    running_time1 = end1 - start1
    print('time cost : %.5f sec' % running_time1)
    print("Step 3: Done")
    print("------------------------------------------------------")
    print("Step 4: Generating Recommendation by Colleague")
    ### Method 2 ---- Colleague Recommendation
    start2 = time.time()
    cl_rc = ColleagueRcsys(wecall_behavior, hcp_market_title, hcp_brand, content_brand, doc_list, all_content)
    method2_final = cl_rc.delivery_final()
    method2_final = method2_final[['doctor_id', 'content_id', 'strength', 'method']]
    end2 = time.time()
    running_time2 = end2 - start2
    print('time cost : %.5f sec' % running_time2)
    print("Step 4: Done")
    print("------------------------------------------------------")
    print("Step 5: Generating Recommendation by Guess what you Like")
    ### Method 1 ---- guess what you like
    start3 = time.time()
    method1_final = recommand(all_behavior_data,
                              behavior_content_tag,
                              wecall_content_tag,
                              hcp_brand,
                              content_brand,
                              doc_list)
    method1_final = method1_final[['doctor_id', 'content_id', 'strength', 'method']]
    end3 = time.time()
    running_time3 = end3 - start3
    print('time cost : %.5f sec' % running_time3)
    print("Step 5: Done")
    print("------------------------------------------------------")
    print("Step 6: Generating Final Recommendation Result")
    start4 = time.time()
    final_recommend = method1_final.append(method2_final)
    final_recommend_new = final_recommend.groupby(['doctor_id', 'content_id'])['method'].min().reset_index()
    final_recommend_new = final_recommend_new.groupby(['doctor_id', 'method']).head(5)
    final_recommend_2 = final_recommend_new.append(method3_final)
    popularity_df_update = popularity_df[['content_id', 'strength']].drop_duplicates()
    final_output = final_recommend_2.groupby(['doctor_id', 'content_id'])['method'].min().reset_index()
    final_output = final_output.merge(popularity_df_update, how='left', on='content_id')
    # final_with_url = final_output.merge(wecall_url, how='left', on='content_id')
    # print("add url")
    #final_output.to_csv('stage01.csv')
    df1 = final_output[final_output['method'] == 1]
    df2 = final_output[final_output['method'] == 2]
    df3 = final_output[final_output['method'] == 3]
    t = Transformer(df1)
    x1 = t.getDataframe()
    if df2.empty:
        x2 = DataFrame([], columns=['doctor_id', 'xn1', 'content_id', 'method', 'strength'])
    else:
        t.setDataframe(df2)
        x2 = t.getDataframe()
    t.setDataframe(df3)
    x3 = t.getDataframe()

    xf = x3.merge(x2, on=['doctor_id', 'xn1'], how='left').merge(x1, on=['doctor_id', 'xn1'], how='left')
    xf['createtime'] = time.strftime("%m/%d/%Y %H:%M", time.localtime())
    xf = xf.rename(columns={'doctor_id': 'doctorid', 'xn1': 'rec_cnt',
                            'content_id_x': 'm1_id',
                            'content_id': 'm2_id',
                            'content_id_y': 'm3_id'})
    xf1 = xf.merge(wecall_url,
                   how='left',
                   left_on='m1_id',
                   right_on='content_id').rename(columns={'content_title': 'method1',
                                                          'url': 'url_1'
                                                          })
    xf2 = xf1.merge(wecall_url,
                    how='left',
                    left_on='m2_id',
                    right_on='content_id').rename(columns={'content_title': 'method2',
                                                           'url': 'url_2'
                                                           })
    xf3 = xf2.merge(wecall_url,
                    how='left',
                    left_on='m3_id',
                    right_on='content_id').rename(columns={'content_title': 'method3',
                                                           'url': 'url_3'
                                                           })
    xf_final = xf3[['doctorid', 'rec_cnt',
                     'method1','m1_id','method2','m2_id',
                       'method3','m3_id','url_1','url_2','url_3',
                    'createtime']]
    xf_final["method1"]= xf_final["method1"].str.replace(',', '，', regex=False)
    xf_final["method2"]= xf_final["method2"].str.replace(',', '，', regex=False)   
    xf_final["method3"]= xf_final["method3"].str.replace(',', '，', regex=False)
    end4 = time.time()
    running_time4 = end4 - start4
    print('time cost : %.5f sec' % running_time4)
    print("Step 6: Done")
    #print("------------------------------------------------------")
    #print("Writing Table to Hive")
    #nn.write_table(xf_final,"rec_out",iotype=iotype)
    xf_final['Index'] = xf_final.index
    xf_final = xf_final.merge(status,how="left",on="doctorid")
    print("------------------------------------------------------")
    print('Writing Table to MySql')
    nn.write_mysql_table(xf_final,'rec_out','mysql_con')
    print("All Done")
    return (1)


