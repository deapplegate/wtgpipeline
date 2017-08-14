import pyfits, os, do_multiple_photoz, scipy, sys, string

import qc_wrapper

aptype = sys.argv[2]

#root_path = os.environ['subdir'] + '/COSMOS_PHOTOZ/' 

path = os.environ['subdir'] + '/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC' + aptype + '/'

catalog = path + '/cosmos30_matched.stars.calibrated.cat'
qc_wrapper.reformat(catalog)
offset_list = catalog + '.offsets.list' 
offset_list_reformat = offset_list + '.reformat'

photoz_offset_list = path + 'multiPHOTOZ.offsets.list'

print offset_list, 'offset_list'

''' calibrates cosmos30_matched.cat catalog in /COSMOS_PHOTOZ/ folder which should be a symbolic link '''
inputcat = path + 'cosmos30_matched.cat'

print inputcat

if sys.argv[1] == 'SLR':
    cats = [offset_list_reformat]
    outputcat = path + 'COSMOS_PHOTOZ.slr.cat'
elif sys.argv[1] == 'PHOTOZ':
    cats = [offset_list_reformat,photoz_offset_list]
    outputcat = path + 'COSMOS_PHOTOZ.sedzp.cat'

change_dict = {}
    
change_dict_dummy = {'SUBARU-10_2-1-W-J-B':-0.08,
'SUBARU-10_2-1-W-J-V':-0.06,
'SUBARU-10_2-1-W-S-R+':-0.04,
'SUBARU-10_2-1-W-S-I+':-0.02,
'SUBARU-10_2-1-W-S-Z+':-0.0
}

zp_dict = {}
for cat in cats:
    zps = open(cat,'r').readlines()
    for line in zps:
        import re
        res = re.split('\s+',line)
        filt = res[1]
        zp = float(res[2])

        ''' UPDATE zeropoint if present in both catalogs -- kind of like ZP table '''
        if zp_dict.has_key(filt): 
            zp_dict[filt] += zp
        else:
            zp_dict[filt] = zp

print zp_dict

''' add in zeropoints from catalog in path '''
if sys.argv[3] == 'True':
    from glob import glob
    if glob(path + '/test_offsets.zps'):
        f = open(path + '/test_offsets.zps','r').readlines()
        for l in f:
            import re
            res = re.split('\s+',l)
            change_dict[res[0]] = float(res[1])
        for key in change_dict:              
            zp_dict[key] += change_dict[key]


print sys.argv[3]
print zp_dict


p = pyfits.open(inputcat)

for o,n in [['u','MEGAPRIME-0-1-u'],['g','SUBARU-10_2-1-W-S-G+'],['B','SUBARU-10_2-1-W-J-B'],['V','SUBARU-10_2-1-W-J-V'],['r','SUBARU-10_2-1-W-S-R+'],['i','SUBARU-10_2-1-W-S-I+'],['z','SUBARU-10_2-1-W-S-Z+']]:
    for i in range(len(p['OBJECTS'].columns)):
        if p['OBJECTS'].columns[i].name == 'ID': p['OBJECTS'].columns[i].name = 'SeqNr'
        col = p['OBJECTS'].columns[i]
        if col.name == o or col.name == o + '_mag':
            p['OBJECTS'].columns[i].name = 'MAG_APER-' + n
        if col.name == 'd'+ o:
            p['OBJECTS'].columns[i].name = 'MAGERR_APER-' + n

for key in zp_dict:
    from copy import copy
    array = copy(scipy.array(p['OBJECTS'].data.field('MAG_APER-' + key)  ))
    print 'before ', array
    print 'applying ', zp_dict[key], ' correction to ', key
    value = array +  zp_dict[key]*scipy.ones(len(array))

    value[array==-99] = -99
    value[array==99] = 99
    print 'after ', value
    p['OBJECTS'].data['MAG_APER-' + key][:] = value
    #cols.append(pyfits.Column(name ))


    

hdu = pyfits.PrimaryHDU()
hduOBJECTS = pyfits.new_table(p['OBJECTS'].columns)

filterlist = do_multiple_photoz.get_filters(inputcat,'OBJECTS',SPECTRA='CWWSB_capak.list')

cols = [pyfits.Column(name='filter',format='60A',array=zp_dict.keys())]
cols += [pyfits.Column(name='zeropoints',format='E',array=scipy.array(zp_dict.values()))]
cols += [pyfits.Column(name='errors',format='E',array=scipy.zeros(len(filterlist)))]

hduZPS = pyfits.new_table(cols)

hdulist = pyfits.HDUList([hdu])
hdulist.append(hduOBJECTS)
hdulist.append(hduZPS)
hdulist[1].header.update('EXTNAME','OBJECTS')
hdulist[2].header.update('EXTNAME','ZPS')

os.system('rm ' + outputcat)
hdulist.writeto(outputcat)
print 'written to outputcat', outputcat
