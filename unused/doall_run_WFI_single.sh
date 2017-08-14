#!/bin/bash

# the script gives the reduction steps for a
# WFI run reduction; ldacpipeline version 0.12.20
# and higher

# the script is called with 
# ./doall_run_marvin.sh -m "MODE1 MODE2 ...."
# the different modes are the following:
#
# - PREPARE:
#   splits data and checks whether the
#   modes of images are within given limits
#
# - BIAS
#   creates master bias images
#
# - FLAT
#   ceated master skyflat images
#
# - CLEANCALIBDIRS
#   deletes all necessary, temporaray files
#   created during the calibration frame processing
#
# - SCIENCE
#   does the preprocessing on science frames
#   (overscan, flatfielding, superflatfielding)
#
# - CLEANSCIENCEDIRS
#   deletes all necessary, temporaray files
#   created during the science frame processing
#   
# - CLEANSTANDARDDIRS
#   deletes all necessary, temporaray files
#   created during the standardstar frame processing
#   
# - MOSAICS
#   creates the small, binned mosaics
#
# - SINGLEASTROM
#   perform singlastrom on run basis (this is mainly for
#   the completeness of the WEB pages to be created on
#   a run basis)
# 
# - WEIGHTS
#   creates weight images
#
# - ABSPHOTOM
#   perform absolute photometry on standardstar
#   observations
#
# - RUNDISTRIBUTE
#   distribute current DPS run into the DPS 
#   set structure  
#
# - OLDRUNPAGES
#   creates WEB pages for the run (old version
#   from Joergs scripts). This step is now done
#   in several steps: RUNCALIBPAGES, RUNSCIENCEPAGES,
#   UPDATERUNSCIENCEPAGES. This step is kept
#   for compatibility reasons.

#
# definitions
#
export INSTRUMENT=WFI
BASEDIR=/raid4/thomas/SABINE/I_EIS
RUN=run_2004_03_14

# root directory for WEB pages:
WEBDIR=/home/www/public_html/IRAN/

# band to be processed (mainly needed to
# decide whether fringing has to be done
# or not (filters are U, B, V, R, I)
FILTER="R"

#
# standard star catalog for U-Band reductions
export USTANDARDSTARCATALOG=/raid4/pipeline/pipecats/Landolt_std_usno1.0.cat

#
# Flatfield to be used (DOMEFLAT or SKYFLAT)
FLATTYPE=SKYFLAT

#
# default survey:
SURVEY=CLUSTERS

#
# read command line arguments
#
MODE=""
GoOn=0
while [ $GoOn = 0 ]
do
   case $1 in
   -b)
       BASEDIR=${2}
       shift 2
       ;;
   -f)       
       FILTER=${2}
       shift 2
       ;; 
   -m)
       MODE=${2}
       shift 2
       ;;
   -r)
       RUN=${2}
       shift 2
       ;; 
   -s)
       SURVEY=${2}
       shift 2
       ;; 
   -t)
       FLATTYPE=${2}
       shift 2
       ;;
    *)
       GoOn=1
       ;;
   esac
done

if [ "${MODE}_A" = "_A" ]; then
  echo "nothing to do: exiting!"
  exit 1
fi

export BASEDIR
export FILTER
export RUN
export MD=${BASEDIR}/${SURVEY}/${FILTER}/${RUN}

# root directory for the sets
export SETDIR=${BASEDIR}/${SURVEY}
export REGDIR=${BASEDIR}/regs/

#
# suffix is a shortcut for filter_run
# This will be the RUN keyword added to all images:
SUFFIX=${FILTER}_${RUN}

# if fringing is done the endings of the
# science fromes in the individual set directories
# are OFCSF instead of OFCSF. This 
if [ "${FILTER}" = "R" ] || [ "${FILTER}" = "I" ] || [ "${FILTER}" = "I_EIS" ]; then
  FRINGING="F"
else
  FRINGING=""
fi

export MAGMIN=-100  # dummy for the automatic absolute photometric
                    # calibration mode
export MAGMAX=100   #      "

# default values for color index, extinction coefficient
# and color term (absolute photometry) in the different
# WFI filters
#
if [ "${FILTER}" = "R" ]; then
    export COLOR=VmR
    export EXT=-0.07
    export COLCOEFF=0.0
    export MAGMIN=24.40  # for the automatic absolute photometric
    export MAGMAX=24.55
