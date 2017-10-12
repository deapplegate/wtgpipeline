#! /bin/bash
set -xv

### superscript template to do the preprocessing
. progs.ini > /tmp/progs.out 2>&1
REDDIR=`pwd`

####################################################
### the following need to be specified for each run
####################################################

export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU

## adam notes: fgas_Zclusters_doubled_datasets.log
#1# all Z2089 biases are Z2701 biases!
#2# some Z2089 Flats are Z2701 FLATs (the ones in W-J-V from 2010-03-15 and 2010-12-05)
###    Z2089 Flats from (below) actually in Z2701/FLAT right now
###    *SKYFLAT        2010-03-15      W-J-V
###    *DOMEFLAT       2010-12-05      W-J-V
#3# all SUPERFLATs and SUPERFLAT2s from (Z2089 2010-12-05_W-J-V) should be used for (Z2701 2010-12-05 W-J-V)
###    /u/ki/awright/data/from_archive/f_gas_clusters/Z2089/SUPERFLAT_2010-12-05_W-J-V
###    Z2701   2010-12-05      W-J-V
#4# all SUPERFLATs and SUPERFLAT2s  from (Z2089 2010-03-15 W-J-V) should be used for (Z2701 2010-03-15 W-J-V)

## adam notes: adam_group2_process_now.txt
### 2007-02-13_W-J-V 	DOMEFLAT #Z2089   10_2	FLAT
### 2007-02-13_W-J-V 	SKYFLAT  #Z2089   10_2	FLAT
### 2007-02-13_W-S-I+	DOMEFLAT #Z2089   10_2	FLAT
### #2007-02-13_W-S-I+	SCIENCE  #Z2089   10_2	SCIENCE
### #2007-02-13_W-S-I+	SCIENCE  #Z2089   10_2	SUPERFLAT2_2007-02-13_W-S-I+
### #2007-02-13_W-S-I+	SCIENCE  #Z2089   10_2	SUPERFLAT_2007-02-13_W-S-I+
### 2009-03-28_W-S-I+	DOMEFLAT #Z2089   10_3	FLAT
### #2009-03-28_W-S-I+	SCIENCE  #Z2089   10_3	SCIENCE
### #2009-03-28_W-S-I+	SCIENCE  #Z2089   10_3	SUPERFLAT2_2009-03-28_W-S-I+
### #2009-03-28_W-S-I+	SCIENCE  #Z2089   10_3	SUPERFLAT_2009-03-28_W-S-I+
### 2009-03-28_W-S-I+	SKYFLAT  #Z2089   10_3	FLAT
### 2010-03-12_W-J-V 	DOMEFLAT #Z2701   10_3	FLAT
### #2010-03-12_W-J-V 	SCIENCE  #Z2701   10_3	SCIENCE
### #2010-03-12_W-J-V 	SCIENCE  #Z2089   10_3	SUPERFLAT2_2010-03-15_W-J-V
### #2010-03-12_W-J-V 	SCIENCE  #Z2089   10_3	SUPERFLAT_2010-03-15_W-J-V
### 2010-03-12_W-J-V 	SKYFLAT  #Z2701   10_3	FLAT
### #2010-03-12_W-S-I+	SCIENCE  #Z2701   10_3	SCIENCE
### #2010-03-12_W-S-I+	SCIENCE  #Z2701   10_3	SUPERFLAT2_2010-03-15_W-S-I+
### #2010-03-12_W-S-I+	SCIENCE  #Z2701   10_3	SUPERFLAT_2010-03-15_W-S-I+
### 2010-03-12_W-S-I+	SKYFLAT  #Z2701   10_3	FLAT
### #adam-SHNT#2010-11-07_W-J-V (process with 2010-12-05)	SCIENCE  #Z2089   10_3	SUPERFLAT2_2010-12-05_W-J-V ##hopefully I don't need this at all
### 2010-12-05_W-J-V	DOMEFLAT #Z2701   10_3	FLAT
### #2010-12-05_W-J-V	SCIENCE  #Z2089   10_3	SCIENCE
### #2010-12-05_W-J-V	SCIENCE  #Z2701   10_3	SCIENCE
### #2010-12-05_W-J-V	SCIENCE  #Z2089   10_3	SUPERFLAT_2010-12-05_W-J-V

#adam# maybe helpful to copy later
#for run in "2007-02-13" "2009-03-28" "2010-03-12" "2010-12-05"
#do
#	for filter in "W-J-V" "W-S-I+"
#	do
#		if [ -d ${SUBARUDIR}/${run}_${filter}/ ]; then
#			echo "${run}_${filter} exists"
#		else
#			echo "${run}_${filter} NOT REAL"
#		fi
#	done

