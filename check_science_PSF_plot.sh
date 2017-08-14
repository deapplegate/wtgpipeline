#!/bin/bash -u
. BonnLogger.sh
. log_start
# ----------------------------------------------------------------
# File Name:           check_science_PSF_plot.sh
# Author:              Thomas Erben (terben@astro.uni-bonn.de)
# Last modified on:    19.09.2007
# Description:         creates PSF anisotropy checkplots for
#                      'regularly shaped' multi-chip cameras
# ----------------------------------------------------------------

# Script history information:
# 19.09.2007:
# script written

. progs.ini

# define THELI_DEBUG because of the '-u' script flag
# (the use of undefined variables will be treated as errors!)
# THELI_DEBUG is used in the cleanTmpFiles function.
THELI_DEBUG=${THELI_DEBUG:-""}

# function definitions:
function printUsage 
{
    echo "SCRIPT NAME:"
    echo "    check_science_PSF_plot.sh"
    echo ""
    echo "ARGUMENTS:"
    echo "    1. main_dir."
    echo "    2. science (run)_dir."
    echo "    3. image_extension"
    echo "    4. Super Mongo Postscript device (OPTIONAL)"
    echo "       Default is 'postportfile'"
    echo ""
}

function cleanTmpFiles
{
    if [ -z ${THELI_DEBUG} ]; then
        echo "Cleaning temporary files for script $0"
        rm ${TEMPDIR}/psfimages_plot_$$
        find ${TEMPDIR} -maxdepth 1 -name \*PSF_allellip.asc_$$ -exec rm {} \;
        find ${TEMPDIR} -maxdepth 1 -name \*PSFplot.asc_$$      -exec rm {} \;
        find ${TEMPDIR} -maxdepth 1 -name \*PSF_allellip.asc_$$ -exec rm {} \;
        find ${TEMPDIR} -maxdepth 1 -name \*PSFplot.sm_$$       -exec rm {} \;
    else
        echo "Variable THELI_DEBUG set! No cleaning of temp. files in script $0"    
    fi
}

# Handling of program interruption by CRTL-C
trap "echo 'Script $0 interrupted!! Cleaning up and exiting!'; \
      cleanTmpFiles; log_status 1; exit 1" INT

# check whether we have the external 'sm' program at all:
if [ -z ${P_SM} ]
then
    echo "You need the external Super Mongo (sm) program to"
    echo "use this script! At least the necessary variable in"
    echo "your progs.ini seems not to be set! Exiting!!"
    log_status 1
    exit 1;
fi

