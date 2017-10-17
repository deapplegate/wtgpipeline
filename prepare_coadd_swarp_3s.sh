#!/bin/bash
set -xv
#adam-BL#. BonnLogger.sh
#adam-BL#. log_start
# this script can be considered as the create_drizcl.sh
# part of a coaddition performed with swarp. It mainly creates
# a header file of the final output image from swarp coaddition

# 14.01.2004:
# I introduced the possibility to enter center coordinates
# for the output image. If they are not provided, they are
# taken from one of the input images. Hence the treatment is 
# consistent with that of create_drizcl.sh
#
# 12.02.2004:
# I introduced the possibility to give a directory for
# the WEIGHT images
#
# 19.02.2004:
# Fixed a bug so that given headers (-h option) are now 
# taken into account
#
# 27.04.2004:
# from the swarp output headers, CDELT and PV lines are deleted.
# We assume that input headers carry astrometric information
# in the form of CD matrices.
#
# 29.02.2004:
# If the coaddition directory is already present
# when entering the script, it is either created,
# or old files are deleted. Afterwards, links are
# newly created in any case. The old treatment of
# not recreating links led to errors when determining
# the center position of the pointing.
#
# 01.03.2004:
# the Pixelscale is now manually given in the case
# no header is provided.
# In the same case, from the produced header only 
# possible PV polynomials
# are deleted, not the CDELT keywords anymore. These
# are the only astrometric keywords produced by swarp
# by default (version 1.38)
#
# THE CASE WHERE A HEADER IS PROVIDED IS HIGHLY BUGGY
# (version 1.38 from swarp)
#
# 30.04.2004:
# not used temporary files are deleted at the end now
#
# 28.07.2005:
# - I included the possibility to coadd only the data from
#   a specified chip (command line option '-c').
# - I included the possibiliry to use external headers
#   for all the images.
#
# 23.01.2006:
# if a catalog is given defining conditions on the
# input images we now have to specify the table in which
# the conditions are given.
#
# 25.07.2006:
# - Temporary files get more robust, unique filenames and
#   are deleted at the end of the script.
# - If a CCD has a headerkeyword 'BADCCD' containing '1'
#   that CCD is not considered in the co-addition process.
# - The 'coadd.head' file stored in the reduce directory
#   gets a unique name consisting of science dir. and
#   co-addition identifier. This allows the execution of several
#   co-additions simultaneously.
#
# 23.09.2006:
# The filenames of images to be resampled are passed to swarp 
# no longer on the command line but in a file instead. 
#
# 03.08.2007:
# If external headers are given we check whether images have
# ASTBAD=1 set inside these headers. If yes, the image is not
# included in the co-addition. ASTROMETRIX indicates with this 
# flag (besids with BADCCD=1) that astrometric calibration for 
# this image went wrong.
#
# 15.09.2007:
# It is now necessary to specify the directory of external headers
# (together with the -eh option). This is necessary because with
# the possibility to use scamp for astrometric calibration different
# header directories can exist.
#
# 11.09.2008: (AvdL)
# added an optional argument to specify the image size

# preliminary work:
. progs.ini > /tmp/progs.out 2>&1 

# -m: main dir.
# -s: science dir. (the cat dir is a subdirectory
#                  of this)
# -e: extension (added by add_image_calibs)      (including OFCSFF etc.)
# -n: coaddition identifier (4 charracters)      (OPTIONAL: DEFA)
# -w: weight base extension                      (OPTIONAL: same as extension; without OFCSFF etc.)
# -l: catalog table condition output cat         (OPTIONAL: all images in dir; catalog with COMPLETE path;
#                                                 condition in ldacfilter format; catalog must have
#                                                 IMAGES table)
# -r RA   (Ra of coadded image center)           (OPTIONAL: first image)
# -d DEC  (Dec of coadded image center)          (OPTIONAL: first image)
# -wd weight directory                           (OPTIONAL: WEIGHTS)
# -h header file conatining cards for the        (OPTIONAL: no header file)
#    coadded image (has to be given with full
#    path)
# -c chips to coadd                              (OPTIONAL: default: all chips)
# -eh header directory  (directory with astrometric headers under maindir/sciencedir) 
#                                                (OPTIONAL: default: images themselfs have 
#                                                           astrometric headers)
# -i size_x, size_y                              (OPTIONAL: dimensions of the output image;
#                                                           default: let swarp figure it out)
# -p pixelscale                                  (OPTIONAL: pixelscale)

