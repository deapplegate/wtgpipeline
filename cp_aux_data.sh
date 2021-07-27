#! /bin/bash -xv
#adam-example# ./cp_aux_data.sh ${SUBARUDIR} /u/ki/awright/data/from_archive/Z2701/
#adam-example# ./cp_aux_data.sh ${SUBARUDIR} 2010-03-04_W-S-Z+ /u/ki/awright/data/from_archive/Z2089/ (would put those from 2010-03-03 2010-03-04 & 2010-03-05 all in the same dir)
#adam-example# ./cp_aux_data.sh ${SUBARUDIR} 2010-12-05_W-J-V ~/my_data/from_archive/fgas_preH_raw/Z2701/FLAT/DOMEFLAT_2010-12-05_W-J-V
#. BonnLogger.sh
#. log_start
# copies auxiliary data (downloaded from the archive)
# searches also one level of subdirectories from $2

# one can optionally specify the rundir name (e.g. to associate data
# from other nights). to be compatible with older scripts, the rundir
# name comes before the auxiliary name.
# i.e.  ${MAINDIR} [${rundir}] ${auxdir}

# CVSId: $Id: cp_aux_data.sh,v 1.9 2009-02-07 03:21:01 anja Exp $

. progs.ini

REDDIR=`pwd`

SUBARUDIR=$1

if [ $# -eq 3 ]; then
    RUNDIR=$2
    rundirspecified=1
    AUXDATA=$3
else
    AUXDATA=$2
    rundirspecified=0
fi

mkdir ${SUBARUDIR}/tmpdir_$$


find ${AUXDATA} -follow -maxdepth 2 -name SUP?\*fits\* > cpfiles_$$.txt

while read FILE
do
     cp ${FILE} ${SUBARUDIR}/tmpdir_$$
done < cpfiles_$$.txt
rm -f cpfiles_$$.txt

cd ${SUBARUDIR}/tmpdir_$$

gunzip *.fits.gz


find . -maxdepth 1 -name SUP?????????\*fits > allfiles1_$$.txt

while read file
do

  base=`basename ${file}`
  expid=`dfits ${file} | fitsort -d EXP-ID | awk '{print $2}'`
  ending=`echo ${expid} | sed 's/\(SUP[A-Z][0-9][0-9][0-9][0-9][0-9][0-9][0-9]\)\([0-9]\)/\2/'`

  if [ ! ${ending} -eq 0 ]; then
      detid=`dfits ${file} | fitsort -d DET-ID | awk '{print $2}'`
      shortexpid=`echo ${expid} | sed 's/\(SUP[A-Z]\)\([0-9][0-9][0-9][0-9][0-9][0-9][0-9]\)\([0-9]\)/\2/'`
      
      mv ${file} SUPR${shortexpid}${detid}.fits
  fi

done < allfiles1_$$.txt

find . -maxdepth 1 -name SUP?????????\*fits > allfiles_$$.txt

sed 's/[0-9]\.fits//' allfiles_$$.txt | sort | uniq > uniqfiles_$$.txt

while read IMAGE
do
	BASE=`basename ${IMAGE}`
	echo ${BASE}
	mefcreate ${BASE}?.fits -OUTPUT_IMAGE ${BASE}.fits 
	rm -f ${BASE}?.fits
done < uniqfiles_$$.txt

rm -f allfiles_$$.txt
rm -f uniqfiles_$$.txt

# sort images by type, filter

find . -maxdepth 1 -name SUP????????\*fits > allfiles_mef_$$.txt

while read IMAGE
do
    BASE=`basename ${IMAGE}`

    date=`dfits -x 1 ${BASE} | fitsort DATE-OBS | awk '{if($1=="'${BASE}'") print $2}'`

    filter=`dfits -x 1 ${BASE} | fitsort FILTER01 | awk '{if($1=="'${BASE}'") print $2}'`

    obstype=`dfits -x 1 ${BASE} | fitsort DATA-TYP | awk '{if($1=="'${BASE}'") print $2}'`

    exptime=`dfits -x 1 ${BASE} | fitsort EXPTIME | awk '{if($1=="'${BASE}'") print $2}'`

    long=`awk 'BEGIN{if('${exptime}'>=30) print 1; else print 0}'`

    if [ ${rundirspecified} -eq 0 ]; then
	RUNDIR="${date}_${filter}"
    fi

    if [ "${obstype}" = "OBJECT" ];then
	if [ ${long} -eq 1 ]; then
      	   obstype=SCIENCE
	else
	   obstype=STANDARD
	fi
    fi

    if [ "${obstype}" = "BIAS" ] || [ "${obstype}" = "DARK" ]; then
	filter=${obstype}
	if [ ${rundirspecified} -eq 0 ]; then
	    RUNDIR="${date}_${obstype}"
        fi
    fi

    if [ ! -d ${SUBARUDIR}/${RUNDIR} ]; then
	mkdir ${SUBARUDIR}/${RUNDIR}
    fi

    if [ ! -d ${SUBARUDIR}/${RUNDIR}/${obstype} ]; then
	mkdir ${SUBARUDIR}/${RUNDIR}/${obstype}
    fi

    if [ ! -d ${SUBARUDIR}/${RUNDIR}/${obstype}/ORIGINALS ]; then
	mkdir ${SUBARUDIR}/${RUNDIR}/${obstype}/ORIGINALS
    fi

    echo ${BASE} ${obstype} ${exptime} ${long}

    mv ${BASE} ${SUBARUDIR}/${RUNDIR}/${obstype}/ORIGINALS

done < allfiles_mef_$$.txt

rm -f allfiles_mef_$$.txt

cd ${SUBARUDIR}
rm -rf tmpdir_$$

cd $REDDIR
#log_status $?
