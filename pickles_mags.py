#!/usr/bin/env python

import sys, glob,astropy, astropy.io.fits as pyfits, os.path
from numpy import *
import scipy.interpolate.interpolate as interp
from dappleutils import readtxtfile
from optparse import OptionParser

c = 2.99792458e18 #Angstroms/s

spectrafiles = glob.glob('pickles/*.dat')
spectra = [readtxtfile(s)[:,:2] for s in spectrafiles]
nspectra = len(spectra)

def applyFilter(filterfile):

    filter = readtxtfile(filterfile)[:,:2]
    step = filter[1,0] - filter[0,0]

    #convert photon response filters to flux response filters
    filterSpline = interp.interp1d(filter[:,0], filter[:,1], 
                                   bounds_error = False, 
                                   fill_value = 0.)

    
    spec_mags = []
    for spec in spectra:
        specStep = spec[1,0] - spec[0,0]
        resampFilter = filterSpline(spec[:,0])

        logEff = log10(sum(specStep * resampFilter * spec[:,0]*spec[:,1]))
        logNorm = log10(sum(resampFilter*c*specStep/spec[:,0])) #pivot wavelength, with cancelation of norm
        mag = 2.5*(logNorm - logEff)
        spec_mags.append(mag)
        
    return spec_mags

def computeInstrument(instrument, filterfiles):


    spec_filters = [pyfits.Column(name='SeqNr',
                                  format='J',
                                  array = arange(1,nspectra+1))]

    for filterfile in filterfiles:
        
        filtername, ext = os.path.splitext(os.path.basename(filterfile))
        try:
            spec_mags = applyFilter(filterfile)
        except:
            pass
        spec_filters.append(pyfits.Column(name=filtername,
                                          format = 'D',
                                          array = array(spec_mags)))


    cols = pyfits.ColDefs(spec_filters)
    table = pyfits.BinTableHDU.from_columns(cols)
    table.header['EXTNAME']=( instrument, 'table name')
    return table

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-i', dest='inputcat',
                      help='catalog to append table to',
                      default = None)
    parser.add_option('-o', dest='outputcat',
                      help='file to save output to',
                      default = None)
    parser.add_option('-t', '--instrument',
                      help='instrument name (REQUIRED)',
                      dest='instrument')
    parser.add_option('-f', '--filterdir', dest='filterdir',
                      help='Directory with filers',
                      default=None)
    
    options, args = parser.parse_args()

    if options.instrument is None:
        parser.error('Instrument Required')
    instrument = options.instrument
        

    if options.inputcat is None:
        hdulist = pyfits.HDUList([pyfits.PrimaryHDU()])
    else:
        hdulist = pyfits.open(options.inputcat)

    filterdir = options.filterdir
    if filterdir is None:
        filterdir = instrument

    filters = glob.glob('%s/*.pb' % filterdir) + glob.glob('%s/*.res' % filterdir)
    table = computeInstrument(instrument, filters)
    hdulist.append(table)

    if options.outputcat is None:
        hdulist.writeto('Pickles.%s.cat' % instrument, overwrite = True)
    else:
        hdulist.writeto(options.outputcat, overwrite = True)





    
    
