#!/bin/bash

# the script gives the reduction steps for a
# set reduction of WFI data. This version
# is for use on a single processor machine

#
# HISTORY COMMENTS:
#
# 08.02.2008:
# first script version

# the script is called with 
# ./doall_set_WFI_single.sh -m "MODE1 MODE2 ...."
# the different modes are the following:
#
# - ASTROMPHOTOM
#   does astrometric and photometric calibration
#   via ASTROMETRIX and PHOTOMETRIX
#
# - SETCHECKPLOT
#   creates checkplot (with seeing dist., ellipticities
#   etc.) for to set to be processed 
#  
# - COADD
#   do image coaddition with eisdrizzle or swarp
#
# - POSTCOADD
#   create a first SExtractor catalog and produce basic
#   science verification of data (mag-rh diagram,
#   galaxy number counts)
#   (NOT YET DONE PROPERLY)
#
# - COADDHEADERUPDATE
#   updates the final coadded image header with EXPTIME
#   GAIN and MAGZP information
#   (NOT YET DONE PROPERLY; e.g. the gain is not correct
#   when data are not co-added with a mean co-addition)
#
# - SETPAGES
#   create WEB pages for the sets
#
# - CLEANORIG
#   restore the original state of the run directories
#   after Elixir processed files were moved to them,
#
# - CLEANNEWCOADD
#   remove all 'derived' products except final files
#   from the co-addition process. This mode should be 
#   used if the same set directory has to be reused for
#   a completely new co-addition (e.g. Ludo's PSF project).
#
# - FINALCLEAN
#   delete completely the contents of the set and setweights
#   directories.

#
# Definitions and default variable values
#

#
# DO NOT TOUCH the following line!!
export INSTRUMENT=WFI

# The variables MD, WEBDIR, COADDIDENT, COADDCONDITION,
# FIELD and FILTER are typically passed on the command line.
# If they are not passed the following 'defaults' are used: 

# Main directory for SET
# data. 
# Below, the set MDROOT is modified to MDROOT/${SURVEY} which
# is called MD then.
MDROOT=/raid1/thomas/

# root directory for WEB pages. It will be modified
# below to WEBDIR=${WEBDIRROOT}/${SURVEY}WWW to give
# the final location of WWW pages.
WEBDIRROOT=/home/www/public_html/

# default identifier for coaddition)
COADDIDENT="V1.7A"

# default method for final image coaddition used
# by swarp
COADDMETHOD=MEDIAN
 
#
# default field selection for coaddition (LDAC filter format)
COADDCONDITION="(SEEING<2.0);"

# which field should be processed
FIELD=A226

# Survey to process; below we have special settings for
# each known survey. This includs special processing
# and directory settings.
SURVEY=CLUSTERS

# band to be processed (filters are U_38, U_35060, B, V, R, I, I_EIS ...)
FILTER="R"

# dummy setting for magnitude zeropoint. We need this
# to detect if the zeropoint was given on the command line. 
MAGZP=-1.0

#
# default catalog used for ASTROMETRIX (-s catalog parameter
# in ASTROMETRIX). DO NOT TOUCH!!
ASTROMETRIXCAT=USNOB1

# 
# default standardstar catalogue for scamp
SCAMPCAT=SDSS-R5

#
# default method for astrometry (possible are ASTROMETRIX and SCAMP
ASTROMETRYMETHOD=ASTROMETRIX
ASTROMADD="" # for scamp headers etc. are in a directory header_scamp
             # If ASTROMETRYMETHOD=SCAMP this variable will be set to
             # "_scamp" and used at appropriate places.

#
# by default we co-add all the chips:
CHIPS="ALL"

