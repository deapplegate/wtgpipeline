#! /bin/bash -xv

# $1: main dir
# $2: star catalog
# $3: Mag name (ISO, APER1, etc)

. progs.ini > /tmp/progs.out 2>&1

MAINDIR=$1
STARCAT=$2
MAGTYPE=$3


export IDLUTILS_DIR=/nfs/slac/g/ki/ki04/pkelly/idlutils
export IDL_PATH=+$IDLUTILS_DIR/pro:+$IDLUTILS_DIR/goddard/pro:${IDL_PATH}
export IDL_PATH=+/nfs/slac/g/ki/ki06/anja/software/slr/pro:${IDL_PATH}
export SLR_INSTALL=/nfs/slac/g/ki/ki06/anja/software/slr
export SLR_DATA=/nfs/slac/g/ki/ki06/anja/software/slr/example_data


#old#./dump_cat_filters.py ${MAINDIR}/${STARCAT} | awk '($1 !~ /COADD/){print}' > filters.raw.list_$$
./dump_cat_filters.py -a ${MAINDIR}/${STARCAT} | awk '($1 !~ /COADD/){print}' > filters.raw.list_$$

rm -f filters.wc.list_$$
while read filterlong
do
  nobj=`./ldactoasc.py -i ${MAINDIR}/${STARCAT} -t OBJECTS MAG_${MAGTYPE}-${filterlong} | awk '{if($1>-90) print $0}' | wc | awk '{print $1}'`
  echo ${filterlong} ${nobj} >> filters.wc.list_$$ 
done < filters.raw.list_$$

rm -f filters.list_$$

for filter in W-J-B W-J-V W-C-RC W-C-IC W-S-I+ W-S-Z+ u g r i z K WHT-0-1-U WHT-0-1-B
do
  awk 'BEGIN{
         nmax=0
         while (getline <"filters.wc.list_'$$'" > 0)
         {
           if($1~"'${filter}'" && $2>nmax)
           {
             out=$1
             nmax=$2
           }
         }
         if(nmax>0) print out
       }
       ' >> filters.list_$$
done

for filter in B
do
  awk 'BEGIN{
         nmax=0
         while (getline <"filters.wc.list_'$$'" > 0)
         {
           if($1~"SPECIAL" && $1~"'${filter}'" && $2>nmax)
           {
             out=$1
             nmax=$2
           }
         }
         if(nmax>0) print out
       }
       ' >> filters.list_$$
done

outline="ALPHA_J2000 DELTA_J2000"
outheader="# ID type tmixed RA Dec "

rm -f ${MAINDIR}/slr.offsets.list
nfilt=0
nK=1000

Mupres=0
Mgpres=0
Mrpres=0
Mipres=0
Mzpres=0
SBpres=0
SVpres=0
SRpres=0
SIpres=0
Sipres=0
Szpres=0
WKpres=0
WUpres=0
WBpres=0
CBpres=0

while read filterlong
do
    instrum=`echo ${filterlong} | awk 'BEGIN{FS="-"}{print $1}'`
    config=`echo ${filterlong} | awk 'BEGIN{FS="-"}{print $2}'`
    chiptype=`echo ${filterlong} | awk 'BEGIN{FS="-"}{print $3}'`

    if [ ${instrum} == "SUBARU" ]; then
	filter=`echo ${filterlong} | awk 'BEGIN{FS="-"}{print $4"-"$5"-"$6}'`
    elif [ ${instrum} == "WHT" ]; then
	filter=`echo ${filterlong} | awk 'BEGIN{FS="-"}{print "WHT"$4}'`
    elif [ ${instrum} == "SPECIAL" ]; then
	filter=`echo ${filterlong} | awk 'BEGIN{FS="-"}{print "CFH"$4}'`
    else
	filter=`echo ${filterlong} | awk 'BEGIN{FS="-"}{print $4}'`
    fi

    case ${filter} in
        "B" | "I" )
    	shortfilt=${filter};;
        "u" )
    	shortfilt="MPu"
	Mupres=1;;
        "g" )
    	shortfilt="MPg"
	Mgpres=1;;
        "r" )
    	shortfilt="MPr"
	Mrpres=1;;
        "i" )
    	shortfilt="MPi"
	Mipres=1;;
        "z" )
    	shortfilt="MPz"
	Mzpres=1;;
        "K" )
    	shortfilt="WK"
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
        "W-S-I+" )
    	shortfilt="WSI"
	Sipres=1;;
        "W-S-Z+" )
    	shortfilt="WSZ"
	Szpres=1;;
        "WHTU" )
    	shortfilt="WHTU"
	WUpres=1;;
        "WHTB" )
    	shortfilt="WHTB"
	WBpres=1;;
        "CFHB" )
    	shortfilt="CFHB"
	CBpres=1;;
    esac

    ### NOTE!!!!
    ### this still needs to be fixed:
    ### currently, it would output more than one column if there is data from several configurations
    ### if the colorterms between chips are small enough, it's probably best to concatenate all of them


    if [ "${filterlong}" == "SPECIAL-0-1-K" ]; then
	outline="${outline} MAG_${MAGTYPE}-${filterlong} MAGERR_${MAGTYPE}-${filterlong}"
	outheader="${outheader} ${shortfilt} ${shortfilt}_err"
	echo ${shortfilt} ${filterlong} >> ${MAINDIR}/slr.offsets.list
	nfilt=$(($nfilt+1))
	nK=$nfilt
    else
	outline="${outline} MAG_${MAGTYPE}-${filterlong} MAGERR_${MAGTYPE}-${filterlong}"
	outheader="${outheader} ${shortfilt} ${shortfilt}_err"
	echo ${shortfilt} ${filterlong} >> ${MAINDIR}/slr.offsets.list
	nfilt=$(($nfilt+1))
    fi

