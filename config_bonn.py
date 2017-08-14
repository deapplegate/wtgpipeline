#cluster = 'MACS0018+16'
cluster = 'MACS1423+24_nonillum'
#cluster = 'MACS1423+24'
#cluster = 'HDFN'
#cluster = 'MACS0018+16'
cluster = 'MACS1423+24'

path_root = '/nfs/slac/g/ki/ki05/anja/SUBARU/'

info = {'B':{'filter':'g','color1':'gmr','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0},\
    'W-J-B':{'filter':'g','color1':'gmr','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0},\
    'W-J-V':{'filter':'g','color1':'gmr','color2':'rmi','EXTCOEFF':-0.1202,'COLCOEFF':0.0},\
    'W-C-RC':{'filter':'r','color1':'rmi','color2':'gmr','EXTCOEFF':-0.0925,'COLCOEFF':0.0},\
    'W-C-IC':{'filter':'i','color1':'imz','color2':'rmi','EXTCOEFF':-0.02728,'COLCOEFF':0.0},\
    'W-S-I+':{'filter':'i','color1':'imz','color2':'rmi','EXTCOEFF':-0.02728,'COLCOEFF':0.0},\
    'I':{'filter':'i','color1':'imz','color2':'rmi','EXTCOEFF':-0.02728,'COLCOEFF':0.0},\
    'W-S-Z+':{'filter':'z','color1':'imz','color2':'rmi','EXTCOEFF':0.0,'COLCOEFF':0.0}}

#wavelength_order = ['U','W-S-U+','B','W-J-B','g','W-S-G+','W-J-V','V','r','W-S-R+','W-C-RC','R','W-S-I+','i','W-C-IC','W-S-Z+','z']

wavelength_groups = [['W-J-U','U','W-S-U+'],['B','W-J-B','g','W-S-G+'],['W-J-V','V'],['r','W-S-R+','W-C-RC','R'],['W-S-I+','i','W-C-IC'],['W-S-Z+','z']]

wavelength_order = reduce(lambda x,y: x + y,wavelength_groups)

#chip_groups = {'8':{'1':[1,5],'2':[2,6],'3':[3,4,7,8]},'9':{'1':[2,7],'2':[3,4,8,9],'3':[5,10],'4':[6]}}

chip_groups = {'8':{'2':[2,6],'3':[3,4,7,8]},'9':{'1':[2,7],'2':[3,4,8,9]}}

chip_divide_10_3 = {'1':[0,496],'2':[496,1008],'3':[1008,1520],'4':[1520,2016]}

#if cluster == '0911':
#    cluster = 'MACS0911+17'
#    tag = 'local50'
#    arc = ''
#    filters = ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']
#    magnitude = 'MAG_APER1'
#    spectra = '/tmp/0911.cat'

if cluster == 'MACS0018+16':
    appendix = ''
    appendix_root = appendix
    tag = 'local50'
    filters = ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']
    filter_root = 'W-J-V'
    magnitude = 'MAG_APER2'
    magnitude_err = 'MAGERR_APER2'
    #magnitude = 'MAG_ISO'
    #magnitude_err = 'MAGERR_ISO'
    spectra = '0018.cat' # 'spec.cat' #
    arc = '' #.arc'
    area = int(3.14 * 10.**2.) * 0.2**2. # area in arcseconds

if cluster == 'MACS1423+24_nonillum' or cluster == 'MACS1423+24':
    appendix = '_all'
    appendix_root = appendix
    tag = 'local50'
    filters = ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']
    filter_root = 'W-J-V'
    magnitude = 'MAG_AUTO'
    magnitude_err = 'MAGERR_AUTO'
    #magnitude = 'MAG_AUTO'
    #magnitude_err = 'MAGERR_AUTO'
    spectra = '/tmp/1423.cat' # 'spec.cat' #
    arc = '' #.arc'
    area = int(3.14 * 10.**2.) * 0.2**2. # area in arcseconds

if cluster == 'MACS0417-11':
    appendix = '_all'
    appendix_root = appendix
    tag = 'local50'
    filters = ['W-J-V','W-C-RC','W-C-IC']
    filter_root = 'W-C-RC'
    magnitude = 'MAG_APER2'
    magnitude_err = 'MAGERR_APER2'
    spectra = 'M2243_spectra.cat' # 'spec.cat' #
    arc = '' #.arc'
    area = int(3.14 * 10.**2.) * 0.2**2. # area in arcseconds

