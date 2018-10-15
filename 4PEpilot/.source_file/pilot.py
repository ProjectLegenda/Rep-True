# -*- coding: utf-8 -*-
"""
# @Author: Yubo HE
# @Date:   2018-10-11 15:46:11
# @Last Modified by:   Yubo HE
# @Last Modified time: 2018-10-11 17:20:12
# @Email: yubo.he@cn.imshealth.com
"""


import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import jieba
import re
import datetime as dt
from datetime import datetime
import nndw as nn

import os
from collections import Counter
from functools import wraps
from time import time

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

def tokenize(content):
    """
    cut sentences into tokens
    """
    wordList = jieba.cut(content, cut_all=False)
    token = [word for word in wordList if word not in stopWord]
    return token

def cleanNan(words):
    """
    Clean NaN value in the lists
    """
    cleanedList = [x for x in words if str(x) != 'nan']
    return cleanedList

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


@timing
def titleLabeling(df, keyTable):
    """Labeling Title

    Loading a dataframe of titles, and convert it to the dataframe with differet level labels

    Arguments:
        df {Pandas Dataframe} -- [dataframe with variable name of 'content_title']
        keyTable {Pandas Dataframe} -- [key metric]

    Returns:
        [pandas dataframe] -- [labeled title]
    """
    dataFrame = df.copy()
    dataFrame['Token'] = dataFrame['content_title'].apply(tokenize)
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

    def labelIt(tokens):
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
        for word in diabetes:
            if word in lv2Label:
                lv2Label.remove(word)
        for word in complication:
            if (word in lv2Label) and ('并发症/合并症') in lv2Label:
                lv2Label.remove('并发症/合并症')
        return lv2Label

    print("Labelling Title")
    dataFrame[['labels','HCP标签','一级标签','二级标签']] = dataFrame['Token'].apply(labelIt)
    dataFrame['二级标签'] = dataFrame['二级标签'].apply(filterComplication)
    return dataFrame

def calContInst(taggedDf, hcp_id):
    """Caculate content insterests
    Arguments:
        taggedDf {[dataframe]} -- [the output dataframe from title labeling]
        hcp_id {[string]} -- [the specific hcp_id]

    Returns:contentInsteret [dataframe]
            otherTags [list]
            lb [dictionary]
            labelMap [dictionary]

    """
    df = taggedDf[taggedDf['doctorid'] == hcp_id]
    open_id = df.hcp_openid_u_2.iloc[0]
    lb = []
    for labels in df['HCP标签']:
        lb.extend(labels)
    lb = dict(Counter(lb))

    dic = {'content_interest':list(lb.keys()),'ratio':list(lb.values())}
    contentInsteret = pd.DataFrame(dic)
    contentInsteret.sort_values(by='ratio',ascending=False,inplace=True)
    contentInsteret.reset_index(drop=True,inplace=True)

    if contentInsteret.shape[0] > 5:
        others = ['其他',contentInsteret[5:].ratio.sum()]
        otherTags = contentInsteret[5:]['content_interest'].tolist()
        contentInsteret.drop(contentInsteret.index[5:],inplace =True)
        contentInsteret.loc[5] = others
    else:
        otherTags = []

    total = contentInsteret['ratio'].apply('sum')
    contentInsteret['ratio'] = contentInsteret['ratio'].apply( lambda x:"{0:.0%}".format(x/total))
    contentInsteret['open_id'] = open_id
    contentInsteret['hcp_id'] = hcp_id
    contentInsteret['last_update'] = pd.Timestamp("now").strftime("%Y-%m-%d %H:%M:%S")
    contentInsteret['id'] = contentInsteret.index +1
    outputVar =['id','open_id','hcp_id','content_interest','ratio','last_update']
    contentInsteret = contentInsteret[outputVar]
    labelMap =  dict(zip(contentInsteret['content_interest'].tolist(),contentInsteret['id'].tolist()))

    return contentInsteret,otherTags,lb,labelMap

