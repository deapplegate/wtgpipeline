#!/bin/bash
SET="SET1"
for pprun in "2007-02-13_W-S-I+" "2009-03-28_W-S-I+" "2010-03-12_W-J-V" "2010-03-12_W-S-I+"
do
	filter=${pprun#2*_}
	run=${pprun%_*}
	if [ -d ${SUBARUDIR}/${run}_${filter}/DOMEFLAT ]; then
		FLAT=DOMEFLAT
	elif [ -d ${SUBARUDIR}/${run}_${filter}/SKYFLAT ]; then
		FLAT=SKYFLAT
	else
		continue
	fi
	SCIENCEDIR=SCIENCE_${FLAT}_${SET}
	echo "SCIENCEDIR=" ${SCIENCEDIR}
	ls ${SUBARUDIR}/${run}_${filter}/${SCIENCEDIR}/SUPA*OCF.fits | wc -l
	ls ${SUBARUDIR}/${run}_${filter}/SCIENCE/SUPA*OCF.fits | wc -l
	ls ${SUBARUDIR}/${run}_${filter}/${SCIENCEDIR}/ > dir.tmp
	sed '/OCF.fits/d' dir.tmp > dir.out
	wc -l dir.out
done
