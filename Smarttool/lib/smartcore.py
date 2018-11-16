# -*- coding: utf-8 -*-
"""
# @Author: Yubo HE
# @Date:   2018-11-08 17:36:05
# @Last Modified by:   Yubo HE
# @Last Modified time: 2018-11-08 17:42:48
# @Email: yubo.he@cn.imshealth.com
""" 
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import jieba
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.externals import joblib

from datetime import datetime
import os
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
    dic_path = '../resource/'
    jieba.load_userdict(dic_path + "mappingWordFinal.txt")
    dic = pd.read_csv(dic_path + "mappingWordFinal.txt", engine='python', sep='\r\n')
    word = dic.word.tolist()   
    stopWord = pd.read_csv(dic_path + 'StopWordFinal.txt',encoding='utf-8', engine='python',sep='/r/n')  
    stopWord = stopWord.stopword.tolist()
    stopWord.append(" ")
    jieba.re_han_default =re.compile(r'([\u0020\u4e00-\u9fa5a-zA-Z0-9+#&._%/β/α/-]+)', re.UNICODE)
    frequnecy = 100000000000000000000000
    # Add words to dictionary
    for words in word:
        jieba.add_word(words,freq=frequnecy)
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
    sentence = re.sub('\s+',' ',sentence)
    segs = jieba.cut(sentence,cut_all=False)
    outList = [seg for seg in segs if seg not in stopWord and  not re.match('^[0-9|.|%]*$',seg) and not re.match('\s*[\.|\-]\s*',seg)]
    
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

def toDictionary(df):
    data=[]
    col = []
    for lb in df.columns:
        lbs = df[lb].loc[0]
        cols = [lb+'_lb_{}'.format(i) for i in range(1,len(lbs)+1)]
        data.extend(lbs)
        col.extend(cols)
    dic = dict(zip(col, data))
    return dic

def calcTfidf(newseg, vectorizer):
    response = vectorizer.transform([newseg])
    tf_idf = response.toarray()
    return tf_idf

def calcSimilarity(tfidf,tfidf_matix,title_list,top_n = 5):
    cosine_similarities = cosine_similarity(tfidf,tfidf_matix)
    similar_indices = cosine_similarities.argsort().flatten()[-top_n:]
    similar_items = sorted([(title_list[i], cosine_similarities[0,i]) for i in similar_indices], key=lambda x: -x[1])
    return similar_items



def Worker(contentqueue,labelqueue):

    def loading_everything():
    
        global tag,similar,mapping,clf,tfidf_matrix,labeled_corpus,title_list        
        createDictStop()
        tag = pd.read_csv('../resource/tag.csv')
        print('tag')
        similar = pd.read_csv('../resource/tag_similar_words.csv')
        print('similar')
        mapping =  mappingCbind(similar,tag)
        print('mapping')
        clf = joblib.load('../resource/vectorizer.joblib')
        print('clf')
        tfidf_matrix = np.load('../resource/tfidf.npy')
        print('tfidf')
        labeled_corpus = pd.read_excel('../resource/labeledContent.xlsx')
        print('corpus')
        title_list = labeled_corpus.title.tolist()
        print('title_list')
    
        #initiate
    loading_everything()
    print('[INFO]algorithm launched, smarttool is ready for serve')

    while True:
        request = contentqueue.get(block=True)
        print('[INFO]Worker get request from contentq, request sequence ' + str(request.rseq()))
        
        if request.rtype() == 'RELOAD':
          
        #reload every thing algorithm need 
            loading_everything()
            print('[INFO]algorithm reloaded, smarttool is ready for serve') 

        elif request.rtype() == 'CALCULATE':    
         
            start = time()
       
            inputdict = request.rdata() 
    
            df = pd.DataFrame(inputdict,index=[0])
            df["title_token"]= df.title.apply(segContent)
            df["all"] = df["title"] + "" + df["content"]
            df["all_token"] = df["all"].apply(segContent)
            seg = ' '.join(df["all_token"][0])
    
    #title tagging
            df[['lb','hcp','lv1','lv2']] = df.title_token.apply(labelIt,args=(mapping, ))
            df['lv2'] = df['lv2'].apply(filterComplication)
    
            title_lv1 = df['lv1'][0]
            title_lv2 = df['lv2'][0]
    
    #content tagging
            tfidf = calcTfidf(seg,clf)
            similar_items = calcSimilarity(tfidf,tfidf_matrix,title_list,5)
    
            similarTitle = [i[0] for i in similar_items] 
            similarScore = [i[1] for i in similar_items] 
            #print("Article {} \n has the following similar articles".format(df["title"][0]))
            #print("---------------------------------------")
            #print(*similarTitle,sep = "\n")
            #print("---------------------------------------")
    
            content_lv1_raw = labeled_corpus[labeled_corpus.title.isin(similarTitle)]['lv1'].str.split(',').tolist()
            content_lv2_raw = labeled_corpus[labeled_corpus.title.isin(similarTitle)]['lv2'].str.split(',').tolist()
            cleaned_content_lv1 = [x for x in content_lv1_raw if str(x) != 'nan']
            cleaned_content_lv2 = [x for x in content_lv2_raw if str(x) != 'nan']
            content_lv1 = [item for sublist in cleaned_content_lv1 for item in sublist]
            content_lv2 = [item for sublist in cleaned_content_lv2 for item in sublist]
    
    
            lv1_tags = list(set(content_lv1 + title_lv1))
            lv2_tags = list(set(content_lv2 + title_lv2))
    
            out = pd.DataFrame({"lv1":[lv1_tags],"lv2":[lv2_tags]})
    
            final = toDictionary(out)
            #print(inputtuple[0])
            #print(final)
            end = time()
            print(end-start)
            labelqueue.put((request.rseq(),final))

        elif request.rtype() == 'SHUTDOWN':
            print('[INFO]worker down')
            break;
