#!/bin/bash -xv

# the script corrects a set of Science frames
# for fringe pattern. 
#
# 30.05.04:
# tempaorary files go to a TEMPDIR directory 

# $1: main directory (filter)
# $2: science directory
# $3: chips to be processed

# preliminary work:
. ${INSTRUMENT:?}.ini

for CHIP in $3
do
  RESULTDIR[${CHIP}]="$1/$2"
done

for CHIP in $3
do
  echo "INPUT"                      >  ${TEMPDIR}/imred.param_$$
  echo "     name   ${TEMPDIR}/@in-imred_$$"   >> ${TEMPDIR}/imred.param_$$
  echo "end"                        >> ${TEMPDIR}/imred.param_$$
  echo "OUTPUT"                     >> ${TEMPDIR}/imred.param_$$
  echo "     name   ${TEMPDIR}/@out-imred_$$"  >> ${TEMPDIR}/imred.param_$$
  echo "     outbitpix -32"         >> ${TEMPDIR}/imred.param_$$
  echo "end"                        >> ${TEMPDIR}/imred.param_$$
  echo "OVERSCAN"                   >> ${TEMPDIR}/imred.param_$$
  echo "     doover 0"              >> ${TEMPDIR}/imred.param_$$
  echo "end"                        >> ${TEMPDIR}/imred.param_$$
  echo "DARK"                       >> ${TEMPDIR}/imred.param_$$
  echo "     dodark 0"              >> ${TEMPDIR}/imred.param_$$
  echo "end"                        >> ${TEMPDIR}/imred.param_$$
  echo "FLAT"                       >> ${TEMPDIR}/imred.param_$$
  echo "     doflat 0"              >> ${TEMPDIR}/imred.param_$$
  echo "end"                        >> ${TEMPDIR}/imred.param_$$
  echo "MASK"                       >> ${TEMPDIR}/imred.param_$$
  echo "     domask 0"              >> ${TEMPDIR}/imred.param_$$
  echo "end"                        >> ${TEMPDIR}/imred.param_$$
  echo "FRINGE"                     >> ${TEMPDIR}/imred.param_$$
  echo "     dofringe 1"            >> ${TEMPDIR}/imred.param_$$
  echo "     name ${TEMPDIR}/@fringe-imred_$$" >> ${TEMPDIR}/imred.param_$$
  echo "end"                        >> ${TEMPDIR}/imred.param_$$
  echo "RASTER"                     >> ${TEMPDIR}/imred.param_$$
  echo "     cut 0"                 >> ${TEMPDIR}/imred.param_$$
  echo "end"                        >> ${TEMPDIR}/imred.param_$$
  echo "END"                        >> ${TEMPDIR}/imred.param_$$

  if [ -f ${TEMPDIR}/@fringe-imred_$$ ]; then
    rm ${TEMPDIR}/@fringe-imred_$$
  fi
  if [ -f ${TEMPDIR}/@in-imred_$$ ]; then
    rm ${TEMPDIR}/@in-imred_$$
  fi

  FILES=`ls $1/$2/*_${CHIP}OFCS.fits`

  for FILE in ${FILES}
  do
    if [ -L ${FILE} ]; then
	 LINK=`${P_READLINK} ${FILE}`
	 echo ${LINK} >> ${TEMPDIR}/@in-imred_$$ 
	 BASE=`basename ${LINK} .fits`
	 DIR=`dirname ${LINK}`
	 ln -s ${DIR}/${BASE}F.fits $1/$2/${BASE}F.fits
	 RESULTDIR[${CHIP}]=`dirname ${LINK}`    
    else
	 echo "${FILE}" >> ${TEMPDIR}/@in-imred_$$
    fi
  done 

  cat ${TEMPDIR}/fringevalues_${CHIP} |\
  {
    while read file fact
    do
      echo "${RESULTDIR[${CHIP}]}/$2_${CHIP}_fringe.fits ${fact}" >> ${TEMPDIR}/@fringe-imred_$$
    done
  }  
  
  ${S_LIO} ${TEMPDIR}/@in-imred_$$ ${TEMPDIR}/@out-imred_$$ .fits F
  ${P_IMRED} ${TEMPDIR}/imred.param_$$

  if [ ! -d /$1/$2/OFCS_IMAGES ]; then
     mkdir /$1/$2/OFCS_IMAGES
  fi
  mv /$1/$2/*_${CHIP}OFCS.fits /$1/$2/OFCS_IMAGES

done




