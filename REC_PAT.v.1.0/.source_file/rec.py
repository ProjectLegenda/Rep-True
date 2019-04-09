#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__project__ = 'Content Rec SyS'
__author__ = 'Yubo'

import numpy as np
import pandas as pd

import json
import random

import jieba
import re
import math
import scipy
from time import time
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'

import nndw as nn

iotype = 'db'


# 创建字典部分 以及切词模块
def createDictStop():
    """
    Load external dictionary and stop words
    """
    print("Loading Dictionary and Stopwords")
    global stopWord
    
    dic = nn.Dataframefactory("mappingword",sep = '\r\n',iotype=iotype)    
    stopWord = nn.Dataframefactory("stopword",sep = '\r\n',iotype=iotype)
    
    word = dic.word.tolist()   
    stopWord = stopWord.word.tolist()
    jieba.re_han_default =re.compile(r'([\u0020\u4e00-\u9fa5a-zA-Z0-9+#&._%/”/“/"/β/α/-]+)', re.UNICODE)
    
    frequnecy = 1000000000000000000000
    # Add words to dictionary
    for words in word:
        jieba.add_word(words,frequnecy)
    print("Finished Dic Loading")


def segment(text):
    """
    return string
    """
    sentence = text.replace('\n', '').replace('\u3000', '').replace(
        '\u00A0', '').replace('\xa0', '').replace('&quot', '')
    sentence = re.sub('\s+', ' ', sentence)
    segs = jieba.cut(sentence, cut_all=False)
    outList = [seg for seg in segs if
               seg not in stopWord and not re.match('^[0-9|.|%]*$', seg) and not re.match('\s*[\.|\-]\s*', seg)]
    outStr = ' '.join(outList)
    return outStr


def tokenize(text):
    """
    return list
    """
    sentence = text.replace('\n', '').replace('\u3000', '').replace(
        '\u00A0', '').replace('\xa0', '').replace('&quot', '')
    sentence = re.sub('\s+', ' ', sentence)
    segs = jieba.cut(sentence, cut_all=False)
    outList = [seg for seg in segs if
               seg not in stopWord and not re.match('^[0-9|.|%]*$', seg) and not re.match('\s*[\.|\-]\s*', seg)]

    return outList

# 打标签用的！！！
def labelIt(tokens,keyTable):
    lv2Lb = []
    for token in tokens:
        for index, row in keyTable.iterrows():
            if token in row['tag_similar_word']:
                lv2Lb.append(row['tag_name_lv2'])
    lv2Lb= list(set(lv2Lb))
    lv2Lb = [ x for x in lv2Lb if str(x) != 'nan']
    return lv2Lb

def filterComplication(lv2Label):
    diabetes = ['糖尿病','2型糖尿病']
    complication = ['心脑血管相关',
                    '血压相关',
                    '血脂相关',
                    '糖尿病足相关',
                    '眼病相关',
                    '肾脏相关',
                    '急性/严重并发症',
                    '肝脏相关',
                    '呼吸系统相关',
                    '神经病变相关',
                    '认知相关',
                    '风湿免疫性相关',
                    '消化道相关',
                    '骨骼肌肉相关',
                    '皮肤相关',
                    '精神/心理相关',
                    '肿瘤相关']

    for word in diabetes:
        if word in lv2Label:
            lv2Label.remove(word)
    for word in complication:
        if (word in lv2Label) and ('并发症/合并症') in lv2Label:
                lv2Label.remove('并发症/合并症')
    return lv2Label