echo ${outline}

done < filters.list_$$
rm -f filters.list_$$ filters.wc.list_$$ filters.raw.list_$$

echo ${outheader} > ${MAINDIR}/stars_4slr.ctab

${P_LDACTOASC} -i ${MAINDIR}/${STARCAT} \
               -t OBJECTS \
               -b -k SeqNr \
	       | awk '{printf "%5i 1 0\n", $1}' \
               > ${TEMPDIR}/tmp_stars_1_$$.dat

./ldactoasc.py -i ${MAINDIR}/${STARCAT} \
               -t OBJECTS \
               ${outline} \
	       | awk '{for(n=1;n<=NF;n++){if($n==0 || $n==-99 || $n=="inf" || $n=="nan") printf "           -"; else if(n==(2+(2*'${nK}'-1))){if($n>1 && $(n+1)>0) printf " % 11.9g", $n-1.837; else printf "           -"} else printf " % 11.9g", $n}; printf "\n"}' \
               > ${TEMPDIR}/tmp_stars_2_$$.dat

paste ${TEMPDIR}/tmp_stars_1_$$.dat ${TEMPDIR}/tmp_stars_2_$$.dat >> ${MAINDIR}/stars_4slr.ctab


cd ${MAINDIR}

export SLR_COLORTABLE_IN=stars_4slr.ctab
export SLR_COLORTABLE_OUT=test.dat

### SLR really likes environment variables, btw...
### the SDSS --> Johnson color terms are defined in
###  /nfs/slac/g/ki/ki06/anja/software/slr/pro/io/slr_read_covey_median_locus.pro 
### from line 221

