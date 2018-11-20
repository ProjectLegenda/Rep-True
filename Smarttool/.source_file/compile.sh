cp nndw.py nndw.pyx
cp nnenv.py nnenv.pyx
cp pilot.py pilot.pyx

python3 setup.py build_ext --inplace

cp *.cpy* ../lib/
