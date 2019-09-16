Pe-requisite:

    Install original python3.6.5+ from https://www.python.org
 
    NOTE:Please don't install anaconda or ipython for this tools because original python depend on variable PYTHONPATH when searching for user defined site packages 
    But others may not, but if you are familiar with all distribution of python, you can install other distribution and hack launch shell script yourself

    Install Standard site-package from PyPI and make sure whenever you launch python process and packages below are accessible and importable without changing sys.path explicitly 

    pandas
    jieba
    numpy
    pyhive
    sqlalchemy
    thrift
    Cython
    sklearn
    pymysql

    export PATH and let shell know where to find your python3 binary
    example: 
    export PATH=$PATH:/usr/local/bin

Installing project 

    tar -xf WECALL_RECSYS.v.1.0.tar
    cd WECALL_RECSYS.v.1.0 
    export WECALL_HOME=`pwd`

Launching project:
  
    $WECALL_HOME/bin/wecall_rec.sh

Caveats:

    Enviorment variable A4PE_HOME must be set 


