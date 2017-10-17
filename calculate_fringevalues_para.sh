#!/bin/bash
set -xv
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# calculated fringe values with the method:
# mode of science frame/mode of background frame
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 


# $1: main directory (filter)
# $2: science directory
# $3: chips to be reduced

# preliminary work:
. ${INSTRUMENT:?}.ini

# get the modes of the background images
# create input file and config file on the fly for mode determination:

${S_LISTEXT_PARA} $1/$2/$2 _illum.fits immode $$ "$3"

echo "INPUT"                       > ${TEMPDIR}/immode.param_$$ 
echo "     name   ${TEMPDIR}/@in-immode_$$"   >> ${TEMPDIR}/immode.param_$$ 
echo "     dyn_min  -66000.0"      >> ${TEMPDIR}/immode.param_$$
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

${P_IMMODE} ${TEMPDIR}/immode.param_$$ \
            ${TEMPDIR}/immode.dat_$$ ${TEMPDIR}/immode-stat.dat_$$

# get the factors to normalise flats
MODEILLUM=`${P_GAWK} '($1!="->" && $1!="") {printf ("%f ", $2)}' ${TEMPDIR}/immode.dat_$$`

i=1
for CHIP in $3
do
  ACTUMODE=`echo ${MODEILLUM} | ${P_GAWK} '{print $'${i}'}'`

  # get the modes of the science frames:
  ls -1 $1/$2/*_${CHIP}OFCS.fits > ${TEMPDIR}/@in-immode_$$
  
  echo "INPUT"                       >  ${TEMPDIR}/immode.param_$$
  echo "     name   ${TEMPDIR}/@in-immode_$$"   >> ${TEMPDIR}/immode.param_$$
  echo "     dyn_min  -66000.0"      >> ${TEMPDIR}/immode.param_$$
  echo "     dyn_max  66000.0"       >> ${TEMPDIR}/immode.param_$$
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
  
  ${P_IMMODE} ${TEMPDIR}/immode.param_$$ ${TEMPDIR}/immode.dat_$$ \
              ${TEMPDIR}/immode-stat.dat_$$

  # write the fringevalues file
  ${P_GAWK} '($1!="->" && $1!="") {printf ("%s %f\n", $1, $2/'${ACTUMODE}')}' ${TEMPDIR}/immode.dat_$$ \
      > ${TEMPDIR}/fringevalues_${CHIP}

  i=$(( $i + 1 ))
done

#adam-BL# log_status $?
