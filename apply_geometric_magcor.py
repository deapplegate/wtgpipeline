#!/usr/bin/env python
#################
# Applies Geometric Distortion Flux Correction to Unstacked Catalogs
################

import os, glob, re, sys, copy
import astropy.io.fits as pyfits, numpy as np
import ldac, utilities
import calctransformscaling as cts
import dump_cat_filters as dcf
import photocalibrate_cat as pcc
import measure_unstacked_photometry as mup

################

subarudir = '/nfs/slac/g/ki/ki05/anja/SUBARU'
swarpconfig = "/u/ki/anja/software/ldacpipeline-0.12.20/conf/reduction/create_coadd_swarp.swarp"

swarpargs = {}
swarpargs['RESAMPLE'] = 'Y'
swarpargs['COMBINE'] = 'N'
swarpargs["RESAMPLE_SUFFIX"] = "RXJ1720_all.resamp.fits"
swarpargs["RESAMPLE_DIR"] = "/u/ki/dapple/nfs/swarp-code/swarp-2.19.1/src/temp"
swarpargs['NTHREADS'] = "1"


################

def uniqueMasterFilters(filters):

    masterfilters = []
    
    for filter in filters:
        masterfilter = '-'.join(filter.split('-')[3:])
        if masterfilter not in masterfilters:
            masterfilters.append(masterfilter)

    return masterfilters


################

def applyCorrection(cluster, lensingfilter, activefilter = None):

    clusterdir = '%s/%s' % (subarudir, cluster)
    photdir = '%s/PHOTOMETRY_%s_aper' % (clusterdir, lensingfilter)
    lensingcoadddir = '%s/%s/SCIENCE/coadd_%s_all' % (clusterdir, lensingfilter, cluster)

    coaddfile = '%s/coadd.fits' % lensingcoadddir

    photcat = ldac.openObjectFile('%s/%s.slr.cat' % (photdir, cluster))

    if activefilter is None:
    
        filters = dcf.dumpFilters(photcat)

        masterfilters = uniqueMasterFilters(filters)

    else:

        masterfilters = [activefilter]

    for filter in masterfilters:

        catdir = '%s/%s/unstacked' % (photdir, filter)
        filtercoadddir = '%s/%s/SCIENCE/coadd_%s_all' % (clusterdir, filter, cluster)

        exposurecats = glob.glob('%s/*.filtered.cat' % (catdir))

        localargs = copy.copy(swarpargs)
        localargs['RESAMPLE_SUFFIX'] = "%s_all.resamp.fits" % cluster
        localargs['RESAMPLE_DIR'] = filtercoadddir

        for catfile in exposurecats:

            base = os.path.basename(catfile)
            
            exposure = base.split('.')[0]

            inputfiles = glob.glob('%s/%s_*.sub.fits' \
                                       % (filtercoadddir, exposure))

            print len(inputfiles)
            if len(inputfiles) == 0:
                print "Skipping %s" % exposure
                continue

            cat = ldac.openObjectFile(catfile)


            posdat = np.column_stack([cat['ALPHA_J2000'], cat['DELTA_J2000']])



            fluxscale = cts.calcTransformScaling(coaddfile, 
                                                 inputfiles,
                                                 swarpconfig,
                                                 swarpargs,
                                                 posdat)

            badfluxes = fluxscale < -9998
            

            flux_keys, fluxerr_keys, magonlykeys, other_keys = utilities.sortFluxKeys(cat.keys())

            cols = [pyfits.Column(name = 'fluxscale', format='E', array = fluxscale)]
            for key in other_keys:
                if not (re.match('^MAG_', key) or re.match('^MAGERR_', key)):
                    cols.append(cat.extractColumn(key))

            for fluxkey in flux_keys:

                fluxtype = utilities.extractFluxType(fluxkey)
                fluxerr_key = 'FLUXERR_%s' % fluxtype
                mag_key = 'MAG_%s' % fluxtype
                magerr_key = 'MAGERR_%s' % fluxtype

                if len(cat[fluxkey].shape) == 1:
                    flux = cat[fluxkey]*fluxscale
                    fluxerr = cat[fluxerr_key]*fluxscale
                    
                    flux[badfluxes] = mup.__bad_flux__
                    fluxerr[badfluxes] = mup.__bad_flux__

                    arraysize = 'E'
                else:
                    flux = np.zeros_like(cat[fluxkey])
                    fluxerr = np.zeros_like(cat[fluxerr_key])
                    for i in range(flux.shape[1]):
                        flux[:,i] = cat[fluxkey][:,i]*fluxscale
                        fluxerr[:,i] = cat[fluxerr_key][:,i]*fluxscale

                        flux[:,i][badfluxes] = mup.__bad_flux__
                        fluxerr[:,i][badfluxes] = mup.__bad_flux__
                    arraysize = '%dE' % flux.shape[1]
                

                mag, magerr = mup.calcMags(flux, fluxerr)

                cols.append(pyfits.Column(name = fluxkey,
                                          format = arraysize,
                                          array = flux))
                cols.append(pyfits.Column(name = fluxerr_key,
                                          format = arraysize,
                                          array = fluxerr))
                cols.append(pyfits.Column(name = mag_key,
                                          format = arraysize,
                                          array = mag))
                cols.append(pyfits.Column(name = magerr_key,
                                          format = arraysize,
                                          array = magerr))

            for magkey in magonlykeys:

                magtype = utilities.extractMagType(magkey)

                magerr_key = 'MAGERR_%s' % magtype

                newmag = cat[magkey] - 2.5*np.log10(fluxscale)

                magerr = cat[magerr_key]

                cols.append(pyfits.Column(name = magkey,
                                          format = 'E',
                                          array = newmag))
                cols.append(pyfits.Column(name = magerr_key,
                                          format = 'E',
                                          array = magerr))

            correctedCat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols)))

            hdus = [pyfits.PrimaryHDU(), correctedCat.hdu]
            hdus.extend(pcc._transferOtherHDUs(catfile))
            hdulist = pyfits.HDUList(hdus)
            print '%s/%s.corrected.cat' % (catdir, base)
            hdulist.writeto('%s/%s.corrected.cat' % (catdir, base), overwrite=True)



    
####################################

if __name__ == '__main__':

    cluster = sys.argv[1]
    filter = sys.argv[2]

    activefilter = None
    if len(sys.argv) > 3:
        activefilter = sys.argv[3]

    applyCorrection(cluster, filter, activefilter)
