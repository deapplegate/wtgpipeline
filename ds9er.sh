#! /bin/bash -xv

### superscript template to do the preprocessing
. progs.ini > /tmp/progs.out 2>&1
REDDIR=`pwd`

### the following need to be specified for each run

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
### #2010-11-07_W-J-V	SCIENCE  #Z2089   10_3	SUPERFLAT2_2010-12-05_W-J-V ##hopefully I don't need this at all
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
run="2007-02-13" ; filter="W-J-V"; FLAT=DOMEFLAT #Z2089   10_2 2007-02-13_W-J-V
run="2007-02-13" ; filter="W-J-V"; FLAT=SKYFLAT  #Z2089   10_2 2007-02-13_W-J-V
run="2007-02-13" ; filter="W-S-I+";FLAT=DOMEFLAT #Z2089   10_2 2007-02-13_W-S-I+
run="2009-03-28" ; filter="W-S-I+";FLAT=DOMEFLAT #Z2089   10_3 2009-03-28_W-S-I+
run="2009-03-28" ; filter="W-S-I+";FLAT=SKYFLAT  #Z2089   10_3 2009-03-28_W-S-I+
run="2010-03-12" ; filter="W-J-V"; FLAT=DOMEFLAT #Z2701   10_3 2010-03-12_W-J-V
run="2010-03-12" ; filter="W-J-V"; FLAT=SKYFLAT  #Z2701   10_3 2010-03-12_W-J-V
run="2010-03-12" ; filter="W-S-I+";FLAT=SKYFLAT  #Z2701   10_3 2010-03-12_W-S-I+
run="2010-12-05" ; filter="W-J-V"; FLAT=DOMEFLAT #Z2701   10_3 2010-12-05_W-J-V

export BONN_TARGET=${run}
export BONN_FILTER=${filter}

#FLAT=        # SKYFLAT or DOMEFLAT
SET=SET1            # sets time period of flat to use
SKYBACK=256          # in case of SKYFLAT: size of background mesh for superflat
                    # illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?)
                    # 16 (or 32) if lots of blobs

FRINGE=NOFRINGE       # FRINGE if fringing correction necessary; NOFRINGE otherwise

###
if [ ${FRINGE} == "FRINGE" ]; then
    ending="OCFSF"
elif [ ${FRINGE} == "NOFRINGE" ]; then
    ending="OCFS"
else
    echo "You need to specify FRINGE or NOFRINGE for the fringing correction!"
    exit 2;
fi
### Reset Logger
#adam-BL# ./BonnLogger.py clear
# if needed: cp auxiliary data
#adam# use this to sort the downloaded data
###DARK Step (1)# make DARK dir if I haven't already
###./cp_aux_data.sh /nfs/slac/g/ki/ki18/anja/SUBARU 10_3_DARK /nfs/slac/g/ki/ki18/anja/SUBARU/from_archive/darks
###./cp_aux_data.sh ${SUBARUDIR} [optional run directory] ${SUBARUDIR}/${run}_RAWDATA

### create and load the SUBARU.ini file
### !!! DO NOT COMMENT THIS BLOCK !!!
###
### well, this only works after some data has been adapted to
### THELI format. otherwise, make sure that SUBARU.ini has the
### right configuration (10_3)

export INSTRUMENT=SUBARU

. ${INSTRUMENT:?}.ini
for run in "2007-02-13" "2009-03-28" "2010-03-12" "2010-12-05"
do
	for filter in  "W-S-I+" "W-J-V"
	do
		if [ -d ${SUBARUDIR}/${run}_${filter}/SCIENCE/ ] ; then
		       #adam-DO# if there is another type of flat (which hasn't been processed yet), change which flat you're using and start over at #STARTOVER-OTHER FLAT CHOSEN
		       echo "adam-look| #BEFORE moving on to the next step, I'll have to rm SCIENCE and replace it with either SCIENCE_DOMEFLAT or SCIENCE_SKYFLAT!"
		       echo "adam-look| rm -r ${SUBARUDIR}/${run}_${filter}/SCIENCE/"
		       echo "adam-look| mv ${SUBARUDIR}/${run}_${filter}/SCIENCE_DOMEFLAT/ ${SUBARUDIR}/${run}_${filter}/SCIENCE/"
		       echo "adam-look| OR"
		       echo "adam-look| mv ${SUBARUDIR}/${run}_${filter}/SCIENCE_SKYFLAT/ ${SUBARUDIR}/${run}_${filter}/SCIENCE/"
		       if [ -d ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm]; then
			ds9 -zscale -geometry 2000x2000 ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm/BINNED/*mosOCFN.fits -zoom to fit &
		       elif [ -d ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm_SKYFLAT ]; then
			ds9 -zscale -geometry 2000x2000 ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm_SKYFLAT/BINNED/*mosOCFN.fits -zoom to fit
		       elif [ -d ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm_DOMEFLAT ]; then
			ds9 -zscale -geometry 2000x2000 ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm_DOMEFLAT/BINNED/*mosOCFN.fits -zoom to fit
		       fi
		       #adam-DO check# choose which FLAT is better by comparing science images
		       echo "if there are two flats available and you still have to process the other one, then start over here"
		       echo "check: the normalized science images from which type of flat looks better?"
		       #adam-DO pick/restart# determine which flat is better and continue on from here using only one flat (change beginning of script to make sure you have the right one, then go to #STARTOVER-OTHER FLAT CHOSEN)
		       #### this is it if we assume we don't need a fringing correction...
		fi
	done
done
exit 0; #8-9
