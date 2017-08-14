import MySQLdb

def reformat(catalog):
    import string
    offset_list = catalog + '.offsets.list' 
    offset_list_reformat = offset_list + '.reformat'
                                                                                              
    o = open(offset_list,'r').readlines()
    o_new = open(offset_list_reformat,'w')
                                                                                              
    ''' translate into SLR format '''
    for l in o:
        import re
        res = re.split('\s+',l)
        if res[0] != '#' and string.find(l,'psf') == -1:
            o_new.write('DUMMY ' + res[0].replace('MAG_APER-','').replace('MAG_APER1-','') + ' ' + res[1] + ' 0\n')
    o_new.close()


def all(subarudir,cluster,DETECT_FILTER,aptype,magtype,location=None,faintSDSS=False,brightSDSS=False):
    print magtype
    save_slr_flag = photocalibrate_cat_flag = '--spec mode=' + magtype.replace('1','').replace('APER','aper').replace('2','')
    catalog_dir = subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + aptype + '/'
    catalog_dir_iso = subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + '_iso/'

    import pyfits, os, string, random
    min_err = 0.02

    #catalog_dir = '/'.join(catalog.split('/')[:-1])
    catalog_notcal = catalog_dir + '/' + cluster + '.stars.cat'

    catalog = catalog_dir + '/' + cluster + '.stars.calibrated.cat'

    import do_multiple_photoz   
    filterlist_all = do_multiple_photoz.get_filters(catalog,'OBJECTS')

    filterlist = []
    for filt in filterlist_all:
        if string.find(filt,'-2') == -1 and string.find(filt,'u') == -1 and string.find(filt,'-U') == -1:
            filterlist.append(filt)

    columns = catalog_dir + '/' + cluster + '.qc.columns'

    columnsSDSS = catalog_dir + '/' + cluster + '.sdss.columns'

    columnsSDSSFile = open(columnsSDSS,'w')
    columnsSDSSFile.write('psfPogCorr_g psfPogErr_g SDSS-g.res VARY\n\
psfPogCorr_r psfPogErr_r SDSS-r.res VARY\n\
psfPogCorr_i psfPogErr_i SDSS-i.res VARY\n\
psfPogCorr_z psfPogErr_z SDSS-z.res HOLD 0')
    columnsSDSSFile.close()

    useSDSS = False
    ''' if fewer than four filters, include SDSS stars '''

    if brightSDSS:
        command = 'python ' + os.environ['sne'] + '/qc/trunk/fit_locus.py -f ' + catalog + ' -c ' + columnsSDSS + ' -e 1 -b 0 -a -p ' + os.environ['sne'] + '/photoz/' + cluster + '/brightSDSSplots/'

    elif faintSDSS:
        command = 'python ' + os.environ['sne'] + '/qc/trunk/fit_locus.py -f ' + catalog + ' -c ' + columnsSDSS + ' -e 1 -b 0 -a -p ' + os.environ['sne'] + '/photoz/' + cluster + '/faintSDSSplots/'

    elif len(filterlist) < 4:
        command = 'python ' + os.environ['sne'] + '/qc/trunk/fit_locus.py -f ' + catalog + ' -c ' + columns + ' -e 1 -b 0 -a -p ' + os.environ['sne'] + '/photoz/' + cluster + '/SLRplots/'
        useSDSS = True
    else:
        command = 'python ' + os.environ['sne'] + '/qc/trunk/fit_locus.py -f ' + catalog + ' -c ' + columns + ' -e 1 -b 0 -p ' + os.environ['sne'] + '/photoz/' + cluster + '/SLRplots/'

    if faintSDSS or brightSDSS:

        import string
        offset_list = catalog + '.offsets.list' 
        offset_list_reformat = offset_list + '.reformat'

        print command
        exit_code = os.system(command)
        if exit_code != 0: raise Exception    



        print offset_list                                                                                                  
        o = open(offset_list,'r').readlines()

        db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-sr01')
        c = db2.cursor()

                                                                                                  
        ''' translate into SLR format '''
        for l in o:
            import re
            res = re.split('\s+',l)

            print res
            if res[0] != '#':
                if faintSDSS:                                                                                      
                    filt = res[0].replace('psfPogCorr_','') + 'faint'
                else:
                    filt = res[0].replace('psfPogCorr_','') + 'bright'
                                                                                                                   
                commandst = 'update slrsdss set ' + filt + '=' + str(res[1]) + ' where objname="' + cluster + '"'
                print commandst
                c.execute(commandst)                                             

        



        



    else:
        if True: #not useSDSS:                                                                                                                           
            ''' figure out the filter to hold '''                                                                                                       
            list = ['SUBARU-10_1-1-W-C-RC','SUBARU-10_2-1-W-C-RC','MEGAPRIME-0-1-r','SUBARU-10_2-1-W-S-R+','SUBARU-9-4-W-C-RC','SUBARU-10_2-1-W-S-I+',]
            for filt in list:
                if filt in filterlist:
                    hold_all = filt
                    break
        else: 
            ''' do not hold a filter is using SDSS -- otherwise potential for mismatch '''
            hold_all = None 
                                                                                                                                                         
        
        print hold_all
                                                                                                                                                         
                                                                                                                                                         
        f = open(columns,'w')
                                                                                                                                                         
        for filt in filterlist:
            if filt != hold_all:
                f.write('MAG_' + magtype + '-' + filt + ' MAGERR_' + magtype + '-' + filt + ' ' + filt + '.res VARY\n')
            else:
                f.write('MAG_' + magtype + '-' + filt + ' MAGERR_' + magtype + '-' + filt + ' ' + filt + '.res HOLD 0\n')
                                                                                                                                                         
        f.close()
                                                                                                                                                         
                                                                                                                                                         
        print command
        #exit_code = os.system(command)
        #if exit_code != 0: raise Exception    
                                                                                                                                                         
        
        
        reformat(catalog)
        
        
        offset_list = catalog + '.offsets.list' 
        offset_list_reformat = offset_list + '.reformat'

    
    
    
    
    
    

    
    



        import os                                                                                                                                                                                                                                         
        
        
        magtype = 'APER1'
        
        if magtype == 'APER1': aptype='aper'
        elif magtype == 'ISO': aptype='iso'
        
        if not cluster == 'COSMOS_PHOTOZ': # and updated_zeropoints > 0:
            save_slr_flag = photocalibrate_cat_flag = '--spec mode=' + magtype
            import subprocess
            print 'running save_slr'
            command = os.environ['bonn'] + '/save_slr.py --cluster "%(cluster)s" -i %(catalog)s -o %(offset_list)s %(save_slr_flag)s' % {'cluster':cluster, 'catalog':catalog, 'offset_list':offset_list_reformat, 'save_slr_flag':save_slr_flag}
            print command
            exit_code = subprocess.check_call(command.split(),shell=True)
    
            print 'slr exit code', exit_code
            if exit_code != 0: raise Exception    
    
    
            #import save_slr as sslr
            #import ldac
    
            #zplist = ldac.openObjectFile(catalog, 'ZPS')
    
            #sslr.saveSlrZP(cluster = cluster,
            #               offsetFile = offset_list_reformat,
            #               zplist = zplist,
            #               mode = magtype)
    
        









if __name__ == '__main__':
    import os , sys, string
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
                magtype = 'APER'

            if s == 'faintSDSS':
                faintSDSS = True

            if s == 'brightSDSS':
                brightSDSS = True
    
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

    print 'magtype', magtype
    
    #photdir = subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + AP_TYPE + '/'
    all(subarudir,cluster,DETECT_FILTER,AP_TYPE,magtype,faintSDSS=faintSDSS, brightSDSS=brightSDSS)