# read command line arguments:
#
# default values:
MAIN=""
SCIENCE=""
EXTEN=""
WBASE=""
SCRIPT="DEFA"
LIST=""
TABLE=""
CONDITION=""
OUTPUT=""
HEADER=""
RA=""
DEC=""
WEIGHTDIR="WEIGHTS"
EXTERNHEAD=0
EXTERNHEADDIR=""
CHIPS=""
IMAGESIZE=0


GoOn=0
while [ $GoOn = 0 ]
do
   case $1 in
   -m)
       MAIN=${2}
       shift 2
       ;;
   -s)
       SCIENCE=${2}
       shift 2
       ;;
   -e)
       EXTEN=${2}
       shift 2
       ;;
   -n)
       SCRIPT=${2}
       shift 2
       ;;
   -w)
       WBASE=${2}
       shift 2
       ;;
   -r)
       RA=${2}
       shift 2
       ;;
   -d)
       DEC=${2}
       shift 2
       ;;
   -re)
       RESOL=${2}
       shift 2
       ;;
   -h)
       HEADER=${2}
       shift 2
       ;;
   -eh)
       EXTERNHEAD=1
       EXTERNHEADDIR=${2}
       shift 2
       ;;
   -c)
       CHIPS=${2}
       shift 2
       ;;
   -wd)
       WEIGHTDIR=${2}
       shift 2
       ;;
   -l)
       LIST=${2}
       TABLE=${3}
       CONDITION=${4}
       OUTPUT=${5}
       shift 5
       ;;
   -i)
       IMAGESIZE=${2}
       shift 2
       ;;
   -p)
       PIXSCALE=${2}
       shift 2
       ;;
    *)
       GoOn=1
       ;;
   esac
done

if [ ! -d ${MAIN}/${SCIENCE}/${EXTERNHEADDIR} ]; then

    #adam-BL#log_status 2 "External header dir doesn't exist: ${EXTERNHEADDIR}"
    exit 2

fi

# weight images are assumed to reside in 
# /${MAIN}/${WEIGHTDIR}

# create links of the science and weight frames:
BONNDIR=`pwd`
HEADDIR="/nfs/slac/g/ki/ki18/anja/SUBARU/coadd_headers/"
# construct a unique name for the coadd.head file
# of this co-addition:
#
# The following 'sed' ensures a 'unique' construction with the
# '/' character which can appear in arbitrary combinations in
# file- and pathnames.
TMPNAME_1=`echo ${MAIN##/*/} | sed -e 's!/\{2,\}!/!g' -e 's!^/*!!' -e 's!/*$!!'`
TMPNAME_2=`echo ${SCIENCE} | sed -e 's!/\{2,\}!/!g' -e 's!^/*!!' -e 's!/*$!!'`
COADDFILENAME=${TMPNAME_1}_${TMPNAME_2}_${SCRIPT}

cd /${MAIN}/${SCIENCE}/

NCHIPS=`ls -1 *${EXTEN}.fits | awk -F'_' '{print $2}' | awk -F"${EXTEN}." '{print $1}' | awk 'BEGIN{n=0}{if($1>n)n=$1}END{print n}'`

i=1
while [ "${i}" -le "${NCHIPS}" ]
do
  CHIPS="${CHIPS} ${i}"
  i=$(( $i + 1 ))
done

### create coadd directory if it not yet exists
if [ ! -d coadd_${SCRIPT} ]; then
  mkdir coadd_${SCRIPT}
else
  # in case that the coaddition directory already
  # exists we assume that we want to REDO
  # some coaddition. Hence all old files are deleted.
  rm -rf ./coadd_${SCRIPT}/
  mkdir coadd_${SCRIPT}
fi
#
if [ -f ${TEMPDIR}/coaddimages_$$ ]; then
  rm -f ${TEMPDIR}/coaddimages_$$
fi

if [ -f ${TEMPDIR}/crvals_$$ ]; then
  rm -f ${TEMPDIR}/crvals_$$
fi

