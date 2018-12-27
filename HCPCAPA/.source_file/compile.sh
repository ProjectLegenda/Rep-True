cp nndw.py nndw.pyx
cp nnenv.py nnenv.pyx

python3 setup.py build_ext --inplace

cp *.cpy* ../lib/
                 
