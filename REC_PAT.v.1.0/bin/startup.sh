#!/bin/bash
#shell script for launching algorithm,mainly setting up enviorment for python lib

#PYTHON BINARY location

export PYTHONBINARY=python3

#ALGORITHM_HOME check
if [ "$RECP_HOME" == "" ];then
   echo "[ERROR]Please setup REC_HOME first before launch algorithm"
   exit
fi
echo "[INFO]HOME directory check"
echo "[INFO]HOME directory is ""$RECP_HOME"

#PYTHON LIB HOME check
if [ "$PYTHONPATH" == "" ];then
   export PYTHONPATH=$RECP_HOME/lib
   export PYTHONPATH=$PATHONPATH:$RECP_HOME/.source_file
else
   export PYTHONPATH=$PYTHONPATH:$RECP_HOME/lib
   export PYTHONPATH=$PATHONPATH:$RECP_HOME/.source_file
fi

echo "[INFO]PYTHONPATH checked"

#PYTHON check
if [ "`which python3 | grep 'no python3 in'`" != "" ];then
   echo "[ERROR]Can't locate your python3 please setup your PATH enviorment variable correctly or install python3"
   exit
fi


#configuration check
if [ ! -f "$RECP_HOME/etc/config.json" ];then
   echo "[ERROR]There is no configuration file in etc directory"
   exit
fi
echo "[INFO]configuration file checked"

if [ "$1" == "" ];then
   echo "[ERROR] please provide hostname for rpc server"
   exit
fi

if [ "$2" == "" ];then
   echo"[ERROR]please provide port for rpc server"
fi 

#launch the entry of algorithm
if [ -f "$RECP_HOME/lib/start.py" ];then

export COMM="$PYTHONBINARY $RECP_HOME/lib/start.py $1 $2"

fi

echo "[INFO]REC is running"
eval $COMM

