#!/bin/bash
set -xv

#################################

cluster=$1
filter=$2    # lensing band
photozcat=$3
photozcattype=BPZ # "BPZ" or "LePhare"

IMAGE=coadd

shear_cut="1.0"
rh_cut_mult="1.15"
snrcut="3.0"

#################################

. progs.ini

reddir=`pwd`
export LENSCONF=${reddir}/lensconf

subarudir=/gpfs/slac/kipac/fs1/u/awright/SUBARU
LENSDIR=$subarudir/$cluster/LENSING
PHOTDIR=$subarudir/$cluster/PHOTOMETRY

#if [ ! -e ${PHOTDIR}/${photozcat} ]; then
#    echo "PHOTOZ File Doesn't Exist!"
#    exit 1
#fi
#
touch ${LENSDIR}/.test_$$
if [ ! -e ${LENSDIR}/.test_$$ ]; then
    echo "Cannot Write to Lensing Directory!"
    exit 1
fi
rm -f ${LENSDIR}/.test_$$

lensingimage=${subarudir}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_good/${IMAGE}.fits

redshift=`grep ${cluster} ${subarudir}/clusters.redshifts | awk '{print $2}'`
zcut=`awk 'BEGIN{print '${redshift}'*1.1}'`

if [ ! -f ${LENSDIR}/${IMAGE}_anisocorr.cat ]; then
    echo "${LENSDIR}/${IMAGE}_anisocorr.cat not present"
    exit 2
fi

#### measures and applies Pg corrections
#./measure_shear.sh ${lensingimage} ${LENSDIR}/${IMAGE}_anisocorr.cat ${LENSDIR}/${IMAGE}_shear.cat
#
#### Lensing Object Selection
##

