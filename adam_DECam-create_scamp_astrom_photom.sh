#!/bin/bash
set -xv
#adam-example# ./adam_DECam-create_scamp_astrom_photom.sh /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/u_DECam/ single_V0.0.2A  /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/g_DECam/ single_V0.0.2A  /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/r_DECam/ single_V0.0.2A  /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/i_DECam/ single_V0.0.2A  /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/z_DECam/ single_V0.0.2A  /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/Y_DECam/ single_V0.0.2A PANSTARRS
#adam-example# ./adam_DECam-create_scamp_astrom_photom.sh /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/Y_DECam/ single_V0.0.2A PANSTARRS

cluster="A2204"
INSTRUMENT="DECam"
# File inclusions:
. ${INSTRUMENT:?}.ini > /tmp/INSTRUMENT.out 2>&1

### we can have different INSTRUMENTs
. progs.ini > /tmp/progs.out 2>&1

# NCHIPSMAX needs to be set before
NCHIPS=${NCHIPSMAX}

# define THELI_DEBUG and some other variables because of the '-u'
# script flag (the use of undefined variables will be treated as
# errors!)  THELI_DEBUG is used in the cleanTmpFiles function.

THELI_DEBUG=${THELI_DEBUG:-""}
P_SCAMP=${P_SCAMP:-""}
P_ACLIENT=${P_ACLIENT:-""}

##
## function definitions:
##
function cleanTmpFiles
{
    if [ -z ${THELI_DEBUG} ]; then
        echo "Cleaning temporary files for script $0"
        test -f photdata.txt_$$           && rm -f photdata.txt_$$
        test -f photdata_relzp.txt_$$     && rm -f photdata_relzp.txt_$$
    else
        echo "Variable THELI_DEBUG set! No cleaning of temp. files in script $0"    
    fi
}

# Handling of program interruption by CRTL-C
trap "echo 'Script $0 interrupted!! Cleaning up and exiting!'; \
      cleanTmpFiles; exit 1" INT

##
## initial sanity checks
##
# check whether we have the external 'scamp' and 'aclient' programs at all:
if [ -z ${P_SCAMP} ] || [ -z ${P_ACLIENT} ] 
then
    echo "You need the external 'scamp' AND 'aclient' programs to"
    echo "use this script! The necessary variable(s) in"
    echo "your progs.ini seem(s) not to be set! Exiting!!"
    exit 1;
fi

