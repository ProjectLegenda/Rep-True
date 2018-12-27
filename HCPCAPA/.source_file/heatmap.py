import pandas as pd
import numpy as np

import jieba
import re

import datetime as dt
from datetime import datetime

import itertools
import nndw as nn
#import nndw as nn

def chordStatsBySeg(data, segId):
    segAllData = data
   
    docTagAggList = []
   
    for docid in set(segAllData["doctorid"]):
        tagList = []
        tempData = segAllData[segAllData.doctorid==docid]
        for hcpTagList in tempData["hcp_tag"]:
            for word in hcpTagList:
                if word not in tagList:
                    tagList.append(word)
       
        tagListDf = pd.DataFrame(data=tagList, columns=["point_one"])
        tagListDf.insert(0, "doctor_id", docid)
       
        docTagAggList.append(tagListDf)
   
    docTagAggData = pd.concat(docTagAggList, ignore_index=True)
   
    mergedPoints = pd.merge(docTagAggData, docTagAggData, how="inner", left_on="doctor_id", right_on="doctor_id")
    pointOne = mergedPoints[mergedPoints["point_one_x"]==mergedPoints["point_one_y"]]
    conditionPoint = mergedPoints[mergedPoints["point_one_x"]!=mergedPoints["point_one_y"]]
   
    pointOneAgg = pointOne.groupby("point_one_x").agg({"doctor_id":pd.Series.nunique})
    pointOneAgg.reset_index(inplace=True)
    conditionPointsAgg = conditionPoint.groupby(["point_one_x", "point_one_y"]).agg({"doctor_id":pd.Series.nunique})
    conditionPointsAgg.reset_index(inplace=True)
   
    aggAllPoints = pd.merge(pointOneAgg, conditionPointsAgg, how="left", left_on="point_one_x", right_on="point_one_x")
    aggAllPoints["ratio"] = aggAllPoints["doctor_id_y"] / aggAllPoints["doctor_id_x"]
   
    segChordData = aggAllPoints[["point_one_x", "point_one_y", "ratio"]]
    segChordData.insert(0, "segment_id", segId)
    segChordData.rename(columns={"point_one_x":"point_one", "point_one_y":"point_two"}, inplace=True)
   
    return segChordData

# subset data into doctors belongs to segment_id
def statsBySegment(data, segment_id, topLv2LabelsDf):
    segAllData = data
    topLabels = topLv2LabelsDf.copy()
    statsList = []
    months = getOneYrMonths()
    
    for month_id in months:
        subStats = statsByMonthId(segAllData, month_id)
        #print(subStats)
        #print("    ")
        #print(topLabels)
        #print("    ")
        #print(topLv2LabelsDf)
        #print("    ")
        
        if len(subStats)==0:
            segMonthMerge = topLabels
            segMonthMerge["tag_count"] = 0
        else:
            segMonthMerge = pd.merge(topLv2LabelsDf, subStats, how="left", left_on="tag_name", right_on=subStats.index)
            
        segMonthMerge["month"] = month_id
        #print(segMonthMerge)
        #print("    ")
        #print("    ")
        #print("    ")
        #print("    ")
        statsList.append(segMonthMerge)
    
    statsBySeg = pd.concat(statsList, ignore_index=True)
    #statsBySeg["segment_id"] = segment_id
    statsBySeg.insert(loc=0, column="segment_id", value=segment_id)
    heatMapDataBySeg = statsBySeg.fillna(0)
    
    return heatMapDataBySeg
	
	
# stats on each month by lvl2 tags
def statsByMonthId(data, month_id):
    subsetLog = data[data["month_id"] == month_id]
    
    subStats = statsByLevel(subsetLog, "lv2_tag")
    
    return subStats

	
# use labelled behaviour data to do stats on different level
def statsByLevel(data, lvl):
    resList = []
    
    for tempList in data[lvl]:
        for word in tempList:
            resList.append(word)
    
    df = pd.DataFrame({"tag_count":resList})
    #print(df)
    stats = df["tag_count"].value_counts().to_frame(name="tag_count")
    #print(stats)
    
    return stats

	
