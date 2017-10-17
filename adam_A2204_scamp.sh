## first guess will be the .ahead files: /nfs/slac/g/ki/ki18/anja/DECAM/Lucie/reduce_DECam_copy/DECam.ahead
## use the cats after they have been split: /nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/r_DECam/cat/dec086030_1OXCLFS.cat (ccd# ranges from 1 to 62 62OXCLFS.cat)
## use the cats after they have been split: ldacsplit -i /nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/r_DECam/cat/dec086030.cat
## /afs/slac/g/ki/software/local/bin/scamp (version 2.0.4)
. progs.ini
P_SCAMP2=/afs/slac/g/ki/software/local/bin/scamp

## SUBARU ahead inputs:
/u/ki/awright/bonnpipeline/SUBARU_c10_2_r0.ahead
/u/ki/awright/bonnpipeline/SUBARU_c10_2_r1.ahead
/u/ki/awright/bonnpipeline/MEGAPRIME.ahead
/u/ki/awright/bonnpipeline/WHT.ahead
## SUBARU cats:
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204$ ls -d */SCIENCE/cat_scampIC
W-C-RC/SCIENCE/cat_scampIC  W-J-B/SCIENCE/cat_scampIC  W-J-V/SCIENCE/cat_scampIC  g/SCIENCE/cat_scampIC  r/SCIENCE/cat_scampIC

## /nfs/slac/g/ki/ki18/anja/DECAM/Lucie/reduce_DECam_copy/create_scamp_astrom_photom_multiinst.sh
/nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/Y_DECam/coadd_V0.0.2A/A2204_Y_DECam.V0.0.2A.swarp.cut.fits
/nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/g_DECam/coadd_V0.0.2A/A2204_g_DECam.V0.0.2A.swarp.cut.fits
/nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/i_DECam/coadd_V0.0.2A/A2204_i_DECam.V0.0.2A.swarp.cut.fits
/nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/r_DECam/coadd_V0.0.2A/A2204_r_DECam.V0.0.2A.swarp.cut.fits
/nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/u_DECam/coadd_V0.0.2A/A2204_u_DECam.V0.0.2A.swarp.cut.fits
/nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/z_DECam/coadd_V0.0.2A/A2204_z_DECam.V0.0.2A.swarp.cut.fits

/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048646/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048647/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048648/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048649/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048650/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048651/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048652/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048653/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048654/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048655/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048656/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048657/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048658/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048659/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048660/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048661/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048662/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_SUPA0048663/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_all/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-C-RC/SCIENCE/coadd_A2204_pretty/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048683/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048684/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048685/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048686/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048687/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048688/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048689/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048690/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048691/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048692/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048693/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048694/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048695/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048696/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048697/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048698/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048699/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_SUPA0048700/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_all/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-B/SCIENCE/coadd_A2204_pretty/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0032876/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0032877/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0032878/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0032879/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0032880/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0032881/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048665/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048666/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048667/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048668/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048669/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048670/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048671/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048672/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048673/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048674/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048675/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048676/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048677/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048678/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048679/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048680/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048681/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_SUPA0048682/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_all/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_gab2025-rot0/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_gab2025-rot1/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_gab2732-rot0/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_gab2732-rot1/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_gabodsid2025/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_gabodsid2732/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_good/coadd.fits
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/W-J-V/SCIENCE/coadd_A2204_pretty/coadd.fits

## adam: run sex and scamp on DECam
ALLCATS=`\ls /nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/{u,g,r,i,z,Y}_DECam/single_V0.0.2A/dec*_*OXCLFSF.sub.fits`
cluster=A2204
INSTRUMENT=DECam
for filter in u g r i z Y
do
	#/nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/${cluster}/${filter}_DECam/
	\ls /nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/${filter}_DECam/single_V0.0.2A/dec*_*OXCL*.sub.fits > subims.log
	\ls /nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/${filter}_DECam/single_V0.0.2A/dec*_*OXCL*.weight.fits > weightims.log
	\ls /nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/${filter}_DECam/single_V0.0.2A/dec*_*OXCL*.flag.fits > flagims.log
	echo /nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/${filter}_DECam/ single_V0.0.2A
	#sub_wt_flag=`wc -l subims.log weightims.log flagims.log`
	#echo $filter , $sub_wt_flag >> decam_data.log
	
	#./parallel_manager.sh ./create_astromcats_scamp_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE WEIGHTS
done