def calContKeyWord(taggedDf,hcp_id,lb,other_tag,mapping,keytable):
    #print(mapping)
    df= taggedDf[taggedDf['doctorid'] == hcp_id]
    #create a dict of HCP labels
    dicHcpLb ={}
    for idx,key in enumerate(lb.keys()):
        l = []
        for i,row in df.iterrows():
            if key in row['HCP标签']:
                l.append(i)
        dicHcpLb[key] = l

    #
    contKey = {}
    for key in dicHcpLb.keys():
        lv2LbList = df.loc[dicHcpLb[key]]['二级标签'].tolist()
        lv2label = keytable[keytable['tag_name_hcp'] == key].tag_name_lv2.tolist()
        flatList = [item for sublist in lv2LbList for item in sublist]
        lv2Cnt = [x for x in flatList if x in lv2label]
        contKeyWord = dict(Counter(lv2Cnt))
        contKey[key] = contKeyWord

    if other_tag:
        z = [contKey[x] for x in other_tag]
        contKey['其他'] = { k: v for d in z for k, v in d.items()}
        for k in other_tag:
            contKey.pop(k, None)

    keywordCnt = pd.DataFrame()
    for key,item in contKey.items():
        #keywordCnt['Content_Interest_ID'] = key
        df_join = pd.DataFrame.from_dict(item, orient='index',columns=['keyword_count'])
        df_join.reset_index(inplace=True)
        df_join.rename(columns={"index": "keyword"},inplace=True)
        df_join.sort_values(by=['keyword_count'],ascending=False,inplace=True)
        df_join['last_update'] = pd.Timestamp("now").strftime("%Y-%m-%d %H:%M:%S")
        df_join['content_interest_id'] = key
        keywordCnt = keywordCnt.append(df_join,ignore_index=True)
    keywordCnt["hcp_id"] = hcp_id
    keywordCnt["content_interest_id"] = keywordCnt["content_interest_id"].map(mapping)
    outputVar = ['hcp_id','content_interest_id','keyword','keyword_count','last_update']
    keywordCnt = keywordCnt[outputVar]
    return keywordCnt

# 数据预处理，返回为五个data frame
@timing
def dataPrepare(wechatRaw, webRaw):
    
    # filter wechat data having doctorid
    wechatColList = ["doctorid", "hcp_openid_u_2", "content_id", "content_title", "start_date", "duration"]
    wechatFilterd = wechatRaw[~wechatRaw.doctorid.isnull()][wechatColList]
    
    # filter web data having doctorid
    webColList = ["doctorid", "content_id", "content_title", "start_date", "end_date"]
    webFilterd = webRaw[~webRaw.doctorid.isnull()][webColList]
    # use the wechatFilterd and webFilterd for channel preference calculation
    
    # Remove the invalid data: content title is 0
    validWechatLog = wechatFilterd[~(wechatFilterd.content_title == "0")].reset_index(drop=True)
    validWebLog = webFilterd[~(webFilterd.content_title == "0")].reset_index(drop=True)
    # use validWechatLog and validWebLog as parameters for reading history without tokens
    
    # prepare data for content preference calculation
    # fill open id as null into webLog and concat required data into one df
    validWebLog.insert(1, "hcp_openid_u_2", np.nan)
    contentPrefData = pd.concat([validWechatLog[["doctorid", "hcp_openid_u_2", "content_title"]],\
                                 validWebLog[["doctorid", "hcp_openid_u_2", "content_title"]]]).reset_index(drop=True)
    
    return wechatFilterd, webFilterd, validWechatLog, validWebLog, contentPrefData

# 渠道偏好
@timing
def channelPref(wechatRaw, webRaw):
    
    # record start algorithm start time
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # aggregate the counts in different channel
    wechatAggRes = wechatRaw.groupby("doctorid").size().reset_index(name="wechat_content_count")
    webAggRes = webRaw.groupby("doctorid").size().reset_index(name="web_content_count")
    
    # merge two channels and fillna 
    ### 这里是否需要fillna待定，因为数据展示的时候，如果微信渠道为0，可以直接不展示微信渠道
    resCbind = pd.merge(wechatAggRes, webAggRes, on="doctorid", how="outer").fillna(0)
    
    # add time stamp to df
    resCbind["last_update"] = time
    
    # change data formats
    resCbind[["wechat_content_count", "web_content_count"]] = resCbind[["wechat_content_count", "web_content_count"]].astype(int)
    resCbind["last_update"] = pd.to_datetime(resCbind["last_update"])
    resCbind.rename(columns={'doctorid':'hcp_id'},inplace=True)
    
    return resCbind

# 计算秒
def getSeconds(time_delta):
    return time_delta.seconds

