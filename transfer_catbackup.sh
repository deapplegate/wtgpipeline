#!/bin/bash -u

worklist=$1
outdir=$2
overwrite=False
if [ $# -gt 2 ]; then
    overwrite=$3
fi

subarudir=/nfs/slac/g/ki/ki05/anja/SUBARU

OK2Write(){
    dest=$1
    if ( [ -e $dest ] && [ $overwrite = True ] ) || [ ! -e $dest ]; then
	return 0
    else
	return 1
    fi
}

###############

copy(){
    src=$1
    dest=$2
    if OK2Write $dest; then
	cp $src $dest
    fi
}

###############

awk '($1 !~ "#"){print}' $worklist | {
    while read cluster filter image; do
	
	echo "Working on $cluster $filter $image"

	photdir=$subarudir/$cluster/PHOTOMETRY_${filter}_aper
	lensdir=$subarudir/$cluster/LENSING_${filter}_${filter}_aper/$image

	copy $photdir/$cluster.slr.cat $outdir/$cluster.$filter.cat
	copy $photdir/$cluster.APER1.1.CWWSB_capak.list.all.bpz.tab $outdir/$cluster.$filter.bpz.tab
	copy $lensdir/cut_lensing.cat $outdir/$cluster.$filter.$image.cut_lensing.cat
	copy $lensdir/coadd_photo.cat $outdir/$cluster.$filter.$image.lensingbase.cat
	copy $lensdir/${cluster}_redsequence.cat $outdir/$cluster.$filter.$image.redsequence.cat
	copy $lensdir/neighbors.cat $outdir/$cluster.$filter.$image.neighbors.cat

	inputpdz=$photdir/$cluster.APER1.1.CWWSB_capak.list.all.probs
	outputpdz=$outdir/$cluster.$filter.pdz.cat
	if OK2Write $outputpdz; then
	    bsub -q medium python pdzfile_utils.py $inputpdz $outputpdz
#	    python pdzfile_utils.py $inputpdz $outputpdz
	    echo "Submitted PDZ File Job: $cluster $filter $image"
	fi
	
	

    done
}


##################################
##################################
## Testing of OK2Write
#################################
#
#overwrite=False
#touch fakesrc
#touch fakedest1
#
#if OK2Write fakedest1; then
#    echo "Test 1: Failed; Overwrote file that existed"
#else
#    echo "Test 1: Passed; File not overwritten"
#fi
#
#overwrite=True
#if OK2Write fakedest1; then
#    echo "Test 2: Passed; Overwrote file that existed"
#else
#    echo "Test 2: Failed; File not overwritten"
#fi
#
#if OK2Write fakedest2; then
#    echo "Test 3: Passed; No prior file existed"
#else
#    echo "Test 3: Failed; Did not copy into nonexistant file"
#fi
#
#overwrite=False
#if OK2Write fakedest2; then
#    echo "Test 4: Passed; No prior file existed"
#else
#    echo "Test 4: Failed; Did not copy into nonexistant file"
#fi
#
#
