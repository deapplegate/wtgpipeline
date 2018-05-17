#!/bin/bash
## see here for details:
## 	/gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B/SCIENCE/astrom_photom_scamp_PANSTARRS/headers_photom_old_perfect
set -xv
. ~/wtgpipeline/progs.ini > tmp.log 2>&1
. ~/wtgpipeline/SUBARU.ini > tmp.log 2>&1
rm tmp.log

STARCAT="PANSTARRS"
cluster=MACS0429-02
NPARA=4
PHOTFLUXKEY="FLUX_AUTO"
PHOTFLUXERRKEY="FLUXERR_AUTO"
#adam-tmp# PHOTFLUXKEY="FLUX_APER1"
#adam-tmp# PHOTFLUXERRKEY="FLUXERR_APER1"
#adam-SHNT#             -ASTREFMAG_KEY iMeanApMag \                                                                                                                                                              
#adam-SHNT#             -ASTREFMAGERR_KEY iMeanApMagErr "

## scamp mode settings
scamp_mode_instrum_star="-STABILITY_TYPE INSTRUMENT -ASTREF_CATALOG ${STARCAT} " #default
scamp_mode_exp_star="-STABILITY_TYPE EXPOSURE -ASTREF_CATALOG ${STARCAT} "
scamp_mode_instrum_ref="-STABILITY_TYPE INSTRUMENT -ASTREF_CATALOG FILE -ASTREFCENT_KEYS X_WORLD,Y_WORLD -ASTREFERR_KEYS ERRA_WORLD,ERRB_WORLD,ERRTHETA_WORLD -ASTREFMAG_KEY MAG_AUTO "
scamp_mode_exp_ref="-STABILITY_TYPE EXPOSURE -ASTREF_CATALOG FILE -ASTREFCENT_KEYS X_WORLD,Y_WORLD -ASTREFERR_KEYS ERRA_WORLD,ERRB_WORLD,ERRTHETA_WORLD -ASTREFMAG_KEY MAG_AUTO "

if [ "${STARCAT}" == "PANSTARRS" ]; then
        cp /nfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}/panstarrs_cats/astrefcat-stars_only.cat ./astrefcat.cat
        scamp_mode_instrum_ref="-STABILITY_TYPE INSTRUMENT \
                -ASTREF_CATALOG FILE \
                -ASTREFCAT_NAME astrefcat.cat \
                -ASTREFCENT_KEYS raMean,decMean \
                -ASTREFERR_KEYS raMeanErr,decMeanErr \
                -ASTREFMAG_LIMITS 13,30 \
                -ASTREFMAG_KEY iMeanPSFMag \
                -ASTREFMAGERR_KEY iMeanPSFMagErr "
        #adam: "iMeanPSFMag","iMeanPSFMagErr","iMeanKronMag","iMeanKronMagErr","iMeanApMag","iMeanApMagErr"
        scamp_mode_use=${scamp_mode_instrum_ref}
else
        # really very little difference when changing "-ASTREF_WEIGHT 1" to "-ASTREF_WEIGHT 10", so ignore this                                                                                                  
        scamp_mode_use=${scamp_mode_instrum_star} #default
fi
## catalogs are these:
# ../cat_photom/SUPA0050796_scamp.cat ../cat_photom/SUPA0154639_scamp.cat ../cat_photom/SUPA0154629_scamp.cat ../cat_photom/SUPA0043649_scamp.cat ../cat_photom/SUPA0043650_scamp.cat ../cat_photom/SUPA0043636_scamp.cat ../cat_photom/SUPA0154627_scamp.cat ../cat_photom/SUPA0154628_scamp.cat ../cat_photom/SUPA0154630_scamp.cat ../cat_photom/SUPA0154650_scamp.cat ../cat_photom/SUPA0154632_scamp.cat ../cat_photom/SUPA0154635_scamp.cat ../cat_photom/SUPA0154625_scamp.cat ../cat_photom/SUPA0043648_scamp.cat ../cat_photom/SUPA0154647_scamp.cat ../cat_photom/SUPA0154644_scamp.cat ../cat_photom/SUPA0043642_scamp.cat ../cat_photom/SUPA0043643_scamp.cat ../cat_photom/SUPA0154640_scamp.cat ../cat_photom/SUPA0154641_scamp.cat ../cat_photom/SUPA0050800_scamp.cat ../cat_photom/SUPA0050792_scamp.cat ../cat_photom/SUPA0154653_scamp.cat ../cat_photom/SUPA0154638_scamp.cat ../cat_photom/SUPA0050797_scamp.cat ../cat_photom/SUPA0050798_scamp.cat ../cat_photom/SUPA0050799_scamp.cat ../cat_photom/SUPA0050801_scamp.cat ../cat_photom/SUPA0154642_scamp.cat ../cat_photom/SUPA0154643_scamp.cat ../cat_photom/SUPA0154631_scamp.cat ../cat_photom/SUPA0154633_scamp.cat ../cat_photom/SUPA0154634_scamp.cat ../cat_photom/SUPA0154636_scamp.cat ../cat_photom/SUPA0154646_scamp.cat ../cat_photom/SUPA0154648_scamp.cat ../cat_photom/SUPA0154649_scamp.cat ../cat_photom/SUPA0154651_scamp.cat ../cat_photom/SUPA0154652_scamp.cat ../cat_photom/SUPA0154626_scamp.cat ../cat_photom/SUPA0043645_scamp.cat ../cat_photom/SUPA0154645_scamp.cat ../cat_photom/SUPA0043646_scamp.cat ../cat_photom/SUPA0043647_scamp.cat ../cat_photom/SUPA0043641_scamp.cat ../cat_photom/SUPA0043639_scamp.cat ../cat_photom/SUPA0043640_scamp.cat ../cat_photom/SUPA0043637_scamp.cat ../cat_photom/SUPA0043638_scamp.cat 
#mkdir cat_photom
#ln -s /u/ki/awright/my_data/SUBARU/MACS0429-02/W-J-B/SCIENCE/astrom_photom_scamp_PANSTARRS/cat_photom/SUPA*scamp.cat ./cat_photom/
#ln -s /u/ki/awright/my_data/SUBARU/MACS0429-02/W-J-B/SCIENCE/astrom_photom_scamp_PANSTARRS/cat_photom/SUPA*scamp.ahead ./cat_photom/

