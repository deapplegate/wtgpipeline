#!/bin/bash

cat referenceset | awk '($1 !~ "#"){print}' | { 

    while read cluster lfilter image; do

	echo $cluster $filter $image
	
	pfilters=`grep "${cluster}" cluster_cat_filters.dat | awk -v ORS=' ' '{for(i=3;i<=NF;i++){if($i!~"CALIB" && $i!="K") print $i}}'`

	for pfilter in $pfilters; do



	    clusterdir=/u/ki/dapple/subaru/$cluster
	    photdir=$clusterdir/PHOTOMETRY_${lfilter}_aper

	    if [ -e $photdir/$pfilter/unstacked/$cluster.$pfilter.unstacked.cor.cat ]; then
		continue
	    fi

	    echo "  $pfilter"
	    
	    ./run_geocor_unstacked_photometry.sh $clusterdir $photdir $cluster $pfilter
	    if [ $? != 0 ]; then
		echo "    FAIL!"
	    fi

	done

    done
}