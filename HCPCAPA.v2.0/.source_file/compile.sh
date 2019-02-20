

#!/bin/bash

echo '[INFO]copyping py to pyx'

ls | awk -F '\t' '{ if ( $1 ~ /.py$/ ) print $1}' | while read line
do
cp $line ${line%%.*}.pyx

done

echo '[INFO]building'
python3 setup.py build_ext --inplace

echo '[INFO]copying'
cp *.cpy* ../lib/
                
echo '[INFO]cleansing' 
rm -r build
rm *.c
rm *.pyx
rm *.so


