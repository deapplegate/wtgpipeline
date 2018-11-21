#!/bin/bash

# last update: 27.02.2004 
# author     : Marco Hetterscheidt
#

#$1: main dir.
#$2: science dir.
#$3: name of coadded image (without FITS extension)
#$4 colourindex to compare with McCracken et al. 2004 (r,b,v,i bands)
#$5 CLASS_STAR  -
#$6 FLUX_RADIUS -- values to separate between stars & gal.+ fit interval ($4)  
#$7 MAG_AUTO    -



# The script calls the sm-script "mag_distribution_korr2.sm". The
# sm-program expects a asc-file:Xpos Ypos MAG_AUTO ISO0 FLUX_RADIUS CLASS_STAR
 
# It calculates the number of galaxies and stars per 0.5 mag and sq. degree.
# It takes into account that each object occupies an area, so that darker
# objects can not be detected in this area. For this corr. the isophotal area
# ISO0 (isophote above analysis threshold) and the pixel size of pz is taken .   

# The total area is calculated from the position of detected objects.

# To separate stars & gal., CLASS_STAR is taken. Objects with CLASS_STAR > cs
# are defined as stars, if additionally the FLUX_RADIUS < fr (close to half 
# light radius of stars) and MAG_AUTO < ma (close to saturation level).

# The fit of the logarithmic number counts is an error weighted liner regres.
# of the data points between mag ma and the 4th last point (detection limit).    

# By default the separate parameters are: cs=0.04, fr=2.5, ma=17.5 and
# the default filter colour is R

# If you want to change at least one parameter, you have to type all four
# values.    

. progs.ini

{
  echo "define TeX_strings 0"
  echo 'macro read "'${SMMACROS}'/mag_distribution_korr2.sm"'
  echo 'dev postencap "/'$1'/'$2'/postcoadd/plots/'$3'_mag_distribution.ps"'
  echo 'plot "/'$1'/'$2'/postcoadd/cats/'$3'_sex_ldac.asc"'

  COLOUR=${4}
  CLASS_STAR=${5}
  FLUX_RADIUS=${6}
  MAG_AUTO=${7}

  echo "$3"
  echo "${COLOUR}"
  echo "${CLASS_STAR}"
  echo "${FLUX_RADIUS}"
  echo "${MAG_AUTO}"
} | ${P_SM}

