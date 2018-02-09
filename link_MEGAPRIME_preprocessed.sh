#! /bin/bash -xv

REDDIR=`pwd`

cluster=$1
clusterMP=`echo ${cluster} | sed 's/+/p/g' | sed 's/-/m/g'`

SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
MPDIR=/nfs/slac/g/ki/ki06/anja/MEGAPRIME/CLUSTERS

filters="u g r i z"
ending="C"

if [ -d ${MPDIR}/${clusterMP} ]; then
    cd ${MPDIR}/${clusterMP}
else
    echo "No directory ${MPDIR}/${clusterMP} !"
    exit 2
fi

for filter in ${filters}
do

    if [ -d ${filter} ] && [ -d WEIGHTS_${filter} ] && [ ! $(ls -1 ${filter} | wc -l) -eq 0 ]; then
	if [ ! -d ${SUBARUDIR}/${cluster} ]; then
	   mkdir ${SUBARUDIR}/${cluster}
	fi
	if [ ! -d ${SUBARUDIR}/${cluster}/${filter} ]; then
	   mkdir ${SUBARUDIR}/${cluster}/${filter}
	   mkdir ${SUBARUDIR}/${cluster}/${filter}/SCIENCE
	   mkdir ${SUBARUDIR}/${cluster}/${filter}/WEIGHTS
	fi
	
	cd ${SUBARUDIR}/${cluster}/${filter}/SCIENCE
#	ln -s ${MPDIR}/${clusterMP}/${filter}/*${ending}.fits .
	find ${MPDIR}/${clusterMP}/${filter} -name \*${ending}.fits -exec ln -s {} . \;

	cd ${SUBARUDIR}/${cluster}/${filter}/WEIGHTS
#	ln -s ${MPDIR}/${clusterMP}/WEIGHTS_${filter}/*${ending}.weight.fits .
	find ${MPDIR}/${clusterMP}/WEIGHTS_${filter} -name \*${ending}.weight.fits -exec ln -s {} . \;

	cd ${REDDIR}
	./update_config_header_megaprime.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE MEGAPRIME

	cd ${MPDIR}/${clusterMP}

    fi

done
