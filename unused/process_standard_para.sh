#!/bin/bash -xv

# the script processes a set of Standard star frames
# the images are overscan corrected, debiased, flatfielded 
# and superflat corrected with superflats created
# from correspondending science frames (that have a higher
# S/N in comparison to standard star frames)

# 22.03.2004:
# I deleted the superfluous creation of superflats
# from the standard fields as they are not used anyway
# (this was a leftover from the creation of this script
# out of the process_science code.)
#
# 15.07.2004:
# I adapted the script to process_science, i.e.
# the gain equalisation can be either done in
# this script with skyflats or at a later stage
# with superflats.
#
# 16.07.2004:
# corrected a bug in the setting of the FACT variable.

#$1: main directory (filter)
#$2: Bias directory
#$3: Flat directory
#$4: Science directory
#$5: Standard directory
#$6: RESCALE/NORESCALE
#$7: chips to be processed

# preliminary work:
. ${INSTRUMENT:?}.ini

# the resultdir is where the output coadded images
# will go. If ONE image of the corresponding chip
# is a link the image will go to THIS directory
for CHIP in $7
do
  SCIRESULTDIR[${CHIP}]="$1/$4/"
  STDRESULTDIR[${CHIP}]="$1/$5/"
done

#rm @in-imred

# Correction overscan, Bias and flat; create config file on the fly
# we do not assume that the overscan is the same for all chips

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

${S_LISTEXT_PARA} $1/$3/$3 .fits immode $$ "${ALLCHIPS}"

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

if [ -f ${TEMPDIR}/immode.dat_$$ ]; then
  rm ${TEMPDIR}/immode.dat_$$
fi
if [ -f ${TEMPDIR}/immode-stat.dat_$$ ]; then
  rm ${TEMPDIR}/immode-stat.dat_$$
fi

${P_IMMODE} ${TEMPDIR}/immode.param_$$ ${TEMPDIR}/immode.dat_$$ ${TEMPDIR}/immode-stat.dat_$$

# get the factors to normalise flats
FACT=`${P_GAWK} '($1!="->" && $1!="") {printf ("%f ", $2)}' ${TEMPDIR}/immode.dat_$$`
MAXFACT=`${P_GAWK} 'BEGIN {max=0} ($1!="->" && $1!="") {if($2>max) max=$2} END {print max}' ${TEMPDIR}/immode.dat_$$`

for CHIP in $7
do
  ACTUFACT=`echo ${FACT} | ${P_GAWK} '{print $'${CHIP}'}'`
  if [ "$6" = "RESCALE" ]; then
    ACTUFACT=${MAXFACT}
  fi
  echo "INPUT"                        >  ${TEMPDIR}/imred.param_$$
  echo "     name   ${TEMPDIR}/@in-imred_$$"     >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "OUTPUT"                       >> ${TEMPDIR}/imred.param_$$
  echo "     name   ${TEMPDIR}/@out-imred_$$"    >> ${TEMPDIR}/imred.param_$$
  echo "     outbitpix -32"           >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "OVERSCAN"                     >> ${TEMPDIR}/imred.param_$$
  echo "     doover 1"                >> ${TEMPDIR}/imred.param_$$
  echo "     modline  1"              >> ${TEMPDIR}/imred.param_$$
  echo "     ovscan ${OVSCANX1[${CHIP}]} ${OVSCANX2[${CHIP}]}" >> ${TEMPDIR}/imred.param_$$
  echo "     reject 5 5"              >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "DARK"                         >> ${TEMPDIR}/imred.param_$$
  echo "     file 1"                  >> ${TEMPDIR}/imred.param_$$
  echo "     dodark 1"                >> ${TEMPDIR}/imred.param_$$
  echo "     fact 1.0"                >> ${TEMPDIR}/imred.param_$$
  echo "     name ${TEMPDIR}/@dark-imred_$$"     >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "FLAT"                         >> ${TEMPDIR}/imred.param_$$
  echo "     doflat 1"                >> ${TEMPDIR}/imred.param_$$
  echo "     fact ${ACTUFACT}"        >> ${TEMPDIR}/imred.param_$$
  echo "     subst 50.0"              >> ${TEMPDIR}/imred.param_$$
  echo "     name ${TEMPDIR}/@flat-imred_$$"     >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "MASK"                         >> ${TEMPDIR}/imred.param_$$
  echo "     domask 0"                >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "FRINGE"                       >> ${TEMPDIR}/imred.param_$$
  echo "     dofringe 0"              >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "RASTER"                       >> ${TEMPDIR}/imred.param_$$
  echo "     cut 1"                   >> ${TEMPDIR}/imred.param_$$ 
  echo "     x ${CUTX[${CHIP}]}"      >> ${TEMPDIR}/imred.param_$$
  echo "     y ${CUTY[${CHIP}]}"      >> ${TEMPDIR}/imred.param_$$
  echo "     sizex ${SIZEX[${CHIP}]}" >> ${TEMPDIR}/imred.param_$$
  echo "     sizey ${SIZEY[${CHIP}]}" >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "END"                          >> ${TEMPDIR}/imred.param_$$
  

  if [ -f ${TEMPDIR}/@in-imred_$$ ]; then
    rm ${TEMPDIR}/@in-imred_$$
  fi
  if [ -f ${TEMPDIR}/@out-imred_$$ ]; then
    rm ${TEMPDIR}/@out-imred_$$
  fi
  if [ -f ${TEMPDIR}/@dark-imred_$$ ]; then
    rm ${TEMPDIR}/@dark-imred_$$
  fi
  if [ -f ${TEMPDIR}/@flat-imred_$$ ]; then
    rm ${TEMPDIR}/@flat-imred_$$
  fi

  ls $1/$2/$2_${CHIP}.fits > ${TEMPDIR}/@dark-imred_$$
  ls $1/$3/$3_${CHIP}.fits > ${TEMPDIR}/@flat-imred_$$

  FILES=`ls $1/$5/*_${CHIP}.fits`

  for FILE in ${FILES}
  do
    if [ -L ${FILE} ]; then
	     LINK=`${P_READLINK} ${FILE}`
	     echo ${LINK} >> ${TEMPDIR}/@in-imred_$$ 
	     BASE=`basename ${LINK} .fits`
	     DIR=`dirname ${LINK}`
	     ln -s ${DIR}/${BASE}OFC.fits $1/$5/${BASE}OFC.fits
	     STDRESULTDIR[${CHIP}]=`dirname ${LINK}`    
    else
	     echo "${FILE}" >> ${TEMPDIR}/@in-imred_$$
    fi
  done 
  
  ${S_LIO} ${TEMPDIR}/@in-imred_$$ ${TEMPDIR}/@out-imred_$$ .fits OFC
  ${P_IMRED} ${TEMPDIR}/imred.param_$$

  if [ ! -d /$1/$5/SPLIT_IMAGES ]; then
	    mkdir /$1/$5/SPLIT_IMAGES
  fi
  mv /$1/$5/*_${CHIP}.fits /$1/$5/SPLIT_IMAGES

done


for CHIP in $7
do
    cp /${SCIRESULTDIR[${CHIP}]}/$4_${CHIP}.fits /${STDRESULTDIR[${CHIP}]}/$5_${CHIP}.fits

    # create link if necessary
    if [ ! -f $1/$5/$5_${CHIP}.fits ]; then
      ln -s /${STDRESULTDIR[${CHIP}]}/$5_${CHIP}.fits $1/$5/$5_${CHIP}.fits
    fi
done