def mappingCbind(tagSimilarWords, tag):
    """
    create mapping file
    """

    # Cut tags into different levels
    lv2Tags = tag[(tag.tag_class == "内容标签") & (tag.tag_level == "2")]
    lv1Tags = tag[(tag.tag_class == "内容标签") & (tag.tag_level == "1")]
    hcpTags = tag[tag.tag_class == "病人标签"]

    # Group by lv2 tag and add the similar words into a list
    simiList = tagSimilarWords.groupby(["tag_id", "tag_name"])["tag_similar_word"].apply(list).to_frame().reset_index()

    # Merge similar words and lv2 tags
    simiLv2 = pd.merge(simiList, lv2Tags, how="left", left_on="tag_id",
                       right_on="tag_id", suffixes=("_simi", "_lv2"))

    # Merge lv2 tags and lv1 tags
    lv2Lv1 = pd.merge(simiLv2[["tag_similar_word", "tag_name_lv2", "parent_tag_id"]], lv1Tags,
                  how="left", left_on="parent_tag_id", right_on="tag_id", suffixes=("_lv2", "_lv1"))

    # Merge lv1 tags and hcp tags
    lv1Hcp = pd.merge(lv2Lv1[["tag_similar_word", "tag_name_lv2", "tag_name", "parent_tag_id_lv1"]], hcpTags,
                  how="left", left_on="parent_tag_id_lv1", right_on="tag_id", suffixes=("_lv1", "_pat"))

    # Re-adjust into four columns
    mapping = lv1Hcp[["tag_similar_word", "tag_name_lv2", "tag_name_lv1", "tag_name_pat"]]

    return mapping


# 对文章库做处理
def content_lib_processing(content_raw_df):
    """
    lib will be dataframe
    raw_lib: used in tfidf caculation
    """
    raw_lib = content_raw_df.copy()
    raw_lib["title"] = raw_lib["title"].apply(lambda x: x.strip())
    raw_lib.drop_duplicates(subset=["title"], keep="last", inplace=True)
    all_content = raw_lib.reset_index(drop=True)
    raw_lib.dropna(subset=["content"], inplace=True)
    raw_lib.reset_index(drop=True, inplace=True)
    print("Content_Lib: Total Cnt: {}".format(raw_lib.shape[0]))
    global item_ids
    item_ids = raw_lib["title"].tolist()
    return raw_lib, all_content


# 对行为数据进行处理
def interaction_process(behavior_raw):
    behavior_df = behavior_raw.copy()
    behavior_process = lambda x: 1 if x in [
        "点击点赞", "点击收藏", "点击分享", "分享"] else 0
    behavior_df["thumbs_up"] = behavior_df["thumbs_up"].apply(behavior_process)
    behavior_df["collected"] = behavior_df["collected"].apply(behavior_process)
    behavior_df["share"] = behavior_df["share"].apply(behavior_process)
    behavior_df["strength"] = behavior_df["thumbs_up"] * 1.5 + \
        behavior_df["share"] * 2 + behavior_df["collected"] * 2 + 1
    cols = ['hcp_openid_u_2', 'content_title', 'platform', 'strength']
    behavior = behavior_df[cols]
    behavior.reset_index(drop=True, inplace=True)
    behavior_all_indexed = behavior.set_index("hcp_openid_u_2")
    return behavior_all_indexed


# 利用行为数据以及文章库 得到文章库的受欢迎程度排序
def get_ranked_content_title(behavior_all_indexed,all_content):
    content_rank = behavior_all_indexed.groupby("content_title").size(
        ).sort_values(ascending=False).to_frame("size").reset_index()
    most_viewed = content_rank[content_rank.content_title.isin(
        all_content["title"])].reset_index(drop=True)
    most_viewed.rename(columns={"content_title":"title"},inplace=True)
    all_title = all_content[["title"]]
    popularity = all_title.merge(most_viewed,on="title",how="outer")
    popularity.fillna(0,inplace=True)
    popularity.sort_values(by=["size"],ascending=False,inplace=True)
    popularity.reset_index(drop=True,inplace=True)
    return popularity


# tfidf相关模块
def corpus_process(content_lib):
    content_lib["corpus"] = content_lib["title"] + " " + content_lib["content"]
    corpus_list = content_lib["corpus"].apply(segment).tolist()
    return corpus_list

def gen_tfidf_matrix(corpus_list):
    vectorizer = TfidfVectorizer(
        min_df=0.003,
        max_df=0.5,
        max_features=5000
    )
    global tfidf_matrix
    tfidf_matrix = vectorizer.fit_transform(corpus_list)


# 建立个人兴趣偏好vector
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


# 其他工具
def smooth_user_preference(x):
    return math.log(1+x, 2)


def create_var(labels, ziplist):
    return pd.Series(map(lambda x: 1 if x in labels else 0, ziplist))


