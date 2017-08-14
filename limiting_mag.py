###########################
# Function to calculate detection limit based on background sigma and measured zeropoint
#############################

import numpy as np
import scipy.optimize as optimize
import photometry_db as pdb

#############################


def findMinCounts(sigb, sigma=5, npix = 0.25*np.pi*(3./0.2)**2):

    def limiteq(s):
#        return s**2 - sigma*s - sigma*npix*sigb**2
        return s**2  - sigma*npix*sigb**2

    return optimize.brentq(limiteq, 0, 50)

db = pdb.Photometry_db()

def convertCounts2Mag(cluster, filter, counts):

    zp = db.getZeropoint(cluster, filter, mode = 'APER1')

    if zp is None:
        return -1

    return -2.5*np.log10(counts) + zp.zp

