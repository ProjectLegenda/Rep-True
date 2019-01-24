#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ----------------
# File: recommendation.py
# Project: Rec
# Created Date: Tuesday, January 22nd 2019, 11:07:27 am
# Author: Yubo HE
# ----------------
# Last Modified: Wednesday, 23rd January 2019 9:57:19 am
# Modified By: Yubo HE (yubo.he@cn.imshealth.com>) 
# -----------------
# Copyright (c) 2019 IQVIA.Inc
# All Rights Reserved
__project__ = 'Content Rec SyS'
__author__ = 'Yubo'

import numpy as np
import pandas as pd

import jieba
import re
import math
import scipy
from functools import wraps
from time import time

#from tqdm import tqdm

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'

import nndw as nn

iotype = 'db'

# utils
############################################


def smooth_user_preference(x):
    return math.log(1+x, 2)


def create_dict_stop():
    """
    Load external dictionary and stop words
    """
    print("Loading Dictionary and Stopwords")
    global stopWord
    dic_path = '../essentials/'
    #dic = pd.read_csv(dic_path + "mappingWordFinal.txt",
    #                  encoding='utf-8', engine='python', sep='\r\n')
    dic = nn.Dataframefactory("mappingword",sep = '\r\n',iotype = iotype)
    word = dic.word.tolist()
    #
    #stopWord = pd.read_csv(dic_path + 'StopWordFinal.txt',
    #                       encoding='utf-8', engine='python', sep='\r\n')
    stopWord = nn.Dataframefactory("stopword",iotype = iotype)
    stopWord = stopWord.word.tolist()
    stopWord.append(" ")
    jieba.re_han_default = re.compile(
        r'([\u0020\u4e00-\u9fa5a-zA-Z0-9+#&._%/”/“/"/β/α/-]+)', re.UNICODE)
    frequnecy = 100000000000000000000000
    # Add words to dictionary
    for words in word:
        jieba.add_word(words, freq=frequnecy)
    print("Finished Dic Loading")


def segment(text):
    sentence = text.replace('\n', '').replace('\u3000', '').replace(
        '\u00A0', '').replace('\xa0', '').replace('&quot', '')
    sentence = re.sub('\s+', ' ', sentence)
    segs = jieba.cut(sentence, cut_all=False)
    outList = [seg for seg in segs if
               seg not in stopWord and not re.match('^[0-9|.|%]*$', seg) and not re.match('\s*[\.|\-]\s*', seg)]
    outStr = ' '.join(outList)
    return outStr

################################################
# data preprocessing
def content_lib_processing(content_lib_pat, content_lib_hcp):
    content_lib_hcp["source"] = "D"
    content_lib_pat["source"] = "P"

    content_lib_hcp["title"] = content_lib_hcp["title"].apply(
        lambda x: x.strip())
    content_lib_pat["title"] = content_lib_pat["title"].apply(
        lambda x: x.strip())

    print("Patient Content Lbirary Cnt:{}\nHCP Library content Cnt:{}".format(
        content_lib_pat.shape[0], content_lib_hcp.shape[0]))

    print("removing dupilicated content")
    content_lib_pat.drop_duplicates(
        subset=["title"], keep="last", inplace=True)
    content_lib_hcp.drop_duplicates(
        subset=["title"], keep="last", inplace=True)

    print("Dropping Invalid Contents")
    content_lib_pat.dropna(subset=["content"], inplace=True)
    content_lib_hcp.dropna(subset=["content"], inplace=True)

    content_lib_cols = ["title", "content", "source", "publish_date"]
    content_lib = pd.concat([content_lib_hcp[content_lib_cols],
                             content_lib_pat[content_lib_cols]], ignore_index=True)
    content_lib.drop_duplicates(subset=["title"], inplace=True, keep="last")
    content_lib.reset_index(drop=True, inplace=True)
    print("Content-Lib: Total Cnt: {}".format(content_lib.shape[0]))
    global item_ids
    item_ids = content_lib["title"].tolist()
    return content_lib


def corpus_process(content_lib):
    content_lib["corpus"] = content_lib["title"] + " " + content_lib["content"]
    corpus_list = content_lib["corpus"].apply(segment).tolist()
    return corpus_list