#################################################
#患者类型定义模块
def patient_classification(df):
    # 所有患者
    #patient_flag = 1 

    # “未诊断”的患者
    not_diagnosed = 1 if df["q1_answer"] == "b" else 0
    
    # “未诊断”及“新诊断1年以内”的糖尿病患者
    not_diagnosed_within_one_year_dia = 1 if df["q1_answer"] =="b" or df["q3_answer"]=="a" or df["q3_answer"] =="b" else 0
    
    # 所有女性患者中年龄在“20-45”岁，以及“妊娠糖尿病”患者
    female_20_45_gestational = 1 if (df["gender"] == "female" and df["age"]<= 45 and df["age"] >= 20) or df["diabetes_type"] == "妊娠糖尿病" else 0
    
    # “1型糖尿病患者”
    type_1 = 1 if df["diabetes_type"] == "1型糖尿病" else 0
    
    # 所有55岁以上患者
    above_55 = 1 if df["age"] >= 55 else 0
    
    # 所有20岁以下患者
    under_20 = 1 if df["age"] <= 20 else 0
    
    # 所有“特殊类型糖尿病患者“
    type_sp = 1 if df["diabetes_type"] == "特殊糖尿病" else 0
    
    # 所有女性患者
    female = 1 if df["gender"] == "female" else 0
    
    # 所有诊断为糖尿病的患者
    diagnosed = 1 if df["q1_answer"] == "a" else 0
    
    # 初始胰岛素治疗
    insulin_ini_user = 1 if (
                                ((df["q7_answer"] =="d" or df["q7_answer"] == "f" ) and (df["q2_answer"] !="" and df["q2_answer"] !="g"))
                            or
                                (df["q8_answer"] == "a" or df["q8_answer"] =="b")
                            or 
                                (df["q3_answer"] == "a" or df["q3_answer"] =="b" or df["q3_answer"] =="d" or df["q3_answer"] =="e")
                            ) else 0
    
    # 目前胰岛素使用者：
    insulin_current_user = 1 if df["q8_answer"] == "a" or df["q8_answer"] =="b" else 0
    
    return pd.Series([not_diagnosed_within_one_year_dia,not_diagnosed,female_20_45_gestational,type_1,
                      above_55,under_20,type_sp,female,diagnosed,insulin_ini_user,insulin_current_user])


# 二级标签转换成病人分类
def get_trans_pat_cls(list_of_lv2,lv2_to_pcls):
    
    def find_key(input_dict, value):
        output = [k for k, v in input_dict.items() if value in v ]
        if not output:
            return np.nan
        else:
            return output[0]
    
    if not list_of_lv2:
        pat_cls_list = []
    else:
        pat_cls_list = list(set([find_key(lv2_to_pcls,x) for x in list_of_lv2 ]))
    
    return pat_cls_list


def check_behav_valid_usr(usr_id,behavior_all_indexed,content_lib,num=3):
    try:
        personal_interaction = behavior_all_indexed.loc[[usr_id]]
        personal_interaction_valid = personal_interaction[personal_interaction["content_title"].isin(
        content_lib["title"])]
        valid_behavior = personal_interaction_valid.groupby(
            ["content_title"])["strength"].sum().apply(smooth_user_preference).reset_index()
        valid_record = valid_behavior.shape[0]
        if valid_record >= num:
            flag = True
        else:
            flag = False
        items_to_ignore = valid_behavior.content_title.tolist()
    
    except KeyError:
        print("Unable to track \"{}\" behavior data".format(usr_id))
        flag = False
        items_to_ignore = []
        valid_behavior = pd.DataFrame()
        
    return flag, items_to_ignore,valid_behavior