# get the first n labels of the stats
def getTopNLabels(stats, n):
    topLabels = stats[0:n].index.tolist()
    topLabelsDf = pd.DataFrame({"tag_name":topLabels})
    return topLabelsDf

	
# extract the montid, e.g. 201711 from behaviour data
def getMonthId(date):
    timeStamp = pd.to_datetime(date)
    year= timeStamp.year
    month = "{:02d}".format(timeStamp.month)
    
    month_id = str(year) + str(month)
    
    return month_id

	
def getOneYrMonths():
    months = []
    
    for n in range(0, 12):
        temp = datetime.now() - dt.timedelta(n*365/12)
        monthId = getMonthId(temp)
        months.append(monthId)
        
    return months

	
# 数据预处理，返回所有在列表中医生的行为数据
def dataPrepare(wechatRaw, webRaw, doctorList):
    
    # filter wechat data in doctorList 
    wechatColList = ["doctorid", "hcp_openid_u_2", "content_id", "content_title", "start_date", "duration"]
    wechatFilterd = wechatRaw[wechatRaw["doctorid"].isin(doctorList)][wechatColList]
    #print(wechatFilterd.shape)
    
    # filter web data in doctorList 
    webColList = ["doctorid", "content_id", "content_title", "start_date", "end_date"]
    webFilterd = webRaw[webRaw["doctorid"].isin(doctorList)][webColList]
    #print(webFilterd.shape)
    
    # Remove the invalid data: content title is 0
    validWechatLog = wechatFilterd[~(wechatFilterd.content_title == "0")].reset_index(drop=True)
    validWebLog = webFilterd[~(webFilterd.content_title == "0")].reset_index(drop=True)
    #print(validWechatLog.shape)
    #print(validWebLog.shape)
    
    # fill open id as null into webLog and concat required data into one df
    validWebLog.insert(1, "hcp_openid_u_2", np.nan)
    cbindData = pd.concat([validWechatLog[["doctorid", "hcp_openid_u_2", "content_title", "start_date"]],\
                                 validWebLog[["doctorid", "hcp_openid_u_2", "content_title", "start_date"]]]).reset_index(drop=True)
    #print(cbindData.shape)
    return cbindData


def createDictStop():
    """
    Load external dictionary and stop words
    """
    print("Loading Dictionary and Stopwords")
    global stopWord
    
    dic = nn.Dataframefactory("mappingword",sep = '\r\n')
    #dic = pd.read_csv(inPath+"/mappingWords_20181219.txt", sep="\r\n", engine="python")
    
    stopWord = nn.Dataframefactory("stopword",sep = '\r\n')
    #stopWord = pd.read_csv(inPath+"/StopWordFinal.txt", encoding="utf-8", sep="\r\n", engine="python")
    
    word = dic.word.tolist()   
    stopWord = stopWord.stopword.tolist()
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
        lv2Lb = [ x for x in lv2Lb if str(x) != 'nan']
        #lv1Lb= list(set(lv1Lb))
        #lv1Lb = [ x for x in lv1Lb if str(x) != 'nan']
        funcLb= list(set(funcLb))
        funcLb = [ x for x in funcLb if str(x) != 'nan']

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

	
def cbindAllConditions(novoHcpAgg):
    
    data = novoHcpAgg
    
    title = list(set(data["novo_hcp_ability_detailing_path.academic_title"]))
    title.append("全部")
    department = list(set(data["novo_hcp_ability_detailing_path.department"]))
    department.append("全部")
    level = list(set(data["novo_hcp_ability_detailing_path.level"]))
    level.append("全部")
    detailingPath = list(set(data["novo_hcp_ability_detailing_path.detailing_path_id"]))
    detailingPath.append("全部")
    
    allCombinations = list(itertools.product(detailingPath, level, title, department))
    allCbindDf = pd.DataFrame(data=allCombinations, columns=["detailing_path", "hcp_segment", "title", "department"])
    #allCbindDf["segment_id"] = allCbindDf.index + 1
    allCbindDf.insert(loc=0, column="segment_id", value=allCbindDf.index+1)
    
    return allCbindDf

	
