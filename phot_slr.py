#! /usr/bin/env python

# $1: main dir
# $2: star catalog

. progs.ini

import sys

MAINDIR=sys.argv[0]
STARCAT=sys.argv[1]
CLUSTER=sys.argv[2]

os.environ['IDLUTILS_DIR']='/nfs/slac/g/ki/ki04/pkelly/idlutils'
os.environ['IDL_PATH'] += '+$IDLUTILS_DIR/pro:+$IDLUTILS_DIR/goddard/pro' 
os.environ['IDL_PATH'] += '+/nfs/slac/g/ki/ki06/anja/software/slr/pro'
os.environ['SLR_INSTALL'] += '/nfs/slac/g/ki/ki06/anja/software/slr'
os.environ['SLR_DATA'] += '/nfs/slac/g/ki/ki06/anja/software/slr/example_data'

./dump_cat_filters.py ${MAINDIR}/${STARCAT} > filters.list_$$

outline="ALPHA_J2000 DELTA_J2000"
outheader="# ID type tmixed RA Dec "

rm ${MAINDIR}/slr.offsets.list
nfilt=0
nK=1000

Mupres=0
SBpres=0
SVpres=0
SRpres=0
SIpres=0
Szpres=0
WKpres=0

while read filterlong
do
    instrum=`echo ${filterlong} | awk 'BEGIN{FS="-"}{print $1}'`
    config=`echo ${filterlong} | awk 'BEGIN{FS="-"}{print $2}'`
    chiptype=`echo ${filterlong} | awk 'BEGIN{FS="-"}{print $3}'`

    if [ ${instrum} == "SUBARU" ]; then
	filter=`echo ${filterlong} | awk 'BEGIN{FS="-"}{print $4"-"$5"-"$6}'`
    else
	filter=`echo ${filterlong} | awk 'BEGIN{FS="-"}{print $4}'`
    fi

    case ${filter} in
        "g" | "r" | "i" | "z" | "B" | "I" )
    	shortfilt=${filter};;
        "u" )
    	shortfilt=${filter}
	Mupres=1;;
        "K" )
    	shortfilt=${filter}
	WKpres=1;;
        "W-J-B" )
    	shortfilt="B"
	SBpres=1;;
        "W-J-V" )
    	shortfilt="V"
	SVpres=1;;
        "W-C-RC" )
    	shortfilt="R"
	SRpres=1;;
        "W-C-IC" )
    	shortfilt="I"
	SIpres=1;;
        "W-S-Z+" )
    	shortfilt="z"
	Szpres=1;;
    esac

    ### NOTE!!!!
    ### this still needs to be fixed:
    ### currently, it would output more than one column if there is data from several configurations
    ### if the colorterms between chips are small enough, it's probably best to concatenate all of them
    
    if [ ${instrum} == "SUBARU" ]; then
       if [ ${chiptype} == "1" ]; then
	  outline="${outline} MAG_APER-${filterlong}:1 MAGERR_APER-${filterlong}:1"
	  outheader="${outheader} ${shortfilt} ${shortfilt}_err"
	  echo ${shortfilt} ${filterlong} >> ${MAINDIR}/slr.offsets.list
	  nfilt=$(($nfilt+1))
       fi
    elif [ "${instrum}" == "MEGAPRIME" ]; then
	outline="${outline} MAG_APER-${filterlong}:1 MAGERR_APER-${filterlong}:1"
	outheader="${outheader} ${shortfilt} ${shortfilt}_err"
	echo ${shortfilt} ${filterlong} >> ${MAINDIR}/slr.offsets.list
	nfilt=$(($nfilt+1))
    elif [ "${filterlong}" == "SPECIAL-0-1-K" ]; then
	outline="${outline} MAG_APER-${filterlong}:1 MAGERR_APER-${filterlong}:1"
	outheader="${outheader} ${shortfilt} ${shortfilt}_err"
	echo ${shortfilt} ${filterlong} >> ${MAINDIR}/slr.offsets.list
	nfilt=$(($nfilt+1))
	nK=$nfilt
    fi

echo ${outline}

done < filters.list_$$
rm filters.list_$$

echo ${outheader} > ${MAINDIR}/stars_4slr.dat

${P_LDACTOASC} -i ${MAINDIR}/${STARCAT} \
               -t OBJECTS \
               -b -k SeqNr \
	       | awk '{printf "%5i 1 0\n", $1}' \
               > ${TEMPDIR}/tmp_stars_1_$$.dat

./ldactoasc.py -i ${MAINDIR}/${STARCAT} \
               -t OBJECTS \
               ${outline} \
	       | awk '{for(n=1;n<=NF;n++){if($n==0 || $n==-99) printf "           -"; else if(n==(2+(2*'${nK}'-1))) printf " % 11.9g", $n-1.837; else printf " % 11.9g", $n}; printf "\n"}' \
               > ${TEMPDIR}/tmp_stars_2_$$.dat

