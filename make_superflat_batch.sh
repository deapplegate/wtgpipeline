#!/bin/bash -xv
. BonnLogger.sh
. log_start
#$1 FLAT Directory
#$2 FLAT prefix
#$3 SCIENCE directory
#$4 CHIPS



# preliminary work:
. ${INSTRUMENT:?}.ini



for CHIP in $4
do

    workdir=/scratch/flated_${CHIP}_$$

    mkdir $workdir
    
    
    MAXX=$(( ${CUTX[${CHIP}]} + ${SIZEX[${CHIP}]} - 1 ))
    MAXY=$(( ${CUTY[${CHIP}]} + ${SIZEY[${CHIP}]} - 1 ))

        # build up list of all flatfields necessary for rescaling
    # when gains between chips are equalised here.
    i=1
    j=1
    FLATSTR=""
    while [ "${i}" -le "${NCHIPS}" ]
    do
      if [ ${NOTUSE[${i}]:=0} -eq 0 ] && [ ${NOTPROCESS[${i}]:=0} -eq 0 ]; then
        if [ "${j}" = "1" ]; then
          FLATSTR="$1/${2}_${i}.fits"
	  j=2
        else
          FLATSTR="${FLATSTR},$1/${2}_${i}.fits"
        fi
      fi    
      i=$(( $i + 1 ))
    done
     
    FLATFLAG="-FLAT_SCALE Y -FLAT_SCALEIMAGE ${FLATSTR}" 

        # flatfield
    # science images:
    ${P_IMRED_ECL:?} `ls $3/SUPA*_${CHIP}OC.fits` \
	-MAXIMAGES ${NFRAMES} \
	-STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
	-OVERSCAN N \
	-BIAS N \
	-FLAT Y \
	-FLAT_IMAGE $1/${2}_${CHIP}.fits \
	-COMBINE N \
	-OUTPUT Y \
	-OUTPUT_DIR $workdir \
	-OUTPUT_SUFFIX F.fits \
	-TRIM N ${FLATFLAG}
    
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    ls -1 $workdir/*_${CHIP}OCF.fits > images-objects_$$
    
    cat images-objects_$$ |\
    {
      while read file
      do
  	BASE=`basename ${file} .fits`
  	#
  	# now run sextractor to subtract objects from the image
  	#
  	${P_SEX} ${file} -c ${DATACONF}/image-objects.sex\
  		  -CHECKIMAGE_NAME $workdir/${BASE}"_sub.fits"
  	
  	${P_IC} '%1 -70000 %2 fabs 1.0e-06 > ?' ${file} $workdir/${BASE}"_sub.fits"\
  		> $workdir/${BASE}"_sub1.fits"
  
  
      done
    }
  fi
done

for CHIP in $4
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    # do statistics from all science frames.
    # This is necessary to get the mode
    # of the combination from all images, so that
    # the combination where images have been excluded
    # can be scaled accordingly.
    ${P_IMSTATS} `ls $workdir/*_${CHIP}OCF_sub1.fits`\
                 -o science_images_$$

    RESULTMODE=`${P_GAWK} 'BEGIN {mean=0.0; n=0} ($1!="#") {
                           n=n+1; mean=mean+$2} END {print mean/n}' science_images_$$`

    # modify the input list of images
    # in case we have to reject files for the superflat:
    if [ -s $3/superflat_exclusion ]; then
	echo "Reading Superflat_Exclusion"
      ${P_GAWK} 'BEGIN {nex = 0; while (getline <"'$3'/superflat_exclusion" > 0) {
                 gsub(" ", "", $1); if (length($1) >0) {ex[nex]=$1; nex++; }}}
                 {exclude = 0; i=0;
                  while (i<nex) {
                    if ((ind=index($1, ex[i]))!=0) {
                      tmp=$1;
                      gsub(ex[i],"",tmp);
                      first=substr(tmp,ind,1);
                      if (first !~ /[0-9]/) {
                        exclude = 1;
                      }
                    }
  	          i++;
                  }
                  if(exclude == 0) {print $0}}' science_images_$$ > science_coadd_images_$$
    else
      cp science_images_$$ science_coadd_images_$$
    fi

  
  
    # do the combination
  
    ${P_IMCOMBFLAT_IMCAT} -i science_coadd_images_$$\
                    -o $1/SCIENCE_${CHIP}.fits \
                    -s 1 -e 0 1 -m ${RESULTMODE}

    rm -rf $workdir

    rm science_images_$$ science_coadd_images_$$ images-objects_$$
  fi
done



log_status $?
