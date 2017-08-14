#! /bin/bash -xv

. progs.ini

### simple version, single filter

cluster=$1
detectfilter=$2

#################################

DETECTTHRESH=1.5

#################################

filters=`grep "${cluster}" cluster_cat_filters.dat | awk -v ORS=' ' '{for(i=3;i<=NF;i++){if($i!~"CALIB" && $i!="K") print $i}}'`

PXSCALE=0.2
reddir=`pwd`
subaru05dir=/nfs/slac/g/ki/ki05/anja/SUBARU
subaru06dir=/nfs/slac/g/ki/ki06/anja/SUBARU
photdir=${subaru06dir}/photometry_clustergals

cluster05dir=${subaru05dir}/${cluster}
clusterphot=${photdir}/${cluster}

allimage=${cluster05dir}/${detectfilter}/SCIENCE/coadd_${cluster}_all/coadd.fits
prettyimage=${cluster05dir}/${detectfilter}/SCIENCE/coadd_${cluster}_pretty/coadd.fits
prettyweight=${cluster05dir}/${detectfilter}/SCIENCE/coadd_${cluster}_pretty/coadd.weight.fits
prettyflag=${cluster05dir}/${detectfilter}/SCIENCE/coadd_${cluster}_pretty/coadd.flag.fits

if [  -e seeing_big_${cluster}.dat ]; then
    rm seeing_big_${cluster}.dat
fi


files="${cluster05dir}/W-?-??/SCIENCE/coadd_${cluster}_all/coadd.fits
       ${cluster05dir}/W-?-?/SCIENCE/coadd_${cluster}_all/coadd.fits
       ${cluster05dir}/?/SCIENCE/coadd_${cluster}_all/coadd.fits
       ${cluster05dir}/[UB]-WHT/SCIENCE/coadd_${cluster}_all/coadd.fits"

for file in $files; do
    
    if [ -e $file ]; then

        seeing=`dfits $file | fitsort -d SEEING | awk '{print $2}'`
        echo $file $seeing >> seeing_big_${cluster}.dat
    fi
    
done

worstseeing=`sort -n -k2 seeing_big_${cluster}.dat | tail -n1 | awk '{print $2}'`
detectseeing=`dfits ${allimage}| fitsort -d SEEING | awk '{print $2}'`
convolveseeing=`echo "worst=${worstseeing}; maxconvolve=${detectseeing}+.3; if (maxconvolve < worst) {maxconvolve} else {worst}" | bc`


if [ ! -d ${photdir}/${cluster} ]; then
   mkdir ${photdir}/${cluster}
fi

if [ ! -d ${photdir}/${cluster}/PHOTOMETRY_${detectfilter}_unconv ]; then
   mkdir ${photdir}/${cluster}/PHOTOMETRY_${detectfilter}_unconv
fi

if [ ! -d ${photdir}/${cluster}/PHOTOMETRY_${detectfilter}_conv ]; then
   mkdir ${photdir}/${cluster}/PHOTOMETRY_${detectfilter}_conv
fi


########################################################################################

cd ${photdir}/${cluster}

### convolve all filters to worst seeing

for filter in ${filters}
do

  (
  seeing=`dfits ${cluster05dir}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits | fitsort -d SEEING | awk '{print $2}'`
  convflag=`awk 'BEGIN{if('${seeing}'<'${convolveseeing}') print 1; else print 0}'`

  if [ "${filter}" == "I" ]; then
    image=${cluster05dir}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits
  else
    image=${cluster05dir}/${filter}/SCIENCE/coadd_${cluster}_pretty/coadd.fits
  fi

  if [ ${convflag} -eq 1 ]; then

    python ${reddir}/create_gausssmoothing_kernel.py ${seeing} ${convolveseeing} ${PXSCALE} ${filter}_worst_${detectfilter}.conv
    
    ${P_SEX} ${image} \
           -c ${BPPHOTCONF}/smooth_better.image.conf.sex \
           -FLAG_IMAGE "" -WEIGHT_IMAGE "" \
           -FILTER_NAME ${filter}_worst_${detectfilter}.conv \
           -CATALOG_TYPE FITS_LDAC -CATALOG_NAME ${filter}_empty_${detectfilter}.cat \
           -CHECKIMAGE_NAME ${filter}_pretty_convolved_${detectfilter}.fits

  else
    cp  ${image} ${filter}_pretty_convolved_${detectfilter}.fits
  fi

   ) &

