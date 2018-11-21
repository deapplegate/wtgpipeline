#!/bin/bash -xv

# the script processes a set of Science frames
# the images are overscan corrected, debiased, flatfielded 
# and stacked with
# mode rescaling (Superflat). We assume that we do NOT work
# with a normaliced flat
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 
 
# $1: main directory (filter)
# $2: Science directory
# $3: chips to be processed

# preliminary work:
. ${INSTRUMENT:?}.ini

for CHIP in $3
do
  RESULTDIR[${CHIP}]="$1/$2"
done

# first find out the modes of the flat images as factor
# for flat fielding

# create input file and config file on the fly for mode determination:
${S_LISTEXT_PARA} $1/$2/$2 .fits immode $$ "$3"

echo "INPUT"                       >  ${TEMPDIR}/immode.param_$$
echo "     name ${TEMPDIR}/@in-immode_$$"   >> ${TEMPDIR}/immode.param_$$
echo "     dyn_min  -66000.0     " >> ${TEMPDIR}/immode.param_$$
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

i=1
for CHIP in $3
do
  if [ -f ${TEMPDIR}/@in-imred_$$ ]; then
     rm ${TEMPDIR}/@in-imred_$$
  fi
  if [ -f ${TEMPDIR}/@out-imred_$$ ]; then
    rm ${TEMPDIR}/@out-imred_$$
  fi
  if [ -f ${TEMPDIR}/@flat-imred_$$ ]; then
    rm ${TEMPDIR}/@flat-imred_$$
  fi

  ACTUFACT=`echo ${FACT} | ${P_GAWK} '{print $'${i}'}'`
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
  echo "     file 0"               >> ${TEMPDIR}/imred.param_$$
  echo "end"                       >> ${TEMPDIR}/imred.param_$$
  echo "FLAT"                      >> ${TEMPDIR}/imred.param_$$
  echo "     doflat 1"             >> ${TEMPDIR}/imred.param_$$
  echo "     fact ${ACTUFACT}"     >> ${TEMPDIR}/imred.param_$$
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

  ls $1/$2/$2_${CHIP}.fits > ${TEMPDIR}/@flat-imred_$$

  FILES=`ls $1/$2/*_${CHIP}OFCSF.fits`

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
  
  ${S_LIO} ${TEMPDIR}/@in-imred_$$ ${TEMPDIR}/@out-imred_$$ .fits F
  ${P_IMRED} ${TEMPDIR}/imred.param_$$

  if [ ! -d $1/$2/OFCSF_IMAGES ]; then
     mkdir $1/$2/OFCSF_IMAGES
  fi
  mv $1/$2/*_${CHIP}OFCSF.fits $1/$2/OFCSF_IMAGES

  i=$(( ${i} + 1 ))  
done