# do_Subaru_register_4batch.sh "astrom" mode
#   if [ ! -d "${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scamp" ]; then
    ###adds astrometric info; makes directory cat with ${image}_${chip}*.cat
    ./parallel_manager.sh ./create_astromcats_scamp_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE WEIGHTS
        #now run sextractor to extract the objects
        ${P_SEX} ${file} -c ${DATACONF}/singleastrom.conf.sex\
                       -CATALOG_NAME /${MAINDIR}/${SCIENCEDIR}/cat_scamp/${BASE}.cat\
                       -SEEING_FWHM $fwhm \
                       -DETECT_MINAREA ${MINAREA} -DETECT_THRESH ${THRESH} \
                       ${FLAG} ${WEIGHT}

    ####################################################################
    ### astrometric and relative photometric calibration:            ###
    ###   this can be done with scamp for all filters simultaneously ###
    ####################################################################
    ./create_scamp_astrom_photom.sh ${LINE} ${ASTROMETRYCAT}
	## FILTER CHIP CATS
        #adam-old# -c "((((FLAGS<20))AND(B_IMAGE>1.2))AND(IMAFLAGS_ISO<97));" \
        ${P_LDACFILTER} -i ${CAT} -t LDAC_OBJECTS \
            -c "(((FLAGS<8)AND(B_IMAGE>0.8))AND((IMAFLAGS_ISO=0)OR(IMAFLAGS_ISO=2)));" \
            -o ${BASE}.ldac

	## MERGE CHIP CATS INTO MEF CAT: from our single chip catalogues create merged MEF catalogues
	# for each exposure:
	# first get the basenames of all available exposures.
	# The following fiddling is necessary because catalogues
	# for individual chips might not be present (bad chips)
	#FOR EACH IMAGE: build up list of indiv chip cats (${IMAGE}_${i}OCF.ldac) in ${CATS}
	#FOR EACH IMAGE: echo "${CATS} ./${IMAGE}_scamp.cat" >> ${DIR}/catlist.txt_$$
	#FOR EACH IMAGE: Dummy external header containing focal plane and missing chip information (AHEADFILE=${DIR}/${INSTRUM}_c${CONFIG}_r${ROTATION}.ahead). They are used to distinguish different chip configurations in an, otherwise, unique astrometric context.
	#after loop, run: python ${S_SCAMPCAT} ${DIR}/catlist.txt_$$

	## RUN SCAMP (after choosing SCAMP params based on conditions)
	MOSAICTYPE="-MOSAIC_TYPE FIX_FOCALPLANE"
	#MOSAICTYPE="-MOSAIC_TYPE UNCHANGED"
	#MOSAICTYPE="-MOSAIC_TYPE LOOSE"
	STARCAT="SDSS-R6"
	scamp_mode_instrum_star="-STABILITY_TYPE INSTRUMENT -ASTREF_CATALOG ${STARCAT} "
	scamp_mode_use=${scamp_mode_instrum_star} #default
	${P_SCAMP} `${P_FIND} ../cat/ -name \*scamp.cat` \
           -c ${CONF}/scamp_astrom_photom.scamp \
           -ASTRINSTRU_KEY FILTER,INSTRUM,CONFIG,ROTATION,MISSCHIP,PPRUN \
           -CDSCLIENT_EXEC ${P_ACLIENT} \
           -NTHREADS ${NPARA} ${MOSAICTYPE} \
           -XML_NAME ${BONN_TARGET}_scamp.xml \
           -MAGZERO_INTERR 0.1 \
           -MAGZERO_REFERR 0.1 \
           -POSITION_MAXERR 5.0 \
           -POSANGLE_MAXERR 30.0 \
           -SN_THRESHOLDS 3,100 \
           -FLAGS_MASK 0x00e0 \
           -MATCH_NMAX 10000 \
           -CROSSID_RADIUS 0.3 \
           -PIXSCALE_MAXERR 1.03 \
           -DISTORT_DEGREES 3 \
           -ASTREF_WEIGHT 1 ${scamp_mode_use}
	#scamp creates the headers in the directory where the catalogs are, and diagnostic plots elsewhere

	## FIND PHOT ZPs OF ALL KINDS (get the relative magnitude offsets from the FLXSCALES estimated by scamp)
	# make list with each row as: ${NAME}" "${EXPTIME}" "${FLXSCALE}" "${PHOTINST}
	# awk script calculates relative zeropoints and THELI fluxscales for the different photometric contexts.
	# then split the exposure catalogues for the indivudual chips, add the RZP and FLXSCALE header keywords, and put cats in headers_scamp_${STARCAT}