def interaction_processing(behavior_raw):
    behavior_1 = behavior_raw

    def behavior_process(x): return 1 if x in [
        "点击点赞", "点击收藏", "点击分享", "分享"] else 0
    behavior_1["thumbs_up"] = behavior_1["thumbs_up"].apply(behavior_process)
    behavior_1["collected"] = behavior_1["collected"].apply(behavior_process)
    behavior_1["share"] = behavior_1["share"].apply(behavior_process)
    behavior_1["strength"] = behavior_1["thumbs_up"] * 1.5 + \
        behavior_1["share"] * 2 + behavior_1["collected"] * 2 + 1
    behavior_cols = ['hcp_openid_u_2', 'content_title', 'platform', 'strength']
    behavior_2 = behavior_1[behavior_cols]
    behavior_2.reset_index(drop=True, inplace=True)
    behavior_all_indexed = behavior_2.set_index("hcp_openid_u_2")
    return behavior_all_indexed


def gen_tfidf_matrix(corpus_list):
    vectorizer = TfidfVectorizer(
        min_df=0.003,
        max_df=0.5,
        max_features=5000
    )
    global tfidf_matrix
    tfidf_matrix = vectorizer.fit_transform(corpus_list)


def split_tfidf_matrix(content_lib):
    pat_content_index = content_lib[content_lib["source"]
                                    == "P"].index.tolist()
    pat_content_title = content_lib[content_lib["source"]
                                    == "P"]["title"].tolist()
    pat_tfidf_matrix = tfidf_matrix[pat_content_index]
    hcp_content_index = content_lib[content_lib["source"]
                                    == "D"].index.tolist()
    hcp_content_title = content_lib[content_lib["source"]
                                    == "D"]["title"].tolist()
    hcp_tfidf_matrix = tfidf_matrix[hcp_content_index]
    return pat_tfidf_matrix, hcp_tfidf_matrix, pat_content_title, hcp_content_title


def get_ranked_content_title(behavior_all_indexed, content_lib):
    content_rank = behavior_all_indexed.groupby("content_title").size(
    ).sort_values(ascending=False).to_frame("size").reset_index()
    most_viewed = content_rank[content_rank.content_title.isin(
        content_lib["title"])].reset_index(drop=True)
    most_viewed = most_viewed.merge(
        content_lib[["title", "source"]], left_on="content_title", right_on="title")
    most_viewed.drop(columns="title", axis=1, inplace=True)
    return most_viewed


def get_item_profile(item_title):
    idx = item_ids.index(item_title)
    item_profile = tfidf_matrix[idx:idx+1]
    return item_profile


def get_item_profiles(ids):
    if not isinstance(ids, pd.Series):
        ids = [ids]
    item_profiles_list = [get_item_profile(x) for x in ids]
    item_profiles = scipy.sparse.vstack(item_profiles_list)
    return item_profiles


def build_users_profile(valid_behavior):
    user_item_profiles = get_item_profiles(valid_behavior['content_title'])
    user_item_strengths = np.array(valid_behavior['strength']).reshape(-1, 1)
    user_item_strengths_weighted_avg = np.sum(user_item_profiles.multiply(
        user_item_strengths), axis=0) / np.sum(user_item_strengths)
    user_profile_norm = normalize(user_item_strengths_weighted_avg)
    return user_profile_norm


def generate_usr_rec(usr_id, behavior_all_indexed, content_lib, tfidf_matrix_P, P_title, tfidf_matrix_D, D_title, most_viewed, num=3):

    recommendations_df = pd.DataFrame(
        columns=["openid", "rec_title", "rec_method"])

    try:
        personal_interaction = behavior_all_indexed.loc[[usr_id]]
    except KeyError:

        print("Invalid Open ID, Unable to find \"{}\" in Dataset! \n".format(usr_id))
        recommendations_df["rec_title"] = most_viewed["content_title"].head(6)
        recommendations_df["openid"] = usr_id
        recommendations_df["rec_method"] = "Popularity"

        return(recommendations_df)

    personal_interaction_valid = personal_interaction[personal_interaction["content_title"].isin(
        content_lib["title"])]
    valid_behavior = personal_interaction_valid.groupby(
        ["content_title"])["strength"].sum().apply(smooth_user_preference).reset_index()

    valid_record = valid_behavior.shape[0]
    status = personal_interaction["platform"].values[0]
    items_to_ignore = valid_behavior.content_title.tolist()

    if valid_record >= num:
        #print("valid User")
        user_profile_norm = build_users_profile(valid_behavior)

        if status == '1':
            cosine_similarities = cosine_similarity(
                user_profile_norm, tfidf_matrix_P)
            title_list = P_title
            num_to_rec = 6
        elif status == '2':
            cosine_similarities = cosine_similarity(
                user_profile_norm, tfidf_matrix_D)
            title_list = D_title
            num_to_rec = 10
        else:
            print(
                "User: '{}' is neither a patient or a hcp, please check in database".format(usr_id))

        similar_indices = cosine_similarities.argsort().flatten()[-100:]
        similar_items = sorted([(title_list[i], cosine_similarities[0, i])
                                for i in similar_indices], key=lambda x: -x[1])

        similar_items_filtered = list(
            filter(lambda x: x[0] not in items_to_ignore, similar_items))
        recTitle = [i[0] for i in similar_items_filtered][:num_to_rec]
        recommendations_df["rec_title"] = recTitle
        recommendations_df["rec_method"] = "content_based"
        recommendations_df["openid"] = usr_id
    else:
        #print("not enough usr")
        if status == '1':
            recommend_list = most_viewed[most_viewed['source'] == 'P']
            recommendations_df["rec_title"] = recommend_list[~recommend_list["content_title"].isin(items_to_ignore)]["content_title"] \
                .head(6) \
                .reset_index(drop=True)
        elif status == '2':
            recommend_list = most_viewed[most_viewed['source'] == 'D']
            recommendations_df["rec_title"] = recommend_list[~recommend_list["content_title"].isin(items_to_ignore)]["content_title"] \
                .head(10) \
                .reset_index(drop=True)
        else:
            print(
                "User: '{}' is neither a patient or a hcp, please check in database".format(usr_id))
        recommendations_df["rec_method"] = "Popularity"
        recommendations_df["openid"] = usr_id
    return recommendations_df


