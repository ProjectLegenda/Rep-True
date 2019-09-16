# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 16:20:31 2019

@author: yxiong
"""
from utils import timing
import pandas as pd
import os
def recommand(behavior_data,behavior_content_tags,wecall_content_tags,hcp_market_mapping,wecall_article_brand,wecall_doctor):
    hcp_market_mapping = pd.DataFrame(hcp_market_mapping)
    hcp_market_mapping = hcp_market_mapping.rename(columns={'doctor_id':'doctorid'})
    wecall_article_brand = pd.DataFrame(wecall_article_brand)
    wecall_article_brand = wecall_article_brand.rename(columns={'document_id':'content_id'})
    
    ##给doctor看过的文章匹配标签
    behavior=pd.merge(behavior_data,behavior_content_tags,on=['content_id','module_2'],how='left')
    # 计算每个医生tag的strength
    behavior['strength']=pd.to_numeric(behavior['strength'])
    grouped=behavior.groupby(['doctorid','func_lb']).sum()
    idx = grouped.groupby(['doctorid'])['strength'].transform(max) == grouped['strength']
    preference=pd.DataFrame(grouped[idx])
    preference.reset_index(inplace=True)
    preference=preference.drop(['strength', 'num_lb'], axis=1)
    #给doctor匹配brand_id
    preference_marketing=pd.merge(preference, hcp_market_mapping, on=['doctorid'], how='left')
    preference_marketing.dropna(axis=0, how='any', inplace=True)
    ### 和behavior匹配，添加文章strength by doctorid
    wecall_content_tags=pd.DataFrame(wecall_content_tags,dtype='str') 
    wecall_cal=pd.merge(wecall_content_tags, behavior_data, on=['content_id'],how='left')
    wecall_cal['strength']=wecall_cal['strength'].fillna(0)
    #计算每篇文章strength总和
    wecall_content_pop=wecall_cal.groupby(['content_id']).sum()
    wecall_content_pop.reset_index(inplace=True)
    wecall_content_tags_brand=pd.merge(wecall_content_tags,wecall_article_brand,on=['content_id'], how='left')
    wecall_content_tags_brand = wecall_content_tags_brand[['content_id', 'content_title',  'func_lb',  'brand_id']]
    ####匹配doctor和推荐文章的brand_id
    rec=pd.merge(preference_marketing,wecall_content_tags_brand,on=['func_lb','brand_id'], how='left')
    ##添加推荐文章的strength
    rec = rec.dropna()
    rec_pop=pd.merge(rec,wecall_content_pop,on=['content_id'], how='left')
    ##处理表格,从推荐中去除已经看过的文章
    rec_pop=pd.DataFrame(rec_pop,dtype='str')
    behavior_data=pd.DataFrame(behavior_data,dtype='str')
    rec_pop['doctorid_content']=rec_pop[['doctorid','content_id']].apply(lambda x:'_'.join(x),axis=1)
    behavior_data['doctorid_content']=behavior_data[['doctorid','content_id']].apply(lambda x:'_'.join(x),axis=1)
    rec=rec_pop[~rec_pop['doctorid_content'].isin(behavior_data['doctorid_content'])]
    rec['content_id']=pd.to_numeric(rec['content_id'])
    rec['strength']=pd.to_numeric(rec['strength'])
    ##取前十
    rec2 = rec.set_index(['content_id', 'content_title', 'brand_id']).groupby('doctorid')['strength'].nlargest(5).reset_index()
    if 'content_id' not in rec2.columns:
        rec2['content_id'] = []
    if 'content_title' not in rec2.columns:
        rec2['content_title'] = []
    if 'brand_id' not in rec2.columns:
        rec2['brand_id'] = []

    df = pd.DataFrame(wecall_doctor, columns=['doctorid'])
    df = pd.merge(left=df, right=rec2, how='inner', on=['doctorid'])
    #df['content_id'] = df.content_id.astype(str).str.split(pat=".", n=1, expand=True)[0]
    df = df.rename(columns={'doctorid':'doctor_id'})
    df=df.drop(['content_title','brand_id'],axis=1)
    df['method'] = 1
    df['content_id'] = df['content_id'].astype(int).astype(str)
    return df

