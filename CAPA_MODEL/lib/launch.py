import sys

if sys.argv[1] == 'cal_hcp_wechat_web_docid_4pe':
    import cal_hcp_wechat_web_docid_4pe as al 
    if al.main() == 1:
        print('[INFO]Algorithm done')


elif sys.argv[1] == 'cal_hcp_wechat_openid_bi':
    import cal_hcp_wechat_openid_bi as al 
    if al.main() == 1:
        print('[INFO]Algorithm done')


elif sys.argv[1] == 'cal_hcp_web_docid_bi':
    import cal_hcp_web_docid_bi as al 
    if al.main() == 1:
        print('[INFO]Algorithm done')

elif sys.argv[1] == 'cal_pat_wechat_openid_4pe_bi':
    import cal_pat_wechat_openid_4pe_bi as al 
    if al.main() == 1:
        print('[INFO]Algorithm done')

elif sys.argv[1] == 'cal_pat_search_openid_stats':
    import cal_pat_search_openid_stats as al 
    if al.main() == 1:
        print('[INFO]Algorithm done')

elif sys.argv[1] == 'cal_pat_callcenter_patid_stats':
    import cal_pat_callcenter_patid_stats as al 
    if al.main() == 1:
        print('[INFO]Algorithm done')
