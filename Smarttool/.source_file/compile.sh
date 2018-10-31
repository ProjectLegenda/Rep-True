cp smarttool.py smarttool.pyx

python3 setup.py build_ext --inplace

cp *.cpy* ../lib/