if [ "${LIST}_A" == "_A" ]; then
  for chip in ${CHIPS}
  do  
    ls -1 /${MAIN}/${SCIENCE}/*_${chip}${EXTEN}.fits >> ${TEMPDIR}/coaddimages_$$
  done
else
  ${P_LDACFILTER} -i ${LIST} -t ${TABLE} -c ${CONDITION}\
                  -o ${OUTPUT} -m ${SCRIPT}

  if [ "$?" -gt "0" ]; then
      cd ${BONNDIR}
      echo "error in filtering list catalog; exiting"
      #adam-BL#log_status 1 "err in filtering list catalog"
      exit 1;
  fi              

  ${P_LDACFILTER} -i ${OUTPUT} -t ${TABLE} \
                  -c "(${SCRIPT}=1);" -o ${TEMPDIR}/tmp_$$.cat
  ${P_LDACTOASC} -i ${TEMPDIR}/tmp_$$.cat -t ${TABLE} -b -s\
                 -k IMAGENAME > ${TEMPDIR}/tmp_$$.asc

  cat ${TEMPDIR}/tmp_$$.asc |\
  {
    while read FILE
    do
      for chip in ${CHIPS}
      do  
        echo "/${MAIN}/${SCIENCE}/${FILE}_${chip}${EXTEN}.fits" \
             >> ${TEMPDIR}/coaddimages_$$
      done
    done        
  }
fi

cat ${TEMPDIR}/coaddimages_$$ |\
{
  while read file
  do
    BASE=`basename ${file}`
    BASEWEIGHT=`basename ${file} ${WBASE}.fits`

    # check for BADCCD; if an image has a BADCCD mark of '1' it is
    # NOT included in the co-addition process

    BADCCD=`${P_DFITS} ${file} | ${P_FITSORT} BADCCD |\
            ${P_GAWK} '($1!="FILE") {print $2}'`

    # do the same for ASTBAD! ASTBAD is a header keyword set in
    # ASTROMETRIX to '1' if for some reason astrometry went
    # wrong and we do not want to use the frame in co-addition. 
    # This flag is not present anywhere else. Hence, the
    # following grep/awk construct which is not at all robust 
    # to errors, misformats of external headers:
    if [ "${EXTERNHEAD}" -eq 1 ]; then
      HEADBASE=`basename ${file} ${EXTEN}.fits`
      if [ -f /${MAIN}/${SCIENCE}/${EXTERNHEADDIR}/${HEADBASE}.head ]; then
        ASTBAD=`grep ASTBAD /${MAIN}/${SCIENCE}/${EXTERNHEADDIR}/${HEADBASE}.head |\
                ${P_GAWK} '{print $3}'`    
	CRVAL1=`grep CRVAL1 /${MAIN}/${SCIENCE}/${EXTERNHEADDIR}/${HEADBASE}.head |\
                ${P_GAWK} '{print $3}'`
	CRVAL2=`grep CRVAL2 /${MAIN}/${SCIENCE}/${EXTERNHEADDIR}/${HEADBASE}.head |\
                ${P_GAWK} '{print $3}'`
      else
	  ASTBAD=1
      fi
    else
	CRVAL1=`${P_DFITS} ${file} | ${P_FITSORT} -d CRVAL1 | ${P_GAWK} '{print $2}'`
	CRVAL2=`${P_DFITS} ${file} | ${P_FITSORT} -d CRVAL2 | ${P_GAWK} '{print $2}'`
    fi
    

    if [ "${BADCCD}" != "1" ] && [ "${ASTBAD}" != "1" ]; then
      ln -s ${file} ./coadd_${SCRIPT}/${BASE}
      ln -s /${MAIN}/${WEIGHTDIR}/${BASEWEIGHT}.weight.fits \
            ./coadd_${SCRIPT}/${BASEWEIGHT}${WBASE}.weight.fits
      if [ -e /${MAIN}/${WEIGHTDIR}/${BASEWEIGHT}.flag.fits ]; then
	  ln -s /${MAIN}/${WEIGHTDIR}/${BASEWEIGHT}.flag.fits \
              ./coadd_${SCRIPT}/${BASEWEIGHT}${WBASE}.flag.fits
      fi

      echo "${BASE} ${CRVAL1} ${CRVAL2}" >> ${TEMPDIR}/crvals_$$
  
      if [ "${EXTERNHEAD}" -eq 1 ]; then
        cp /${MAIN}/${SCIENCE}/${EXTERNHEADDIR}/${HEADBASE}.head \
          ./coadd_${SCRIPT}/${HEADBASE}${EXTEN}.head
	if [ "$?" -gt "0" ]; then exit $? ; fi

	if [ -e /${MAIN}/${WEIGHTDIR}/${BASEWEIGHT}.flag.fits ]; then
	    ln -s ${HEADBASE}${EXTEN}.head \
		./coadd_${SCRIPT}/${BASEWEIGHT}${WBASE}.flag.head
	fi
      fi
    else
      echo "${file} marked as BAD CCD; not included in the coaddition"
    fi
  done
}

# get RA and DEC for the coaddition centre
# --> use the image that has a different RA DEC

calibfile=`${P_GAWK} 'function acos(x) { return atan2((1.-x^2)^0.5,x) }
           {
             dist=57.2958*acos(cos(1.5708-($3*0.01745))*cos(1.5708-('${DEC}'*0.01745)) + (sin(1.5708-($3*0.01745))*sin(1.5708-('${DEC}'*0.01745)))*cos(($2-'${RA}')*0.01745))
             print $1, dist
           }' ${TEMPDIR}/crvals_$$ | awk 'BEGIN{max=0}{if($2>max){max=$2;keep=$1}}END{print keep}' | awk 'BEGIN{FS="_"}{print $1}'`

clustfile=`${P_GAWK} 'function acos(x) { return atan2((1.-x^2)^0.5,x) }
           {
             dist=57.2958*acos(cos(1.5708-($3*0.01745))*cos(1.5708-('${DEC}'*0.01745)) + (sin(1.5708-($3*0.01745))*sin(1.5708-('${DEC}'*0.01745)))*cos(($2-'${RA}')*0.01745))
             print $1, dist
           }' ${TEMPDIR}/crvals_$$ | awk 'BEGIN{max=100}{if($2<max){max=$2;keep=$1}}END{print keep}' | awk 'BEGIN{FS="_"}{print $1}'`

### update header FLXSCALE keyword

update=`grep SFLSCALE ${MAIN}/${SCIENCE}/${EXTERNHEADDIR}/${calibfile}_*.head`
if [ ! ${update} ]; then
  echo "Updating FLXSCALE keyword of 3s exposure."
  for headfile in $(ls -1 ${MAIN}/${SCIENCE}/${EXTERNHEADDIR}/${calibfile}_*.head)
  do
    chnum=`basename ${headfile} .head | awk 'BEGIN{FS="_"}{print $NF}'`
    flxscale=`grep FLXSCALE ${MAIN}/${SCIENCE}/${EXTERNHEADDIR}/${clustfile}_${chnum}.head | awk '{sum=sum+$2;n++}END{print sum/n}'`
    rzp=`grep RZP ${MAIN}/${SCIENCE}/${EXTERNHEADDIR}/${clustfile}_${chnum}.head | grep relative | awk '{sum=sum+$3;n++}END{print sum/n}'`
    sed 's/FLXSCALE/SFLSCALE/g' ${MAIN}/${SCIENCE}/${EXTERNHEADDIR}/${calibfile}_${chnum}.head |\
    sed 's/RZP     =/SRZP    =/g' |\
    ${P_GAWK} '{
                 if($1 == "END")
                 {
                   printf("FLXSCALE= %20E / flxscale of cluster 3s exposure\n", 
                                '${flxscale}');
                   printf("RZP     = %20f / RZP of cluster 3s exposure\n", 
                                '${rzp}');
                   printf("END\n")
                 }
                 else
                   print $0
               }' > tmp.head
    mv tmp.head ${headfile}
  done
fi

while read file
do
  base=`basename ${file} .fits`
  expo=`echo ${base} | awk 'BEGIN{FS="_"}{print $1}'`

  if [ "${expo}" != "${calibfile}" ]; then
      rm -f ./coadd_${SCRIPT}/${base}*
  else
      RA=`${P_DFITS} ${file} | ${P_FITSORT} -d CRVAL1 | ${P_GAWK} '{print $2}'`
      DEC=`${P_DFITS} ${file} | ${P_FITSORT} -d CRVAL2 | ${P_GAWK} '{print $2}'`
  fi

done < ${TEMPDIR}/coaddimages_$$

#
cd ./coadd_${SCRIPT}

# run swarp to get output header
${P_FIND} . -maxdepth 1 -name \*${EXTEN}.fits > ${TEMPDIR}/files_$$.list

if [ ! -s ${TEMPDIR}/files_$$.list ]; then
    cd ${BONNDIR}
    #adam-BL#log_status 3 "No files found to coadd!"
    exit
fi

if [ "${HEADER}_A" == "_A" ]; then

  #create a header file with proper WCS info
  
  NAXIS1=`echo $IMAGESIZE | sed 's/,/ /' | awk '{print $1}'`
  NAXIS2=`echo $IMAGESIZE | sed 's/,/ /' | awk '{print $2}'`

  CENTER1=$((NAXIS1 / 2))
  CENTER2=$((NAXIS2 / 2))

  echo "NAXIS   = 2" > coadd.head
  echo "NAXIS1  = $NAXIS1" >> coadd.head
  echo "NAXIS2  = $NAXIS2" >> coadd.head
  echo "CTYPE1  = 'RA---TAN'" >> coadd.head
  echo "CUNIT1  = 'deg     '" >> coadd.head
  echo "CRVAL1  = ${RA}" >> coadd.head
  echo "CRPIX1  = $CENTER1" >> coadd.head                    
  echo "CTYPE2  = 'DEC--TAN'          " >> coadd.head 
  echo "CUNIT2  = 'deg     '          " >> coadd.head                     
  echo "CRVAL2  = ${DEC}" >> coadd.head 
  echo "CRPIX2  = $CENTER2" >> coadd.head 
  #adam: make CDELT[1-2] dependent upon PIXSCALE. convert to degrees!!
  PXSCALE=`${P_GAWK} 'BEGIN{print '${PIXSCALE}'/3600.}'`
  if [ "$?" -gt "0" ]; then exit $? ; fi
  echo "CD1_1   = -${PXSCALE}" >>  ./coadd.head
  echo "CD2_2   = ${PXSCALE}" >>  ./coadd.head
  echo "CD2_1   = 0.000000000000" >>  ./coadd.head
  echo "CD1_2   = 0.000000000000" >>  ./coadd.head
  echo "END     "  >>  ./coadd.head


  ${P_SWARP} -c ${DATACONF}/create_coadd_swarp.swarp \
             -RESAMPLE N -COMBINE N \
             -CENTER_TYPE MANUAL -HEADER_ONLY Y -PIXELSCALE_TYPE MANUAL \
             -VERBOSE_TYPE FULL \
	     @${TEMPDIR}/files_$$.list 
             #adam-old#-PIXEL_SCALE ${PIXSCALE} -IMAGE_SIZE ${IMAGESIZE} -VERBOSE_TYPE FULL \
	     #adam-old#-INPUTIMAGE_LIST ${TEMPDIR}/files_$$.list 
  if [ "$?" -gt "0" ]; then exit $? ; fi
  
  fold coadd.fits | grep -v "^PV\|^CDELT[1-2]" > ${HEADDIR}/coadd_${COADDFILENAME}.head
  if [ "$?" -gt "0" ]; then exit $? ; fi
  rm -f ./coadd.head

else
  cp ${HEADER} ./coadd.head
  #
  # we assume that the header contains astrometric information;
  # hence, centers given by hand have no effect here
  # (this is to avoid possible conflicts if centers are
  # given manually and in header files)
  ${P_SWARP} -c ${DATACONF}/create_coadd_swarp.swarp \
             -RESAMPLE N -COMBINE N \
             -HEADER_ONLY Y \
	     @${TEMPDIR}/files_$$.list
	     #adam-old#-INPUTIMAGE_LIST ${TEMPDIR}/files_$$.list
  if [ "$?" -gt "0" ]; then exit $? ; fi
  
  #adam-old# fold coadd.fits fold | grep -v "^PV" |\
  #adam-old#    grep -v "^CDELT" > ${BONNDIR}/coadd_${COADDFILENAME}.head
  fold coadd.fits | grep -v "^PV\|^CDELT[1-2]" > ${HEADDIR}/coadd_${COADDFILENAME}.head
  if [ "$?" -gt "0" ]; then exit $? ; fi

  rm -f coadd.head
fi

cd ${BONNDIR}

# clean up temporary files
rm -f ${TEMPDIR}/tmp_$$.asc
rm -f ${TEMPDIR}/tmp_$$.cat
rm -f ${TEMPDIR}/coaddimages_$$
rm -f ${TEMPDIR}/files_$$.list
#adam-BL#log_status $exit_status