fi
if [ "${FILTER}" = "U_35060" ]; then
    export COLOR=UmB
    export EXT=-0.48
    export COLCOEFF=0.05
fi
if [ "${FILTER}" = "U_38" ]; then
    export COLOR=UmB
    export EXT=-0.73
    export COLCOEFF=-0.01
fi
if [ "${FILTER}" = "B" ]; then
    export COLOR=BmV
    export EXT=-0.22
    export COLCOEFF=0.25
    export MAGMIN=24.55  # for the automatic absolute photometric
    export MAGMAX=24.8
fi
if [ "${FILTER}" = "V" ]; then
    export COLOR=VmR
    export EXT=-0.11
    export COLCOEFF=-0.13
    export MAGMIN=24.1  # for the automatic absolute photometric
    export MAGMAX=24.35
fi
if [ "${FILTER}" = "I_EIS" ]; then
    export COLOR=RmI
    export EXT=0.00
    export COLCOEFF=0.03
fi
if [ "${FILTER}" = "I" ]; then
    export COLOR=RmI
    export EXT=-0.10
    export COLCOEFF=0.11
fi

#
# default values for thresshholds of global weights:
#

export FLATMIN=0.7
export FLATMAX=1.3
export SCIENCEMIN=0.9
export SCIENCEMAX=1.1
export DARKMIN=-7
export DARKMAX=7

if [ "${FILTER}" = "I_EIS" ]; then
  SCIENCEMAX=1.15
fi

if [ "${FILTER}" = "U_38" ] || [ "${FILTER}" = "U_35060" ]; then
  FLATMIN=0.5
  SCIENCEMIN=0.6
  SCIENCEMAX=1.4
fi

#
# function definitions
#

#
## Here starts the real work !!!!
#

# preparatory work (splitting of images; checking of integrity)
for mode in ${MODE}
do
  if [ "${mode}" = "PREPARE" ]; then
#     ./process_split_WFI_eclipse.sh ${MD} BIAS  	 
#     ./process_split_WFI_eclipse.sh ${MD} DARK 	 
     ./process_split_WFI_eclipse.sh ${MD} ${FLATTYPE}_${FILTER} 
     ./process_split_WFI_eclipse.sh ${MD} SCIENCE_${FILTER} 

     if [ -d ${MD}/STANDARD_${FILTER} ]; then
       ./process_split_WFI_eclipse.sh ${MD} STANDARD_${FILTER} 
       ./check_files.sh ${MD} STANDARD_${FILTER} "" 100 3500
     fi

     # BIASES from November 2006 have values as low as 60!
#     ./check_files.sh ${MD} BIAS "" 50 250
     ./check_files.sh ${MD} ${FLATTYPE}_${FILTER} "" 5000 45000
     ./check_files.sh ${MD} SCIENCE_${FILTER} "" 120 3000
  fi
done

# creation of master BIAS and master DARKS
for mode in ${MODE}
do
  if [ "${mode}" = "BIAS" ]; then
     ./parallel_manager.sh ./process_bias_eclipse_para.sh ${MD} BIAS
     ./parallel_manager.sh ./create_image_stat.sh ${MD} BIAS "OC."
  fi
done

for mode in ${MODE}
do
  if [ "${mode}" = "DARK" ]; then
     ./parallel_manager.sh ./process_bias_eclipse_para.sh ${MD} DARK
     ./parallel_manager.sh ./create_image_stat.sh ${MD} DARK "OC."
  fi
done

# creation of master FLAT 
for mode in ${MODE}
do
  if [ "${mode}" = "FLAT" ]; then
    ./parallel_manager.sh ./process_flat_eclipse_para.sh ${MD} BIAS ${FLATTYPE}_${FILTER}         
    ./parallel_manager.sh create_norm_para.sh ${MD} ${FLATTYPE}_${FILTER}
    ./parallel_manager.sh ./create_image_stat.sh ${MD} ${FLATTYPE}_${FILTER} "OC."
    ./resolvelinks.sh ${MD}/${FLATTYPE}_${FILTER} ${FLATTYPE}_${FILTER}
  fi
done

