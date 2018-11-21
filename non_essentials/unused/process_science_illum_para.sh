#!/bin/bash -xv

# 14.08.02:
#        the correction for the gains is not done in this script
#        anymore but in the first processing of the science frames.
#
# 30.05.04:
# tempaorary files go to a TEMPDIR directory 
#
# 01.07.2004:
# new RESCALE flag; it was introduced so that the user can decide
# whether the gain equalisation is done here with Superflats
# or in the process_science step with skyflats. 

# the script corrects a set of Science frames
# for illumination pattern. This is an effective
# second flat-fielding. Here, the maximum mode
# of all flats is taken as factor for the flatfielding
# to bring all the images to the same gain.

# $1: main directory (filter)
# $2: Science directory
# $3: RESCALE/NORESCALE
# $4: chips to be processed

# preliminary work:
. ${INSTRUMENT:?}.ini

for CHIP in $4
do
  RESULTDIR[${CHIP}]="$1/$2"
done

# first find out the modes of the flat images as factor
# for flat fielding

# create input file and config file on the fly for mode determination:

# We MUST use all ccds here since the chips should be brought to the 
# same gain!


k=1
while [ "${k}" -le "${NCHIPS}" ]
do
  ALLCHIPS="${ALLCHIPS} ${k}"
  k=$(( $k + 1 ))
done

${S_LISTEXT_PARA} $1/$2/$2 _illum.fits immode $$ "${ALLCHIPS}"

echo "INPUT"                       >  ${TEMPDIR}/immode.param_$$
echo "     name   ${TEMPDIR}/@in-immode_$$"   >> ${TEMPDIR}/immode.param_$$
echo "     dyn_min  -66000.0 "     >> ${TEMPDIR}/immode.param_$$
echo "     dyn_max  66000.0 "      >> ${TEMPDIR}/immode.param_$$
echo "end"                         >> ${TEMPDIR}/immode.param_$$
echo "RASTER"                      >> ${TEMPDIR}/immode.param_$$
echo "     xc    ${STATSALLIM[1]}" >> ${TEMPDIR}/immode.param_$$
echo "     yc    ${STATSALLIM[2]}" >> ${TEMPDIR}/immode.param_$$
echo "     sizex ${STATSALLIM[3]}" >> ${TEMPDIR}/immode.param_$$
echo "     sizey ${STATSALLIM[4]}" >> ${TEMPDIR}/immode.param_$$
echo "end"                         >> ${TEMPDIR}/immode.param_$$
echo "STAT"                        >> ${TEMPDIR}/immode.param_$$
echo "percent 40"                  >> ${TEMPDIR}/immode.param_$$
echo "end"                         >> ${TEMPDIR}/immode.param_$$
echo "END"                         >> ${TEMPDIR}/immode.param_$$

${P_IMMODE} ${TEMPDIR}/immode.param_$$ ${TEMPDIR}/immode.dat_$$ ${TEMPDIR}/immode-stat.dat_$$

# get the factors to normalise flats
FACT=`${P_GAWK} '($1!="->" && $1!="") {printf ("%f ", $2)}' ${TEMPDIR}/immode.dat_$$`
MAXFACT=`${P_GAWK} 'BEGIN {max=0} ($1!="->" && $1!="") {if($2>max) max=$2} END {print max}' ${TEMPDIR}/immode.dat_$$`

