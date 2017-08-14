#! /bin/bash -x

### superscript template to do the preprocessing
### $Id: do_Subaru_0025_I.sh,v 1.1 2008-08-13 20:54:13 pkelly Exp $


. progs.ini

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki02/xoc/anja/SUBARU

#run=2005-11-30
#filter=W-J-B
run=2006-12-21
filter=W-C-IC
STANDARDSTARTYPE=3SEC
IMGSDSS=SUPA0050734
IMGTOCAL=SUPA0050736




export BONN_TARGET=${run}
export BONN_FILTER=${filter}

#only choice of flat
FLAT=SKYFLAT        # SKYFLAT or DOMEFLAT
SET=SET3            # sets time period of flat to use
SKYBACK=32          # in case of SKYFLAT: size of background mesh for superflat
                    # illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?)
                    # 16 (or 32) if lots of blobs

FRINGE=FRINGE       # FRINGE if fringing correction necessary; NOFRINGE otherwise
STANDARDSTARS=1     # process the STANDARD frames, too  (1 if yes; 0 if no)

if [ ${FRINGE} == "FRINGE" ]; then
    ending="OCFSF"
elif [ ${FRINGE} == "NOFRINGE" ]; then
    ending="OCFS"
else
    echo "You need to specify FRINGE or NOFRINGE for the fringing correction!"
    exit 2;
fi

SCIENCEDIR=SCIENCE_${FLAT}_${SET}

export TEMPDIR='.'
#Comment out the lines as you progress through the script



########################################
### Reset Logger
./BonnLogger.py clear

##################################################################
### create and load the SUBARU.ini file
### !!! DO NOT COMMENT THIS BLOCK !!!
##################################################################

./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/STANDARD/ORIGINALS
export INSTRUMENT=SUBARU

. ${INSTRUMENT:?}.ini
##################################################################
### Capture Variables
./BonnLogger.py config \
    run=${run} \
    filter=${filter} \
    FLAT=${FLAT} \
    SET=${SET} \
    SKYBACK=${SKYBACK} \
    FRINGE=${FRINGE} \
    STANDARDSTARS=${STANDARDSTARS} \
    config=${config}


#
#################################################################################
#### STANDARD star processing
#################################################################################


#if [ ! -d  ${SUBARUDIR}/${run}_${filter}/STANDARD ] && [ ${STANDARDSTARS} -eq 1 ]; then

if  [ ${STANDARDSTARS} -eq 1 ]; then

    ./BonnLogger.py clear
    ./BonnLogger.py comment "STANDARD star processing"

  case ${filter} in
      "W-J-B" )
  	photfilter=B          # corresponding Johnson filter
  	photcolor=BmV         # color to use
  	EXTCOEFF=-0.2104      # guess for the extinction coefficient
  	COLCOEFF=0.0          # guess for the color coefficient
  	;;
      "W-J-V" )
  	photfilter=V
  	photcolor=VmR
  	EXTCOEFF=-0.1202
  	COLCOEFF=0.0
  	;;
      "W-C-RC" )
  	photfilter=R
  	photcolor=VmR
  	EXTCOEFF=-0.0925
  	COLCOEFF=0.0
  	;;
      "W-C-IC" | "W-S-I+" )
  	photfilter=I
  	photcolor=RmI
  	EXTCOEFF=-0.02728
  	COLCOEFF=0.0
  	;;
      "W-S-Z+" )
  	photfilter=z
  	photcolor=Imz
  	EXTCOEFF=0.0
  	COLCOEFF=0.0
  	;;
  esac

    
### OC STANDARD frames

    #./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} STANDARD
    #./parallel_manager.sh ./process_standard_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE STANDARD RESCALE # BIAS AND FLAT 
    # IF IMAGES ARE ALREADY OC'd USE THIS ONE:
    #./parallel_manager.sh ./process_standard_eclipse_para_OC.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE STANDARD NORESCALE # BIAS AND FLAT 

   #./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} STANDARD SUPA OCF 8 -32 

   #./maskBadOverscans.py ${SUBARUDIR}/${run}_${filter} STANDARD SUPA
   #./maskAutotracker.py ${SUBARUDIR}/${run}_${filter} STANDARD

  
   #./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${SKYBACK}


  #if [ ${FRINGE} == "NOFRINGE" ]; then
  #  ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD RESCALE ILLUM ${SKYBACK}
  #else
  #  ./parallel_manager.sh ./process_science_illum_fringe_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD RESCALE ${SKYBACK}
  #fi
  
  #./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} STANDARD SUPA ${ending} 8 -32

 
  #./parallel_manager.sh ./create_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${ending} WEIGHTS_FLAGS 


# the three-second calibrating routine  
#if [ ${STANDARDTYPE} -eq '3SEC']; then 

#python retrieve_sdss.py ${SUBARUDIR}/${run}_${filter}/STANDARD/${IMGSDSS}_1${ending}.fits ${IMGSDSS}.cat
#./parallel_manager.sh ./create_astrom_3SEC_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${ending} ${IMGSDSS}.cat ${IMGSDSS} 
  ./create_abs_photo_3SEC.sh ${SUBARUDIR}/${run}_${filter} STANDARD SCIENCE \
      ${ending} ${filter} ${photfilter} ${photcolor} ${EXTCOEFF} ${COLCOEFF} ${IMGTOCAL} 
exit 0
./parallel_manager.sh ./create_astrom_3SEC_target_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${ending} default ${IMGTOCAL}  
  
exit 0
  ./create_zp_correct_header.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending}

   # now work on 3-second exposure on MACS field
  ./parallel_manager.sh ./create_astrom_obs_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${ending} default

   ./mk_standard_list.sh 

   #create a standard star list 
 
  ./create_abs_photo_info.sh ${SUBARUDIR}/${run}_${filter} STANDARD SCIENCE \
      ${ending} ${filter} ${photfilter} ${photcolor} ${EXTCOEFF} ${COLCOEFF}
  
  #./create_zp_correct_header.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending}

#fi

fi
exit 0