done
wait


### note: the background settings don't affect SE's RMS measurement because it is relative
### to the median (background?) value
if [ ! -f ${detectfilter}_empty_${detectfilter}.cat ]; then
    ${P_SEX} ${cluster05dir}/${detectfilter}/SCIENCE/coadd_${cluster}_pretty/coadd.fits \
           -c ${BPPHOTCONF}/smooth_better.image.conf.sex \
           -FLAG_IMAGE "" -WEIGHT_IMAGE "" \
           -FILTER_NAME ${BPPHOTCONF}/gauss_1.5_3x3.conv \
           -CATALOG_TYPE FITS_LDAC -CATALOG_NAME ${detectfilter}_empty_${detectfilter}.cat \
           -CHECKIMAGE_NAME tmp.fits
    rm tmp.fits
fi

rmsdetectimage=`${P_LDACTOASC} -i ${detectfilter}_empty_${detectfilter}.cat -t LDAC_IMHEAD -s | fold | awk '{if($1=="SEXBKDEV=") print $2}'`

################################################################
### for detecting on image "pre-filtered with 1.5 sigma gaussian

${P_SEX} -c ${BPPHOTCONF}/smooth_better.image.conf.sex \
         ${prettyimage} \
         -FLAG_IMAGE "" -WEIGHT_IMAGE "" \
         -CATALOG_NAME tmp01_${detectfilter}.cat \
         -CHECKIMAGE_NAME ${detectfilter}_pretty_filtered1.5_${detectfilter}.fits

### run SE to measure RMS in filtered image

${P_SEX} -c ${BPPHOTCONF}/smooth_better.image.conf.sex \
         ${detectfilter}_pretty_filtered1.5_${detectfilter}.fits \
         -FLAG_IMAGE "" -WEIGHT_IMAGE "" \
         -CATALOG_NAME empty1p5_${detectfilter}.cat \
         -CHECKIMAGE_TYPE NONE

rmsfilt1p5=`${P_LDACTOASC} -i empty1p5_${detectfilter}.cat -t LDAC_IMHEAD -s | fold | awk '{if($1=="SEXBKDEV=") print $2}'`

### this is for the "unconvolved" image
detect1p5thresh=`awk 'BEGIN{print '${DETECTTHRESH}'*'${rmsdetectimage}'/'${rmsfilt1p5}'}'`

######################################################
### for detecting on image convolved to worst seeing

### run SE to measure RMS in filtered image

${P_SEX} -c ${BPPHOTCONF}/smooth_better.image.conf.sex \
         ${detectfilter}_pretty_convolved_${detectfilter}.fits \
         -FLAG_IMAGE "" -WEIGHT_IMAGE "" \
         -CATALOG_NAME ${detectfilter}_empty2_${detectfilter}.cat \
         -CHECKIMAGE_TYPE NONE

convolvrms=`${P_LDACTOASC} -i ${detectfilter}_empty2_${detectfilter}.cat -t LDAC_IMHEAD -s | fold | awk '{if($1=="SEXBKDEV=") print $2}'`
convolvethresh=`awk 'BEGIN{print '${DETECTTHRESH}'*'${rmsdetectimage}'/'${convolvrms}'}'`

#####################################################
### now run dual-image mode for all filters

