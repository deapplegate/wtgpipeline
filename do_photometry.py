
import make_lephare_cats
import do_multiple_photoz
import os, re, sys, string

subarudir = os.environ['subdir']
cluster = sys.argv[1] #'MACS1423+24'
spec = False 
train_first = False 
magtype = 'APER1'
AP_TYPE = ''
type = 'all' 
SPECTRA='CWWSB_capak.list'

#SPECTRA='CWWSB4.list'
test_zps = False
short = False
only_type=False

#SPECTRA='ZEBRA.list'

#SPECTRA='CWWSB4_txitxo.list'
FILTER_WITH_LIST=None
if len(sys.argv) > 2:
    for s in sys.argv:
        if s == 'spec':
            type = 'spec'            
            spec = True
        if s == 'rand':
            type = 'rand'
        if s == 'train':
            train_first = True
        if s == 'ISO':
            magtype = 'ISO'
        if s == 'APER1':
            magtype = 'APER1'
        if s == 'short':
            short = True
        if s == 'APER':
            magtype = 'APER'

        if s == 'only_type':
            only_type=True

        if string.find(s,'flist') != -1:
            import re
            rs = re.split('=',s)
            FILTER_WITH_LIST=rs[1]

        if s == 'zp':
            test_zps = True

        if string.find(s,'detect') != -1:
            import re
            rs = re.split('=',s)
            DETECT_FILTER=rs[1]
        if string.find(s,'spectra') != -1:
            import re
            rs = re.split('=',s)
            SPECTRA=rs[1]
        if string.find(s,'aptype') != -1:
            import re
            rs = re.split('=',s)
            AP_TYPE = '_' + rs[1]

photdir = subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + AP_TYPE + '/'

if spec:
    from glob import glob
    if not glob(subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + '/' + cluster + 'spec.cat'):
        command = 'cp ' + subarudir + '/' + cluster + '/PHOTOMETRY/' + cluster + 'spec.cat ' + subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + '/' + cluster + 'spec.cat'
        os.system(command)

''' photoz parameters '''
calib_type = 'slr'
use_spec = False
picks = None #[11757]

print type, 'type'

inputcat = photdir + cluster + '.slr.cat'

inputcat_alter = photdir + cluster + '.slr.alter.cat'

inputcat_sed = photdir + cluster + '.sedzp.cat'
inputcat_sed_alter = photdir + cluster + '.sedzp.alter.cat'

inputcat_zlist = None
if short: 
    inputcat_zlist = photdir + cluster + '.short.zs'
    inputcat = photdir + cluster + '.short.cat'
    inputcat_alter = photdir + cluster + '.short.alter.cat'

print inputcat_alter

import do_multiple_photoz
reload(do_multiple_photoz)

#[23026 24752 29126 13149 24325]


#SPECTRA = 'CWWSB_capak_uz.list' # use Peter Capak's SEDs
#SPECTRA = 'CWWSB_capak_ub.list' # use Peter Capak's SEDs
#SPECTRA = 'CWWSB_capak_u.list' # use Peter Capak's SEDs
#SPECTRA = 'CWWSB_capak.list' # use Peter Capak's SEDs
#SPECTRA = 'CWWSB4_txitxo.list' # use Peter Capak's SEDs

print SPECTRA

import calc_test_save

if not short:
    calc_test_save.photocalibrate(cluster,'SLR',AP_TYPE,test_zps)

