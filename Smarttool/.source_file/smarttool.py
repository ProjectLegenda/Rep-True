# -*- coding: utf-8 -*-
"""
# @Author: Yubo HE
# @Date:   2018-10-31 09:43:16
# @Last Modified by:   Yubo HE
# @Last Modified time: 2018-10-31 14:37:29
# @Email: yubo.he@cn.imshealth.com
"""
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import jieba
import jieba.analyse
import re
import datetime as dt
from datetime import datetime
import nndw as nn
import math
import os
from functools import wraps
from time import time

import sys, getopt

def timing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time()
        result = f(*args, **kwargs)
        end = time()
        print ("func:{}, time elaps:{:.0f}m {:.0f}s".format(f.__name__,(end-start)//60, (end-start) % 60))
        return result
    return wrapper

@timing
def createDictStop():
    """
    Load external dictionary and stop words
    """
    print("Loading Dictionary and Stopwords")
    global stopWord    
    #dic_path = ''
    dic = nn.read_table(nn.getTable("mappingword"))
    stopWord = nn.read_table(nn.getTable("stopword"))
    word = dic.word.tolist()   
    stopWord = stopWord.word.tolist()
    jieba.re_han_default =re.compile(r'([\u0020\u4e00-\u9fa5a-zA-Z0-9+#&._%/β/α/-]+)', re.UNICODE)
    frequnecy = 1000000000000000000000
    # Add words to dictionary
    for words in word:
        jieba.add_word(words,frequnecy)
    print("Finished Dic Loading")

@timing
def mappingCbind(tagSimilarWords, tag):
    """
    create mapping file
    """

    # Cut tags into different levels
    lv2Tags = tag[(tag.tag_class == "内容标签") & (tag.tag_level == 2)]
    lv1Tags = tag[(tag.tag_class == "内容标签") & (tag.tag_level == 1)]
    hcpTags = tag[tag.tag_class == "医生标签"]

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
                  how="left", left_on="parent_tag_id_lv1", right_on="tag_id", suffixes=("_lv1", "_hcp"))

    # Re-adjust into four columns
    mapping = lv1Hcp[["tag_similar_word", "tag_name_lv2", "tag_name_lv1", "tag_name_hcp"]]

    return mapping

def segContent(sentence):
    sentence = sentence.replace('\n', '').replace('\u3000', '').replace('\u00A0', '').replace('\xa0','')
    segs = jieba.cut(sentence,cut_all=False)
    outList = [seg for seg in segs if seg not in stopWord and  not re.match('^[0-9|.|%]*$',seg)]
    return outList

def labelIt(tokens,keyTable):
    labels = []
    lv1Lb = []
    lv2Lb = []
    funcLb = []
    for token in tokens:
        for index, row in keyTable.iterrows():
            if token in row['tag_similar_word']:
                labels.append(index)
                lv2Lb.append(row['tag_name_lv2'])
                lv1Lb.append(row['tag_name_lv1'])
                funcLb.append(row['tag_name_hcp'])


    labels = list(set(labels))
    labels = [ x for x in labels if str(x) != 'nan']
    lv2Lb= list(set(lv2Lb))
    lv2Lb = [ x for x in lv2Lb if str(x) != 'nan']
    lv1Lb= list(set(lv1Lb))
    lv1Lb = [ x for x in lv1Lb if str(x) != 'nan']
    funcLb= list(set(funcLb))
    funcLb = [ x for x in funcLb if str(x) != 'nan']

    return pd.Series([labels, funcLb, lv1Lb, lv2Lb])

def filterComplication(lv2Label):
    diabetes = ['糖尿病','2型糖尿病']
    complication = ['急性/严重并发症',
                    '酮症酸中毒',
                    '肝病相关',
                    '呼吸系统相关',
                    '肾病相关',
                    '神经病变',
                    '糖尿病足',
                    '心脑血管相关',
                    '高血压相关',
                    '高血脂相关',
                    '视网膜病变',
                    '风湿性疾病',
                    '性功能问题',
                    '胃肠不适',
                    '骨相关问题',
                    '皮肤病变',
                    '精神/心理相关',
                    '肿瘤相关',
                    '其它代谢性疾病',
                    '其它不严重的症状或不良反应']
    for word in diabetes:
        if word in lv2Label:
            lv2Label.remove(word)
    for word in complication:
        if (word in lv2Label) and ('并发症/合并症') in lv2Label:
                lv2Label.remove('并发症/合并症')
    return lv2Label

def toJsonFormat(df):
    data=[]
    col = []
    for lb in df.columns:
        lbs = df[lb].loc[0]
        cols = [lb+'_lb_{}'.format(i) for i in range(1,len(lbs)+1)]
        data.extend(lbs)
        col.extend(cols)
    final = pd.DataFrame(data=data,index=col,columns=['tags']).T
    return final

def main(inputfile,outputfile):

    createDictStop()
    tag = nn.read_table(nn.getTable("tag"))
    similar = nn.read_table(nn.getTable("similar"))
    mapping =  mappingCbind(similar,tag)
    
    df = pd.read_json(inputfile,typ='series',encoding='utf-8' ).to_frame().T
    df["title_token"]= df.title.apply(segContent)
    df["content_token"] = df.content.apply(segContent)
    df[['lb','hcp','lv1','lv2']] = df.title_token.apply(labelIt,args=(mapping, ))
    df['lv2'] = df['lv2'].apply(filterComplication)
    out = df[['lv1','lv2']]
    final = toJsonFormat(out)
    with open(outputfile, 'w', encoding='utf-8') as f:
        final.to_json(f,orient='index', force_ascii=False)

    # -*- coding: utf-8 -*-
"""
# @Author: Yubo HE
# @Date:   2018-10-31 13:21:50
# @Last Modified by:   Yubo HE
# @Last Modified time: 2018-10-31 13:21:50
# @Email: yubo.he@cn.imshealth.com
"""
