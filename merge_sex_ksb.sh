#!/bin/bash -xv
. BonnLogger.sh
. log_start
# the script merges info from the singleastrom
# and the check_science_PSF step. It transfers
# e1, e2 from the KSB cats to the SExtractor cats
# giving the "new" catalogs the same .cat as the old
# ones. Hence these catalogs can be used in the
# further processing having KSB info. Also this step
# is not absolutely necssary in the processing and
# can be omitted if this PSF information is not 
# important.
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 17.01.2007:
# - If KSB catalogues for certain files are not present
#   they will be filled up with dummy values for the four
#   keys e1, e2, rh and cl (e1=e2=-2.0; rh=0.0; cl=0).
#   We no longer quit the script
#   if KSB information is not present for all files.
#   In this way we still can use the present lensing
#   information.
# - filenames for temporary files are unique now including
#   the process number.
#
# 07.02.2007:
# I substituted two 'ls' commands with 'find' equivalents 
# to avoid 'argument list too long' errors.
#
# 28.07.2007:
# I corrected a bug when seeting the BASE variable in a loop.

#$1: main dir.
#$2: science dir.
#$3: image extension (ext) on ..._iext.fits (i is the chip number)

. ${INSTRUMENT:?}.ini

# first make a security copy if it does not yet exist
if [ -d /$1/$2/cat/copy ]; then
    mv /$1/$2/cat/copy /$1/$2/cat/copy2
fi

mkdir /$1/$2/cat/copy
${P_FIND} /$1/$2/cat/ -maxdepth 1 -name \*$3.cat -exec cp {} /$1/$2/cat/copy \;


# now transfer KSB info
${P_FIND} /$1/$2/cat/copy/ -name \*$3.cat > ${TEMPDIR}/mergecats_$$

# test if all KSB cats are there; if not
# do nothing !!!

if [ -f ${TEMPDIR}/fail_$$ ]; then
    rm ${TEMPDIR}/fail_$$
fi

cat ${TEMPDIR}/mergecats_$$ |\
while read CAT
do
    BASE=`basename ${CAT} .cat`
    if [ ! -f "/$1/$2/cat/${BASE}_ksb_tmp.cat2" ]; then
        echo "/$1/$2/cat/${BASE}_ksb_tmp.cat2 is not there" >> fail_$$
    fi
done  

cat ${TEMPDIR}/mergecats_$$ |\
{
    while read CAT
    do
        # The following ldacfilter is necessary because a 
        # corresponding cut was applied when running the KSB
        # algorithm (TO BE CHANGED because we would like to
        # keep all objects!)
        ${P_LDACFILTER} -i ${CAT} -o ${TEMPDIR}/tmp1_$$.cat \
                        -t LDAC_OBJECTS \
	                -c "(IMAFLAGS_ISO=0)AND((FLUX_RADIUS>0.0)AND(FLUX_RADIUS<20.0));"

        BASE=`basename ${CAT} .cat`
        if [ -f "/$1/$2/cat/${BASE}_ksb_tmp.cat2" ]; then
            ${P_LDACRENTAB} -i /$1/$2/cat/${BASE}_ksb_tmp.cat2 \
		            -o ${TEMPDIR}/tmp_$$.cat \
                            -t OBJECTS LDAC_OBJECTS
            ${P_LDACJOINKEY} -i ${TEMPDIR}/tmp1_$$.cat \
                             -o /$1/$2/cat/${BASE}.cat \
		             -p ${TEMPDIR}/tmp_$$.cat \
		             -t LDAC_OBJECTS -k e1 e2 rh cl snratio  
            rm ${TEMPDIR}/tmp_$$.cat ${TEMPDIR}/tmp1_$$.cat		     
        else
            # if we have no lensing information we add dummy
            # information to have consistent catalogues
            ${P_LDACADDKEY} -i ${TEMPDIR}/tmp1_$$.cat \
                            -o /$1/$2/cat/${BASE}.cat \
                            -t LDAC_OBJECTS \
                            -k e1 -2.0 FLOAT "dummy value" \
                               e2 -2.0 FLOAT "dummy value" \
                               rh 0.0 FLOAT "dummy value" \
                               cl 0 SHORT "dummy value"
            rm ${TEMPDIR}/tmp1_$$.cat
        fi
  done
}

rm ${TEMPDIR}/mergecats_$$



log_status $?
