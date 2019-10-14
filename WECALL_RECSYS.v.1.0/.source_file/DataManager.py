#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ----------------
# File: DataManager.py
# Project: etc
# Created Date: Thursday, May 30th 2019, 2:13:05 pm
# Author: Yubo HE
# ----------------
# Last Modified: Thursday, 30th May 2019 3:30:44 pm
# Modified By: Yubo HE (yubo.he@cn.imshealth.com>) 
# -----------------
# Copyright (c) 2019 IQVIA.Inc
# All Rights Reserved
import nndw as nn
import pandas as pd
from jiebaSegment import Seg
from utils import smooth_user_preference, TagSys
import warnings
warnings.filterwarnings('ignore')
iotype = 'fs'


class DataManager:

    def __init__(self):
        print("Preparing WeCall DataManager")
        self.__tokenizer = Seg()
        self.__tagger = TagSys()

        self.__behavior_raw = nn.Dataframefactory("behavior", iotype=iotype)
        self.__web_raw = nn.Dataframefactory("web", iotype=iotype)
        self.__wecall_content = nn.Dataframefactory("wecall_article", iotype=iotype)
        self.__wecall_doctor = nn.Dataframefactory("wecall_doctor", iotype=iotype)
        self.__wecall_sales = nn.Dataframefactory("wecall_sales", iotype=iotype)
        self.__novo_hcp_info = nn.Dataframefactory("novo_hcp", iotype=iotype)
        self.__novo_market_lv = nn.Dataframefactory("novo_hcp_market", iotype=iotype)
        self.__wecall_article_brand = nn.Dataframefactory("wecall_brand", iotype=iotype)
        self.__wecall_content_detail = nn.Dataframefactory("wecall_detail",iotype=iotype)
        
        self.__cooked_behavior, self.__wecall_bev = self.__behavior_data_process()
        self.__hcp_behavior = self.__make_hcp_behavior()
        self.__behavior_content_tag = self.__make_behavior_content_tag()
        self.__wecall_content_tag = self.__make_wecall_content_tag()
        self.__wecall_hcp_market_mapping = self.__make_wecall_market_mapping()
        self.__wecall_behavior = self.__make_wecall_behavior()
        self.__hcp_title_market_info = self.__make_hcp_market_title()
        self.__wecall_content_brand = self.__make_wecall_content_brand()
        self.__wecall_content_url = self.__make_wecall_content_url()

        print("WeCall DataManager's ready to serve")

    def __behavior_data_process(self):
        # filter wechat data having doctorid
        wechat_raw = self.__behavior_raw
        web_raw = self.__web_raw

        wechat_col_list = ["doctorid", "content_id", "content_title", "module_2", "thumbs_up", "collected", "share"]
        wechat_behavior_process = lambda x: 1 if x in ["点击点赞", "点击收藏", "点击分享", "分享"] else 0
        wechat_raw["thumbs_up"] = wechat_raw["thumbs_up"].apply(
            wechat_behavior_process)
        wechat_raw["collected"] = wechat_raw["collected"].apply(
            wechat_behavior_process)
        wechat_raw["share"] = wechat_raw["share"].apply(wechat_behavior_process)

        wechatFilterd = wechat_raw[~(wechat_raw.doctorid.isnull() | (
                wechat_raw.doctorid == ""))][wechat_col_list]

        wecall_col_list = ["doctorid", "hcp_openid_u_2", "content_id", "content_title", "module_2", "thumbs_up",
                           "collected", "share"]
        wecall_bav = wechat_raw[wechat_raw.module_2.isin(["WeCall 2.0"])][wecall_col_list]
        wecall_bav = wecall_bav[~((wecall_bav.content_title == "") | (wecall_bav.content_title.isnull()))] \
            .reset_index(drop=True)
        wecall_bav["doctorid"] = wecall_bav["doctorid"].fillna("")
        wecall_bav["strength"] = wecall_bav["thumbs_up"] * 1.5 + wecall_bav["share"] * 2 + wecall_bav["collected"] * 2 + 1

        # filter web data having doctorid
        webColList = ["doctorid", "content_id", "content_title", "module_2", "thumbs_up", "collected", "share"]

        def web_behavior_process(x):
            share = 1 if "分享" in x else 0
            thumbs_up = 1 if "点击标签" in x else 0
            collect = 1 if "收藏" in x else 0

            return pd.Series([thumbs_up, collect, share])

        web_raw.rename(columns={"module_category": "module_2"}, inplace=True)
        web_raw["key_operation"].fillna("空", inplace=True)
        web_raw[["thumbs_up", "collected", "share"]
        ] = web_raw["key_operation"].apply(web_behavior_process)
        webFilterd = web_raw[~(web_raw.doctorid.isnull() | (
                web_raw.doctorid == ""))][webColList]

        # Remove the invalid data: content title is 0
        validWechatLog = wechatFilterd[~((wechatFilterd.content_title == "") | (wechatFilterd.content_title.isnull()))] \
            .reset_index(drop=True)
        validWebLog = webFilterd[~((webFilterd.content_title == "") | (wechatFilterd.content_title.isnull()))] \
            .reset_index(drop=True)
        # use validWechatLog and validWebLog as parameters for reading history without tokens

        # fill open id as null into webLog and concat required data into one df

        PrefCols = ["doctorid", "content_id", "module_2",
                    "content_title", "thumbs_up", "collected", "share"]

        content_pref_data = pd.concat([validWechatLog[PrefCols], validWebLog[PrefCols]]) \
            .reset_index(drop=True)

        content_pref_data["strength"] = content_pref_data["thumbs_up"] * 1.5 + content_pref_data["share"] * 2 + \
                                        content_pref_data["collected"] * 2 + 1

        return content_pref_data, wecall_bav

    def __content_lib_processing(self, content_df, lib="behavior"):
        if lib == "wecall":
            title = "name"
        elif lib == "behavior":
            title = "content_title"
        else:
            print("lib only for wecall/behavior")
            raise Exception
        content_df["token"] = content_df[title].apply(self.__tokenizer.cut)
        content_df["func"] = content_df["token"].apply(self.__tagger.label)
        return content_df

    def __make_hcp_behavior(self):
        hcp_behavior = self.__cooked_behavior.groupby(["doctorid", "content_id", "module_2"])["strength"].sum().apply(
            smooth_user_preference).reset_index()
        return hcp_behavior

    def __make_wecall_behavior(self):
        wecall = self.__wecall_bev.groupby(["doctorid", "hcp_openid_u_2", "content_id"])["strength"].sum().apply(
            smooth_user_preference).reset_index()
        return wecall

    def __make_behavior_content_tag(self):
        content_behavior = self.__cooked_behavior[["content_id", "content_title", "module_2"]]
        content_behavior.drop_duplicates(subset=["content_id"], inplace=True)
        content_behavior.reset_index(drop=True, inplace=True)
        content_behavior = self.__content_lib_processing(content_behavior)
        content_behavior = content_behavior.set_index(['content_id', 'module_2'])['func'].apply(pd.Series).stack()
        content_behavior = content_behavior.reset_index()
        content_behavior.columns = ['content_id', 'module_2', 'num_lb', 'func_lb']
        content_behavior["content_id"] = content_behavior["content_id"].astype(str)
        return content_behavior

    def __make_wecall_content_tag(self):
        wecall_content = self.__wecall_content.drop_duplicates(subset=["id"])
        wecall_content = wecall_content[~(wecall_content["deleted"] == 1)].reset_index(drop=True)
        wecall_content = self.__content_lib_processing(wecall_content, 'wecall')
        wecall_content = wecall_content.set_index(['id', "name"])['func'].apply(pd.Series).stack()
        wecall_content = wecall_content.reset_index()
        wecall_content.columns = ['content_id', 'content_title', 'num_lb', 'func_lb']
        wecall_content["content_id"] = wecall_content["content_id"].astype(str)
        return wecall_content

    def __make_wecall_content_url(self):
        url = self.__wecall_content.drop_duplicates(subset=["id"]).reset_index(drop=True)
        url = url[["id", "name","file_name"]]
        url.columns = ["content_id", "content_title", "url"]
        url["content_id"] = url["content_id"].astype(str)
        return url

    def __make_wecall_market_mapping(self):
        hcp_market_mapping = self.__wecall_sales.merge(self.__wecall_doctor[["id", "code"]], left_on=["doctor_id"], right_on=["id"])
        hcp_market_mapping = hcp_market_mapping.drop_duplicates(subset=["doctor_id", "brand_id"])
        hcp_market_mapping = hcp_market_mapping[["code", "brand_id"]]
        hcp_market_mapping.rename(columns={"code": "doctor_id"},inplace=True)
        hcp_market_mapping["brand_id"] = hcp_market_mapping["brand_id"].astype(str)
        return hcp_market_mapping

    def __make_hcp_market_title(self):
        hcp_lv = pd.merge(self.__novo_hcp_info, self.__novo_market_lv,
                          left_on=['city', 'county'],
                          right_on=['city', 'area'],
                          how="left")[
            ["customer_code", "market_name", "academic_title"]]
        hcp_lv = hcp_lv.drop_duplicates().reset_index(drop=True)
        return hcp_lv
   
    def __make_wecall_content_brand(self):
        mapping = dict(zip(self.__wecall_content_detail['id'],self.__wecall_content_detail['document_id']))
        content_brand = self.__wecall_article_brand
        content_brand["document_id"] = content_brand["document_id"].replace(mapping)
        content_brand = content_brand.astype(str)
        
        return content_brand


    @property
    def get_behavior_content_tag(self):
        return self.__behavior_content_tag

    @property
    def get_wecall_content_tag(self):
        return self.__wecall_content_tag

    @property
    def get_all_behavior(self):
        return self.__hcp_behavior

    @property
    def get_wecall_behavior(self):
        return self.__wecall_behavior

    @property
    def get_wecall_doctor(self):
        return self.__wecall_doctor.code.tolist()

    @property
    def get_hcp_market_mapping(self):
        return self.__wecall_hcp_market_mapping

    @property
    def get_hcp_market_title(self):
        return self.__hcp_title_market_info

    @property
    def get_wecall_article_brand(self):
        return self.__wecall_content_brand

    @property
    def get_wecall_url(self):
        return self.__wecall_content_url