print inputcat,
# python do_photometry.py COSMOS_PHOTOZ detect=W-C-IC aptype=APER train APER
if cluster == 'COSMOS_PHOTOZ':
    #filterlist = ['MEGAPRIME-0-1-u','SUBARU-10_2-1-W-J-B','SUBARU-10_2-1-W-J-V','SUBARU-10_2-1-W-S-G+','SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-S-I+','SUBARU-10_2-1-W-S-Z+']

    if True:
        do_multiple_photoz.add_dummy_filters(inputcat,inputcat_alter)                   
        inputcat = inputcat_alter
        print inputcat
        filterlist = do_multiple_photoz.get_filters(inputcat,'OBJECTS',SPECTRA=SPECTRA)


        print filterlist

    else: 
        filterlist = ['MEGAPRIME-0-1-u','SUBARU-10_2-1-W-J-B','SUBARU-10_2-1-W-J-V','SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-S-I+','SUBARU-10_2-1-W-S-Z+']


    
        #if AP_TYPE == '_UGRIZ':                                                                                                             
        #    filterlist = ['MEGAPRIME-0-1-u','SUBARU-10_2-1-W-S-G+','SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-S-I+','SUBARU-10_2-1-W-S-Z+']
        #elif AP_TYPE == '_BVRIZ': 
        #    filterlist = ['SUBARU-10_2-1-W-J-B','SUBARU-10_2-1-W-J-V','SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-S-I+','SUBARU-10_2-1-W-S-Z+']
        #elif AP_TYPE == '_GRIZ':
        #    filterlist = ['SUBARU-10_2-1-W-S-G+','SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-S-I+','SUBARU-10_2-1-W-S-Z+']
        #elif AP_TYPE[:6] == '_BVRIZ': 
        #    filterlist = ['SUBARU-10_2-1-W-J-B','SUBARU-10_2-1-W-J-V','SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-S-I+','SUBARU-10_2-1-W-S-Z+']
        #elif AP_TYPE == '_BVRI': 
        #    filterlist = ['SUBARU-10_2-1-W-J-B','SUBARU-10_2-1-W-J-V','SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-S-I+']
        #elif AP_TYPE == '_VRIZ': 
        #    filterlist = ['SUBARU-10_2-1-W-J-V','SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-S-I+','SUBARU-10_2-1-W-S-Z+']
        #elif AP_TYPE == '_RIZ': 
        #    filterlist = ['SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-S-I+','SUBARU-10_2-1-W-S-Z+']
        #elif AP_TYPE == '_BVR': 
        #    filterlist = ['SUBARU-10_2-1-W-J-B','SUBARU-10_2-1-W-J-V','SUBARU-10_2-1-W-S-R+']
        #elif AP_TYPE == '_VRI': 
        #    filterlist = ['SUBARU-10_2-1-W-J-V','SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-S-I+']
        #elif AP_TYPE == '_BRZ': 
        #    filterlist = ['SUBARU-10_2-1-W-J-B','SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-S-Z+']


    ID = 'PatID'
    magflux = 'MAG'
    print filterlist

else:    
    ''' add new Subaru W-S-I+ filter '''
    do_multiple_photoz.add_dummy_ifilter(inputcat,inputcat_alter)                   
    filterlist = do_multiple_photoz.get_filters(inputcat_alter,'OBJECTS',SPECTRA=SPECTRA)
    print filterlist


    ID = 'PatID'        
    magflux = 'FLUX'


print filterlist, 'filterlist'    

if FILTER_WITH_LIST:
    import pyfits
    p = pyfits.open(inputcat_alter)['OBJECTS'].data
    s = pyfits.open(FILTER_WITH_LIST)['OBJECTS'].data
    indices = s.field('SeqNr')
    for index in indices:
        p.field('CLASS_STAR')[index-1] = -999

    mask = p.field('CLASS_STAR') == -999
    p_orig = pyfits.open(inputcat_alter)['OBJECTS']

    cols = []
    for column in p_orig.columns:    
        cols.append(pyfits.Column(name=column.name, format = column.format, array = p_orig.data.field(column.name)[mask]))

    hdu = pyfits.PrimaryHDU()
    hduSTDTAB = pyfits.new_table(cols) 
    hdulist = pyfits.HDUList([hdu])
    hdulist.append(hduSTDTAB)
    hdulist[1].header.update('EXTNAME','OBJECTS')
    import os
    os.system('rm ' + inputcat_alter)
    hdulist.writeto(inputcat_alter)
    os.system('cp ' + inputcat_alter + ' ' + inputcat)
    print inputcat, inputcat_alter



print filterlist, len(filterlist)

speccat = photdir + cluster + 'spec.cat'
from glob import glob
if not glob(speccat):
    os.system('cp ' +  subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + '/' + cluster + 'spec.cat ' + speccat)


outspeccat = photdir + 'spec.' + magtype + '.' + AP_TYPE+ '.' + SPECTRA + '.cat'
outfullcat = photdir + 'all.' + magtype + SPECTRA + '.cat'

''' retrieve SDSS spectra '''

''' make spectra file '''

''' make the catalogs '''
print filterlist

print inputcat
print SPECTRA 
print train_first, type
print magflux

filterlist_short = filter(lambda x: string.find(x,'10_2-2') == -1 and string.find(x,'10_1-2') == -1, filterlist)

print filterlist_short

''' TRAINING ONLY ON u-band '''
train_filters = ['WHT-0-1-U','MEGAPRIME-10_2-1-u','MEGAPRIME-0-1-u','SUBARU-10_2-1-W-J-U','SUBARU-10_1-1-W-J-U']
train_filters += ['SUBARU-10_1-1-W-J-B','SUBARU-10_2-1-W-J-B','SUBARU-9-4-W-J-B','SUBARU-9-2-W-J-B']

overlap = False
for filt1 in filterlist:
    for filt2 in train_filters:
        if filt1==filt2: overlap = True


