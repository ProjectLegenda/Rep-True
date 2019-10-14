#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ----------------
# File: utils.py
# Project: WECALL
# Created Date: Monday, May 27th 2019, 11:20:45 am
# Author: Yubo HE
# ----------------
# Last Modified: Tuesday, 28th May 2019 3:08:10 pm
# Modified By: Yubo HE (yubo.he@cn.imshealth.com>) 
# -----------------
# Copyright (c) 2019 IQVIA.Inc
# All Rights Reserved
import pandas as pd
from time import time
from functools import wraps
import nndw as nn
import numpy as np
from multiprocessing import Pool
import math

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'

iotype = 'fs'


def parallelize_dataframe(df, func, n_cores=4):
    df_split = np.array_split(df, n_cores)
    pool = Pool(n_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df


def timing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time()
        result = f(*args, **kwargs)
        end = time()
        print("func:{}, time elaps:{:.0f}m {:.0f}s".format(
            f.__name__, (end - start) // 60, (end - start) % 60))
        return result

    return wrapper


def smooth_user_preference(x):
    return math.log(1 + x, 2)


class TagSys:
    """
    打标签系统
    """

    def __init__(self, option="hcp"):
        self.similar_words = nn.Dataframefactory('similar', iotype=iotype)

        if option == "hcp":
            self.tag = nn.Dataframefactory('hcp_tag', iotype=iotype)
            self.lb = "医生标签"
        elif option == "pat":
            self.tag = nn.Dataframefactory('pat_tag', iotype=iotype)
            self.lb = "病人标签"
        else:
            print('option is only for pat or hcp')
            raise Exception
        self.mapping = self.__create_mapping()
        self.word_tag = self.__get_word_tag()

    def __create_mapping(self):
        """
        create mapping file
        """
        # Cut tags into different levels
        lv2Tags = self.tag[(self.tag.tag_class == "内容标签") & (self.tag.tag_level == "2")]
        lv1Tags = self.tag[(self.tag.tag_class == "内容标签") & (self.tag.tag_level == "1")]
        Tags = self.tag[self.tag.tag_class == self.lb]

        # Group by lv2 tag and add the similar words into a list
        simiList = self.similar_words.groupby(["tag_id", "tag_name"])[
            "tag_similar_word"].apply(list).to_frame().reset_index()

        # Merge similar words and lv2 tags
        simiLv2 = pd.merge(simiList, lv2Tags, how="left", left_on="tag_id",
                           right_on="tag_id", suffixes=("_simi", "_lv2"))

        # Merge lv2 tags and lv1 tags
        lv2Lv1 = pd.merge(simiLv2[["tag_similar_word", "tag_name_lv2", "parent_tag_id"]], lv1Tags,
                          how="left", left_on="parent_tag_id", right_on="tag_id", suffixes=("_lv2", "_lv1"))

        # Merge lv1 tags and hcp tags
        lv1Hcp = pd.merge(lv2Lv1[["tag_similar_word", "tag_name_lv2", "tag_name", "parent_tag_id_lv1"]], Tags,
                          how="left", left_on="parent_tag_id_lv1", right_on="tag_id", suffixes=("_lv1", "_func"))

        # Re-adjust into four columns
        mapping = lv1Hcp[["tag_similar_word",
                          "tag_name_lv2", "tag_name_lv1", "tag_name_func"]]

        return mapping

    def __get_word_tag(self):
        word_tag = {}
        for idx, row in self.mapping.iterrows():
            for word in row['tag_similar_word']:
                word_tag[word] = row['tag_name_func']
        return word_tag

    def label(self, tokens):
        diabetes = ['糖尿病', '2型糖尿病']

        # 根据码表去打标签

        funcLb = []

        for token in tokens:
            if token in self.word_tag.keys():
                funcLb.append(self.word_tag[token])

        # lv2Lb = list(set(lv2Lb))
        # lv2Lb = [x for x in lv2Lb if x != '' and str(x) != 'nan' and x not in diabetes]
        # lv1Lb = list(set(lv1Lb))
        # lv1Lb = [x for x in lv1Lb if x != '' and str(x) != 'nan']
        funcLb = list(set(funcLb))
        funcLb = [x for x in funcLb if x != '' and str(x) != 'nan']

        # # 定义并发症
        # complication = ['急性/严重并发症',
        #                 '酮症酸中毒',
        #                 '肝病相关',
        #                 '呼吸系统相关',
        #                 '肾病相关',
        #                 '神经病变',
        #                 '糖尿病足',
        #                 '心脑血管相关',
        #                 '高血压相关',
        #                 '高血脂相关',
        #                 '视网膜病变',
        #                 '风湿性疾病',
        #                 '性功能问题',
        #                 '胃肠不适',
        #                 '骨相关问题',
        #                 '皮肤病变',
        #                 '精神/心理相关',
        #                 '肿瘤相关',
        #                 '其它代谢性疾病',
        #                 '其它不严重的症状或不良反应']

        # 如果二级标签中同时有 '并发症/合并症' 或任意已经定义的并发症，去除掉'并发症/合并症'
        # for word in complication:
        #     if (word in lv2Lb) and ('并发症/合并症') in lv2Lb:
        #         lv2Lb.remove('并发症/合并症')

        #return pd.Series([funcLb, lv1Lb, lv2Lb])

        return funcLb
