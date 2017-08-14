#! /bin/bash -xv

### template superscript to coadd a set of images
### (set meaning images of the same object, possibly different nights)
###
### $Id: do_Subaru_coadd_rotations.sh,v 1.1 2008-09-05 21:48:13 mallen Exp $

. progs.ini
. bash_functions.include

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki02/xoc/anja/SUBARU

cluster="MACS0018+16"  # cluster nickname as in /nfs/slac/g/ki/ki02/xoc/anja/SUBARU/SUBARU.list
filter="W-J-V"


###############################################
######################
#Some Setup Stuff

export BONN_TARGET=$cluster
export BONN_FILTER=$filter


lookupfile=/nfs/slac/g/ki/ki02/xoc/anja/SUBARU/SUBARU.list

#Find Ending
testfile=`ls -1 $SUBARUDIR/$cluster/$filter/SCIENCE/SUPA*_2*.fits | awk 'NR>1{exit};1'`
ending=`filename $testfile | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`

########################################
### Reset Logger
./BonnLogger.py clear

./setup_SUBARU.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE
export INSTRUMENT=SUBARU
. ${INSTRUMENT:?}.ini


##################################################################
### Capture Variables
./BonnLogger.py config \
    cluster=${cluster} \
    filter=${filter} \
    config=${config} \
    ending=${ending}

./BonnLogger.py comment "COADDING BY ROTATON 0"
rot=0


##################
### coaddition ###
##################


ra=`grep ${cluster} ${lookupfile} | awk '{print $3}'`
dec=`grep ${cluster} ${lookupfile} | awk '{print $4}'`

echo ${cluster} ${ra} ${dec}


#
# this makes the all of the coadded images
# on the same patch of sky

cp coadd.head coadd.ROT0.head
cp coadd.head coadd.ROT1.head



./perform_coadd_rot_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}
exit 0;

### add header keywords

