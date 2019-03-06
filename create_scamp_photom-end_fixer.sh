#!/bin/bash
set -xvu
#adam-example# ./create_scamp_photom-end_fixer.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B_2015-12-15_CALIB SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-V SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-V_2009-01-23_CALIB SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-RC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-RC_2009-01-23_CALIB SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-IC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-IC_2006-12-21_CALIB SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+ SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+_2015-12-15_CALIB SCIENCE 30000 PANSTARRS 2>&1 | tee -a OUT-create_scamp_photom-end_no_overwrite_MACS0429-02.log
ending="OCF*I"

# File inclusions:
if [ -z ${INSTRUMENT} ] ;then
	INSTRUMENT="SUBARU"
fi
. ${INSTRUMENT:?}.ini > /tmp/SUBARU.out 2>&1

### we can have different INSTRUMENTs
. progs.ini > /tmp/progs.out 2>&1

NCHIPSMAX=10
NCHIPS=${NCHIPSMAX:-10}

# define THELI_DEBUG and some other variables because of the '-u'
# script flag (the use of undefined variables will be treated as
# errors!)  THELI_DEBUG is used in the cleanTmpFiles function.
# 
THELI_DEBUG=${THELI_DEBUG:-""}
P_SCAMP=${P_SCAMP:-""}
P_ACLIENT=${P_ACLIENT:-""}

function cleanTmpFiles
{
    if [ -z ${THELI_DEBUG} ]; then
        echo "Cleaning temporary files for script $0"
        test -f "photdata.txt_$$"           && rm -f photdata.txt_$$
        test -f "photdata_relzp.txt_$$"     && rm -f photdata_relzp.txt_$$
    else
        echo "Variable THELI_DEBUG set! No cleaning of temp. files in script $0"    
    fi
}

