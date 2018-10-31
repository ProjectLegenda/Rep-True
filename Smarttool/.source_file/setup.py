from distutils.core import setup
from Cython.Build import cythonize

setup(name='nn4pe pilot',
      ext_modules=cythonize("smarttool.pyx"))

