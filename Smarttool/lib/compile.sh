cp nndw.py nndw.pyx
cp nnenv.py nnenv.pyx
cp smartcore.py smartcore.pyx
cp smartclient.py smartclient.pyx
cp smartserver.py smartserver.pyx
cp request.py request.pyx
cp tfidf.py tfidf.pyx

python3 setup.py build_ext --inplace

cp *.cpy* ../lib/

rm *.pyx
