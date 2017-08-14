#!/bin/bash -xv

# the script creates plot for the mosaics + individual chips.
# 
# First version : 31/01/2007
# 

# $1: main directory
# $2: science dir.
# $3: image extension (ext) on ..._iext.fits (i is the chip number)

. ${INSTRUMENT:?}.ini
. progs.ini

PROGS_DIR=$PWD
export PROGS_DIR;


# parameters 
i=1
while [ "${i}" -le "${NCHIPS}" ]
do
  CHIPS="${CHIPS} ${i}"
  i=$(( $i + 1 ))
done

SMOOTH=4
MASKDIR=/$1/$2/STRACK
MASKDIR_PLOT=/$1/$2/STRACK/plots

mkdir ${MASKDIR_PLOT}

ls -1 /$1/$2/*_1$3.fits > ${TEMPDIR}/crw_images_$$
#ls -1 /$1/$2/715229p*_1$3.fits > ${TEMPDIR}/crw_images_$$

# Loop on the exposures 
cat ${TEMPDIR}/crw_images_$$ |\
      {
      while read file
	do

	# Create the reg file for the whole mosaic
	BASE=`basename ${file} _1$3.fits`
	
	cd ${MASKDIR}
	#echo perl ~/perl/VIRMOS/pipeline/plot_reg_mos_bin.pl -root /$1/$2/${BASE} -root_reg ${MASKDIR}/${BASE} -ext ${3}.fits -conv ${SMOOTH} -out ${MASKDIR_PLOT}/${BASE}_STRACK.ps
	echo perl ${S_STRACK_PLOT_MOS} -root /$1/$2/${BASE} -root_reg ${MASKDIR}/${BASE} -ext ${3}.fits -conv ${SMOOTH} -out ${MASKDIR_PLOT}/${BASE}_STRACK.ps
	if [ ! -f ${MASKDIR_PLOT}/${BASE}_STRACK.ps ]; then 
	    perl ${S_STRACK_PLOT_MOS} -root /$1/$2/${BASE} -root_reg ${MASKDIR}/${BASE} -ext ${3}.fits -conv ${SMOOTH} -out ${MASKDIR_PLOT}/${BASE}_STRACK.ps
	fi
     



	# Create reg files for individual chips
	ls -1 ${MASKDIR}/${BASE}_*$3.reg > ${TEMPDIR}/crw_reg_$$
	cat ${TEMPDIR}/crw_reg_$$ |\
	    {
	    while read file2
	      do
	      BASE2=`basename ${file2} .reg`
	      IM=/$1/$2/${BASE2}.fits

	      LINES=`wc ${file2} | awk '{print $1}'`
	      if [ ${LINES} -gt 3 ]; then
		  #echo perl ~/perl/VIRMOS/needed/plot_reg_bin_conv.pl -image ${IM} -reg ${file2} -out ${BASE2}_STRACK.ps -conv ${SMOOTH}
		  echo perl ${S_STRACK_PLOT_CHIP} -image ${IM} -reg ${file2} -out ${MASKDIR_PLOT}/${BASE2}_STRACK.ps -conv ${SMOOTH}
		  perl ${S_STRACK_PLOT_CHIP} -image ${IM} -reg ${file2} -out ${MASKDIR_PLOT}/${BASE2}_STRACK.ps -conv ${SMOOTH}
	      fi
	    done
	}
      done
  }
  

