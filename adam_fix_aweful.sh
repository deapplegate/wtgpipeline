#! /bin/bash -xv
#adam-does# this code changes the coordinates of region files from physical to fk5
#adam-predecessor# this code came from /u/ki/awright/data/MACS0416-24/W-C-RC_2010-11-04/reg/wcs2phys.sh
#adam-call_example# ./adam_wcs2phys.sh /u/ki/awright/data/MACS0416-24/W-C-RC/SCIENCE/autosuppression/ /u/ki/awright/data/MACS0416-24/W-C-RC/SCIENCE/ OCF
#adam-comments# could be adapted to change other properties as well
regdir="/u/ki/awright/data/MACS1115+01/W-C-RC_2010-03-12/SCIENCE/reg"
scidir="/u/ki/awright/data/MACS1115+01/W-C-RC_2010-03-12/SCIENCE"
ending="OCFS"


file=$1


base=`basename ${file}`
BASE_no_ext=`basename ${file} .reg`

ds9 ${scidir}/${BASE_no_ext}${ending}.fits &
sleep 10
xpaset -p ds9 lower
xpaset -p ds9 regions load ${regdir}/wcs_coord_regs/${base}
xpaset -p ds9 regions format ds9
sleep 1
xpaset -p ds9 regions system image
sleep 2
#xpaset -p ds9 regions skyformat sexagesimal
xpaset -p ds9 regions save ${regdir}/${base}
sleep 2
xpaset -p ds9 regions delete all
sleep 5
wc -l ${file} ${regdir}//${base}
echo ''

xpaset -p ds9 exit
