#!/bin/bash
. BonnLogger.sh
. log_start
# the scripts creates a check plot out of the
# chips.cat6 IMAGE table

# 13.06.03:
# control plots now also can be made when no
# lensing information is available. In this case
# the ellipticity panel in the plot is just
# skipped
#
# 21.03.2004:
# now also the standard deviations from the seeing,
# sky background and relative photometric zeropoints
# are plotted. Also the RA and DEC offsets of 
# singleastrom are included in the plots now.
#
# 23.03.2004:
# The two plots created by this script are now stored
# in two different files.
#
# 30.05.04:
# tempaorary files go to a TEMPDIR directory 
#
# 08.07.2004:
# corrected a bug giving TEMPDIR to sm
#
# 09.07.2004:
# the plots showing standard deviations start at zero
# not (standard deviations are always positive)

#$1: main dir.
#$2: science dir.

. ${INSTRUMENT:?}.ini

if [ ! -f /$1/$2/cat/chips.cat6 ] && [ ! -f /$1/$2/cat/chips.cat5 ]; then
  echo "no chips.cat5 and chips.cat6 in /$1/$2/cat/; exiting"
  log_status 1 "no chips.cat5 and chips.cat6 in /$1/$2/cat/"
  exit 1
fi 

# do we have lensing information

LENS=1

if [ ! -f /$1/$2/cat/chips.cat6 ]; then
  LENS=0
fi 


if [ ! -d /$1/$2/plots ]; then
  mkdir /$1/$2/plots
fi

if [ "${LENS}" == "1" ]; then
${P_LDACTOASC} -i /$1/$2/cat/chips.cat6 -t IMAGES\
               -k SEEING -b > ${TEMPDIR}/seeing.asc
${P_LDACTOASC} -i /$1/$2/cat/chips.cat6 -t IMAGES\
               -k BACKGR -b > ${TEMPDIR}/backgr.asc
${P_LDACTOASC} -i /$1/$2/cat/chips.cat6 -t IMAGES\
               -k AUTO_ZP -b > ${TEMPDIR}/auto_zp.asc
${P_LDACTOASC} -i /$1/$2/cat/chips.cat6 -t IMAGES\
               -k e1 e2 -b > ${TEMPDIR}/e1e2.asc
${P_LDACTOASC} -i /$1/$2/cat/chips.cat6 -t IMAGES\
               -k SEEING_SDEV -b > ${TEMPDIR}/seeing_sdev.asc
${P_LDACTOASC} -i /$1/$2/cat/chips.cat6 -t IMAGES\
               -k BACKGR_SDEV -b > ${TEMPDIR}/backgr_sdev.asc
${P_LDACTOASC} -i /$1/$2/cat/chips.cat6 -t IMAGES\
               -k AUTO_ZP_SDEV -b > ${TEMPDIR}/auto_zp_sdev.asc
${P_LDACTOASC} -i /$1/$2/cat/chips.cat6 -t IMAGES\
               -k RA_OFF DEC_OFF -b > ${TEMPDIR}/radec.asc
else
${P_LDACTOASC} -i /$1/$2/cat/chips.cat5 -t IMAGES\
               -k SEEING -b > ${TEMPDIR}/seeing.asc
${P_LDACTOASC} -i /$1/$2/cat/chips.cat5 -t IMAGES\
               -k BACKGR -b > ${TEMPDIR}/backgr.asc
${P_LDACTOASC} -i /$1/$2/cat/chips.cat5 -t IMAGES\
               -k AUTO_ZP -b > ${TEMPDIR}/auto_zp.asc
${P_LDACTOASC} -i /$1/$2/cat/chips.cat5 -t IMAGES\
               -k SEEING_SDEV -b > ${TEMPDIR}/seeing_sdev.asc
${P_LDACTOASC} -i /$1/$2/cat/chips.cat5 -t IMAGES\
               -k BACKGR_SDEV -b > ${TEMPDIR}/backgr_sdev.asc
${P_LDACTOASC} -i /$1/$2/cat/chips.cat5 -t IMAGES\
               -k AUTO_ZP_SDEV -b > ${TEMPDIR}/auto_zp_sdev.asc
${P_LDACTOASC} -i /$1/$2/cat/chips.cat5 -t IMAGES\
               -k RA_OFF DEC_OFF -b > ${TEMPDIR}/radec.asc
fi
 
# now make plots
if [ "${LENS}" == "1" ]; then
{
echo "define TeX_strings 0"
echo 'device "'psfile /$1/$2/plots/$2_1.ps'"'
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
echo 'device "'psfile /$1/$2/plots/$2_2.ps'"'
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
echo 'device "'psfile /$1/$2/plots/$2_1.ps'"'
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
echo 'device "'psfile /$1/$2/plots/$2_2.ps'"'
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


log_status $?
