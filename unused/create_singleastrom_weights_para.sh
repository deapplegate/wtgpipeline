#!/bin/bash -xv

# this version of the singleastrom step uses the WEIGHT images
# of the individual frames in the object detection process.
# Hence, catalogs are supoosed to be much cleaner and detection
# threshhold is lowered to 5, 5.

#$1: main directory
#$2: science dir.
#$3: image extension (ext) on ..._iext.fits (i is the chip number)
#$4: WEIGHTS directory
#$5: image extension for weight images 
#$6: chips to work on


. ${INSTRUMENT:?}.ini 

if [ ! -d "/$1/$2/cat" ]; then
  mkdir /$1/$2/cat
fi

echo $6
for CHIP in $6
do
  ls -1 /$1/$2/*_${CHIP}$3.fits > ${TEMPDIR}/singleastromimages_$$
  
  cat ${TEMPDIR}/singleastromimages_$$ |\
  {
    while read file
    do
      BASE=`basename ${file} .fits`
      WBASE=`basename ${file} $3.fits`
      #
      # now run sextractor to determine the seeing:
      ${P_SEX} ${file} -c ${DATACONF}/singleastrom.conf.sex \
			-CATALOG_NAME ${TEMPDIR}/seeing_$$.cat \
	                -FILTER_NAME ${DATACONF}/default.conv\
			-CATALOG_TYPE "ASCII" \
			-DETECT_MINAREA 5 -DETECT_THRESH 5.\
			-ANALYSIS_THRESH 1.2 \
			-PARAMETERS_NAME ${DATACONF}/singleastrom.ascii.param.sex\
	                -WEIGHT_IMAGE /$1/$4/${WBASE}$5.fits\
                        -WEIGHT_TYPE MAP_WEIGHT

      NLINES=`wc ${TEMPDIR}/seeing_$$.cat | ${P_GAWK} '{print $1}'`
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
      ${P_SEX} ${file} -c ${DATACONF}/singleastrom.conf.sex\
		       -CATALOG_NAME /$1/$2/cat/${BASE}.cat\
		       -SEEING_FWHM $fwhm \
		       -DETECT_MINAREA 5 -DETECT_THRESH 5.\
	               -WEIGHT_IMAGE /$1/$4/${WBASE}$5.fits\
                       -WEIGHT_TYPE MAP_WEIGHT
      
      #
      # now ldacconv
      ${P_LDACCONV} -b 1 -c R -i /$1/$2/cat/${BASE}.cat -o /$1/$2/cat/${BASE}.cat0
      #
      # then run preastrom:
      ${P_PREASTROM} -i /$1/$2/cat/${BASE}.cat0 -o /$1/$2/cat/${BASE}.cat1\
		      -p ${TEMPDIR}/tmp_$$.cat -a ${STANDARDSTARSCAT} \
                      -c ${DATACONF}/singleastrom.preastrom.conf \
	              -d ${TEMPDIR}/distances.cat

      rm ${TEMPDIR}/seeing_$$.cat
      rm ${TEMPDIR}/tmp_$$.cat
    done
  }
done

rm ${TEMPDIR}/singleastromimages_$$

exit 0;


