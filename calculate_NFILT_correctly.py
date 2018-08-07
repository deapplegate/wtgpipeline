#! /usr/bin/env python
#adam-from# this was extracted from adam_plot_bpz_output.py/bpz_analyzer.py and converted into a function, it has to be incorporated into adam_bigmacs_apply_zps.py at some point
#adam-does#  calculates NFILT from the number of observations for each object in the photometry catalog
# 
#ADVICE: when starting fresh with a new cluster. first search for #adam-Warning# in this code and change stuff whereever there is a #adam-Warning#

import numpy
import sys,os
purepath=sys.path
sys.path=purepath+['/u/ki/awright/InstallingSoftware/pythons/','/u/ki/awright/wtgpipeline/']
import ldac
from adam_bigmacs_apply_zps import getZP

try:
        cl=os.environ['cluster']
except:
        cl='MACS1115+01'


def calc_NFILT(cluster=cl):
    ## open photometry catalog
    mag_fl = "/nfs/slac/g/ki/ki18/anja/SUBARU/%s/PHOTOMETRY_W-C-RC_aper/%s.calibrated_PureStarCalib.alter.cat" % (cluster,cluster)
    flzps="/nfs/slac/g/ki/ki18/anja/SUBARU//%s/PHOTOMETRY_W-C-RC_aper/%s.bigmacs_cleaned_offsets-PureStarCalib.list" % (cluster,cluster)
    assert(os.path.isfile(mag_fl))
    assert(os.path.isfile(flzps))

    #adam-useful# document this later, it's helpful!
    #adam-Warning# I'll have to choose between 10_3 and 10_2 mags in a more robust way eventually

    ## Make NFILT calculation count 10_3 and 10_2 mags from the same filter as one 
    # first get the lensing mag/filter
    in_lens_file=0
    fo_lens_filter=open('lensing_coadd_type_filter.list','r')
    lines_lens_filter=fo_lens_filter.readlines()
    for line in lines_lens_filter:
        clean_line=line.strip()
        if line.startswith(cluster):
            line_data=[dat for dat in clean_line.split(' ') if not dat is '']
            cluster_lens,type_lens,filt_lens,mag_lens=line_data
            print ' cluster_lens=',cluster_lens , ' type_lens=',type_lens , ' filt_lens=',filt_lens , ' mag_lens=',mag_lens
            in_lens_file=1

    #adam-Warning# eventually this quick and dirty way of choosing between filters won't work
    if in_lens_file==0:
        raise Exception(cluster+" not found in lensing_coadd_type_filter.list...find another way to choose between different configs if needed!")

    # apply the NFILT cuts, and put the resulting catalog somewhere for @Ricardo Herbonnet to find
    filt_zp_err=getZP(flzps)
    mag_aper1_keys=filt_zp_err.keys()
    mag_aper1_sdr={} #get a system of distinct representatives (SDR)
    for mag_key in mag_aper1_keys:
        filt=mag_key[mag_key.find('W-'):]
        if filt==filt_lens:
            if mag_key==mag_lens:
                mag_aper1_sdr[filt]=mag_key
            else:
                print "not including %s in NFILT calculation, since it's of the lensing-band, but not the actual lensing magnitude" % (mag_key)
        else:
            mag_aper1_sdr[filt]=mag_key

    mag_aper1_keys_clean=mag_aper1_sdr.values()

    catinput=ldac.openObjectFile(mag_fl)
    for i,mag_key in enumerate(mag_aper1_keys_clean):
        flux_key=mag_key.replace("MAG_APER1","FLUX_APER1")
        fluxerr_key=flux_key.replace("FLUX","FLUXERR")
        filt=mag_key[mag_key.find('W-'):]
        flag_key='IMAFLAGS_ISO-SUBARU-'+filt

        #adam-switch#     m=catinput[mag_key].copy()
        #adam-switch#     if not m.ndim==1: raise Exception("this column doesn't seem to need to be split (shape is "+str(inmag.shape)+"), but it has APER- in the name. Thats weird and contradictory")
        #adam-switch#     f=catinput[flux_key].copy()
        #adam-switch#     flag=catinput[flag_key].copy()
        ef=catinput[fluxerr_key].copy()
        #nondetected=(f<=0.)*(ef>0) #Flux <=0, meaningful phot. error
        #nonobserved=(ef<=0.) #Negative errors were not observed
        #detected=numpy.logical_not(nondetected+nonobserved)
        #detected=(f>0.)*(flag<2)
        #adam-switch# observed=(ef>0.)*(flag<=4)
        observed=(ef>0.)
        if i==0:
            NFILT_corrected=numpy.zeros(observed.shape,dtype=numpy.float32)
        NFILT_corrected+=numpy.array(observed,dtype=numpy.float32)

        ## check how the data looks
        print '\n%s\n## observed: %i  (of %i). Percentage: %.1f  ## ' % (filt,observed.sum(),observed.__len__(),100*observed.mean())

    return NFILT_corrected
