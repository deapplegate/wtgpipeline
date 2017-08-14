#!/bin/bash  -xv
#. BonnLogger.sh
#. log_start
# perform astrometric calibration of photometric
# standard star observations and merge these
# calibrated catalogs with a photometric standard
# star catalog

# 30.05.04:
# temporary files go to a TEMPDIR directory 

#$1: main directory
#$2: science dir.
#$3: image extension (ext) on ..._iext.fits (i is the chip number)
#$4: standard star catalog to use; 'default' means that the default
#    catalog given in progs.ini will be used.
#$5: chips to work on
#$6: name of 3sec exposure (i.e. SUPA534134)

# 08.2003-09.2003 (Joerg Dietrich)
# Added full astrom step 
# Moved all conf files to ${PHOTCONF}
#
# 09.09.02:
# changed the filter for the SEEING determination
# to default.conv. The former gauss filter was too broad
# for cosmic rays that were later misidentified
# with stars
#
# 18.02.04:
# changed the config file make_ssc.pairs to
# fullastrom.make_ssc.pairs as they were the same.
#
# 27.04.2004:
# corrected a bug that could overwrite tmp.pairs.cat
# when run in parallel (the file is now names 
# tmp_$$.pairs.cat 
#
# 01.03.2005:
# I introduced the possibility to use another standard
# star catalog than the default one (given in progs.ini)
# For this, a new command line argument has been introduced.
#
# 18.03.2005:
# Now also the WEIGHTS are used in the SExtraction process
# of standard stars.

. ${INSTRUMENT}.ini 

if [ ! -d "/$1/$2/cat" ]; then
  mkdir /$1/$2/cat
fi

if [ "$4" == "default" ]; then
  PHOTCAT=${PHOTSTANDARDSTARSCAT}
else
  PHOTCAT=$4 
fi


echo $5
echo $3


# remove old catalogs
#rm /$1/$2/cat/*

