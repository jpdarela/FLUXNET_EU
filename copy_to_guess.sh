#!/bin/sh

## copy reference data to the guess dir
FILES="nee reco et gpp"

destdir="../LPJG-home/FLUXNET2015/ref/"

for val in $FILES; do
    mv $val* $destdir
done

## update FLUXNET2015_gridlist
mv  ./FLUXNET2015_gridlist.txt ../LPJG-home/grd/

## update input data
FILES1="pr ps rsds tas vpd wind hurs"
destdir1="../LPJG-home/FLUXNET2015/"

for val1 in $FILES1; do
    mv $val1* $destdir1
done

rm -rf *.nc
rm -rf *.png
rm -rf __pycache__
rm -rf FLUXNET2015_gridlist.txt
