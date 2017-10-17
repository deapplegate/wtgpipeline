#!/bin/bash -u

export BONN_LOG=0

subarudir=/nfs/slac/g/ki/ki18/anja/SUBARU

for cluster in `cat ${subarudir}/SUBARU.list | awk '{print $1}'`; do

    if [ -d ${subarudir}/${cluster} ]; then

	filters=`ls ${subarudir}/${cluster}`
	for filter in ${filters}; do

	    if [ -d ${subarudir}/${cluster}/${filter}/SCIENCE ]; then

		    ./setup_general.sh ${subarudir}/${cluster}/${filter}/SCIENCE instrument_$$
		    export INSTRUMENT=`cat instrument_$$`
		    if [ "${INSTRUMENT}" != "UNKNOWN" ]; then
			echo ${cluster} ${filter} ${INSTRUMENT}
		    
			./update_config_header.sh ${subarudir}/${cluster}/${filter}/SCIENCE ${INSTRUMENT} ${cluster}

		    fi

	    fi
	done
    fi
done