# check validity of command line arguments:
if [ $# -lt 3 ] || [ $# -gt 4 ] ; then
    printUsage
    log_status 1
    exit 1
fi

# Here the main script begins

# set SM postscript device
SMPSDEVICE="postportfile"

if [ $# -eq 4 ]; then
  SMPSDEVICE=$4
fi

if [ ! -d "/$1/$2/cat/PSFcheck" ]; then
  # immediately quit if we do not yet have a 'cat' subdirectory!
  mkdir /$1/$2/cat/PSFcheck || \
  { echo "creation of dir. /$1/$2/cat/PSFcheck failed! Exiting!"; log_status 1; exit 1; } 
fi

# first get a list of all images for which to create PSF plots:
${P_FIND} /$1/$2/ -name \*_3$3.fits > ${TEMPDIR}/psfimages_plot_$$

while read file
do
  BASE=`basename ${file} _3$3.fits`

  INSTRUM=`${P_DFITS} ${file} | fitsort -d INSTRUM | awk '{print $2}'`

  case ${INSTRUM} in
      "SUBARU" )
	  CONFIG=`${P_DFITS} ${file} | fitsort -d CONFIG | awk '{print $2}'`
	  CHIPGEOMETRY=`grep CHIPGEOMETRY $(echo ${INSTRUM} | sed 'y/ABCDEFGHIJKLMNOPQRSTUVWXYZ/abcdefghijklmnopqrstuvwxyz/')_${CONFIG}.ini | ${P_GAWK} 'BEGIN{FS="="}{print $2}' | sed 's/\"//g'`
	  NCHIPS=`grep NCHIPS\= $(echo ${INSTRUM} | sed 'y/ABCDEFGHIJKLMNOPQRSTUVWXYZ/abcdefghijklmnopqrstuvwxyz/')_${CONFIG}.ini | ${P_GAWK} 'BEGIN{FS="="}{print $2}'`
	  ;;
      * )
	  CHIPGEOMETRY=`grep CHIPGEOMETRY ${INSTRUM}.ini | ${P_GAWK} 'BEGIN{FS="="}{print $2}' | sed 's/\"//g'`
	  NCHIPS=`grep NCHIPS ${INSTRUM}.ini | ${P_GAWK} 'BEGIN{FS="="}{print $2}'`
	  ;;
  esac


  # decompose the CHIPGEOMETRY variable:
  NCHIPSX=`echo ${CHIPGEOMETRY} | ${P_GAWK} '{print $1}'`
  NCHIPSY=`echo ${CHIPGEOMETRY} | ${P_GAWK} '{print $2}'`
  NAXIS1=`echo ${CHIPGEOMETRY} | ${P_GAWK} '{print $3}'`
  NAXIS2=`echo ${CHIPGEOMETRY} | ${P_GAWK} '{print $4}'`
  
  # If something is wrong with the CHIPGEOMETRY var.
  # probably NAXIS2 is not set!
  test -z ${NAXIS2} && { echo "Malformed CHIPGEOMETRY variable! Exiting !!"; log_status 1; exit 1; }

  NCATS=0  # the number of available KSB catalogues for
           # the current image

  # The file for global ellipticity statistics:
  test -f  ${TEMPDIR}/${BASE}_PSF_allellip.asc_$$ && \
        rm ${TEMPDIR}/${BASE}_PSF_allellip.asc_$$ 

  i=1
  while [ "${i}" -le ${NCHIPS} ]
  do
    if [ -f /$1/$2/cat/${BASE}_${i}$3_ksb.cat2 ]
    then
      ${P_LDACTOASC} -i /$1/$2/cat/${BASE}_${i}$3_ksb.cat2 -b -t OBJECTS\
                     -k Xpos Ypos e1 e2 > ${TEMPDIR}/${BASE}_${i}_PSFplot.asc_$$

      # gather all ellipticity values for global statistics:
      ${P_GAWK} '{print $3, $4}' ${TEMPDIR}/${BASE}_${i}_PSFplot.asc_$$ >> \
                ${TEMPDIR}/${BASE}_PSF_allellip.asc_$$ 

      NCATS=$(( ${NCATS} + 1 ))
    fi
    i=$(( $i + 1 ))
  done

  if [ ${NCATS} -gt 0 ]
  then
    # Ok, create a sm script file for the current image
    # First the sickplots for each chip:
    {
      echo 'macro read "'${SMMACROS}'/shearfield.sm"'
      echo 'device "'${SMPSDEVICE}' /'$1'/'$2'/cat/PSFcheck/'${BASE}'.ps"'
      echo "relocate (17600 32500)"
      echo "putlabel 5 '${BASE}'"
      echo "limits 0 ${NAXIS1} 0 ${NAXIS2}"      
      echo "lweight 1.5"
      echo "expand 0.5"

      i=1
      j=1
      k=1
      while [ ${j} -le ${NCHIPSY} ]
      do
        while [ ${k} -le ${NCHIPSX} ]
        do
          echo "window -${NCHIPSX} -${NCHIPSY} ${k} ${j}"
          
	  # The box command specifying whether and where
          # to put lablels depends on where we are in the
          # mosaic:
          if [ ${j} -eq 1 ] && [ ${k} -eq 1 ]; then
            echo "box"
          else
            if [ ${j} -eq 1 ]; then
              echo "box 1 0"
            else
              if [ ${k} -eq 1 ]; then
                echo "box 0 2"
              else
                echo "box 0 0"
              fi
            fi
          fi

          if [ -f ${TEMPDIR}/${BASE}_${i}_PSFplot.asc_$$ ]
          then
            echo 'shearfield "'${TEMPDIR}'/'${BASE}'_'${i}'_PSFplot.asc_'$$'" 2000'
          fi

          i=$(( $i + 1 ))
          k=$(( $k + 1 ))
        done
        j=$(( $j + 1 )) 
        k=1
      done

      # global statistics on the PSF ellipticity      
      # distribution:
      echo 'data "'${TEMPDIR}'/'${BASE}'_PSF_allellip.asc_'$$'"'
      echo "read { e1 1 e2 2 }"
      echo "stats e1 m1 s1 k1"
      echo "stats e2 m2 s2 k2"
      echo "relocate ( 2000 1500 )"
      echo "define s (sprintf('<e1>: %.2f +/- ', \$m1))"
      echo 'label $s'
      echo "define s (sprintf('%.2f;', \$s1))"
      echo 'label $s'
      echo "relocate ( 8000 1500 ) "
      echo "define s (sprintf('<e2>: %.2f +/- ', \$m2))"
      echo 'label $s'
      echo "define s (sprintf('%.2f;', \$s2))"
      echo 'label $s'
      echo "set eabs=sqrt(e1*e1+e2*e2)"
      echo "sort {eabs}"
      echo "relocate ( 15000 1500 )"
      echo "define s (sprintf('|e| min = %.2f;', \$(eabs[0])))"
      echo 'label $s'
      echo "relocate ( 20000 1500 )"
      echo "define n (dimen(eabs)-1)"
      echo "define s (sprintf('|e| max = %.2f', \$(eabs[\$n])))"
      echo 'label $s'

      echo "sort {e1}"
      echo "relocate ( 2000 1000 )"
      echo "define s (sprintf('e1 min = %.2f;', \$(e1[0])))"
      echo 'label $s'
      echo "relocate ( 8000 1000 )"
      echo "define n (dimen(e1)-1)"
      echo "define s (sprintf('e1 max = %.2f', \$(e1[\$n])))"
      echo 'label $s'

      echo "sort {e2}"
      echo "relocate ( 15000 1000 )"
      echo "define s (sprintf('e2 min = %.2f;', \$(e2[0])))"
      echo 'label $s'
      echo "relocate ( 20000 1000 )"
      echo "define n (dimen(e2)-1)"
      echo "define s (sprintf('e2 max = %.2f', \$(e2[\$n])))"
      echo 'label $s'

      echo "expand 1.0"
      echo "lweight 1.0"
      echo "hardcopy"      
    } > ${TEMPDIR}/${BASE}_PSFplot.sm_$$
    cat ${TEMPDIR}/${BASE}_PSFplot.sm_$$ | ${P_SM}
  else
    echo "Not a single chip KSB catalogue for exposure ${BASE}!"
  fi
done < ${TEMPDIR}/psfimages_plot_$$

# clean temporary files and bye
#cleanTmpFiles

log_status $?