def generate_usr_rec(usr_id, behavior_all_indexed, content_lib, content_pop_rank, pat_attr_dict, content_attr_dict):
    pref_num = 8
    strat_num = 8
    prog_num = 4

    title_list = content_lib.title.tolist()

    flag, history, behavior = check_behav_valid_usr(
        usr_id, behavior_all_indexed, content_lib)

    if flag:
        print("Enough Behavior Data Detected,Rec:Using Personal Reading Preference")
        user_profile_norm = build_users_profile(behavior)
        cosine_similarities = cosine_similarity(
            user_profile_norm, tfidf_matrix)
        similar_indices = cosine_similarities.argsort().flatten()[-100:]
        similar_items = sorted([(title_list[i], cosine_similarities[0, i])
                                for i in similar_indices], key=lambda x: -x[1])
        similar_items_filtered = list(
            filter(lambda x: x[0] not in history, similar_items))
        recTitle_pref = [i[0] for i in similar_items_filtered][:pref_num]
        rec_method_pref = ["Patient Preference"]*pref_num
    else:
        print("Not Enough Behavior Data Detected,Rec: Using Popularity instead")
        recTitle_pref = content_pop_rank[~content_pop_rank["title"].isin(
            history)]["title"].head(pref_num).tolist()
        rec_method_pref = ["Popularity"]*pref_num
#####################################################################################################
    cls = pat_attr_dict.get(usr_id, ["所有患者"])

    progess = set()

    for x in cls:
        progess |= content_attr_dict.get(x)

    item_to_ignore_2 = set(recTitle_pref) | set(history)

    progess_filtered = list(
        filter(lambda x: x[0] not in item_to_ignore_2, progess))

    progress_final = random.sample(progess_filtered, prog_num)

    if not "所有患者" in cls:
        rec_method_prog = ["Patient Progress"]*prog_num
    else:
        print("No survey data found, Using Product Strat instead of Pat Progress")
        rec_method_prog = ["Product Strategy"]*prog_num

######################################################################################################
    item_to_ignore_3 = set(recTitle_pref) | set(history) | set(progress_final)
    strategy = content_attr_dict.get("所有患者")
    strategy_filtered = list(
        filter(lambda x: x[0] not in item_to_ignore_3, strategy))
    strategy_final = random.sample(strategy_filtered, strat_num)
    rec_method_strat = ["Product Strategy"]*strat_num
######################################################################################################
    rec_final = recTitle_pref + strategy_final + progress_final
    rec_method = rec_method_pref + rec_method_strat + rec_method_prog
    open_id = [usr_id] * (pref_num+strat_num+prog_num)
    RecFrame = pd.DataFrame(list(zip(open_id, rec_final, rec_method)), columns=[
                          "open_id", "rec_title", "rec_method"])

    return RecFrame

def input_check(table):
    try:
        df = nn.Dataframefactory(table,iotype = iotype)
        if df.empty:
            raise ValueError("table {} is empty".format(table))
        return df
    except Exception as e:
        print("There was an error in your input table, Please double check your data source\n:{}".format(e))

