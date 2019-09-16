# -*- coding: utf-8 -*-

"""
Created on Tue May 28 16:26:38 2019

@author: Luxi Wang
"""
import pandas as pd
import numpy as np
import os
from utils import timing

class PopularityRecommender:
    '''
    文章热度推荐策略
    如需调用文章库热度排序，可以用 popularity_df_return函数 如：
    popularity_model = PopularityRecommender(all_content_merge, all_behavior_merge)
    popularity_model.popularity_df_return()

    如需输出每个医生的15篇热度推荐文章（去掉已读）：
    popularity_model.recommend_items(user_id = '1-G9XLX0')

    '''

    MODEL_NAME = 'Popularity'

    def __init__(self, all_behavior_merge, popularity_df):
        self.all_behavior_merge = all_behavior_merge
        self.popularity_df = popularity_df

    def get_model_name(self):
        return self.MODEL_NAME

    # Computes the most popular items 得到文章库的受欢迎程度排序
    def popularity_df_return(self):
        print('-------------------------------------------------------------')
        print('The most popular items are computed')
        return self.popularity_df

    def get_items_interacted(self, person_id):
        # 返回每人已阅读的文章list
        all_behavior_merge_indexed_df = self.all_behavior_merge.set_index('doctorid')
        if person_id in self.all_behavior_merge['doctorid']:
            behavior_items = all_behavior_merge_indexed_df.loc[person_id]['content_id']
        else:
            behavior_items = []
        return set(behavior_items if type(behavior_items) == pd.Series else behavior_items)

    def recommend_items(self, user_id, brand_id, items_to_ignore=[], topn=15, verbose=False):
        # Recommend the more popular items that the user hasn't seen yet.
        #abc = self.all_behavior_merge['doctorid']
        all_behavior_merge1 = self.all_behavior_merge[self.all_behavior_merge.brand_id == brand_id]
       # if user_id in self.all_behavior_merge['doctorid'].values:  # 如果是给已有记录的用户推荐
        items_to_ignore = self.get_items_interacted(user_id)
        recommendations_df = all_behavior_merge1[~all_behavior_merge1['content_id'].isin(items_to_ignore)] \
                .sort_values('strength', ascending=False) \
                .head(topn)
        recommendations_df = recommendations_df[['content_id', 'strength']]
        return recommendations_df

    def behavior_recommend(self, doctor_list):
        doctor_list_1 = self.all_behavior_merge.merge(doctor_list, how='inner', left_on='doctorid', right_on='doctor_id')
        doctor_list_1 = doctor_list_1[['doctor_id','brand_id_y']].drop_duplicates().reset_index(drop=True)
        doctor_list_1 = doctor_list_1.rename(columns={'brand_id_y':'brand_id'})
        final = []

        for i in range(len(doctor_list_1)):
            individual_recommend = self.recommend_items(user_id=doctor_list_1.iloc[i]['doctor_id'], brand_id=doctor_list_1.iloc[i]['brand_id'])
            ##print(individual_recommend)
            individual_recommend["doctor_id"] = doctor_list_1.loc[i]['doctor_id']            
            individual_recommend1 = individual_recommend.to_dict('records')
            final = final + individual_recommend1
        final = pd.DataFrame(final, columns=["doctor_id", "content_id",'strength'])
        final['method'] = 3
        return final

    def no_behavior_recommend(self, doctor_list):
        doctor_list_2 = self.all_behavior_merge.merge(doctor_list, how ='outer', left_on = 'doctorid', right_on='doctor_id', indicator=True)
        doctor_list_2 = doctor_list_2[doctor_list_2['_merge'] == 'right_only']
        doctor_list_2 = doctor_list_2[['doctor_id', 'brand_id_y']]
        doctor_list_2 = doctor_list_2.rename(columns={'brand_id_y':'brand_id'})
        popularity_df2 = pd.DataFrame()
        for i in doctor_list.brand_id.unique():
            popularity_df1 =self.popularity_df[self.popularity_df.brand_id == i].head(15)
            popularity_df2 = popularity_df2.append(popularity_df1)
        final_2 = doctor_list_2.merge(popularity_df2, how = 'left', on='brand_id')
        final_2 = final_2[["doctor_id", "content_id",'strength']]
        final_2['method'] = 3
        return final_2

    def deliver_final(self, doctor_list):
        behavior = self.behavior_recommend(doctor_list)
        no_behavior = self.no_behavior_recommend(doctor_list)
        final = behavior.append(no_behavior)

        return final
