# -*- coding: utf-8 -*-
"""
# @Author: Yubo HE
# @Date:   2018-12-27 10:48:51
# @Last Modified by:   Yubo HE
# @Last Modified time: 2018-12-28 15:04:31
# @Email: yubo.he@cn.imshealth.com
"""

import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import jieba
import re
from datetime import datetime
#import nndw

import os
from collections import Counter
from functools import wraps
from time import time
import nndw as nn

iotype = 'db'

def timing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time()
        result = f(*args, **kwargs)
        end = time()
        print("func:{}, time elaps:{:.0f}m {:.0f}s".format(
            f.__name__, (end-start)//60, (end-start) % 60))
        return result
    return wrapper


@timing
def createDictStop():
    """
    Load external dictionary and stop words
    """
    print("Loading Dictionary and Stopwords")
    global stopWord

    dic = nn.Dataframefactory("mappingword",sep = '\r\n',iotype=iotype)
   
    stopWord = nn.Dataframefactory("stopword",sep = '\r\n',iotype=iotype)

    word = dic.word.tolist()
    stopWord = stopWord.stopword.tolist()
    jieba.re_han_default = re.compile(
        r'([\u0020\u4e00-\u9fa5a-zA-Z0-9+#&._%/β/α/-]+)', re.UNICODE)
    frequnecy = 1000000000000000000000
    # Add words to dictionary
    for words in word:
        jieba.add_word(words, frequnecy)
    print("Dictionary and StopWord have been loaded")


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
    simiList = tagSimilarWords.groupby(["tag_id", "tag_name"])[
        "tag_similar_word"].apply(list).to_frame().reset_index()

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
    mapping = lv1Hcp[["tag_similar_word",
                      "tag_name_lv2", "tag_name_lv1", "tag_name_hcp"]]

    return mapping


def segContent(sentence):
    """
    切词模块
    """
    sentence = sentence.replace('\n', '').replace(
        '\u3000', '').replace('\u00A0', '').replace('\xa0', '')
    sentence = re.sub('\s+', ' ', sentence)
    segs = jieba.cut(sentence, cut_all=False)
    outList = [seg for seg in segs if
               seg not in stopWord and not re.match('^[0-9|.|%]*$', seg) and not re.match('\s*[\.|\-]\s*', seg)]

    return outList


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
    dataFrame['Token'] = dataFrame['content_title'].apply(segContent)
    diabetes = ['糖尿病', '2型糖尿病']
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
        labels = [x for x in labels if str(x) != 'nan']
        lv2Lb = list(set(lv2Lb))
        lv2Lb = [x for x in lv2Lb if str(x) != 'nan']
        lv1Lb = list(set(lv1Lb))
        lv1Lb = [x for x in lv1Lb if str(x) != 'nan']
        funcLb = list(set(funcLb))
        funcLb = [x for x in funcLb if str(x) != 'nan']

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
    dataFrame[['labels', 'HCP标签', '一级标签', '二级标签']
              ] = dataFrame['Token'].apply(labelIt)
    dataFrame['二级标签'] = dataFrame['二级标签'].apply(filterComplication)
    return dataFrame

# 数据预处理，返回为五个data frame


@timing
def dataPrepare(wechatRaw, webRaw):

    # content need to be filtered
    content_filtered = ["向黄金周坚守一线的工作者致敬",
                        "小龙人祝您中秋快乐",
                        "早期联合：血糖早期达标，患者远期获益",
                        "《龙门秘笈》—2型糖尿病合并慢性肾脏病之病例分享",
                        "更早干预，更早达标，赢在糖尿病治疗的起跑线",
                        "胰岛β细胞我们知多少",
                        "在一起，更出彩——瑞格列奈+二甲双胍是尽早联合的不二之选",
                        "大唐龙神探——糖前别慌张，龙龙来帮忙",
                        "控糖我来说——2型糖尿病合并肥胖症及动脉粥样硬化症患者之病例分享",
                        "抗衰老激素Klotho水平降低预测2型糖尿病患者的肾功能下降",
                        "大糖TV倾力巨献《糖人街探案》之糖人怪相：诺和龙患者肖像卡",
                        "老年T2DM患者降糖方案的选择"
                        ]

    # filter wechat data having doctorid
    wechatColList = ["doctorid", "hcp_openid_u_2", "content_id", "content_title",
                     "start_date", "duration", "thumbs_up", "collected", "share"]

    wechatRaw[["thumbs_up", "collected", "share"]] = wechatRaw[["thumbs_up", "collected", "share"]] \
        .where(wechatRaw[["thumbs_up", "collected", "share"]]
               .isnull(), 1)\
        .fillna(0) \
        .astype(int)

    wechatFilterd = wechatRaw[~wechatRaw.doctorid.isnull()][wechatColList]

    # filter web data having doctorid
    webColList = ["doctorid", "content_id",
                  "content_title", "start_date", "end_date", "thumbs_up", "collected", "share"]

    def web_behavior_process(x):
        share = 1 if "分享" in x else 0
        thumbs_up = 1 if "点击标签" in x else 0
        collect = 1 if "收藏" in x else 0

        return pd.Series([thumbs_up, collect, share])

    webRaw["key_operation"].fillna("空", inplace=True)
    webRaw[["thumbs_up", "collected", "share"]
           ] = webRaw["key_operation"].apply(web_behavior_process)
    webFilterd = webRaw[~webRaw.doctorid.isnull()][webColList]

    # use the wechatFilterd and webFilterd for channel preference calculation

    # Remove the invalid data: content title is 0
    validWechatLog = wechatFilterd[~((wechatFilterd.content_title.isnull()) | (wechatFilterd.content_title.isin(content_filtered)))] \
        .reset_index(drop=True)
    validWebLog = webFilterd[~((webFilterd.content_title.isnull()) | (webFilterd.content_title.isin(content_filtered)))] \
        .reset_index(drop=True)
    # use validWechatLog and validWebLog as parameters for reading history without tokens

    # prepare data for content preference calculation
    # fill open id as null into webLog and concat required data into one df
    validWebLog.insert(1, "hcp_openid_u_2", np.nan)
    PrefCols = ["doctorid", "hcp_openid_u_2", "content_id",
                "content_title", "thumbs_up", "collected", "share"]
    contentPrefData = pd.concat([validWechatLog[PrefCols], validWebLog[PrefCols]])\
        .reset_index(drop=True)

    wechatLog = validWechatLog[[
        "doctorid", "hcp_openid_u_2", "content_id", "content_title", "start_date"]]
    webLog = validWebLog[["doctorid", "hcp_openid_u_2",
                          "content_id", "content_title", "start_date"]]
    LogData = pd.concat([wechatLog, webLog]).reset_index(drop=True)
    LogData["start_date"] = pd.to_datetime(LogData["start_date"])

    return wechatFilterd, webFilterd, validWechatLog, validWebLog, contentPrefData, LogData


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
    def countHcpValue(hcp_list, weight):
        return {i: weight for i in hcp_list}

    df = taggedDf[taggedDf['doctorid'] == hcp_id]

    df["weight"] = df["thumbs_up"] * 1.5 + \
        df["share"] * 2 + df["collected"] * 2 + 1
    df['dict'] = df[['HCP标签', 'weight']].apply(
        lambda x: countHcpValue(*x), axis=1)

    hcp_lb = df["HCP标签"].tolist()
    open_id = df.hcp_openid_u_2.iloc[0]
    dic_list = df["dict"].tolist()
    hcp_lb_uq = set([item for sublist in hcp_lb for item in sublist])

    lb_weight = {}
    for key in hcp_lb_uq:
        value = 0
        for dic in dic_list:
            value += dic.get(key, 0)
        lb_weight[key] = value

    lb_count = []
    for labels in df["HCP标签"]:
        lb_count.extend(labels)
    lb_count = dict(Counter(lb_count))

    dic = {'Content_Interest': list(
        lb_weight.keys()), 'Ratio': list(lb_weight.values())}
    contentInsteret = pd.DataFrame(dic)
    contentInsteret.sort_values(by='Ratio', ascending=False, inplace=True)
    contentInsteret.reset_index(drop=True, inplace=True)

    if contentInsteret.shape[0] > 5:
        others = ['其他', contentInsteret[5:].Ratio.sum()]
        otherTags = contentInsteret[5:]['Content_Interest'].tolist()
        contentInsteret.drop(contentInsteret.index[5:], inplace=True)
        contentInsteret.loc[5] = others
    else:
        otherTags = []

    total = contentInsteret['Ratio'].apply('sum')
    contentInsteret['Ratio'] = contentInsteret['Ratio'].apply(
        lambda x: "{0:.0%}".format(x/total))
    contentInsteret['Open_ID'] = open_id
    contentInsteret['HCP_ID'] = hcp_id
    contentInsteret['last_update'] = pd.Timestamp(
        "now").strftime("%Y-%m-%d %H:%M:%S")
    contentInsteret['ID'] = contentInsteret.index + 1
    outputVar = ['ID', 'Open_ID', 'HCP_ID',
                 'Content_Interest', 'Ratio', 'last_update']
    contentInsteret = contentInsteret[outputVar]
    labelMap = dict(
        zip(contentInsteret['Content_Interest'].tolist(), contentInsteret['ID'].tolist()))

    return contentInsteret, otherTags, lb_count, labelMap


def calContKeyWord(taggedDf, hcp_id, lb, other_tag, mapping, keytable):
    df = taggedDf[taggedDf['doctorid'] == hcp_id]

    # create a dict of HCP labels
    dicHcpLb = {}
    for idx, key in enumerate(lb.keys()):
        l = []
        for i, row in df.iterrows():
            if key in row.HCP标签:
                l.append(i)
        dicHcpLb[key] = l

    #
    contKey = {}
    for key in dicHcpLb.keys():
        lv2LbList = df.loc[dicHcpLb[key]].二级标签.tolist()
        lv2label = keytable[keytable['tag_name_hcp']
                            == key].tag_name_lv2.tolist()
        flatList = [item for sublist in lv2LbList for item in sublist]
        lv2Cnt = [x for x in flatList if x in lv2label]
        contKeyWord = dict(Counter(lv2Cnt))
        contKey[key] = contKeyWord

    if other_tag:
        z = [contKey[x] for x in other_tag]
        contKey['其他'] = {k: v for d in z for k, v in d.items()}
        for k in other_tag:
            contKey.pop(k, None)

    keywordCnt = pd.DataFrame()
    for key, item in contKey.items():
        #keywordCnt['Content_Interest_ID'] = key
        df_join = pd.DataFrame.from_dict(
            item, orient='index', columns=['keyword_count'])
        df_join.reset_index(inplace=True)
        df_join.rename(columns={"index": "keyword"}, inplace=True)
        df_join.sort_values(by=['keyword_count'],
                            ascending=False, inplace=True)
        df_join['last_update'] = pd.Timestamp(
            "now").strftime("%Y-%m-%d %H:%M:%S")
        df_join['Content_Interest_ID'] = key
        keywordCnt = keywordCnt.append(df_join, ignore_index=True)

    keywordCnt["HCP_ID"] = hcp_id
    keywordCnt["Content_Interest_ID"] = keywordCnt["Content_Interest_ID"].map(
        mapping)
    outputVar = ['HCP_ID', 'Content_Interest_ID',
                 'keyword', 'keyword_count', 'last_update']
    keywordCnt = keywordCnt[outputVar]
    return keywordCnt


# 渠道偏好
@timing
def channelPref(wechatRaw, webRaw):

    # record start algorithm start time
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # aggregate the counts in different channel
    wechatAggRes = wechatRaw.groupby("doctorid").size(
    ).reset_index(name="Wechat_Content_Count")
    webAggRes = webRaw.groupby("doctorid").size(
    ).reset_index(name="Web_Content_Count")

    # merge two channels and fillna
    # 这里是否需要fillna待定，因为数据展示的时候，如果微信渠道为0，可以直接不展示微信渠道
    resCbind = pd.merge(wechatAggRes, webAggRes,
                        on="doctorid", how="outer").fillna(0)

    # add time stamp to df
    resCbind["last_update"] = time

    # change data formats
    resCbind[["Wechat_Content_Count", "Web_Content_Count"]] = resCbind[[
        "Wechat_Content_Count", "Web_Content_Count"]].astype(int)
    resCbind["last_update"] = pd.to_datetime(resCbind["last_update"])
    resCbind.rename(columns={'doctorid': 'hcp_id'}, inplace=True)

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
    webLog = webLog[webLog.view_length >= 30]

    # combine required columns into a dataframe, without tokens
    res = webLog[["doctorid", "content_id", "content_title",
                  "start_date"]].reset_index(drop=True)
    res.insert(0, "hcp_openid_u_2", np.nan)

    return res


def wechatHistWithoutTokens(wechatLog):

    # filter the data with view lenth >= 30s
    validLog = wechatLog[wechatLog.duration >= 30].reset_index(drop=True)

    # filter the required columns
    resCbind = validLog[["hcp_openid_u_2", "doctorid",
                         "content_id", "content_title", "start_date"]]

    # change the date to timestamp
    resCbind["start_date"] = pd.to_datetime(resCbind.start_date)

    return resCbind


def readingHist(webHistWithoutTokens, wechathistWithoutTokens, contentLabeled):
    # 整合阅读历史并且添加文章的二级标签
    allHistCbind = pd.concat([webHistWithoutTokens, wechathistWithoutTokens])

    allHistWithTags = allHistCbind.merge(contentLabeled, how="left",
                                         left_on="content_title", right_on="content_title")

    allHistWithLv2Tags = allHistWithTags[[
        "hcp_openid_u_2", "doctorid", "content_id", "content_title", "二级标签", "start_date"]]

    res = allHistWithLv2Tags.rename(columns={
                                    "hcp_openid_u_2": "open_id", "doctorid": "hcp_id", "二级标签": "content_keyword", "start_date": "browser_time"})
    res["content_keyword"] = res["content_keyword"].apply(
        lambda x: ' '.join(x))
    return res


def get_content_uniq(LogData):
    """
    得到每篇文章的流行度
    """
    first_click = LogData.groupby(["content_title"])[
        "start_date"].min().to_frame().reset_index()
    view_count = LogData.groupby(
        ["content_title"]).size().to_frame().reset_index()
    view_count = view_count.rename(columns={0: "click_times"})
    content_uq = LogData[["content_id", "content_title"]]
    content_uq = content_uq.drop_duplicates(subset="content_title")
    content_uq.reset_index(drop=True, inplace=True)
    content_uq = content_uq.merge(first_click, on="content_title")
    content_uq = content_uq.merge(view_count, on="content_title")
    content_uq.rename(columns={"start_date": "first_click_time"}, inplace=True)
    content_uq["current_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content_uq["current_time"] = pd.to_datetime(content_uq["current_time"])
    content_uq["first_click_time"] = pd.to_datetime(
        content_uq["first_click_time"])
    content_uq["diff"] = content_uq["current_time"] - \
        content_uq["first_click_time"]
    content_uq["diff_sec"] = content_uq["diff"].dt.total_seconds()
    content_uq["popularity"] = content_uq["click_times"] / \
        content_uq["diff_sec"]
    content_uq = content_uq.sort_values(
        by=["popularity"], ascending=False).reset_index(drop=True)

    return content_uq


def get_hcp_reading_history(LogData):
    """
    得到每个医生所阅读过的字典
    """
    doctorid_uq = set(LogData.doctorid.tolist())
    hcp_reading_history = {}
    for doc_id in doctorid_uq:
        reading_history = LogData[LogData["doctorid"]
                                  == doc_id]["content_title"].tolist()
        hcp_reading_history[doc_id] = set(reading_history)

    return hcp_reading_history


def get_uniq_doctorid(LogData):
    # 得到每个医生的list
    doctorid_uq = set(LogData.doctorid.tolist())
    return doctorid_uq


def get_hcp_label_uniq(mapping):
    # 拿出HCP标签UNQ
    hcp_lb_uq_na = list(mapping.tag_name_hcp.unique())
    hcp_lb_uq = [x for x in hcp_lb_uq_na if str(x) != 'nan']

    return hcp_lb_uq


def create_var(labels, uniq_hcp_label):
    return pd.Series(map(lambda x: 1 if x in labels else 0,  uniq_hcp_label))


def p2f(x):
    return float(x.strip('%'))/100


def get_most_interest_keyword(dataframe, doctorid):

    error = "其他"
    doctor_keyword = dataframe[dataframe["HCP_ID"] == doctorid]
    pre_point = doctor_keyword.Ratio.unique()
    pre_point.sort()

    maxRatio = pre_point[-1]
    most_interest_keyword = doctor_keyword[doctor_keyword["Ratio"]
                                           == maxRatio]["Content_Interest"].tolist()

    if error in most_interest_keyword:
        most_interest_keyword.remove(error)

    if not most_interest_keyword:
        maxRatio = pre_point[-2]
        most_interest_keyword = doctor_keyword[doctor_keyword["Ratio"]
                                               == maxRatio]["Content_Interest"].tolist()

    return most_interest_keyword


def get_hcp_tech_class(novo_hcp, novo_market, doctorid_uq, hcp_reading_history):

    hcp_info = novo_hcp[novo_hcp["customer_code"].isin(
        doctorid_uq)].reset_index(drop=True)
    hcp_info.drop_duplicates(inplace=True)
    hcp_info_pro = hcp_info.merge(
        novo_market, left_on="county", right_on="area")

    hcp_tech_class = hcp_info_pro.groupby(["market_name", "academic_title"])[
        "customer_code"].apply(list)
    hcp_tech_class = hcp_tech_class.to_frame()
    hcp_tech_class.reset_index(inplace=True)
    hcp_tech_class["content_title"] = hcp_tech_class["customer_code"].apply(
        get_loc_title_content, args=(hcp_reading_history,))
    hcp_tech_class["class_id"] = hcp_tech_class.index+1.0

    return hcp_tech_class, hcp_info_pro


def get_loc_title_content(doctorid, hcp_reading_history):
    hist_content = [hcp_reading_history.get(doc_id) for doc_id in doctorid]
    hist_content = list(
        set([item for sublist in hist_content for item in sublist]))

    return hist_content


def get_hcp_class_mapping(hcp_info_pro, hcp_tech_class, doctorid_uq):
    doctorid_uq_df = pd.DataFrame(list(doctorid_uq), columns=["doctorid"])
    doctorid_uq_df = doctorid_uq_df.merge(
        hcp_info_pro, left_on="doctorid", right_on="customer_code", how="left")
    doctorid_uq_class_df = pd.merge(doctorid_uq_df,
                                    hcp_tech_class[[
                                        "market_name", "academic_title", "class_id"]],
                                    left_on=["market_name", "academic_title"],
                                    right_on=["market_name", "academic_title"],
                                    how="left")
    hcp_class_mapping = dict(
        zip(doctorid_uq_class_df["doctorid"], doctorid_uq_class_df["class_id"]))

    return hcp_class_mapping


def get_hcp_class(hcp_tech_class, hcp_class_mapping, doctorid, content_pop):
    hcp_class = hcp_tech_class[hcp_tech_class["class_id"] == hcp_class_mapping.get(
        doctorid)]["content_title"].tolist()[0]
    content_class = content_pop[content_pop["content_title"].isin(hcp_class)]
    return content_class


def main():
    print("Designed for Novo4PE-Pilot")
    print("------------------------------------------------------")
    print("Step 1: loading necessary data")
    tag = nn.Dataframefactory('tag',iotype = iotype) 

    simi = nn.Dataframefactory('similar',iotype = iotype)

    mapping = mappingCbind(similar, tag)

    web = nn.Dataframefactory("web",iotype = iotype)

    wechat = nn.Dataframefactory("wechat",iotype = iotype) 

    novo_hcp = nn.Dataframefactory("novo_hcp",iotype = iotype)
    
    novo_market = nn.Dataframefactory("novo_hcp_market",iotype = iotype)

    print("Step 1: Done")
    print("------------------------------------------------------")
    print("Step 2: Creating dictionary")
    createDictStop()
    print("Step 2: Done")
    print("------------------------------------------------------")
    print("Step 3: Processing Raw Data")
    wechatFilterd, webFilterd, validWechatLog, validWebLog, contentPrefData, LogData = dataPrepare(
        wechat, web)
    print("Step 3: Done")
    print("------------------------------------------------------")
    print("Step 4: Caculating Channel Preference")
    output1 = channelPref(wechatFilterd, webFilterd)
    print("Step 4: Done")
    cotentTitle = contentPrefData['content_title'].dropna(
    ).drop_duplicates().to_frame()
    contentLabeled = titleLabeling(cotentTitle, mapping)
    contentNew = contentPrefData.merge(
        contentLabeled, left_on='content_title', right_on='content_title')
    print("------------------------------------------------------")
    print("Step 5: Caculating HCP Content Preference and Interest Point")
    output2 = pd.DataFrame()
    output3 = pd.DataFrame()
    for dc_id in contentNew.doctorid.unique():
        contentInsteret, otherTags, lb, labelMap = calContInst(
            contentNew, dc_id)
        keywordCnt = calContKeyWord(
            contentNew, dc_id, lb, otherTags, labelMap, mapping)
        output2 = output2.append(contentInsteret)
        output3 = output3.append(keywordCnt)
    output2.reset_index(drop=True, inplace=True)
    output3.reset_index(drop=True, inplace=True)
    print("Step 5: Done")
    print("------------------------------------------------------")
    print("Step 6: Caculating HCP reading History")
    webHistWithoutToken = webHistWithoutTokens(validWebLog)
    wechathistWithoutToken = wechatHistWithoutTokens(validWechatLog)
    output4 = readingHist(webHistWithoutToken,
                          wechathistWithoutToken, contentLabeled)
    print("Step 6: Done")
    content_uq = get_content_uniq(LogData)
    hcp_reading_history = get_hcp_reading_history(LogData)
    doctorid_uq = get_uniq_doctorid(LogData)
    hcp_lb_uq = get_hcp_label_uniq(mapping)
    content_lb = contentLabeled[["content_title", "HCP标签"]]
    content_lb_pop = content_lb.merge(
        content_uq[["content_id", "content_title", "popularity"]], on="content_title")
    # 更新表结构 ！！！HCP标签的 好计算
    content_lb_pop[hcp_lb_uq] = content_lb_pop["HCP标签"].apply(
        create_var, args=(hcp_lb_uq,))
    hcp_tech_class, hcp_info_pro = get_hcp_tech_class(
        novo_hcp, novo_market, doctorid_uq, hcp_reading_history)
    content_pop = content_lb_pop[["content_title", "popularity"]]
    hcp_class_mapping = get_hcp_class_mapping(
        hcp_info_pro, hcp_tech_class, doctorid_uq)
    print("------------------------------------------------------")
    print("Step 7: Generating HCP Personal Recommendation List")
    o2 = output2.copy()
    o2["Ratio"] = o2.Ratio.apply(p2f)
    output5 = pd.DataFrame()
    for doc_id in doctorid_uq:
        test = pd.DataFrame(np.nan, index=range(0, 5), columns=[
                            "doctorid", "rec_cnt", "method1", "method2", "method3"])

        test["method1"] = content_lb_pop[~content_lb_pop["content_title"].isin(hcp_reading_history.get(doc_id))] \
            .sort_values('popularity', ascending=False) \
            .head(5) \
            .content_title \
            .reset_index(drop=True)
    ###################################################################################################
        inst_list = get_most_interest_keyword(o2, doc_id)
        personal_rec = content_lb_pop[content_lb_pop[inst_list].any(1)]
        test["method2"] = personal_rec[~personal_rec["content_title"].isin(hcp_reading_history.get(doc_id))] \
            .sort_values('popularity', ascending=False) \
            .head(5) \
            .content_title \
            .reset_index(drop=True)
    ###################################################################################################
        try:
            hcp_class_content = get_hcp_class(
                hcp_tech_class, hcp_class_mapping, doc_id, content_pop)
        except IndexError:
            hcp_class_content = pd.DataFrame(
                columns=["content_title", "popularity"])

        test["method3"] = hcp_class_content[~hcp_class_content["content_title"].isin(hcp_reading_history.get(doc_id))] \
            .sort_values('popularity', ascending=False) \
            .head(5) \
            .content_title \
            .reset_index(drop=True)
        test["doctorid"] = doc_id
        test["rec_cnt"] = test.index + 1

        output5 = output5.append(test)

    output5 = output5.reset_index(drop=True)
    print("Step 7: Done")
    print("------------------------------------------------------")
    print("ALL COMPLETE")
    
    return(1)