#rhmin=`awk '{print $2}' $LENSDIR/starselection`
#rhmax=`awk '{print $3}' $LENSDIR/starselection`
#rhmean=`awk 'BEGIN{print ('${rhmin}'+'${rhmax}')/2.0}'`
#
#shear_cut="1.0"
#rh_cut=`awk 'BEGIN{print ('${rhmean}'*1.15)}'`
#snrcut="3.0"
#
#${P_LDACFILTER} -i ${LENSDIR}/${IMAGE}_shear.cat -t OBJECTS -o ${TEMPDIR}/tmp63_$$.cat -c "(gs<$shear_cut);"
#
#${P_LDACFILTER} -i ${TEMPDIR}/tmp63_$$.cat -o ${TEMPDIR}/tmp64_$$.cat -c "(rh>$rh_cut);"
#
#${P_LDACFILTER} -i ${TEMPDIR}/tmp64_$$.cat -o ${LENSDIR}/${IMAGE}_shear_cut.cat  -c "(snratio>$snrcut);"
#
#rm -f tmp*_$$.cat
#
##################################
#### Clean out masked objects
#
#${P_LDACFILTER} -i ${LENSDIR}/${IMAGE}_shear_cut.cat \
#		-t OBJECTS \
#		-o ${LENSDIR}/${IMAGE}_masked.cat\
#		-c "(IMAFLAGS_ISO<16);"
#
#
#./weight_catalog.sh ${LENSDIR}/${IMAGE}_masked.cat ${LENSDIR}/${IMAGE}_weighted.cat
#
#
##exit
##
##################################
####### associate photo-z's
##
##exit
#
#if [ ! -e ${LENSDIR}/${IMAGE}_weighted.cat ]; then
#    echo "WEIGHTED CATALOG DOESN'T EXIST!"
#    exit 1
#fi
#
#${P_LDACTOASC} -i ${PHOTDIR}/${cluster}.calibrated.cat \
#               -t OBJECTS \
#               -b -k SeqNr \
#               > ${TEMPDIR}/nrs_$$.dat
#
#if [ ${photozcattype} == "LePhare" ]; then
#
#  ${P_GAWK} '{if($1!~"#") print $0}' ${PHOTDIR}/${photozcat} > ${TEMPDIR}/photz_$$.dat
#  
#  nseqnr=`wc ${TEMPDIR}/nrs_$$.dat | awk '{print $1}'`
#  nphotz=`wc ${TEMPDIR}/photz_$$.dat | awk '{print $1}'`
#  if [ ${nseqnr} -ne ${nphotz} ]; then
#      echo "Number of objects in phot-z catalog != number in photometry catalog"
#      exit 2
#  fi
#  
#  paste ${TEMPDIR}/nrs_$$.dat ${TEMPDIR}/photz_$$.dat > ${TEMPDIR}/photz_seqnr_$$.dat
#  
#  ${P_GAWK} 'BEGIN{
#             print "VERBOSE = DEBUG"
#  	   print "#"
#  	   print "COL_NAME  = SeqNr"
#  	   print "COL_TTYPE = LONG"
#  	   print "COL_HTYPE = INT"
#  	   print "COL_COMM = \"\""
#  	   print "COL_UNIT = \"\""
#  	   print "COL_DEPTH = 1"
#  	   print "#"
#             while (getline < ("'${PHOTDIR}'/'${photozcat}'") > 0)
#  	   if ($2~"Output" && $3~"format")
#  	   {
#  	     while (getline < ("'${PHOTDIR}'/'${photozcat}'") > 0)
#  	     {
#  	       if($1~"###") break
#  	       for(i=2;i<NF;i=i+3)
#  	       {
#  	         name=$i
#  	         print "COL_NAME  = "$i
#  		 print "COL_TTYPE = FLOAT"
#  		 print "COL_HTYPE = FLOAT"
#  		 print "COL_COMM = \"\""
#  		 print "COL_UNIT = \"\""
#  		 print "COL_DEPTH = 1"
#  		 print "#"
#  	       }
#  	     }
#  	   }
#  	   else
#  	   {
#  	     if($1!~"#")
#  	       break
#  	   }
#             }' > ${PHOTDIR}/photz2ldac.a2l.conf
#  
#  ${P_ASCTOLDAC} -i ${TEMPDIR}/photz_seqnr_$$.dat \
#                 -o ${PHOTDIR}/${photozcat}.cat \
#                 -t PHOTZ \
#  	       -c ${PHOTDIR}/photz2ldac.a2l.conf
#  
#  
#  ${P_LDACADDTAB} -i ${LENSDIR}/${IMAGE}_weighted.cat \
#                  -o ${TEMPDIR}/tmp_100_$$.cat \
#                  -p ${PHOTDIR}/${photozcat}.cat \
#                  -t PHOTZ
#  
#  ${P_MAKEJOIN} -i ${TEMPDIR}/tmp_100_$$.cat \
#                -o ${TEMPDIR}/tmp_101_$$.cat \
#  	      -m OBJECTS \
#                -r PHOTZ \
#                -c ${reddir}/conf/dummy_SeqNr.mj.conf \
#                -COL_NAME Z_BEST -COL_INPUT Z_BEST
#  
#  ${P_LDACDELTAB} -i ${TEMPDIR}/tmp_101_$$.cat \
#  	        -o ${LENSDIR}/${IMAGE}_weighted_photz.cat \
#  	        -t PHOTZ
#
##################
## filter out cluster+foreground objects
#
#${P_LDACFILTER} -i ${LENSDIR}/${IMAGE}_weighted_photz.cat \
#                -o ${LENSDIR}/${cluster}_fbg.cat \
#		-t OBJECTS \
#                -c "(Z_BEST > ${zcut});"
#
#
#elif [ ${photozcattype} == "BPZ" ]; then
#
#  ${P_ASCTOLDAC} -i ${TEMPDIR}/nrs_$$.dat \
#                 -o ${TEMPDIR}/${photozcat}.nrs \
#                 -t STDTAB \
#  	         -c ${reddir}/conf/SeqNr.a2l.conf
#  
#
#  ${P_LDACJOINKEY} -i ${PHOTDIR}/${photozcat} \
#                  -o ${TEMPDIR}/tmp_200_$$.cat \
#                  -p ${TEMPDIR}/${photozcat}.nrs \
#                  -t STDTAB -k SeqNr
#
#  ${P_LDACRENKEY} -i ${PHOTDIR}/${photozcat} \
#                  -o ${TEMPDIR}/tmp_200_$$.cat \
#                  -t STDTAB \
#                  -k BPZ_Z_B Z_BEST
#
#  
# 
#  ${P_LDACADDTAB} -i ${LENSDIR}/${IMAGE}_weighted.cat \
#                  -o ${TEMPDIR}/tmp_100_$$.cat \
#                  -p ${TEMPDIR}/tmp_200_$$.cat \
#                  -t STDTAB
# 
#  ${BIN}/make_join -i ${TEMPDIR}/tmp_100_$$.cat \
#                -o ${TEMPDIR}/tmp_101_$$.cat \
#  	        -m OBJECTS \
#                -r STDTAB \
#                -c ${reddir}/conf/dummy_SeqNr.mj.conf \
#                -COL_NAME Z_BEST -COL_INPUT Z_BEST \
#                -COL_NAME BPZ_Z_B_MIN -COL_INPUT BPZ_Z_B_MIN \
#                -COL_NAME BPZ_Z_B_MAX -COL_INPUT BPZ_Z_B_MAX \
#                -COL_NAME BPZ_ODDS -COL_INPUT BPZ_ODDS
#  
#  ${P_LDACDELTAB} -i ${TEMPDIR}/tmp_101_$$.cat \
#  	        -o ${TEMPDIR}/tmp_102_$$.cat \
#  	        -t STDTAB
#
#  ${P_LDACCALC} -i ${TEMPDIR}/tmp_102_$$.cat \
#  	        -o ${LENSDIR}/${IMAGE}_weighted_photz.cat \
#  	        -t OBJECTS \
#                -n BPZ_Z_B_MAX-MIN "" -k FLOAT \
#                -c "(BPZ_Z_B_MAX - BPZ_Z_B_MIN);" \
#                -n BPZ_Z_B_MAX-MIN_Z "" -k FLOAT \
#                -c "( (BPZ_Z_B_MAX - BPZ_Z_B_MIN) / (1+Z_BEST));"
#
##################
## filter out cluster+foreground objects
#
#${P_LDACFILTER} -i ${LENSDIR}/${IMAGE}_weighted_photz.cat \
#                -o ${LENSDIR}/${cluster}_fbg.cat \
#		-t OBJECTS \
#                -c "(((Z_BEST > ${zcut}) AND (BPZ_Z_B_MAX-MIN_Z<0.8)) AND (BPZ_ODDS>0.95));"
#
#else
#    echo "Photo-z catalog unknown."
#    exit 2
#fi
#               
##exit 0;
#
#
#################################
## Reject bad regions
#
#./reject_objs.sh ${LENSDIR}/${cluster}_fbg.cat ${LENSDIR}/quickmask.reg
#
#
##################################
## Do Map reconstruction
#
#./process_map_recon.sh ${lensingimage} ${LENSDIR}/${cluster}_fbg.filtered.cat 10000 10000 "500 1000 1500 2000 3000"
#
#
#
##################
## fit SIS profile
#
##{
##echo "ldist=lumdist(${redshift})"
##echo 'get_lun, lun1'
##echo 'openw, lun1, "'${LENSDIR}'/lumdist.dat"'
##echo 'printf, lun1, ldist, FORMAT="(g)"'
##echo 'close, lun1'
##echo 'free_lun, lun1'
##} | idl
##
##lumdist=`awk '{print $1}' ${LENSDIR}/lumdist.dat`
##angdist=`awk 'BEGIN{print '${lumdist}'/((1+'${redshift}')*(1+'${redshift}'))}'`
##angscale=`awk 'BEGIN{print '${angdist}'*(1./3.6)*(3.14159/180.)}'`   # kpc/"
##
##pix03=`awk 'BEGIN{print 300/('${angscale}'*0.1)}'`
##pix30=`awk 'BEGIN{print 3000/('${angscale}'*0.1)}'`
##
#
PIXSCALE=0.2