for phottype in unconv conv
do

  cd ${photdir}/${cluster}

  case ${phottype} in
    "unconv" )
       detectimage=${detectfilter}_pretty_filtered1.5_${detectfilter}.fits
       thresh=${detect1p5thresh}
       ;;
    "conv" )
       detectimage=${detectfilter}_pretty_convolved_${detectfilter}.fits
       thresh=${convolvethresh}
       ;;
  esac

  for filter in ${filters}
  do
  
    (

    if [ "${filter}" == "I" ]; then
      filterprettyimage=${cluster05dir}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits
      filterprettyweight=${cluster05dir}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.weight.fits
      filterprettyflag=${cluster05dir}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.flag.fits
    else
      filterprettyimage=${cluster05dir}/${filter}/SCIENCE/coadd_${cluster}_pretty/coadd.fits
      filterprettyweight=${cluster05dir}/${filter}/SCIENCE/coadd_${cluster}_pretty/coadd.weight.fits
      filterprettyflag=${cluster05dir}/${filter}/SCIENCE/coadd_${cluster}_pretty/coadd.flag.fits
    fi
  
    if [ ! -f ${filterprettyflag} ]; then
      ic -p 8 '16 1 %1 1e-6 < ?' ${filterprettyweight} > ${filterprettyflag}
    fi
  
    seeing=`dfits ${cluster05dir}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits | fitsort -d SEEING | awk '{print $2}'`

    if [ "${filter}" == "${detectfilter}" ]; then
  
      ${P_SEX} -c ${BPPHOTCONF}/clustergals.conf.sex \
             -PARAMETERS_NAME ${BPPHOTCONF}/clustergals_detect.param.sex \
             ${detectimage},${filter}_pretty_convolved_${detectfilter}.fits \
             -WEIGHT_IMAGE ${prettyweight},${filterprettyweight} \
             -FLAG_IMAGE ${filterprettyflag} \
             -SEEING_FWHM ${seeing} \
             -DETECT_THRESH ${thresh} -ANALYSIS_THRESH ${thresh} \
             -CATALOG_NAME PHOTOMETRY_${detectfilter}_${phottype}/${filter}_detect.cat \
	     -CHECKIMAGE_NAME PHOTOMETRY_${detectfilter}_${phottype}/segm.fits
      
      ${P_LDACDELKEY} -i PHOTOMETRY_${detectfilter}_${phottype}/${filter}_detect.cat \
                      -o PHOTOMETRY_${detectfilter}_${phottype}/${filter}_detect.cat4 \
                      -t LDAC_OBJECTS \
                      -k FLUX_APER

      ${P_LDACCONV} -i PHOTOMETRY_${detectfilter}_${phottype}/${filter}_detect.cat4 -o PHOTOMETRY_${detectfilter}_${phottype}/${filter}_detect.cat0 -b 1 -c 1 -f ${filter}
      
      ${reddir}/convert_aper.py PHOTOMETRY_${detectfilter}_${phottype}/${filter}_detect.cat0 PHOTOMETRY_${detectfilter}_${phottype}/${filter}_detect.cat1
  
    fi
  
    ${P_SEX} -c ${BPPHOTCONF}/clustergals.conf.sex \
           -PARAMETERS_NAME ${BPPHOTCONF}/clustergals_measure.param.sex \
           ${detectimage},${filter}_pretty_convolved_${detectfilter}.fits \
           -WEIGHT_IMAGE ${prettyweight},${filterprettyweight} \
           -FLAG_IMAGE ${filterprettyflag} \
           -SEEING_FWHM ${seeing} \
           -DETECT_THRESH ${thresh} -ANALYSIS_THRESH ${thresh} \
           -CATALOG_NAME PHOTOMETRY_${detectfilter}_${phottype}/${filter}_convolved.cat \
	   -CHECKIMAGE_TYPE NONE
  
    ${P_LDACCONV} -i PHOTOMETRY_${detectfilter}_${phottype}/${filter}_convolved.cat -o PHOTOMETRY_${detectfilter}_${phottype}/${filter}_convolved.cat0 -b 1 -c 1 -f ${filter}
  
    ${reddir}/convert_aper.py PHOTOMETRY_${detectfilter}_${phottype}/${filter}_convolved.cat0 PHOTOMETRY_${detectfilter}_${phottype}/${filter}_convolved.cat1
  
  
    ${P_SEX} -c ${BPPHOTCONF}/clustergals.conf.sex \
           -PARAMETERS_NAME ${BPPHOTCONF}/clustergals_measure_unconv.param.sex \
           ${detectimage},${filterprettyimage} \
           -WEIGHT_IMAGE ${prettyweight},${filterprettyweight} \
           -FLAG_IMAGE ${filterprettyflag} \
           -SEEING_FWHM ${seeing} \
           -DETECT_THRESH ${thresh} -ANALYSIS_THRESH ${thresh} \
           -CATALOG_NAME PHOTOMETRY_${detectfilter}_${phottype}/${filter}_unconvolved.cat \
	   -CHECKIMAGE_TYPE NONE

    ${P_LDACDELKEY} -i PHOTOMETRY_${detectfilter}_${phottype}/${filter}_unconvolved.cat \
                    -o PHOTOMETRY_${detectfilter}_${phottype}/${filter}_unconvolved.cat4 \
                    -t LDAC_OBJECTS \
                    -k FLUX_APER
  
    ${P_LDACCONV} -i PHOTOMETRY_${detectfilter}_${phottype}/${filter}_unconvolved.cat4 -o PHOTOMETRY_${detectfilter}_${phottype}/${filter}_unconvolved.cat0 -b 1 -c 1 -f ${filter}
  
    ${P_LDACRENKEY} -i PHOTOMETRY_${detectfilter}_${phottype}/${filter}_unconvolved.cat0 \
	            -o PHOTOMETRY_${detectfilter}_${phottype}/${filter}_unconvolved.cat1 \
	            -t OBJECTS \
	            -k FLUX_RADIUS rg
  
    ) &
  
  done
  wait


  cd PHOTOMETRY_${detectfilter}_${phottype}

  string=""
  for filter in ${filters}
  do
  
    shortfilt=${filter}
    case ${filter} in
      "W-J-U" | "W-J-B" | "W-J-V" | "W-C-RC" | "W-C-IC" | "W-S-I+" | "W-S-Z+" )
         instrum=SUBARU
         ;;
      "u" | "g" | "r" | "i" | "z" )
         instrum=MEGAPRIME
         ;;
      "U-WHT" | "B-WHT" )
         instrum=WHT
         shortfilt=`echo ${filter} | awk 'BEGIN{FS="-"}{print $1}'`
         ;;
      * )
        instrum=SPECIAL
        ;;
    esac
  
    string="${string} ${filter}_convolved.cat1 ${instrum}-conv-1-${shortfilt} ${filter}_unconvolved.cat1 ${instrum}-${shortfilt}"
  
  done
  
  ${reddir}/merge_filters.py ${cluster}.raw.cat ${detectfilter}_detect.cat1 ${string}

  
  for filter in ${filters}
  do
  
  
    shortfilt=${filter}
    case ${filter} in
      "W-J-U" | "W-J-B" | "W-J-V" | "W-C-RC" | "W-C-IC" | "W-S-I+" | "W-S-Z+" )
         instrum=SUBARU
         ;;
      "u" | "g" | "r" | "i" | "z" )
         instrum=MEGAPRIME
         ;;
      "U-WHT" | "B-WHT" )
         instrum=WHT
         shortfilt=`echo ${filter} | awk 'BEGIN{FS="-"}{print $1}'`
         ;;
      * )
        instrum=SPECIAL
        ;;
    esac
  
    longfilters=`${reddir}/dump_cat_filters.py ${cluster}.raw.cat | grep ${filter} | grep conv |awk -v ORS=' ' '{print}'`
    ${reddir}/transfer_photocalibration.py -c ${cluster} -f ${instrum}-COADD-1-${filter} --spec mode=APER1 ${longfilters}
  
  done
  
  ${reddir}/photocalibrate_cat.py -i ${cluster}.raw.cat -c ${cluster} -o ${cluster}.cat --spec mode=APER1

done

rm ${photdir}/${cluster}/*_convolved_${detectfilter}.fits
