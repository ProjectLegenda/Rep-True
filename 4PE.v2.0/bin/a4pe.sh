#!/bin/bash
#shell script for launching algorithm,mainly setting up enviorment for python lib

#PYTHON BINARY location

export PYTHONBINARY=python3


#ALGORITHM_HOME check
if [ "$A4PE_HOME" == "" ];then
   echo "[ERROR]Please setup A4PE_HOME first before launch algorithm"
   exit
fi
echo "[INFO]HOME directory check"

#PYTHON LIB HOME check
if [ "$PYTHONPATH" == "" ];then
   export PYTHONPATH=$A4PE_HOME/lib
   export PYTHONPATH=$PATHONPATH:$A4PE_HOME/.source_file
else 
   export PYTHONPATH=$PYTHONPATH:$A4PE_HOME/lib
   export PYTHONPATH=$PATHONPATH:$A4PE_HOME/.source_file  
fi

echo "[INFO]PYTHONPATH checked"

#PYTHON check
if [ "`which python3 | grep 'no python3 in'`" != "" ];then
   echo "[ERROR]Can't locate your python3 please setup your PATH enviorment variable correctly or install python3"
   exit
fi


#configuration check
if [ ! -f "$A4PE_HOME/etc/config.json" ];then
   echo "[ERROR]There is no configuration file in etc directory"
   exit
fi 
echo "[INFO]configuration file checked"

if [ "$1" != "" ];then
   echo "[ERROR]hcp capability algorithm shouldn't have parameters from operation system"
   exit
fi


#launch the entry of algorithm
export COMM="$PYTHONBINARY $A4PE_HOME/lib/launch.py "

eval $COMM

