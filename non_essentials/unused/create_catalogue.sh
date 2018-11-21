#!/bin/bash -xv

# last update: 17.02.2007 
# authors    : Marco Hetterscheidt & Thomas Erben

# creation of catalogues and corresponding asc-files for 
# mag_distribution_korr2.sh
# and create_checkplot_rh_mag.sh 

# 17.03.2004:
# In the final catalog creation I changed the background
# mode from MANUAL to AUTO. The MANUAL mode gave very
# bad results in the mag-rh plots and the number count
# distributions
#
# 17.05.2004:
# included a prefiltering of the initial catalog (MAG_AUTO<40)
# to avoid errors when estimating number counts 
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 16.02.2007:
# - The image seeing is estimated only if it is not yet given
#   in the image headers.
# - The catalogue is now created taking into account a flag map.
#   Filtering is done for all objects not having an external flag
#   of zero. 
 
#$1: main dir.
#$2: science dir.
#$3: Mag Zeropoint
#$4: name of coadd script
#$5: name of coadded image (without FITS extension)
#$6: name of the catalog (if not given it is the same
#    as the name of the coadded image)

. ${INSTRUMENT:?}.ini

if [ "$#" -eq "6" ]; then
  CATNAME=$6
else
  CATNAME=$5
fi

if [ ! -d /$1/$2/postcoadd ]; then
  mkdir /$1/$2/postcoadd
  mkdir /$1/$2/postcoadd/cats
  mkdir /$1/$2/postcoadd/plots
fi

# If necessary: run SExtractor first to get the seeing:
FWHM=`dfits /$1/$2/coadd_$4/$5.fits | fitsort -d SEEING | awk '{print $2}'`

if [ "${FWHM}" = "KEY_N/A" ]
then
    ${P_SEX} /$1/$2/coadd_$4/$5.fits -c ${CONF}/postcoadd.conf.sex \
               -CATALOG_NAME ${TEMPDIR}/seeing_$$.cat \
               -FILTER_NAME ${DATACONF}/default.conv\
               -CATALOG_TYPE "ASCII" \
               -WEIGHT_IMAGE /$1/$2/coadd_$4/$5.weight.fits \
               -WEIGHT_TYPE MAP_WEIGHT -DETECT_MINAREA 10 \
               -DETECT_THRESH 10 -ANALYSIS_THRESH 10\
               -PARAMETERS_NAME ${DATACONF}/singleastrom.ascii.param.sex
    
    NLINES=`wc ${TEMPDIR}/seeing_$$.cat | awk '{print $1}'`
    FWHM=`gawk 'BEGIN {binsize=10./'${NLINES}'; 
    		   nbins=int(((3.0-0.3)/binsize)+0.5);
    		   for(i=1; i<=nbins; i++) bin[i]=0}
    		   { if(($3*'${PIXSCALE}' > 0.3) && ($3*'${PIXSCALE}' < 3.0))
    		     actubin=int(($3*'${PIXSCALE}'-0.3)/binsize);
    		     bin[actubin]+=1; }
    	    END {max=0; k=0 
    		 for(i=1;i<=nbins; i++)
    		 {
    		    if(bin[i]>max)
    		    { 
    		      max=bin[i];
    		      k=i;
    		    }
    		 }
    		 print 0.3+k*binsize}' ${TEMPDIR}/seeing_$$.cat`
    
    if [ "A${FWHM}" = "A0.0" ]; then
    	  FWHM=1.0
    fi
fi


${P_SEX} /$1/$2/coadd_$4/$5.fits -c ${CONF}/postcoadd.conf.sex \
           -CATALOG_NAME ${TEMPDIR}/sex.cat \
           -SEEING_FWHM ${FWHM} \
           -MAG_ZEROPOINT $3 \
           -PIXEL_SCALE ${PIXSCALE}\
           -BACK_TYPE AUTO \
           -BACK_SIZE 64 \
           -WEIGHT_IMAGE /$1/$2/coadd_$4/$5.weight.fits \
           -WEIGHT_TYPE MAP_WEIGHT -DETECT_MINAREA 3 \
           -FLAG_IMAGE /$1/$2/coadd_$4/$5.flag.fits \
           -FLAG_TYPE MAX -DETECT_MINAREA 3 \
           -DETECT_THRESH 2 -ANALYSIS_THRESH 2


${P_LDACCONV}  -i ${TEMPDIR}/sex.cat -o /$1/$2/postcoadd/cats/${CATNAME}_sex_ldac_tmp.cat -b 1 -c "sex" -f R

${P_LDACFILTER} -i /$1/$2/postcoadd/cats/${CATNAME}_sex_ldac_tmp.cat \
                -o /$1/$2/postcoadd/cats/${CATNAME}_sex_ldac.cat \
                -t OBJECTS -c "(MAG_AUTO<40)AND(IMAFLAGS_ISO<1);"

${P_LDACTOASC} -i /$1/$2/postcoadd/cats/${CATNAME}_sex_ldac.cat -t OBJECTS \
               -k Xpos Ypos MAG_AUTO ISO0 FLUX_RADIUS CLASS_STAR \
               -b > /$1/$2/postcoadd/cats/${CATNAME}_sex_ldac.asc

#create_checkplot_rh_mag.sh /$1/$2/coadd_$3/$5.fits 0.9 2.3 17.5

# CLASS_STAR=0.9, FLUX_RADIUS=2.3 and MAG_AUTO=17.5 are typical values to separate 
# stars from galaxies. 
