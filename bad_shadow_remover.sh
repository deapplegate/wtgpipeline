#!/bin/bash
set -xv
#adam-does# this makes ds9 screenshots of the spikefinder stuff (masks and images) so you can see if sf did ok
#adam-example# ./bad_shadow_remover.sh /u/ki/awright/data/2015-12-15_W-S-Z+/SCIENCE/diffmask
echo "moving to $1"
OCFsfdir=$1
OCFdir=${OCFsfdir%diffmask*}

#for CHIP in 1 2 3 4 5
#do
#	ims=`\ls ${OCFsfdir}/SUPA[0-9][0-9][0-9][0-9][0-9][0-9][0-9]_${CHIP}OCF.sf.fits`
#	ds9 -title "CHIP=${CHIP} are there any false shadows?" -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -scale limits 0 1 ${ims} -frame lock image -zoom to fit -saveimage png "${OCFsfdir}/plt_shadowcheck_bottomrow_chip${CHIP}.png" -quit
#done

for CHIP in 6 7 8 9 10
do
	ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale ${OCFdir}/SUPA[0-9][0-9][0-9][0-9][0-9][0-9][0-9]_${CHIP}OCF.fits -frame lock image -zoom to fit -saveimage png "${OCFsfdir}/plt_shadowcheck_toprow_IMAGE_chip${CHIP}.png" -quit
	fls=`\ls ${OCFdir}/SUPA[0-9][0-9][0-9][0-9][0-9][0-9][0-9]_${CHIP}OCF.fits`
	echo "#!/bin/bash" > ${OCFsfdir}/remove_bad_shadows_chip${CHIP}.sh
	for fl in ${fls}
	do
		BASE=`basename ${fl} .fits`
		echo "ic '%1 %2 *' ${BASE}.sp.fits ${BASE}.sa.fits > ${BASE}.sf.fits" >> ${OCFsfdir}/remove_bad_shadows_chip${CHIP}.sh
	done
	chmod u+x ${OCFsfdir}/remove_bad_shadows_chip${CHIP}.sh

	ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -scale limits 0 1 ${OCFsfdir}/SUPA[0-9][0-9][0-9][0-9][0-9][0-9][0-9]_${CHIP}OCF.sf.fits -frame lock image -zoom to fit -saveimage png "${OCFsfdir}/plt_shadowcheck_toprow_MASK_chip${CHIP}.png" -quit
	echo "if chip #${CHIP} has no shadow, then run the following:"
	echo "./remove_bad_shadows_chip${CHIP}.sh"
done

exit 0;

#adam-tmp# examples
#rename 's/SUPA/oldSUPA/g' SUPA0110211_9OCF.sf.fits
#rename 's/SUPA/oldSUPA/g' SUPA0110212_9OCF.sf.fits
#rename 's/SUPA/oldSUPA/g' SUPA0111270_9OCF.sf.fits
#rename 's/SUPA/oldSUPA/g' SUPA0111271_9OCF.sf.fits
#ic '%1 %2 *' SUPA0110169_9OCF.sh.fits oldSUPA0110211_9OCF.sf.fits > SUPA0110211_9OCF.sf.fits                                                                                           
#ic '%1 %2 *' SUPA0110169_9OCF.sh.fits oldSUPA0110212_9OCF.sf.fits > SUPA0110212_9OCF.sf.fits
#ic '%1 %2 *' SUPA0110169_9OCF.sh.fits oldSUPA0111270_9OCF.sf.fits > SUPA0111270_9OCF.sf.fits                                                                                           
#ic '%1 %2 *' SUPA0110169_9OCF.sh.fits oldSUPA0111271_9OCF.sf.fits > SUPA0111271_9OCF.sf.fits
