#!/bin/bash
SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU/


for pprun in 2010-12-05_W-J-V 2007-02-13_W-J-V 2010-03-12_W-J-V 2010-03-12_W-S-I+ 2007-02-13_W-S-I+ 2009-03-28_W-S-I+
do
    \ls -1d ${SUBARUDIR}/${pprun}/SCIENCE_norm/BINNED/*/ >> superflatable.log
done
