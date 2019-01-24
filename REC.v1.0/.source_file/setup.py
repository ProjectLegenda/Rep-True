from distutils.core import setup
from Cython.Build import cythonize

setup(name='rec',
      ext_modules=cythonize("rec.pyx"))

setup(name='rec',
      ext_modules=cythonize("nndw.pyx"))

setup(name='rec',
      ext_modules=cythonize("nnenv.pyx"))

setup(name='rec',
      ext_modules=cythonize("rpc.pyx"))




