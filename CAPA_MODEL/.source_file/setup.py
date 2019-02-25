from distutils.core import setup
from Cython.Build import cythonize


setup(name='nn4pe pilot',ext_modules=cythonize("nndw.pyx"))
setup(name='nn4pe pilot',ext_modules=cythonize("nnenv.pyx"))
setup(name='nn4pe pilot',ext_modules=cythonize("cal_pat_wechat_openid_4pe_bi.pyx"))
setup(name='nn4pe pilot',ext_modules=cythonize("cal_hcp_wechat_web_docid_4pe.pyx"))
setup(name='nn4pe pilot',ext_modules=cythonize("cal_hcp_wechat_openid_bi.pyx"))
setup(name='nn4pe pilot',ext_modules=cythonize("cal_hcp_web_docid_bi.pyx"))
setup(name='nn4pe pilot',ext_modules=cythonize("cal_pat_search_openid_stats.pyx"))
setup(name='nn4pe pilot',ext_modules=cythonize("cal_pat_callcenter_patid_stats.pyx"))
