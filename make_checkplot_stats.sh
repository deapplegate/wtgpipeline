#!/bin/bash
. BonnLogger.sh
. log_start
# the scripts creates a check plot for set quantities.
# out of the
# chips.cat5 STATS table. It needs the STATS
# table (chips.cat5) including relative photometric 
# zeropoint information.

# 22.01.2006:
# - I rewrote the script to accept the catalog and the
#   table containing the statistics on the command line.
#   This makes the script much more flexibel.
#   (Previously it needed a STATS table in a chips.cat5 catalog)
# - The name of the output plots in now a command line argument, too.
#
# 27.04.2006:
# The SupeMongo postscript device to use for the control plots
# can now be given as an optional command line argument (the default
# is 'postportfile')
#
# 18.09.2007:
# I included a plot of the datas dither pattern.

#$1: main dir.
#$2: science dir.
#$3: catalog (the location is assumed to be in /$1/$2/cat)
#$4: table containing statistics
#$5: basename of the output plots (they finally will be named
#    /$1/$2/plots/$5_1.ps (or $5_2.ps)
#$6: SuperMongo postscript device (OPTIONAL: defualted to postportfile)

. progs.ini

# set Super Mongo Postscript device:
SMDEVICE="postportfile"
if [ $# -eq 6 ]; then
  SMDEVICE=$6
fi

CAT=/$1/$2/cat/$3

if [ ! -f ${CAT} ]; then
  echo "no $3 in /$1/$2/cat/; exiting"
  log_status 1 "no $3 in /$1/$2/cat/"
  exit 1
fi 

# do we have lensing information

LENS=1

${P_LDACTESTEXIST} -i ${CAT} -t $4 -k e1 e2

if [ "$?" -gt "0" ]; then
  LENS=0
fi 


if [ ! -d /$1/$2/plots ]; then
  mkdir /$1/$2/plots
fi

${P_LDACTOASC} -i ${CAT} -t $4\
               -k SEEING -b > ${TEMPDIR}/seeing.asc_$$
${P_LDACTOASC} -i ${CAT} -t $4\
               -k RA DEC -b > ${TEMPDIR}/ra_dec_tmp.asc_$$
${P_LDACTOASC} -i ${CAT} -t $4\
               -k BACKGR -b > ${TEMPDIR}/backgr.asc_$$
${P_LDACTOASC} -i ${CAT} -t $4\
               -k RZP -b > ${TEMPDIR}/auto_zp.asc_$$
${P_LDACTOASC} -i ${CAT} -t $4\
               -k AIRMASS -b > ${TEMPDIR}/airmass.asc_$$
${P_LDACTOASC} -i ${CAT} -t $4\
               -k SEEING_SDEV -b > ${TEMPDIR}/seeing_sdev.asc_$$
${P_LDACTOASC} -i ${CAT} -t $4\
               -k BACKGR_SDEV -b > ${TEMPDIR}/backgr_sdev.asc_$$

if [ "${LENS}" == "1" ]; then
${P_LDACTOASC} -i ${CAT} -t $4\
               -k e1 e2 -b > ${TEMPDIR}/e1e2.asc_$$
fi
 
# calculate distances in arcsec from the mean
# RA, DEC values from this set:
${P_GAWK} 'BEGIN { DEGRAD = 3.14159 / 180.;} 
           { ra[NR]  = $1; ramean  += $1; 
             dec[NR] = $2; decmean += $2; }
           END { ramean /= NR; decmean /= NR;
             for(i = 1; i <= NR; i++)
             {
               radist[i]  = 3600. * (ra[i] - ramean) * cos(decmean * DEGRAD)
               decdist[i] = 3600. * (dec[i] - decmean) ;
               print radist[i], decdist[i];
             }}' ${TEMPDIR}/ra_dec_tmp.asc_$$ > ${TEMPDIR}/ra_dec.asc_$$

# now make plots
if [ "${LENS}" == "1" ]; then
{
echo "define TeX_strings 0"
echo 'device "'${SMDEVICE} /$1/$2/plots/$5_1.ps'"'
echo "toplabel $2_1"
echo "window 2 2 1 2"
echo 'data "'${TEMPDIR}/seeing.asc_$$'"'
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
echo 'data "'${TEMPDIR}/seeing_sdev.asc_$$'"'
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
echo 'data "'${TEMPDIR}/backgr.asc_$$'"'
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
echo 'data "'${TEMPDIR}/backgr_sdev.asc_$$'"'
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
echo 'device "'${SMDEVICE} /$1/$2/plots/$5_2.ps'"'
echo "toplabel $2_2"
echo "window 2 2 1 2"
echo 'data "'${TEMPDIR}/auto_zp.asc_$$'"'
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
echo "window 2 2 2 2"
echo 'data "'${TEMPDIR}/airmass.asc_$$'"'
echo "read { am 1 }"
echo "sort { am }"
echo "define min (am[0])"
echo "define max (am[dimen(backgr)-1])"
echo 'set x=$min-0.01,$max+0.01,0.01'
echo "set n=histogram(am:x)"
echo "limits x n"
echo "box"
echo "xlabel airmass"
echo "ylabel N"
echo "histogram x n"
echo "window 2 2 1 1"
echo 'data "'${TEMPDIR}/ra_dec.asc_$$'"'
echo "read { ra 1 dec 2}"
echo "limits ra dec"
echo "box"
echo "xlabel (Ra - <RA>) (arcsec)"
echo "ylabel (Dec - <Dec>) (arcsec)"
echo "points ra dec"
echo "window 2 2 2 1"
echo 'data "'${TEMPDIR}/e1e2.asc_$$'"'
echo "read { e1 1 e2 2}"
echo "limits e1 e2"
echo "box"
echo "xlabel e1"
echo "ylabel e2"
echo "points e1 e2"
echo "hardcopy"
} | ${P_SM}
else
{
echo "define TeX_strings 0"
echo 'device "'${SMDEVICE} /$1/$2/plots/$5_1.ps'"'
echo "toplabel $2_1"
echo "window 2 2 1 2"
echo 'data "'${TEMPDIR}/seeing.asc_$$'"'
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
echo 'data "'${TEMPDIR}/seeing_sdev.asc_$$'"'
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
echo 'data "'${TEMPDIR}/backgr.asc_$$'"'
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
echo 'data "'${TEMPDIR}/backgr_sdev.asc_$$'"'
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
echo 'device "'${SMDEVICE} /$1/$2/plots/$5_2.ps'"'
echo "toplabel $2_2"
echo "window 2 2 1 2"
echo 'data "'${TEMPDIR}/auto_zp.asc_$$'"'
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
echo 'data "'${TEMPDIR}/airmass.asc_$$'"'
echo "read { am 1 }"
echo "sort { am }"
echo "define min (am[0])"
echo "define max (am[dimen(backgr)-1])"
echo 'set x=$min-0.01,$max+0.01,0.01'
echo "set n=histogram(am:x)"
echo "limits x n"
echo "box"
echo "xlabel airmass"
echo "ylabel N"
echo "histogram x n"
echo "window 2 2 1 1"
echo 'data "'${TEMPDIR}/ra_dec.asc_$$'"'
echo "read { ra 1 dec 2}"
echo "limits ra dec"
echo "box"
echo "xlabel (Ra - <RA>) (arcsec)"
echo "ylabel (Dec - <Dec>) (arcsec)"
echo "points ra dec"
echo "hardcopy"
} | ${P_SM}
fi

rm ${TEMPDIR}/seeing.asc_$$
rm ${TEMPDIR}/ra_dec_tmp.asc_$$
rm ${TEMPDIR}/ra_dec.asc_$$
rm ${TEMPDIR}/backgr.asc_$$
rm ${TEMPDIR}/auto_zp.asc_$$
rm ${TEMPDIR}/airmass.asc_$$
rm ${TEMPDIR}/seeing_sdev.asc_$$
rm ${TEMPDIR}/backgr_sdev.asc_$$

if [ "${LENS}" == "1" ]; then
  rm ${TEMPDIR}/e1e2.asc_$$
fi
log_status $?
