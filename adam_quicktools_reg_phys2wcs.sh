#! /bin/bash -xv
#adam-does# this code changes the coordinates of region files from physical to fk5
#adam-predecessor# this code came from /u/ki/awright/data/MACS0416-24/W-C-RC_2010-11-04/reg/wcs2phys.sh
#adam-call_example# ./adam_wcs2phys.sh /u/ki/awright/data/MACS0416-24/W-C-RC/SCIENCE/autosuppression/ /u/ki/awright/data/MACS0416-24/W-C-RC/SCIENCE/ OCF
#adam-comments# could be adapted to change other properties as well
regdir="/u/ki/awright/data/MACS1226+21/W-C-RC_2010-02-12/SCIENCE/reg"
scidir="/u/ki/awright/data/MACS1226+21/W-C-RC_2010-02-12/SCIENCE"
ending="OCF"


for file in $(ls -1 ${regdir}/SUPA011833[4-6]_*.reg)
do

base=`basename ${file}`
BASE_no_ext=`basename ${file} .reg`

ds9 ${scidir}/${BASE_no_ext}${ending}.fits &
sleep 5
xpaset -p ds9 lower
xpaset -p ds9 regions load ${file}
xpaset -p ds9 regions format ds9
xpaset -p ds9 regions system wcs
#xpaset -p ds9 regions skyformat sexagesimal
xpaset -p ds9 regions save ${regdir}/wcs_regs/${base}
xpaset -p ds9 regions delete all

done

xpaset -p ds9 exit
