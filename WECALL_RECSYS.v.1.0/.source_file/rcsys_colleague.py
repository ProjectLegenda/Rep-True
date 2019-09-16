import pandas as pd
from utils import timing


class ColleagueRcsys:

    def __init__(self, wecall_behavior, hcp_market, hcp_brand, content_brand, doctor_list,wecall_content_tag):
        self.wecall_behavior = wecall_behavior.rename(columns={'doctorid': 'doctor_id'})
        self.hcp_market = hcp_market
        self.hcp_brand = hcp_brand
        self.content_brand = content_brand
        self.doctor_list = pd.DataFrame(doctor_list, columns=['doctor_id'])
        self.wecall_content_tag = wecall_content_tag
    # Loading DataFrames
    def get_colleague_read(self):
        doctor_with_market_info = self.doctor_list.merge(self.hcp_market,
                                                         left_on='doctor_id', right_on='customer_code', how='left'
                                                         ).dropna().reset_index(drop=True)[['doctor_id',
                                                                                            'market_name',
                                                                                            'academic_title']]
        # 从doctor_list中查找所有具有market信息的医生
        doctor_add_behavior = doctor_with_market_info.merge(self.wecall_behavior, on='doctor_id', how='left').dropna()
        doctor_add_behavior = doctor_add_behavior.merge(self.wecall_content_tag,on="content_id",how = "left").dropna()
        # join并返回有wecall行为记录的医生
        colleague_group = pd.DataFrame(doctor_add_behavior.groupby([
            'market_name','academic_title'])['content_id'].apply(list).reset_index(),columns=['market_name',
                                                                                              'academic_title',
                                                                                              'content_id'])
        # 根据市场信息分组，得到每组应推荐文章库
        doctor_with_colleague_info = doctor_with_market_info.merge(colleague_group,
                                                                   on=['market_name',
                                                                       'academic_title'],
                                                                   how='left').dropna().reset_index(drop=True)
        # 根据hcp市场分组信息，给每个hcp JOIN 初始推荐列表，存储在列表中
        return doctor_with_colleague_info
    def unstack_rm_dup(self):
        doctor_with_colleague_info = self.get_colleague_read()[['doctor_id', 'content_id']]
        unstack_rclist = doctor_with_colleague_info.set_index('doctor_id').content_id.apply(pd.Series). \
            stack().reset_index(level=-1, drop=True).astype(str).reset_index().rename(columns={0: 'content_id'})
        # 将存储在列表中的每个医生的推荐列表展开
        rm_dup_df = unstack_rclist.drop_duplicates(keep='first')
        content_strength = self.wecall_behavior.groupby(
            'content_id')['strength'].sum().sort_values(ascending=False).reset_index()
        # 添加strength信息
        df_with_strength = rm_dup_df.merge(content_strength, on='content_id', how='left').fillna(0)
        df_rmread_content = df_with_strength.merge(self.wecall_behavior.rename(columns={'doctorid': 'doctor_id'})
                                                   [['doctor_id', 'content_id']], on=['doctor_id', 'content_id'],
                                                   how='left', indicator=True)
        # 去除hcp已阅读文章
        df_rmread_content = df_rmread_content[df_rmread_content['_merge'] == 'left_only'
                                              ][['doctor_id', 'content_id', 'strength']]
        return df_rmread_content
    def delivery_final(self):
        if self.get_colleague_read().empty:
            df_final = pd.DataFrame([], columns=['doctor_id', 'content_id', 'strength', 'method'])
        elif self.unstack_rm_dup().empty:
            df_final = pd.DataFrame([], columns=['doctor_id', 'content_id', 'strength', 'method'])
        else:
            df_before_filter = self.unstack_rm_dup()
            df_add_hcpbrand = df_before_filter.merge(self.hcp_brand, on='doctor_id', how='left')
            df_filter_brand = df_add_hcpbrand.merge(self.content_brand,
                                                    on=['content_id', 'brand_id'],
                                                    how='left').dropna()[['doctor_id', 'content_id', 'strength']]
            # 根据brand信息filter hcp可读文章
            df_filter_brand.sort_values(['doctor_id', 'strength'], ascending=False, inplace=True)
            df_final = df_filter_brand.groupby('doctor_id').head(10)
            df_final['method'] = 2
        return df_final
