#!/bin/bash
set -xv

posangle=0.06
position=4.0
pixscale=1.02
#/afs/slac/g/ki/software/local/bin/scamp ../cat/SUPA0109617_scamp.cat ../cat/SUPA0109618_scamp.cat ../cat/SUPA0109619_scamp.cat ../cat/SUPA0109620_scamp.cat ../cat/SUPA0120015_scamp.cat ../cat/SUPA0120016_scamp.cat ../cat/SUPA0120017_scamp.cat ../cat/SUPA0120018_scamp.cat ../cat/SUPA0120019_scamp.cat ../cat/SUPA0120142_scamp.cat ../cat/SUPA0120143_scamp.cat ../cat/SUPA0120144_scamp.cat ../cat/SUPA0120145_scamp.cat ../cat/SUPA0120146_scamp.cat ../cat/SUPA0120147_scamp.cat ../cat/SUPA0120148_scamp.cat ../cat/SUPA0120149_scamp.cat ../cat/SUPA0120150_scamp.cat ../cat/SUPA0120151_scamp.cat ../cat/SUPA0120152_scamp.cat ../cat/SUPA0120153_scamp.cat ../cat/SUPA0109600_scamp.cat ../cat/SUPA0109601_scamp.cat ../cat/SUPA0109602_scamp.cat ../cat/SUPA0109603_scamp.cat ../cat/SUPA0109604_scamp.cat ../cat/SUPA0109605_scamp.cat ../cat/SUPA0109606_scamp.cat ../cat/SUPA0109607_scamp.cat ../cat/SUPA0109608_scamp.cat ../cat/SUPA0109609_scamp.cat ../cat/SUPA0109610_scamp.cat ../cat/SUPA0109611_scamp.cat ../cat/SUPA0109612_scamp.cat ../cat/SUPA0109613_scamp.cat ../cat/SUPA0109614_scamp.cat ../cat/SUPA0109615_scamp.cat ../cat/SUPA0120021_scamp.cat ../cat/SUPA0120022_scamp.cat ../cat/SUPA0120023_scamp.cat ../cat/SUPA0120024_scamp.cat ../cat/SUPA0120025_scamp.cat ../cat/SUPA0120026_scamp.cat ../cat/SUPA0120027_scamp.cat ../cat/SUPA0120028_scamp.cat ../cat/SUPA0120029_scamp.cat ../cat/SUPA0120030_scamp.cat ../cat/SUPA0120031_scamp.cat ../cat/SUPA0120032_scamp.cat ../cat/SUPA0120033_scamp.cat ../cat/SUPA0120034_scamp.cat ../cat/SUPA0120035_scamp.cat ../cat/SUPA0120036_scamp.cat ../cat/SUPA0120037_scamp.cat ../cat/SUPA0120038_scamp.cat -c /afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/conf/reduction/scamp_astrom_photom.scamp -ASTRINSTRU_KEY FILTER,INSTRUM,CONFIG,ROTATION,MISSCHIP,PPRUN -CDSCLIENT_EXEC /afs/slac.stanford.edu/g/ki/software/cdsclient/bin/aclient_cgi -NTHREADS 4 -MOSAIC_TYPE FIX_FOCALPLANE -XML_NAME _scamp.xml -MAGZERO_INTERR 0.1 -MAGZERO_REFERR 0.1 -POSITION_MAXERR 5.0 -POSANGLE_MAXERR 0.07 -SN_THRESHOLDS 3,100 -FLAGS_MASK 0x00e0 -MATCH_NMAX 10000 -CROSSID_RADIUS 0.3 -PIXSCALE_MAXERR 1.03 -DISTORT_DEGREES 3 -ASTREF_WEIGHT 1 -STABILITY_TYPE INSTRUMENT -ASTREF_CATALOG SDSS-R9
cp ~/wtgpipeline/scamp.xsl ../plots
for posangle in 0.02 0.03 0.04 0.05 0.06
do
	for position in 1.0 2.0 3.0 4.0 5.0
	do
		#for pixscale in 1.02 1.01 1.005
		for pixscale in 1.001 1.002 1.003 1.004 1.005
		do

			/afs/slac/g/ki/software/local/bin/scamp ../cat/SUPA0109617_scamp.cat ../cat/SUPA0109618_scamp.cat ../cat/SUPA0109619_scamp.cat ../cat/SUPA0109620_scamp.cat ../cat/SUPA0120015_scamp.cat ../cat/SUPA0120016_scamp.cat ../cat/SUPA0120017_scamp.cat ../cat/SUPA0120018_scamp.cat ../cat/SUPA0120019_scamp.cat ../cat/SUPA0120142_scamp.cat ../cat/SUPA0120143_scamp.cat ../cat/SUPA0120144_scamp.cat ../cat/SUPA0120145_scamp.cat ../cat/SUPA0120146_scamp.cat ../cat/SUPA0120147_scamp.cat ../cat/SUPA0120148_scamp.cat ../cat/SUPA0120149_scamp.cat ../cat/SUPA0120150_scamp.cat ../cat/SUPA0120151_scamp.cat ../cat/SUPA0120152_scamp.cat ../cat/SUPA0120153_scamp.cat ../cat/SUPA0109600_scamp.cat ../cat/SUPA0109601_scamp.cat ../cat/SUPA0109602_scamp.cat ../cat/SUPA0109603_scamp.cat ../cat/SUPA0109604_scamp.cat ../cat/SUPA0109605_scamp.cat ../cat/SUPA0109606_scamp.cat ../cat/SUPA0109607_scamp.cat ../cat/SUPA0109608_scamp.cat ../cat/SUPA0109609_scamp.cat ../cat/SUPA0109610_scamp.cat ../cat/SUPA0109611_scamp.cat ../cat/SUPA0109612_scamp.cat ../cat/SUPA0109613_scamp.cat ../cat/SUPA0109614_scamp.cat ../cat/SUPA0109615_scamp.cat ../cat/SUPA0120021_scamp.cat ../cat/SUPA0120022_scamp.cat ../cat/SUPA0120023_scamp.cat ../cat/SUPA0120024_scamp.cat ../cat/SUPA0120025_scamp.cat ../cat/SUPA0120026_scamp.cat ../cat/SUPA0120027_scamp.cat ../cat/SUPA0120028_scamp.cat ../cat/SUPA0120029_scamp.cat ../cat/SUPA0120030_scamp.cat ../cat/SUPA0120031_scamp.cat ../cat/SUPA0120032_scamp.cat ../cat/SUPA0120033_scamp.cat ../cat/SUPA0120034_scamp.cat ../cat/SUPA0120035_scamp.cat ../cat/SUPA0120036_scamp.cat ../cat/SUPA0120037_scamp.cat ../cat/SUPA0120038_scamp.cat -c /afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/conf/reduction/scamp_astrom_photom.scamp -ASTRINSTRU_KEY FILTER,INSTRUM,CONFIG,ROTATION,MISSCHIP,PPRUN -CDSCLIENT_EXEC /afs/slac.stanford.edu/g/ki/software/cdsclient/bin/aclient_cgi -NTHREADS 4 -MOSAIC_TYPE FIX_FOCALPLANE -XML_NAME posangle_${posangle}_position_${position}_pixscale_${pixscale}_scamp.xml -MAGZERO_INTERR 0.1 -MAGZERO_REFERR 0.1 -POSITION_MAXERR ${position} -POSANGLE_MAXERR ${posangle} -SN_THRESHOLDS 3,100 -FLAGS_MASK 0x00e0 -MATCH_NMAX 10000 -CROSSID_RADIUS 0.3 -PIXSCALE_MAXERR ${pixscale} -DISTORT_DEGREES 3 -ASTREF_WEIGHT 1 -STABILITY_TYPE INSTRUMENT -ASTREF_CATALOG SDSS-R9 2>&1 | tee -a OUT-posangle_${posangle}_position_${position}_pixscale_${pixscale}_scamp.log
			ending=posangle_${posangle}_position_${position}_pixscale_${pixscale}_scamp
			for plotfl in astr_chi2_1.png astr_interror1d_1.png astr_interror2d_1.png astr_referror1d_1.png astr_referror2d_1.png astr_refsysmap_1.png astr_refsysmap_2.png astr_refsysmap_3.png astr_refsysmap_4.png astr_refsysmap_5.png astr_refsysmap_6.png distort_1.png distort_2.png distort_3.png distort_4.png distort_5.png distort_6.png fgroups_1.png phot_errorvsmag_1.png phot_zpcorr_1.png psphot_error_1.png
			do
				base=`basename ${plotfl} .png`
				mv ${plotfl} ${base}_${ending}.png
				sed -i.old "s/${plotfl}/${base}_${ending}.png/g" posangle_${posangle}_position_${position}_pixscale_${pixscale}_scamp.xml
				sed -i.old 's/href=".*"?>/href="scamp.xsl"?>/g' posangle_${posangle}_position_${position}_pixscale_${pixscale}_scamp.xml
				mv fgroups*         ../plots
				mv distort*         ../plots
				mv astr_interror2d* ../plots
				mv astr_interror1d* ../plots
				mv astr_referror2d* ../plots
				mv astr_referror1d* ../plots
				mv astr_chi2*       ../plots
				mv psphot_error*    ../plots
				mv astr_refsysmap*  ../plots
				mv phot_zpcorr*     ../plots
				mv phot_errorvsmag* ../plots
				mv posangle_${posangle}_position_${position}_pixscale_${pixscale}_scamp.xml ../plots
			done
		done
	done
done


#astr_chi2_1.png astr_interror1d_1.png astr_interror2d_1.png astr_referror1d_1.png astr_referror2d_1.png astr_refsysmap_1.png astr_refsysmap_2.png astr_refsysmap_3.png astr_refsysmap_4.png astr_refsysmap_5.png astr_refsysmap_6.png distort_1.png distort_2.png distort_3.png distort_4.png distort_5.png distort_6.png fgroups_1.png phot_errorvsmag_1.png phot_zpcorr_1.png psphot_error_1.png
