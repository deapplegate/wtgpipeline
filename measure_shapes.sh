#!/bin/bash -xv
##################
#. BonnLogger.sh
#. log_start

##################
# This program measures shapes and mags of objects given in an ldac catalog, in an image
################

# $1 : input image
# $2 : input catalog (ldac format)
# $3 : output catalog name
# $4 : Directory with space (for temp files)

#CVSID="$Id: measure_shapes.sh,v 1.3 2010-10-05 22:42:30 dapple Exp $"

#############################################################

imagefile=$1
inputcat=$2
outputcat=$3
tmpdir=$4

. progs.ini > scratch/progs.out 2>&1

##################

if [ -e ${outputcat} ]; then
    rm ${outputcat}
fi

image=`basename ${imagefile} .fits`

###Reformat catalog / hfindpeaks
${P_LDACADDKEY} -i $inputcat -o ${tmpdir}/shapes_$$.cat \
			-t OBJECTS -k nu 1.0 FLOAT ""

${P_LDACCALC} -i ${tmpdir}/shapes_$$.cat -o ${tmpdir}/shapes_1_$$.cat -t OBJECTS \
			  -c "(FLUX_RADIUS);" -n "rg" "" -k FLOAT \
			  -c "(Xpos-1.0);" -n "x" "" -k LONG \
			  -c "(Ypos-1.0);" -n "y" "" -k LONG \
			  -c "(Xpos);" -n "xbad" "" -k FLOAT \
			  -c "(Ypos);" -n "ybad" "" -k FLOAT

${P_LDACTOASC} -i ${tmpdir}/shapes_1_$$.cat -b -t FIELDS \
			   -k FITSFILE SEXBKGND SEXBKDEV -s > ${tmpdir}/shapes_$$.asc


${P_ASCTOLDAC} -i ${tmpdir}/shapes_$$.asc \
    -c ${LENSCONF}/asctoldac_shapes.conf \
    -t HFINDPEAKS -o ${tmpdir}/hfind_$$.cat -b 1 -n "KSB"


# now transfer the HFINDPEAKS table to the SEX catalog
${P_LDACADDTAB} -i ${tmpdir}/shapes_1_$$.cat -o ${tmpdir}/shapes_2_$$.cat \
    -t HFINDPEAKS -p ${tmpdir}/hfind_$$.cat

#ANJA's Copy Has:
#	#### no more cuts! -- Anja, 2011-04-25
#	cp ${tmpdir}/shapes_2_$$.cat ${tmpdir}/${image}_pos_$$.cat
#	## at this point, rg is the flux radius --DOUG
#	#${P_LDACFILTER} -i ${tmpdir}/shapes_2_$$.cat \
#	#    -o ${tmpdir}/${image}_pos_$$.cat \
#	#    -c "(rg>0.0)AND(rg<25.0);"
#DOUG's Copy Has:
#	# at this point, rg is the flux radius --DOUG
#	# analyseldac fails on rg<0 . It also rarely returns cl=2 for rg>10 (5% of objects)
#	${P_LDACFILTER} -i ${TEMPDIR}/shapes_2_$$.cat \
#	    -o ${TEMPDIR}/${lensing_base}_pos_$$.cat \
#	    -c "(rg>0.0)AND(rg<10.0);"
#THE POINT: Anja doesn't want to add unnecessary cuts,
# 	while Doug wants to add cuts for the sake of CPU time/errors
# 	instead, what I'll do is only cut out negative rg (rg>0.0), in order to avoid a segfault error
${P_LDACFILTER} -i ${tmpdir}/shapes_2_$$.cat \
    -o ${tmpdir}/${image}_pos_$$.cat \
    -c "(rg>0.0);"

# now run analyseldac
./run_analyseldac.py ${tmpdir}/${image}_pos_$$.cat ${tmpdir}/${image}_ksb_$$.cat ${imagefile}

transfer_keys=""
coadd_filters=`./dump_cat_filters.py ${tmpdir}/${image}_pos_$$.cat | grep COADD`
if [ -n "$coadd_filters" ]; then
    mag_isos=`echo $coadd_filters | awk '{print "MAG_ISO-"$1}'`
    mag_isos_errs=`echo $coadd_filters | awk '{print "MAGERR_ISO-"$1}'`
    mag_aperss=`echo $coadd_filters | awk '{print "MAG_APER-"$1}'`
    mag_aperss_errs=`echo $coadd_filters | awk '{print "MAGERR_APER-"$1}'`
    
    transfer_keys="$mag_isos $mag_isos_errs $mag_aperss $mag_aperss_errs"
fi

${P_LDACJOINKEY} -i ${tmpdir}/${image}_ksb_$$.cat \
		 -t OBJECTS \
		 -o ${tmpdir}/shapes_3_$$.cat \
		 -p ${tmpdir}/${image}_pos_$$.cat \
    -k Flag \
    IMAFLAGS_ISO \
    NIMAFLAGS_ISO \
    CLASS_STAR      \
    ALPHA_J2000 \
    DELTA_J2000 $transfer_keys

if [ ! -e ${tmpdir}/shapes_3_$$.cat ]; then
    log_status 2 "Shape catalog not produced"
    exit 2
fi

#### no more cuts! -- Anja, 2011-04-25
cp ${tmpdir}/shapes_3_$$.cat ${tmpdir}/${image}_clean_$$.cat
#${P_LDACFILTER} -i ${tmpdir}/shapes_3_$$.cat \
#		-t OBJECTS \
#		-o ${tmpdir}/${image}_clean_$$.cat\
#		-c "((cl=0 AND deltae1!=1000) AND deltae2!=1000);"

#######
#calculating angle and ellipticity
${P_LDACTOASC} -i ${tmpdir}/${image}_clean_$$.cat \
	       -t OBJECTS \
	       -b -k e1 e2 \
	       | awk '{print 0.5*atan2($2,$1)}' \
	       > ${tmpdir}/shapes_ang_$$.dat

${P_ASCTOLDAC} -i ${tmpdir}/shapes_ang_$$.dat \
	       -o ${tmpdir}/shapes_ang_$$.cat \
	       -t OBJECTS \
	       -c ${LENSCONF}/atan2.a2l.conf

${P_LDACJOINKEY} -i ${tmpdir}/${image}_clean_$$.cat \
		 -o ${tmpdir}/shapes_4_$$.cat \
		 -t OBJECTS \
		 -p ${tmpdir}/shapes_ang_$$.cat \
		 -k theta_al

${P_LDACCALC} -i ${tmpdir}/shapes_4_$$.cat \
	       -t OBJECTS \
	       -o ${outputcat} \
	       -n eps_abs "" -k FLOAT \
	       -c "(sqrt(e1*e1+e2*e2));"

if [ ! -e ${outputcat} ]; then
    #log_status 3 "Output catalog not produced"
    exit 3
fi


#rm ${tmpdir}/shapes_$$.cat ${tmpdir}/shapes_$$.asc ${tmpdir}/shapes_*_$$.cat ${tmpdir}/hfind_$$.cat ${tmpdir}/${image}_*_$$.cat ${tmpdir}/shapes_ang_$$.dat ${tmpdir}/${image}_*_$$.out.cat

#log_status 0