# The number of different image directories we have to consider:
NDIRS=$(( ($# - 1) / 2 ))

# get the used reference catalogue into a variable
STARCAT=${!#}
nTHRESHOLD=$(($# - 1))
THRESHOLD=${!nTHRESHOLD}
echo "adam-look: NDIRS=" $NDIRS
echo "adam-look: THRESHOLD=" $THRESHOLD
echo "adam-look: STARCAT=" $STARCAT
## adam-note: I believe this could be a one-script thing if I just put this here:
#adam-SHNT# I'd have to uncomment this line though:
#./create_scamp_photom-middle_combine_dirs.sh ${cluster} W-J-B W-J-B

# Test existence of image directory(ies) and create headers_scamp
# directories:
i=1 
j=2
k=1

while [ ${k} -le ${NDIRS} ]
do 
  if [ -d /${!i}/${!j} ]; then
      if [ -d /${!i}/${!j}/headers_scamp_photom_${STARCAT} ]; then
          mv /${!i}/${!j}/headers_scamp_photom_${STARCAT} /${!i}/${!j}/headers_scamp_photom_${STARCAT}_unfixed
      fi
      mkdir /${!i}/${!j}/headers_scamp_photom_${STARCAT}
  else
      echo "Can't find directory /${!i}/${!j}"; 
      exit 1;
  fi

  if [ ! -d /${!i}/${!j}/headers_scamp_${STARCAT} ]; then
      echo "No existing header directory in /${!i}/${!j}"; 
      exit 1;
  fi

  i=$(( ${i} + 2 ))
  j=$(( ${j} + 2 ))
  k=$(( ${k} + 1 ))
done


##
## Here the main script starts:
##
DIR=`pwd`

ALLMISS=""
l=0
while [ ${l} -le ${NCHIPS} ]
do
  ALLMISS="${ALLMISS}${l}"
  l=$(( ${l} + 1 ))
done

# all processing is performed in the 'first' image directory in
# a astrom_photom_scamp subdirectory:
cd /$1/$2/

if [ ! -d astrom_photom_scamp_${STARCAT} ]; then
    echo "No scamp directory in /$1/$2/astrom_photom_scamp_${STARCAT}"; 
    exit 1;
fi

cd astrom_photom_scamp_${STARCAT}/cat_photom

# filter input catalogues to reject bad objects
i=1
j=2
l=1
NCATS=0
CATDIR_uniq=""

while [ ${l} -le ${NDIRS} ]
do 
  FILES=`${P_FIND} /${!i}/${!j}/cat_scampIC/ -maxdepth 1 -name \*.cat`

  for CAT in ${FILES}
  do
    NCATS=$(( ${NCATS} + 1 ))

    BASE=`basename ${CAT} .cat`

    CATBASE[${NCATS}]=`echo ${BASE} | perl -e '<STDIN> =~ /(.+_\d+)/; print "$1\n";'`
    CATDIR[${NCATS}]=/${!i}/${!j}
  done
  CATDIR_uniq="${CATDIR_uniq} /${!i}/${!j}"
  i=$(( ${i} + 2 ))
  j=$(( ${j} + 2 ))
  l=$(( ${l} + 1 ))
done

export cluster=MACS0429-02
export NCHIPS=10
export ALLIMAGES=' SUPA0154627 SUPA0154628 SUPA0154629 SUPA0154630 SUPA0154631 SUPA0154632 SUPA0154633 SUPA0154634 SUPA0154635 SUPA0154636 SUPA0154625 SUPA0154626 SUPA0043645 SUPA0043646 SUPA0043647 SUPA0043648 SUPA0043649 SUPA0043650 SUPA0105789 SUPA0043636 SUPA0043637 SUPA0043638 SUPA0043639 SUPA0043640 SUPA0043641 SUPA0043642 SUPA0043643 SUPA0105809 SUPA0050792 SUPA0050796 SUPA0050797 SUPA0050798 SUPA0050799 SUPA0050800 SUPA0050801 SUPA0050791 SUPA0154640 SUPA0154641 SUPA0154642 SUPA0154643 SUPA0154644 SUPA0154645 SUPA0154646 SUPA0154647 SUPA0154648 SUPA0154649 SUPA0154650 SUPA0154651 SUPA0154652 SUPA0154653 SUPA0154638 SUPA0154639'
#export CATDIR_uniq=' //gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B/SCIENCE //gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B_2015-12-15_CALIB/SCIENCE //gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-V/SCIENCE //gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-V_2009-01-23_CALIB/SCIENCE //gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-RC/SCIENCE //gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-RC_2009-01-23_CALIB/SCIENCE //gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-IC/SCIENCE //gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-IC_2006-12-21_CALIB/SCIENCE //gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+/SCIENCE //gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+_2015-12-15_CALIB/SCIENCE'
#export NCATS=309
cd ../headers_photom

test -f photdata.txt_$$ && rm -f photdata.txt_$$

# Because the flux scales refer to an image normalised to one
# second we need to obtain the exposure times of all frames
# first. We also get the SCAMP flux scale and the photometric 
# instrument:
for IMAGE in ${ALLIMAGES}
do
  NAME=${IMAGE}
  EXPTIME=`${P_LDACTOASC} -i ../cat_photom/${IMAGE}_scamp.cat \
                     -t LDAC_IMHEAD -s |\
           fold | grep EXPTIME | ${P_GAWK} '{print $3}'`
  if [ -z ${EXPTIME} ]; then EXPTIME=`${P_LDACTOASC} -i ../cat/${IMAGE}_scamp.cat -t LDAC_IMHEAD -s | fold | grep EXPTIME | ${P_GAWK} '{print $3}'` ; echo "adam-look: from cat (not cat_photom): EXPTIME=${EXPTIME}"  ; fi
  if [ -z ${EXPTIME} ]; then EXPTIME=`${P_LDACTOASC} -i /nfs/slac/g/ki/ki05/anja/SUBARU/MACS0429-02//W-J-V/SCIENCE/astrom_photom_scamp_2MASS//cat_photom//${IMAGE}_scamp.cat -t LDAC_IMHEAD -s | fold | grep EXPTIME | ${P_GAWK} '{print $3}'` ; echo "adam-look: from OLD ki-05 cat dir (not cat_photom): EXPTIME=${EXPTIME}"  ; fi
  if [ -z ${EXPTIME} ]; then exit 1 ;fi
  echo "adam-look2: EXPTIME=${EXPTIME}" 
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

if [ -f "${cluster}_checkZP.dat" ]; then
    rm -f ${cluster}_checkZP.dat
fi

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
        ocat_photom=`\ls ../cat_photom/${NAME}_${i}${ending}.ldac`
        if [ ! -f "${ocat_photom}" ]; then
            ocat_photom=`\ls ../cat_photom/${NAME}_${i}[!0-9]*I.ldac`
            ocat_photom_mode=2
        else
            ocat_photom_mode=1
        fi
        if [ -f "${ocat_photom}" ]; then
            if [ "${ocat_photom_mode}" -eq 1 ]; then
                headername=`basename ../cat_photom/${NAME}_${i}${ending}.ldac .ldac | perl -e '<STDIN> =~ /(.+_\d+)/; print "$1\n";'`
            elif [ "${ocat_photom_mode}" -eq 2 ]; then
                headername=`basename ../cat_photom/${NAME}_${i}[!0-9]*I.ldac .ldac | perl -e '<STDIN> =~ /(.+_\d+)/; print "$1\n";'`
            fi
            
            if [ ${j} -eq 1 ];then
                OLDRZP=`awk 'BEGIN{print '${RELZP}'}'`
                for possible_dir in ${CATDIR_uniq}
                do 
                    if [ -f ${possible_dir}/headers_scamp_${STARCAT}/${headername}.head ]; then
                        Nlines=`grep RZP ${possible_dir}/headers_scamp_${STARCAT}/${headername}.head | wc -l `
			if [[ ${Nlines} == "1" ]]; then
                        	OLDRZP=`grep RZP ${possible_dir}/headers_scamp_${STARCAT}/${headername}.head | awk '{print $3}'`
			elif [[ ${Nlines} == "2" ]]; then
                        	OLDRZP=`grep OLDRZP ${possible_dir}/headers_scamp_${STARCAT}/${headername}.head | awk '{print $3}'`
			else
				exit 1
			fi
                        diff=`awk 'BEGIN{printf "%i\n",sqrt(('${RELZP}'-1.0*'${OLDRZP}')*('${RELZP}'-1.0*'${OLDRZP}'))+0.5}'`
                        faint=`awk 'BEGIN{if('${RELZP}'<-0.5) print "1"; else print "0"}'`
                        if [ ${diff} -ge 1 ] || [ ${faint} -eq 1 ]; then
                            echo "adam-Error:Must check the ZP for NAME=${NAME} (diff=$diff and faint=$faint )! see entry in \${cluster}_checkZP.dat ( ${NAME} ${OLDRZP} ${RELZP} >> ${cluster}_checkZP.dat ) "
                            echo ${NAME} ${OLDRZP} ${RELZP} >> ${cluster}_checkZP.dat
                        fi
                        break
                    fi
                done
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
                             printf("OLDRZP  = %20f / THELI RZP from astrometric matching\n",
                                    '${OLDRZP}');
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
    mv ${CATBASE[$i]}.head ${CATDIR[$i]}/headers_scamp_photom_${STARCAT}
    exit_stat=$?
    if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
    fi
  fi

  i=$(( ${i} + 1 ))
done

# clean up temporary files and bye
cleanTmpFiles

cd ${DIR}
#log_status $exit_status
exit $exit_stat
