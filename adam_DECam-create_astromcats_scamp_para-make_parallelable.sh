#!/bin/bash
set -xv
#adam-does# basically this is do_Subaru_register_4batch.sh "astrom" mode
export cluster=A2204
export INSTRUMENT=DECam

lookupfile=/nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
ra=`grep ${cluster} ${lookupfile} | awk '{print $3}'`
dec=`grep ${cluster} ${lookupfile} | awk '{print $4}'`

#ALLCATS=`\ls /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/{u,g,r,i,z,Y}_DECam/single_V0.0.2A/dec*_*OXCLFSF.sub.fits`
LINE=""
for filter in u g r i z Y
do
	LINE="${LINE} /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/${cluster}/${filter}_DECam/ single_V0.0.2A "
  	export filter
        ###./adam_DECam-create_astromcats_scamp_para.sh /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/${filter}_DECam/ single_V0.0.2A/
	sed "s/filterTEMP/${filter}/g" adam_DECam-create_astromcats_scamp_para-TEMPLATE.sh > adam_DECam-create_astromcats_scamp_para-bsub_${filter}.sh
	#\/nfs\/slac\/g\/ki\/ki18\/anja\/DECAM\/CLUSTERSCOLLAB_V0.0.2\/${cluster}\/${filter}_DECam\/
        #\ls /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/${filter}_DECam/single_V0.0.2A/dec*_*OXCL*.sub.fits > subims.log
        #\ls /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/${filter}_DECam/single_V0.0.2A/dec*_*OXCL*.weight.fits > weightims.log
        #\ls /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/${filter}_DECam/single_V0.0.2A/dec*_*OXCL*.flag.fits > flagims.log
        #sub_wt_flag=`wc -l subims.log weightims.log flagims.log`
        #echo $filter , $sub_wt_flag >> decam_data.log
        #./parallel_manager.sh ./create_astromcats_scamp_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE WEIGHTS
done
echo "adam-look: LINE=$LINE"
#ASTROMETRYCAT="astrefcat.cat"
#./create_scamp_astrom_photom.sh ${LINE} ${ASTROMETRYCAT}
#adam-SHNT# ask anja what this ASTROMETRYCAT should be
echo "adam-look: ./create_scamp_astrom_photom.sh \${LINE} \${ASTROMETRYCAT}"

