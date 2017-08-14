#!/usr/bin/env python

import astropy, astropy.io.fits as pyfits, sys, numpy as np
import regionfile as rf
#The matplotlib.nxutils module has been removed. Use the functionality on matplotlib.path.Path.contains_point
#from matplotlib.nxutils import points_inside_poly
from matplotlib.path import Path


def makeEdgemask(inputfile, outputfile, regionfile=0):

    input = pyfits.open(inputfile)[0].data

    output = np.zeros_like(input)

    badPixel = 16
    maskedPixel = 1

    masksize=8

    xsize=input.shape[0]
    ysize=input.shape[1]

    megagrid = badPixel*np.ones((xsize + 2*masksize, ysize + 2*masksize))
    megagrid[masksize:masksize+xsize, masksize:masksize+ysize] = input
    megagrid[megagrid != badPixel] = 0
    megagrid[megagrid == badPixel] = 1

    transfergrid = np.copy(megagrid)

    for i in xrange(masksize):
        megagrid[:,:] = megagrid[:,:] + np.roll(transfergrid, i, axis=1)

    megagrid[:,:] = megagrid[:,:] + np.roll(megagrid, -masksize, axis=1)

    transfergrid = np.copy(megagrid)

    for i in xrange(masksize):
        megagrid[:,:] = megagrid[:,:] + np.roll(transfergrid, i, axis=0)

    megagrid[:,:] = megagrid[:,:] + np.roll(megagrid, -masksize, axis=0)

    output = megagrid[masksize:masksize+xsize, masksize:masksize+ysize]
    output[output > 1] = 1


    
    if regionfile != 0:        

        regfile=open(regionfile)
        regions=rf.parseRegionFile(regfile.readlines())

        regionmask=make_mask_from_reg(regions,output.shape[0],output.shape[1])
        output = np.logical_or(output , regionmask)*1.
        
    

    hdu = pyfits.PrimaryHDU(output)
    hdu.writeto(outputfile, clobber=True)

######################

def make_mask_from_reg(regions,xsize,ysize):
    x, y = np.meshgrid(np.arange(xsize), np.arange(ysize))
    x, y = x.flatten(), y.flatten()
    points = np.vstack((x,y)).T

    outarr = np.zeros((ysize,xsize))
    
    for region in regions:
        vertlist = region.vertices
        paired_vertlist=[]
        for ipair in range(0,len(vertlist),2):
            paired_vertlist.append([vertlist[ipair],vertlist[ipair+1]])
        grid = points_inside_poly(points, paired_vertlist)
        grid = grid.reshape((ysize,xsize))*1
        outarr = outarr+grid

    return outarr
    # as is True -> inside.
    

######################

    
if __name__ == '__main__':

    inputfile = sys.argv[1]
    outputfile = sys.argv[2]

    makeEdgemask(inputfile, outputfile)