if cluster == 'FIELDB':
    appendix = ''
    appendix_root = appendix
    tag = 'local50'
    filters = ['W-C-RC']
    filter_root = 'W-C-RC'
    magnitude = 'MAG_APER2'
    magnitude_err = 'MAGERR_APER2'
    spectra = 'M2243_spectra.cat' # 'spec.cat' #
    arc = '' #.arc'
    area = int(3.14 * 10.**2.) * 0.2**2. # area in arcseconds

if cluster == 'MACS0018+16':
    appendix = ''
    appendix_root = appendix
    tag = 'local50'
    filters = ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']
    filter_root = 'W-J-V'
    magnitude = 'MAG_APER2'
    magnitude_err = 'MAGERR_APER2'
    #magnitude = 'MAG_ISO'
    #magnitude_err = 'MAGERR_ISO'
    spectra = '0018.cat' # 'spec.cat' #
    arc = '' #.arc'
    area = int(3.14 * 10.**2.) * 0.2**2. # area in arcseconds

if cluster == 'MACS0417-11':
    appendix = '_all'
    appendix_root = appendix
    tag = 'local50'
    filters = ['W-J-V','W-C-RC','W-C-IC']
    filter_root = 'W-C-RC'
    magnitude = 'MAG_APER2'
    magnitude_err = 'MAGERR_APER2'
    spectra = 'M2243_spectra.cat' # 'spec.cat' #
    arc = '' #.arc'
    area = int(3.14 * 10.**2.) * 0.2**2. # area in arcseconds

if cluster == 'MACS1423+24':
    appendix = '_all'
    appendix_root = appendix
    tag = 'local50'
    filters = ['W-C-RC', 'W-J-B','W-J-V','W-C-IC','W-S-Z+']
    filter_root = 'W-C-RC'
    magnitude = 'MAG_APER2'
    magnitude_err = 'MAGERR_APER2'
    spectra = 'M2243_spectra.cat' # 'spec.cat' #
    arc = '' #.arc'
    area = int(3.14 * 10.**2.) * 0.2**2. # area in arcseconds

if cluster == 'FIELDB':
    appendix = ''
    appendix_root = appendix
    tag = 'local50'
    filters = ['W-C-RC']
    filter_root = 'W-C-RC'
    magnitude = 'MAG_APER2'
    magnitude_err = 'MAGERR_APER2'
    spectra = 'M2243_spectra.cat' # 'spec.cat' #
    arc = '' #.arc'
    area = int(3.14 * 10.**2.) * 0.2**2. # area in arcseconds

if cluster == 'HDFN':
    appendix = '_all'
    appendix_root = appendix
    cluster = 'HDFN'
    tag = 'local50'
    filters = ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']
    filter_root = 'W-C-RC'
    magnitude = 'MAG_APER2'
    magnitude_err = 'MAGERR_APER2'
    spectra = 'M2243_spectra.cat' # 'spec.cat' #
    arc = '' #.arc'
    area = int(3.14 * 10.**2.) * 0.2**2. # area in arcseconds

if cluster == '2219':
    appendix = ''
    cluster = 'A2219'
    tag = 'local50'
    filters = ['W-J-B','W-J-V','W-C-RC','I']
    filter_root = 'W-J-V'
    appendix_root = '_all'
    magnitude = 'MAG_APER2'
    magnitude_err = 'MAGERR_APER2'
    spectra = '' # 'spec.cat' #
    arc = '' #.arc'
    area = int(3.14 * 10.**2.) * 0.2**2. # area in arcseconds

if cluster == '2243':
    appendix = '_all'
    cluster = 'MACS2243-09'
    tag = 'local50'
    filters = ['B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']
    filter_root = 'W-J-V'
    magnitude = 'MAG_APER1'
    magnitude_err = 'MAGERR_APER1'
    spectra = 'M2243_spectra.cat' # 'spec.cat' #
    arc = '' #.arc'
    area = int(3.14 * 10.**2.) * 0.2**2. # area in arcseconds

if cluster == '0911':
    #appendix = ''
    cluster = 'MACS0911+17'
    tag = 'local50true'
    filters = ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']
    filter_root = 'W-J-V'
    magnitude = 'MAG_APER2'
    magnitude_err = 'MAGERR_APER2'
    spectra = '/tmp/0911.cat' # 'spec.cat' #
    arc = '' #.arc'
    area = int(3.14 * 10.**2.) * 0.2**2. # area in arcseconds
    appendix = '_all'
    appendix_root = appendix

path = path_root + cluster + '/'

