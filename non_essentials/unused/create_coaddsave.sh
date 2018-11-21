#!/bin/bash

# 22.03.02:
# now the results are saved into a coadd_$3
# directory, where $3 is the name of the drizzle
# script.

# the script saves the results from the
# coaddtion process
# after the coaddition process.
# by a call to IRAF

. ${INSTRUMENT:?}.ini

#$1: main dir.
##2: science dir.
#$3: name of the cl-script (4 charracters)

if [ ! -d /$1/$2/coadd_$3 ]; then
  mkdir /$1/$2/coadd_$3
fi

i=1
while [ "${i}" -le ${NPARA} ]
do
  mv ${IRAFDIR[${i}]}/$3*context.fits /$1/$2/coadd_$3
  mv ${IRAFDIR[${i}]}/$3*weight.fits /$1/$2/coadd_$3
  mv ${IRAFDIR[${i}]}/$3*.fits /$1/$2/coadd_$3
  mv ${IRAFDIR[${i}]}/$3*CON /$1/$2/coadd_$3
  mv ${IRAFDIR[${i}]}/$3CONTAB /$1/$2/coadd_$3
  mv ${IRAFDIR[${i}]}/$3*cl /$1/$2/coadd_$3

  i=$(( $i + 1 ))
done



