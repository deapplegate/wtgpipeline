#!/bin/bash
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# the scripts creates a check plot out of the
# chips.cat6 IMAGE table. It is identical
# to make_checkplot.sh except that a filtering
# is performed before the plots are created.

#
# 05.07.2004:
# corrected a bug in giving TEMPDIR to sm
#
# 09.07.2004:
# the plots showing standard deviations start at zero
# not (standard deviations are always positive)
#
# 10.08.2004:
# corrected a bug in the creation of an ASCII list
# of relative zeropoints in the lensing case
# (a space was too much)
#
# 21.09.2004:
# at the start of the script chips.cat5 and chips.cat6
# are removed in the TEMPDIR if they exist (there were
# problems of an old chips.cat6 was present)

#$1: main dir.
#$2: science dir.
#$3: COADDIDENT
#$4: COADDCONDITION

. ${INSTRUMENT:?}.ini

mkdir /$1/$2/coadd_$3/cat

if [ -f ${TEMPDIR}/chips.cat6 ]; then
  rm -f  ${TEMPDIR}/chips.cat6
fi

if [ -f ${TEMPDIR}/chips.cat5 ]; then
  rm -f  ${TEMPDIR}/chips.cat5
fi

if [ ! -f /$1/$2/cat/chips.cat6 ]; then 
    ${P_LDACFILTER} -i /$1/$2/cat/chips.cat5 -o ${TEMPDIR}/chips.cat5 -t IMAGES -c $4
    else
    ${P_LDACFILTER} -i /$1/$2/cat/chips.cat6 -o ${TEMPDIR}/chips.cat6 -t IMAGES -c $4
fi

if [ ! -f ${TEMPDIR}/chips.cat6 ] && [ ! -f ${TEMPDIR}/chips.cat5 ]; then
  echo "adam-look | error: no chips.cat5 and chips.cat6 in ${TEMPDIR}; exiting"
  #adam-BL# log_status 1 "no chips.cat5 and chips.cat6 in ${TEMPDIR}"
  exit 1
fi 

# do we have lensing information

LENS=1

if [ ! -f ${TEMPDIR}/chips.cat6 ]; then
  LENS=0
fi 


if [ "${LENS}" == "1" ]; then
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat6 -t IMAGES\
               -k SEEING -b > ${TEMPDIR}/seeing.asc
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat6 -t IMAGES\
               -k BACKGR -b > ${TEMPDIR}/backgr.asc
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat6 -t IMAGES\
               -k AUTO_ZP -b >${TEMPDIR}/auto_zp.asc
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat6 -t IMAGES\
               -k e1 e2 -b > ${TEMPDIR}/e1e2.asc
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat6 -t IMAGES\
               -k SEEING_SDEV -b > ${TEMPDIR}/seeing_sdev.asc
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat6 -t IMAGES\
               -k BACKGR_SDEV -b > ${TEMPDIR}/backgr_sdev.asc
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat6 -t IMAGES\
               -k AUTO_ZP_SDEV -b > ${TEMPDIR}/auto_zp_sdev.asc
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat6 -t IMAGES\
               -k RA_OFF DEC_OFF -b > ${TEMPDIR}/radec.asc
else
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat5 -t IMAGES\
               -k SEEING -b > ${TEMPDIR}/seeing.asc
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat5 -t IMAGES\
               -k BACKGR -b > ${TEMPDIR}/backgr.asc
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat5 -t IMAGES\
               -k AUTO_ZP -b > ${TEMPDIR}/auto_zp.asc
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat5 -t IMAGES\
               -k SEEING_SDEV -b > ${TEMPDIR}/seeing_sdev.asc
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat5 -t IMAGES\
               -k BACKGR_SDEV -b > ${TEMPDIR}/backgr_sdev.asc
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat5 -t IMAGES\
               -k AUTO_ZP_SDEV -b > ${TEMPDIR}/auto_zp_sdev.asc
${P_LDACTOASC} -i ${TEMPDIR}/chips.cat5 -t IMAGES\
               -k RA_OFF DEC_OFF -b > ${TEMPDIR}/radec.asc