outputfile=${LENSDIR}/${cluster}_fbg_sisfit.ml.filtered.dat

./fit_SIS.py ${LENSDIR}/${cluster}_fbg.filtered.cat ${redshift} "5000,5000" ${PIXSCALE} ${cluster} | awk '($1 !~ /</){print}' > $outputfile




exit




#beta=`awk '{if($1~"beta:") print $2}' ${LENSDIR}/${cluster}_fbg_sisfit.dat`
#beta2=`awk '{if($1~"beta2:") print $2}' ${LENSDIR}/${cluster}_fbg_sisfit.dat`
#sigma=`awk '{if($1~"sigma:") print $2}' ${LENSDIR}/${cluster}_fbg_sisfit.dat`
#r500x=`grep ${cluster} ${subarudir}/clusters.r500x.dat | awk '{print $2}'`
#mass_SIS=`awk 'BEGIN{print 3*'${sigma}'*'${sigma}'*'${r500x}'/4.3e-06}'`

#beta=`awk '{if($1~"beta:") print $2}' ${LENSDIR}/coadd_fbg_sisfit.dat`
#beta2=`awk '{if($1~"beta2:") print $2}' ${LENSDIR}/coadd_fbg_sisfit.dat`
#sigma=`awk '{if($1~"sigma:") print $2}' $outputfile`
#sigmaerr=`awk '{if($1~"sigma:") print $3}' $outputfile`
#r500x=`grep ${cluster} ${subarudir}/clusters.r500x.dat | awk '{print $2}'`
#r500x_err=`grep ${cluster} ${subarudir}/clusters.r500x.dat | awk '{print $3}'`
#mass_SIS=`awk 'BEGIN{printf "%4.3e\n", 3*'${sigma}'*'${sigma}'*'${r500x}'/4.3e-09}'`
#mass_SIS_err=`awk 'BEGIN{printf "%4.3e\n", '${mass_SIS}'*sqrt( (2*'${sigmaerr}'/'${sigma}')^2 + ('${r500x_err}'/'${r500x}')^2 )}'`
#
#echo "Copy ${LENSDIR}/${cluster}_fbg_4nfw.dat to xoc; run"
#echo "  nfwshear ${cluster}_fbg_4nfw.dat ${redshift} ${angdist} ${beta} 0.1 ${beta2} 1.082 0.026 > ${cluster}.mcmc"
#echo "and copy ${cluster}.mcmc back here"
#
#~/programs/sis.prog -s ${sigma} -b ${beta} -o ${LENSDIR}/${cluster}.bestsis
#
#{
#echo 'device postencap "'${LENSDIR}'/'${cluster}'_fbg_SIS.eps"'
#echo "lweight 4"
#echo 'data "'${LENSDIR}'/'${cluster}'_fbg_profile.dat"'
#echo "read { r 1 g 2 ge 3 b 4 be 5}"
#echo "window -1 -4 1 2:4"
#echo "limits 0 800 -0.08 0.15"
#echo "box 0 2"
##echo "xlabel r"
#echo "ylabel \langle\gamma_t\rangle"
#echo "ptype 20 3"
#echo "points r g"
#echo "lweight 1"
#echo "errorbar r g ge 2"
#echo "errorbar r g ge 4"
#echo "ltype 2"
#echo "relocate 0 0"
#echo "draw 2000 0"
##
#echo "ltype 1"
#echo 'data "'${LENSDIR}'/'${cluster}'.bestsis"'
#echo "read { rf 1 gf 2 }"
#echo "connect rf gf"
##
#echo "ltype 0"
#echo "window -1 -4 1 1"
#echo "limits 0 800 -0.099 0.099"
#echo "lweight 4"
#echo "box"
#echo "xlabel r"
#echo "ylabel \langle\gamma_{\times}\rangle"
#echo "points r b"
#echo "lweight 1"
#echo "errorbar r b be 2"
#echo "errorbar r b be 4"
#echo "ltype 2"
#echo "relocate 0 0"
#echo "draw 2000 0"
#echo "hardcopy"
#} | sm
#
#echo ${mass_SIS} ${mass_SIS_err}

#echo ${mass_SIS} ${mass_SIS_err} > ${cluster}.m500.lensing.dat

#exit 0;
#################
#./read_MCMC.py ${LENSDIR}/${cluster}_fbg.cat ${LENSDIR}/${cluster}.mcmc ${redshift} ${beta}
