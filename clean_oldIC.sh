#!/bin/bash

subaru=/nfs/slac/g/ki/ki05/anja/SUBARU

cluster=$1

filter=$2

rm -f ${subaru}/${cluster}/${filter}/SCIENCE/*I.fits
rm -f ${subaru}/${cluster}/${filter}/SCIENCE/*I.sub.fits    
rm -f ${subaru}/${cluster}/${filter}/WEIGHTS/*I.weight.fits
rm -f ${subaru}/${cluster}/${filter}/WEIGHTS/*I.flag.fits


