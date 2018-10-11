#!/bin/bash
#shell script for launching algorithm,mainly setting up enviorment for python lib

#ALGORITHM_HOME check
if [ "$ALGORITHM_HOME" ==  "" ];then
   echo "[ERROR]Please setup ALGORITHM_HOME first before launch algorithm"
fi


#PYTHON LIB HOME check
if [ "$PYTHONPATH" == "" ];then
   export PYTHONPATH=$ALGORITHM_HOME/lib
   echo $PYTHONPATH
else export PYTHONPATH=$PYTHONPATH:$ALGORITHM_HOME/lib
fi

#PYTHON check
if [ "`which python3 | grep 'no python3 in'`" != "" ];then
   echo "[ERROR]Can't locate your python3 please setup your PATH enviorment variable correctly or install python3"
fi


#launch the entry of algorithm
python3 "$ALGORITHM_HOME/bin/launch_alg.py"