# create run web pages for calibration files
for mode in ${MODE}
do
  if [ "${mode}" = "RUNCALIBPAGES" ]; then
    ./create_binnedmosaics.sh ${MD} BIAS BIAS "" 8 -32
    ./create_binnedmosaics.sh ${MD} DARK DARK "" 8 -32
    ./create_binnedmosaics.sh ${MD} ${FLATTYPE}_${FILTER} ${FLATTYPE}_${FILTER} "" 8 -32
    ./pipelog_WFI.py -a runcalib -f ${FILTER} -o ${WEBDIR}\
                                 -b ${BASEDIR}/${SURVEY} -r ${RUN} -w BIAS
    ./pipelog_WFI.py -a runcalib -f ${FILTER} -o ${WEBDIR}\
                                 -b ${BASEDIR}/${SURVEY} -r ${RUN} -w DARK
    ./pipelog_WFI.py -a runcalib -f ${FILTER} -o ${WEBDIR}\
                                 -b ${BASEDIR}/${SURVEY} -r ${RUN}\
                                 -w ${FLATTYPE}_${FILTER}
    ./pipelog_WFI.py -a runindex -f ${FILTER} -o ${WEBDIR}\
                                 -b ${BASEDIR}/${SURVEY} -r ${RUN}
  fi
done

for mode in ${MODE}
do
  if [ "${mode}" = "CLEANCALIBDIRS" ]; then
     ./cleanfiles.sh ${MD}/BIAS WFI "."
     ./cleanfiles.sh ${MD}/DARK WFI "."
     ./cleanfiles.sh ${MD}/${FLATTYPE}_${FILTER} WFI "."
  fi
done  

# preprocessing of science frames
for mode in ${MODE}
do
  if [ "${mode}" = "SCIENCE" ]; then
    # header update 
    ./parallel_manager.sh ./create_runid_para.sh ${MD} SCIENCE_${FILTER} "." ${SUFFIX}
    
    # preprocessing
    if [ "${FILTER}" = "I" ] || [ "${FILTER}" = "I_EIS" ]; then 
       ./parallel_manager.sh ./process_science_eclipse_para.sh ${MD} BIAS ${FLATTYPE}_${FILTER} \
           SCIENCE_${FILTER} NORESCALE FRINGE
    else
       if [ "${FILTER}" = "U_35060" ] || [ "${FILTER}" = "U_38" ]; then
           ./parallel_manager.sh ./process_science_eclipse_para.sh ${MD} BIAS ${FLATTYPE}_${FILTER} \
               SCIENCE_${FILTER} RESCALE NOFRINGE
       else
           ./parallel_manager.sh ./process_science_eclipse_para.sh ${MD} BIAS ${FLATTYPE}_${FILTER} \
               SCIENCE_${FILTER} NORESCALE NOFRINGE
       fi
    fi
    ./parallel_manager.sh ./create_illumfringe_para.sh ${MD} SCIENCE_${FILTER}
    ./resolvelinks.sh ${MD}/SCIENCE_${FILTER} SCIENCE_${FILTER} illum
    
    if [ "${FILTER}" = "U_35060" ] || [ "${FILTER}" = "U_38" ]; then 
       ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${MD} SCIENCE_${FILTER} NORESCALE ILLUM
    else
       ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${MD} SCIENCE_${FILTER} RESCALE ILLUM
    fi
    
    if [ "${FRINGING}" = "F" ]; then
      ./parallel_manager.sh ./process_science_fringe_eclipse_para.sh ${MD} SCIENCE_${FILTER}	     
    fi
  fi
done


# Preprocess standards
for mode in ${MODE}
do
  if [ "${mode}" = "STANDARD" ]; then
    # Preprocess the standards without creating superflat again
    if [ -d ${MD}/STANDARD_${FILTER} ]; then
      if [ "${FILTER}" = "U_35060" ] || [ "${FILTER}" = "U_38" ]; then
        ./parallel_manager.sh ./process_standard_eclipse_para.sh ${MD} BIAS ${FLATTYPE}_${FILTER} SCIENCE_${FILTER} \
  	    STANDARD_${FILTER} RESCALE 
      else
        ./parallel_manager.sh ./process_standard_eclipse_para.sh ${MD} BIAS ${FLATTYPE}_${FILTER} SCIENCE_${FILTER} \
  	STANDARD_${FILTER} NORESCALE 
      fi
      ./parallel_manager.sh ./create_illumfringe_para.sh ${MD} STANDARD_${FILTER}
  
       if [ "${FILTER}" = "U_35060" ] || [ "${FILTER}" = "U_38" ]; then 
         ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${MD} STANDARD_${FILTER} NORESCALE ILLUM
       else
         ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${MD} STANDARD_${FILTER} RESCALE ILLUM
       fi
  
      if [ "${FRINGING}" = "F" ]; then
          ./parallel_manager.sh ./process_science_fringe_eclipse_para.sh ${MD} STANDARD_${FILTER}
      fi
    fi
  fi
