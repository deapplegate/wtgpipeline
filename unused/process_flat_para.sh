#!/bin/bash -xv

# parallel version of process_flat_WFI.sh
#
# 18.09.01: - included parallel processing
#           - substituted the flipsrun calls by
#             direct calls to the corresponding
#             FLIPS programs
# 22.09.01: - included handling of links
#
# 03.09.2003:
# adapted script for new estimation of overscan:
#   - Instead of estimating the overscan of each line with the
#     median of the pixels in the overscan region, I now consider
#     the mean. From its calculation the 'minreject' lowest and
#     'maxreject' highest values are excluded.
#   - The smoothing of overscan over several lines is no longer done.
#
# 30.05.04:
# tempaorary files go to a TEMPDIR directory 


# the script processes a set of FLAT frames
# the images are overscan corrected, debiased and stacked with
# mode rescaling.

#$1: main directory (filter)
#$2: Bias directory
#$3: Flat directory
#$4: chips to process

# preliminary work:
. ${INSTRUMENT:?}.ini

#
# the resultdir is where the output coadded images
# will go. If ONE image of the corresponding chip
# is a link the image will go to THIS directory
for CHIP in $4
do
  RESULTDIR[${CHIP}]="$1/$3"
done

# Correction overscan; create config file on the fly
# we do not assume that the overscan is the same for all chips

for CHIP in $4
do
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
  echo "     doflat 0"                >> ${TEMPDIR}/imred.param_$$
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

  FILES=`ls $1/$3/*_${CHIP}.fits`

  for FILE in ${FILES}
  do
    if [ -L ${FILE} ]; then
	 LINK=`${P_READLINK} ${FILE}`
	 echo ${LINK} >> ${TEMPDIR}/@in-imred_$$ 
	 BASE=`basename ${LINK} .fits`
	 DIR=`dirname ${LINK}`
	 ln -s ${DIR}/${BASE}OC.fits $1/$3/${BASE}OC.fits
	 RESULTDIR[${CHIP}]=`dirname ${LINK}`
    else
	 echo "${FILE}" >> ${TEMPDIR}/@in-imred_$$
    fi
  done 
  
  if [ -f ${TEMPDIR}/@dark-imred_$$ ]; then
    rm ${TEMPDIR}/@dark-imred_$$
  fi

  ls $1/$2/$2_${CHIP}.fits >> ${TEMPDIR}/@dark-imred_$$

  ${S_LIO} ${TEMPDIR}/@in-imred_$$ ${TEMPDIR}/@out-imred_$$ .fits OC
  ${P_IMRED} ${TEMPDIR}/imred.param_$$

done

# We do a mode rescaling when combining flat images,
# so we run the mode on the overscan and bias subtracted
# images

# create input file and config file on the fly:
${S_LISTEXT_PARA} $1/$3/ OC.fits immode $$ "$4"

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

# Combine flat frames; create config file on the fly
echo "INPUT"                                       >  ${TEMPDIR}/imcombflat.param_$$
echo "     name   ${TEMPDIR}/@@in-imcombine.${INSTRUMENT}_$$" >> ${TEMPDIR}/imcombflat.param_$$
echo "end"                                         >> ${TEMPDIR}/imcombflat.param_$$
echo "OUTPUT"                                      >> ${TEMPDIR}/imcombflat.param_$$
echo "     name   ${TEMPDIR}/@out-imcombine_$$"               >> ${TEMPDIR}/imcombflat.param_$$
echo "     outbitpix -32"                          >> ${TEMPDIR}/imcombflat.param_$$
echo "     rescale 2"                              >> ${TEMPDIR}/imcombflat.param_$$
echo "end"                                         >> ${TEMPDIR}/imcombflat.param_$$
echo "CLIPPING"                                    >> ${TEMPDIR}/imcombflat.param_$$
echo "     median 1"                               >> ${TEMPDIR}/imcombflat.param_$$
echo "     lsigmas 2.5"                            >> ${TEMPDIR}/imcombflat.param_$$
echo "     hsigmas 2.5"                            >> ${TEMPDIR}/imcombflat.param_$$
echo "     threshold 1000"                         >> ${TEMPDIR}/imcombflat.param_$$
echo "     lcut -65000"                            >> ${TEMPDIR}/imcombflat.param_$$
echo "     hcut 65000"                             >> ${TEMPDIR}/imcombflat.param_$$
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

${S_LISTMODE_PARA} ${TEMPDIR}/immode.dat_$$ O imcombine $$ "$4"

for CHIP in $4
do
  echo "${TEMPDIR}/@in-imcombine.${CHIP}_$$" >> ${TEMPDIR}/@@in-imcombine.${INSTRUMENT}_$$
done

if [ -f ${TEMPDIR}/@out-imcombine_$$ ]; then
  rm ${TEMPDIR}/@out-imcombine_$$
fi

for CHIP in $4
do
  echo "${RESULTDIR[${CHIP}]}/$3_${CHIP}.fits" >> ${TEMPDIR}/@out-imcombine_$$

  if [ "${RESULTDIR[${CHIP}]}" != "$1/$3" ]; then
    ln -s ${RESULTDIR[${CHIP}]}/$3_${CHIP}.fits $1/$3/$3_${CHIP}.fits
  fi  
done

${P_IMCOMBFLAT} ${TEMPDIR}/imcombflat.param_$$

# remove intermediate results if asked for
if [ "${CLEANUP:+1}" = "1" ]; then    
  for CHIP in $3
  do
    # remove soft links and files; but ONLY from
    # the FLAT files
    ls -1 $1/$2/*_${CHIP}OC.fits > ${TEMPDIR}/tmp_$$
    cat ${TEMPDIR}/tmp_$$ |\
    {
      while read file
      do
	BASE=`basename ${file} OC.fits`
        rm $1/$2/${BASE}OC.fits      
        if [ "${RESULTDIR[${CHIP}]}" != "$1/$2" ]; then
          rm ${RESULTDIR[${CHIP}]}/${BASE}OC.fits
        fi
      done
    }
  done  
fi  


