#!/bin/bash -xv

# this script can be considered as the create_drizcl.sh
# part of a coaddition performed with swarp. It mainly creates
# a header file of the final output image from swarp coaddition

# This version is special for CFH12K reduction!!
# It orginates from prepare_coadd_swarp.sh from 23.01.2006!!
# If the GABODSID of an input image is smaller than 305
# (i.e. from the first instrument consiguration period) chips 
# 6 and 12 are NEVER included in the coaddition.

# preliminary work:
. ${INSTRUMENT:?}.ini

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
CHIPS=""


i=1
while [ "${i}" -le "${NCHIPS}" ]
do
  CHIPS="${CHIPS} ${i}"
  i=$(( $i + 1 ))
done


GoOn=0
while [ $GoOn = 0 ]
do
   case $1 in
   -m)
       MAIN=${2}
       shift
       shift
       ;;
   -s)
       SCIENCE=${2}
       shift
       shift
       ;;
   -e)
       EXTEN=${2}
       shift
       shift
       ;;
   -n)
       SCRIPT=${2}
       shift
       shift
       ;;
   -w)
       WBASE=${2}
       shift
       shift
       ;;
   -r)
       RA=${2}
       shift
       shift
       ;;
   -d)
       DEC=${2}
       shift
       shift
       ;;
   -re)
       RESOL=${2}
       shift
       shift
       ;;
   -h)
       HEADER=${2}
       shift
       shift
       ;;
   -eh)
       EXTERNHEAD=1
       shift
       ;;
   -c)
       CHIPS=${2}
       shift
       shift
       ;;
   -wd)
       WEIGHTDIR=${2}
       shift
       shift
       ;;
   -l)
       LIST=${2}
       TABLE=${3}
       CONDITION=${4}
       OUTPUT=${5}
       shift
       shift
       shift
       shift
       shift
       ;;
    *)
       GoOn=1
       ;;
   esac
done

# weight images are assumed to reside in 
# /${MAIN}/${WEIGHTDIR}

# create links of the science and weight frames:
DIR=`pwd`

cd /${MAIN}/${SCIENCE}/

# create coadd directory if it not yet exists
if [ ! -d coadd_${SCRIPT} ]; then
  mkdir coadd_${SCRIPT}