def load():
    print("Designed for Novo4PE: Content Rec Sys")
    print("------------------------------------------------------")
    print("Step 1: Loading Raw Data")

    diabetes_type = input_check("diabetes_type") #糖尿病类型数据
    info = input_check('pat_info') #病人个人信息数据
    answer = input_check('survey_answer') #病人问卷回答数据
    #question = nn.Dataframefactory('survey_question',iotype = iotype) #病人问题数据，没用到

    with open('../etc/pat_rec_strat.json',encoding="utf-8") as f: #病人分类 与 二级标签的对应关系
        patient_cls = dict(json.load(f))

    tag_simi = input_check('similar') # 码表
    pat_t = input_check('pat_tag') # 码表

    #content_hcp_raw = nn.Dataframefactory('hcp_articles',iotype = iotype) # 医生文章库
    content_pat_raw = input_check('pat_articles')#病人文章库
    behavior_raw = input_check('behavior') #行为数据    

    print("Step 1: Done")
    print("------------------------------------------------------")
    print("Step 2: Processing Data and Preparing Algorithm")

    createDictStop()
    mapping = mappingCbind(tag_simi, pat_t)
    
    global behavior_all_indexed
    behavior_all_indexed = interaction_process(behavior_raw) #对行为数据 先进行处理 

    global content_lib
    content_lib,all_content = content_lib_processing(content_pat_raw) #对文章库进行处理 
    
    global content_pop_rank
    content_pop_rank = get_ranked_content_title(behavior_all_indexed,all_content) #得到有排名的文章库
    corpus_list = corpus_process(content_lib) #将文章库切词
    gen_tfidf_matrix(corpus_list) #建立TFIDF矩阵
    
    # 建立 文章与病人的分类关系
    all_lb_content = all_content.copy() #复制一个先
    all_lb_content["token"] = all_lb_content.title.apply(tokenize) #给文章切词
    all_lb_content['lv2'] = all_lb_content.token.apply(labelIt,args=(mapping, )) # 给文章打标签
    all_lb_content["lv2"] = all_lb_content["lv2"].apply(filterComplication) #去掉并发症

    all_lb_content["pat_cls"] = all_lb_content.lv2.apply(get_trans_pat_cls,args=(patient_cls, )) #二级标签转病人分类
    uniq_pat_cls = list(patient_cls.keys()) #获取病人分类list
    # 转dummy
    all_lb_content[uniq_pat_cls] = all_lb_content["pat_cls"].apply(     
        create_var, args=(uniq_pat_cls,))
    pat_cls_col = uniq_pat_cls.copy()
    pat_cls_col.insert(0,"title")

    content_attr = all_lb_content[pat_cls_col]
    content_attr.set_index('title',inplace=True)
    content_attr_new=content_attr[content_attr==1].stack().reset_index().drop(0,1)
    
    global content_attr_dict
    content_attr_dict = dict(content_attr_new.groupby(by=["level_1"])["title"].apply(set)) # 病人分类与文章title的映射


    #建立 病人的分类关系
    dtype = dict(zip(diabetes_type.id,diabetes_type.type)) #建立疾病id与文字描述映射
    answer.drop_duplicates(subset=["open_id"],keep="last",inplace=True) #去除掉无效问答记录，只保留最新的问卷记录
    answer.reset_index(drop=True,inplace=True)
    info["diabetes_type"] = info["diabetes_type_id"].replace(dtype) #将文字疾病描述建立
    patient_attribute = info.merge(answer,left_on="open_id",right_on="open_id",how="outer") #将病人信息与问卷记录做full-join
    patient_attribute["age"] = pd.to_numeric(patient_attribute["age"],errors='coerce') #将年龄从 str 转为 numeric


    pat_class =[ '“未诊断”及“新诊断1年以内”的糖尿病患者',
                 '“未诊断”的患者',
                 '所有女性患者中年龄在“20-45”岁，以及“妊娠糖尿病”患者',
                 '“1型糖尿病患者”',
                 '所有55岁以上患者',
                 '所有20岁以下患者',
                 '所有“特殊类型糖尿病患者”',
                 '所有女性患者',
                 '所有诊断为糖尿病的患者',
                 '初始胰岛素治疗',
                 '目前胰岛素使用者'] #病人疾病 与 patient_classification返回值的对应columns，注意顺序要与 func返回值一致

    patient_attribute[pat_class] = patient_attribute.apply(patient_classification,axis=1)
    patient_attr = patient_attribute.copy()
    pat_class_col = pat_class.copy()
    pat_class_col.insert(0,"open_id")


    patient_attr = patient_attr[pat_class_col]
    pat_attr = patient_attr.copy()
    pat_attr.set_index('open_id',inplace=True)
    pat_attr=pat_attr[pat_attr==1].stack().reset_index().drop(0,1)
    
    global pat_attr_dict
    pat_attr_dict = dict(pat_attr.groupby(by=["open_id"])["level_1"].apply(set).apply(list)) #病人open_id与病人分类的映射
    print("Step 2: Done")
    print("------------------------------------------------------")
    
    return('ALGORITHM LOADING COMPLETE') 


def rec(patient):
    
    if patient != '':

        a = time()
        rec = generate_usr_rec(patient, behavior_all_indexed, content_lib, content_pop_rank, pat_attr_dict, content_attr_dict)
        b = time()
        print('Elapse:',b-a,' seconds')
        t = rec.T.to_dict()
        d = {}
        for item in t:
            d[str(item)] =  t[item]
        print(d)
        return(d)    


def mainloop():
    while True:
        id_ = input('----> please input openid:\n') 
        if id_ == 'exit':
            break
        elif id_ == '':
            continue
        else:
            print(rec(id_))