fi

# now make plots
if [ "${LENS}" == "1" ]; then
{
echo "define TeX_strings 0"
echo 'device "'psfile /$1/$2/plots/coadd_$3_$2_1.ps'"'
echo "toplabel $2_1"
echo "window 2 2 1 2"
echo 'data "'${TEMPDIR}/seeing.asc'"'
echo "read { seeing 1 }"
echo "sort { seeing }"
echo "define min (seeing[0])"
echo "define max (seeing[dimen(seeing)-1])"
echo 'set x=$min,$max,0.1'
echo "set n=histogram(seeing:x)"
echo "limits x n"
echo "box"
echo "xlabel seeing"
echo "ylabel N"
echo "histogram x n"
echo "window 2 2 2 2"
echo 'data "'${TEMPDIR}/seeing_sdev.asc'"'
echo "read { seeing_sdev 1 }"
echo "sort { seeing_sdev }"
echo "define min (seeing_sdev[0])"
echo "define max (seeing_sdev[dimen(seeing_sdev)-1])"
echo 'set x=0,$max+0.01,0.01'
echo "set n=histogram(seeing_sdev:x)"
echo "limits x n"
echo "box"
echo "xlabel seeing sdev"
echo "ylabel N"
echo "histogram x n"
echo "window 2 2 1 1"
echo 'data "'${TEMPDIR}/backgr.asc'"'
echo "read { backgr 1 }"
echo "sort { backgr }"
echo "define min (backgr[0])"
echo "define max (backgr[dimen(backgr)-1])"
echo 'set x=$min,$max,0.1'
echo "set n=histogram(backgr:x)"
echo "limits x n"
echo "box"
echo "xlabel sky background/sec"
echo "ylabel N"
echo "histogram x n"
echo "window 2 2 2 1"
echo 'data "'${TEMPDIR}/backgr_sdev.asc'"'
echo "read { backgr_sdev 1 }"
echo "sort { backgr_sdev }"
echo "define min (backgr_sdev[0])"
echo "define max (backgr_sdev[dimen(backgr_sdev)-1])"
echo 'set x=0,$max+0.001,0.001'
echo "set n=histogram(backgr_sdev:x)"
echo "limits x n"
echo "box"
echo "xlabel sky background sdev/sec"
echo "ylabel N"
echo "histogram x n"
echo "hardcopy"
echo 'device "'psfile /$1/$2/plots/coadd_$3_$2_2.ps'"'
echo "toplabel $2_2"
echo "window 2 2 1 2"
echo 'data "'${TEMPDIR}/auto_zp.asc'"'
echo "read { zp 1 }"
echo "sort { zp }"
echo "define min (zp[0])"
echo "define max (zp[dimen(zp)-1])"
echo 'set x=$min-0.01,$max+0.01,0.01'
echo "set n=histogram(zp:x)"
echo "limits x n"
echo "box"
echo "xlabel sky relative zeropoint"
echo "ylabel N"
echo "histogram x n"
echo "window 2 2 1 1"
echo 'data "'${TEMPDIR}/e1e2.asc'"'
echo "read { e1 1 e2 2}"
echo "limits e1 e2"
echo "box"
echo "xlabel e1"
echo "ylabel e2"
echo "points e1 e2"
echo "window 2 2 2 2"
echo 'data "'${TEMPDIR}/auto_zp_sdev.asc'"'
echo "read { zp_sdev 1 }"
echo "sort { zp_sdev }"
echo "define min (zp_sdev[0])"
echo "define max (zp_sdev[dimen(zp_sdev)-1])"
echo 'set x=0,$max+0.01,0.01'
echo "set n=histogram(zp_sdev:x)"
echo "limits x n"
echo "box"
echo "xlabel sky relative zeropoint sdev"
echo "ylabel N"
echo "histogram x n"
echo "window 2 2 2 1"
echo 'data "'${TEMPDIR}/radec.asc'"'
echo "read { ra 1 dec 2}"
echo "limits ra dec"
echo "box"
echo "xlabel RA Offset"
echo "ylabel DEC Offset"
echo "points ra dec"
echo "hardcopy"
} | ${P_SM}
else
{
echo "define TeX_strings 0"
echo 'device "'psfile /$1/$2/plots/coadd_$3_$2_1.ps'"'
echo "toplabel $2_1"
echo "window 2 2 1 2"
echo 'data "'${TEMPDIR}/seeing.asc'"'
echo "read { seeing 1 }"
echo "sort { seeing }"
echo "define min (seeing[0])"
echo "define max (seeing[dimen(seeing)-1])"
echo 'set x=$min,$max,0.1'
echo "set n=histogram(seeing:x)"
echo "limits x n"
echo "box"
echo "xlabel seeing"
echo "ylabel N"
echo "histogram x n"
echo "window 2 2 2 2"
echo 'data "'${TEMPDIR}/seeing_sdev.asc'"'
echo "read { seeing_sdev 1 }"
echo "sort { seeing_sdev }"
echo "define min (seeing_sdev[0])"
echo "define max (seeing_sdev[dimen(seeing_sdev)-1])"
echo 'set x=0,$max+0.01,0.01'
echo "set n=histogram(seeing_sdev:x)"
echo "limits x n"
echo "box"
echo "xlabel seeing_sdev"
echo "ylabel N"
echo "histogram x n"
echo "window 2 2 1 1"
echo 'data "'${TEMPDIR}/backgr.asc'"'
echo "read { backgr 1 }"
echo "sort { backgr }"
echo "define min (backgr[0])"
echo "define max (backgr[dimen(backgr)-1])"
echo 'set x=$min,$max,0.1'
echo "set n=histogram(backgr:x)"
echo "limits x n"
echo "box"
echo "xlabel sky background/sec"
echo "ylabel N"
echo "histogram x n"
echo "window 2 2 2 1"
echo 'data "'${TEMPDIR}/backgr_sdev.asc'"'
echo "read { backgr_sdev 1 }"
echo "sort { backgr_sdev }"
echo "define min (backgr_sdev[0])"
echo "define max (backgr_sdev[dimen(backgr_sdev)-1])"
echo 'set x=0,$max+0.001,0.001'
echo "set n=histogram(backgr_sdev:x)"
echo "limits x n"
echo "box"
echo "xlabel sky background_sdev/sec"
echo "ylabel N"
echo "histogram x n"
echo "hardcopy"
echo 'device "'psfile /$1/$2/plots/coadd_$3_$2_2.ps'"'
echo "toplabel $2_2"
echo "window 2 2 1 2"
echo 'data "'${TEMPDIR}/auto_zp.asc'"'
echo "read { zp 1 }"
echo "sort { zp }"
echo "define min (zp[0])"
echo "define max (zp[dimen(backgr)-1])"
echo 'set x=$min-0.01,$max+0.01,0.01'
echo "set n=histogram(zp:x)"
echo "limits x n"
echo "box"
echo "xlabel sky relative zeropoint"
echo "ylabel N"
echo "histogram x n"
echo "window 2 2 2 2"
echo 'data "'${TEMPDIR}/auto_zp_sdev.asc'"'
echo "read { zp_sdev 1 }"
echo "sort { zp_sdev }"
echo "define min (zp_sdev[0])"
echo "define max (zp_sdev[dimen(zp_sdev)-1])"
echo 'set x=0,$max+0.01,0.01'
echo "set n=histogram(zp_sdev:x)"
echo "limits x n"
echo "box"
echo "xlabel sky relative zeropoint_sdev"
echo "ylabel N"
echo "histogram x n"
echo "window 2 2 1 1"
echo 'data "'${TEMPDIR}/radec.asc'"'
echo "read { ra 1 dec 2}"
echo "limits ra dec"
echo "box"
echo "xlabel RA Offset"
echo "ylabel DEC Offset"
echo "points ra dec"
echo "hardcopy"
} | ${P_SM}
 
fi


#adam-BL# log_status $?
