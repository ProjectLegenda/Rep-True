from distutils.core import setup
from Cython.Build import cythonize

setup(name='nn4pe pilot',
      ext_modules=cythonize("hcpcapacore.pyx"))

setup(name='nn4pe pilot',
      ext_modules=cythonize("nndw.pyx"))

setup(name='nn4pe pilot',
      ext_modules=cythonize("nnenv.pyx"))
