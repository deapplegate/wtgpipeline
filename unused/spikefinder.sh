#! /bin/tcsh 
#
# Wrapper designed to run the diffraction spike finder on a 
# series of images.  -MTA
# Usage:
# ./spikefinder.sh  ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA OFCS
#
# $argv[1] = ${SUBARUDIR}/${run}_${filter}
# $argv[2] = SCIENCE
# $argv[3] = SUPA
# $argv[4] = OFCS




if(! -e $argv[1]/$argv[2]/diffmask) then
    mkdir $argv[1]/$argv[2]/diffmask
endif
 
foreach iter ($argv[1]/$argv[2]/$argv[3]*OFCS.fits)
    echo ${iter};
    setenv fname `echo $iter | gawk -F/ '{print $NF}' | gawk -F. '{print $1"_diffmask.fits"}'`
    sfdir/spikefinder ${iter} $argv[1]/$argv[2]/diffmask/$fname 1
end


