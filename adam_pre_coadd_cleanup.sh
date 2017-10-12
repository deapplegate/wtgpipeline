#!/bin/bash
set -xvu

rm -rf ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/plots
rm -rf ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat
rm -rf ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_*
rm ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/MACS*.cat
rm ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/SUPA*.sub.fits

exit 0;

function cleanTmpFiles
{
    if [ -z ${THELI_DEBUG} ]; then
        echo "Cleaning temporary files for script $0"

	for CHIP in ${!#}
        do
          ${P_FIND} ${RESULTDIR[${CHIP}]} \
                    -name \*_${CHIP}$1_weighted.fits    -exec rm -f {} \;
          ${P_FIND} ${RESULTDIR[${CHIP}]} \
                    -name \*_${CHIP}$1_backsub.fits    -exec rm -f {} \;
          ${P_FIND} ${RESULTDIR[${CHIP}]} \
                    -name \*_${CHIP}$1_noobj.fits      -exec rm -f {} \;
          ${P_FIND} ${RESULTDIR[${CHIP}]} \
                    -name \*_${CHIP}$1_noobj_mode.fits -exec rm -f {} \;
          ${P_FIND} ${RESULTDIR[${CHIP}]} \
                    -name \*_${CHIP}$1_skyback.fits    -exec rm -f {} \;
          ${P_FIND} ${RESULTDIR[${CHIP}]} \
                    -name \*_${CHIP}$1_backsub1.fits    -exec rm -f {} \;
          ${P_FIND} ${RESULTDIR[${CHIP}]} \
                    -name \*_${CHIP}$1_skyback1.fits    -exec rm -f {} \;
          ${P_FIND} ${RESULTDIR[${CHIP}]} \
                    -name \*_${CHIP}$1_backsub_noobj.fits    -exec rm -f {} \;
        done
    else
        echo "Variable THELI_DEBUG set! No cleaning of temp. files in script $0"    
    fi
}
