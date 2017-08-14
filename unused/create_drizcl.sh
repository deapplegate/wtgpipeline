#!/bin/bash -xv

# the script creates the drizzle cl-script
# by a call to IRAF

. ${INSTRUMENT:?}.ini

# -m: main dir.
# -s: science dir. (the cat dir is a subdirectory
#                  of this)
# -e: extension (added by add_image_calibs)      (including OFCSFF etc.)
# -n: name of the cl-script (4 charracters)      (OPTIONAL: DEFA)
# -w: weight base extension                      (OPTIONAL: same as extension; without OFCSFF etc.)
# -si: size of output sections                   (OPTIONAL: 2048)
# -re: resolution of coadded image               (OPTIONAL: pixel scale of input images)
# -r: RA                                         (OPTIONAL: first ima)
# -d: DEC                                        (OPTIONAL: first ima)
# -l: catalog condition output cat               (OPTIONAL: all images in dir; catalog with COMPLETE path;
#                                                 condition in ldacfilter format; catalog must have
#                                                 IMAGES table)
# -wd: WEIGHT directory                          (OPTIONAL: WEIGHTS)

# 26.04.02:
# chnaged the IRAFDIR concept for
# parallel processing. There are now
# as many IRAFDIR directories as
# processors (realised as arrays
# IRAFDIR[i]

# 01.11.02:
# the resolution of the coadded image can now
# be changed on the command line with the 're'
# specifier.

# 12.02.2004:
# I introduced the possibility to give a directory for
# the WEIGHT images. .hhh and .hhd files from an old
# coaddition are now deleted.

# 30.05.04:
# tempaorary files go to a TEMPDIR directory 

# read command line arguments:
#
# default values:
MAIN=""
SCIENCE=""
EXTEN=""
WBASE=""
SCRIPT="DEFA"
RA=""
DEC=""
LIST=""
CONDITION=""
OUTPUT=""
SIZE="2048"
RESOL=""
WEIGHTDIR="WEIGHTS"

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
   -si)
       SIZE=${2}
       shift
       shift
       ;;
   -re)
       RESOL=${2}
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
   -wd)
       WEIGHTDIR=${2}
       shift
       shift
       ;;
   -l)
       LIST=${2}
       CONDITION=${3}
       OUTPUT=${4}
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

# set WBASE if necessary:
if [ "${WBASE}_A" == "_A" ]; then
  WBASE=${EXTEN}
fi

#
# here the script starts
#
DIR=`pwd`

# prepare image list of frames to be
# coadded
\rm ${DIR}/drizclimages

if [ "${LIST}_A" == "_A" ]; then
  ls -1 /${MAIN}/${SCIENCE}/*${EXTEN}.fits > ${DIR}/drizclimages
else
  ${P_LDACFILTER} -i ${LIST} -t IMAGES -c ${CONDITION}\
                  -o ${OUTPUT} -m ${SCRIPT}

  if [ "$?" -gt "0" ]; then
    echo "error in filtering list catalog; exiting"
    exit 1;
  fi		  

  ${P_LDACFILTER} -i ${OUTPUT} -t IMAGES \
                  -c "(${SCRIPT}=1);" -o ${TEMPDIR}/tmp.cat
  ${P_LDACTOASC} -i ${TEMPDIR}/tmp.cat -t IMAGES -b -s\
                 -k IMAGENAME > ${TEMPDIR}/tmp.asc

  cat ${TEMPDIR}/tmp.asc |\
  {
    while read FILE
    do
	 i=1
	 while [ "${i}" -le "${NCHIPS}" ]
	 do
	   echo "/${MAIN}/${SCIENCE}/${FILE}_${i}${EXTEN}.fits" >> ${DIR}/drizclimages
	   i=$(( $i + 1 ))
	 done
    done	
  }
fi

# go through the IRAF directories and create
# links to the SCIENCE/WEIGHT frames. We just
# create links for ALL images in ALL directories.

i=1
while [ "$i" -le "${NPARA}" ]
do
  cd ${IRAFDIR[${i}]}

  # delete old links
  \rm *${EXTEN}.fits
  \rm *weight.fits

  # delete possible files from a previous coaddition
  \rm ${SCRIPT}*hhh
  \rm ${SCRIPT}*hhd
    
  # create new links
  #
  cat ${DIR}/drizclimages |\
  {
    while read file
    do
      BASE=`basename ${file}`
      BASEWEIGHT=`basename ${file} ${WBASE}.fits`
  
      ln -s ${file} ${BASE}
      ln -s /${MAIN}/${WEIGHTDIR}/${BASEWEIGHT}.weight.fits ${BASEWEIGHT}${WBASE}.weight.fits
    done
  }

  i=$(( $i + 1 ))  
done


# the creation of scripts is done
# in the first IRAF dir.
cd ${IRAFDIR[1]}


# get RA and DEC for the coaddition centre
# from the first image of the list if RA and DEC
# are not provided
if [ "${RA}_A" == "_A" ]; then
  REFFILE=`${P_GAWK} '(NR==1) {print $0}' ${DIR}/drizclimages`

  RA=`${P_DFITS} ${REFFILE} | ${P_FITSORT} CRVAL1 | ${P_GAWK} '($1!="FILE") {print $2}'`
  DEC=`${P_DFITS} ${REFFILE} | ${P_FITSORT} CRVAL2 | ${P_GAWK} '($1!="FILE") {printf $2}'`
fi

# the resolution of the coadded image is taken from the INSTRUMENT
# config file if not provided by the user.
if [ "${RESOL}_A" == "_A" ]; then
  RESOL=${PIXSCALE}
fi

{
  echo "eis"
  echo 'parapredriz.image = "'*${EXTEN}.fits'"'
  echo 'parapredriz.outmode = "'tiles'"'
  echo "parapredriz.npara = ${NPARA}"
  echo 'parapredriz.stem = "'${SCRIPT}'"'
  echo 'parapredriz.output = "''"'
  echo "parapredriz.outra = ${RA}"
  echo "parapredriz.outdec = ${DEC}"
  echo 'parapredriz.proj = "'TAN'"'
  echo 'parapredriz.context = no'
  echo 'parapredriz.direct = "''"'
  echo 'parapredriz.weight = "'default'"'
  echo "parapredriz.raref = ${RA}"
  echo "parapredriz.decref = ${DEC}"
  echo "parapredriz.outscl = ${RESOL}"
  echo "parapredriz.outnx = ${SIZE}"
  echo "parapredriz.outny = ${SIZE}"
  echo 'parapredriz.xcen = 0'
  echo 'parapredriz.ycen = 0'
  echo 'parapredriz.mode = "'ql'"'
  #
  echo "flprc"
  echo 'parapredriz(image="'*${EXTEN}.fits'", outmode="'tiles'")'
  echo "flprc"
  echo "logout"
} | ${P_CL}

i=2

while [ "${i}" -le "${NPARA}" ]
do
  mv ${SCRIPT}*${i}.cl ${IRAFDIR[${i}]}
  i=$(( $i + 1 )) 
done

rm ${TEMPDIR}/tmp.cat
rm ${TEMPDIR}/tmp.asc

cd ${DIR}



