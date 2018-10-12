#!/bin/bash
#shell script for launching algorithm,mainly setting up enviorment for python lib

#ALGORITHM_HOME check
if [ "$ALGORITHM_HOME" == "" ];then
   echo "[ERROR]Please setup ALGORITHM_HOME first before launch algorithm"
   exit
fi
echo "[INFO]ALGORITHM_HOME check"

#PYTHON LIB HOME check
if [ "$PYTHONPATH" == "" ];then
   export PYTHONPATH=$ALGORITHM_HOME/lib
else export PYTHONPATH=$PYTHONPATH:$ALGORITHM_HOME/lib
fi

echo "[INFO]PYTHONPATH checked"

#PYTHON check
if [ "`which python3 | grep 'no python3 in'`" != "" ];then
   echo "[ERROR]Can't locate your python3 please setup your PATH enviorment variable correctly or install python3"
   exit
fi


#configuration check
if [ ! -f "$ALGORITHM_HOME/etc/config.json" ];then
   echo "[ERROR]There is no configuration file in etc directory"
   exit
fi 
echo "[INFO]configuration file checked"

#launch the entry of algorithm
python3 "$ALGORITHM_HOME/lib/algorithm.py"