def getSegDoctorList(allCbindDf, novoHcpAgg, segment_id):
    title = allCbindDf[allCbindDf["segment_id"]==segment_id]["title"][segment_id-1]
    #print(title)
    department = allCbindDf[allCbindDf["segment_id"]==segment_id]["department"][segment_id-1]
    #print(department)
    hcp_segment = allCbindDf[allCbindDf["segment_id"]==segment_id]["hcp_segment"][segment_id-1]
    #print(hcp_segment)
    detailing_path = allCbindDf[allCbindDf["segment_id"]==segment_id]["detailing_path"][segment_id-1]
    #print(detailing_path)
    
    if (title=="全部") & (department=="全部") & (hcp_segment=="全部") & (detailing_path=="全部"):
        segDoctorList = novoHcpAgg["novo_hcp_ability_detailing_path.customer_code"].tolist()
        
    elif (title=="全部") & (department=="全部") & (hcp_segment=="全部") & (detailing_path!="全部"):
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.detailing_path_id"]==detailing_path)]\
                                ["novo_hcp_ability_detailing_path.customer_code"].tolist()
        
    elif (title=="全部") & (department=="全部") & (hcp_segment!="全部") & (detailing_path=="全部"):
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.level"]==hcp_segment)]\
                                ["novo_hcp_ability_detailing_path.customer_code"].tolist()
        
    elif (title=="全部") & (department=="全部") & (hcp_segment!="全部") & (detailing_path!="全部"):
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.level"]==hcp_segment) 
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.detailing_path_id"]==detailing_path)]\
                                    ["novo_hcp_ability_detailing_path.customer_code"].tolist()
        
    elif (title=="全部") & (department!="全部") & (hcp_segment=="全部") & (detailing_path=="全部"):
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.department"]==department)]\
                                ["novo_hcp_ability_detailing_path.customer_code"].tolist()
        
    elif (title=="全部") & (department!="全部") & (hcp_segment=="全部") & (detailing_path!="全部"):
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.department"]==department) 
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.detailing_path_id"]==detailing_path)]\
                                    ["novo_hcp_ability_detailing_path.customer_code"].tolist()
        
    elif (title=="全部") & (department!="全部") & (hcp_segment!="全部") & (detailing_path=="全部"):
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.department"]==department) 
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.level"]==hcp_segment)]\
                                    ["novo_hcp_ability_detailing_path.customer_code"].tolist()
        
    elif (title=="全部") & (department!="全部") & (hcp_segment!="全部") & (detailing_path!="全部"):
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.department"]==department) 
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.level"]==hcp_segment) 
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.detailing_path_id"]==detailing_path)]\
                                    ["novo_hcp_ability_detailing_path.customer_code"].tolist()
        
    elif (title!="全部") & (department=="全部") & (hcp_segment=="全部") & (detailing_path=="全部"):
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.academic_title"]==title)]\
                                    ["novo_hcp_ability_detailing_path.customer_code"].tolist()
        
    elif (title!="全部") & (department=="全部") & (hcp_segment=="全部") & (detailing_path!="全部"):
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.academic_title"]==title) 
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.detailing_path_id"]==detailing_path)]\
                                    ["novo_hcp_ability_detailing_path.customer_code"].tolist()
        
    elif (title!="全部") & (department=="全部") & (hcp_segment!="全部") & (detailing_path=="全部"):
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.academic_title"]==title)
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.level"]==hcp_segment)]\
                                    ["novo_hcp_ability_detailing_path.customer_code"].tolist()
        
    elif  (title!="全部") & (department=="全部") & (hcp_segment!="全部") & (detailing_path!="全部"):
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.academic_title"]==title)
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.level"]==hcp_segment) 
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.detailing_path_id"]==detailing_path)]\
                                    ["novo_hcp_ability_detailing_path.customer_code"].tolist()
        
    elif (title!="全部") & (department!="全部") & (hcp_segment=="全部") & (detailing_path=="全部"):
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.academic_title"]==title) 
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.department"]==department)]\
                                    ["novo_hcp_ability_detailing_path.customer_code"].tolist()
        
    elif (title!="全部") & (department!="全部") & (hcp_segment=="全部") & (detailing_path!="全部"):
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.academic_title"]==title) 
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.department"]==department)
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.detailing_path_id"]==detailing_path)]\
                                    ["novo_hcp_ability_detailing_path.customer_code"].tolist()
        
    elif (title!="全部") & (department!="全部") & (hcp_segment!="全部") & (detailing_path=="全部"):
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.academic_title"]==title) 
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.department"]==department) 
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.level"]==hcp_segment)]\
                                    ["novo_hcp_ability_detailing_path.customer_code"].tolist()
    else:
        segDoctorList = novoHcpAgg[(novoHcpAgg["novo_hcp_ability_detailing_path.academic_title"]==title) 
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.department"]==department) 
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.level"]==hcp_segment) 
                                   &(novoHcpAgg["novo_hcp_ability_detailing_path.detailing_path_id"]==detailing_path)]\
                                    ["novo_hcp_ability_detailing_path.customer_code"].tolist()

    return segDoctorList




