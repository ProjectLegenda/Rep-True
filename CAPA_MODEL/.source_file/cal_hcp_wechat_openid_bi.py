import pandas as pd
import numpy as np

import jieba
import re

import datetime as dt
from datetime import datetime

import nndw as nn

iotype = 'db'


def chordStatsBySeg(data, openID):
    segAllData = data.copy()
    tagList = []
    
    for hcpTagList in segAllData["hcp_tag"]:
        for word in hcpTagList:
            if word not in tagList and word != '':
                tagList.append(word)
       
    tagListDf = pd.DataFrame(data=tagList, columns=["point_one"])
    tagListDf.insert(0, "openID", openID)
 
    mergedPoints = pd.merge(tagListDf, tagListDf, how="inner", left_on="openID", right_on="openID")
    mergedPoints.reset_index(drop=True, inplace=True)
    mergedPoints.insert(3, "count", 1)
    mergedPoints.rename(columns={"point_one_x":"point_one", "point_one_y":"point_two"}, inplace=True)
    
    if mergedPoints.shape[0] != 1:
        mergedPoints = mergedPoints[mergedPoints["point_one"]!=mergedPoints["point_two"]]

    return mergedPoints

# by pat openid, no continuous months	
def statsBySegment(data, openID):
    segAllData = data.copy()
    statsList = []
    months = list(set(segAllData["month_id"]))
    
    for month_id in months:
        subsetLog = segAllData[segAllData["month_id"]==month_id]
        if subsetLog.shape[0] != 0:
            subStats = statsByLevel(subsetLog, "lv2_tag")
            subStats.insert(0, "month_id", month_id)
            statsList.append(subStats)
    
    statsBySeg = pd.concat(statsList, ignore_index=True)
    statsBySeg.insert(loc=0, column="openID", value=openID)
    
    return statsBySeg
	
	
# use labelled behaviour data to do stats on different level
def statsByLevel(data, lvl):
    resList = []
    
    for tempList in data[lvl]:
        for word in tempList:
            resList.append(word)
    
    df = pd.DataFrame({"tag_count":resList})
    stats = df["tag_count"].value_counts().to_frame(name="tag_count")
    stats.reset_index(inplace=True)
    stats.rename(columns={"index":"tag_name"}, inplace=True)
    
    return stats

	
# extract the montid, e.g. 201711 from behaviour data
def getMonthId(date):
    timeStamp = pd.to_datetime(date)
    year= timeStamp.year
    month = "{:02d}".format(timeStamp.month)
    
    month_id = str(year) + str(month)
    
    return month_id

	
def dataPrepare(wechatRaw):
    
    # filter wechat data in doctorList
    patWechatRaw = wechatRaw[wechatRaw["platform"]=="2"]
    wechatColList = ["hcp_openid_u_2", "content_title", "start_date"]
    wechatFilterd = patWechatRaw[wechatColList]
    
    # Remove the invalid data: content title is 0
    validWechatLog = wechatFilterd[~((wechatFilterd.content_title=="") | (wechatFilterd.content_title.isnull()) | (wechatFilterd.hcp_openid_u_2.isnull()) | (wechatFilterd.hcp_openid_u_2==''))].reset_index(drop=True)

    return validWechatLog


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


def tokenize(content):
    """
    cut sentences into tokens
    """
    wordList = jieba.cut(content, cut_all=False)
    token = [word for word in wordList if word not in stopWord]
    return token

	
def mappingCbind(tagSimilarWords, tag):
    """
    create mapping file
    """

    # Cut tags into different levels
    lv2Tags = tag[(tag.tag_class == "内容标签") & (tag.tag_level == "2")]
    lv1Tags = tag[(tag.tag_class == "内容标签") & (tag.tag_level == "1")]
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
    dataFrame['Token'] = dataFrame["content_title"].apply(tokenize)
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

    def labelIt(tokens):
        #labels = []
        #lv1Lb = []
        lv2Lb = []
        funcLb = []
        for token in tokens:
            for index, row in keyTable.iterrows():
                if token in row['tag_similar_word']:
                    #labels.append(index)
                    lv2Lb.append(row['tag_name_lv2'])
                    #lv1Lb.append(row['tag_name_lv1'])
                    funcLb.append(row['tag_name_hcp'])


        #labels = list(set(labels))
        #labels = [ x for x in labels if str(x) != 'nan']
        lv2Lb= list(set(lv2Lb))
        lv2Lb = [ x for x in lv2Lb if x != '' and str(x) != 'nan']
        #lv1Lb= list(set(lv1Lb))
        #lv1Lb = [ x for x in lv1Lb if str(x) != 'nan']
        funcLb= list(set(funcLb))
        funcLb = [ x for x in funcLb if x != '' and str(x) != 'nan']

        return pd.Series([lv2Lb, funcLb])

    def filterComplication(lv2Label):
        for word in diabetes:
            if word in lv2Label:
                lv2Label.remove(word)
        for word in complication:
            if (word in lv2Label) and ('并发症/合并症') in lv2Label:
                lv2Label.remove('并发症/合并症')
        return lv2Label

    print("Labelling Title")
    dataFrame[['lv2_tag','hcp_tag',]] = dataFrame['Token'].apply(labelIt)
    dataFrame['lv2_tag'] = dataFrame['lv2_tag'].apply(filterComplication)
    print("Finished Labelling")
    return dataFrame


def main():
    tag = nn.Dataframefactory("hcp_tag",iotype = iotype)
    simi = nn.Dataframefactory("similar",iotype = iotype)
    
    mapping =  mappingCbind(simi,tag)
    createDictStop()
    
    wechat = nn.Dataframefactory("wechat",iotype = iotype)
    
    # 整合微信和网站的数据到同一个df
    cbindBehavData = dataPrepare(wechat)
    hcpList = list(set(cbindBehavData["hcp_openid_u_2"]))
    print("Finished Data preparation")
    
    contentTitle = cbindBehavData['content_title'].dropna().drop_duplicates().to_frame()
    contentLabeled = titleLabeling(contentTitle,mapping)
    allBehavDataLabelled= cbindBehavData.merge(contentLabeled,left_on='content_title',right_on='content_title')
    allBehavDataLabelled["month_id"] = allBehavDataLabelled["start_date"].apply(getMonthId)
    validBehavDataLabelled = allBehavDataLabelled[allBehavDataLabelled.lv2_tag.str.len() != 0]

    # calculate the heatmap data and chord diagram data
    heatMapPart = []
    chordMapPart = [] 
    print("Begin calculating")
    
    for openID in hcpList:
        segBehavData = validBehavDataLabelled[validBehavDataLabelled["hcp_openid_u_2"]==openID]
        if segBehavData.shape[0] != 0:
            segHeatData = statsBySegment(segBehavData, openID)
            heatMapPart.append(segHeatData)
            segChordData = chordStatsBySeg(segBehavData, openID)
            if segChordData.shape[0] != 0:
                chordMapPart.append(segChordData)
       
    heatMapOutput = pd.concat(heatMapPart, ignore_index=True)
    chordMapOutput = pd.concat(chordMapPart, ignore_index=True)
    print("Finished calculating")
    
    nn.write_table(heatMapOutput,'hcp_heatmap_openid',iotype = iotype)
	# hcp_heatmap_openid structure: four columns - openID, month_id, tag_name, tag_count
    nn.write_table(chordMapOutput,'hcp_chordmap_openid', iotype = iotype)
	# hcp_chordmap_openid structure: four columns - openID, point_one, point_two, count
    
    return (1)   



