#!/bin/bash 
#shell script for launching algorithm,mainly setting up enviorment for python lib 
 
#PYTHON BINARY location 
 
export PYTHONBINARY=python3 
 
 
#ALGORITHM_HOME check 
if [ "$WECALL_HOME" == "" ];then 
   echo "[ERROR]Please setup WECALL_HOME first before launch algorithm" 
   exit 
fi 
echo "[INFO]HOME directory check" 
 
#PYTHON LIB HOME check 
if [ "$PYTHONPATH" == "" ];then 
   export PYTHONPATH=$WECALL_HOME/lib 
   export PYTHONPATH=$PATHONPATH:$WECALL_HOME/.source_file 
else  
   export PYTHONPATH=$PYTHONPATH:$WECALL_HOME/lib 
   export PYTHONPATH=$PATHONPATH:$WECALL_HOME/.source_file   
fi 
 
echo "[INFO]PYTHONPATH checked" 
 
#PYTHON check 
if [ "`which python3 | grep 'no python3 in'`" != "" ];then 
   echo "[ERROR]Can't locate your python3 please setup your PATH enviorment variable correctly or install python3" 
   exit 
fi 
 
 
#configuration check 
if [ ! -f "$WECALL_HOME/etc/config.json" ];then 
   echo "[ERROR]There is no configuration file in etc directory" 
   exit 
fi  
echo "[INFO]configuration file checked" 
 
if [ "$1" != "" ];then 
   echo "[ERROR]hcp capability algorithm shouldn't have parameters from operation system" 
   exit 
fi 
 
 
#launch the entry of algorithm 
export COMM="$PYTHONBINARY $WECALL_HOME/lib/launch.py " 
 
eval $COMM 
 
