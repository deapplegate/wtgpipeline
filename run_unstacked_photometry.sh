#!/bin/bash
set -uxv
##########################
# Takes a directory coadded by all, and by exposure
#   and measures and compiles photometry on a per exposure basis
###########################

# $Id: run_unstacked_photometry.sh,v 1.26 2010-10-05 22:45:26 dapple Exp $

#############################

# $1 : Cluster dir
# $2 : Photdir
# $3 : Cluster
# $4 : Filter
# $5 : Detection Image
# $6 : Target Seeing

clusterdir=$1
photdir=$2
cluster=$3
filter=$4
detect=$5
convolve=$6

############################

. progs.ini > /tmp/out.log 2>&1

##############################

special_filters="I K"

###############################

unstacked_dir=$photdir/${filter}/unstacked

if [ ! -d ${unstacked_dir} ]; then
    mkdir -p ${unstacked_dir}
fi


#### Pre-req Test
inSpecialFilters=`echo $special_filters | grep $filter`
if [ -z "$inSpecialFilters" ] && [ ! -e $clusterdir/$filter/SCIENCE/cat/chips.cat8 ]; then
    echo "chips.cat8 files does not exist"
    exit 15
fi



### Generate catalogs for individual exposures

detect_dir=`dirname $detect`
detect_base=`basename $detect .fits`
detect_weight=${detect_dir}/${detect_base}.weight.fits
detect_cat=${detect_dir}/detection.cat
if [ ! -e ${detect_cat} ]; then
    echo "Cannot Find Detection Catalog: $detect_cat"
    exit 14
fi

exposures=`ldactoasc -i $clusterdir/$filter/SCIENCE/${cluster}_all.cat -t STATS -b -s -k IMAGENAME ${cluster}_all | awk '($2 == 1){print $1}'`
exposures="${exposures} all"

catfiles=""
for exposure in $exposures; do

    file=$clusterdir/$filter/SCIENCE/coadd_${cluster}_$exposure/coadd.fits

    if [ -e $file ]; then

	measure_dir=`dirname $file`
	measure_base=`basename $file .fits`
	measure_weight=${measure_dir}/${measure_base}.weight.fits
	measure_flag=${measure_dir}/${measure_base}.flag.fits
	seeing=`dfits $file | fitsort -d SEEING | awk '{print $2}'`
	
	tag=`echo $measure_dir | awk -F '_' '{print $NF}'`

	./extract_object_cats.py --di $detect --dw $detect_weight \
	    --pi $file --pw $measure_weight --pf $measure_flag \
	    -o ${unstacked_dir}/${tag}.filtered.cat --fwhm ${seeing} --new-fwhm ${convolve} \
	    --areacat ${detect_cat}
	exit_code=$?
	if [ "$exit_code" != "0" ]; then
	    echo "Failure in do_multiple_exposures.py: $exit_code" 
	    exit $exit_code
	fi

	catfiles="$catfiles ${unstacked_dir}/${tag}.filtered.cat"
	
    else
	echo "Missing Exposure: ${exposure}"
	exit 1
    fi


done




# Sort catalogs by instrument and config

if [ -e unstacked.exp.list_$$ ]; then
    rm -f unstacked.exp.list_$$
fi

############################
#special filters
inSpecialFilters=`echo ${special_filters} | grep ${filter}`
if [ -n "$inSpecialFilters" ]; then
    ./convertSpecialFilters.py ${catfiles} ${unstacked_dir}/${cluster}.${filter}.unstacked.cat
    exit 0   
fi
#############################



mastercat=""
for cat in $catfiles; do

    base=`basename $cat`

    expid=`echo $base | awk -F'.' '{print $1}'`

    if [ "$expid" == "all" ];then
	mastercat=$cat
	continue
    fi

    exp_instrum_config=`ldactoasc -i $clusterdir/$filter/SCIENCE/cat/chips.cat8 -t CHIPS_STATS -s -b -k INSTRUM CONFIG FITSFILE | grep "$expid" | awk '{print $1, $2}' | sort | uniq`
    instrum=`echo $exp_instrum_config | awk '{print $1}'`
    config=`echo $exp_instrum_config | awk '{print $2}'`

    if [ "${instrum}" == "0" ]; then
	instrum='SPECIAL'
	config="0"
    fi

    echo $cat ${instrum}-${config} >> unstacked.exp.list_$$
done

if [ "${filter}" == "B-WHT" ]; then
    filter=B
elif [ "${filter}" == "U-WHT" ]; then
    filter=U
fi

configs=`awk '{print $2}' unstacked.exp.list_$$ | sort | uniq`
# Combine catalogs into final catalog
echo "adam-look: configs=$configs for $cluster - $filter"
merge_line=""
for config in $configs; do


    cats=`grep "$config" unstacked.exp.list_$$ | awk -v ORS=' ' '{print $1}'`

    ./measure_unstacked_photometry.py -o $unstacked_dir/$cluster.$filter.$config.unstacked.cat -i $config -m $mastercat $cats
  
    exit_code=$?
    if [ "$exit_code" != "0" ]; then
	echo "$exit_code Failure in measure_unstacked_photometry.py"
	exit $exit_code
    fi
    
    if [ ! -s $unstacked_dir/$cluster.$filter.$config.unstacked.cat ]; then
	echo "Final catalog not produced: $unstacked_dir/$cluster.$filter.$config.unstacked.cat"
	exit 1
    fi
    
    merge_line="$merge_line $unstacked_dir/$cluster.$filter.$config.unstacked.cat"

done

instrum=`awk '{if (NR==1) print $2}' unstacked.exp.list_$$ | awk -F'-' '{print $1}'`

./combine_unstacked_config_cats.py $unstacked_dir/$cluster.$filter.unstacked.cat $instrum $mastercat $merge_line

rm -f unstacked.exp.list_$$
