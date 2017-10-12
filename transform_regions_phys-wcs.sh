#! /bin/bash -xv

image=$1
regdir=$2

ds9 $1 &
sleep 30
xpaset -p ds9 lower

physdir=`dirname ${regdir}`/`basename ${regdir}`_phys

if [ ! -d ${physdir} ]; then
   mkdir ${physdir}
fi
mv ${regdir}/*.reg ${physdir}

for file in $(ls -1 ${physdir}/*.reg)
do

base=`basename ${file}`

xpaset -p ds9 regions load ${file}
xpaset -p ds9 regions format ciao
xpaset -p ds9 regions system wcs
xpaset -p ds9 regions skyformat sexagesimal
xpaset -p ds9 regions save ${regdir}/${base}
xpaset -p ds9 regions delete all

done

xpaset -p ds9 exit