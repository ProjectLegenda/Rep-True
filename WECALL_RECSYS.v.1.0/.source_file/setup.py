from distutils.core import setup
from Cython.Build import cythonize

setup(name='WeCall RecSys',
      ext_modules=cythonize("DataManager.pyx"))

setup(name='WeCall RecSys',
      ext_modules=cythonize("jiebaSegment.pyx"))

setup(name='WeCall RecSys',
      ext_modules=cythonize("nndw.pyx"))

setup(name='WeCall RecSys',
      ext_modules=cythonize("nnenv.pyx"))

setup(name='WeCall RecSys',
      ext_modules=cythonize("Novo_Luxi.pyx"))

setup(name='WeCall RecSys',
      ext_modules=cythonize("rcsys_colleague.pyx"))

setup(name='WeCall RecSys',
      ext_modules=cythonize("recommand_tags.pyx"))

setup(name='WeCall RecSys',
      ext_modules=cythonize("wecall_rec.pyx"))

setup(name='WeCall RecSys',
      ext_modules=cythonize("Transformer.pyx"))

setup(name='WeCall RecSys',
      ext_modules=cythonize("utils.pyx"))