def main():
    tag = nn.Dataframefactory("tag")
    #tag = pd.read_excel(inPath+"/20181219_hcp_tag.xlsx")
    
    simi = nn.Dataframefactory("similar")
    #simi = pd.read_excel(inPath+"/20181219_tag_simi.xlsx")

    mapping =  mappingCbind(simi,tag)
    createDictStop()
    
    novoHcpAgg = nn.Dataframefactory("hcp_ability_detailing")
    #novoHcpAgg = pd.read_csv(inPath+"/novo_hcp_ability_detailing_path.txt", encoding="utf-8", engine="python")
    doctorList = list(set(novoHcpAgg["novo_hcp_ability_detailing_path.customer_code"]))
    
    wechat = nn.Dataframefactory("wechat")
    #wechat = pd.read_excel(inPath+"/webchat_content_view.xlsx")
    
    web = nn.Dataframefactory("web")
    #web = pd.read_excel(inPath+"/pc_data.xlsx")

    # 整合微信和网站的数据到同一个df
    cbindBehavData = dataPrepare(wechat, web, doctorList)
    print("Finished Data preparation")
    
    contentTitle = cbindBehavData['content_title'].dropna().drop_duplicates().to_frame()
    contentLabeled = titleLabeling(contentTitle,mapping)
    allBehavDataLabelled= cbindBehavData.merge(contentLabeled,left_on='content_title',right_on='content_title')
    allBehavDataLabelled["month_id"] = allBehavDataLabelled["start_date"].apply(getMonthId)

    # segment mapping file, write this table to Hive
    allCbindDf = cbindAllConditions(novoHcpAgg)
    print("Created segment mapping file")
    
    # do lv2 tag stats and get the top 15 labels
    allLv2Stats = statsByLevel(allBehavDataLabelled, "lv2_tag")
    topLv2LabelsDf = getTopNLabels(allLv2Stats, 15)
    print("Found top 15 tags of all doctors")
    
    # for seg in all segments, for each month in all months in the segment
    # calculate the heatmap data and chord diagram data
    heatMapPart = []
    chordMapPart = [] 
    print("Begin calculating")
    
    for segId in allCbindDf["segment_id"]:
        segDocList = getSegDoctorList(allCbindDf, novoHcpAgg, segId)
        if len(segDocList) != 0:
            segBehavData = allBehavDataLabelled[allBehavDataLabelled["doctorid"].isin(segDocList)]
            segHeatData = statsBySegment(segBehavData, segId, topLv2LabelsDf)
            heatMapPart.append(segHeatData)
            segChordData = chordStatsBySeg(segBehavData, segId)
            chordMapPart.append(segChordData)
       
    heatMapOutput = pd.concat(heatMapPart, ignore_index=True)
    chordMapOutput = pd.concat(chordMapPart, ignore_index=True)
    print("Finished calculating")
    return (heatMapOutput,chordMapOutput )   

