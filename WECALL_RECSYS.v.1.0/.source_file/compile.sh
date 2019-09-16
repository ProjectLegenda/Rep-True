echo '[INFO]copyping py to pyx'
cp nndw.py nndw.pyx
cp nnenv.py nnenv.pyx
cp DataManager.py DataManager.pyx
cp jiebaSegment.py jiebaSegment.pyx
cp Novo_Luxi.py Novo_Luxi.pyx
cp rcsys_colleague.py rcsys_colleague.pyx
cp recommand_tags.py recommand_tags.pyx
cp wecall_rec.py wecall_rec.pyx
cp Transformer.py Transformer.pyx
cp utils.py utils.pyx


echo '[INFO]building'
python3 setup.py build_ext --inplace

echo '[INFO]copying'
cp *.cpy* ../lib/
                
echo '[INFO]cleansing' 
rm -r build
rm *.c
rm *.pyx
rm *.so