done

# clean unnecessary files from the SCIENCE directories 
for mode in ${MODE}
do
  if [ "${mode}" = "CLEANSCIENCEDIRS" ]; then
    if [ "${FRINGING}" = "F" ]; then
      ./cleanfiles.sh ${MD}/SCIENCE_${FILTER}/OFCS_IMAGES WFI OFCS.
    fi
    ./cleanfiles.sh ${MD}/SCIENCE_${FILTER}/OFC_IMAGES WFI OFC.
    ./cleanfiles.sh ${MD}/SCIENCE_${FILTER}/SUB_IMAGES WFI "OFC_sub."
    ./cleanfiles.sh ${MD}/SCIENCE_${FILTER}/SPLIT_IMAGES WFI "."
  fi
done  

# clean unnecessary files from the STANDARD directories 
for mode in ${MODE}
do
  if [ "${mode}" = "CLEANSTANDARDDIRS" ]; then
    if [ "${FRINGING}" = "F" ]; then
      ./cleanfiles.sh ${MD}/STANDARD_${FILTER}/OFCS_IMAGES WFI OFCS.
    fi
    ./cleanfiles.sh ${MD}/STANDARD_${FILTER}/OFC_IMAGES WFI OFC.
    ./cleanfiles.sh ${MD}/STANDARD_${FILTER}/SUB_IMAGES WFI "OFC_sub."
    ./cleanfiles.sh ${MD}/STANDARD_${FILTER}/SPLIT_IMAGES WFI "."
  fi
done  


# create binned mosaics
for mode in ${MODE}
do
  if [ "${mode}" = "MOSAICS" ]; then
     ./create_binnedmosaics.sh ${MD} SCIENCE_${FILTER} "*" OFCS${FRINGING} 8 -32
  fi
done

# create global weight images
for mode in ${MODE}
do
  if [ "${mode}" = "GLOBALWEIGHTS" ]; then
    ./parallel_manager.sh create_norm_para.sh ${MD} SCIENCE_${FILTER}
    ./parallel_manager.sh ./create_global_weights_flags_para.sh ${MD} \
      ${FLATTYPE}_${FILTER}_norm ${FLATMIN} ${FLATMAX} DARK ${DARKMIN} ${DARKMAX} \
      SCIENCE_${FILTER}_norm ${SCIENCEMIN} ${SCIENCEMAX}
  fi
done

# check for the existence of region files
for mode in ${MODE}
do
  if [ "${mode}" = "TESTREG" ]; then
    # REG files are 'defined' to not be present if:
    # - The corresponding reg file directory does not exist
    # - The corresponding reg file directory does exist but
    #   is empty
    # - There are only reg files for short exposures (less than
    #   100 sec.)  
    REGPRESENT=0  
    if [ -d ${REGDIR}/${FILTER}/${RUN} ]; then
      for REGFILE in `find ${REGDIR}/${FILTER}/${RUN} -name \*reg`
      do
        # check exptime of all FITS files of which reg files
        # exist
        FITSFILE=${MD}/SCIENCE_${FILTER}/`basename ${REGFILE} .reg`C.fits
        if [ -f ${FITSFILE} ]; then
          SCIENCE_FILE=`dfits ${FITSFILE} | fitsort -d EXPTIME\
                        | awk '{if($2 > 100.0) { print 1} else {print 0}}'`

          if [ ${SCIENCE_FILE} -eq 1 ]; then
            REGPRESENT=1
          fi
        fi 
      done
    fi
    echo ${REGPRESENT}
  fi
done

