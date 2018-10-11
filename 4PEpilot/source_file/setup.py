from distutils.core import setup
from Cython.Build import cythonize

setup(name='Hello world app',
      ext_modules=cythonize("init.pyx"))

setup(name='Hello world app',
      ext_modules=cythonize("nndw.pyx"))

setup(name='Hello world app',
      ext_modules=cythonize("nnenv.pyx"))
