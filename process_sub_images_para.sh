#!/bin/bash
set -xv
#adam-example# ./process_sub_images_para.sh /u/ki/awright/data/2015-12-15_W-C-RC SCIENCE_SKYFLAT_SET8 NOFRINGE ' 1 '
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start

###############
# $Id: process_sub_images_para.sh,v 1.6 2009-06-02 01:27:50 anja Exp $
###############
# adam: changed to something that subtracts objects from OCF images (used to do flatfielding also)
###############
# Takes OCF science images, and creates object subtracted images
###############

#$1 Run directory
#$2 SCIENCE directory
#$3 FRINGE/NOFRINGE
#$4 CHIPS
run_dir=$1 #Run directory
science_dir=$2 #SCIENCE directory
fringe_bool=$3 #FRINGE/NOFRINGE
chip_nums=$4 #CHIPS
echo "run_dir=" $run_dir
echo "science_dir=" $science_dir
echo "fringe_bool=" $fringe_bool
echo "chip_nums=" $chip_nums



# preliminary work:
. ${INSTRUMENT:?}.ini > /tmp/subaru.out 2>&1

for CHIP in $chip_nums
do

    if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then

	MAXX=$(( ${CUTX[${CHIP}]} + ${SIZEX[${CHIP}]} - 1 ))
	MAXY=$(( ${CUTY[${CHIP}]} + ${SIZEY[${CHIP}]} - 1 ))

	if [ $? -gt 0 ]; then
	    #adam-BL# log_status 1 "Preprocess Failed. Chip $CHIP"
	    echo "adam-look | error: Preprocess Failed. Chip $CHIP"
	    exit 1
	fi

	ls -1 ${run_dir}/${science_dir}/*_${CHIP}OCF.fits > images-objects_$$

	cat images-objects_$$ |\
        {
	    while read file
	    do
  		BASE=`basename ${file} .fits`
		#
		# now run sextractor to subtract objects from the image
		#
		if [ "${fringe_bool}" = "FRINGE" ]; then
  		    ${P_SEX} ${file} -c ${DATACONF}/image-objects.sex\
			  -CHECKIMAGE_NAME ${run_dir}/${science_dir}/${BASE}"_sub.fits"\
			  -DETECT_MINAREA 7 -DETECT_THRESH 5 -ANALYSIS_THRESH 5
  		else
  		    ${P_SEX} ${file} -c ${DATACONF}/image-objects.sex\
			-DETECT_THRESH 0.7 -DETECT_MINAREA 5 -BACK_SIZE 1024 \
			  -CHECKIMAGE_NAME ${run_dir}/${science_dir}/${BASE}"_sub.fits"
  		fi

		#adam-SHNT# could set shadow to -70000 here (easier, see the shadow mask stuff in diffmask/)
		# OR
		# maybe it's better to just go to some version of the illum.fits and set this region=1 (harder)

		fixfile=${run_dir}/${science_dir}/${BASE}_sub_sf.fits
  		#adam-SET8#		#fixfile_4modecalc=${run_dir}/${science_dir}/${BASE}_sub_sf_4modecalc.fits
  		${P_IC} '%1 %2 *' ${run_dir}/SCIENCE/diffmask/${BASE}.sf.fits ${run_dir}/${science_dir}/${BASE}"_sub.fits"  > ${fixfile}
  		#adam-SET8# ${P_IC} '%1 %2 *' ${fixfile} ~/data/RADIAL_MASKS/SUBARU_10_3/RadialMask_10_3_${CHIP}.fits > ${fixfile_4modecalc}

		#adam# if {|%2|>1.0e-06} then{%1} else{-70000}
		#basically it's the object subtracted image with pixels on objects set to -70000
  		${P_IC} '%1 -70000 %2 fabs 1.0e-06 > ?' ${file} ${fixfile} \
  		    > ${run_dir}/${science_dir}/${BASE}"_sub1.fits"
		mv ${run_dir}/${science_dir}/${BASE}"_sub1.fits" ${run_dir}/${science_dir}/${BASE}"_sub.fits"

  		#adam-SET8#  		#${P_IC} '%1 -70000 %2 fabs 1.0e-06 > ?' ${file} ${fixfile_4modecalc} \
  		#adam-SET8#  		#    > ${run_dir}/${science_dir}/${BASE}"_sub_4modecalc.fits"
  		#adam-SET8#  		#rm -f ${fixfile_4modecalc} ${fixfile}
	    done
	}

	rm -f images-objects_$$
    fi
done

#adam-BL# log_status $?
