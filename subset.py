import astropy, astropy.io.fits as pyfits, os, scipy

cluster = 'MACS0454-03'
detect_filt = 'r'


cluster = 'MACS2243-09'
detect_filt = 'W-J-V'


import calc_test_save

test_zps = False
AP_TYPE='_aper'
#calc_test_save.photocalibrate(cluster,'SLR',AP_TYPE,test_zps)

''' run on subset of SeqNrs '''                                                      
file_matched = os.environ['subdir'] + '/' + cluster + '/PHOTOMETRY_' + detect_filt + '_aper/' + cluster + '.matched.tab'

print file_matched
p = pyfits.open(file_matched)
SeqNr = p[1].data.field('SeqNr_data')
z_spec = p[1].data.field('z_spec')
#NFILT = p[1].data.field('NFILT_data')

if False:
    file_to_use = '/nfs/slac/g/ki/ki05/anja/SUBARU/A383/LENSING_W-S-I+_W-S-I+_aper/good/A383_redsequence.cat'
    p = pyfits.open(file_to_use)
    SeqNr = p['OBJECTS'].data.field('SeqNr')

file_sed = os.environ['subdir'] + '/' + cluster + '/PHOTOMETRY_' + detect_filt + '_aper/' + cluster + '.slr.cat'
table = pyfits.open(file_sed)
                                                                                     
zs = scipy.zeros(len(table[1].data.field('SeqNr')),dtype=float)
mask = scipy.zeros(len(table[1].data.field('SeqNr')),dtype=bool)
index = 0
for i in range(len(SeqNr)):
    if z_spec[i] < 1.2: # and NFILT[i] >= 5:
        mask[SeqNr[i]==table[1].data.field('SeqNr')] = True 
        zs[SeqNr[i]==table[1].data.field('SeqNr')] = z_spec[i] 
    if index % 100 == 0: print index        
    index += 1
                                                                                     
print mask[:10000]
                                                                                      
table[1].data = table[1].data[mask]

''' ADJUST B-BAND MAGS!!!! '''
#factor = 1. #10.**(0.2/-2.5)
#bad = table[1].data.field('FLUX_APER1-SUBARU-10_2-1-W-J-B')[:] == -99
#table[1].data.field('FLUX_APER1-SUBARU-10_2-1-W-J-B')[:] = factor * table[1].data.field('FLUX_APER1-SUBARU-10_2-1-W-J-B')[:]
#table[1].data.field('FLUX_APER1-SUBARU-10_2-1-W-J-B')[bad] = -99

#table[1].data.field('FLUX_APER1-SUBARU-10_2-1-W-J-V')[:] = 1 # * table[1].data.field('MAG_APER1-SUBARU-10_2-1-W-J-B')[:]

#table[1].data.field('FLUX_APER1-SUBARU-10_2-1-W-C-RC')[:] =  table[1].data.field('MAG_APER1-SUBARU-10_2-1-W-J-B')[:]
                                                                                      
print len(table[1].data), 'table length'

file_short = os.environ['subdir'] + '/' + cluster + '/PHOTOMETRY_' + detect_filt + '_aper/' + cluster + '.short.cat'
import os
os.system('rm ' + file_short)
table.writeto(file_short)

zs_mask = zs[mask]
file = os.environ['subdir'] + '/' + cluster + '/PHOTOMETRY_' + detect_filt + '_aper/' + cluster + '.short.zs'
fw = open(file,'w')
for l in zs_mask:
    fw.write('%.3f\n' % l)
fw.close()

print z_spec, SeqNr
    
    