posangle=1.0
position=1.0
pixscale=1.003

for pixscale in 1.05 1.2
do
	for posangle in 4.0 6.0 10.0 2.0
	do
		ending=posangle_${posangle}_position_${position}_pixscale_${pixscale}_scamp

		${P_SCAMP} `${P_FIND} ./cat_photom/ -name SUPA\*scamp.cat` \
			-c ${CONF}/scamp_astrom_photom.scamp \
			-PHOTINSTRU_KEY FILTER -ASTRINSTRU_KEY ASTINST,MISSCHIP,NEWOLD \
			-PHOTFLUX_KEY ${PHOTFLUXKEY} -PHOTFLUXERR_KEY ${PHOTFLUXERRKEY} \
			-CDSCLIENT_EXEC ${P_ACLIENT} \
			-NTHREADS ${NPARA} \
			-XML_NAME ${cluster}_scamp.xml \
			-MAGZERO_INTERR 0.1 \
			-MAGZERO_REFERR 0.03 \
			-POSITION_MAXERR ${position} \
			-POSANGLE_MAXERR ${posangle} \
			-PIXSCALE_MAXERR ${pixscale} \
			-SN_THRESHOLDS 5,50 \
			-MATCH Y \
			-MATCH_NMAX 10000 \
			-MATCH_RESOL 0.0 \
			-CROSSID_RADIUS 0.3 \
			-DISTORT_DEGREES 3 \
			-MOSAIC_TYPE UNCHANGED \
			-ASTREF_WEIGHT 1 ${scamp_mode_use} -CHECKPLOT_RES 2000,1500

		#mkdir headers_photom_oldscamp_matchNO/plots_photom
		#cd headers_photom_oldscamp_matchNO/
		if [ $? -ne 0 ]
		then
		    echo "scamp call failed !! Exiting !!"
		    exit 1
		fi
		mkdir plots_photom_${ending}
		mkdir headers_photom_${ending}

		# scamp creates the headers in the directory where the catalogs are:
		${P_FIND}  ./cat_photom/ -name \*.head -exec mv {} ./headers_photom_${ending} \;

		# we want the diagnostic plots in an own directory:
		mv fgroups*         plots_photom_${ending}
		mv distort*         plots_photom_${ending}
		mv astr_interror2d* plots_photom_${ending}
		mv astr_interror1d* plots_photom_${ending}
		mv astr_referror2d* plots_photom_${ending}
		mv astr_referror1d* plots_photom_${ending}
		mv astr_chi2*       plots_photom_${ending}
		mv psphot_error*    plots_photom_${ending}
		mv astr_refsysmap*  plots_photom_${ending}
		mv phot_zpcorr*     plots_photom_${ending}
		mv phot_errorvsmag* plots_photom_${ending}
		mv ${cluster}_scamp.xml plots_photom_${ending}
		cp ~/wtgpipeline/scamp.xsl plots_photom_${ending}
		sed -i.old 's/href=".*"?>/href="scamp.xsl"?>/g' plots_photom_${ending}/${cluster}_scamp.xml
	done
	firefox plots_photom_posangle_*_pixscale_${pixscale}_scamp/${cluster}_scamp.xml &
done