paste ${TEMPDIR}/tmp_stars_1_$$.dat ${TEMPDIR}/tmp_stars_2_$$.dat >> ${MAINDIR}/stars_4slr.dat


cd ${MAINDIR}

cp stars_4slr.dat stars_4slr.ctab

export SLR_COLORTABLE_IN=stars_4slr.ctab
export SLR_COLORTABLE_OUT=test.dat

### SLR really likes environment variables, btw...
### the SDSS --> Johnson color terms are defined in
###  /nfs/slac/g/ki/ki06/anja/software/slr/pro/io/slr_read_covey_median_locus.pro 
### from line 221

ZPR=0
awk '{if($1=="R") print $0, '${ZPR}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list

### this is the main SLR call: our most powerful color-color diagram is VR-RI - make sure this is used first!
if [ ${SVpres} -eq 1 ] &&  [ ${SRpres} -eq 1 ] && [ ${SIpres} -eq 1 ]; then
  if  [ ${Szpres} -eq 1 ]; then
    {
    echo "slr_pipe, force=1, colors2calibrate=['VR','RI','Rz'], write_ctab=1, kappa_fix=[0,0,0],kappa_guess=[0,0,0],kappa_guess_err=[0,0,0],kappa_guess_range=[1,1,1],colorterms=[-0.03],colortermbands=['z'],colormult=['Rz'],snlow=10,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
    kappaRz=`grep 'kappa Rz (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaRzerr=`grep 'kappa Rz uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPz=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRz}'}'`
    awk '{if($1=="z") print $0, '${ZPz}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
  else
    {
    echo "slr_pipe, force=1, colors2calibrate=['VR','RI'], write_ctab=1, kappa_fix=[0,0],kappa_guess=[0,0],kappa_guess_err=[0,0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=10,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
  fi

### the kappa values are simply:  kappa_VR = V - R = ZP_V - ZP_R

kappaVR=`grep 'kappa VR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
kappaVRerr=`grep 'kappa VR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
ZPV=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaVR}'}'`
awk '{if($1=="V") print $0, '${ZPV}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list

kappaRI=`grep 'kappa RI (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
kappaRIerr=`grep 'kappa RI uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
ZPI=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRI}'}'`
awk '{if($1=="I") print $0, '${ZPI}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list

else
    echo "VRI not present."
    exit 2
fi


### note that B was not included in the first SLR call: currently, SLR requires stars to be present in all bands it
### fits on. too many stars are not detected in B, hence we run it separately. note that kappa_VR is fixed now!

if  [ ${SBpres} -eq 1 ]; then
  {
  echo "slr_pipe, force=1, colors2calibrate=['BR','VR'], write_ctab=1, kappa_fix=[0,1],kappa_guess=[0,${kappaVR}],kappa_guess_err=[0,${kappaVRerr}],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=10,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
  } | ${P_IDL}
  
  kappaBR=`grep 'kappa BR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
  kappaBRerr=`grep 'kappa BR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
  ZPB=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaBR}'}'`
  awk '{if($1=="B") print $0, '${ZPB}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
  mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
fi

if  [ ${Mupres} -eq 1 ]; then
  {
  echo "slr_pipe, force=1, colors2calibrate=['uR','VR'], write_ctab=1, kappa_fix=[0,1],kappa_guess=[0,${kappaVR}],kappa_guess_err=[0,${kappaVRerr}],kappa_guess_range=[1,1],colorterms=[-0.116],colortermbands=['u'],colormult=['uR'],snlow=10,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
  } | ${P_IDL}
  
  kappauR=`grep 'kappa uR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
  kappauRerr=`grep 'kappa uR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
  ZPu=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappauR}'}'`
  awk '{if($1=="u") print $0, '${ZPu}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
  mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
fi

if  [ ${WKpres} -eq 1 ]; then
  {
  echo "slr_pipe, force=1, colors2calibrate=['RK','RI'], write_ctab=1, kappa_fix=[0,1],kappa_guess=[0,${kappaRI}],kappa_guess_err=[0,${kappaRIerr}],kappa_guess_range=[1,1],colorterms=[0.0019],colortermbands=['K'],colormult=['RK'],snlow=10,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
  } | ${P_IDL}
  
  kappaRK=`grep 'kappa RK (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
  kappaRKerr=`grep 'kappa RK uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
  ZPK=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRK}'}'`
  awk '{if($1=="K") print $0, '${ZPK}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
  mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
fi

exit 0;

ZPR=0
ZPu=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappauR}'}'`
ZPB=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaBR}'}'`
ZPV=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaVR}'}'`
ZPI=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRI}'}'`
ZPz=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRz}'}'`
ZPK=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRK}'}'`