for CHIP in $4
do
  ACTUFACT=`echo ${FACT} | ${P_GAWK} '{print $'${CHIP}'}'`
  if [ "$3" = "RESCALE" ]; then
    ACTUFACT=${MAXFACT}
  fi
  echo "INPUT"                     >  ${TEMPDIR}/imred.param_$$
  echo "     name   ${TEMPDIR}/@in-imred_$$"  >> ${TEMPDIR}/imred.param_$$
  echo "end"                       >> ${TEMPDIR}/imred.param_$$
  echo "OUTPUT"                    >> ${TEMPDIR}/imred.param_$$
  echo "     name   ${TEMPDIR}/@out-imred_$$" >> ${TEMPDIR}/imred.param_$$
  echo "     outbitpix -32"        >> ${TEMPDIR}/imred.param_$$
  echo "end"                       >> ${TEMPDIR}/imred.param_$$
  echo "OVERSCAN"                  >> ${TEMPDIR}/imred.param_$$
  echo "     doover 0"             >> ${TEMPDIR}/imred.param_$$
  echo "end"                       >> ${TEMPDIR}/imred.param_$$
  echo "DARK"                      >> ${TEMPDIR}/imred.param_$$
  echo "     dodark 0"             >> ${TEMPDIR}/imred.param_$$
  echo "end"                       >> ${TEMPDIR}/imred.param_$$
  echo "FLAT"                      >> ${TEMPDIR}/imred.param_$$
  echo "     doflat 1"             >> ${TEMPDIR}/imred.param_$$
  echo "     fact ${ACTUFACT}"         >> ${TEMPDIR}/imred.param_$$
  echo "     subst 50.0"           >> ${TEMPDIR}/imred.param_$$
  echo "     name ${TEMPDIR}/@flat-imred_$$"  >> ${TEMPDIR}/imred.param_$$
  echo "end"                       >> ${TEMPDIR}/imred.param_$$
  echo "MASK"                      >> ${TEMPDIR}/imred.param_$$
  echo "     domask 0"             >> ${TEMPDIR}/imred.param_$$
  echo "end"                       >> ${TEMPDIR}/imred.param_$$
  echo "FRINGE"                    >> ${TEMPDIR}/imred.param_$$
  echo "     dofringe 0"           >> ${TEMPDIR}/imred.param_$$
  echo "end"                       >> ${TEMPDIR}/imred.param_$$
  echo "RASTER"                    >> ${TEMPDIR}/imred.param_$$
  echo "     cut 0"                >> ${TEMPDIR}/imred.param_$$
  echo "end"                       >> ${TEMPDIR}/imred.param_$$
  echo "END"                       >> ${TEMPDIR}/imred.param_$$
  
  if [ -f ${TEMPDIR}/@in-imred_$$ ]; then
    rm ${TEMPDIR}/@in-imred_$$
  fi
  if [ -f ${TEMPDIR}/@out-imred_$$ ]; then
    rm ${TEMPDIR}/@out-imred_$$
  fi
  if [ -f ${TEMPDIR}/@flat-imred_$$ ]; then
    rm ${TEMPDIR}/@flat-imred_$$
  fi

  ls $1/$2/$2_${CHIP}_illum.fits > ${TEMPDIR}/@flat-imred_$$

  FILES=`ls $1/$2/*_${CHIP}OFC.fits`

  for FILE in ${FILES}
  do
    if [ -L ${FILE} ]; then
	 LINK=`${P_READLINK} ${FILE}`
	 echo ${LINK} >> ${TEMPDIR}/@in-imred_$$ 
	 BASE=`basename ${LINK} .fits`
	 DIR=`dirname ${LINK}`
	 ln -s ${DIR}/${BASE}S.fits $1/$2/${BASE}S.fits
	 RESULTDIR[${CHIP}]=`dirname ${LINK}`    
    else
	 echo "${FILE}" >> ${TEMPDIR}/@in-imred_$$
    fi
  done 

  ${S_LIO} ${TEMPDIR}/@in-imred_$$ ${TEMPDIR}/@out-imred_$$ .fits S
  ${P_IMRED} ${TEMPDIR}/imred.param_$$

  if [ ! -d /$1/$2/OFC_IMAGES ]; then
     mkdir /$1/$2/OFC_IMAGES
  fi 
  mv /$1/$2/*_${CHIP}OFC.fits /$1/$2/OFC_IMAGES
done






