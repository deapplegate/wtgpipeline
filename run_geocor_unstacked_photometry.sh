#!/bin/bash -u
##########################
# Takes a directory coadded by all, and by exposure
#   and reruns unstacked photometry with new geocor catalogs
###########################

# $Id: run_unstacked_photometry.sh,v 1.26 2010-10-05 22:45:26 dapple Exp $

#############################

# $1 : Cluster dir
# $2 : Photdir
# $3 : Cluster
# $4 : Filter

clusterdir=$1
photdir=$2
cluster=$3
filter=$4


############################

. progs.ini

##############################


special_filters="I K"

############################
#special filters

inSpecialFilters=`echo $special_filters | grep $filter`
if [ -n "$inSpecialFilters" ]; then
    ln $catfiles $unstacked_dir/$cluster.$filter.unstacked.cat $unstacked_dir/$cluster.$filter.unstacked.cor.cat
    exit 0   
fi

###############################

unstacked_dir=$photdir/${filter}/unstacked

exposures=`ldactoasc -i $clusterdir/$filter/SCIENCE/${cluster}_all_reject_2012-05-07 -t STATS -b -s -k IMAGENAME ${cluster}_all | awk '($2 == 1){print $1}'`
echo $exposures
catfiles=""
for exposure in $exposures; do
    curfile=$unstacked_dir/$exposure.filtered.cat.corrected.cat
    if [ ! -e $curfile ]; then
	echo "Cannot find file $curfile"
	exit 3
    fi
    catfiles="$catfiles $curfile"
done


if [ -z "$catfiles" ]; then
    echo "Cannot Find Files"
    exit 1
fi


# Sort catalogs by instrument and config

if [ -e unstacked.exp.list_$$ ]; then
    rm unstacked.exp.list_$$
fi


mastercat=$unstacked_dir/all.filtered.cat
for cat in $catfiles; do

    base=`basename $cat`

    expid=`echo $base | awk -F'.' '{print $1}'`

    if [ "$expid" = "all" ]; then
	continue
    fi


    rotation=`echo $expid | awk '($1 ~ "rot"){print}'`
    if [ -n "$rotation" ]; then
	continue
    fi

    exp_instrum_config=`ldactoasc -i $clusterdir/$filter/SCIENCE/cat/chips.cat8 -t CHIPS_STATS -s -b -k INSTRUM CONFIG FITSFILE | grep "$expid" | awk '{print $1, $2}' | sort | uniq`
    if [ $? != 0 ]; then
	echo "$expid   Cannot find config info"
	exit 1
    fi
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
merge_line=""
for config in $configs; do

    cats=`grep "$config" unstacked.exp.list_$$ | awk -v ORS=' ' '{print $1}'`

    ./measure_unstacked_photometry.py -o $unstacked_dir/$cluster.$filter.$config.unstacked.cor.cat -i $config -m $mastercat $cats
  
    exit_code=$?
    if [ "$exit_code" != "0" ]; then
	echo "$exit_code Failure in measure_unstacked_photometry.py"
	exit $exit_code
    fi
    
    if [ ! -s $unstacked_dir/$cluster.$filter.$config.unstacked.cat ]; then
	echo "Final catalog not produced: $unstacked_dir/$cluster.$filter.$config.unstacked.cat"
	exit 1
    fi
    
    merge_line="$merge_line $unstacked_dir/$cluster.$filter.$config.unstacked.cor.cat"

done

instrum=`awk '{if (NR==1) print $2}' unstacked.exp.list_$$ | awk -F'-' '{print $1}'`

./combine_unstacked_config_cats.py $unstacked_dir/$cluster.$filter.unstacked.cor.cat $instrum $mastercat $merge_line

    

rm unstacked.exp.list_$$
