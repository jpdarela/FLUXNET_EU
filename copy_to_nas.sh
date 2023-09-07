#!/bin/sh

## copy reference data to the guess dir
FILES="nee reco aet gpp"


destdir="/home/jpdarela/NAS/z/data/Joao/FLUXNET/ref_data"

for val in $FILES; do
    cp $val* $destdir
done

## update FLUXNET2015_gridlist
cp  ./FLUXNET2015_gridlist.txt  /home/jpdarela/NAS/z/data/Joao/FLUXNET/

## update input data
FILES1="pr ps rsds tas vpd wind hurs"
destdir1="/home/jpdarela/NAS/z/data/Joao/FLUXNET/input_data"

for val1 in $FILES1; do
    cp $val1* $destdir1
done

rm -rf *.nc
rm -rf *.png
rm -rf __pycache__
rm -rf FLUXNET2015_gridlist.txt
