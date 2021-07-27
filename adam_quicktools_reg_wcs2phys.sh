#! /bin/bash -xv
#adam-does# this code changes the coordinates of region files from fk5 to image
#adam-predecessor# this code came from /u/ki/awright/data/MACS0416-24/W-C-RC_2010-11-04/reg/wcs2phys.sh
#adam-call_example# ./adam_quicktools_reg_wcs2phys.sh
#adam-comments# could be adapted to change other properties as well

##IMPORTANT NOTE##
##THIS WILL KILL ALL THE ds9 WINDOWS ON THIS HOST!
echo "THIS WILL KILL ALL THE ds9 WINDOWS ON THIS HOST!"






regdir="${SUBARUDIR}/${cluster}/W-C-RC/SCIENCE/autosuppression/"
scidir="${SUBARUDIR}/${cluster}/W-C-RC/SCIENCE/"
ending="OCFSI"
mkdir ${regdir}/image_coord_regs/
mkdir ${regdir}/wcs_coord_regs/


#for file in $(ls -1 ${regdir}/SUPA*.reg)
for file in $(ls -1 ~/my_data/SUBARU/RXJ2129/W-C-RC/SCIENCE/autosuppression/SUPA0032911_*.reg)
do

	base=`basename ${file}`
	BASE_no_ext=`basename ${file} .reg`

	ds9 ${scidir}/${BASE_no_ext}${ending}.fits &
	sleep 10
	xpaset -p ds9 lower
	xpaset -p ds9 regions load ${file}
	xpaset -p ds9 regions format ds9
	sleep 1
	xpaset -p ds9 regions system image
	sleep 2
	#xpaset -p ds9 regions skyformat sexagesimal
	xpaset -p ds9 regions save ${regdir}/image_coord_regs/${base}
	sleep 2
	xpaset -p ds9 regions delete all
	sleep 3
	#wc -l ${file} ${regdir}//${base}
	mv ${file} ${regdir}/wcs_coord_regs/
	cp -n ${regdir}/image_coord_regs/${base} ${regdir}/
	echo "done with ${base}"

done

xpaset -p ds9 exit