if not short and overlap and train_first and len(filterlist_short)>=5:

    ''' first derive correction '''

    print train_filters

    #if len(filterlist) >= 4: train_filters += ['SUBARU-10_1-1-W-J-B','SUBARU-10_2-1-W-J-B']

    print magtype

    print filterlist

        
    #import flux_comp
    #correction_dict = flux_comp.calc_comp(cluster,DETECT_FILTER,AP_TYPE,SPECTRA,magtype=magtype, type='rand',verbose=True)
    #print correction_dict                                                                                                                                                                                                    
    #raw_input()


    
    if not short: 
        make_lephare_cats.doit(cluster,DETECT_FILTER,filterlist,inputcat_alter,speccat,outspeccat,outfullcat,False,'','',magtype,train_filters=train_filters,randsample=True,magflux=magflux)  
        print outfullcat, 'outfullcat'
        do_multiple_photoz.do_it(cluster,DETECT_FILTER,AP_TYPE,filterlist,inputcat_alter,calib_type,False,use_spec,SPECTRA, picks,magtype=magtype,magflux=magflux,randsample=True,ID=ID,only_type=only_type)
        import flux_comp
        correction_dict = flux_comp.calc_comp(cluster,DETECT_FILTER,AP_TYPE,SPECTRA,magtype=magtype, type='rand',verbose=True)
        print correction_dict                                                                                                                                                                                                    
        print 'finished'

        ''' measure photoz's '''
        offset_list = photdir + '/multiPHOTOZ.offsets.list'
        ''' record all ZPs and numbers of stars '''
        offset_list_file = open(offset_list,'w')
        updated_zeropoints = 0
        for key in correction_dict.keys():    
            if key in train_filters:
                updated_zeropoints += 1                
                offset_list_file.write('DUMMY ' + key + ' ' + str(correction_dict[key]) + ' ' + str(0) + ' 0\n')              
        offset_list_file.close()
                                                                                                                                                                                                                                 
        if magtype == 'APER1': aptype='aper'
        elif magtype == 'ISO': aptype='iso'
                                                                                                                                                                                                                                 
        if not cluster == 'COSMOS_PHOTOZ' and updated_zeropoints > 0:
            save_slr_flag = photocalibrate_cat_flag = '--spec mode=' + magtype
            print 'running save_slr'
            command = os.environ['bonn'] + '/save_slr.py -c %(cluster)s -i %(catalog)s -o %(offset_list)s %(save_slr_flag)s' % {'cluster':cluster, 'catalog':inputcat, 'offset_list':offset_list, 'save_slr_flag':save_slr_flag}
            print command
            os.system(command)
        
        os.system('rm ' + inputcat_sed)                                                                                                                                                                                                                               
        os.system('rm ' + inputcat_sed_alter)
        import calc_test_save
        calc_test_save.photocalibrate(cluster,'PHOTOZ',AP_TYPE)
                                                                                                                                                                                                                                 
    print 'calibrated'
        
    if cluster == 'COSMOS_PHOTOZ':
        do_multiple_photoz.add_dummy_filters(inputcat_sed,inputcat_sed_alter)                   
    else:
        do_multiple_photoz.add_dummy_ifilter(inputcat_sed,inputcat_sed_alter)                   

    #spec = True
    #print cluster,DETECT_FILTER,filterlist,inputcat_sed_alter,speccat,outspeccat,outfullcat,spec,'','',magtype,correction_dict,train_filters,

    print inputcat_sed_alter
    make_lephare_cats.doit(cluster,DETECT_FILTER,filterlist,inputcat_sed_alter,speccat,outspeccat,outfullcat,spec,'','',magtype,randsample=False,magflux=magflux)
    #print correction_dict, picks
    do_multiple_photoz.do_it(cluster,DETECT_FILTER, AP_TYPE, filterlist,inputcat_sed_alter,calib_type,spec,use_spec,SPECTRA, picks,magtype=magtype,magflux=magflux,randsample=False,short=short,ID=ID,only_type=only_type)

else: 
    print filterlist
    make_lephare_cats.doit(cluster,DETECT_FILTER,filterlist, inputcat_alter,speccat,outspeccat,outfullcat,spec,'','',magtype=magtype,randsample=False,magflux=magflux,inputcat_zlist=inputcat_zlist)

    #picks = [1285]
    do_multiple_photoz.do_it(cluster,DETECT_FILTER, AP_TYPE, filterlist,inputcat_alter, calib_type,spec,use_spec,SPECTRA, picks,magtype=magtype,randsample=False,magflux=magflux,short=short,ID=ID,only_type=only_type)

#import cutout_bpz        
#cutout_bpz.run(cluster)
#os.system('python cutout_bpz.py ' + cluster + ' spec')

''' now make the cutout images '''
''' python cutout_bpz.py '''