#
# read command line arguments
#
MODE=""
GoOn=0
while [ $GoOn = 0 ]
do
   case $1 in
   -b)
       MDROOT=${2}
       shift 2
       ;;
   -fi)
       FIELD=${2}
       shift 2
       ;;
   -f)
       FILTER=${2}
       shift 2
       ;;
   -ci)
       COADDIDENT=${2}
       shift 2
       ;;
   -chips)
       CHIPS="${2}"
       shift 2
       ;;
   -cc)
       COADDCONDITION=${2}
       shift 2
       ;;
   -cm)
       COADDMETHOD=${2}
       shift 2
       ;;
   -m)
       MODE=${2}
       shift 2
       ;;
   -ma)
       MAGZP=${2}
       shift 2
       ;;
   -a)
       ASTROMETRIXCAT=${2}
       shift 2
       ;;
   -am)
       ASTROMETRYMETHOD=${2}
       shift 2
       ;;
   -s)
       SURVEY=${2}
       shift 2
       ;;
   -www)
       WEBDIRROOT=${2}
       shift 2
       ;;
    *)
       if [ $# -ge 1 ]; then
         echo "Unknown command line option: ${1}"
         exit 1	   
       else
         GoOn=1
       fi
       ;;
   esac
done

export FILTER
export FIELD
export COADDIDENT

# sanity checks:
if [ "${MODE}_A" = "_A" ]; then
  echo "nothing to do: exiting!"
  exit 1
fi

if [ "${ASTROMETRYMETHOD}" != "ASTROMETRIX" ] && \
   [ "${ASTROMETRYMETHOD}" != "SCAMP" ]; then
  echo "Unknown astrometry method! Only SCAMP and ASTROMETRIX are supported!"
  exit 1;
fi

if [ "${ASTROMETRYMETHOD}" = "SCAMP" ]; then
  ASTROMADD="_scamp"
fi
 
#
# center coordinates for the different surveys:
#
if [ "${SURVEY}" = "CLUSTERS" ]; then
  A226="24.74166667 -10.24666667"
fi

# root directory for WEB pages (not absolutely necessary;
# the script has full reduction capabilities without the
# WWW option). The WEBDIR is dependent on the set SURVEY.
# Therefore this variable is set here.
WEBDIR=${WEBDIRROOT}/IRAN

# Main directory for SET
# data. 
# The actual images to
# process reside in ${MD}/${FIELD}/${FILTER}
# and the weights in ${MD}/${FIELD}/WEIGHTS_${FILTER}.
export MD=${MDROOT}/${SURVEY}

# set the reduce directory. We assume that this script
# is called within the reduce directory:
export REDDIR=`pwd`

#
# ENDING has to be .sub. here. DO NOT EDIT!!
export ENDING=".sub"

# if fringing is done the endings of the
# science fromes in the individual set directories
# are OFCSF instead of OFCSF. This 
if [ "${FILTER}" = "R" ] || [ "${FILTER}" = "I" ] ||\
   [ "${FILTER}" = "I_EIS" ]; then
  FRINGING="F"
else
  FRINGING=""
fi

#
# here starts the real work !!
#
for mode in ${MODE}
do
  if [ "${mode}" = "ASTROMPHOTOM" ]; then
     #
     # mark bad chips if necessary!
     # Our strategy is to mark chips as bad which were bad in the reference
     # image. Hence, also chips that are physically ok in other colours can be
     # marked as bad!
     for BADCHIPFILE in ${FIELD}_badchips.txt ${FIELD}_${FILTER}_badchips.txt
     do
       if [ -f ${BADCHIPFILE} ]; then
         ./mark_badchips.sh ${MD}/${FIELD} ${FILTER} OFCS${FRINGING}.sub 1 ${BADCHIPFILE}
         ./mark_badchips.sh ${MD}/${FIELD} ${FILTER} OFCS${FRINGING} 1 ${BADCHIPFILE}
       fi
     done  

     if [ "${ASTROMETRYMETHOD}" = "ASTROMETRIX" ]; then
         # initial SExtractor catalogues were already created during the
         # RUN phase and copied to the SET directories!!
         #
         ./create_run_list.sh ${MD}/${FIELD} ${FILTER} OFCS${FRINGING} RUN uniqruns_$$.txt NOSPLIT
     
         # build the string containing the individual runs in this set
         RUNS=""
         NRUNS=0
         while read run
         do
             RUNS="${RUNS} ${REDDIR}/${run}.txt"
             NRUNS=$(( ${NRUNS} + 1 ))
         done < uniqruns_$$.txt
    
         ./create_astrometrix_astrom_run.sh ${MD}/${FIELD} ${FILTER} OFCS${FRINGING}\
                  ${ASTROMETRIXCAT} ${RUNS}
         ./create_photometrix.sh ${MD}/${FIELD} ${FILTER} OFCS${FRINGING}
     else   # von ASTROMETRYMETHOD
         ./create_scamp_astrom_photom.sh ${MD}/${FIELD} ${FILTER} OFCS${FRINGING}\
                  ${SCAMPCAT}
     fi     # von ASTROMETRYMETHOD
     ./create_stats_table.sh ${MD}/${FIELD} ${FILTER} OFCS${FRINGING} headers${ASTROMADD}

     PHOTFLAG=""
     if [ -f ${FIELD}_${FILTER}_phot.txt ]; then
         PHOTFLAG=`cat ${FIELD}_${FILTER}_phot.txt`
     fi

     ./create_absphotom_photometrix.sh ${MD}/${FIELD} ${FILTER} ${PHOTFLAG}
  fi
done

for mode in ${MODE}
do
  if [ "${mode}" = "SETCHECKPLOT" ]; then
      CAT=chips.cat5
      if [ -f ${MD}/${FIELD}/${FILTER}/cat/chips.cat6 ]; then
	   CAT=chips.cat6
      fi
      ./make_checkplot_stats.sh ${MD}/${FIELD} ${FILTER} ${CAT} STATS ${FILTER}
  fi
done

# do the coaddition (SWARP)
for mode in ${MODE}
do
  if [ "${mode}" = "COADD" ]; then
      RA=`echo ${!FIELD} | awk '{print $1}'`
      DEC=`echo ${!FIELD} | awk '{print $2}'`

      # The following definition of TWO variables appears
      # because I did not succeed in passing command line
      # arguments properly to the following prepare_coadd ...
      # script when trying with only one variable (paranthesis
      # issues)
      if [ "${CHIPS}" = "ALL" ]; then
          CHIPSCOADDFLAG=""
          CHIPSCOADD=""
      else
          CHIPSCOADDFLAG=-c
          CHIPSCOADD="${CHIPS}"
      fi

      if [ "${COADDCONDITION}_A" = "_A" ]; then
          ./prepare_coadd_swarp.sh -m ${MD}/${FIELD} \
                                   -s ${FILTER} -eh headers${ASTROMADD}\
                                   -e "OFCS${FRINGING}${ENDING}" -n ${COADDIDENT} \
                                   -w "${ENDING}" \
                                   -wd WEIGHTS_${FILTER} -r ${RA} \
                                   -d ${DEC} \
                                   ${CHIPSCOADDFLAG} "${CHIPSCOADD}"
      else
        if [ -f ${MD}/${FIELD}/${FILTER}/cat/chips.cat6 ]; then
          CAT=chips.cat6
        else
          CAT=chips.cat5	 
        fi
  
        ./prepare_coadd_swarp.sh -m ${MD}/${FIELD} -s ${FILTER} \
                                 -e "OFCS${FRINGING}${ENDING}" -n ${COADDIDENT} -w "${ENDING}" \
                                 -wd WEIGHTS_${FILTER} -r ${RA} -d ${DEC} \
                                 -eh headers${ASTROMADD}\
                                 -l ${MD}/${FIELD}/${FILTER}/cat/${CAT} STATS\
                                    ${COADDCONDITION} \
                                    ${MD}/${FIELD}/${FILTER}/cat/${COADDIDENT}.cat \
                                    ${CHIPSCOADDFLAG} "${CHIPSCOADD}"
      fi
      ./parallel_manager.sh ./resample_coadd_swarp_CFHTLS_para.sh ${MD}/${FIELD} \
                              ${FILTER} "OFCS${FRINGING}${ENDING}" ${COADDIDENT} ${REDDIR}
      ./parallel_manager.sh ./create_modesub_para.sh ${MD}/${FIELD}/${FILTER} \
                             coadd_${COADDIDENT} ? OFCS${FRINGING}${ENDING}.${COADDIDENT}.resamp.
      ./perform_coadd_swarp.sh ${MD}/${FIELD} ${FILTER} ${COADDIDENT} \
                               ${COADDMETHOD}

      DIR=`pwd`
      cd ${MD}/${FIELD}/${FILTER}/coadd_${COADDIDENT}
      mv coadd.fits ${FIELD}_${FILTER}.${COADDIDENT}.swarp.fits
      mv coadd.flag.fits ${FIELD}_${FILTER}.${COADDIDENT}.swarp.flag.fits
      mv coadd.weight.fits ${FIELD}_${FILTER}.${COADDIDENT}.swarp.weight.fits
      cd ${DIR}
  fi
done

# update header from the final coadded images
#
for mode in ${MODE}
do
  if [ "${mode}" = "COADDHEADERUPDATE" ]; then
      if [ "${MAGZP}" = "-1.0" ]; then 
        if [ -f ${MD}/${FIELD}/${FILTER}/cat/chips_phot.cat5 ]; then
          MAGZP=`ldactoasc -i ${MD}/${FIELD}/${FILTER}/cat/chips_phot.cat5 -t ABSPHOTOM -k COADDZP | tail -n 1`
        fi
      fi

      ./update_coadd_header.sh ${MD}/${FIELD} ${FILTER} ${COADDIDENT} STATS\
                               ${FIELD}_${FILTER}.${COADDIDENT}.swarp \
                               ${MAGZP} Vega "${COADDCONDITION}"
  fi
done

# do the postcoaddition (catalog creation and basic
# science verification)
#
for mode in ${MODE}
do
  if [ "${mode}" = "POSTCOADD" ]; then
      if [ "${MAGZP}" = "-1.0" ]; then 
        if [ -f ${MD}/${FIELD}/${FILTER}/cat/chips_phot.cat5 ]; then
          MAGZP=`ldactoasc -i ${MD}/${FIELD}/${FILTER}/cat/chips_phot.cat5 -t ABSPHOTOM -k COADDZP | tail -n 1`
        fi
      fi

      ./create_catalogue.sh ${MD}/${FIELD} ${FILTER} ${MAGZP} \
                            ${COADDIDENT} ${FIELD}_${FILTER}.${COADDIDENT}.swarp

      if [ "${MAGZP}" != "-1.0" ]; then
        ./create_checkplot_rh_mag.sh ${MD}/${FIELD} ${FILTER} \
                              ${FIELD}_${FILTER}.${COADDIDENT}.swarp 0.95 5.5 17.5
        ./mag_distribution_korr.sh ${MD}/${FIELD} ${FILTER} \
                              ${FIELD}_${FILTER}.${COADDIDENT}.swarp ${FILTER} \
                              0.95 5.5 17.5 "CDFS number counts"
      fi
      ldacfilter -i ${MD}/${FIELD}/${FILTER}/cat/${COADDIDENT}.cat \
                 -o ${MD}/${FIELD}/${FILTER}/cat/${COADDIDENT}_filt.cat -t STATS\
                 -c "(${COADDIDENT}=1);"

      ./make_checkplot_stats.sh ${MD}/${FIELD} ${FILTER} ${COADDIDENT}_filt.cat \
                 STATS coadd_${COADDIDENT}

      rm ${MD}/${FIELD}/${FILTER}/cat/${COADDIDENT}_filt.cat
  fi
done

for mode in ${MODE}
do
  if [ "${mode}" = "SETPAGES" ]; then
    ./pipelog_WFI.py -a setpages -f ${FILTER} -e OFCS${FRINGING} -o ${WEBDIR} -b ${MD} \
        -d sub -r ${FIELD} -i ${COADDIDENT} 
  fi
done

# remove all 'derived' products and restore the state after data
# have been moved from the run directories.
for mode in ${MODE}
do
  if [ "${mode}" = "CLEANORIG" ]; then

      if [ -d ${MD}/${FIELD}/${FILTER}/astrom ]; then
          rm -rf ${MD}/${FIELD}/${FILTER}/astrom
      fi

      if [ -d ${MD}/${FIELD}/${FILTER}/photom ]; then
          rm -rf ${MD}/${FIELD}/${FILTER}/photom
      fi

      if [ -d ${MD}/${FIELD}/${FILTER}/headers ]; then
          rm -rf ${MD}/${FIELD}/${FILTER}/headers
      fi

      if [ -d ${MD}/${FIELD}/${FILTER}/plots ]; then
          rm -rf ${MD}/${FIELD}/${FILTER}/plots
      fi

      if [ -d ${MD}/${FIELD}/${FILTER}/postcoadd ]; then
          rm -rf ${MD}/${FIELD}/${FILTER}/postcoadd
      fi

      COADDDIRS=`find ${MD}/${FIELD}/${FILTER}/ -type d -name coadd_\*`
      for dir in ${COADDDIRS}
      do
	  rm -rf ${dir}
      done
  fi
done

# remove all 'derived' products except final files
# from the co-addition process.
for mode in ${MODE}
do
  if [ "${mode}" = "CLEANNEWCOADD" ]; then

      if [ -d ${MD}/${FIELD}/${FILTER}/astrom ]; then
          rm -rf ${MD}/${FIELD}/${FILTER}/astrom
      fi

      if [ -d ${MD}/${FIELD}/${FILTER}/photom ]; then
          rm -rf ${MD}/${FIELD}/${FILTER}/photom
      fi

      if [ -d ${MD}/${FIELD}/${FILTER}/headers ]; then
          rm -rf ${MD}/${FIELD}/${FILTER}/headers
      fi

      CURDIR=`pwd`
      COADDDIRS=`find ${MD}/${FIELD}/${FILTER}/ -type d -name coadd_\*`
      for dir in ${COADDDIRS}
      do
          cd ${dir}
          rm *resamp*fits
          rm *sub*fits
          rm *head
      done
      cd ${CURDIR}
  fi
done

# clean up set and setweights directories completely
for mode in ${MODE}
do
  if [ "${mode}" = "FINALCLEAN" ]; then
     DIR=`pwd` 

     cd ${MD}/${FIELD}/${FILTER} 
     rm -rf *
     cd ${MD}/${FIELD}/WEIGHTS_${FILTER} 
     rm -rf *

     cd ${DIR}
  fi
done