# The number of different image directories we have to consider:
NDIRS=$(( ($# - 1) / 2 ))

# get the used reference catalogue into a variable
STARCAT="PANSTARRS"

#adam-SHNT# shouldn't be hard to (1) filter, (2) make catlist, and (3) run s_scampcat on catlist
#        ${P_LDACFILTER} -i ${CAT} -t LDAC_OBJECTS \
#            -c "(((FLAGS<8)AND(B_IMAGE>0.8))AND((IMAFLAGS_ISO=0)OR(IMAFLAGS_ISO=2)));" \
#            -o ${BASE}.ldac

## MERGE CHIP CATS INTO MEF CAT: from our single chip catalogues create merged MEF catalogues                                                                              
# for each exposure:
# first get the basenames of all available exposures.
# The following fiddling is necessary because catalogues
# for individual chips might not be present (bad chips)
#FOR EACH IMAGE: build up list of indiv chip cats (${IMAGE}_${i}${ending}ldac) in ${CATS}
#adam-tmp# ending="OXC*"
#FOR EACH IMAGE: echo "${CATS} ./${IMAGE}_scamp.cat" >> ${DIR}/catlist.txt_$$
#FOR EACH IMAGE: Dummy external header containing focal plane and missing chip information (AHEADFILE=${DIR}/${INSTRUM}_c${CONFIG}_r${ROTATION}.ahead). They are used to distinguish different chip configurations in an, otherwise, unique astrometric context.
#after loop, run: python ${S_SCAMPCAT} ${DIR}/catlist.txt_$$
#adam-SHNT# end

# Test existence of image directory(ies) and create headers_scamp
# directories:
i=1 
j=2
k=1

#adam-tmp# while [ ${k} -le ${NDIRS} ]
#adam-tmp# do 
#adam-tmp#   if [ -d /${!i}/${!j} ]; then
#adam-tmp#       if [ -d /${!i}/${!j}/headers_scamp_${STARCAT} ]; then
#adam-tmp#           rm -rf /${!i}/${!j}/headers_scamp_${STARCAT}
#adam-tmp#       fi
#adam-tmp#       mkdir /${!i}/${!j}/headers_scamp_${STARCAT}
#adam-tmp#   else
#adam-tmp#       echo "Can't find directory /${!i}/${!j}"; 
#adam-tmp#       exit 1;
#adam-tmp#   fi
#adam-tmp#   i=$(( ${i} + 2 ))
#adam-tmp#   j=$(( ${j} + 2 ))
#adam-tmp#   k=$(( ${k} + 1 ))
#adam-tmp# done


##
## Here the main script starts:
##
DIR=`pwd`

ALLMISS=""
l=0
while [ ${l} -le ${NCHIPSMAX} ]
do
  ALLMISS="${ALLMISS}${l}"
  l=$(( ${l} + 1 ))
done

# all processing is performed in the 'first' image directory in
# a astrom_photom_scamp subdirectory:
cd /$1/$2/

#adam-tmp# test -d "astrom_photom_scamp_${STARCAT}" && rm -rf astrom_photom_scamp_${STARCAT}
#adam-tmp# mkdir -p astrom_photom_scamp_${STARCAT}/cat
#adam-tmp# mkdir astrom_photom_scamp_${STARCAT}/headers
#adam-tmp# mkdir astrom_photom_scamp_${STARCAT}/plots

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

    # we filter away flagged objects except THOSE which are saturated!
    # we also require a minimum size (semi minor axis) of two pixels

    #${P_LDACFILTER} -i ${CAT} -t LDAC_OBJECTS \
    #	-c "(((FLAGS<8)AND(B_IMAGE>0.8))AND((IMAFLAGS_ISO=0)OR(IMAFLAGS_ISO=2)));" \
    #	-o ${BASE}.ldac
    if [ ! -e "${BASE}.ldac" ]; then
	    ${P_LDACFILTER} -i ${CAT} -t LDAC_OBJECTS \
		-c "(((FLAGS<8)AND(B_IMAGE>0.8))AND(IMAFLAGS_ISO=0));" \
		-o ${BASE}.ldac
    fi


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
	IMAGES=`${P_FIND} ${curdir} -maxdepth 1 -name \*.sub.fits -exec basename {} \; |\
	    ${P_GAWK} '{ n = split($1, a, "_"); 
	                 name=""; 
	                 for(i = 1; i < (n-1); i++) 
	                 {
	                   name = name a[i] "_"
	                 } 
	                 name = name a[n-1]; 
	                 print name;}' | sort | uniq`
	# now the merging with a pyfits-based Python script:
	for IMAGE in ${IMAGES}
	do
		# If an old scamp catalogue exists the python call below
		# would fail!
		test -f ./${IMAGE}_scamp.cat && rm -f ./${IMAGE}_scamp.cat
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
			ocat=`\ls ${IMAGE}_${i}[!0-9]*.ldac`
			if [ -f "${ocat}" ]; then
			    #CATS="${CATS} `echo ${IMAGE}_${i}[!0-9]*.ldac`"
			    CATS="${CATS} `\ls ${ocat}`"
			    #echo "ADAMLOG: IMAGE=$IMAGE and CATS=$CATS "
			else
			    MISSCHIP=${MISSCHIP}${i}
			    echo "#adam-look#(error-possible): : IMAGE=$IMAGE and MISSCHIP=$MISSCHIP"
			fi
			# not R.fits either?
			#adam-old# oimage=`${P_FIND} ${curdir} -maxdepth 1 -name ${IMAGE}_${i}[!0-9]*.fits | awk '{if($1!~"sub.fits" && $1!~"I.fits" && $1!~"R.fits" ) print $0}'`
			oimage=`${P_FIND} ${curdir} -maxdepth 1 -name "${IMAGE}_${i}[!0-9]*.fits" | awk '{if($1!~"weight.fits" && $1!~"flag.fits" ) print $0}'`
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
			    
			    if [ "${INSTRUM}" == "KEY_N/A" ]; then
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
		#python ${S_SCAMPCAT} ${CATS} ./${IMAGE}_scamp.cat
		echo "${CATS} ./${IMAGE}_scamp.cat" >> ${DIR}/catlist.txt_$$
		# Dummy external header containing focal plane and missing 
		# chip information.
		# They are used to distinguish different chip configurations
		# in an, otherwise, unique astrometric conetxt.
		test -f ./${IMAGE}_scamp.ahead && rm -f ./${IMAGE}_scamp.ahead
		i=1
		while [ ${i} -le ${NCHIPS} ]
		do
			ocat=`\ls ${IMAGE}_${i}[!0-9]*.ldac`
			if [ -f "${ocat}" ]; then
			  if [ ${INSTRUM} == "SUBARU" ]; then
			     AHEADFILE=${DIR}/${INSTRUM}_c${CONFIG}_r${ROTATION}.ahead
			  else
			     AHEADFILE=${DIR}/${INSTRUM}.ahead
			  fi
			  if [ -f "${AHEADFILE}" ]; then
			    ${P_GAWK} 'BEGIN {ext = '${i}'; nend = 0} 
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
				       }' ${AHEADFILE} >> ${IMAGE}_scamp.ahead

			    echo "${IMAGE} ${AHEADFILE}" >> aheadfiles.txt
			  fi
			  echo "MISSCHIP= '${MISSCHIP}'" >> ./${IMAGE}_scamp.ahead
			  echo "END      "               >> ./${IMAGE}_scamp.ahead
			fi
			i=$(( ${i} + 1 ))
		done
	done
	j=$(( ${j} + 2 ))
	k=$(( ${k} + 2 ))
	m=$(( ${m} + 1 ))
done

python ${S_SCAMPCAT} ${DIR}/catlist.txt_$$
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	echo "adam-Error: something wrong with python scamp call. Checkout ${DIR}/catlist.txt_$$"
	exit ${exit_stat};
fi

#exit 0; #adam-SHNT#
# now call scamp:
cd ../headers

##scamp manual says:
# Hence for every input (say, xxxx.cat) FITS catalogue, SCAMP looks for a xxxx.ahead header
# file, loads it if present, and overrides or adds to image header keywords those found there.
if [ -f "${DIR}/${INSTRUM-${INSTRUMENT}}_c${CONFIG-""}_r${ROTATION-0}.ahead" ]; then
  MOSAICTYPE="-MOSAIC_TYPE FIX_FOCALPLANE"
else
  MOSAICTYPE="-MOSAIC_TYPE UNCHANGED"
fi
MOSAICTYPE="-MOSAIC_TYPE FIX_FOCALPLANE"
#MOSAICTYPE="-MOSAIC_TYPE UNCHANGED"
#MOSAICTYPE="-MOSAIC_TYPE LOOSE"
echo "MOSAICTYPE=" $MOSAICTYPE

#adam-SHNT# START put scamp call here
## SEE adam_A2204_scamp_DECam.sh in ~/wtgpipeline/adam-run_scamp
cp /nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/run_scamp/astrefcat.cat .                                                                                                                   
scamp_mode_instrum_ref="-STABILITY_TYPE INSTRUMENT \
        -ASTREF_CATALOG FILE \
        -ASTREFCAT_NAME astrefcat.cat \
        -ASTREFCENT_KEYS raMean,decMean \
        -ASTREFERR_KEYS raMeanErr,decMeanErr \
        -ASTREFMAG_LIMITS 13,23 \
        -ASTREFMAG_KEY iMeanPSFMag \
        -ASTREFMAGERR_KEY iMeanPSFMagErr"
scamp_mode_use=${scamp_mode_instrum_ref}

export SCAMP_NAMETAG=scamp_${cluster}_${INSTRUMENT}_pass1-like
ALLCATS=`${P_FIND} ../cat/ -name \*scamp.cat`

#is CONFIG going to screw this up?
${P_SCAMP2} ${ALLCATS} \
    -c ${CONF}/scamp_astrom_photom.scamp \
    -ASTRINSTRU_KEY FILTER,INSTRUM,CONFIG,ROTATION,MISSCHIP,PPRUN \
    -CDSCLIENT_EXEC ${P_ACLIENT} \
    -NTHREADS ${NPARA} \
    -XML_NAME ${SCAMP_NAMETAG}.xml \
    -MAGZERO_INTERR 0.1 \
    -MAGZERO_REFERR 0.1 \
    -MATCH Y \
    -SN_THRESHOLDS 3,100 \
    -CROSSID_RADIUS 2.0 \
    -DISTORT_DEGREES 3 \
    -ASTREF_WEIGHT 1 \
    ${MOSAIC_TYPE} ${scamp_mode_use}
#-CHECKPLOT_RES 4000,3000

if [ $? -ne 0 ]
then
    echo "scamp call failed !! Exiting !!"
    #adam-tmp# cleanTmpFiles
    exit 1
fi

mkdir /nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/run_scamp/${SCAMP_NAMETAG}
cp ~/wtgpipeline/scamp.xls /nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/run_scamp/${SCAMP_NAMETAG}
sed -i.old 's/http:\/\/www.slac.stanford.edu\/\~anja\/scamp.xsl/scamp.xsl/g' ${SCAMP_NAMETAG}.xml
cp *.png /nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/run_scamp/${SCAMP_NAMETAG}
cp ${SCAMP_NAMETAG}.xml /nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/run_scamp/${SCAMP_NAMETAG}
echo "cd /nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/run_scamp/"
echo "firefox ${SCAMP_NAMETAG}.xml &"
#adam-SHNT# END   put scamp call here


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
mv ${BONN_TARGET}_scamp.xml ../plots

# now get the relative magnitude offsets from the FLXSCALES
# estimated by scamp:
#adam-tmp# test -f photdata.txt_$$ && rm -f photdata.txt_$$

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
while read NAME RELZP FLXSCALE
do
    i=1
    j=1  # counts the actually available chips!
    while [ ${i} -le ${NCHIPS} ]
    do
        # we need to take care of catalogs that may not be
        # present (bad chips)!
        ocat=`\ls ../cat/${NAME}_${i}[!0-9]*.ldac`
        if [ -f "${ocat}" ]; then
            headername=`basename ../cat/${NAME}_${i}[!0-9]*.ldac .ldac | perl -e '<STDIN> =~ /(.+_\d+)/; print "$1\n";'`
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
  if [ -f ${CATBASE[$i]}.head ]; then
    mv ${CATBASE[$i]}*head ${CATDIR[$i]}/headers_scamp_${STARCAT}
    exit_status=$?
  fi
  
  i=$(( ${i} + 1 )) 
done

# clean up temporary files and bye
#adam-tmp# cleanTmpFiles

cd ${DIR}
#log_status $exit_status
exit $exit_status