# create weight images
for mode in ${MODE}
do
  if [ "${mode}" = "WEIGHTS" ]; then
     # use region files if present:
     if [ ${REGPRESENT} -eq 1 ]; then
       test -d ${MD}/SCIENCE_${FILTER}/reg || mkdir ${MD}/SCIENCE_${FILTER}/reg
       cp ${REGDIR}/${FILTER}/${RUN}/*reg ${MD}/SCIENCE_${FILTER}/reg
     fi
    ./parallel_manager.sh ./create_weights_para.sh ${MD} SCIENCE_${FILTER} OFCS${FRINGING} 
  fi
done

# create Satellite TRACK images
for mode in ${MODE}
do
  if [ "${mode}" = "STRACK" ]; then

      # do nothing if region files are already available:
      REGPRESENT=${REGPRESENT=0}
      if [ ${REGPRESENT} -eq 0 ]; then
        MIN_WIDTH=12
  
        # Create the hough images
        # up now the following script does not work properly
        # on several chips at the same time!
        ./parallel_manager.sh ./create_hough_para.sh ${MD} SCIENCE_${FILTER} OFCS${FRINGING}
  
        # Detect the tracks
        #echo  ./create_strack_mask.sh ${MD} SCIENCE_${FILTER} C
        ./create_strack_mask.sh ${MD} SCIENCE_${FILTER} OFCS${FRINGING} ${MIN_WIDTH}
  
        # Plot the mosaics + tracks
        #echo ./create_strack_plot.sh ${MD} SCIENCE_${FILTER} C
        #./create_strack_plot.sh ${MD} SCIENCE_${FILTER} C
  
        # delete not needes stuff from the track detection.
        # Especially the 'SEG' images are very large:
        ./cleanfiles.sh ${MD}/SCIENCE_${FILTER} '*' "OFCS${FRINGING}_SEG."
        ./cleanfiles.sh ${MD}/SCIENCE_${FILTER} '*' "OFCS${FRINGING}_SEG_hSN."
        ./cleanfiles.sh ${MD}/SCIENCE_${FILTER} '*' "OFCS${FRINGING}_SEG.fits_weight_ref."
        find ${MD}/SCIENCE_${FILTER} -maxdepth 1 -name default\* -exec rm {} \;
        find ${MD}/SCIENCE_${FILTER} -maxdepth 1 -name tmp\* -exec rm {} \;
        find ${MD}/SCIENCE_${FILTER}/cat -maxdepth 1 \
             -name seeing\*cat -exec rm {} \;
        find ${MD}/SCIENCE_${FILTER} -maxdepth 1 -name \*LOG -exec rm {} \;
        find ${MD}/SCIENCE_${FILTER} -maxdepth 1 -name log\* -exec rm {} \;
        find ${MD}/SCIENCE_${FILTER} -maxdepth 1 -name HTweight\*fits\* -exec rm {} \;

        # copy region files to appropriate subdirs of REGDIR
        # and to a reg subdirectory:
        test -d ${MD}/SCIENCE_${FILTER}/reg || mkdir ${MD}/SCIENCE_${FILTER}/reg
        test -d ${REGDIR}/${FILTER}         || mkdir ${REGDIR}/${FILTER}
        test -d ${REGDIR}/${FILTER}/${RUN}  || mkdir ${REGDIR}/${FILTER}/${RUN}
  
        FILES=`find ${MD}/SCIENCE_${FILTER}/STRACK -name \*OFCS${FRINGING}.reg`
        
        for FILE in ${FILES}
        do
          BASE=`basename ${FILE} OFCS${FRINGING}.reg`
          cp ${FILE} ${MD}/SCIENCE_${FILTER}/reg/${BASE}.reg
          cp ${FILE} ${REGDIR}/${FILTER}/${RUN}/${BASE}.reg
        done
      fi
  fi
done

# create initial weight images
for mode in ${MODE}
do
  if [ "${mode}" = "REGIONWEIGHTS" ]; then
    if [ -d  ${MD}/SCIENCE_${FILTER}/reg ] && [ ${REGPRESENT} -eq 0 ]; then
      # first delete old weight files:
      ./cleanfiles.sh ${MD}/WEIGHTS '*' "OFCS${FRINGING}.weight."

      ./parallel_manager.sh ./create_weights_para.sh ${MD} SCIENCE_${FILTER} \
                            "OFCS${FRINGING}" ${RETINAFILTER}
      ./parallel_manager.sh ./create_bitpixchange.sh ${MD} WEIGHTS \
	                    "?" "OFCS${FRINGING}.weight." 8
    fi
  fi
done


# create weight images, astrometrically calibrate standard
# images. Do photometric calibration
for mode in ${MODE}
do
  if [ "${mode}" = "ABSPHOTOM" ]; then
    if [ -d ${MD}/STANDARD_${FILTER} ]; then
      ./parallel_manager.sh ./create_weights_flags_para.sh ${MD} STANDARD_${FILTER} OFCS${FRINGING} WEIGHTS_FLAGS
  
      if [ "${FILTER}" = "U_35060" ] || [ "${FILTER}" = "U_38" ]; then
        ./parallel_manager.sh ./create_astrom_std_para.sh ${MD} STANDARD_${FILTER} \
                              OFCS${FRINGING} ${USTANDARDSTARCATALOG}
      else
        ./parallel_manager.sh ./create_astrom_std_para.sh ${MD} STANDARD_${FILTER} \
                              OFCS${FRINGING} default
      fi
  
      if [ "${FILTER}" = "U_35060" ] || [ "${FILTER}" = "U_38" ]; then
        ./create_abs_photo_info.sh ${MD} STANDARD_${FILTER} SCIENCE_${FILTER} OFCS${FRINGING} \
                                   ${FILTER} U ${COLOR} ${EXT} ${COLCOEFF}\
                                   AUTOMATIC ${MAGMIN} ${MAGMAX}
      else
        if [ "${FILTER}" = "I_EIS" ]; then
          ./create_abs_photo_info.sh ${MD} STANDARD_${FILTER} SCIENCE_${FILTER} OFCS${FRINGING} \
                                     ${FILTER} I ${COLOR} ${EXT} ${COLCOEFF} \
                                     AUTOMATIC ${MAGMIN} ${MAGMAX}
        else
          ./create_abs_photo_info.sh ${MD} STANDARD_${FILTER} SCIENCE_${FILTER} OFCS${FRINGING} \
                                     ${FILTER} ${FILTER} ${COLOR} ${EXT} ${COLCOEFF}\
                                     AUTOMATIC ${MAGMIN} ${MAGMAX}
        fi
      fi
    fi
    ./create_zp_correct_header.sh ${MD} SCIENCE_${FILTER} OFCS${FRINGING}
  fi
done

# perform astrometry on run basis (this is mainly to be able to create
# WEB pages on the run basis)

for mode in ${MODE}
do
  if [ "${mode}" = "SINGLEASTROM" ]; then
    ./parallel_manager.sh ./create_astromcats_weights_para.sh ${MD} \
           SCIENCE_${FILTER} OFCS${FRINGING} \
           WEIGHTS OFCS${FRINGING}.weight
    #
    # to make things simple for the WEB page creation we create
    # PSF checkplots for all colours 
    ./parallel_manager.sh ./check_science_PSF_para.sh ${MD} \
            SCIENCE_${FILTER} OFCS${FRINGING}
    ./check_science_PSF_plot.sh ${MD} SCIENCE_${FILTER} OFCS${FRINGING}
    ./merge_sex_ksb.sh ${MD} SCIENCE_${FILTER} OFCS${FRINGING}
    ./create_stats_table.sh ${MD} SCIENCE_${FILTER} OFCS${FRINGING}
  fi
done

# Create web pages for SCIENCE frames
for mode in ${MODE}
do
  if [ "${mode}" = "RUNSCIENCEPAGES" ]; then
    ./pipelog_WFI.py -a runscience -f ${FILTER} -o ${WEBDIR}\
            -b ${BASEDIR}/${SURVEY} -r ${RUN} -e OFCS${FRINGING}
    ./pipelog_WFI.py -a runindex -f ${FILTER} -o ${WEBDIR}\
            -b ${BASEDIR}/${SURVEY} -r ${RUN}
  fi
done

# subtract the sky from science images:
for mode in ${MODE}
do
  if [ "${mode}" = "SKYSUB" ]; then
     ./parallel_manager.sh ./create_skysub_para.sh  ${MD} SCIENCE_${FILTER}\
            OFCS${FRINGING} ".sub" TWOPASS
  fi
done


# Update SCIENCE WWW pages with ZPs
for mode in ${MODE}
do
  if [ "${mode}" = "UPDATERUNSCIENCEPAGES" ]; then
    ./pipelog_WFI.py -a runscience -f ${FILTER} -o ${WEBDIR} -b ${BASEDIR} -r ${RUN} -e OFCS${FRINGING} -u
  fi
done

# distribute current run
for mode in ${MODE}
do
  if [ "${mode}" = "RUNDISTRIBUTE" ]; then
    ./parallel_manager.sh ./link_sets_WFI_para.sh ${MD} SCIENCE_${FILTER} \
                          OFCS${FRINGING} ${FILTER} ${SETDIR} ${SURVEY}
  fi
done
