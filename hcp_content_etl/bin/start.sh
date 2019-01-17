#!/bin/bash
#shell script for launching algorithm,mainly setting up enviorment for python lib

#PYTHON BINARY location

export PYTHONBINARY=python3


#ALGORITHM_HOME check
if [ "$ETL_HOME" == "" ];then
   echo "[ERROR]Please setup HCPCAPA_HOME first before launch algorithm"
   exit
fi
echo "[INFO]HOME directory check"


export ETL_LIB_HOME=$ETL_HOME/lib
export ETL_SOURCE_HOME=$ETL_HOME/.source_file

echo $ETL_LIB_HOME

#PYTHON LIB HOME check
if [ "$PYTHONPATH" == "" ];then
   export PYTHONPATH=$ETL_HOME/lib
   export PYTHONPATH=$PATHONPATH:$ETL_HOME/.source_file
else 
   export PYTHONPATH=$PYTHONPATH:$ETL_HOME/lib
   export PYTHONPATH=$PATHONPATH:$ETL_HOME/.source_file  
fi

echo "[INFO]PYTHONPATH checked"

#PYTHON check
if [ "`which python3 | grep 'no python3 in'`" != "" ];then
   echo "[ERROR]Can't locate your python3 please setup your PATH enviorment variable correctly or install python3"
   exit
fi


#configuration check
if [ ! -f "$ETL_HOME/etc/config.json" ];then
   echo "[ERROR]There is no configuration file in etc directory"
   exit
fi 
echo "[INFO]configuration file checked"

if [ "$1" != "" ];then
   echo "[ERROR]current verison does not support input parameters"
   exit
fi

if [ -f "$ETL_LIB_HOME/client.py" ];then

    export COMM="$PYTHONBINARY $ETL_LIB_HOME/client.py" 
#launch the entry of algorithm
else
    export COMM="$PYTHONBIANRY $ETL_SOURCE_HOME/client.py"
fi 
echo  $COMM

