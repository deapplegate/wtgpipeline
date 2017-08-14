#!/bin/bash -u

subarudir=/nfs/slac/g/ki/ki05/anja/SUBARU

clusters=`ls ${subarudir}`
for cluster in ${clusters}; do

    if [ -d ${subarudir}/${cluster} ]; then

	echo ${cluster}

	filters=`ls ${subarudir}/${cluster}`
	for filter in ${filters}; do

	    if [ -d ${subarudir}/${cluster}/${filter}/SCIENCE ]; then

		echo "  ${filter}"

		headercats=`ls ${subarudir}/${cluster}/${filter}/SCIENCE | grep headers`
		for headercat in ${headercats}; do

		    headerdir=${subarudir}/${cluster}/${filter}/SCIENCE/${headercat}
		    if [ -d ${headerdir} ]; then

			echo "    ${headerdir}"
			files=`find $headerdir -name \*.head -printf "%f\n"`

			for file in ${files}; do
			
			    base=`echo ${file} | perl -e '<STDIN> =~ /(.+_\d+)/; print "$1\n";'`
			    if [ "${base}.head" != "${file}" ]; then
#			    echo ${headerdir}/${file} ${headerdir}/${base}.head
				mv ${headerdir}/${file} ${headerdir}/${base}.head
			    fi
			    

			done
		    fi
		done
	    fi
	done
    fi
done