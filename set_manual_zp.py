#!/usr/bin/env python
#####################

# Manually set a zeropoint for a fitid, such as from SLR

#####################

import sys
import photometry_db
photometry_db.initConnection()

######################

def setManualZP(cluster, fitID, zp):

    manualZP = photometry_db.registerManualZP(cluster, fitID, zp)

    photometry_db.updateCalibration(cluster, fitID, 'manual_z_p', manualZP.id)

#######################

def main(argv = sys.argv):

    cluster = argv[1]
    fitId = argv[2]
    zp = float(argv[3])

    setManualZP(cluster, fitId, zp)

#######################

if __name__ == '__main__':

    main()
