#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project  : smarttool
# @FileName : createTFIDFmatrix.py
# @Created  : 09 Nov 2018 9:54 AM
# @Author   : Yubo He(yubo.he@cn.imehealth.com)
"""
import pandas as pd
import numpy as np
import re
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib

from datetime import datetime
import os
from functools import wraps
from time import time

import nndw as nn

import nnenv

def timing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time()
        result = f(*args, **kwargs)
        end = time()
        print("func:{}, time elaps:{:.0f}m {:.0f}s".format(f.__name__, (end - start) // 60, (end - start) % 60))
        return result

    return wrapper


@timing
def createDictStop():
    """
    Load external dictionary and stop words
    """
    print("Loading Dictionary and Stopwords")
    global stopWord
    dic = nn.Dataframefactory(nn.getName('mappingword'),sep = '/r/n')
    word = dic.word.tolist()
    stopWord = nn.Dataframefactory(nn.getName('stopword'),sep = '/r/n') 
    stopWord = stopWord.stopword.tolist()
    stopWord.append(" ")
    jieba.re_han_default = re.compile(r'([\u0020\u4e00-\u9fa5a-zA-Z0-9+#&._%/β/α/-]+)', re.UNICODE)
    frequnecy = 100000000000000000000000
    # Add words to dictionary
    for words in word:
        jieba.add_word(words, freq=frequnecy)
    print("Finished Dic Loading")


def segment(text):
    sentence = text.replace('\n', '').replace('\u3000', '').replace('\u00A0', '').replace('\xa0', '')
    sentence = re.sub('\s+', ' ', sentence)
    segs = jieba.cut(sentence, cut_all=False)
    outList = [seg for seg in segs if
               seg not in stopWord and not re.match('^[0-9|.|%]*$', seg) and not re.match('\s*[\.|\-]\s*', seg)]
    outStr = ' '.join(outList)
    return outStr

def combineTitleAndContent(dataset):
    """
    read coprus into dataframe
    :param dataset: xlsx or sth
    :return: corpus: list of tokens for each article
    """
    corpus = dataset[dataset["status"]==1]
  
    corpus = corpus.reset_index(drop = True)

    corpus['all'] = corpus['title'] + corpus['content']  
    corpus = corpus[["all","title","content","content_id"]]
    return corpus


def createTfidfMatrix(corpus):

    corpus_list = corpus["corpus"].tolist()
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(
                         min_df=0.003,
                         max_df=0.5,
                         max_features=5000
                         )
    tfidf_matrix = vectorizer.fit_transform(corpus_list)
    tfidf_feature_names = vectorizer.get_feature_names()
    tfidf = tfidf_matrix.toarray()
    return tfidf, vectorizer 

def main():
    # pre-define path & variables
    corpus_raw = nn.Dataframefactory(nn.getName('content_articles'),sep = ',')
    vector = "vectorizer.joblib"
    matrix = "tfidf.npy"
    outpath = nnenv.getResourcePath() 
    
    
    # load dict and stopwords
    createDictStop()
    
    # load corpus/
    corpus = combineTitleAndContent(corpus_raw)
    

    # save content_id mapping
    content_id_mapping = corpus["content_id"]
    content_id_mapping.to_csv(outpath + nn.getName('content_id_mapping')) 

    # transform corpus to right format
    corpus["corpus"] = corpus["all"].apply(segment)
    
    #create tfidf-matrix and vectorizer
    tfidfMatrix, vectorizer = createTfidfMatrix(corpus)
    
    #save esstenial files
    with open(outpath + vector, 'wb') as f:
        joblib.dump(vectorizer, f)
    
    np.save(outpath + matrix, tfidfMatrix)
    
    print("new tfidf_matrix and vectorizer have been saved into {""}".format(outpath))


