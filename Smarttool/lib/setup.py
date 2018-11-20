from distutils.core import setup
from Cython.Build import cythonize

setup(name='smarttool',ext_modules=cythonize("nndw.pyx"))
setup(name='smarttool',ext_modules=cythonize("nnenv.pyx"))
setup(name='smarttool',ext_modules=cythonize("smartcore.pyx"))
setup(name='smarttool',ext_modules=cythonize("smartserver.pyx"))
setup(name='smarttool',ext_modules=cythonize("smartclient.pyx"))
setup(name='smarttool',ext_modules=cythonize("tfidf.pyx"))
setup(name='smarttool',ext_modules=cythonize("request.pyx"))

