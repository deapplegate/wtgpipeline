#!/bin/bash
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# The script allows to write a photometric solution into 
# image headers. The filename of the file containing photometric
# solutions has to have the contents:
#
# ZP1 COEFF1 CT1
# ZP2 COEFF2 CT2
# ZP3 COEFF3 CT3
#
# where ZP, COEFF and CT represent zeropoints (at zero airmass),
# extinction coefficients and color terms correspondingly (for
# the moment the color terms are used nowhere in the pipeline).
# The user is free to choose the meaning of the three solutions.
# We use: ZP1 etc. stems from a three parameter fit (ZP, COEFF
# and CT), ZP2 is from a 2-parameter fit (ZP and CT, COEFF fixed)
# and ZP3 is from a one parameter fit (ZP; CT and COEFF fixed).

#$1: main dir
#$2: science dir
#$3: image extension
#$4: GABODSID of the night to be updated
#$5: filename; the file containing the three 
#    photometric solutions
#$6: ZPCHOICE: the solution to be choosen as default

. ${INSTRUMENT:?}.ini
. bash_functions.include

i=1
while read ZEROP EXT COLOR
do
  ZP[$i]=${ZEROP}
  COEFF[$i]=${EXT}
  COL[$i]=${COLOR}

  i=$(( $i + 1 ))
done < $5

${P_DFITS} /$1/$2/*$3.fits | ${P_FITSORT} -d GABODSID | \
   ${P_GAWK} '{if ($2 == '${4}') print $1}' > ${TEMPDIR}/night_${4}_img_list_$$.asc

while read IMG
do
   echo $IMG
   # Write the choice to the header
   value ${6}
   writekey /$1/$2/${IMG} ZPCHOICE "${VALUE}" REPLACE

   value ${ZP[$6]}
   writekey /$1/$2/${IMG} ZP "${VALUE}" REPLACE

   value ${COEFF[$6]}
   writekey /$1/$2/${IMG} COEFF "${VALUE}" REPLACE

   i=1
   while [ "${i}" -le "3" ]
   do
     value ${ZP[$i]}
     writekey /$1/$2/${IMG} ZP${i} "${VALUE}" REPLACE

     value ${COEFF[$i]}
     writekey /$1/$2/${IMG} COEFF${i} "${VALUE}" REPLACE

     i=$(( $i + 1 ))
   done
done < ${TEMPDIR}/night_${4}_img_list_$$.asc
#adam-BL# log_status $?
