#!/bin/bash
set -xv

##template for switching##
run=2015-12-15;filter=W-S-Z+;FLAT=DOMEFLAT
SUBARUDIR="/nfs/slac/g/ki/ki18/anja/SUBARU/"

./parallel_manager.sh adam_CTcorr_make_images_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE " O X C F"
exit_stat=$? #use ${PIPESTATUS[0]} if it's <command> | tee -a OUT-command.log                                                                                                      
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi
./parallel_manager.sh ./adam_CTcorr_early_run_correction_para.py ${filter} ${run} OCF
exit_stat=$? #use ${PIPESTATUS[0]} if it's <command> | tee -a OUT-command.log                                                                                                      
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi

## now rename OCFX to OCF and delete unneeded files
FILES=`\ls ${SUBARUDIR}/${run}_${filter}/SCIENCE/SUPA*OCFX.fits`
mkdir ${SUBARUDIR}/${run}_${filter}/SCIENCE/IM_PRE_CTcorr
for flX in $FILES
do
	echo $flX > tmp_$$
	fl=`sed 's/OCFX.fits/OCF.fits/g' tmp_$$`
	bfl=`basename $fl`
	flO=${bfl%*CF.fits}
	mv $fl ${SUBARUDIR}/${run}_${filter}/SCIENCE/IM_PRE_CTcorr
	rename 's/OCFX.fits/OCF.fits/g' $flX
	rm ${SUBARUDIR}/${run}_${filter}/SCIENCE/IM_O/${flO}*.fits
	rm ${SUBARUDIR}/${run}_${filter}/SCIENCE/IM_OX/${flO}*.fits
	rm ${SUBARUDIR}/${run}_${filter}/SCIENCE/IM_OC_and_OXC/${flO}*.fits
	rm ${SUBARUDIR}/${run}_${filter}/SCIENCE/IM_diff/${flO}*.fits
done

echo "deleting these empty dirs:"
find ${SUBARUDIR}/${run}_${filter}/SCIENCE/ -type d -empty -print
find ${SUBARUDIR}/${run}_${filter}/SCIENCE/ -type d -empty -delete
