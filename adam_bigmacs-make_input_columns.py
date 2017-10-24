#! /usr/bin/env python
#adam-use# Use this to make the cluster.sdss.columns file and the ${cluster}.qc.columns file needed to run bigmacs/fit_locus.py (this itself doesn't run fit_locus.py or save_slr.py)
#adam-example# python adam_bigmacs-make_input_columns.py $cluster detect=W-C-RC aptype=aper
import sys
sys.path.append('/u/ki/awright/wtgpipeline/')
import astropy, astropy.io.fits as pyfits, os, string, random, re,subprocess
import MySQLdb
import do_multiple_photoz

def all(subarudir,cluster,DETECT_FILTER,aptype,magtype,location=None,faintSDSS=False,brightSDSS=False):
    print ' magtype=',magtype
    save_slr_flag = photocalibrate_cat_flag = '--spec mode=' + magtype.replace('1','').replace('APER','aper').replace('2','')
    catalog_dir = subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + aptype + '/'
    catalog_dir_iso = subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + '_iso/'
    #catalog_dir = '/'.join(catalog.split('/')[:-1])
    catalog = catalog_dir + '/' + cluster + '.stars.cat'
    filterlist_all = do_multiple_photoz.get_filters(catalog,'OBJECTS')
    filterlist = []
    for filt in filterlist_all:
        if string.find(filt,'-2') == -1 and string.find(filt,'u') == -1 and string.find(filt,'-U') == -1:
            filterlist.append(filt)

    columns = catalog_dir + '/' + cluster + '.qc.columns'
    columnsSDSS = catalog_dir + '/' + cluster + '.sdss.columns'
    columnsSDSSFile = open(columnsSDSS,'w')
    columnsSDSSFile.write('psfPogCorr_g psfPogErr_g SDSS-g.res VARY\npsfPogCorr_r psfPogErr_r SDSS-r.res VARY\npsfPogCorr_i psfPogErr_i SDSS-i.res VARY\npsfPogCorr_z psfPogErr_z SDSS-z.res HOLD 0')
    columnsSDSSFile.close()

    ''' figure out the filter to hold '''
    list = ['SUBARU-10_1-1-W-C-RC','SUBARU-10_2-1-W-C-RC','MEGAPRIME-0-1-r','SUBARU-10_2-1-W-S-R+','SUBARU-9-4-W-C-RC','SUBARU-10_2-1-W-S-I+',]
    list += ['SUBARU-10_3-1-W-C-RC','SUBARU-10_3-1-W-S-R+','SUBARU-10_3-1-W-S-I+'] #adam
    for filt in list:
        if filt in filterlist:
            hold_all = filt
            break
    print ' hold_all=',hold_all
    f = open(columns,'w')
    for filt in filterlist:
        if filt != hold_all:
            f.write('MAG_' + magtype + '-' + filt + ' MAGERR_' + magtype + '-' + filt + ' ' + filt + '.res VARY\n')
        else:
            f.write('MAG_' + magtype + '-' + filt + ' MAGERR_' + magtype + '-' + filt + ' ' + filt + '.res HOLD 0\n')
    f.close()
    return columns

####### print command
####### #exit_code = os.system(command)
####### #if exit_code != 0: raise Exception
####### offset_list = catalog + '.offsets.list'
####### offset_list_reformat = offset_list + '.reformat'
####### magtype = 'APER1'
####### if magtype == 'APER1': aptype='aper'
####### elif magtype == 'ISO': aptype='iso'
####### if not cluster == 'COSMOS_PHOTOZ': # and updated_zeropoints > 0:
#######     save_slr_flag = photocalibrate_cat_flag = '--spec mode=' + magtype
#######     print 'running save_slr'
#######     command = os.environ['bonn'] + '/save_slr.py --cluster "%(cluster)s" -i %(catalog)s -o %(offset_list)s %(save_slr_flag)s' % {'cluster':cluster, 'catalog':catalog, 'offset_list':offset_list_reformat, 'save_slr_flag':save_slr_flag}
#######     print command
#######     exit_code = subprocess.check_call(command.split(),shell=True)
#######     print 'slr exit code', exit_code
#######     if exit_code != 0: raise Exception


if __name__ == '__main__':
    subarudir = os.environ['subdir']
    cluster = sys.argv[1] #'MACS1423+24'
    spec = False
    brightSDSS = False
    faintSDSS = False
    train_first = False
    magtype = 'APER1'
    AP_TYPE = ''
    type = 'all'
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
            if s == 'APER':
                raise Exception("Ughhh! You're raising the MAG_APER- vector version vs. splitting it into MAG_APER0-/MAG_APER1- and just using MAG_APER1- again!")
            if s == 'faintSDSS':
                faintSDSS = True
            if s == 'brightSDSS':
                brightSDSS = True
            if string.find(s,'detect') != -1:
                rs = re.split('=',s)
                DETECT_FILTER=rs[1]
            if string.find(s,'spectra') != -1:
                rs = re.split('=',s)
                SPECTRA=rs[1]
            if string.find(s,'aptype') != -1:
                rs = re.split('=',s)
                AP_TYPE = '_' + rs[1]
    print 'magtype', magtype
    #photdir = subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + AP_TYPE + '/'
    all(subarudir,cluster,DETECT_FILTER,AP_TYPE,magtype,faintSDSS=faintSDSS, brightSDSS=brightSDSS)
