sex /nfs/slac/g/ki/ki05/anja/proposals/chandra_c17_hiz_group/lenstool/image.fits -c ./photconf/phot.conf.sex \
            -PARAMETERS_NAME ./photconf/phot.param.short.sex \
            -DETECT_MINAREA 3 -DETECT_THRESH 1.5 -ANALYSIS_THRESH 1.5 \
            -MAG_ZEROPOINT 27.0 \
            -FLAG_TYPE MAX\
            -FLAG_IMAGE ""\
            -DEBLEND_MINCONT 0.00005\
            -CHECKIMAGE_NAME /tmp/coadd.background.fits,/tmp/coadd.apertures.fits,/tmp/coadd.segmentation.fits\
            -CHECKIMAGE_TYPE BACKGROUND,APERTURES,SEGMENTATION\
            -WEIGHT_TYPE NONE 