else
  # in case that the coaddition directory already
  # exists we assume that we want to REDO
  # some coaddition. Hence all old files are deleted.
  rm ./coadd_${SCRIPT}/*
fi

\rm ${DIR}/coaddimages

if [ "${LIST}_A" == "_A" ]; then
  # we assume for now that chip 1 of each image is present !!  
  ls -1 /${MAIN}/${SCIENCE}/*_1${EXTEN}.fits |\
  {
      while read FILE
      do
	BASE=`basename ${FILE} _1${EXTEN}.fits`

        for chip in ${CHIPS}
        do  
	  GABODSID=`${P_DFITS} ${FILE} | ${P_FITSORT} -d GABODSID | ${P_GAWK} '($1!="FILE") {print $2}'`

	  if [ ${GABODSID} -lt 305 ]; then
	      if [ ${chip} -eq 6 ] || [ ${chip} -eq 12 ]; then
	         echo "Not including chip ${chip} from ${FILE} in coaddition!!"
	      else
		 echo "/${MAIN}/${SCIENCE}/${BASE}_${chip}${EXTEN}.fits"  >> ${DIR}/coaddimages
	      fi
	  else
	      echo "/${MAIN}/${SCIENCE}/${BASE}_${chip}${EXTEN}.fits" >> ${DIR}/coaddimages
	  fi
	done
      done
  }
else
  ${P_LDACFILTER} -i ${LIST} -t ${TABLE} -c ${CONDITION}\
                  -o ${OUTPUT} -m ${SCRIPT}

  if [ "$?" -gt "0" ]; then
    echo "error in filtering list catalog; exiting"
    exit 1;
  fi		  

  ${P_LDACFILTER} -i ${OUTPUT} -t ${TABLE} \
                  -c "(${SCRIPT}=1);" -o ${DIR}/tmp.cat
  ${P_LDACTOASC} -i ${DIR}/tmp.cat -t ${TABLE} -b -s\
                 -k IMAGENAME > ${DIR}/tmp.asc

  cat ${DIR}/tmp.asc |\
  {
    while read FILE
    do
         for chip in ${CHIPS}
         do  
	  GABODSID=`${P_DFITS} ${FILE}_1${EXTEN}.fits | ${P_FITSORT} -d GABODSID |\
                     ${P_GAWK} '($1!="FILE") {print $2}'`

	  if [ ${GABODSID} -lt 305 ]; then
	      if [ ${chip} -eq 6 ] || [ ${chip} -eq 12 ]; then
	         echo "Not including chip ${chip} from ${FILE}_${chip}${EXTEN}.fits in coaddition!!"
	      else
		 echo "/${MAIN}/${SCIENCE}/${FILE}_${chip}${EXTEN}.fits"  >> ${DIR}/coaddimages
	      fi
	  else
	      echo "/${MAIN}/${SCIENCE}/${FILE}_${chip}${EXTEN}.fits" >> ${DIR}/coaddimages
	  fi
	done
    done	
  }
fi

cat ${DIR}/coaddimages |\
{
  while read file
  do
    BASE=`basename ${file}`
    BASEWEIGHT=`basename ${file} ${WBASE}.fits`

    ln -s ${file} ./coadd_${SCRIPT}/${BASE}
    ln -s /${MAIN}/${WEIGHTDIR}/${BASEWEIGHT}.weight.fits ./coadd_${SCRIPT}/${BASEWEIGHT}${WBASE}.weight.fits

    if [ "${EXTERNHEAD}" -eq 1 ]; then
	HEADBASE=`basename ${file} ${EXTEN}.fits`
	if [ -f /${MAIN}/${SCIENCE}/headers/${HEADBASE}.head ]; then
	    cp /${MAIN}/${SCIENCE}/headers/${HEADBASE}.head \
            ./coadd_${SCRIPT}/${HEADBASE}${EXTEN}.head
	else
	    echo "/${MAIN}/${SCIENCE}/headers/${HEADBASE}.head not present; Aborting"
	    exit 1;
	fi
    fi
  done
}

# get RA and DEC for the coaddition centre
# from the first image of the list if RA and DEC
# are not provided
if [ "${RA}_A" == "_A" ] || [ "${DEC}_A" == "_A" ]; then
  REFFILE=`${P_GAWK} '(NR==1) {print $0}' ${DIR}/coaddimages`

  RA=`${P_DFITS} ${REFFILE} | ${P_FITSORT} CRVAL1 | ${P_GAWK} '($1!="FILE") {print $2}'`
  DEC=`${P_DFITS} ${REFFILE} | ${P_FITSORT} CRVAL2 | ${P_GAWK} '($1!="FILE") {printf $2}'`
fi

#
cd ./coadd_${SCRIPT}

# run swarp to get output header
if [ "${HEADER}_A" == "_A" ]; then
  ${P_SWARP} -c ${DATACONF}/create_coadd_swarp.swarp \
             *${EXTEN}.fits -RESAMPLE N -COMBINE N \
             -CENTER `${P_DECIMALTOHMS} ${RA}`,`${P_DECIMALTODMS} ${DEC}`\
             -CENTER_TYPE MANUAL -HEADER_ONLY Y -PIXELSCALE_TYPE MANUAL \
             -PIXEL_SCALE ${PIXSCALE}
  
  fold coadd.fits | grep -v "^PV" > ${DIR}/coadd.head
else
  cp ${HEADER} ./coadd.head
  #
  # we assume that the header contains astrometric information;
  # hence, centers given by hand have no effect here
  # (this is to avoid possible conflicts if centers are
  # given manually and in header files)
  ${P_SWARP} -c ${DATACONF}/create_coadd_swarp.swarp \
             *${EXTEN}.fits -RESAMPLE N -COMBINE N \
             -HEADER_ONLY Y
  
  fold coadd.fits fold | grep -v "^PV" | grep -v "^CDELT" > ${DIR}/coadd.head
  rm coadd.head
fi

cd ${DIR}
rm tmp.asc
rm tmp.cat