bla=(1)
echo $5
echo $6
for CHIP in $6
do
    ls -1 /$1/$2/$5_${CHIP}$3.fits > ${TEMPDIR}/singleastromimages_$$
    echo "ls -1 /$1/$2/$5_${CHIP}$3.fits > ${TEMPDIR}/singleastromimages_$$"

    #ls -1 /$1/$2/SUPA0055780_${CHIP}$3.fits > ${TEMPDIR}/singleastromimages_$$
    
    cat ${TEMPDIR}/singleastromimages_$$ |\
    {
	while read file
	do
	    echo ${file}
	    BASE=`basename ${file} .fits`
	    #
	    # now run sextractor to determine the seeing:
	    ${P_SEX} ${file} -c ${PHOTCONF}/singleastrom.conf.sex \
			    -CATALOG_NAME ${TEMPDIR}/seeing_$$.cat \
			    -FILTER_NAME ${PHOTCONF}/default.conv\
			    -CATALOG_TYPE "ASCII" \
			    -DETECT_MINAREA 10 -DETECT_THRESH 10.\
			    -ANALYSIS_THRESH 1.2 \
			    -PARAMETERS_NAME ${PHOTCONF}/singleastrom.ascii.param.sex

	    NLINES=`wc ${TEMPDIR}/seeing_$$.cat | awk '{print $1}'`
	    fwhm=`${P_GAWK} 'BEGIN {binsize=10./'${NLINES}'; 
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

	    if [ "A${fwhm}" = "A0.0" ]; then
		fwhm=1.0
	    fi
      
	    #now run sextractor to extract the objects
	    ${P_SEX} ${file} -c ${PHOTCONF}/singleastrom_std.conf.sex\
		    -FLAG_IMAGE /$1/WEIGHTS/${BASE}.flag.fits\
		    -FLAG_TYPE MAX\
		    -WEIGHT_IMAGE /$1/WEIGHTS/${BASE}.weight.fits\
		    -WEIGHT_TYPE MAP_WEIGHT\
		    -CATALOG_NAME /$1/$2/cat/${BASE}.cat\
		    -SEEING_FWHM $fwhm \
		    -DETECT_MINAREA 5 -DETECT_THRESH 2.
		    #-CHECKIMAGE_NAME ${TEMPDIR}/${BASE}.apertures.fits\
		    #-CHECKIMAGE_TYPE APERTURES\
     	    echo ${PHOTCONF} 
	    #
	    # now ldacconv
	    ${P_LDACCONV} -b 1 -c R -i /$1/$2/cat/${BASE}.cat -o /$1/$2/cat/${BASE}.cat0

	    #
	    # then run preastrom:
	    ${P_PREASTROM} -i /$1/$2/cat/${BASE}.cat0 -o /$1/$2/cat/${BASE}.cat1\
			-p ${TEMPDIR}/tmp_$$.cat -a ${STANDARDSTARSCAT}\
			-c ${PHOTCONF}/std.singleastrom.preastrom.conf
 
	    #
	    # apply the solution
	    ${P_APLASTROM} -i /$1/$2/cat/${BASE}.cat1 -o /$1/$2/cat/${BASE}.cat2
		

	    #
	    # and build the pairs catalog
	    ${P_ASSOCIATE} -i /$1/$2/cat/${BASE}.cat2 ${TEMPDIR}/tmp_$$.cat \
			    -o /$1/$2/cat/${BASE}.cat3 ${TEMPDIR}/tmp_$$.cat2 \
			    -c ${PHOTCONF}/std.conf.associate
	    ${P_MAKESSC} -i /$1/$2/cat/${BASE}.cat3 ${TEMPDIR}/tmp_$$.cat2\
			    -o ${TEMPDIR}/tmp_$$.pairs.cat \
			    -c ${PHOTCONF}/fullastrom.make_ssc.pairs
	    #
	    # and now astrom:
	    ${P_ASTROM} -i /$1/$2/cat/${BASE}.cat3 -o /$1/$2/cat/${BASE}.cat4\
			-p ${TEMPDIR}/tmp_$$.pairs.cat\
			-c ${PHOTCONF}/stdastrom.conf

	    #
	    # apply the new solution
	    ${P_APLASTROM} -i /$1/$2/cat/${BASE}.cat4 -o /$1/$2/cat/${BASE}.cat5

	    ${P_MAKEDISTORT} -i /$1/$2/cat/${BASE}.cat5 -o /$1/$2/cat/${BASE}.cat6\
				-c ${PHOTCONF}/singleframe.conf.make_distort

	    ${P_APLPHOTOM} -i /$1/$2/cat/${BASE}.cat6 -o /$1/$2/cat/${BASE}.cat7\
			    -c ${PHOTCONF}/fullphotom.conf.aplphotom\
			    -ZP_ESTIMATES 0.0 -COEFS 0.0
	    ${P_MAKEJOIN} -i /$1/$2/cat/${BASE}.cat7 -o  /$1/$2/cat/${BASE}.cat8\
			    -c ${PHOTCONF}/make_join_std.conf
	    ${P_LDACRENTAB} -i /$1/$2/cat/${BASE}.cat8 -o /$1/$2/cat/${BASE}.cat9\
			    -t OBJECTS STDTAB

	    
	    
	    
	    
	    

	    
	    
	    
	    
	    
 
	    
	    
	    

	    
            
            
	    

	    
            
            
            

	    
            
	    
	    
	    

	    
	    
	    

	    
	    
	    rm ${TEMPDIR}/seeing_$$.cat
	    rm ${TEMPDIR}/tmp_$$.cat
    done
  }
  #${P_LDACPASTE} -i /$1/$2/cat/*_${CHIP}$3.cat9 \
  #               -o /$1/$2/cat/chip_${CHIP}_merg.cat 

done

rm ${TEMPDIR}/singleastromimages_$$


log_status $?


