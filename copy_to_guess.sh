#!/bin/sh

## copy reference data to the guess dir
FILES="nee reco aet gpp"
# FOLDER="bugfix_et"
FOLDER="parent_commit"

destdir="/home/jpdarela/Desktop/hyd_europe/$FOLDER/guess4.1_hydraulics/FLUXNET_results/flx_ref/"

for val in $FILES; do
    cp $val* $destdir
done

## update FLUXNET2015_gridlist
cp  ./FLUXNET2015_gridlist.txt  /home/jpdarela/Desktop/hyd_europe/$FOLDER/guess4.1_hydraulics/data/gridlist/

## update input data
FILES1="pr ps rsds tas vpd wind"
destdir1="/home/jpdarela/Desktop/hyd_europe/$FOLDER/guess4.1_hydraulics/data/env/FLUXNET2015/"

for val1 in $FILES1; do
    cp $val1* $destdir1
done

rm -rf *.nc
rm -rf *.png
rm -rf __pycache__
rm -rf FLUXNET2015_gridlist.txt
