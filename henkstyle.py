######################
# Implement a Henk Style color cut analysis 
#  from Anja's simulated ata
#######################

import numpy as np, astropy.io.fits as pyfits
from dappleutils import readtxtfile
import ldac, shearprofile as sp


def convertTxt2LDAC(file, keys, type):

    rawfile = readtxtfile(file)

    cols = []
    for i, key, type in zip(xrange(len(keys)), keys, type):

        cols.append(pyfits.Column(name = key, format = type, array = rawfile[:,i]))

    hdu = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
    hdu.header['EXTNAME']= 'OBJECTS'

    return ldac.LDACCat(hdu)
    


def convertSIMCatalog(catfile):

    keys = 'myID x y g1 g2 sigma2 hdfnID B R'.split()
    type = 'J E E E E E J E E'.split()

    return convertTxt2LDAC(catfile, keys, type)


def convertHDFNPhotoz(file):

    keys = 'ID Z_B Z_B_MIN Z_B_MAX T_B ODDS Z_ML T_ML CHI-SQUARED Z_S M_0'.split()
    type = 'J E E E E E E E E E E'.split()

    return convertTxt2LDAC(file, keys, type)


def convertHDFNPhotometry(file):

    keys = 'ID z U B V R I Z F435W F606W F775W F850LP J H HK K m3.6 m4.5 m5.8 m8 dU dB dV dR dI dZ dF435W dF606W dF775W dF850LP dJ dH dHK dK dm3.6 dm4.5 dm5.8 dm8'.split()
    type = ['J'] + (len(keys)-1)*['E']

    return convertTxt2LDAC(file, keys, type)

def convertNFWTestCat(file):

    keys = 'id x y g2 g1 sigma2'.split()
    type = ['J'] + 5*['E']

    return convertTxt2LDAC(file, keys, type)


def analysisCuts(cat, center = (0,0)):

    r = np.sqrt( (cat['x'] - center[0])**2 + (cat['y'] - center[1])**2 )
    rcut = np.logical_and(100 < r, r < 4063)

    photCuts = photometryCuts(cat['B'], cat['R'])

    return np.logical_and(rcut, photCuts)


def photometryCuts(V, R):

    magcut = np.logical_and(R > 19, R < 24.5)
    
    color = V - R

    colorcut = np.logical_or(color > (-0.0717*R + 2.675 + 0.15),
                             color < (-0.0717*R + 2.675 - 0.3))


    return np.logical_and(magcut, colorcut)


ri2R = lambda r, i : r - 0.2936*(r - i) - 0.1439

def photometryCutsZ018(V,R):

    magcut = np.logical_and(R > 19, R < 24.5)

    color = V-R

    colorcut = np.logical_or(color > (-0.0234*R + 0.969 + 0.15),
                             color < (-0.0234*R + 0.969 - 0.3))

    return np.logical_and(magcut, colorcut)


#def bootstrapAnalysis(simcat, betas, bins=21, range=(100, 4100), nbootstraps = 100):
#
#    rss = []
#    masses = []
#    nfails = 0
#    for i in xrange(nbootstraps):
#
#        anacat = simcat.filter(np.random.randint(0, len(simcat), len(simcat)))
#
#        curBetas = betas[np.random.randint(0, len(betas), len(betas))]
#
#        beta_s = np.mean(curBetas)
#        beta_s2 = np.mean(curBetas**2)
#
#        profile = sp.shearprofile(anacat['x'], anacat['y'], anacat['g1'], anacat['g2'], 
#                                  None, range, bins = bins, center=(0,0), logbin=True)
#
#        
#        r_mpc = profile.r * 0.2*6.136/1000  #pixels to mpc
#
#        okBin = np.logical_and(np.isfinite(profile.E), np.isfinite(profile.Eerr))
#        
#        rs = sp.runNFW_ML(r_mpc[okBin], profile.E[okBin], profile.Eerr[okBin], beta_s, beta_s2,
#                          0.505, guess=0.4)
#
#        if rs is None:
#            nfails += 1
#            continue
#
#        rss.append(rs)
#        
#        masses.append(sp.AdamMass(4, rs, 1, 0.505))
#
#    return rss, masses, nfails
