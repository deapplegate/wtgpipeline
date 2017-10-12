#!/bin/bash -xv
cd /nfs/slac/g/ki/ki18/anja/SUBARU/

# ds9 -tile grid layout 5 2 -geometry 2000x2000 -frame lock image -cmap bb -scale limits .99 1.01 SUPA012604*.fits -zoom to fit -saveimage png -saveimage png plt10ims_SUPA012604.png -quit

ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-12-05_W-J-V/SCIENCE_norm/BINNED/ABELL0543/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-12-05_W-J-V/SCIENCE_norm/BINNED/ABELL0543_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-12-05_W-J-V/SCIENCE_norm/BINNED/ABELL0586/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-12-05_W-J-V/SCIENCE_norm/BINNED/ABELL0586_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-12-05_W-J-V/SCIENCE_norm/BINNED/ABELL0980/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-12-05_W-J-V/SCIENCE_norm/BINNED/ABELL0980_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-12-05_W-J-V/SCIENCE_norm/BINNED/ABELL1111/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-12-05_W-J-V/SCIENCE_norm/BINNED/ABELL1111_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-12-05_W-J-V/SCIENCE_norm/BINNED/ABELL1201/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-12-05_W-J-V/SCIENCE_norm/BINNED/ABELL1201_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-12-05_W-J-V/SCIENCE_norm/BINNED/ZwCl0857.9+2107/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-12-05_W-J-V/SCIENCE_norm/BINNED/ZwCl0857_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-12-05_W-J-V/SCIENCE_norm/BINNED/ZwCl0949.6+5207/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-12-05_W-J-V/SCIENCE_norm/BINNED/ZwCl0949_scale96.png -quit

ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ABELL0773/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ABELL0773_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ABELL0781/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ABELL0781_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ABELL0963/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ABELL0963_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ABELL1423/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ABELL1423_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ABELL1763/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ABELL1763_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ABELL2009/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ABELL2009_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ABELL2111/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ABELL2111_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-J-V/SCIENCE_norm/BINNED/RXCJ1212.3-1816/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-J-V/SCIENCE_norm/BINNED/RXCJ1212_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-J-V/SCIENCE_norm/BINNED/RXCJ1504.1-0248/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-J-V/SCIENCE_norm/BINNED/RXCJ1504_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ZWCL0857.9+2107/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ZWCL0857_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ZwCl0949.6+5207/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ZwCl0949_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ZwCl1231.4+1007/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ZwCl1231_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ZwCl1309.1+2216/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-J-V/SCIENCE_norm/BINNED/ZwCl1309_scale96.png -quit

ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ABELL0773/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ABELL0773_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ABELL0781/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ABELL0781_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ABELL0901/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ABELL0901_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ABELL0907/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ABELL0907_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ABELL1451/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ABELL1451_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ABELL1682/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ABELL1682_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/RXCJ1212.3-1816/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/RXCJ1212_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ZwCl0949.6+5207/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ZwCl0949_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ZwCl1021.0+0426/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ZwCl1021_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ZwCl1231.4+1007/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ZwCl1231_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ZwCl1309.1+2216/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2010-03-12_W-S-I+/SCIENCE_norm/BINNED/ZwCl1309_scale96.png -quit

ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2007-02-13_W-S-I+/SCIENCE_norm/BINNED/A586/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2007-02-13_W-S-I+/SCIENCE_norm/BINNED/A586_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2007-02-13_W-S-I+/SCIENCE_norm/BINNED/A689/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2007-02-13_W-S-I+/SCIENCE_norm/BINNED/A689_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2007-02-13_W-S-I+/SCIENCE_norm/BINNED/A697/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2007-02-13_W-S-I+/SCIENCE_norm/BINNED/A697_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2007-02-13_W-S-I+/SCIENCE_norm/BINNED/SDF/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2007-02-13_W-S-I+/SCIENCE_norm/BINNED/SDF_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2007-02-13_W-S-I+/SCIENCE_norm/BINNED/Z1432/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2007-02-13_W-S-I+/SCIENCE_norm/BINNED/Z1432_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2007-02-13_W-S-I+/SCIENCE_norm/BINNED/Z1883/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2007-02-13_W-S-I+/SCIENCE_norm/BINNED/Z1883_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2007-02-13_W-S-I+/SCIENCE_norm/BINNED/Z2089/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2007-02-13_W-S-I+/SCIENCE_norm/BINNED/Z2089_scale96.png -quit

ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL0665/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL0665_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL0868/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL0868_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL1201/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL1201_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL1413/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL1413_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL1423/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL1423_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL1763/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL1763_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL2254/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ABELL2254_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/Abell2111/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/Abell2111_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/Abell2204/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/Abell2204_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/RXCJ1504.1-0248/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/RXCJ1504_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ZwCl0857.9+2107/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ZwCl0857_scale96.png -quit
ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ZwCl1021.0+0426/SUPA*mosOCFN.fits -zoom to fit -saveimage png 2009-03-28_W-S-I+/SCIENCE_norm/BINNED/ZwCl1021_scale96.png -quit
cd ~/bonnpipeline
