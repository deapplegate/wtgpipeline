#!/bin/bash -xv

# the script creates Sex background images for one pointing and
# coadds them.

# 30.05.04:
# temporary files go to a TEMPDIR directory 

# $1: main directory (filter)
# $2: Science directory
# $3: ending
# $4: chips to be processed

# preliminary work:
. ${INSTRUMENT:?}.ini

for CHIP in $4
do
  RESULTDIR[${CHIP}]="/$1/$2"
done

for CHIP in $4
do
  ls -1 /$1/$2/*_${CHIP}$3.fits > ${TEMPDIR}/backimages_$$

  FILE=`${P_GAWK} '(NR==1) {print $0}' ${TEMPDIR}/backimages_$$`
  
  if [ -L ${FILE} ]; then
     LINK=`${P_READLINK} ${FILE}`
     RESULTDIR[${CHIP}]=`dirname ${LINK}`    
  fi
    
  cat ${TEMPDIR}/backimages_$$ |\
  {
    while read file
    do
	BASE=`basename ${file} .fits`
	#
	# now run sextractor to subtract objects from the image
 	${P_SEX} ${file} -c ${DATACONF}/image-objects.sex\
		         -CHECKIMAGE_TYPE -OBJECTS\
		         -CHECKIMAGE_NAME ${RESULTDIR[${CHIP}]}/${BASE}"_back.fits"\
		         -PARAMETERS_NAME ${DATACONF}/point_back.param.sex

        ${P_IC} '%1 -70000 %2 fabs 1.0e-06 > ?' ${file} ${RESULTDIR[${CHIP}]}/${BASE}"_back.fits"\
             > ${RESULTDIR[${CHIP}]}/${BASE}"_back1.fits"
        mv ${RESULTDIR[${CHIP}]}/${BASE}"_back1.fits" ${RESULTDIR[${CHIP}]}/${BASE}"_back.fits"

        if [ "${RESULTDIR[${CHIP}]}" != "/$1/$2" ]; then
          ln -s ${RESULTDIR[${CHIP}]}/${BASE}"_back.fits"\
                /$1/$2/${BASE}"_back.fits"	  
        fi
    done
  }
done

#
#

# We do a mode rescaling when combining superflat images,
# (here background)
# so we run the mode on the overscan and bias subtracted
# images

# create input file and config file on the fly:

if [ -f ${TEMPDIR}/@in-immode_$$ ]; then
  rm ${TEMPDIR}/@in-immode_$$
fi
if [ -f @${TEMPDIR}/immode.dat_$$ ]; then
  rm @${TEMPDIR}/immode.dat_$$
fi
if [ -f ${TEMPDIR}/@@in-imcombine.${INSTRUMENT}_$$ ]; then
  rm ${TEMPDIR}/@@in-imcombine.${INSTRUMENT}_$$
fi
if [ -f ${TEMPDIR}/@out-imcombine_$$]; then
  rm ${TEMPDIR}/@out-imcombine_$$
fi

${S_LISTEXT_PARA} $1/$2/ $3_back.fits immode $$ "$4"

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

${P_IMMODE} ${TEMPDIR}/immode.param_$$ ${TEMPDIR}/immode.dat_$$ ${TEMPDIR}/immode-stat.dat_$$

touch ${TEMPDIR}/@@in-imcombine.${INSTRUMENT}_$$
for CHIP in $4
do
  echo "${TEMPDIR}/@in-imcombine.${CHIP}_$$" >> ${TEMPDIR}/@@in-imcombine.${INSTRUMENT}_$$
done

# Combine flat frames; create config file on the fly
echo "INPUT"                                       >  ${TEMPDIR}/imcombflat.param_$$
echo "     name   @@in-imcombine.${INSTRUMENT}_$$" >> ${TEMPDIR}/imcombflat.param_$$
echo "end"                                         >> ${TEMPDIR}/imcombflat.param_$$
echo "OUTPUT"                                      >> ${TEMPDIR}/imcombflat.param_$$
echo "     name   @out-imcombine_$$"               >> ${TEMPDIR}/imcombflat.param_$$
echo "     outbitpix -32"                          >> ${TEMPDIR}/imcombflat.param_$$
echo "     rescale 2"                              >> ${TEMPDIR}/imcombflat.param_$$
echo "end"                                         >> ${TEMPDIR}/imcombflat.param_$$
echo "CLIPPING"                                    >> ${TEMPDIR}/imcombflat.param_$$
echo "     median 0"                               >> ${TEMPDIR}/imcombflat.param_$$
echo "     lsigmas 3.5"                            >> ${TEMPDIR}/imcombflat.param_$$
echo "     hsigmas 3.5"                            >> ${TEMPDIR}/imcombflat.param_$$
echo "     lcut -66000"                            >> ${TEMPDIR}/imcombflat.param_$$
echo "     hcut 66000"                             >> ${TEMPDIR}/imcombflat.param_$$
echo "     hrej 1"                                 >> ${TEMPDIR}/imcombflat.param_$$
echo "     sigmare 4.0"                            >> ${TEMPDIR}/imcombflat.param_$$
echo "end"                                         >> ${TEMPDIR}/imcombflat.param_$$
echo "CCDCLIPPING"                                 >> ${TEMPDIR}/imcombflat.param_$$
echo "     ccdclip 0"                              >> ${TEMPDIR}/imcombflat.param_$$
echo "end"                                         >> ${TEMPDIR}/imcombflat.param_$$
echo "BUFFER"                                      >> ${TEMPDIR}/imcombflat.param_$$
echo "     height 1"                               >> ${TEMPDIR}/imcombflat.param_$$
echo "end"                                         >> ${TEMPDIR}/imcombflat.param_$$
echo "VERBOSE"                                     >> ${TEMPDIR}/imcombflat.param_$$
echo "     verbose 0"                              >> ${TEMPDIR}/imcombflat.param_$$
echo "end"                                         >> ${TEMPDIR}/imcombflat.param_$$
echo "END"                                         >> ${TEMPDIR}/imcombflat.param_$$

${S_LISTMODE_SIGMA_PARA} ${TEMPDIR}/immode.dat_$$ $3_back imcombine $$ "$4"

touch ${TEMPDIR}/@out-imcombine_$$
for CHIP in $4
do
  echo "${RESULTDIR[${CHIP}]}/$2_${CHIP}.fits" >>  ${TEMPDIR}/@out-imcombine_$$

  if [ "${RESULTDIR[${CHIP}]}" != "/$1/$2" ]; then
    ln -s ${RESULTDIR[${CHIP}]}/$2_${CHIP}.fits \
          /$1/$2/$2_${CHIP}.fits	  
  fi

done

${P_IMCOMBFLAT} ${TEMPDIR}/imcombflat.param_$$

for CHIP in $4
do
  ${P_SEX} /$1/$2/$2_${CHIP}.fits -c ${DATACONF}/create_point_back.conf.sex \
	    -BACK_SIZE 512 -CHECKIMAGE_NAME ${RESULTDIR[${CHIP}]}/$2_${CHIP}_tmp.fits \
	    -PARAMETERS_NAME ${DATACONF}/point_back.param.sex
  mv ${RESULTDIR[${CHIP}]}/$2_${CHIP}_tmp.fits ${RESULTDIR[${CHIP}]}/$2_${CHIP}.fits

  if [ ! -d /$1/$2/BACK_IMAGES ]; then
     mkdir /$1/$2/BACK_IMAGES
  fi
  mv /$1/$2/*_${CHIP}OFCSF_back.fits /$1/$2/BACK_IMAGES
done

