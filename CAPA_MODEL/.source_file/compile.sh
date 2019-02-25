
echo '[INFO]copyping py to pyx'
cp nndw.py nndw.pyx
cp nnenv.py nnenv.pyx
cp cal_pat_wechat_openid_4pe_bi.py cal_pat_wechat_openid_4pe_bi.pyx
cp cal_hcp_wechat_web_docid_4pe.py cal_hcp_wechat_web_docid_4pe.pyx
cp cal_hcp_wechat_openid_bi.py cal_hcp_wechat_openid_bi.pyx
cp cal_hcp_web_docid_bi.py cal_hcp_web_docid_bi.pyx
cp cal_pat_search_openid_stats.py cal_pat_search_openid_stats.pyx
cp cal_pat_callcenter_patid_stats.py cal_pat_callcenter_patid_stats.pyx

echo '[INFO]building'
python3 setup.py build_ext --inplace

echo '[INFO]copying'
cp *.cpy* ../lib/
                
echo '[INFO]cleansing' 
rm -r build
rm *.c
rm *.pyx
rm *.so


