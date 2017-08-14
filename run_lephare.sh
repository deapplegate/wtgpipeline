#! /bin/bash -xv

maindir=$1
CLUSTER=$2
PHOTOMETRYDIR=$3
LEPHARE_CONFIGFILE=$4
naper=$5
makelibs=$6

export LEPHAREDIR=/nfs/slac/g/ki/ki04/pkelly/lephare_dev/
export LEPHAREWORK=/nfs/slac/g/ki/ki04/pkelly/lepharework/




if [ ${makelibs} == "libs"  ]; then
    ${LEPHAREDIR}/source/filter -c ${LEPHARE_CONFIGFILE} 
    ${LEPHAREDIR}/source/sedtolib -t G -c ${LEPHARE_CONFIGFILE} 
    ${LEPHAREDIR}/source/sedtolib -t S -c ${LEPHARE_CONFIGFILE} 
    ${LEPHAREDIR}/source/mag_star -c ${LEPHARE_CONFIGFILE} 
    ${LEPHAREDIR}/source/mag_gal -t G -c ${LEPHARE_CONFIGFILE}
fi


for (( iaper=0; iaper<naper ; iaper+=1 )); do 
    # run once for spectra,

    ${LEPHAREDIR}/source/zphota -c ${LEPHARE_CONFIGFILE}  \
	-CAT_TYPE     LONG \
	-CAT_IN ${SUBARUDIR}/${CLUSTER}/${PHOTOMETRYDIR}/spec.nocluster.cat.lph${iaper} \
	-CAT_OUT  ${SUBARUDIR}/${CLUSTER}/${PHOTOMETRYDIR}/${CLUSTER}.${iaper}.spec.zs 



    ./lph_outliers.py  $SUBARUDIR/${CLUSTER}/PHOTOMETRY/${CLUSTER}.${iaper}.spec.zs \
	    $SUBARUDIR/${CLUSTER}/PHOTOMETRY/spec.nocluster.cat.lph${iaper}

    ${LEPHAREDIR}/source/zphota -c ${LEPHARE_CONFIGFILE}  \
	-CAT_TYPE     LONG \
	-SPEC_OUT  YES \
	-CAT_IN ${SUBARUDIR}/${CLUSTER}/${PHOTOMETRYDIR}/spec.nocluster.cat.lph${iaper}.1 \
	-CAT_OUT  ${SUBARUDIR}/${CLUSTER}/${PHOTOMETRYDIR}/${CLUSTER}.${iaper}.spec.zs 
 
    raw_input()
	
#
# This next part gets the adjusted zeropoints:  
#     Sorry for the hackery...
    ZSHIFTS=`grep SHIFTS  ${SUBARUDIR}/${CLUSTER}/${PHOTOMETRYDIR}/${CLUSTER}.${iaper}.spec.zs |\
		awk -F"SHIFTS" '{print $2}' |\
		sed 's/\,/\ /g' | \
		awk '{{for(i=1; i<=NF; i++) if(i<NF) txt=txt$(i)","; else txt=txt$(i); }; print txt}' txt=""`
#    	exit 0;

    # run again for everything
    ${LEPHAREDIR}/source/zphota -c ${LEPHARE_CONFIGFILE}  \
	-APPLY_SHIFT ${ZSHIFTS} \
	-AUTO_ADAPT NO \
	-CAT_TYPE     LONG  \
	-CAT_IN ${SUBARUDIR}/${CLUSTER}/${PHOTOMETRYDIR}/all.cat.lph${iaper} \
	-CAT_OUT  ${SUBARUDIR}/${CLUSTER}/${PHOTOMETRYDIR}/${CLUSTER}.${iaper}.all.zs \
	-PDZ_OUT /tmp/${CLUSTER}.tmp.${iaper}.pdz



    ./save_pdz.py /tmp/${CLUSTER}.tmp.${iaper}.pdz.pdz  ${SUBARUDIR}/${CLUSTER}/PHOTOMETRY/${CLUSTER}.${iaper}.all.zs  ${SUBARUDIR}/${CLUSTER}/PHOTOMETRY/${CLUSTER}.${iaper}.pdz

done

