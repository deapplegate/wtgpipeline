
import pickle
f = open('maglocus_SYNTH','r')
m = pickle.Unpickler(f)
locus_mags = m.load()

import astropy.io.fits as pyfits

dict = {'VJOHN':'MAG_APER1-SUBARU-10_2-1-W-J-V',
    'BJOHN':'MAG_APER1-SUBARU-10_2-1-W-J-B',
    'RJOHN':'MAG_APER1-SUBARU-10_2-1-W-C-RC',
    'IJOHN':'MAG_APER1-SUBARU-10_2-1-W-C-IC',
    'WSZSUBARU':'MAG_APER1-SUBARU-10_2-1-W-S-Z+', 
    'WSISUBARU':'MAG_APER1-SUBARU-10_2-1-W-S-I+',
    'MPUSUBARU':'MAG_APER1-MEGAPRIME-10_2-1-u',
    'MPGSUBARU':'MAG_APER1-MEGAPRIME-10_2-1-g',
    'MPRSUBARU':'MAG_APER1-MEGAPRIME-10_2-1-r',
    'MPISUBARU':'MAG_APER1-MEGAPRIME-10_2-1-i',
    'MPZSUBARU':'MAG_APER1-MEGAPRIME-10_2-1-z'}

import random
arrays =  {}
for key in dict.keys(): 
    arrays[key] = []

zps ={} 
for key in dict.keys():
    zps[key] = random.gauss(0,0.1)


for l in locus_mags:
    import random

    print l


    for key in dict.keys():

        err = random.gauss(0,0.04) 

        if random.random() > 0.95: err = 0.5 

        #print err
        arrays[key].append(l[key] + err + zps[key])
    

print arrays
import scipy, astropy.io.fits as pyfits

cols = []
for key in dict.keys():
    cols.append(pyfits.Column(name=dict[key], format='E', array=scipy.array(arrays[key])))
    cols.append(pyfits.Column(name=dict[key].replace('MAG','MAGERR'), format='E', array=0.05*scipy.ones(len(arrays[key]))))

cols.append(pyfits.Column(name='ALPHA_J2000', format='E', array=scipy.array(arrays[key])))
cols.append(pyfits.Column(name='DELTA_J2000', format='E', array=scipy.array(arrays[key])))

hdu = pyfits.PrimaryHDU()
hduOBJECTS = pyfits.BinTableHDU.from_columns(cols)
hduOBJECTS.header['EXTNAME']='OBJECTS'
hdulist = pyfits.HDUList([hdu])
hdulist.append(hduOBJECTS)

import os
file = os.environ['subdir'] + '/TEST/PHOTOMETRY_W-J-V_aper/TEST.stars.calibrated.cat'
import os
os.system('rm ' + file)
hdulist.writeto(file)