def webHistWithoutTokens(webLog):
    
    # transform str to datetime
    webLog["start_date"] = pd.to_datetime(webLog["start_date"])
    webLog["end_date"] = pd.to_datetime(webLog["end_date"])
    
    # transform view datetime to seconds
    webLog["view"] = webLog["end_date"] - webLog["start_date"]
    webLog["view_length"] = webLog["view"].apply(getSeconds)
    
    # filter the records which view length >= 30 seconds
    webLog = webLog[pd.to_numeric(webLog.view_length) >= 30]
    
    # combine required columns into a dataframe, without tokens
    res = webLog[["doctorid", "content_id", "content_title", "start_date"]].reset_index(drop=True)
    res.insert(0, "hcp_openid_u_2", np.nan)
    
    return res

def wechatHistWithoutTokens(wechatLog):
    
    # filter the data with view lenth >= 30s
    validLog = wechatLog[pd.to_numeric(wechatLog.duration) >= 30].reset_index(drop=True)
    
    # filter the required columns
    resCbind = validLog[["hcp_openid_u_2", "doctorid", "content_id", "content_title", "start_date"]]
    
    # change the date to timestamp
    resCbind["start_date"] = pd.to_datetime(resCbind.start_date)
    
    return resCbind

def readingHist(webHistWithoutTokens, wechathistWithoutTokens, contentLabeled):
    # 整合阅读历史并且添加文章的二级标签
    allHistCbind = pd.concat([webHistWithoutTokens, wechathistWithoutTokens])
    
    allHistWithTags = allHistCbind.merge(contentLabeled, how="left", 
                                     left_on="content_title", right_on="content_title")
    
    allHistWithLv2Tags = allHistWithTags[["hcp_openid_u_2", "doctorid", "content_id", "content_title", "二级标签", "start_date"]]
    
    res = allHistWithLv2Tags.rename(columns={"hcp_openid_u_2":"open_id", "doctorid":"hcp_id", "二级标签":"content_keyword", "start_date":"browser_time"})
    res["content_keyword"] = res["content_keyword"].apply(lambda x: ' '.join(x))
    return res

def main():
    tag = nn.read_table(nn.getTable("tag"))
    similar = nn.read_table(nn.getTable("similar"))
    mapping =  mappingCbind(similar,tag)
    createDictStop()
    wechat = nn.read_table(nn.getTable("wechat"))
    web = nn.read_table(nn.getTable("web"))

    # 五部分数据：
    # wechatFilterd, webFilterd用于渠道分析计算
    # contentPrefData用于content preference计算
    # validWebLog, validWechatLog用于阅读历史计算
    wechatFilterd, webFilterd, validWechatLog, validWebLog, contentPrefData = dataPrepare(wechat, web)
    
    output1 = channelPref(wechatFilterd, webFilterd)
    
    # cut title
    cotentTitle = contentPrefData['content_title'].dropna().drop_duplicates().to_frame()
    contentLabeled = titleLabeling(cotentTitle,mapping)
    contentNew= contentPrefData.merge(contentLabeled,left_on='content_title',right_on='content_title')
    output2 = pd.DataFrame()
    output3 = pd.DataFrame()
    for dc_id in contentNew.doctorid.unique():
        contentInsteret,otherTags,lb,labelMap = calContInst(contentNew, dc_id)
        keywordCnt = calContKeyWord(contentNew,dc_id,lb,otherTags,labelMap,mapping)
        output2 = output2.append(contentInsteret)
        output3 = output3.append(keywordCnt)
    output2.reset_index(drop=True,inplace=True)
    output3.reset_index(drop=True,inplace=True)
    
    
    webHistWithoutToken = webHistWithoutTokens(validWebLog)
    wechathistWithoutToken = wechatHistWithoutTokens(validWechatLog)
    output4 = readingHist(webHistWithoutToken, wechathistWithoutToken, contentLabeled)

    #return output1,output2,output3,output4

    #output1.to_csv('output1')
    #output2.to_csv('output2')
    #output3.to_csv('output3')
    #output4.to_csv('output4')
    
    nn.write_table(output1,nn.getTable('channel_preference'))
    nn.write_table(output2,nn.getTable('content_interest'))
    nn.write_table(output3,nn.getTable('content_interest_keyword'))
    nn.write_table(output4,nn.getTable('reading_history'))
    