if [ ${SRpres} -eq 1 ]; then
  
  ZPR=0
  awk '{if($1=="R") print $0, '${ZPR}', "0"; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
  mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
  SRpres=2
  
  ### this is the main SLR call: our most powerful color-color diagram is VR-RI - make sure this is used first!
  if [ ${SVpres} -eq 1 ] && [ ${SIpres} -eq 1 ]; then
    if  [ ${Szpres} -eq 1 ]; then
      {
      echo "slr_pipe, force=1, colors2calibrate=['VR','RI','R-WSZ'], write_ctab=1, kappa_fix=[0,0,0],kappa_guess=[0,0,0],kappa_guess_err=[0,0,0],kappa_guess_range=[1,1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
  
      kappaRz=`grep 'kappa RWSZ (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
      kappaRzerr=`grep 'kappa RWSZ uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
      ZPz=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRz}'}'`
      awk '{if($1=="WSZ" && $2~"SUBARU") print $0, '${ZPz}', '${kappaRzerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
      mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
      SZpres=2
    else
      {
      echo "slr_pipe, force=1, colors2calibrate=['VR','RI'], write_ctab=1, kappa_fix=[0,0],kappa_guess=[0,0],kappa_guess_err=[0,0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
    fi
  
    ### the kappa values are simply:  kappa_VR = V - R = ZP_V - ZP_R
    
    kappaVR=`grep 'kappa VR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaVRerr=`grep 'kappa VR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPV=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaVR}'}'`
    awk '{if($1=="V") print $0, '${ZPV}', '${kappaVRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    SVpres=2
    
    kappaRI=`grep 'kappa RI (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaRIerr=`grep 'kappa RI uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPI=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRI}'}'`
    awk '{if($1=="I") print $0, '${ZPI}', '${kappaRIerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    SIpres=2
  
  elif [ ${SVpres} -eq 1 ] && [ ${Sipres} -eq 1 ]; then
  
    if  [ ${Szpres} -eq 1 ]; then
      {
      echo "slr_pipe, force=1, colors2calibrate=['VR','R-WSI','R-WSZ'], write_ctab=1, kappa_fix=[0,0,0],kappa_guess=[0,0,0],kappa_guess_err=[0,0,0],kappa_guess_range=[1,1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
  
      kappaRz=`grep 'kappa RWSZ (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
      kappaRzerr=`grep 'kappa RWSZ uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
      ZPz=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRz}'}'`
      awk '{if($1=="WSZ" && $2~"SUBARU") print $0, '${ZPz}', '${kappaRzerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
      mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
      Szpres=2
    else
      {
      echo "slr_pipe, force=1, colors2calibrate=['VR','R-WSI'], write_ctab=1, kappa_fix=[0,0],kappa_guess=[0,0],kappa_guess_err=[0,0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
    fi
  
    ### the kappa values are simply:  kappa_VR = V - R = ZP_V - ZP_R
    
    kappaVR=`grep 'kappa VR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaVRerr=`grep 'kappa VR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPV=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaVR}'}'`
    awk '{if($1=="V") print $0, '${ZPV}', '${kappaVRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    SVpres=2
    
    kappaRi=`grep 'kappa RWSI (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaRierr=`grep 'kappa RWSI uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPi=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRi}'}'`
    awk '{if($1=="WSI") print $0, '${ZPi}', '${kappaRierr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    Sipres=2
  
  elif [ ${SVpres} -eq 1 ] && [ ${Szpres} -eq 1 ]; then
  
    {
    echo "slr_pipe, force=1, colors2calibrate=['VR','R-WSZ'], write_ctab=1, kappa_fix=[0,0],kappa_guess=[0,0],kappa_guess_err=[0,0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
  
    kappaVR=`grep 'kappa VR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaVRerr=`grep 'kappa VR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPV=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaVR}'}'`
    awk '{if($1=="V") print $0, '${ZPV}', '${kappaVRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    SVpres=2
    
    kappaRz=`grep 'kappa RWSZ (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaRzerr=`grep 'kappa RWSZ uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPz=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRz}'}'`
    awk '{if($1=="WSZ") print $0, '${ZPz}', '${kappaRzerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    Szpres=2
  
  elif [ ${SBpres} -eq 1 ] && [ ${SVpres} -eq 1 ]; then
  
    {
    echo "slr_pipe, force=1, colors2calibrate=['VR','BR'], write_ctab=1, kappa_fix=[0,0],kappa_guess=[0,0],kappa_guess_err=[0,0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
  
    kappaVR=`grep 'kappa VR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaVRerr=`grep 'kappa VR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPV=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaVR}'}'`
    awk '{if($1=="V") print $0, '${ZPV}', '${kappaVRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    SVpres=2
  
    kappaBR=`grep 'kappa BR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaBRerr=`grep 'kappa BR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPB=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaBR}'}'`
    awk '{if($1=="B") print $0, '${ZPB}', '${kappaBRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    SBpres=2
  
  elif [ ${SBpres} -eq 1 ] && [ ${SIpres} -eq 1 ]; then
  
    if  [ ${Szpres} -eq 1 ]; then
      {
      echo "slr_pipe, force=1, colors2calibrate=['BR','RI','R-WSZ'], write_ctab=1, kappa_fix=[0,0,0],kappa_guess=[0,0,0],kappa_guess_err=[0,0,0],kappa_guess_range=[1,1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
  
      kappaRz=`grep 'kappa RWSZ (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
      kappaRzerr=`grep 'kappa RWSZ uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
      ZPz=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRz}'}'`
      awk '{if($1=="WSZ" && $2~"SUBARU") print $0, '${ZPz}', '${kappaRzerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
      mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
      Szpres=2
    else
      {
      echo "slr_pipe, force=1, colors2calibrate=['BR','RI'], write_ctab=1, kappa_fix=[0,0],kappa_guess=[0,0],kappa_guess_err=[0,0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
    fi
  
    kappaBR=`grep 'kappa BR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaBRerr=`grep 'kappa BR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPB=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaBR}'}'`
    awk '{if($1=="B") print $0, '${ZPB}', '${kappaBRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    SBpres=2
  
    kappaRI=`grep 'kappa RI (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaRIerr=`grep 'kappa RI uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPI=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRI}'}'`
    awk '{if($1=="I") print $0, '${ZPI}', '${kappaRIerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    SIpres=2
  
  elif [ ${SBpres} -eq 1 ] && [ ${Sipres} -eq 1 ]; then
  
    if  [ ${Szpres} -eq 1 ]; then
      {
      echo "slr_pipe, force=1, colors2calibrate=['BR','R-WSI','R-WSZ'], write_ctab=1, kappa_fix=[0,0,0],kappa_guess=[0,0,0],kappa_guess_err=[0,0,0],kappa_guess_range=[1,1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
  
      kappaRz=`grep 'kappa RWSZ (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
      kappaRzerr=`grep 'kappa RWSZ uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
      ZPz=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRz}'}'`
      awk '{if($1=="WSZ" && $2~"SUBARU") print $0, '${ZPz}', '${kappaRzerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
      mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
      Szpres=2
    else
      {
      echo "slr_pipe, force=1, colors2calibrate=['BR','R-WSI'], write_ctab=1, kappa_fix=[0,0],kappa_guess=[0,0],kappa_guess_err=[0,0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
    fi
  
    kappaBR=`grep 'kappa BR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaBRerr=`grep 'kappa BR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPB=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaBR}'}'`
    awk '{if($1=="B") print $0, '${ZPB}', '${kappaBRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    SBpres=2
  
    kappaRi=`grep 'kappa RWSI (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaRierr=`grep 'kappa RWSI uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPi=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRi}'}'`
    awk '{if($1=="WSI") print $0, '${ZPi}', '${kappaRierr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    Sipres=2
  
  elif [ ${SBpres} -eq 1 ] && [ ${Szpres} -eq 1 ]; then
  
    {
    echo "slr_pipe, force=1, colors2calibrate=['BR','R-WSZ'], write_ctab=1, kappa_fix=[0,0],kappa_guess=[0,0],kappa_guess_err=[0,0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
  
    kappaBR=`grep 'kappa BR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaBRerr=`grep 'kappa BR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPB=`awk 'BEGIN{print '${ZPB}'-1.0*'${kappaBR}'}'`
    awk '{if($1=="B") print $0, '${ZPB}', '${kappaBRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    SBpres=2
  
    kappaRz=`grep 'kappa RWSZ (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaRzerr=`grep 'kappa RWSZ uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPz=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRz}'}'`
    awk '{if($1=="WSZ" && $2~"SUBARU") print $0, '${ZPz}', '${kappaRzerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    Szpres=2

  elif [ ${Mgpres} -eq 1 ] && [ ${Mrpres} -eq 1 ]; then

    {
    echo "slr_pipe, force=1, colors2calibrate=['MPg-R','R-MPr'], write_ctab=1, kappa_fix=[0,0],kappa_guess=[0,0],kappa_guess_err=[0,0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
    
    kappagR=`grep 'kappa MPgR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappagRerr=`grep 'kappa MPgR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPg=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappagR}'}'`
    awk '{if($1=="MPg") print $0, '${ZPg}', '${kappagRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    Mgpres=2
    
    kappaRr=`grep 'kappa RMPr (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaRrerr=`grep 'kappa RMPr uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPr=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRr}'}'`
    awk '{if($1=="MPr") print $0, '${ZPr}', '${kappaRrerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    Mrpres=2

  else
      echo "none of VRI, VRi, VRz, BVR, BRI, BRi, Rri present."
      exit 2
  fi
  
  
  ### note that B was not included in the first SLR call: currently, SLR requires stars to be present in all bands it
  ### fits on. too many stars are not detected in B, hence we run it separately. note that kappa_VR is fixed now!
  
  if  [ ${SBpres} -eq 1 ]; then
    {
    echo "slr_pipe, force=1, colors2calibrate=['BR','VR'], write_ctab=1, kappa_fix=[0,1],kappa_guess=[0,${kappaVR}],kappa_guess_err=[0,${kappaVRerr}],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
  
    kappaBR=`grep 'kappa BR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaBRerr=`grep 'kappa BR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPB=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaBR}'}'`
    awk '{if($1=="B") print $0, '${ZPB}', '${kappaBRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    SBpres=2
  fi
  
  
  if  [ ${Mupres} -eq 1 ]; then

    if [ ${SVpres} -eq 2 ]; then
      {
      echo "slr_pipe, force=1, colors2calibrate=['VR','MPu-R'], write_ctab=1, kappa_fix=[1,0],kappa_guess=[${kappaVR},0],kappa_guess_err=[${kappaVRerr},0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
      
      kappauR=`grep 'kappa MPuR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
      kappauRerr=`grep 'kappa MPuR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
      ZPu=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappauR}'}'`
      awk '{if($1=="MPu" && $2~"MEGAPRIME") print $0, '${ZPu}', '${kappauRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
      mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
      Mupres=2
    elif [ ${SBpres} -eq 2 ]; then
      {
      echo "slr_pipe, force=1, colors2calibrate=['BR','MPu-R'], write_ctab=1, kappa_fix=[1,0],kappa_guess=[${kappaBR},0],kappa_guess_err=[${kappaBRerr},0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
      
      kappauR=`grep 'kappa MPuR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
      kappauRerr=`grep 'kappa MPuR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
      ZPu=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappauR}'}'`
      awk '{if($1=="MPu" && $2~"MEGAPRIME") print $0, '${ZPu}', '${kappauRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
      mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
      Mupres=2
    else
      echo "cannot calibrate MPu"
      exit 2
    fi
  fi
  
  
  if  [ ${Mgpres} -eq 1 ] ; then
  
   if [ ${SIpres} -eq 2 ]; then      
     {
     echo "slr_pipe, force=1, colors2calibrate=['MPg-R','RI'], write_ctab=1, kappa_fix=[0,1],kappa_guess=[0,${kappaRI}],kappa_guess_err=[0,${kappaRIerr}],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
     } | ${P_IDL}
   elif [ ${Sipres} -eq 2 ]; then
     {
     echo "slr_pipe, force=1, colors2calibrate=['MPg-R','R-WSI'], write_ctab=1, kappa_fix=[0,1],kappa_guess=[0,${kappaRi}],kappa_guess_err=[0,${kappaRierr}],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
     } | ${P_IDL}
   elif [ ${Szpres} -eq 2 ]; then
     {
     echo "slr_pipe, force=1, colors2calibrate=['MPg-R','R-WSZ'], write_ctab=1, kappa_fix=[0,1],kappa_guess=[0,${kappaRz}],kappa_guess_err=[0,${kappaRzerr}],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
     } | ${P_IDL}
   elif [ ${SVpres} -eq 2 ]; then
      {
      echo "slr_pipe, force=1, colors2calibrate=['MPg-R','VR'], write_ctab=1, kappa_fix=[0,1],kappa_guess=[0,${kappaVR}],kappa_guess_err=[0,${kappaVRerr}],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL} 
   else
     echo "Can't calibrate MPg."
     exit 2
   fi
   kappagR=`grep 'kappa MPgR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
   kappagRerr=`grep 'kappa MPgR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
   ZPg=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappagR}'}'`
   awk '{if($1=="MPg" && $2~"MEGAPRIME") print $0, '${ZPg}', '${kappagRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
   mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
   Mgpres=2

  fi
  
  
  if  [ ${WKpres} -eq 1 ]; then
    {
    echo "slr_pipe, force=1, colors2calibrate=['R-WK','RI'], write_ctab=1, kappa_fix=[0,1],kappa_guess=[0,${kappaRI}],kappa_guess_err=[0,${kappaRIerr}],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
    
    kappaRK=`grep 'kappa RWK (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaRKerr=`grep 'kappa RWK uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPK=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRK}'}'`
    awk '{if($1=="WK") print $0, '${ZPK}', '${kappaRKerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    WKpres=2
  fi
  
  
  if  [ ${Sipres} -eq 1 ] && [ ${SIpres} -eq 2 ]; then
    if [ ${SVpres} -eq 2 ]; then
      {
      echo "slr_pipe, force=1, colors2calibrate=['VR','R-WSI'], write_ctab=1, kappa_fix=[1,0],kappa_guess=[${kappaVR},0],kappa_guess_err=[${kappaVRerr},0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
      
      kappaRi=`grep 'kappa RWSI (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
      kappaRierr=`grep 'kappa RWSI uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
      ZPi=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRi}'}'`
      awk '{if($1=="WSI" && $2~"SUBARU") print $0, '${ZPi}', '${kappaRierr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
      mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    elif [ ${SBpres} -eq 2 ]; then
      {
      echo "slr_pipe, force=1, colors2calibrate=['BR','R-WSI'], write_ctab=1, kappa_fix=[1,0],kappa_guess=[${kappaBR},0],kappa_guess_err=[${kappaBRerr},0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
      
      kappaRi=`grep 'kappa RWSI (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
      kappaRierr=`grep 'kappa RWSI uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
      ZPi=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRi}'}'`
      awk '{if($1=="WSI" && $2~"SUBARU") print $0, '${ZPi}', '${kappaRierr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
      mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    else
      echo "Cannot calibrate W-S-I+"
      exit 2
    fi
    Sipres=2
  fi
  
  
  if  [ ${Mzpres} -eq 1 ]; then
    {
    echo "slr_pipe, force=1, colors2calibrate=['RI','R-MPz'], write_ctab=1, kappa_fix=[1,0],kappa_guess=[${kappaRI},0],kappa_guess_err=[${kappaRIerr},0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
  
    kappaRz=`grep 'kappa RMPz (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaRzerr=`grep 'kappa RMPz uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPz=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRz}'}'`
    awk '{if($1=="MPz" && $2~"MEGAPRIME") print $0, '${ZPz}', '${kappaRzerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    Mzpres=2
  fi

  if [ ${Mrpres} -eq 1 ]; then
  
    if [ ${Mgpres} -eq 2 ] && [[ ${SVpres} -eq 2 || ${SBpres} -eq 2 ]]; then
      if [ ${SVpres} -eq 2 ]; then
        {
        echo "slr_pipe, force=1, colors2calibrate=['MPg-R','V-MPr'], write_ctab=1, kappa_fix=[1,0],kappa_guess=[${kappagR},0],kappa_guess_err=[${kappagRerr},0],kappa_guess_range=[1,1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
        } | ${P_IDL}
        
        kappaVr=`grep 'kappa VMPr (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
        kappaVrerr=`grep 'kappa VMPr uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
        ZPr=`awk 'BEGIN{print '${ZPV}'+1.0*'${kappaVr}'}'`
        awk '{if($1=="MPr" && $2~"MEGAPRIME") print $0, '${ZPr}', '${kappaVrerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
        mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
      elif [ ${SBpres} -eq 2 ]; then
        {
        echo "slr_pipe, force=1, colors2calibrate=['MPg-R','B-MPr'], write_ctab=1, kappa_fix=[1,0],kappa_guess=[${kappagR},0],kappa_guess_err=[${kappagRerr},0],kappa_guess_range=[1,1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
        } | ${P_IDL}
        
        kappaBr=`grep 'kappa BMPr (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
        kappaBrerr=`grep 'kappa BMPr uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
        ZPr=`awk 'BEGIN{print '${ZPB}'+1.0*'${kappaBr}'}'`
        awk '{if($1=="MPr" && $2~"MEGAPRIME") print $0, '${ZPr}', '${kappaBrerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
        mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
      fi
    else
      echo "cannot calibrate Mr"
      exit 2
    fi
    Mrpres=2
  fi
  
  
  if [ ${Mipres} -eq 1 ]; then
    if [ ${SVpres} -eq 2 ]; then
      {
      echo "slr_pipe, force=1, colors2calibrate=['V-R','R-MPi'], write_ctab=1, kappa_fix=[1,0],kappa_guess=[${kappaVR},0],kappa_guess_err=[${kappaVRerr},0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
      
      kappaRi=`grep 'kappa RMPi (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
      kappaRierr=`grep 'kappa RMPi uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
      ZPi=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRi}'}'`
      awk '{if($1=="MPi" && $2~"MEGAPRIME") print $0, '${ZPi}', '${kappaRierr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
      mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
      Mipres=2
    elif [ ${Mgpres} -eq 2 ]; then
      {
      echo "slr_pipe, force=1, colors2calibrate=['MPg-R','R-MPi'], write_ctab=1, kappa_fix=[1,0],kappa_guess=[${kappagR},0],kappa_guess_err=[${kappagRerr},0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
      
      kappaRi=`grep 'kappa RMPi (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
      kappaRierr=`grep 'kappa RMPi uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
      ZPi=`awk 'BEGIN{print '${ZPR}'+1.0*'${kappaRi}'}'`
      awk '{if($1=="MPi" && $2~"MEGAPRIME") print $0, '${ZPi}', '${kappaRierr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
      mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
      Mipres=2
    else
      echo "cannot calibrate MPi"
      exit 0
    fi
  fi
  
  if  [ ${WUpres} -eq 1 ]; then
    {
    echo "slr_pipe, force=1, colors2calibrate=['VR','WHTU-R'], write_ctab=1, kappa_fix=[1,0],kappa_guess=[${kappaVR},0],kappa_guess_err=[${kappaVRerr},0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
  
    kappaUR=`grep 'kappa WHTUR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaURerr=`grep 'kappa WHTUR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPU=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaUR}'}'`
    awk '{if($1=="WHTU" && $2~"WHT") print $0, '${ZPU}', '${kappaURerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    WUpres=2
  fi
  
  if  [ ${WBpres} -eq 1 ]; then
    {
    echo "slr_pipe, force=1, colors2calibrate=['VR','WHTB-R'], write_ctab=1, kappa_fix=[1,0],kappa_guess=[${kappaVR},0],kappa_guess_err=[${kappaVRerr},0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
  
    kappaBR=`grep 'kappa WHTBR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaBRerr=`grep 'kappa WHTBR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPB=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaBR}'}'`
    awk '{if($1=="WHTB" && $2~"WHT") print $0, '${ZPB}', '${kappaBRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    WBpres=2
  fi
  
  if  [ ${CBpres} -eq 1 ]; then
    {
    echo "slr_pipe, force=1, colors2calibrate=['VR','CFHB-R'], write_ctab=1, kappa_fix=[1,0],kappa_guess=[${kappaVR},0],kappa_guess_err=[${kappaVRerr},0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
  
    kappaBR=`grep 'kappa CFHBR (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaBRerr=`grep 'kappa CFHBR uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPB=`awk 'BEGIN{print '${ZPR}'-1.0*'${kappaBR}'}'`
    awk '{if($1=="CFHB" && $2~"SPECIAL") print $0, '${ZPB}', '${kappaBRerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    CBpres=2
  fi

#####################################################################
elif [ ${Mrpres} -eq 1 ] && [ ${Mgpres} -eq 1 ]; then

  ZPr=0
  awk '{if($1=="MPr") print $0, '${ZPr}', "0"; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
  mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list

  if [ ${Sipres} -eq 1 ]; then

    {
    echo "slr_pipe, force=1, colors2calibrate=['MPg-MPr','MPr-WSI'], write_ctab=1, kappa_fix=[0,0],kappa_guess=[0,0],kappa_guess_err=[0,0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
    
    kappagr=`grep 'kappa MPgMPr (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappagrerr=`grep 'kappa MPgMPr uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPg=`awk 'BEGIN{print '${ZPr}'-1.0*'${kappagr}'}'`
    awk '{if($1=="MPg") print $0, '${ZPg}', '${kappagrerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    Mgpres=2
    
    kappari=`grep 'kappa MPrWSI (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kapparierr=`grep 'kappa MPrWSI uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPi=`awk 'BEGIN{print '${ZPr}'+1.0*'${kappari}'}'`
    awk '{if($1=="WSI") print $0, '${ZPi}', '${kapparierr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    Sipres=2

  elif [ ${Mipres} -eq 1 ] && [ ${Mzpres} -eq 1 ]; then

    if  [ ${Mzpres} -eq 1 ]; then
      {
      echo "slr_pipe, force=1, colors2calibrate=['MPg-MPr','MPr-MPi','MPr-MPr'], write_ctab=1, kappa_fix=[0,0,0],kappa_guess=[0,0,0],kappa_guess_err=[0,0,0],kappa_guess_range=[1,1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
  
      kapparz=`grep 'kappa MPrMPz (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
      kapparzerr=`grep 'kappa MPzMPz uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
      ZPz=`awk 'BEGIN{print '${ZPr}'+1.0*'${kapparz}'}'`
      awk '{if($1=="MPz") print $0, '${ZPz}', '${kapparzerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
      mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
      Mzpres=2
    else
      {
      echo "slr_pipe, force=1, colors2calibrate=['MPg-MPr','MPr-MPi'], write_ctab=1, kappa_fix=[0,0],kappa_guess=[0,0],kappa_guess_err=[0,0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
      } | ${P_IDL}
    fi
    
    kappagr=`grep 'kappa MPgMPr (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappagrerr=`grep 'kappa MPgMPr uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPg=`awk 'BEGIN{print '${ZPr}'-1.0*'${kappagr}'}'`
    awk '{if($1=="MPg") print $0, '${ZPg}', '${kappagrerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    Mgpres=2
    
    kappari=`grep 'kappa MPrMPi (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kapparierr=`grep 'kappa MPrMPi uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPi=`awk 'BEGIN{print '${ZPr}'+1.0*'${kappari}'}'`
    awk '{if($1=="MPi") print $0, '${ZPi}', '${kapparierr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    Mipres=2

  elif [ ${SVpres} -eq 1 ]; then

    {
    echo "slr_pipe, force=1, colors2calibrate=['MPg-MPr','V-MPr'], write_ctab=1, kappa_fix=[0,0],kappa_guess=[0,0],kappa_guess_err=[0,0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}

    kappagr=`grep 'kappa MPgMPr (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappagrerr=`grep 'kappa MPgMPr uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPg=`awk 'BEGIN{print '${ZPr}'-1.0*'${kappagr}'}'`
    awk '{if($1=="MPg") print $0, '${ZPg}', '${kappagrerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    Mgpres=2

    kappaVr=`grep 'kappa VMPr (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaVrerr=`grep 'kappa VMPr uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPV=`awk 'BEGIN{print '${ZPr}'-1.0*'${kappaVr}'}'`
    awk '{if($1=="V") print $0, '${ZPV}', '${kappaVrerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    SVpres=2
  fi

  if [ ${SVpres} -eq 1 ]; then
    {
    echo "slr_pipe, force=1, colors2calibrate=['V-MPr','MPg-MPr'], write_ctab=1, kappa_fix=[0,1],kappa_guess=[0,${kappagr}],kappa_guess_err=[0,${kappagrerr}],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
    kappaVr=`grep 'kappa VMPr (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kappaVrerr=`grep 'kappa VMPr uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPV=`awk 'BEGIN{print '${ZPr}'-1.0*'${kappaVr}'}'`
    awk '{if($1=="V") print $0, '${ZPV}', '${kappaVrerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    SVpres=2
  fi

  if [ ${SIpres} -eq 1 ]; then
    {
    echo "slr_pipe, force=1, colors2calibrate=['MPg-MPr','MPr-I'], write_ctab=1, kappa_fix=[1,0],kappa_guess=[${kappagr},0],kappa_guess_err=[${kappagrerr},0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
    } | ${P_IDL}
    kapparI=`grep 'kappa MPrI (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
    kapparIerr=`grep 'kappa MPrI uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
    ZPI=`awk 'BEGIN{print '${ZPr}'+1.0*'${kapparI}'}'`
    awk '{if($1=="I") print $0, '${ZPI}', '${kapparIerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
    mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list
    SIpres=2
  fi

elif [ ${SBpres} -eq 1 ] && [ ${SVpres} -eq 1 ] && [ ${Sipres} -eq 1 ]; then

  ZPV=0
  awk '{if($1=="V") print $0, '${ZPV}', "0"; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
  mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list

  {
  echo "slr_pipe, force=1, colors2calibrate=['BV','V-WSI'], write_ctab=1, kappa_fix=[0,0],kappa_guess=[0,0],kappa_guess_err=[0,0],kappa_guess_range=[1,1],colorterms=colorterms,colortermbands=none,colormult=none,snlow=1,kappa_out=kappa1_out,kappa_err_out=kappa1_err_out,interactive=0"
  } | ${P_IDL}

  kappaBV=`grep 'kappa BV (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
  kappaBVerr=`grep 'kappa BV uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
  ZPB=`awk 'BEGIN{print '${ZPV}'-1.0*'${kappaBV}'}'`
  awk '{if($1=="B") print $0, '${ZPB}', '${kappaBVerr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
  mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list

  kappaVi=`grep 'kappa VWSI (free)' stars_4slr.slr | awk '{k=$4}END{print k}'`
  kappaVierr=`grep 'kappa VWSI uncertainty' stars_4slr.slr | awk '{k=$4}END{print k}'`
  ZPi=`awk 'BEGIN{print '${ZPV}'+1.0*'${kappaVi}'}'`
  awk '{if($1=="WSI") print $0, '${ZPi}', '${kappaVierr}'; else print $0}' ${MAINDIR}/slr.offsets.list > ${MAINDIR}/slr.offsets.list.tmp
  mv ${MAINDIR}/slr.offsets.list.tmp ${MAINDIR}/slr.offsets.list

else
  echo "unknown filter combination"
  exit 2
fi


  
if [ -s "${MAINDIR}/slr.offsets.list" ]; then
    prob=`awk 'BEGIN{prob=0}{if($3=="") prob++}END{print prob}' slr.offsets.list`
    if [ ${prob} -gt 0 ]; then
       echo "Not all filters calibrated!!!"
       exit 2
    else
      exit 0
    fi
else
    echo "${MAINDIR}/slr.offsets.list is empty,"
    echo "there must have been a problem with SLR."
    exit 2
fi
