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

    tar -xf a4pe.tar
    cd 4PE.v2.0 
    export A4PE_HOME=`pwd`

Launching project:
  
    $A4PE_HOME/bin/a4pe.sh

Caveats:

    Enviorment variable A4PE_HOME must be set 

Note:

    The a4pe program will overwrite the following tables in Hive:

    iqvia_hcp_channel_preference
    iqvia_hcp_content_interest
    iqvia_hcp_content_interest_keyword
    iqvia_hcp_reading_history
    iqvia_4pe_hcp_recommendation
