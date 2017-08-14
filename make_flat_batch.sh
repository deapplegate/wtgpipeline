#!/bin/bash -xv
#######################
. BonnLogger.sh
. log_start

#$1: workdir 
#$2: input prefix name
#$3: reject numbers
#$4: chips to work on

# preliminary work:
. ${INSTRUMENT:?}.ini


#
# the resultdir is where the output coadded images
# will go. If ONE image of the corresponding chip
# is a link the image will go to THIS directory
for CHIP in $4
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    RESULTDIR="${1}/${2}"
    if [ ! -d $RESULTDIR ]; then
	mkdir $RESULTDIR
    fi
  else
    echo "Chip ${CHIP} will not be processed in $0"  
  fi

  if [ -e ${RESULTDIR}/${2}_${CHIP}.fits ]; then
      continue
  fi

  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then

        # check whether the result (a FITS image with the
    # proper name) is already there; if yes, do nothing !!
    if [ -f ${RESULTDIR}/${2}_${CHIP}.fits ]; then
        echo "${RESULTDIR}/${2}_${CHIP}.fits already present !!! Skipping !!"
	continue
    fi
    
    awk -v ofs=' ' '{print $1}' $1/$2_${CHIP}.list > input_list_$$

    # and combine them
    ${P_IMSTATS} `cat input_list_$$`\
                 -s ${STATSXMIN} ${STATSXMAX} ${STATSYMIN} ${STATSYMAX}\
                 -o flat_images_$$
    ${P_IMCOMBFLAT_IMCAT} -i  flat_images_$$\
                    -o ${RESULTDIR}/${2}_${CHIP}.fits \
                    -s 1 -e $3

    rm flat_images_$$ input_list_$$
  fi
done

#FILES=""
#for CHIP in $4
#do
#    FILES="${FILES} `ls ${RESULTDIR}/${2}_${CHIP}.fits`"
#done
#
#${P_IMSTATS} ${FILES} -s \
#    ${STATSXMIN} ${STATSXMAX} ${STATSYMIN} ${STATSYMAX} -o \
#    immode.dat_$$
#
#MODES=`${P_GAWK} '($1!="#") {printf ("%f ", $2)}' immode.dat_$$`
#
#i=1
#for CHIP in $3
#do
#    ACTUMODE=`echo ${MODES} | ${P_GAWK} '{print $'${i}'}'`
#
#    if [ -f ${RESULTDIR}/${2}_norm_${CHIP}.fits ]; then
#        echo "${RESULTDIR}/${2}__norm_${CHIP}.fits already present !!! Skipping !!"
#	continue
#    fi 
#    
#    ${P_IC} '%1 '${ACTUMODE}' / ' ${RESULTDIR}/$2_${CHIP}.fits > \
#        ${RESULTDIR}/$2_norm_${CHIP}.fits
#    
#    i=$(( $i + 1 ))
#done
#
#
#rm immode.dat_$$

log_status $?
