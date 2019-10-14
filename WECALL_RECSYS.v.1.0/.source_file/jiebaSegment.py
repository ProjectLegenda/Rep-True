#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ----------------
# File: jiebaSegment.py
# Project: WECALL
# Created Date: Wednesday, May 22nd 2019, 4:47:20 pm
# Author: Yubo HE
# ----------------
# Last Modified: Wednesday, 29th May 2019 3:07:48 pm
# Modified By: Yubo HE (yubo.he@cn.imshealth.com>) 
# -----------------
# Copyright (c) 2019 IQVIA.Inc
# All Rights Reserved

import jieba
import re
import nndw as nn

iotype = 'fs'


class Seg:

    def __init__(self):
        self.freq = 100000000000000
        self.stopwords = set()
        self.__load_dict()
        self.__load_stopword()

    def __load_dict(self):
        jieba.re_han_default = re.compile(r'([\u0020\u4e00-\u9fa5a-zA-Z0-9+#&._%/”/“/"/β/α/-]+)', re.UNICODE)
        dictionary = nn.Dataframefactory('mappingword', sep='\r\n', iotype=iotype)

        for x in dictionary.word:
            jieba.add_word(x, self.freq)

    def load_userdict(self, file_name):
        jieba.load_userdict(file_name)

    def __load_stopword(self):
        stop = nn.Dataframefactory("stopword",sep='\r\n', iotype=iotype)

        self.stopwords = stop.word.tolist()
    
    def cut(self, sentence, mode='list', cut_all=False):
        sentence = sentence.replace('\n', '').replace(
            '\u3000', '').replace('\u00A0', '').replace('\xa0', '')
        sentence = re.sub(r'\s+', ' ', sentence)
        segs = jieba.cut(sentence, cut_all=cut_all)
        outList = [seg for seg in segs if seg not in self.stopwords and not re.match(r'^[0-9|.|%]*$', seg) and not re.match(r'\s*[\.|\-]\s*', seg)]
        outStr = ' '.join(outList)
        
        if mode == 'list':
            return outList
        elif mode == 'string':
            return outStr 
        else:
            print('mode is only for string or list')
            raise Exception
