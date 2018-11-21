#!/bin/bash
set -xv
#adam-example# ./create_scamp_astrom_photom.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-V SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-RC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-IC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+ SCIENCE PANSTARRS 2>&1 | tee -a OUT-create_scamp_astrom_photom-MACS0429-02.log
# File inclusions:
export cluster="RXJ2129"
INSTRUMENT="SUBARU"
. ${INSTRUMENT:?}.ini > /tmp/SUBARU.out 2>&1

### we can have different INSTRUMENTs
. progs.ini > /tmp/progs.out 2>&1

#adam: if there are multiple endings, you can set your preferred one here

# NCHIPSMAX needs to be set before
NCHIPS=10

# define THELI_DEBUG and some other variables because of the '-u'
# script flag (the use of undefined variables will be treated as
# errors!)  THELI_DEBUG is used in the cleanTmpFiles function.
# 
THELI_DEBUG=${THELI_DEBUG:-""}
P_SCAMP=${P_SCAMP:-""}
P_ACLIENT=${P_ACLIENT:-""}

# The number of different image directories we have to consider:
NDIRS=$(( ($# - 1) / 2 ))

# get the used reference catalogue into a variable
STARCAT=${!#}

# Test existence of image directory(ies) and create headers_scamp
# directories:
i=1 
j=2
k=1

# all processing is performed in the 'first' image directory in
# a astrom_photom_scamp subdirectory:
cd /$1/$2/

cd astrom_photom_scamp_${STARCAT}/cat

# filter input catalogues to reject bad objects
i=1
j=2
l=1
NCATS=0

while [ ${l} -le ${NDIRS} ]
do 
  FILES=`${P_FIND} /${!i}/${!j}/cat_scamp/ -maxdepth 1 -name \*.cat`

  for CAT in ${FILES}
  do
    NCATS=$(( ${NCATS} + 1 ))

    BASE=`basename ${CAT} .cat`

    INSTRUM=`${P_LDACTOASC} -i ${CAT} \
                            -t LDAC_IMHEAD -s |\
             fold | grep INSTRUM | ${P_GAWK} '{print $3}'`

    # we filter away flagged objects except THOSE which are saturated!
    # we also require a minimum size (semi minor axis) of two pixels

    # The following two arrays are necessary to put headers
    # to the correct directories lateron.
    CATBASE[${NCATS}]=`echo ${BASE} | perl -e '<STDIN> =~ /(.+_\d+)/; print "$1\n";'`
    CATDIR[${NCATS}]=/${!i}/${!j}
  done
  i=$(( ${i} + 2 ))
  j=$(( ${j} + 2 ))
  l=$(( ${l} + 1 ))
done

# from our single chip catalogues create merged MEF catalogues
# for each exposure:
# first get the basenames of all available exposures.
# The following fiddling is necessary because catalogues
# for individual chips might not be present (bad chips)

ALLIMAGES=""

j=1
k=2
m=1
while [ ${m} -le ${NDIRS} ]
do 
	curdir=/${!j}/${!k}/
	# The following 'awk' construct cuts away everything after 
	# the last '_' in the image names (including the underscore itself);
	# we implicitely assume that the image extension DOES NOT contain
	# '_'s.
	IMAGES=`${P_FIND} ${curdir} -maxdepth 1 -name \*.fits -exec basename {} \; |\
	    ${P_GAWK} '{ n = split($1, a, "_"); 
	                 name=""; 
	                 for(i = 1; i < (n-1); i++) 
	                 {
	                   name = name a[i] "_"
	                 } 
	                 name = name a[n-1]; 
	                 print name;}' | sort | uniq`
	image1=`\ls -1 ${curdir}/SUPA*_1OCF*.fits | head -n 1`
	num_path_supa_chip_ending=(`~/wtgpipeline/adam_quicktools_fast_get_path_supa_chip_ending.py ${image1}`)
	ending=${num_path_supa_chip_ending[4]}
	# now the merging with a pyfits-based Python script:
	for IMAGE in ${IMAGES}
	do
		# If an old scamp catalogue exists the python call below
		# would fail!
		i=1
		CATS=""
		echo "ADAMLOG: IMAGE=$IMAGE and CATS=$CATS "
		MISSCHIP=0     # contains the missing chips in the form of a pasted
		# string. If e. g. chips 19 and 25 are bad the variable
		# would contain 01925 (read 0_19_25; '0' is always at
		# the beginning)
		while [ ${i} -le ${NCHIPS} ]
		do
			# The following test for an image implicitely assumes that the
			# image ending does NOT start with a number: obvious but I mention
			# it just in case ....
			# It is necessary as we allow for images with different endings in the 
			# image directories:
			ocat=`\ls ${IMAGE}_${i}${ending}.ldac`
			if [ ! -f "${IMAGE}_${i}${ending}.ldac" ]; then
				ocat=`\ls ${IMAGE}_${i}[!0-9]*.ldac`
			fi
			if [ -f "${ocat}" ]; then
			    #CATS="${CATS} `echo ${IMAGE}_${i}[!0-9]*.ldac`"
			    CATS="${CATS} `\ls ${ocat}`"
			    echo "ADAMLOG: IMAGE=$IMAGE and CATS=$CATS "
			else
			    MISSCHIP=${MISSCHIP}${i}
			fi
			# not R.fits either?
			#adam-old# oimage=`${P_FIND} ${curdir} -maxdepth 1 -name ${IMAGE}_${i}[!0-9]*.fits | awk '{if($1!~"sub.fits" && $1!~"I.fits" && $1!~"R.fits" ) print $0}'`
			#adam-old# oimage=`${P_FIND} ${curdir} -maxdepth 1 -name ${IMAGE}_${i}[!0-9]*.fits | awk '{if($1!~"sub.fits" && $1!~"I.fits" ) print $0}'`
			oimage=`${P_FIND} ${curdir} -maxdepth 1 -name ${IMAGE}_${i}[!0-9]*.fits | awk '{if($1!~"sub.fits") print $0}'`
			if [ -n "${oimage}" ]; then
			    #ROTATION=`dfits "${oimage}" | fitsort ROTATION | awk '($1!="FILE") {print $2}'`
			    #CONFIG=`dfits "${oimage}" | fitsort CONFIG | awk '($1!="FILE") {print $2}'`
			    #INSTRUM=`dfits "${oimage}" | fitsort INSTRUM | awk '($1!="FILE") {print $2}'`
			    ROTATION=`dfits ${oimage} | fitsort ROTATION | awk '($1!="FILE") {print $2}'`
			    CONFIG=`dfits ${oimage} | fitsort CONFIG | awk '($1!="FILE") {print $2}'`
			    INSTRUM=`dfits ${oimage} | fitsort INSTRUM | awk '($1!="FILE") {print $2}'`
			    
			    if [ "${ROTATION}" == "KEY_N/A" ]; then
			        ROTATION=0
			    fi
			    
			    if [ "${INSTRUM}" = "KEY_N/A" ]; then
			        INSTRUM=${INSTRUMENT:?}
			    fi

			fi
			i=$(( ${i} + 1 ))
		done
		#TO BE CALLED ON EACH IMAGE
		if [ "${MISSCHIP}" == "${ALLMISS}" ]; then
			continue
		fi
		ALLIMAGES="${ALLIMAGES} ${IMAGE}"
	done
	j=$(( ${j} + 2 ))
	k=$(( ${k} + 2 ))
	m=$(( ${m} + 1 ))
done

cd ../headers

find ../cat/ -name \*.head -exec mv {} . \;

# scamp creates the headers in the directory where the catalogs are:
${P_FIND}  ../cat/ -name \*.head -exec mv {} . \;

# we want the diagnostic plots in an own directory:
mv fgroups*         ../plots
mv distort*         ../plots
mv astr_interror2d* ../plots
mv astr_interror1d* ../plots
mv astr_referror2d* ../plots
mv astr_referror1d* ../plots
mv astr_chi2*       ../plots
mv psphot_error*    ../plots
mv astr_refsysmap*  ../plots
mv phot_zpcorr*     ../plots
mv phot_errorvsmag* ../plots
mv ${cluster}_scamp.xml ../plots
cp ~/wtgpipeline/scamp.xsl ../plots
sed -i.old 's/href=".*"?>/href="scamp.xsl"?>/g' ../plots/${cluster}_scamp.xml

# now get the relative magnitude offsets from the FLXSCALES
# estimated by scamp:
test -f photdata.txt_$$ && rm -f photdata.txt_$$

# Because the flux scales refer to an image normalised to one
# second we need to obtain the exposure times of all frames
# first. We also get the SCAMP flux scale and the photometric 
# instrument:
for IMAGE in ${ALLIMAGES}
do
  NAME=${IMAGE}
  EXPTIME=`${P_LDACTOASC} -i ../cat/${IMAGE}_scamp.cat \
                     -t LDAC_IMHEAD -s |\
           fold | grep EXPTIME | ${P_GAWK} '{print $3}'`
  FLXSCALE=`grep FLXSCALE ${IMAGE}_scamp.head | uniq |\
            ${P_GAWK} '{print $2}'`
  PHOTINST=`grep PHOTINST ${IMAGE}_scamp.head | uniq |\
            ${P_GAWK} '{print $2}'`

  echo ${NAME}" "${EXPTIME}" "${FLXSCALE}" "${PHOTINST} >> photdata.txt_$$
done

# The following 'awk' script calculates relative zeropoints 
# and THELI fluxscales for the different photometric contexts: 
${P_GAWK} 'BEGIN {maxphotinst = 1;}
           { name[NR] = $1; 
             exptime[NR] = $2; 
             flxscale_scamp[NR] = $3;
             photinst[NR] = $4
             val[NR] = -2.5*log($3*$2)/log(10); 
             m[$4] = m[$4] + val[NR]
             nphotinst[$4] = nphotinst[$4] + 1 
             if($4 > maxphotinst) {maxphotinst = $4}} 
           END {
             for(i = 1; i <= maxphotinst; i++)
             {  
               m[i] = m[i] / nphotinst[i];
             } 
             for(i = 1; i <= NR; i++) 
             {
               relzp[i] = val[i] - m[photinst[i]];   
               flxscale_theli[i] = (10**(-0.4*relzp[i]))/exptime[i];
               printf("%s %f %e\n", 
                 name[i], relzp[i], flxscale_theli[i]);  
             }
           }' photdata.txt_$$ > photdata_relzp.txt_$$

# now split the exposure catalogues for the indivudual chips
# and add the RZP and FLXSCALE header keywords. Put the headers 
# into appropriate headers_scamp directories
#
exit_stat=$? #use ${PIPESTATUS[0]} if it's <command> | tee -a OUT-command.log                                                                   
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi

while read NAME RELZP FLXSCALE
do
    i=1
    j=1  # counts the actually available chips!
    while [ ${i} -le ${NCHIPS} ]
    do
        # we need to take care of catalogs that may not be
        # present (bad chips)!
        ocat=`\ls ../cat/${NAME}_${i}${ending}.ldac`
        if [ ! -f "${ocat}" ]; then
            ocat=`\ls ../cat/${NAME}_${i}[!0-9]*.ldac`
    	    ocat_mode=2
        else
    	    ocat_mode=1
        fi
        if [ -f "${ocat}" ]; then
            if [ ${ocat_mode} -eq 1 ]; then
                headername=`basename ../cat/${NAME}_${i}${ending}.ldac .ldac | perl -e '<STDIN> =~ /(.+_\d+)/; print "$1\n";'`
            elif [ ${ocat_mode} -eq 2 ]; then
                headername=`basename ../cat/${NAME}_${i}[!0-9]*.ldac .ldac | perl -e '<STDIN> =~ /(.+_\d+)/; print "$1\n";'`
            fi
            # first rename the SCAMP header keyword FLXSCALE
            # to FLSCALE. We need FLXSCALE for the THELI
            # flux scaling later:
            sed -e 's/FLXSCALE/FLSCALE /' ${NAME}_scamp.head |\
            ${P_GAWK} 'BEGIN {ext = '${j}'; nend = 0}
                       {
                         if(nend < ext)
                         {
                           if($1 == "END")
                           {
                             nend++;
                             next;
                           }
                           if(nend == (ext-1)) { print $0 }
                         }
                       }
                       END { printf("RZP     = %20f / THELI relative zeropoint\n",
                                    '${RELZP}');
                             printf("FLXSCALE= %20E / THELI relative flux scale\n",
                                    '${FLXSCALE}');
                         printf("END\n")
                       }' > ${headername}.head
            j=$(( $j + 1 ))
        fi
        i=$(( $i + 1 ))
    done
done < photdata_relzp.txt_$$

i=1
while [ ${i} -le ${NCATS} ]
do
  if [ -f "${CATBASE[$i]}.head" ]; then
    mv ${CATBASE[$i]}*head ${CATDIR[$i]}/headers_scamp_${STARCAT}
    exit_stat=$?
    if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
    fi
  fi
  
  i=$(( ${i} + 1 )) 
done
rm photdata_relzp.txt_$$

cd ${DIR}

exit $exit_stat