def load():
    print("Designed for Novo4PE: Content Rec Sys")
    print("------------------------------------------------------")
    print("Step 1: loading necessary data")
    #behavior_raw = pd.read_csv(
    #    '../essentials/itangyi_wechat_hcp_content_view')
    behavior_raw = nn.Dataframefactory('wechat',iotype = iotype)
    
    #content_lib_pat = pd.read_csv(
    #    "../essentials/idiabetes_patient_history_article")
    global content_lib_pat 
    content_lib_pat = nn.Dataframefactory('pat_articles',iotype = iotype)
    
    #content_lib_hcp = pd.read_csv(
    #    "../essentials/idiabetes_hcp_history_article.csv")
    global content_lib_hcp 
    content_lib_hcp = nn.Dataframefactory('hcp_articles',iotype = iotype)
    print("Step 1: Done")
    print("------------------------------------------------------")
    print("Step 2: Creating dictionary")
    create_dict_stop()
    print("Step 2: Done")
    print("------------------------------------------------------")
    print("Step 3: Processing Content_Lib and Behavior Data")
    global content_lib
    content_lib = content_lib_processing(
        content_lib_pat, content_lib_hcp)
    global behavior_all_indexed 
    behavior_all_indexed = interaction_processing(behavior_raw)
    print("Step 3: Done")
    print("------------------------------------------------------")
    print("Step 4: Caculating Cotent Attribute")
    global corpus_list 
    corpus_list = corpus_process(content_lib)
    gen_tfidf_matrix(corpus_list)

    global pat_tfidf_matrix, hcp_tfidf_matrix, pat_content_title, hcp_content_title 
    pat_tfidf_matrix, hcp_tfidf_matrix, pat_content_title, hcp_content_title = split_tfidf_matrix(
        content_lib)
    global most_viewed 
    most_viewed = get_ranked_content_title(behavior_all_indexed, content_lib)

    print("Step 4: Done")
    print("------------------------------------------------------")
    print("Step 5: Generating Personal Rec List")
    global uniq_usr 
    uniq_usr = behavior_raw.hcp_openid_u_2.unique()

    # for usr_id in tqdm(uniq_usr):
    #     rec = generate_usr_rec(usr_id, behavior_all_indexed, content_lib, pat_tfidf_matrix,
    #                            pat_content_title, hcp_tfidf_matrix, hcp_content_title, most_viewed)

    print("Step 5: Done")
    print("------------------------------------------------------")
    print("LOAD COMPLETE")

def rec(patient):
    
    a = time()
    rec = generate_usr_rec(patient, behavior_all_indexed, content_lib, pat_tfidf_matrix,
                                pat_content_title, hcp_tfidf_matrix, hcp_content_title, most_viewed)
    b = time()
    print('Elapse:',b-a,' seconds')
    return(rec.T.to_dict()) 


def mainloop():
    while True:
        id_ = input('----> please input openid:\n') 
        if id_ == 'exit':
            break
        elif id_ == '':
            continue
        else:
            print(rec(id_))




