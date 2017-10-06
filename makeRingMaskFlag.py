#!/usr/bin/env python
#################################

from __future__ import with_statement
import sys, os
import pywcs, astropy.io.fits as pyfits, numpy as np
import regionfile, ldac, matching

#################################


ringsizes = {
    '1' : 380,
    '2' : 740,
    '3' : 1060,
    '4' : 1420
    }


def processCluster(brightstarfile, refimage, inputcat, outputfile, outputregionfile):

    wcs = pywcs.WCS(pyfits.open(refimage)[0].header)

    outputregions = []

    if os.path.exists(brightstarfile):

        with open(brightstarfile) as input:

            for line in input.readlines():

                tokens = line.split()

                wcs_x = float(tokens[0])
                wcs_y = float(tokens[1])

                largest_ring = tokens[-1]


                pixCoord = wcs.wcs_sky2pix([wcs_x], [wcs_y], 1)

                pix_x = pixCoord[0][0]
                pix_y = pixCoord[1][0]

                if largest_ring in ringsizes:
                    radii = ringsizes[largest_ring]
                else:
                    radii = ringsizes['4']

                outputregions.append(((pix_x, pix_y), radii))

        
    cat = ldac.openObjectFile(inputcat)

    objCat = matching.Catalog(cat['Xpos'],
                              cat['Ypos'],
                              cat['SeqNr'])

    toMask = {}
    for id in cat['SeqNr']:
        toMask[id] = False

    trie = matching.buildTrie(objCat)

    regions = []
    for (x,y),rad in outputregions:

        matchedObjs = trie.findNeighbors(np.array([x,y]), rad)

        for id in matchedObjs:
            toMask[id] = True

        regions.append(regionfile.Circle(np.array([x,y]), rad))


    flagColumn = np.zeros(len(cat))
    masked = np.array([toMask[x] for x in cat['SeqNr']])
    flagColumn[masked] = 1.

    outcat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([pyfits.Column(name = 'SeqNr', format = 'K', array = cat['SeqNr']),
                                                                         pyfits.Column(name = 'InRings', format = 'K', array = flagColumn)])))

    outcat.saveas(outputfile, overwrite=True)

    regionfile.writeRegionFile(outputregionfile, [x.toPolygon() for x in regions], overwrite = True)


    
    
    
    

########################


if __name__ == '__main__':

    cluster = sys.argv[1]
    filter  = sys.argv[2]

    clusterdir = '/nfs/slac/g/ki/ki05/anja/SUBARU/%s/' % cluster

    processCluster('%s/%s/SCIENCE/brightstars.reg' % (clusterdir, filter), 
                   '%s/%s/SCIENCE/coadd_%s_all/coadd.fits' % (clusterdir, filter, cluster),
                   '%s/PHOTOMETRY_%s_aper/%s.unstacked.cat' % (clusterdir, filter, cluster),
                   '%s/masks/InRing.%s.cat' % (clusterdir, filter),
                   '%s/masks/InRing.%s.reg' % (clusterdir, filter))
                   


        

    
