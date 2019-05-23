import pandas as pd
import numpy as np
import jieba
import re
import nndw as nn

iotype = 'db'


def createDictStop():
    """
    Load external dictionary and stop words
    """
    print("Loading Dictionary and Stopwords")
    global stopword
    
    dic = nn.Dataframefactory("mappingword",sep = '\r\n',iotype=iotype)    
    stopWord = nn.Dataframefactory("stopword",sep = '\r\n',iotype=iotype)
    
    word = dic.word.tolist()  
    stopword = stopWord.word.tolist()
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
    token = [word for word in wordList if (word not in stopword) and (word.strip()!="")]
    
    return token
        
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
    dataFrame['Token'] = dataFrame["keyword"].apply(tokenize)
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
        #funcLb = []
        for token in tokens:
            for index, row in keyTable.iterrows():
                if token in row['tag_similar_word']:
                    #labels.append(index)
                    lv2Lb.append(row['tag_name_lv2'])
                    #lv1Lb.append(row['tag_name_lv1'])
                    #funcLb.append(row['tag_name_pat'])


        #labels = list(set(labels))
        #labels = [ x for x in labels if str(x) != 'nan']
        lv2Lb= list(set(lv2Lb))
        lv2Lb = [ x for x in lv2Lb if x != '' and str(x) != 'nan']
        #lv1Lb= list(set(lv1Lb))
        #lv1Lb = [ x for x in lv1Lb if str(x) != 'nan']
        #funcLb= list(set(funcLb))
        #funcLb = [ x for x in funcLb if x != '' and str(x) != 'nan']

        return pd.Series([lv2Lb,])

    def filterComplication(lv2Label):
        for word in diabetes:
            if word in lv2Label:
                lv2Label.remove(word)
        for word in complication:
            if (word in lv2Label) and ('并发症/合并症') in lv2Label:
                lv2Label.remove('并发症/合并症')
        return lv2Label

    print("Labelling Title")
    dataFrame[['lv2_tag',]] = dataFrame['Token'].apply(labelIt)
    dataFrame['lv2_tag'] = dataFrame['lv2_tag'].apply(filterComplication)
    print("Finished Labelling")
    return dataFrame

        

def main():
    tag = nn.Dataframefactory("pat_tag",iotype = iotype)
    simi = nn.Dataframefactory("similar",iotype = iotype)
    
    mapping =  mappingCbind(simi,tag)
    createDictStop()
        
    print("Loading data")
    raw = nn.Dataframefactory("pat_search",iotype = iotype)
    pat_search = raw[(raw.platform=="1")&(raw.module=="小糖问答")][["hcp_openid", "keyword"]]
    print("Finished Data preparation")
        
    if pat_search.shape[0]==0:
        print("raw data is empty, please check the datawarehouse.")
    else:
        searchContents = pat_search["keyword"].dropna().drop_duplicates().to_frame()
        searchLabeled = titleLabeling(searchContents,mapping)
        contentLabeled = pat_search.merge(searchLabeled, left_on="keyword", right_on="keyword")
        validLabeled = contentLabeled[contentLabeled.lv2_tag.str.len()!=0]
        if validLabeled.shape[0]==0:
            print("no tags are labeled, please check the mapping file.")
        else:
            print("Begin calculating")
            finalDf = []

            for index, row in validLabeled.iterrows():
                keysDf = pd.DataFrame({"keyword":row["lv2_tag"]})
                keysDf["pat_search"] = row["keyword"]
                keysDf.insert(0, "pat_openid", row["hcp_openid"])
                finalDf.append(keysDf)
                        
            output = pd.concat(finalDf, ignore_index=True)
            print("Finished calculating")
                
            nn.write_table(output,'pat_search_stats', iotype = iotype)
            # pat_search_stats structure: three columns - pat_openid, keyword, pat_search
                
            return (1)