# do_Subaru_register_4batch.sh "photom" mode
    ./parallel_manager.sh ./create_astromcats_scampIC_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE WEIGHTS
        #now run sextractor to extract the objects
        ${P_SEX} ${file} -c ${DATACONF}/singleastrom.conf.sex\
                       -CATALOG_NAME /$1/$2/cat_scampIC/${BASE}.cat\
                       -SEEING_FWHM $fwhm \
                       -DETECT_MINAREA ${MINAREA} -DETECT_THRESH ${THRESH} \
                       ${FLAG} ${WEIGHT}
    THRESH=$(( ${SATURATION}-4000 ))
    ./create_scamp_photom.sh ${LINE} ${THRESH} ${ASTROMETRYCAT}
    ##same as create_scamp_astrom_photom.sh just more careful 2nd pass
	${P_SCAMP} `${P_FIND} ../cat_photom/ -name \*scamp.cat` \
        -c ${CONF}/scamp_astrom_photom.scamp \
        -PHOTINSTRU_KEY FILTER -ASTRINSTRU_KEY ASTINST,MISSCHIP \
        -CDSCLIENT_EXEC ${P_ACLIENT} \
        -NTHREADS ${NPARA} \
        -XML_NAME ${BONN_TARGET}_scamp.xml \
        -MAGZERO_INTERR 0.1 \
        -MAGZERO_REFERR 0.1 \
        -MATCH N \
        -SN_THRESHOLDS 5,50 \
        -MOSAIC_TYPE UNCHANGED \
        -CROSSID_RADIUS 0.2 \
        -DISTORT_DEGREES 3 \
        -ASTREF_WEIGHT 1 ${scamp_mode_use}

## what *scamp.cat files can we find in /nfs/slac/g/ki/ki05/anja/SUBARU/A2204/g/SCIENCE/astrom_photom_scamp_2MASS/cat/
/nfs/slac/g/ki/ki05/anja/SUBARU/A2204$ find . -name "*scamp.cat"
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048662_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0032876_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048663_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0032877_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048700_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048660_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048648_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048661_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048649_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048666_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048667_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048689_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048688_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048665_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048686_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048687_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048684_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048669_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048685_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048668_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048647_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048682_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048646_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048683_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048680_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0032879_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0032878_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048681_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048656_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048693_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048657_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048692_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048691_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048654_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048690_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048655_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048697_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048652_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048696_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048653_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0032881_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048678_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048650_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048695_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048679_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0032880_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048651_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048694_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048677_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048676_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048675_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048698_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048674_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048699_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048673_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048672_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048659_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048671_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048658_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6/cat/SUPA0048670_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048647_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048682_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048646_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048683_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0032879_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048680_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048681_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0032878_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048686_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048687_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048669_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048684_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048668_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048685_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048666_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048667_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048689_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048665_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048688_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0032876_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048662_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0032877_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048663_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048648_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048700_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048660_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048649_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048661_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048673_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048672_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048671_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048659_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048670_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048658_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048677_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048676_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048698_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048675_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048699_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048674_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048697_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048652_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048696_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048653_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048650_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048695_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048678_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0032881_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048651_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048694_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0032880_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048679_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048656_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048693_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048657_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048692_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048691_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048654_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048690_scamp.cat
./W-J-B/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048655_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048675_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/793601p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048698_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048674_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/795862p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048699_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048677_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048676_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048659_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048671_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048658_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048670_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048673_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/793598p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/793537p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048672_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048691_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048654_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048690_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/793603p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048655_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048656_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048693_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/793250p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048657_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048692_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/793539p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/793596p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048678_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0032881_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048650_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048695_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0032880_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048679_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048651_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048694_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048697_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048652_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048696_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/792999p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048653_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048684_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048669_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048685_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048668_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048686_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/792998p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048687_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0032879_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048680_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/793602p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/793540p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048681_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0032878_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/795861p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/793597p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048647_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048682_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/793538p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048646_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048683_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048700_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048660_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048648_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048661_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048649_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048662_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0032876_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048663_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0032877_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/793249p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048689_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048688_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048665_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/793600p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048666_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/793595p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat_photom/SUPA0048667_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048684_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048669_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048685_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048668_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/793537p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048686_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/793598p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048687_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0032879_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048680_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/795862p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/793601p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048681_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0032878_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048647_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048682_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048646_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048683_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048700_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048660_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048648_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048661_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048649_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048662_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/792999p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0032876_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048663_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0032877_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048689_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/793603p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048688_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048665_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/793596p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048666_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/793539p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/793250p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048667_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048675_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/795861p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/793540p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048698_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048674_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/793602p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048699_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048677_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048676_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/793538p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/793597p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048659_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048671_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048658_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048670_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048673_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048672_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/792998p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048691_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/793600p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048654_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048690_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048655_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048656_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048693_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/793595p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048657_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048692_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048678_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0032881_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048650_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048695_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0032880_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048679_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048651_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048694_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/793249p_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048697_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048652_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048696_scamp.cat
./g/SCIENCE/astrom_photom_scamp_2MASS/cat/SUPA0048653_scamp.cat
