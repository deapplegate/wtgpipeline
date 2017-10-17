#!/bin/bash
set -xv
#adam-example# ./create_scamp_astrom_photom-finish_11275.sh /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-J-B SCIENCE /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-C-RC SCIENCE /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-S-Z+ SCIENCE SDSS-R6 2>&1 | tee -a OUT-create_scamp_astrom_photom-finish_11275.log


# File inclusions:
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

ALLIMAGES=' SUPA0109617 SUPA0109619 SUPA0109620 SUPA0120015 SUPA0120016 SUPA0120017 SUPA0120018 SUPA0120019 SUPA0120144 SUPA0120145 SUPA0120146 SUPA0120147 SUPA0120148 SUPA0120149 SUPA0120150 SUPA0120151 SUPA0120152 SUPA0120153 SUPA0109600 SUPA0109601 SUPA0109602 SUPA0109603 SUPA0109604 SUPA0109605 SUPA0109606 SUPA0109607 SUPA0109608 SUPA0109609 SUPA0109610 SUPA0109613 SUPA0109614 SUPA0109615 SUPA0120021 SUPA0120022 SUPA0120023 SUPA0120024 SUPA0120025 SUPA0120026 SUPA0120027 SUPA0120028 SUPA0120029 SUPA0120030 SUPA0120031 SUPA0120032 SUPA0120033 SUPA0120034 SUPA0120035 SUPA0120036 SUPA0120037 SUPA0120038'

# now call scamp:

cd ../headers
#/afs/slac/g/ki/software/local/bin/scamp ../cat/SUPA0109617_scamp.cat ../cat/SUPA0109619_scamp.cat ../cat/SUPA0109620_scamp.cat ../cat/SUPA0120015_scamp.cat ../cat/SUPA0120016_scamp.cat ../cat/SUPA0120017_scamp.cat ../cat/SUPA0120018_scamp.cat ../cat/SUPA0120019_scamp.cat ../cat/SUPA0120144_scamp.cat ../cat/SUPA0120145_scamp.cat ../cat/SUPA0120146_scamp.cat ../cat/SUPA0120147_scamp.cat ../cat/SUPA0120148_scamp.cat ../cat/SUPA0120149_scamp.cat ../cat/SUPA0120150_scamp.cat ../cat/SUPA0120151_scamp.cat ../cat/SUPA0120152_scamp.cat ../cat/SUPA0120153_scamp.cat ../cat/SUPA0109600_scamp.cat ../cat/SUPA0109601_scamp.cat ../cat/SUPA0109602_scamp.cat ../cat/SUPA0109603_scamp.cat ../cat/SUPA0109604_scamp.cat ../cat/SUPA0109605_scamp.cat ../cat/SUPA0109606_scamp.cat ../cat/SUPA0109607_scamp.cat ../cat/SUPA0109608_scamp.cat ../cat/SUPA0109609_scamp.cat ../cat/SUPA0109610_scamp.cat ../cat/SUPA0109613_scamp.cat ../cat/SUPA0109614_scamp.cat ../cat/SUPA0109615_scamp.cat ../cat/SUPA0120021_scamp.cat ../cat/SUPA0120022_scamp.cat ../cat/SUPA0120023_scamp.cat ../cat/SUPA0120024_scamp.cat ../cat/SUPA0120025_scamp.cat ../cat/SUPA0120026_scamp.cat ../cat/SUPA0120027_scamp.cat ../cat/SUPA0120028_scamp.cat ../cat/SUPA0120029_scamp.cat ../cat/SUPA0120030_scamp.cat ../cat/SUPA0120031_scamp.cat ../cat/SUPA0120032_scamp.cat ../cat/SUPA0120033_scamp.cat ../cat/SUPA0120034_scamp.cat ../cat/SUPA0120035_scamp.cat ../cat/SUPA0120036_scamp.cat ../cat/SUPA0120037_scamp.cat ../cat/SUPA0120038_scamp.cat -c /afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/conf/reduction/scamp_astrom_photom.scamp -ASTRINSTRU_KEY FILTER,INSTRUM,CONFIG,ROTATION,MISSCHIP,PPRUN -CDSCLIENT_EXEC /afs/slac.stanford.edu/g/ki/software/cdsclient/bin/aclient_cgi -NTHREADS 4 -MOSAIC_TYPE FIX_FOCALPLANE -XML_NAME MACS1115+01_scamp.xml -MAGZERO_INTERR 0.1 -MAGZERO_REFERR 0.03 -POSITION_MAXERR 1.0 -POSANGLE_MAXERR 0.05 -SN_THRESHOLDS 3,100 -FLAGS_MASK 0x00e0 -MATCH_NMAX 20000 -PIXSCALE_MAXERR 1.03 -DISTORT_DEGREES 3 -ASTREF_WEIGHT 1 -STABILITY_TYPE INSTRUMENT -ASTREF_CATALOG SDSS-R6 -CHECKPLOT_RES 4000,3000 -SAVE_REFCATALOG Y

find ../cat/ -name \*.head -exec mv {} . \;

#cd ../plots
#cp ~/bonnpipeline/scamp.xsl .
#sed -i.old 's/href=".*"?>/href="scamp.xsl"?>/g' MACS1115+01_scamp.xml

#cd ../headers


# now get the relative magnitude offsets from the FLXSCALES
# estimated by scamp:


# Because the flux scales refer to an image normalised to one
# second we need to obtain the exposure times of all frames
# first. We also get the SCAMP flux scale and the photometric 
# instrument:
rm photdata.txt_11275
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

  echo ${NAME}" "${EXPTIME}" "${FLXSCALE}" "${PHOTINST} >> photdata.txt_11275
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
           }' photdata.txt_11275 > photdata_relzp.txt_11275

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
done < photdata_relzp.txt_11275
exit_stat=$? #use ${PIPESTATUS[0]} if it's <command> | tee -a OUT-command.log                                                                   
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi

i=1
while [ ${i} -le ${NCATS} ]
do
  if [ -f "${CATBASE[$i]}.head" ]; then
    mv ${CATBASE[$i]}*head ${CATDIR[$i]}/headers_scamp_${STARCAT}/
    exit_stat=$? #use ${PIPESTATUS[0]} if it's <command> | tee -a OUT-command.log                                                                   
    if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
    fi
  fi
  
  i=$(( ${i} + 1 )) 
done
