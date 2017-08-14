#!/bin/bash -xv
#adam-does# this script makes the SUPA*_diff.fits images that are used to correct for crosstalk
#adam-use# use this to make ctcorr images. Has four possible modes. Must use all in succession:
#1# O (overscan correct IM -> IM_O) # the script processes a set of Science frames to make images that are overscan corrected, debiased, BUT not flatfielded or cut
#2# X (ctcorr IM_O -> IM_OX)
#3# C (cut IM_OX -> IM_OXC & cut IM_O -> IM_OC)
#4# F ( IM_OXC -> IM_OXCF & IM_OC -> IM_OCF & IM_OCF-IM_OXCF -> diff )
#adam-example# ./parallel_manager.sh adam_CTcorr_make_images_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE " O X C F"
#	./parallel_manager.sh adam_CTcorr_make_images_para.sh /nfs/slac/g/ki/ki18/anja/SUBARU/2010-02-12_W-C-RC BIAS DOMEFLAT SCIENCE " O X C F"

#$1: main directory (filter)
#$2: Bias directory
#$3: Flat directory
#$4: Science directory
#$5: modes to run (of O X C F)
#$6: chips to be processed
main_dir=$1
Bias_dir=$2
Flat_dir=$3
Science_dir=$4
modes=$5
chips=$6

right_clips_x2=([1]=568 [2]=568 [3]=568 [4]=568 [5]=568 [6]=568 [7]=568 [8]=568 [9]=568 [10]=568 \ 
	[11]=1137 [12]=1137 [13]=1137 [14]=1137 [15]=1137 [16]=1137 [17]=1137 [18]=1137 [19]=1137 [20]=1137 \ 
	[21]=1704 [22]=1704 [23]=1704 [24]=1704 [25]=1704 [26]=1704 [27]=1704 [28]=1704 [29]=1704 [30]=1704 \ 
	[31]=2272 [32]=2272 [33]=2272 [34]=2272 [35]=2272 [36]=2272 [37]=2272 [38]=2272 [39]=2272 [40]=2272 )
right_clips_x1=([1]=521 [2]=521 [3]=521 [4]=521 [5]=521 [6]=521 [7]=521 [8]=521 [9]=521 [10]=521 \ 
	[11]=1129 [12]=1129 [13]=1129 [14]=1129 [15]=1129 [16]=1129 [17]=1129 [18]=1129 [19]=1129 [20]=1129 \ 
	[21]=1657 [22]=1657 [23]=1657 [24]=1657 [25]=1657 [26]=1657 [27]=1657 [28]=1657 [29]=1657 [30]=1657 \ 
	[31]=2249 [32]=2249 [33]=2249 [34]=2249 [35]=2249 [36]=2249 [37]=2249 [38]=2249 [39]=2249 [40]=2249 )
left_clips_x2=([1]=24 [2]=24 [3]=24 [4]=24 [5]=24 [6]=24 [7]=24 [8]=24 [9]=24 [10]=24 \ 
	[11]=616 [12]=616 [13]=616 [14]=616 [15]=616 [16]=616 [17]=616 [18]=616 [19]=616 [20]=616 \ 
	[21]=1144 [22]=1144 [23]=1144 [24]=1144 [25]=1144 [26]=1144 [27]=1144 [28]=1144 [29]=1144 [30]=1144 \ 
	[31]=1752 [32]=1752 [33]=1752 [34]=1752 [35]=1752 [36]=1752 [37]=1752 [38]=1752 [39]=1752 [40]=1752 )
left_clips_x1=([1]=1 [2]=1 [3]=1 [4]=1 [5]=1 [6]=1 [7]=1 [8]=1 [9]=1 [10]=1 \ 
	[11]=569 [12]=569 [13]=569 [14]=569 [15]=569 [16]=569 [17]=569 [18]=569 [19]=569 [20]=569 \ 
	[21]=1138 [22]=1138 [23]=1138 [24]=1138 [25]=1138 [26]=1138 [27]=1138 [28]=1138 [29]=1138 [30]=1138 \ 
	[31]=1705 [32]=1705 [33]=1705 [34]=1705 [35]=1705 [36]=1705 [37]=1705 [38]=1705 [39]=1705 [40]=1705 )

# setup which modes I'm going to cover
mode_O=0         
mode_X=0         
mode_C=0         
mode_F=0         

for mode in ${modes}
do
	if [ ${mode} = "O" ]; then
		mode_O=1
	elif [ ${mode} = "X" ]; then
		mode_X=1
	elif [ ${mode} = "C" ]; then
		mode_C=1
	elif [ ${mode} = "F" ]; then
		mode_F=1
	else
		echo "this mode = ${mode} is invalid, it must be one of these: O X C F"
		exit 1
	fi