## define run/filter/flat (ex. run=2010-11-04 ; filter="W-C-RC" ; FLAT=SKYFLAT)
##adam-pprun-PPRUN-list
#done on ki05# run="2007-02-13" ; filter="W-J-V"; FLAT=DOMEFLAT #Z2089   10_2 2007-02-13_W-J-V
#done on ki05# see /nfs/slac/g/ki/ki05/anja/SUBARU/2006-12-21_W-J-V/SCIENCE_DOMEFLAT_SET4
#done on ki05# run="2007-02-13" ; filter="W-J-V"; FLAT=SKYFLAT  #Z2089   10_2 2007-02-13_W-J-V
run="2007-02-13" ; filter="W-S-I+";FLAT=DOMEFLAT #Z2089   10_2 2007-02-13_W-S-I+
run="2009-03-28" ; filter="W-S-I+";FLAT=DOMEFLAT #Z2089   10_3 2009-03-28_W-S-I+
#run="2009-03-28" ; filter="W-S-I+";FLAT=SKYFLAT  #Z2089   10_3 2009-03-28_W-S-I+
run="2010-03-12" ; filter="W-J-V"; FLAT=DOMEFLAT #Z2701   10_3 2010-03-12_W-J-V
#run="2010-03-12" ; filter="W-J-V"; FLAT=SKYFLAT  #Z2701   10_3 2010-03-12_W-J-V
run="2010-03-12" ; filter="W-S-I+";FLAT=SKYFLAT  #Z2701   10_3 2010-03-12_W-S-I+
run="2010-12-05" ; filter="W-J-V"; FLAT=DOMEFLAT #Z2701   10_3 2010-12-05_W-J-V

export BONN_TARGET=${run}
export BONN_FILTER=${filter}

#FLAT=        # SKYFLAT or DOMEFLAT
SET=SET3            # sets time period of flat to use
SKYBACK=256          # in case of SKYFLAT: size of background mesh for superflat
                    # illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?)
                    # 16 (or 32) if lots of blobs

#adam# fringing correction for Z band only
FRINGE=NOFRINGE       # FRINGE if fringing correction necessary; NOFRINGE otherwise
SCIENCEDIR=SCIENCE_${FLAT}_${SET}

####################################################
###
####################################################
if [ ${FRINGE} == "FRINGE" ]; then
    ending="OCFSF"
elif [ ${FRINGE} == "NOFRINGE" ]; then
    ending="OCFS"
else
    echo "You need to specify FRINGE or NOFRINGE for the fringing correction!"
    exit 2;
fi

export INSTRUMENT=SUBARU
filter=${pprun#2*_}
run=${pprun%_*}
#pprun="2007-02-13_W-S-I+"
#pprun="2009-03-28_W-S-I+"
#pprun="2010-03-12_W-J-V"
#pprun="2010-03-12_W-S-I+"
#pprun="2010-12-05_W-J-V"

#for pprun "2007-02-13_W-S-I+" "2009-03-28_W-S-I+" "2010-03-12_W-J-V" "2010-03-12_W-S-I+" "2010-12-05_W-J-V"
#also this one later on: "2007-02-13_W-J-V"
#for pprun in "2015-12-15_W-J-B" "2015-12-15_W-S-Z+" "2015-12-15_W-C-RC" "2012-07-23_W-C-RC" "2010-11-04_W-J-B" "2010-11-04_W-S-Z+" "2010-03-12_W-C-RC" "2010-03-12_W-J-B" "2010-03-12_W-S-Z+" "2009-09-19_W-J-V" "2009-04-29_W-J-B" "2009-04-29_W-S-Z+" "2009-03-28_W-J-V"
#for pprun in "2012-07-23_W-C-RC" "2010-11-04_W-J-B" "2010-11-04_W-S-Z+" "2010-03-12_W-C-RC" "2010-03-12_W-J-B" "2010-03-12_W-S-Z+" "2009-09-19_W-J-V" "2009-04-29_W-J-B" "2009-04-29_W-S-Z+" "2009-03-28_W-J-V"
#for pprun in 2013-06-10_W-S-Z+   2007-02-13_W-S-I+   2007-02-13_W-J-V    2009-03-28_W-S-I+   2010-03-12_W-J-V    2010-03-12_W-S-I+   2010-12-05_W-J-V
for pprun in 2007-02-13_W-S-I+   2007-02-13_W-J-V    2009-03-28_W-S-I+   2010-03-12_W-J-V    2010-03-12_W-S-I+   2010-12-05_W-J-V 2010-11-07_W-J-V #remember 2010-11-07_W-J-V isn't really a legit thing, it's added to 2010-12-05_W-J-V later!
do
	filter=${pprun#2*_}
	run=${pprun%_*}
	ls -d ${SUBARUDIR}/${run}_${filter}/SCIENCE/diffmask
	#	echo "ok, proceed"
	#else
	#	echo "adam-look: ${SUBARUDIR}/${run}_${filter}/SCIENCE/diffmask exists already!"
	#	continue
	#fi

	#adam# have to copy SCIENCE/SUPA*OCF.fits files over to ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR
	./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
	. ${INSTRUMENT:?}.ini > /tmp/instrum.out 2>&1

	#adam-add# need the spikefinder here to make the superflat work later on
	./parallel_manager.sh ./spikefinder_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA OCF ${filter}
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi

done
