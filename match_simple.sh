#!/bin/bash
set -xv
# $1 and $2 give the path
# $3 gives PHOTCAT path

. progs.ini

if [ ! -d "${TEMPDIR}/$$" ]; then
  mkdir ${TEMPDIR}/$$
fi

# remove old catalogs
rm -f ${TEMPDIR}/$$/*

file=$1
USNO=/nfs/slac/g/ki/ki05/anja/USNO-A2/
PHOTCAT=$2
OUTCAT=$3
BASE=`basename ${file} .cat`

cp $file ${TEMPDIR}/$$/${BASE}.cat



ldacaddkey -i ${TEMPDIR}/$$/${BASE}.cat -t OBJECTS -o ${TEMPDIR}/$$/${BASE}.cat0 \
    -k A_WCS_assoc 0.0003 FLOAT "" \
       B_WCS_assoc 0.0003 FLOAT "" \
       Theta_assoc 0.0 FLOAT "" \
       Flag_assoc 0 SHORT "" 


${P_LDACRENKEY} -i ${TEMPDIR}/$$/${BASE}.cat0 -o ${TEMPDIR}/$$/${BASE}.cat1 -k ALPHA_J2000 Ra DELTA_J2000 Dec 


${P_LDACRENTAB} -i ${TEMPDIR}/$$/${BASE}.cat1 -o ${TEMPDIR}/$$/${BASE}.cat9 -t OBJECTS STDTAB

ldacaddkey -i ${PHOTCAT} -t STDTAB -o ${TEMPDIR}/$$/PHOTCAT.cat \
    -k A_WCS_assoc 0.0006 FLOAT "" \
       B_WCS_assoc 0.0006 FLOAT "" \
       Theta_assoc 0.0 FLOAT "" \
       Flag_assoc 0 SHORT "" 

${P_ASSOCIATE} -i ${TEMPDIR}/$$/${BASE}.cat9 ${TEMPDIR}/$$/PHOTCAT.cat \
    -o ${TEMPDIR}/$$/tmp1_$$.cat  ${TEMPDIR}/$$/tmp2_$$.cat -t STDTAB \
    -c ${PHOTCONF}/fullphotom.conf.associate

${P_LDACFILTER} -i ${TEMPDIR}/$$/tmp1_$$.cat -o ${TEMPDIR}/$$/tmp3_$$.cat -c "(Pair_1>0);" -t STDTAB

if [ "$?" -ne "0" ]; then
    echo "Error in Matching!"
    exit 1
fi


${P_LDACFILTER} \
    -i ${TEMPDIR}/$$/tmp2_$$.cat \
    -o ${TEMPDIR}/$$/tmp4_$$.cat \
    -c "(Pair_0>0);" \
    -t STDTAB

	
${P_ASSOCIATE} -i ${TEMPDIR}/$$/tmp3_$$.cat ${TEMPDIR}/$$/tmp4_$$.cat \
    -o ${TEMPDIR}/$$/tmp5_$$.cat ${TEMPDIR}/$$/tmp6_$$.cat \
    -t STDTAB \
    -c ${PHOTCONF}/fullphotom.conf.associate

python mk_ssc_SDSS.py ${TEMPDIR}/$$/tmp.conf ${TEMPDIR}/$$/tmp5_$$.cat ${TEMPDIR}/$$/tmp6_$$.cat

rm -f $OUTCAT

# tmp5 is the SExtrator, tmp6 is standard stars

${P_MAKESSC} -i ${TEMPDIR}/$$/tmp5_$$.cat ${TEMPDIR}/$$/tmp6_$$.cat \
    -o $OUTCAT \
    -t STDTAB -c ${TEMPDIR}/$$/tmp.conf 


rm -rf ${TEMPDIR}/$$/






