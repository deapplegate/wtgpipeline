#!/bin/bash
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# script to split off auxiliary data, i.e. data used to get a better
# superflat

# the script collects some header keywords of a directory with raw fits
# files into an LDAC catalog with a FILES table. These data are then
# used to distinguish 'sets' of images

#$1: main directory
#$2: science directory
#$3: image extension (ext) on ..._iext.fits (i is the chip number)
#$4: lookup file: nick full_name ra dec nicknames

. ${INSTRUMENT:?}.ini

# configuration parameters:

FILTERKEY="FILTER"
OBJECTKEY="OBJECT"
RAKEY="CRVAL1"
DECKEY="CRVAL2"

${P_FIND} $1/$2/ -maxdepth 1 -name \*$3.fits -print > ${TEMPDIR}/images_$$

if [ ! -s ${TEMPDIR}/images_$$ ]; then
    #adam-BL# log_status 2 "No images to review"
    echo "adam-look | error: No images to review"
    exit 2
fi

if [ -f "${TEMPDIR}/images_tmp.dat_$$" ]; then
  rm -f ${TEMPDIR}/images_tmp.dat_$$
fi

cat ${TEMPDIR}/images_$$ |\
{
  while read IMAGE
  do

    BASE=`basename ${IMAGE}`
    OBJECT=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${OBJECTKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`
    RA=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${RAKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`
    DEC=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${DECKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`
    BADCCD=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} BADCCD  | ${P_GAWK} '($1!="FILE") {print $2}'`

    echo ${BASE} ${OBJECT} ${RA} ${DEC} ${BADCCD} >> ${TEMPDIR}/images_tmp.dat_$$
  done
}

cat ${TEMPDIR}/images_tmp.dat_$$ |\
{
  while read BASE OBJECT ra dec BADCCD
  do

    if [ ${BADCCD} == "1" ]; then
	echo ${BASE} ${OBJECT} "moved to" /$1/$2_aux
	mv /$1/$2/${BASE} /$1/$2_aux
    else

	nnick=`grep ${OBJECT} $4 | wc | awk '{print $1}'`

	if [ ${nnick} -eq 1 ]; then
	    nick=`grep ${OBJECT} $4 | awk '{print $1}'`	
	else
	    nick=`awk 'function acos(x) { return atan2((1.-x^2)^0.5,x) }
            {
              dist=57.2958*acos(cos(1.5708-('${dec}'*0.01745))*cos(1.5708-($4*0.01745)) + (sin(1.5708-('${dec}'*0.01745))*sin(1.5708-($4*0.01745)))*cos(('${ra}'-$3)*0.01745))
              if( dist<1.5 ) print $2}' $4`
	fi
	
	if [ -z ${nick} ]; then
	    if [ ! -d "/$1/$2_aux" ]; then
		mkdir "/$1/$2_aux"
	    fi
	    
	    echo ${BASE} ${OBJECT} "moved to" /$1/$2_aux
	    mv /$1/$2/${BASE} /$1/$2_aux

	fi

    fi

  done
}
#adam-BL# log_status $?
