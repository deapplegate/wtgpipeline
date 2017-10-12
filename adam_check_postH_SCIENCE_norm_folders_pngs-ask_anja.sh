#!/bin/bash
set -xv

ds9 -title ABELL1201: -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 ~/data/2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL1201/SUPA*mosOCFN.fits -zoom to fit

