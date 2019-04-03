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

import nndw as nn

import nnenv

iotype = 'db'

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
    #dic_path = '../resource/'
    #jieba.load_userdict(dic_path + "mappingWordFinal.txt")
    dic = nn.Dataframefactory('mappingword',sep = '/r/n',iotype='fs')
    word = dic.word.tolist()   
    stopWord = nn.Dataframefactory('stopword',sep = '/r/n',iotype='fs')  
    stopWord = stopWord.word.tolist()
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

def calcSimilarity_m2(tfidf,tfidf_matix,top_n = 5):
    cosine_similarities = cosine_similarity(tfidf,tfidf_matix)
    similar_indices = cosine_similarities.argsort().flatten()[-top_n:]
    print(similar_indices)
    print(cosine_similarities)
    index_similarity_list = []
    for x in similar_indices:
        index_similarity_list.append({'index': x,'cosine_similarity':cosine_similarities[0,x] })            
    df = pd.DataFrame(index_similarity_list)
    print(df)
    return(df)

def getContentid(df_content_id_mapping,df_index_similarity):
    
    df = pd.merge(df_content_id_mapping,df_index_similarity, on = 'index')
    print(df)
    return(df)   

def Worker(contentqueue,labelqueue,slave_id):

    def loading_everything():
    
        global tag,similar,mapping,clf,tfidf_matrix,labeled_corpus,title_list,content_id_mapping        
        createDictStop()
        tag = nn.Dataframefactory('tag',iotype='fs')
        similar = nn.Dataframefactory('similar',iotype='fs') 
        mapping =  mappingCbind(similar,tag)

        clf = nn.Joblibfactory(nnenv.getItem('vectorizer'))
        tfidf_matrix = nn.Numpyarrayfactory(nnenv.getItem('tfidf'))

        labeled_corpus = nn.Dataframefactory('labeledContent',sep = '|',iotype='db',con=nnenv.getItem('mysql_url'))
        title_list = labeled_corpus.title.tolist()
    
        content_id_mapping = nn.Dataframefactory('content_id_mapping',iotype='fs')

        #initiate
    loading_everything()
    print('[INFO]algorithm launched, smarttool is ready for serve,[slave_id]' + str(slave_id))

    while True:
        request = contentqueue.get(block=True)
        print('[INFO]Worker get request from contentq, request sequence ' + str(request.rseq()) + ' with [slave_id]' + str(slave_id))
        
        if request.rtype() == 'RELOAD':
          
        #reload every thing algorithm need 
            loading_everything()
            print('[INFO]algorithm reloaded, smarttool is ready for serve,[slave_id]' + str(slave_id)) 

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

            df_similarity = calcSimilarity_m2(tfidf,tfidf_matrix,5)
            df_merge = getContentid(content_id_mapping,df_similarity)
             
            content_id_list = df_merge['content_id'].tolist()
            
           # content_lv1_raw = labeled_corpus[labeled_corpus.content_id.isin(content_id_list)]['lv1'].str.split(',').tolist()
            content_lv2_raw = labeled_corpus[labeled_corpus.content_id.isin(content_id_list)]['labels'].str.split(',').tolist()
           # cleaned_content_lv1 = [x for x in content_lv1_raw if str(x) != 'nan']
            cleaned_content_lv2 = [x for x in content_lv2_raw if str(x) != 'nan']
           # content_lv1 = [item for sublist in cleaned_content_lv1 for item in sublist]
            content_lv2 = [item for sublist in cleaned_content_lv2 for item in sublist]
    
    
            #lv1_tags = list(set(content_lv1 + title_lv1))
            lv2_tags = list(set(content_lv2 + title_lv2))
    
            #out = pd.DataFrame({"lv1":[lv1_tags],"lv2":[lv2_tags]})
            out = pd.DataFrame({"lv2":[lv2_tags]})
    
            final = toDictionary(out)
            #print(inputtuple[0])
            #print(final)
            end = time()
            print(end-start)
            labelqueue.put((request.rseq(),final))

 
        elif request.rtype() =='TEST':
            print('[INFO]signal get for TEST')
  
            final = {'test':4321}
            labelqueue.put((request.rseq(),final))


        elif request.rtype() == 'SHUTDOWN':
            print('[INFO]worker down with [slaveid]' + str(slave_id))
            break;
