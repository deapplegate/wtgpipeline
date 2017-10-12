#! /bin/bash -xv

### superscript template to do the preprocessing
. progs.ini > /tmp/progs.out 2>&1
REDDIR=`pwd`
export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
SET=SET1            # sets time period of flat to use
SKYBACK=256          # in case of SKYFLAT: size of background mesh for superflat
                    # illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?)
                    # 16 (or 32) if lots of blobs

FRINGE=NOFRINGE       # FRINGE if fringing correction necessary; NOFRINGE otherwise

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
export run="2009-03-28"
export filter="W-S-I+"
export FLAT="SKYFLAT"
./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/${FLAT}/ORIGINALS/
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi
. ${INSTRUMENT:?}.ini

#### processes SCIENCE frames:
#### overscan, bias, flat -->  SUPA*_${chip}OCF.fits
#adam# process the SCIENCE images result=(science-bias)/(flat-bias)
#makes (in undo form): rm SUPA*OCF.fits ; rm SUPA*OCF_sub.fits ; rm SCIENCE_*.fits ; mv SUB_IMAGES/SUPA*.fits . ; rm -r SUB_IMAGES/
#THIS TAKES ~15 min#
if [ "$config" == "10_3" ] ; then
	./parallel_manager.sh ./process_science_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE} #8
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
elif [ "$config" == "10_2" ] ; then
	./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE} #8
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
else
	echo "problem with config";exit 1
fi
#adam-del# #10_2 & 10_3# this is where process_science_4channels_eclipse_para.sh calls things OCF and process_science_eclipse_para.sh calls things OFC, so you gotta change that in this code (tried changing process_science_eclipse_para.sh, but it won't work)
#adam# normalize the science images
./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUP OCF #9
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi
./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_norm SUP "OCFN" 8 -32 #9
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi
#adam-del# #10_2#./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUP OFC #9
#adam-del# #10_2#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_norm SUP "OFCN" 8 -32 #9
#adam-DO# if there is another type of flat (which hasn't been processed yet), change which flat you're using and start over at #STARTOVER-OTHER FLAT CHOSEN
if [ -d ${SUBARUDIR}/${run}_${filter}/SKYFLAT ]; then
	if [ -d ${SUBARUDIR}/${run}_${filter}/DOMEFLAT ]; then
		mv ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm_${FLAT}
		echo "adam-look| mv ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm_${FLAT}"
		if [ ! -d ${SUBARUDIR}/${run}_${filter}/SCIENCE_${FLAT} ]; then
		    mv ${SUBARUDIR}/${run}_${filter}/SCIENCE ${SUBARUDIR}/${run}_${filter}/SCIENCE_${FLAT}
		    mkdir -p ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
		    cp -r ${SUBARUDIR}/${run}_${filter}/SCIENCE_${FLAT}/SPLIT_IMAGES/SUPA*.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/
		    cp -r ${SUBARUDIR}/${run}_${filter}/SCIENCE_${FLAT}/ORIGINALS/SUPA*.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS/
		    echo "adam-look| cp -r ${SUBARUDIR}/${run}_${filter}/SCIENCE/ ${SUBARUDIR}/${run}_${filter}/SCIENCE_${FLAT}/"
		fi
	fi
fi
#adam-DO check# choose which FLAT is better by comparing science images
#ds9 -zscale -geometry 2000x2000 ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm/BINNED/*mosOCFN.fits -zoom to fit &
echo "if there are two flats available and you still have to process the other one, then start over here"
echo "check: the normalized science images from which type of flat looks better?"




### adam-look | NOW ON TO THE DOMEFLAT!
export FLAT="DOMEFLAT"
#### processes SCIENCE frames:
#### overscan, bias, flat -->  SUPA*_${chip}OCF.fits
#adam# process the SCIENCE images result=(science-bias)/(flat-bias)
#makes (in undo form): rm SUPA*OCF.fits ; rm SUPA*OCF_sub.fits ; rm SCIENCE_*.fits ; mv SUB_IMAGES/SUPA*.fits . ; rm -r SUB_IMAGES/
#THIS TAKES ~15 min#
if [ "$config" == "10_3" ] ; then
	./parallel_manager.sh ./process_science_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE} #8
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
elif [ "$config" == "10_2" ] ; then
	./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE} #8
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
else
	echo "problem with config";exit 1
fi
#adam-del# #10_2 & 10_3# this is where process_science_4channels_eclipse_para.sh calls things OCF and process_science_eclipse_para.sh calls things OFC, so you gotta change that in this code (tried changing process_science_eclipse_para.sh, but it won't work)
#adam# normalize the science images
./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUP OCF #9
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi
./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_norm SUP "OCFN" 8 -32 #9
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi
#adam-del# #10_2#./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUP OFC #9
#adam-del# #10_2#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_norm SUP "OFCN" 8 -32 #9
#adam-DO# if there is another type of flat (which hasn't been processed yet), change which flat you're using and start over at #STARTOVER-OTHER FLAT CHOSEN
exit 0; #8-9