done

echo "modes = "${modes}
echo ${mode_O}, ${mode_X}, ${mode_C}, ${mode_F}

# preliminary work:
. ${INSTRUMENT:?}.ini
# the resultdir is where the output coadded images
# will go. If ONE image of the corresponding chip
# is a link the image will go to THIS directory
for CHIP in ${chips}
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    RESULTDIR[${CHIP}]="${main_dir}/${Science_dir}"
  else
    echo "Chip ${CHIP} will not be processed in $0"  
  fi
done

# perform preprocessing (overscan correction, BIAS subtraction, first flatfield pass)
if [ ${mode_O} -eq 1 ]; then
  for CHIP in ${chips}
  do
    if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
      FILES=`ls ${main_dir}/${Science_dir}/SPLIT_IMAGES/SUPA*_${CHIP}.fits`
    
      for FILE in ${FILES}
      do
        if [ -L ${FILE} ]; then
  	     LINK=`${P_READLINK} ${FILE}`
  	     BASE=`basename ${LINK} .fits`
  	     DIR=`dirname ${LINK}`
  	     ln -s ${DIR}/${BASE}OFC.fits ${main_dir}/${Science_dir}/${BASE}OFC.fits
  	     RESULTDIR[${CHIP}]=`dirname ${LINK}`    
        fi
      done 
    
      # overscan correct and bias subtract 
      # science images:

      CHANNEL=1
      while [ "${CHANNEL}" -le "${NCHANNELS}" ]
      do

        NCHIP=$(( ${NCHIPS}*( ${CHANNEL} -1 ) + ${CHIP}))

        MAXX=$(( ${CUTX[${NCHIP}]} + ${SIZEX[${NCHIP}]} - 1 ))
        MAXY=$(( ${CUTY[${CHIP}]} + ${SIZEY[${CHIP}]} - 1 ))
    
      # overscan correct and trim frames
        ${P_IMRED_ECL:?} ${FILES} \
  	  -MAXIMAGES ${NFRAMES}\
  	  -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
  	  -OVERSCAN Y \
  	  -OVERSCAN_REGION ${OVSCANX1[${NCHIP}]},${OVSCANX2[${NCHIP}]} \
  	  -OUTPUT Y \
  	  -OUTPUT_DIR /${main_dir}/${Science_dir}/ \
  	  -TRIM Y \
  	  -TRIM_REGION ${left_clips_x1[${NCHIP}]},${left_clips_x2[${NCHIP}]},1,4273 \
  	  -OUTPUT_SUFFIX O_CH${CHANNEL}_0.fits
        ${P_IMRED_ECL:?} ${FILES} \
  	  -MAXIMAGES ${NFRAMES}\
  	  -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
  	  -OVERSCAN Y \
  	  -OVERSCAN_REGION ${OVSCANX1[${NCHIP}]},${OVSCANX2[${NCHIP}]} \
  	  -OUTPUT Y \
  	  -OUTPUT_DIR /${main_dir}/${Science_dir}/ \
  	  -TRIM Y \
  	  -TRIM_REGION ${CUTX[${NCHIP}]},${MAXX},1,4273 \
  	  -OUTPUT_SUFFIX O_CH${CHANNEL}_1.fits
        ${P_IMRED_ECL:?} ${FILES} \
  	  -MAXIMAGES ${NFRAMES}\
  	  -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
  	  -OVERSCAN Y \
  	  -OVERSCAN_REGION ${OVSCANX1[${NCHIP}]},${OVSCANX2[${NCHIP}]} \
  	  -OUTPUT Y \
  	  -OUTPUT_DIR /${main_dir}/${Science_dir}/ \
  	  -TRIM Y \
  	  -TRIM_REGION ${right_clips_x1[${NCHIP}]},${right_clips_x2[${NCHIP}]},1,4273 \
  	  -OUTPUT_SUFFIX O_CH${CHANNEL}_2.fits
  	  #-BIAS Y \
  	  #-BIAS_IMAGE /${main_dir}/${Bias_dir}/${Bias_dir}_${CHIP}.fits \
    
      CHANNEL=$(( ${CHANNEL} + 1 ))
      done

      #---> paste four fits files
      for file in ${FILES}; do
  	basename=`basename $file .fits`
  	./horizontal_paste.py -o ${1}/${4}/${basename}O_CHall.fits `ls ${1}/${4}/${basename}O_CH?_[0-2].fits`
      done

      ${P_RENAME} 's/O_CHall/O/g' /${main_dir}/${Science_dir}/*_${CHIP}O_CHall.fits

      rm /${main_dir}/${Science_dir}/*_${CHIP}O_CH?_[0-2].fits
    
    fi

    if [ ! -d /${main_dir}/${Science_dir}/IM_O ]; then
        mkdir /${main_dir}/${Science_dir}/IM_O
    fi
    mv /${main_dir}/${Science_dir}/*_${CHIP}O.fits /${main_dir}/${Science_dir}/IM_O
  done
fi
########${P_IMRED_ECL:?} numbers.fits \
########  -OUTPUT Y \
########  -OVERSCAN N \
########  -BIAS N \
########  -FLAT N \
########  -TRIM Y \
########  -TRIM_REGION ${left_clips_x1[${NCHIP}]},${left_clips_x2[${NCHIP}]},1,4273 \
########  -OUTPUT_SUFFIX O_CH${CHANNEL}_0.fits
########echo "${P_IMRED_ECL:?} numbers.fits \
########  -OUTPUT Y \
########  -OVERSCAN N \
########  -BIAS N \
########  -FLAT N \
########  -TRIM Y \
########  -TRIM_REGION ${left_clips_x1[${NCHIP}]},${left_clips_x2[${NCHIP}]},1,4273 \
########  -OUTPUT_SUFFIX O_CH${CHANNEL}_0.fits"
########${P_IMRED_ECL:?} numbers.fits \
########  -OUTPUT Y \
########  -OVERSCAN N \
########  -BIAS N \
########  -FLAT N \
########  -TRIM Y \
########  -TRIM_REGION ${CUTX[${NCHIP}]},${MAXX},1,4273 \
########  -OUTPUT_SUFFIX O_CH${CHANNEL}_1.fits
########echo "${P_IMRED_ECL:?} numbers.fits \
########  -OUTPUT Y \
########  -OVERSCAN N \
########  -BIAS N \
########  -FLAT N \
########  -TRIM Y \
########  -TRIM_REGION ${CUTX[${NCHIP}]},${MAXX},1,4273 \
########  -OUTPUT_SUFFIX O_CH${CHANNEL}_1.fits"
########${P_IMRED_ECL:?} numbers.fits \
########  -OUTPUT Y \
########  -OVERSCAN N \
########  -BIAS N \
########  -FLAT N \
########  -TRIM Y \
########  -TRIM_REGION ${right_clips_x1[${NCHIP}]},${right_clips_x2[${NCHIP}]},1,4273 \
########  -OUTPUT_SUFFIX O_CH${CHANNEL}_2.fits
########echo "${P_IMRED_ECL:?} numbers.fits \
########  -OUTPUT Y \
########  -OVERSCAN N \
########  -BIAS N \
########  -FLAT N \
########  -TRIM Y \
########  -TRIM_REGION ${right_clips_x1[${NCHIP}]},${right_clips_x2[${NCHIP}]},1,4273 \
########  -OUTPUT_SUFFIX O_CH${CHANNEL}_2.fits"

### Run the ctcorr (Cross-X-you get it)
if [ ${mode_X} -eq 1 ]; then
  if [ ! -d /${main_dir}/${Science_dir}/IM_OX ]; then
      mkdir /${main_dir}/${Science_dir}/IM_OX
  fi
  for CHIP in ${chips}
  do
	  for file in `\ls -1 /${main_dir}/${Science_dir}/IM_O/*_${CHIP}O.fits`
	  do
	    OX_basename=`basename ${file} O.fits`
	    unsplit_basename=`basename ${file} _${CHIP}O.fits`
	    /u/ki/awright/InstallingSoftware/pythons/header_key_add.py ${file} DATE-OBS=`dfits -x 1 /${main_dir}/${Science_dir}/ORIGINALS/${unsplit_basename}.fits| fitsort DATE-OBS | tail -n 1 | awk '{print $2}'`
	    OX_filename=/${main_dir}/${Science_dir}/IM_OX/${OX_basename}OX.fits
	    ctcorr6b1 -notrim -noos ${file} ${OX_filename}
	  done
  done
fi

### Cut the images!
if [ ${mode_C} -eq 1 ]; then

  if [ ! -d /${main_dir}/${Science_dir}/IM_OC_and_OXC ]; then
      mkdir /${main_dir}/${Science_dir}/IM_OC_and_OXC
  fi

  for CHIP in ${chips}
  do
    if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
      FILES=`\ls ${main_dir}/${Science_dir}/IM_OX/*_${CHIP}OX.fits ${main_dir}/${Science_dir}/IM_O/*_${CHIP}O.fits`
      # overscan correct, bias subtract and flatfield
      # science images:

      CHANNEL=1
      while [ "${CHANNEL}" -le "${NCHANNELS}" ]
      do

        NCHIP=$(( ${NCHIPS}*( ${CHANNEL} -1 ) + ${CHIP}))
        MAXX=$(( ${CUTX[${NCHIP}]} + ${SIZEX[${NCHIP}]} - 1 ))
        MAXY=$(( ${CUTY[${CHIP}]} + ${SIZEY[${CHIP}]} - 1 ))

        # trim frames
        ${P_IMRED_ECL:?} ${FILES} \
  	  -MAXIMAGES $((NFRAMES*2))\
  	  -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
  	  -OVERSCAN N \
          -BIAS N \
          -FLAT N \
  	  -COMBINE N \
  	  -TRIM Y \
  	  -TRIM_REGION ${CUTX[${NCHIP}]},${MAXX},${CUTY[${CHIP}]},${MAXY} \
  	  -OUTPUT Y \
  	  -OUTPUT_DIR /${main_dir}/${Science_dir}/ \
  	  -OUTPUT_SUFFIX C_CH${CHANNEL}.fits
          #-OUTPUT_SUFFIX OCF.fits \
          #-FLAT Y \
          #-FLAT_IMAGE /${main_dir}/${Flat_dir}/${Flat_dir}_${CHIP}.fits \
          #-BIAS Y \
          #-BIAS_IMAGE /${main_dir}/${Bias_dir}/${Bias_dir}_${CHIP}.fits \
          #${FLATFLAG}
    
      CHANNEL=$(( ${CHANNEL} + 1 ))
      done

      #---> paste four fits files
      for file in ${FILES}; do
  	basename=`basename $file .fits`
  	./horizontal_paste.py -o /${main_dir}/${Science_dir}/IM_OC_and_OXC/${basename}C.fits `ls ${1}/${4}/${basename}C_CH?.fits`
      done

      rm /${main_dir}/${Science_dir}/*_${CHIP}OXC_CH?.fits
      rm /${main_dir}/${Science_dir}/*_${CHIP}OC_CH?.fits

    fi
    #mv /${main_dir}/${Science_dir}/*_${CHIP}.fits /${main_dir}/${Science_dir}/IM_OC_and_OXC
  done
fi

# Flat-field and Bias Correct the images, then make the difference images!
if [ ${mode_F} -eq 1 ]; then

  if [ ! -d /${main_dir}/${Science_dir}/IM_diff ]; then
      mkdir /${main_dir}/${Science_dir}/IM_diff
  fi

  for CHIP in ${chips}
  do
    if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
      FILES=`ls ${main_dir}/${Science_dir}/IM_OC_and_OXC/*_${CHIP}O*C.fits`
    
      # build up list of all flatfields necessary for rescaling
      # when gains between chips are equalised here.
      i=1
      j=1
      FLATSTR=""
      while [ "${i}" -le "${NCHIPS}" ]
      do
        if [ ${NOTUSE[${i}]:=0} -eq 0 ] && [ ${NOTPROCESS[${i}]:=0} -eq 0 ]; then
  	if [ "${j}" = "1" ]; then
  	  FLATSTR="/${main_dir}/${Flat_dir}/${Flat_dir}_${i}.fits"
  	  j=2
  	else
  	  FLATSTR="${FLATSTR},/${main_dir}/${Flat_dir}/${Flat_dir}_${i}.fits"
  	fi
        fi    
        i=$(( $i + 1 ))
      done
    
      FLATFLAG=""
      if [ "$5" = "RESCALE" ]; then   
        FLATFLAG="-FLAT_SCALE Y -FLAT_SCALEIMAGE ${FLATSTR}" 
      fi
    
      # science images:
      # bias subtraction and flat-fielding
      ${P_IMRED_ECL:?} ${FILES} \
  	-MAXIMAGES ${NFRAMES} \
  	-STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
  	-OVERSCAN N \
  	-TRIM N \
  	-COMBINE N \
  	-BIAS Y \
  	-BIAS_IMAGE /${main_dir}/${Bias_dir}/${Bias_dir}_${CHIP}.fits \
  	-OUTPUT Y \
  	-OUTPUT_DIR /${main_dir}/${Science_dir}/IM_diff \
  	-OUTPUT_SUFFIX F.fits \
  	-FLAT Y \
  	-FLAT_IMAGE /${main_dir}/${Flat_dir}/${Flat_dir}_${CHIP}.fits \
  	${FLATFLAG}

    FILES=`\ls ${main_dir}/${Science_dir}/IM_diff/*_${CHIP}OXCF.fits`
    for file in ${FILES}; do
  	basename=`basename $file OXCF.fits`
  	ic "%1 %2 -"  ${main_dir}/${Science_dir}/IM_diff/${basename}OCF.fits ${file} > ${main_dir}/${Science_dir}/IM_diff/${basename}_diff.fits
    done
    fi

  done
fi

