#!/bin/bash
#shell script for launching algorithm,mainly setting up enviorment for python lib

#PYTHON BINARY location

export PYTHONBINARY=python3


#ALGORITHM_HOME check
if [ "$CAPA_MODEL_HOME" == "" ];then
   echo "[ERROR]Please setup CAPA_MODEL_HOME first before launch algorithm"
   exit
fi
echo "[INFO]HOME directory check"
echo "[INFO]HOME directory is ""$CAPA_MODEL_HOME"

#PYTHON LIB HOME check
if [ "$PYTHONPATH" == "" ];then
   export PYTHONPATH=$CAPA_MODEL_HOME/lib
   export PYTHONPATH=$PATHONPATH:$CAPA_MODEL_HOME/.source_file
else
   export PYTHONPATH=$PYTHONPATH:$CAPA_MODEL_HOME/lib
   export PYTHONPATH=$PATHONPATH:$CAPA_MODEL_HOME/.source_file
fi

echo "[INFO]PYTHONPATH checked"

#PYTHON check
if [ "`which python3 | grep 'no python3 in'`" != "" ];then
   echo "[ERROR]Can't locate your python3 please setup your PATH enviorment variable correctly or install python3"
   exit
fi


#configuration check
if [ ! -f "$CAPA_MODEL_HOME/etc/config.json" ];then
   echo "[ERROR]There is no configuration file in etc directory"
   exit
fi
echo "[INFO]configuration file checked"

if [ "$1" == "" ];then
   echo "[ERROR]Please pass model name to this start script!"
   exit
fi


#launch the entry of algorithm
export COMM="$PYTHONBINARY $CAPA_MODEL_HOME/lib/launch.py $1"

echo "[INFO] algorithm $1 was sent to python3 " 
eval $COMM

