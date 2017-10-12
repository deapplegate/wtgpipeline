#! /bin/bash
. /u/ki/awright/bonnpipeline/SUBARU.ini
file=$1
echo $file
BASE=`basename ${file} .fits`

echo ${DATACONF}
echo ${TEMPDIR}
# first run sextractor to determine the seeing:
${P_SEX} ${file} -c ${DATACONF}/singleastrom.conf.sex \
       -CATALOG_NAME ${TEMPDIR}/seeing_test.cat \
       -FILTER_NAME ${DATACONF}/default.conv\
       -CATALOG_TYPE "ASCII" \
       -DETECT_MINAREA 1 -DETECT_THRESH 5.\
       -ANALYSIS_THRESH 1.2 \
       -PARAMETERS_NAME ${DATACONF}/singleastrom.ascii.param.sex

NLINES=`wc ${TEMPDIR}/seeing_test.cat | ${P_GAWK} '{print $1}'`
fwhm=`${P_GAWK} 'BEGIN{
                         binsize=10./'${NLINES}'; 
                         nbins=int(((3.0-0.3)/binsize)+0.5);
                         for(i=1; i<=nbins; i++) bin[i]=0
                      }
                      { 
                         if(($3*'${PIXSCALE}' > 0.3) && ($3*'${PIXSCALE}' < 3.0)) 
                         {
                            actubin=int(($3*'${PIXSCALE}'-0.3)/binsize);
                            bin[actubin]+=1; 
                         }
                      }
                  END {
                         max=0; k=0 
                         for(i=1;i<=nbins; i++)
                         {   
                            if(bin[i]>max)
                            { 
                               max=bin[i];
                               k=i;
                            }
                         }
                         print 0.3+k*binsize
                      }' ${TEMPDIR}/seeing_test.cat`

echo $fwhm
