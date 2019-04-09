
echo '[INFO]copyping py to pyx'
cp nndw.py nndw.pyx
cp nnenv.py nnenv.pyx
cp rec.py rec.pyx
cp rpc.py rpc.pyx


echo '[INFO]building'
python3 setup.py build_ext --inplace

echo '[INFO]copying'
cp *.cpy* ../lib/
                
echo '[INFO]cleansing' 
rm -r build
rm *.c
rm *.pyx
rm *.so


