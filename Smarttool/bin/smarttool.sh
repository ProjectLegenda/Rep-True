#!/bin/bash
#shell script for launching algorithm,mainly setting up enviorment for python lib

#PYTHON BINARY location

export PYTHONBINARY=python3

#ALGORITHM_HOME check
if [ "$SMARTTOOL_HOME" == "" ];then
   echo "[ERROR]Please setup SMARTTOOL_HOME first before launch algorithm"
   exit
fi
echo "[INFO]HOME directory check"

#PYTHON LIB HOME check
if [ "$PYTHONPATH" == "" ];then
   export PYTHONPATH=$SMARTTOOL_HOME/lib
else export PYTHONPATH=$PYTHONPATH:$SMARTTOOL_HOME/lib
fi

echo "[INFO]PYTHONPATH checked"

#PYTHON check
if [ "`which python3 | grep 'no python3 in'`" != "" ];then
   echo "[ERROR]Can't locate your python3 please setup your PATH enviorment variable correctly or install python3"
   exit
fi


#configuration check
if [ ! -f "$SMARTTOOL_HOME/etc/config.json" ];then
   echo "[ERROR]There is no configuration file in etc directory"
   exit
fi 
echo "[INFO]configuration file checked"

if [ ! -f "$1" ];then
   echo "[ERROR]Jason file does not exist"
   exit
fi 

if [ "$2" == "" ];then
   echo "[ERROR]Please provide outputfile name"
   exit
fi

if [ -f "$2" ];then
   echo "[ERROR]Out put File "$2" already exists change another file name or move the existing file"
   exit
fi

if [ "$3" != "" ];then
   echo "[ERROR]there must be 2 input parameters for this smarttoolscript"
   exit
fi


#launch the entry of algorithm
export COMM="$PYTHONBINARY $SMARTTOOL_HOME/lib/launch.py $1 $2"

eval $COMM
