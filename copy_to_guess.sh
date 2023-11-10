#!/bin/sh

## copy reference data to the guess dir
FILES="nee reco et gpp"

destdir="../LPJG-home/FLUXNET2015/ref/"

for val in $FILES; do
    cp ./ref/$val* $destdir
done

## update FLUXNET2015_gridlist
cp ./driver/FLUXNET2015.grd ../LPJG-home/grd/

## update input data
FILES1="pr ps rsds tas vpd wind hurs"
destdir1="../LPJG-home/FLUXNET2015/"

for val1 in $FILES1; do
    cp ./driver/$val1* $destdir1
done
