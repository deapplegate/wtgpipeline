#!/bin/bash

subaru=/nfs/slac/g/ki/ki05/anja/SUBARU

cluster=$1

filter=$2

rm ${subaru}/${cluster}/${filter}/SCIENCE/*I.fits
rm ${subaru}/${cluster}/${filter}/SCIENCE/*I.sub.fits    
rm ${subaru}/${cluster}/${filter}/WEIGHTS/*I.weight.fits
rm ${subaru}/${cluster}/${filter}/WEIGHTS/*I.flag.fits


