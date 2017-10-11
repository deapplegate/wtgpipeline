import astropy, astropy.io.fits as pyfits

C = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_aper/cosmos_lephare.cat')['OBJECTS'].data
U = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_aper/COSMOS_PHOTOZ.APER.1.CWWSB_capak.list.all.bpz.tab')['STDTAB'].data

U = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_aper/COSMOS_PHOTOZ.APER.1.CWWSB_txitxo.list.all.bpz.tab')['STDTAB'].data

CZ = []
UZ = []
for i in range(80000):
    #print U.field('BPZ_Z_B')[i], U.field('SeqNr')[i], C.field('ID')[i+1], C.field('zp_best')[i+1]
    if U.field('BPZ_ODDS')[i] > 0.9:
        CZ.append(C.field('zp_best')[i])
        UZ.append(U.field('BPZ_Z_B')[i])

import pylab
pylab.scatter(CZ,UZ,s=0.01)
pylab.plot([0,5],[0,5],color='red')
pylab.xlim([0,4.])
pylab.ylim([0,4.])
pylab.ylabel('US',fontsize='x-large')
pylab.xlabel('THEM (COSMOS)',fontsize='x-large')
pylab.savefig('usvscosmos04.png')

pylab.clf()
pylab.scatter(CZ,UZ,s=0.01)
pylab.plot([0,5],[0,5],color='red')
pylab.xlim([0,2.])
pylab.ylim([0,2.])
pylab.ylabel('US',fontsize='x-large')
pylab.xlabel('THEM (COSMOS)',fontsize='x-large')
pylab.savefig('usvscosmos02.png')

pylab.show()




