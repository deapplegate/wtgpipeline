#
def cutout(infile,mag,color='red'):
    import os, utilities
    ppid = str(os.getppid())

    print ppid + 'a'

    #pylab.show()                 

    outfile = raw_input('name of output file?')

    color = raw_input('color of regions?')

    limits = ['lower_mag','upper_mag','lower_diff','upper_diff']
    lim_dict = {}
    for lim in limits:
        print lim + '?'
        b = raw_input()
        lim_dict[lim] = b

    utilities.run('ldacfilter -i ' + infile + ' -t PSSC\
                    -c "(((SEx_' + mag + '>' + str(lim_dict['lower_mag']) + ') AND (SEx_' + mag + '<' + str(lim_dict['upper_mag']) + ')) AND (magdiff>' + str(lim_dict['lower_diff']) + ')) AND (magdiff<' + str(lim_dict['upper_diff']) + ');"\
                    -o cutout1.' + ppid,['cutout1.' + ppid])
    utilities.run('ldactoasc -b -q -i cutout1.' + ppid + '  -t PSSC\
            -k Ra Dec > /tmp/' + outfile,[outfile])
    utilities.run('mkreg.pl -c -rad 8 -xcol 0 -ycol 1 -wcs -colour ' + color + ' /tmp/' +  outfile)

def get_median(cat,key):
    import astropy.io.fits as pyfits, sys, os, re, string, copy

    p = pyfits.open(cat)
    magdiff = p[1].data.field(key)
    magdiff.sort()

    return magdiff[int(len(magdiff)/2)] 

def coordinate_limits(cat):
    import astropy.io.fits as pyfits, sys, os, re, string, copy

    p = pyfits.open(cat)
    ra = p[2].data.field('ALPHA_J2000')
    ra.sort()
    dec = p[2].data.field('DELTA_J2000')
    dec.sort()

    return ra[0],ra[-1],dec[0],dec[-1]

def combine_cats(cats,outfile,search_params):
    #cats = [{'im_type': 'DOMEFLAT', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.DOMEFLAT.fixwcs.rawconv'}, {'im_type': 'SKYFLAT', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.SKYFLAT.fixwcs.rawconv'}, {'im_type': 'OCIMAGE', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.OCIMAGE.fixwcs.rawconv'}] 
    #outfile = '' + search_params['TEMPDIR'] + 'stub'
    #cats = [{'im_type': 'MAIN', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS..fixwcs.rawconv'}, {'im_type': 'D', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.D.fixwcs.rawconv'}]

    import astropy.io.fits as pyfits, sys, os, re, string, copy
    from config_bonn import cluster, tag, arc, filters
    ppid = str(os.getppid())

    tables = {} 
    colset = 0
    cols = []
    for catalog in cats: 
        file = catalog['cat'] 
        os.system('mkdir ' + search_params['TEMPDIR'] )
        os.system('ldactoasc -i ' + catalog['cat'] + ' -b -s -k MAG_APER MAGERR_APER -t OBJECTS > ' + search_params['TEMPDIR'] + '/APER')
        os.system('asctoldac -i ' + search_params['TEMPDIR'] + '/APER -o ' + search_params['TEMPDIR'] + '/cat1 -t OBJECTS -c ./photconf/MAG_APER.conf')
        os.system('ldacjoinkey -i ' + catalog['cat'] + ' -p ' + search_params['TEMPDIR'] + '/cat1 -o ' + search_params['TEMPDIR'] + '/all.conv' + catalog['im_type'] + '  -k MAG_APER1 MAG_APER2 MAGERR_APER1 MAGERR_APER2')
        tables[catalog['im_type']] = pyfits.open(search_params['TEMPDIR'] + '/all.conv' + catalog['im_type'])
        #if filter == filters[0]:
        #    tables['notag'] = pyfits.open('' + search_params['TEMPDIR'] + 'all.conv' )
    
    for catalog in cats:
        for i in range(len(tables[catalog['im_type']][1].columns)): 
            print catalog['im_type'], catalog['cat']
            #raw_input()
            if catalog['im_type'] != '':
                tables[catalog['im_type']][1].columns[i].name = tables[catalog['im_type']][1].columns[i].name + catalog['im_type'] 
            else:
                tables[catalog['im_type']][1].columns[i].name = tables[catalog['im_type']][1].columns[i].name
            cols.append(tables[catalog['im_type']][1].columns[i])
    
    print cols
    print len(cols)
    hdu = pyfits.PrimaryHDU()
    hduIMHEAD = pyfits.BinTableHDU.from_columns(tables[catalog['im_type']][2].columns)
    hduOBJECTS = pyfits.BinTableHDU.from_columns(cols) 
    hdulist = pyfits.HDUList([hdu])
    hdulist.append(hduIMHEAD)
    hdulist.append(hduOBJECTS)
    hdulist[1].header['EXTNAME']='FIELDS'
    hdulist[2].header['EXTNAME']='OBJECTS'
    print file
    os.system('rm ' + outfile)
    import re
    res = re.split('/',outfile)
    os.system('mkdir -p ' + reduce(lambda x,y: x + '/' + y,res[:-1]))
    hdulist.writeto(outfile)
    print outfile , '#########'
    print 'done'

def paste_cats(cats,outfile): #cats,outfile,search_params):
    #outfile = '/tmp/test.cat'
    #cats = ['/tmp/15464/SUPA0028506_1OCFS.newpos', '/tmp/15464/SUPA0028506_9OCFS.newpos']
    #print outfile, cats
      
  
    import astropy.io.fits as pyfits, sys, os, re, string, copy        
    from config_bonn import cluster, tag, arc, filters
    ppid = str(os.getppid())
    tables = {} 
    colset = 0
    cols = []
   
    table = pyfits.open(cats[0])

    data = [] 
    nrows = 0
    for catalog in cats:
        cattab = pyfits.open(catalog)
        nrows += cattab[2].data.shape[0]

    hduOBJECTS = pyfits.BinTableHDU.from_columns(table[2].columns, nrows=nrows) 
   
    rowstart = 0
    rowend = 0
    for catalog in cats:
        cattab = pyfits.open(catalog)
        rowend += cattab[2].data.shape[0]
        for i in range(len(cattab[2].columns)): 
            hduOBJECTS.data.field(i)[rowstart:rowend]=cattab[2].data.field(i)
        rowstart = rowend


    # update SeqNr
    print rowend,len(        hduOBJECTS.data.field('SeqNr')), len(range(1,rowend+1))
    hduOBJECTS.data.field('SeqNr')[0:rowend]=range(1,rowend+1)

    #hdu[0].header['EXTNAME']='FIELDS'


    hduIMHEAD = pyfits.BinTableHDU.from_columns(table[1])

    print cols
    print len(cols)
    hdu = pyfits.PrimaryHDU()
    hdulist = pyfits.HDUList([hdu])
    hdulist.append(hduIMHEAD)
    hdulist.append(hduOBJECTS)
    hdulist[1].header['EXTNAME']='FIELDS'
    hdulist[2].header['EXTNAME']='OBJECTS'
    print file

    os.system('rm ' + outfile)
    hdulist.writeto(outfile)
    print outfile , '#########'
    print 'done'

def imstats(SUPA,FLAT_TYPE):
    import os, re, utilities, bashreader, sys, string
    from copy import copy
    from glob import glob
    dict = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['cluster'])
    search_params.update(dict)
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':search_params['cluster']}
    print dict['files']
    import commands
    tmp_dicts = [] 
    for file in dict['files']:
        op = commands.getoutput('imstats ' + dict['files'][0]) 
        print op
        res = re.split('\n',op)
        for line in res:
            if string.find(line,'filename') != -1:
                line = line.replace('# imstats: ','')
                res2 = re.split('\t',line)
                                                               
        res3 = re.split('\s+',res[-1]) 

        tmp_dict = {}
        for i in range(len(res3)):
            tmp_dict[res2[i]] = res3[i] 
        tmp_dicts.append(tmp_dict)
    print tmp_dicts

    median_average = 0
    sigma_average = 0
    for d in tmp_dicts:
        print d.keys()
        sigma_average += float(d['sigma'])
        median_average += float(d['median'])

    dict['sigma_average'] = sigma_average / len(tmp_dicts)
    dict['median_average'] = median_average / len(tmp_dicts)

    print dict['sigma_average'], dict['median_average']

    save_exposure(dict,SUPA,FLAT_TYPE)

def save_fit(fits,im_type,type,SUPA,FLAT_TYPE):
    import MySQLdb, sys, os, re, time 
    from copy import copy
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()

    for fit in fits:
        #which_solution += 1
        user_name = os.environ['USER']
        time_now = time.asctime() 
        user = user_name #+ str(time.time())
        
        dict = {} 
        #copy array but exclude lists                                                   
        for ele in fit['class'].fitvars.keys():
            if ele != 'condition' and ele != 'model_name' and ele != 'fixed_name': 
                dict[ele + '_' + type + '_' + im_type] = fit['class'].fitvars[ele]
    save_exposure(dict,SUPA,FLAT_TYPE)

def select_analyze(cluster):
    import MySQLdb, sys, os, re, time 
    from copy import copy
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()

    command = "DESCRIBE illumination_db"
    print command
    c.execute(command)
    results = c.fetchall()
    keys = []
    for line in results:
        keys.append(line[0])
    print keys

    command = "SELECT * from illumination_db where zp_err_galaxy_D is null and PPRUN='2002-06-04_W-J-V'" # where cluster='HDFN' and filter='W-J-V' and ROTATION=0"

    command = "SELECT * from illumination_db where matched_cat_star is null" # where cluster='HDFN' and filter='W-J-V' and ROTATION=0"


    #command = "select * from illumination_db where SUPA='SUPA0028506'"

    command = "select * from illumination_db where cluster='MACS0417-11' and  OBJECT like '%0417c%' and color1_star_ is null"
    print command
    c.execute(command)
    results = c.fetchall()
    print len(results)
    dicts = [] 

    for j in range(len(results)):
        dict = {} 
        print j, len(results)
        for i in range(len(results[j])):  
            dict[keys[i]] = results[j][i]
        print dict['SUPA'], dict['file'], dict['cluster'], dict['pasted_cat'], dict['matched_cat_star']

        #good = raw_input()
        d_update = get_files(dict['SUPA'],dict['FLAT_TYPE'])
        go = 0
        if d_update.has_key('TRIED'):
            if d_update['TRIED'] != 'YES':
                go = 1
        else: go = 1
        if 1: #go:
            save_exposure({'TRIED':'YES'},dict['SUPA'],dict['FLAT_TYPE'])
            analyze(dict['SUPA'],dict['FLAT_TYPE'])

def analyze(SUPA,FLAT_TYPE):
    #try:
    import sys
    import os                   
    #os.system('rm -rf ' + search_params['TEMPDIR'] + '*')
    ppid = str(os.getppid())
    #try:
    if 1:
        #imstats(SUPA,FLAT_TYPE) 
        #find_seeing(SUPA,FLAT_TYPE)      
        #length(SUPA,FLAT_TYPE)
        #sextract(SUPA,FLAT_TYPE)
        #match_simple(SUPA,FLAT_TYPE)
        phot(SUPA,FLAT_TYPE)
    #except KeyboardInterrupt:
    #    raise
    #except: 
    #    ppid_loc = str(os.getppid())
    #    print sys.exc_info()
    #    print 'something else failed',ppid, ppid_loc 
    # 
    #    if ppid_loc != ppid: sys.exit(0) 
#        os.system('rm -rf /tmp/' + ppid)
#
#    os.system('rm -rf /tmp/' + ppid)
#

def get_files(SUPA,FLAT_TYPE):    
    import MySQLdb, sys, os, re                                                                     
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()

    command = "DESCRIBE illumination_db"
    print command
    c.execute(command)
    results = c.fetchall()
    keys = []
    for line in results:
        keys.append(line[0])

    command = "SELECT * from illumination_db where SUPA='" + SUPA + "' AND FLAT_TYPE='" + FLAT_TYPE + "'"
    print command
    c.execute(command)
    results = c.fetchall()
    dict = {} 
    for i in range(len(results[0])):
        dict[keys[i]] = results[0][i]
    print dict 

    file_pat = dict['file'] 
    print file_pat
    import re, glob
    res = re.split('_\d+O',file_pat)
    pattern = res[0] + '_*O' + res[1]
    print pattern

    files = glob.glob(pattern)
    dict['files'] = files
    print files
    return dict

def save_exposure(dict,SUPA=None,FLAT_TYPE=None):
    if SUPA != None and FLAT_TYPE != None:
        dict['SUPA'] = SUPA
        dict['FLAT_TYPE'] = FLAT_TYPE

    import MySQLdb, sys, os, re                                                                     
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()
    
    command = "CREATE TABLE IF NOT EXISTS illumination_db ( id MEDIUMINT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id))"
    print command
    #c.execute("DROP TABLE IF EXISTS illumination_db")
    #c.execute(command)

    import MySQLdb, sys, os, re                                                                                                                                                                                
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()

    from copy import copy
    floatvars = {}  
    stringvars = {}
    #copy array but exclude lists                                                   
    import string
    letters = string.ascii_lowercase + string.ascii_uppercase.replace('E','') + '_' + '-'
    for ele in dict.keys():
        type = 'float'
        for l in letters:
            if string.find(str(dict[ele]),l) != -1: 
                type = 'string'
        if type == 'float':  
            floatvars[ele] = str(float(dict[ele])) 
        elif type == 'string':
            stringvars[ele] = dict[ele] 
                                                                                                                                                                                                           
    # make database if it doesn't exist
    print 'floatvars', floatvars
    print 'stringvars', stringvars
                                                                                                                                                                                                          
    for column in stringvars: 
        try:
            command = 'ALTER TABLE illumination_db ADD ' + column + ' varchar(240)'
            c.execute(command)  
        except: nope = 1 
                                                                                                                                                                                                          
    for column in floatvars: 
        try:
            command = 'ALTER TABLE illumination_db ADD ' + column + ' float(30)'
            c.execute(command)  
        except: nope = 1 




    # insert new observation 

    SUPA = dict['SUPA'] 
    flat = dict['FLAT_TYPE']
    c.execute("SELECT SUPA from illumination_db where SUPA = '" + SUPA + "' and flat_type = '" + flat + "'")
    results = c.fetchall() 
    print results
    if len(results) > 0:
        print 'already added'
    else:
        command = "INSERT INTO illumination_db (SUPA,FLAT_TYPE) VALUES ('" + dict['SUPA'] + "','" + dict['FLAT_TYPE'] + "')"
        print command
        c.execute(command) 

    import commands

     
    vals = ''
    for key in stringvars.keys():
        print key, stringvars[key]
        vals += ' ' + key + "='" + str(stringvars[key]) + "',"

    for key in floatvars.keys():
        print key, floatvars[key]
        vals += ' ' + key + "='" + floatvars[key] + "',"
    vals = vals[:-1]

    command = "UPDATE illumination_db set " + vals + " WHERE SUPA='" + dict['SUPA'] + "' AND FLAT_TYPE='" + dict['FLAT_TYPE'] + "'" 
    print command
    c.execute(command)
        

    print vals
        

    #names = reduce(lambda x,y: x + ',' + y, [x for x in floatvars.keys()])
    #values = reduce(lambda x,y: str(x) + ',' + str(y), [floatvars[x] for x in floatvars.keys()])
    #names += ',' + reduce(lambda x,y: x + ',' + y, [x for x in stringvars.keys()])
    #values += ',' + reduce(lambda x,y: x + ',' + y, ["'" + str(stringvars[x]) + "'" for x in stringvars.keys()])

        
    #command = "INSERT INTO illumination_db (" + names + ") VALUES (" + values + ")"
    #print command
    #os.system(command)


def initialize(filter,cluster):
    import os, re, bashreader, sys, string, utilities
    from glob import glob
    from copy import copy

    dict = bashreader.parseFile('progs.ini')
    for key in dict.keys():
        os.environ[key] = str(dict[key])
    import os
    ppid = str(os.getppid())
    PHOTCONF = './photconf/'
    TEMPDIR = '/tmp/' + ppid + '/'
    os.system('mkdir ' + TEMPDIR)
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':cluster}
    search_params = {'path':path, 'cluster':cluster, 'filter':filter, 'PHOTCONF':PHOTCONF, 'DATACONF':os.environ['DATACONF'], 'TEMPDIR':TEMPDIR} 

    return search_params


def update_dict(SUPA,FLAT_TYPE):    
    import utilities
    dict = get_files(SUPA,FLAT_TYPE)
    print dict['file']
    kws = utilities.get_header_kw(dict['file'],['ROTATION','OBJECT','GABODSID','CONFIG','EXPTIME','AIRMASS','INSTRUM','PPRUN','BADCCD']) # return KEY/NA if not SUBARU 
    save_exposure(kws,SUPA,FLAT_TYPE)
    

def gather_exposures(cluster,filters=None):
    if not filters:
        filters =  ['B','W-J-B','W-J-V','W-C-RC','W-C-IC','I','W-S-Z+']        
    for filter in filters:
        search_params = initialize(filter,cluster) 
        import os, re, bashreader, sys, string, utilities
        from glob import glob
        from copy import copy
        
        searchstr = "/%(path)s/%(filter)s/SCIENCE/*fits" % search_params
        print searchstr
        files = glob(searchstr)
        files.sort()
        #print files
        exposures =  {} 
        # first 30 files
        #print files[0:30]
                                                                                                                                                                                      
        import MySQLdb, sys, os, re                                                                     
        db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
        c = db2.cursor()
                                                                                                                                                                                      
        for file in files:
            if string.find(file,'wcs') == -1 and string.find(file,'.sub.fits') == -1:
                res = re.split('_',re.split('/',file)[-1])                                        
                exp_name = res[0]
                                                                                                                                                                                      
                if not exposures.has_key(exp_name): exposures[exp_name] = {'images':[],'keywords':{}}
                                                                                                                                                                                      
                exposures[exp_name]['images'].append(file) # exp_name is the root of the image name
                                                                                                                                                                                      
                if len(exposures[exp_name]['keywords'].keys()) == 0: #not exposures[exp_name]['keywords'].has_key('ROTATION'): #if exposure does not have keywords yet, then get them
                    exposures[exp_name]['keywords']['filter'] = filter
                    exposures[exp_name]['keywords']['file'] = file 
                    res2 = re.split('/',file)   
                    for r in res2:
                        if string.find(r,filter) != -1:
                            print r
                            exposures[exp_name]['keywords']['date'] = r.replace(filter + '_','')
                            exposures[exp_name]['keywords']['fil_directory'] = r 
                            search_params['fil_directory'] = r
                    kws = utilities.get_header_kw(file,['CRVAL1','CRVAL2','ROTATION','OBJECT','GABODSID','CONFIG','EXPTIME','AIRMASS','INSTRUM','PPRUN','BADCCD']) # return KEY/NA if not SUBARU 
                                                                                                                                                                                      
                    ''' figure out a way to break into SKYFLAT, DOMEFLAT '''
                                                                                                                                                                                      
                    ppid = str(os.getppid())
                    command = 'dfits ' + file + ' > ' + search_params['TEMPDIR'] + '/header'
                    utilities.run(command)
                    file = open('' + search_params['TEMPDIR'] + 'header','r').read()
                    import string                    
                    if string.find(file,'SKYFLAT') != -1: exposures[exp_name]['keywords']['FLAT_TYPE'] = 'SKYFLAT' 
                    elif string.find(file,'DOMEFLAT') != -1: exposures[exp_name]['keywords']['FLAT_TYPE'] = 'DOMEFLAT' 
                    #print file, exposures[exp_name]['keywords']['FLAT_TYPE'] 
                                                                                                                                                                                      
                    file = open('' + search_params['TEMPDIR'] + 'header','r').readlines()
                    import string                    
                    for line in file:
                        print line
                        if string.find(line,'Flat frame:') != -1 and string.find(line,'illum') != -1:
                            import re                   
                            res = re.split('SET',line)
                            if len(res) > 1:
                                res = re.split('_',res[1])                                                                                                                                 
                                set = res[0]
                                exposures[exp_name]['keywords']['FLAT_SET'] = set
                                                                                                                                                                                          
                                res = re.split('illum',line)
                                res = re.split('\.',res[1])
                                smooth = res[0]
                                exposures[exp_name]['keywords']['SMOOTH'] = smooth 
                            break
                                                                                                                                                                                      
                    for kw in kws.keys(): 
                        exposures[exp_name]['keywords'][kw] = kws[kw]
                    exposures[exp_name]['keywords']['SUPA'] = exp_name
                    exposures[exp_name]['keywords']['cluster'] = cluster 
                    print exposures[exp_name]['keywords']
                    save_exposure(exposures[exp_name]['keywords'])

    return exposures



def find_seeing(SUPA,FLAT_TYPE):     
    import os, re, utilities, sys
    from copy import copy
    dict = get_files(SUPA,FLAT_TYPE)
    print dict['file']
    search_params = initialize(dict['filter'],dict['cluster'])
    search_params.update(dict)

    print dict['files']

    #params PIXSCALE GAIN

    ''' quick run through for seeing '''
    children = []
    for image in search_params['files']:                                                                                 
        child = os.fork()
        if child:
            children.append(child)
        else:
            params = copy(search_params)     
            
            ROOT = re.split('\.',re.split('\/',image)[-1])[0]
            params['ROOT'] = ROOT
            NUM = re.split('O',re.split('\_',ROOT)[1])[0]
            params['NUM'] = NUM
            print ROOT
                                                                                                                     
            weightim = "/%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits" % params
            #flagim = "/%(path)s/%(fil_directory)s/WEIGHTS/globalflag_%(NUM)s.fits" % params
            #finalflagim = TEMPDIR + "flag_%(ROOT)s.fits" % params 
            params['finalflagim'] = weightim
            #os.system('rm ' + finalflagim)
            #command = "ic -p 16 '1 %2 %1 0 == ?' " + weightim + " " + flagim + " > " + finalflagim
            #utilities.run(command)
            
            command = "nice sex %(file)s -c %(PHOTCONF)s/singleastrom.conf.sex \
                        -FLAG_IMAGE ''\
                        -FLAG_TYPE MAX\
                        -CATALOG_NAME %(TEMPDIR)s/seeing_%(ROOT)s.cat \
                        -FILTER_NAME %(PHOTCONF)s/default.conv\
                        -CATALOG_TYPE 'ASCII' \
                        -DETECT_MINAREA 8 -DETECT_THRESH 8.\
                        -ANALYSIS_THRESH 8 \
                        -WEIGHT_IMAGE /%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits\
                        -WEIGHT_TYPE MAP_WEIGHT\
                        -PARAMETERS_NAME %(PHOTCONF)s/singleastrom.ascii.flag.sex" %  params 
                                                                                                                     
            print command
            os.system(command)
            sys.exit(0)
    for child in children:  
        os.waitpid(child,0)
                                                                                                                          
                                                                                                                          
    command = 'cat ' + search_params['TEMPDIR'] + 'seeing_' +  SUPA + '*cat > ' + search_params['TEMPDIR'] + 'paste_seeing_' + SUPA + '.cat' 
    utilities.run(command)
                                                                                                                          
    file_seeing = search_params['TEMPDIR'] + '/paste_seeing_' + SUPA + '.cat'
    PIXSCALE = float(search_params['PIXSCALE'])
    reload(utilities)
    fwhm = utilities.calc_seeing(file_seeing,10,PIXSCALE)

    save_exposure({'fwhm':fwhm},SUPA,FLAT_TYPE)

    print file_seeing, SUPA, PIXSCALE

def length(SUPA,FLAT_TYPE):
    import os, re, utilities, bashreader, sys, string
    from copy import copy
    from glob import glob
    dict = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['cluster'])
    search_params.update(dict)
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':search_params['cluster']}
    
    ''' get the CRPIX values '''
    start = 1
    #CRPIXZERO is at the chip at the bottom left and so has the greatest value!!!!
    for image in search_params['files']:
        print image                                                 
        res = re.split('\_\d+',re.split('\/',image)[-1])
        #print res
        imroot = "/%(path)s/%(fil_directory)s/SCIENCE/" % search_params
        im = imroot + res[0] + '_1' + res[1] 
        #print im
        crpix = utilities.get_header_kw(image,['CRPIX1','CRPIX2','NAXIS1','NAXIS2'])
        if start == 1:
            crpixzero = copy(crpix)
            crpixhigh = copy(crpix)
            start = 0
        from copy import copy 
        print  float(crpix['CRPIX1'])  < float(crpixzero['CRPIX1']), float(crpix['CRPIX2'])  < float(crpixzero['CRPIX2'])
        if float(crpix['CRPIX1']) + 50   >= float(crpixzero['CRPIX1']) and float(crpix['CRPIX2'])  +50 >= float(crpixzero['CRPIX2']):
            crpixzero = copy(crpix)
                                                                                                                          
        if float(crpix['CRPIX1']) - 50  <= float(crpixhigh['CRPIX1']) and float(crpix['CRPIX2']) - 50  <= float(crpixhigh['CRPIX2']):
            crpixhigh = copy(crpix)

        print crpix['CRPIX1'], crpix['CRPIX2'], crpixzero['CRPIX1'], crpixzero['CRPIX2'], crpixhigh['CRPIX1'], crpixhigh['CRPIX2']#, crpixhigh

    LENGTH1 =  abs(float(crpixhigh['CRPIX1']) - float(crpixzero['CRPIX1'])) + float(crpix['NAXIS1']) 
    LENGTH2 =  abs(float(crpixhigh['CRPIX2']) - float(crpixzero['CRPIX2'])) + float(crpix['NAXIS2']) 

    print LENGTH1, LENGTH2, crpixzero['CRPIX1'], crpixzero['CRPIX2'], crpixhigh['CRPIX1'], crpixhigh['CRPIX2']#, crpixhigh

    save_exposure({'crfixed':'third','LENGTH1':LENGTH1,'LENGTH2':LENGTH2,'CRPIX1ZERO':crpixzero['CRPIX1'],'CRPIX2ZERO':crpixzero['CRPIX2']},SUPA,FLAT_TYPE)

def sextract(SUPA,FLAT_TYPE):
    import os, re, utilities, bashreader, sys, string
    from copy import copy
    from glob import glob
    
    dict = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['cluster'])
    search_params.update(dict)
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':search_params['cluster']}
    subpath='/nfs/slac/g/ki/ki05/anja/SUBARU/'

    children = []
    print search_params

    
    kws = utilities.get_header_kw(search_params['files'][0],['PPRUN'])
    print kws['PPRUN']
    pprun = kws['PPRUN']

    #fs = glob.glob(subpath+pprun+'/SCIENCE_DOMEFLAT*.tarz')
    #if len(fs) > 0: 
    #    os.system('tar xzvf ' + fs[0])
    #fs = glob.glob(subpath+pprun+'/SCIENCE_SKYFLAT*.tarz')
    #if len(fs) > 0: 
    #    os.system('tar xzvf ' + fs[0])


    search_params['files'].sort()

    if 1:
        print search_params['files']                                                                                                                                                                                                                                                                                                                                                                                                                                
        for image in search_params['files']:
            print image
            child = os.fork()
            if child:
                children.append(child)
            else:
                try:
                    params = copy(search_params)     
                    ROOT = re.split('\.',re.split('\/',image)[-1])[0]
                    params['ROOT'] = ROOT
                    BASE = re.split('O',ROOT)[0]
                    params['BASE'] = BASE 
                    NUM = re.split('O',re.split('\_',ROOT)[1])[0]
                    params['NUM'] = NUM
                    print NUM, BASE, ROOT
                    params['GAIN'] = 2.50 ## WARNING!!!!!!
                    print ROOT
                    finalflagim = "%(TEMPDIR)sflag_%(ROOT)s.fits" % params     
                    weightim = "/%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits" % params
                    #flagim = "/%(path)s/%(fil_directory)s/WEIGHTS/globalflag_%(NUM)s.fits" % params
                    #finalflagim = TEMPDIR + "flag_%(ROOT)s.fits" % params 
                    params['finalflagim'] = weightim
                    im = "/%(path)s/%(fil_directory)s/SCIENCE/%(ROOT)s.fits" % params
                    crpix = utilities.get_header_kw(im,['CRPIX1','CRPIX2'])
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                    SDSS1 = "/%(path)s/%(fil_directory)s/SCIENCE/headers_scamp_SDSS-R6/%(BASE)s.head" % params
                    SDSS2 = "/%(path)s/%(fil_directory)s/SCIENCE/headers_scamp_SDSS-R6/%(BASE)sO*.head" % params
                    from glob import glob 
                    print glob(SDSS1), glob(SDSS2)
                    head = None
                    if len(glob(SDSS1)) > 0:
                        head = glob(SDSS1)[0]
                    elif len(glob(SDSS2)) > 0:
                        head = glob(SDSS2)[0]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                    if head is None:
                        command = "sex /%(path)s/%(fil_directory)s/SCIENCE/%(ROOT)s.fits -c %(PHOTCONF)s/phot.conf.sex \
                        -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
                        -CATALOG_NAME %(TEMPDIR)s/%(ROOT)s.cat \
                        -FILTER_NAME %(DATACONF)s/default.conv\
                        -FILTER  Y \
                        -FLAG_TYPE MAX\
                        -FLAG_IMAGE ''\
                        -SEEING_FWHM %(fwhm).3f \
                        -DETECT_MINAREA 3 -DETECT_THRESH 3 -ANALYSIS_THRESH 3 \
                        -MAG_ZEROPOINT 27.0 \
                        -GAIN %(GAIN).3f \
                        -WEIGHT_IMAGE /%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits\
                        -WEIGHT_TYPE MAP_WEIGHT" % params
                        #-CHECKIMAGE_TYPE BACKGROUND,APERTURES,SEGMENTATION\
                        #-CHECKIMAGE_NAME /%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.background.fits,/%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.apertures.fits,/%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.segmentation.fits\
                        
                        catname = "%(TEMPDIR)s/%(ROOT)s.cat" % params
                        filtcatname = "%(TEMPDIR)s/%(ROOT)s.filt.cat" % params
                        print command
                        utilities.run(command,[catname])
                        utilities.run('ldacfilter -i ' + catname + ' -o ' + filtcatname + ' -t LDAC_OBJECTS\
                                    -c "(CLASS_STAR > 0.0);"',[filtcatname])
                        if len(glob(filtcatname)) > 0:
                            import commands                                                                                                        
                            lines = commands.getoutput('ldactoasc -s -b -i ' + filtcatname + ' -t LDAC_OBJECTS | wc -l')
                            import re
                            res = re.split('\n',lines)
                            print lines
                            if int(res[-1]) == 0: sys.exit(0)
                            command = 'scamp ' + filtcatname + " -SOLVE_PHOTOM N -ASTREF_CATALOG SDSS-R6 -CHECKPLOT_TYPE NONE -WRITE_XML N "  
                            print command
                            utilities.run(command)
                            head = "%(TEMPDIR)s/%(ROOT)s.filt.head" % params
                            #headfile = "%(TEMPDIR)s/%(ROOT)s.head" % params
                    print head 
                    if head is not None:
                        hf = open(head,'r').readlines() 
                        hdict = {}
                        for line in hf:
                            import re
                            if string.find(line,'=') != -1:
                                res = re.split('=',line)
                                name = res[0].replace(' ','')
                                res = re.split('/',res[1])
                                value = res[0].replace(' ','')
                                print name, value
                                hdict[name] = value
                                                                                                                                               
                        imfix = "%(TEMPDIR)s/%(ROOT)s.fixwcs.fits" % params
                        print imfix
                        
                        os.system('mkdir ' + search_params['TEMPDIR'])
                        command = "cp " + im + " " + imfix
                        print command
                        utilities.run(command)
                       
                        import commands
                        out = commands.getoutput('gethead ' + imfix + ' CRPIX1 CRPIX2')
                        import re
                        res = re.split('\s+',out)
                        os.system('sethead ' + imfix + ' CRPIX1OLD=' + res[0])
                        os.system('sethead ' + imfix + ' CRPIX2OLD=' + res[1])
                        for name in ['CRVAL1','CRVAL2','CD1_1','CD1_2','CD2_1','CD2_2','CRPIX1','CRPIX2']:
                            command = 'sethead ' + imfix + ' ' + name + '=' + hdict[name]
                            print command
                            os.system(command)
                        main_file = '%(TEMPDIR)s/%(ROOT)s.fixwcs.fits' % params
                        doubles_raw = [{'file_pattern':main_file,'im_type':''},
                                       {'file_pattern':subpath+pprun+'/SCIENCE_DOMEFLAT*/'+BASE+'OC*.fits','im_type':'D'},
                                       {'file_pattern':subpath+pprun+'/SCIENCE_SKYFLAT*/'+BASE+'OC*.fits','im_type':'S'}]
                                       #{'file_pattern':subpath+pprun+'/SCIENCE/OC_IMAGES/'+BASE+'OC*.fits','im_type':'OC'}
                                       # ] 
                                                                                                                                  
                        print doubles_raw
                        doubles_output = []
                        print doubles_raw
                        for double in doubles_raw:
                            file = glob(double['file_pattern'])
                            if len(file) > 0:
                                params.update(double) 
                                params['double_cat'] = '%(TEMPDIR)s/%(ROOT)s.%(im_type)s.fixwcs.cat' % params
                                params['file_double'] = file[0]
                                command = "nice sex %(TEMPDIR)s%(ROOT)s.fixwcs.fits,%(file_double)s -c %(PHOTCONF)s/phot.conf.sex \
                                -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
                                -CATALOG_NAME %(double_cat)s \
                                -FILTER_NAME %(DATACONF)s/default.conv\
                                -FILTER  Y \
                                -FLAG_TYPE MAX\
                                -FLAG_IMAGE ''\
                                -SEEING_FWHM %(fwhm).3f \
                                -DETECT_MINAREA 3 -DETECT_THRESH 3 -ANALYSIS_THRESH 3 \
                                -MAG_ZEROPOINT 27.0 \
                                -GAIN %(GAIN).3f \
                                -WEIGHT_IMAGE /%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits\
                                -WEIGHT_TYPE MAP_WEIGHT" % params
                                #-CHECKIMAGE_TYPE BACKGROUND,APERTURES,SEGMENTATION\
                                #-CHECKIMAGE_NAME /%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.background.fits,/%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.apertures.fits,/%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.segmentation.fits\
                                catname = "%(TEMPDIR)s/%(ROOT)s.cat" % params
                                print command
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                                utilities.run(command,[catname])
                                command = 'ldacconv -b 1 -c R -i ' + params['double_cat']  + ' -o '  + params['double_cat'].replace('cat','rawconv')
                                print command
                                utilities.run(command)
                                #command = 'ldactoasc -b -q -i ' + params['double_cat'].replace('cat','rawconv') + '  -t OBJECTS\
                                #        -k ALPHA_J2000 DELTA_J2000 > ' + params['double_cat'].replace('cat','pos')
                                #print command
                                #utilities.run(command)
                                #print 'mkreg.pl -c -rad 8 -xcol 0 -ycol 1 -wcs -colour green ' + params['double_cat'].replace('cat','pos')
                                #utilities.run(command)
                                #print params['double_cat'].replace('cat','pos')
                                # Xpos_ABS is difference of CRPIX and zero CRPIX
                                doubles_output.append({'cat':params['double_cat'].replace('cat','rawconv'),'im_type':double['im_type']})
                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
                        print doubles_output
                        print '***********************************'
                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
                        outfile = params['TEMPDIR'] + params['ROOT'] + '.conv'
                        combine_cats(doubles_output,outfile,search_params)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                        #outfile_field = params['TEMPDIR'] + params['ROOT'] + '.field'
                        #command = 'ldacdeltab -i ' + outfile + ' -t FIELDS -o ' + outfile_field
                        #utilities.run(command)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                        command = 'ldactoasc -b -q -i ' + outfile + '  -t OBJECTS\
                                        -k ALPHA_J2000 DELTA_J2000 > ' + outfile.replace('conv','pos')
                        print command
                        utilities.run(command)
                        command = 'mkreg.pl -c -rad 8 -xcol 0 -ycol 1 -wcs -colour green ' + outfile.replace('conv','pos')
                        print command
                        utilities.run(command)
                        print outfile
                        command = 'ldaccalc -i ' + outfile + ' -o ' + params['TEMPDIR'] + params['ROOT'] + '.newpos -t OBJECTS -c "(Xpos + ' +  str(float(search_params['CRPIX1ZERO']) - float(crpix['CRPIX1'])) + ');" -k FLOAT -n Xpos_ABS "" -c "(Ypos + ' + str(float(search_params['CRPIX2ZERO']) - float(crpix['CRPIX2'])) + ');" -k FLOAT -n Ypos_ABS "" -c "(Ypos*0 + ' + str(params['NUM']) + ');" -k FLOAT -n CHIP "" ' 
                        print command
                        utilities.run(command)
                except:
                    print sys.exc_info()
                    print 'finishing' 
                    sys.exit(0)
                sys.exit(0)
        print children
        for child in children:  
            print 'waiting for', child
            os.waitpid(child,0)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
        print 'finished waiting'

    pasted_cat = path + 'PHOTOMETRY/ILLUMINATION/' + 'pasted_' + SUPA + '_' + search_params['filter'] + '_' + str(search_params['ROTATION']) + '.cat'

    from glob import glob        
    outcat = search_params['TEMPDIR'] + 'tmppaste_' + SUPA + '.cat'
    newposlist = glob(search_params['TEMPDIR'] + SUPA + '*newpos')
    print search_params['TEMPDIR'] + SUPA + '*newpos'
    if len(newposlist) > 1:
        #command = 'ldacpaste -i ' + search_params['TEMPDIR'] + SUPA + '*newpos -o ' + pasted_cat 
        #print command
        files = glob(search_params['TEMPDIR'] + SUPA + '*newpos')
        print files
        paste_cats(files,pasted_cat)
    else:
        command = 'cp ' + newposlist[0] + ' ' + pasted_cat 
        utilities.run(command)
    save_exposure({'pasted_cat':pasted_cat},SUPA,FLAT_TYPE)

    #fs = glob.glob(subpath+pprun+'/SCIENCE_DOMEFLAT*.tarz'.replace('.tarz','')) 
    #if len(fs) > 0: 
    #    os.system('tar xzvf ' + fs[0])
                                                            
    #fs = glob.glob(subpath+pprun+'/SCIENCE_SKYFLAT*.tarz'.replace('.tarz',''))
    #fs = glob.glob(subpath+pprun+'/SCIENCE_SKYFLAT*.tarz')
    #if len(fs) > 0: 
    #    os.system('tar xzvf ' + fs[0])


    #return exposures, LENGTH1, LENGTH2 

def match_simple(SUPA,FLAT_TYPE):

    dict = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['cluster'])
    search_params.update(dict)

    ROTATION = str(search_params['ROTATION']) #exposures[exposure]['keywords']['ROTATION']

    import os
    starcat ='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/PHOTOMETRY/sdssstar%(ROTATION)s.cat' % {'ROTATION':ROTATION,'cluster':search_params['cluster']}
    galaxycat ='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/PHOTOMETRY/sdssgalaxy%(ROTATION)s.cat' % {'ROTATION':ROTATION,'cluster':search_params['cluster']}

    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':search_params['cluster']}
    illum_path='/nfs/slac/g/ki/ki05/anja/SUBARU/ILLUMINATION/' % {'cluster':search_params['cluster']}
    #os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/') 
    os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/STAR/') 
    os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/GALAXY/') 
    from glob import glob

    print starcat

    for type,cat in [['star',starcat],['galaxy',galaxycat]]:
        catalog = search_params['pasted_cat'] #exposures[exposure]['pasted_cat']
        ramin,ramax, decmin, decmax = coordinate_limits(catalog)    
        limits = {'ramin':ramin-0.2,'ramax':ramax+0.2,'decmin':decmin-0.2,'decmax':decmax+0.2}
        print ramin,ramax, decmin, decmax
        if len(glob(cat)) == 0:                                      
            #os.system('rm ' + cat)
            image = search_params['files'][0]
            print image
            import retrieve_test
            retrieve_test.run(image,cat,type,limits)

        filter = search_params['filter'] #exposures[exposure]['keywords']['filter']
        #GABODSID = exposures[exposure]['keywords']['GABODSID']
        OBJECT = search_params['OBJECT'] #exposures[exposure]['keywords']['OBJECT']
        print catalog
        outcat = path + 'PHOTOMETRY/ILLUMINATION/' + type + '/' + 'matched_' + SUPA + '_' + filter + '_' + ROTATION + '_' + type + '.cat'               
        outcat_dir = path + 'PHOTOMETRY/ILLUMINATION/' + type + '/' + ROTATION + '/' + OBJECT + '/'
        os.system('mkdir -p ' + outcat_dir)
        file = 'matched_' + SUPA + '.cat'               
        linkdir = illum_path + '/' + filter + '/' + ROTATION + '/' + OBJECT + '/'              
        #outcatlink = linkdir + 'matched_' + exposure + '_' + cluster + '_' + GABODSID + '.cat' 
        outcatlink = linkdir + 'matched_' + SUPA + '_' + search_params['cluster'] + '_' + type + '.cat' 
        os.system('mkdir -p ' + linkdir)
        os.system('rm ' + outcat)
        command = 'match_simple.sh ' + catalog + ' ' + cat + ' ' + outcat
        print command
        os.system(command)

        os.system('rm ' + outcatlink)
        command = 'ln -s ' + outcat + ' ' + outcatlink
        print command
        os.system(command)

        save_exposure({'matched_cat_' + type:outcat},SUPA,FLAT_TYPE)

        print type, 'TYPE!'
        print outcat, type
        #exposures[exposure]['matched_cat_' + type] = outcat

    #return exposures

def phot(SUPA,FLAT_TYPE): 

    dict = get_files(SUPA,FLAT_TYPE)
    print dict.keys()
    search_params = initialize(dict['filter'],dict['cluster'])
    search_params.update(dict)

    filter = dict['filter']

    import utilities
    info = {'B':{'filter':'g','color1':'gmr','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0},\
        'W-J-B':{'filter':'g','color1':'gmr','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0},\
        'W-J-V':{'filter':'g','color1':'gmr','color2':'rmi','EXTCOEFF':-0.1202,'COLCOEFF':0.0},\
        'W-C-RC':{'filter':'r','color1':'rmi','color2':'gmr','EXTCOEFF':-0.0925,'COLCOEFF':0.0},\
        'W-C-IC':{'filter':'i','color1':'imz','color2':'rmi','EXTCOEFF':-0.02728,'COLCOEFF':0.0},\
        'W-S-Z+':{'filter':'z','color1':'imz','color2':'rmi','EXTCOEFF':0.0,'COLCOEFF':0.0}}
    
    import mk_saturation_plot,os,re
    os.environ['BONN_TARGET'] = search_params['cluster']
    os.environ['INSTRUMENT'] = 'SUBARU'

    stars_0 = []
    stars_90 = []

    ROTATION = dict['ROTATION']
    print ROTATION 
    import os
    ppid = str(os.getppid())
    from glob import glob
    for im_type in ['']: #,'D','S']:
        for type in ['star']: #,'galaxy']:
            file = dict['matched_cat_' + type]
            print file
            print file
            if type == 'galaxy':
                mag='MAG_AUTO' + im_type      
                magerr='MAGERR_AUTO' + im_type
                class_star = "<0.9"
            if type == 'star':
                mag='MAG_APER2' + im_type      
                magerr='MAGERR_APER2' + im_type
                class_star = ">0.9" 
                                                                                                                                                                                                                                                                                                          
            print 'filter', filter
            os.environ['BONN_FILTER'] = filter 
            filt = re.split('_',filter)[0]
            d = info[filt]
            print file
            utilities.run('ldacfilter -i ' +  file + ' -o ' + search_params['TEMPDIR'] + 'good.stars' + ' -t PSSC\
                        -c "(Flag!=-99);"',['' + search_params['TEMPDIR'] + 'good.stars'])




            utilities.run('ldacfilter -i ' + search_params['TEMPDIR'] + 'good.stars -o ' + search_params['TEMPDIR'] + 'good.colors -t PSSC\
                -c "((((SEx_' + mag + '!=0 AND ' + d['color1'] + '<900) AND ' + d['color1'] + '!=0) AND ' + d['color1'] + '>-900) AND ' + d['color1'] + '!=0);"',['' + search_params['TEMPDIR'] + 'good.colors'])
            print '' + search_params['TEMPDIR'] + 'good.colors'
            utilities.run('ldaccalc -i ' + search_params['TEMPDIR'] + 'good.colors -t PSSC -c "(' + d['filter'] + 'mag - SEx_' + mag + ');"  -k FLOAT -n magdiff "" -o ' + search_params['TEMPDIR'] + 'all.diffA.cat' ,[search_params['TEMPDIR'] + 'all.diffA.cat'] )

            median = get_median('' + search_params['TEMPDIR'] + 'all.diffA.cat','magdiff')
            utilities.run('ldacfilter -i ' + search_params['TEMPDIR'] + 'all.diffA.cat -o ' + search_params['TEMPDIR'] + 'all.diffB.cat -t PSSC\
                -c "((magdiff > ' + str(median -1.25) + ') AND (magdiff < ' + str(median + 1.25) + '));"',['' + search_params['TEMPDIR'] + 'good.colors'])
            utilities.run('ldaccalc -i ' + search_params['TEMPDIR'] + 'all.diffB.cat -t PSSC -c "(SEx_MaxVal + SEx_BackGr);"  -k FLOAT -n MaxVal "" -o ' + search_params['TEMPDIR'] + 'all.diff.cat' ,['' + search_params['TEMPDIR'] + 'all.diff.cat'] )
            command = 'ldactoasc -b -q -i ' + search_params['TEMPDIR'] + 'all.diff.cat -t PSSC -k SEx_' + mag + ' ' + d['filter'] + 'mag SEx_FLUX_RADIUS ' + im_type + ' SEx_CLASS_STAR' + im_type + ' ' + d['filter'] + 'err ' + d['color1'] + ' MaxVal > ' + search_params['TEMPDIR'] + 'mk_sat_all'
            #print command
            #raw_input()
            utilities.run(command,['' + search_params['TEMPDIR'] + 'mk_sat_all'] )
            import commands
            length = commands.getoutput('wc -l ' + search_params['TEMPDIR'] + 'mk_sat_all')
            print 'TOTAL # of STARS:', length
            cuts_to_make = ['MaxVal>27500.0','Clean!=1','SEx_IMAFLAGS_ISO'+im_type + '!=0','SEx_CLASS_STAR'+im_type+ class_star,'SEx_Flag'+im_type+'!=0',]
            files = ['' + search_params['TEMPDIR'] + 'mk_sat_all']
            titles = ['raw']
            for cut in cuts_to_make:
                #print 'making cut:', cut
                cut_name = cut.replace('>','').replace('<','')
                os.system('rm ' + cut_name)
                command = 'ldacfilter -i ' + search_params['TEMPDIR'] + 'all.diff.cat -o ' + search_params['TEMPDIR'] + '' + cut_name + ' -t PSSC\
                       -c "(' + cut + ');"'
                utilities.run(command,['' + search_params['TEMPDIR'] + '' + cut_name])
                import glob
                #print len(glob.glob('' + search_params['TEMPDIR'] + '' + cut_name)), glob.glob('' + search_params['TEMPDIR'] + '' + cut_name)
                if len(glob.glob('' + search_params['TEMPDIR'] + '' + cut_name)) > 0:
                    utilities.run('ldactoasc -b -q -i ' + search_params['TEMPDIR'] + '' + cut_name + '  -t PSSC\
                        -k SEx_' + mag + ' ' + d['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + d['filter'] + 'err ' + d['color1'] + ' > ' + search_params['TEMPDIR'] + '' + cut_name + '.cat',['' + search_params['TEMPDIR'] + '' + cut_name + '.cat'])

                    length = commands.getoutput('wc -l ' + search_params['TEMPDIR'] + '' + cut_name + '.cat')
                    print 'TOTAL # of STARS CUT:', length
                    titles.append(cut_name)
                    files.append('' + search_params['TEMPDIR'] + '' + cut_name + '.cat')
                    #run('ldactoasc -b -q -i cutout1.' + ppid + '  -t PSSC\
                    #        -k Ra Dec > ' + search_params['TEMPDIR'] + '' + outfile,['' + search_params['TEMPDIR'] + '' + outfile])
                    #run('mkreg.pl -c -rad 8 -xcol 0 -ycol 1 -wcs -colour ' + color + ' ' + search_params['TEMPDIR'] + '' + outfile)




            utilities.run('ldacfilter -i ' + search_params['TEMPDIR'] + 'all.diff.cat -o ' + search_params['TEMPDIR'] + 'good.stars -t PSSC\
                    -c "(MaxVal<27500 AND SEx_IMAFLAGS_ISO'+im_type+'=0);"',['' + search_params['TEMPDIR'] + 'good.stars'])

                  #-c "((MaxVal<27500 AND SEx_CLASS_STAR'+im_type+class_star + ') AND SEx_IMAFLAGS_ISO'+im_type+'=0);"',['' + search_params['TEMPDIR'] + 'good.stars'])

                  #-c "(MaxVal<27500 AND SEx_IMAFLAGS_ISO'+im_type+'=0);"',['' + search_params['TEMPDIR'] + 'good.stars' + ppid])
            
            utilities.run('ldactoasc -b -q -i ' + search_params['TEMPDIR'] + 'good.stars  -t PSSC\
                    -k SEx_' + mag + ' ' + d['filter'] + 'mag SEx_FLUX_RADIUS' + im_type + ' SEx_CLASS_STAR'+im_type+' ' + d['filter'] + 'err ' + d['color1'] + ' > ' + search_params['TEMPDIR'] + 'mk_sat',['' + search_params['TEMPDIR'] + 'mk_sat'])
                              
            
            if len(glob.glob('' + search_params['TEMPDIR'] + 'mk_sat')) > 0:
                files.append('' + search_params['TEMPDIR'] + 'mk_sat')
                titles.append('filtered')
            print files, titles
            mk_saturation_plot.mk_saturation_all(files,titles,filter)
            raw_input()
            #cutout('' + search_params['TEMPDIR'] + 'good.stars' + ppid,mag)
          
            print mag


            val = raw_input("Look at the saturation plot?")
            if len(val)>0:
                if val[0] == 'y' or val[0] == 'Y':
                    mk_saturation_plot.mk_saturation(search_params['TEMPDIR'] + '/mk_sat',filter)
                                                                                                                                                                                                                       
            val = raw_input("Make a box?")
            if len(val)>0:
                if val[0] == 'y' or val[0] == 'Y':
                    mk_saturation_plot.use_box(filter)
                    lower_mag,upper_mag,lower_diff,upper_diff = re.split('\s+',open('box' + filter,'r').readlines()[0])
            
                    utilities.run('ldacfilter -i ' + search_params['TEMPDIR'] + '/good.stars -t PSSC\
                                -c "(((SEx_' + mag + '>' + lower_mag + ') AND (SEx_' + mag + '<' + upper_mag + ')) AND (magdiff>' + lower_diff + ')) AND (magdiff<' + upper_diff + ');"\
                                -o ' + search_params['TEMPDIR'] + '/filt.mag.new.cat',[search_params['TEMPDIR'] + '/filt.mag.new.cat'])

                    raw_input()
                    os.system('mv ' + search_params['TEMPDIR'] + '/filt.mag.new.cat ' + search_params['TEMPDIR'] + '/good.stars')
                                                                                                                                                                                                                                                                                                          
            #val = [] 
            #val = raw_input("Look at the saturation plot?")
            #if len(val)>0:
            #    if val[0] == 'y' or val[0] == 'Y':
            #        mk_saturation_plot.mk_saturation('' + search_params['TEMPDIR'] + 'mk_sat' + ppid,filter)
                    # make stellar saturation plot                              
                                                                                                                                                                                                                                                                                                          
            #lower_mag,upper_mag,lower_diff,upper_diff = re.split('\s+',open('box' + filter,'r').readlines()[0])
                                                                                                                                                                                                                                                                                                          
            lower_mag = str(10)
            upper_mag = str(14.0)
            lower_diff = str(5)
            upper_diff = str(9)
            if type == 'star': 
                lower_mag = str(13.2)
             
            utilities.run('ldactoasc -b -q -i ' + search_params['TEMPDIR'] + 'good.stars -t PSSC -k SEx_Xpos_ABS SEx_Ypos_ABS > ' + search_params['TEMPDIR'] + 'positions',[search_params['TEMPDIR'] + 'positions'] )
            
            utilities.run('ldacaddkey -i ' + search_params['TEMPDIR'] + 'good.stars -o ' + search_params['TEMPDIR'] + 'filt.airmass.cat -t PSSC -k AIRMASS 0.0 FLOAT "" ',[search_params['TEMPDIR'] + 'filt.airmass.cat']  )
                                                                                                                                                                                                                                                                                                          
            utilities.run('ldacfilter -i ' + search_params['TEMPDIR'] + 'filt.airmass.cat -o ' + search_params['TEMPDIR'] + 'filt.crit.cat -t PSSC\
              -c "((magdiff>-900) AND magdiff<900) AND SEx_' + mag + '!=0) ;"',['' + search_params['TEMPDIR'] + 'filt.crit.cat'])
            utilities.run('ldacfilter -i ' + search_params['TEMPDIR'] + 'filt.crit.cat -o ' + search_params['TEMPDIR'] + 'all.colors.cat -t PSSC\
                    -c "(((' + d['color1'] + '<900 AND ' + d['color2'] + '<900) AND ' + d['color1'] + '>-900) AND ' + d['color2'] + '>-900);"',['' + search_params['TEMPDIR'] + 'all.colors.cat'])
            
            utilities.run('ldactoasc -b -q -i ' + search_params['TEMPDIR'] + 'all.colors.cat -t PSSC -k SEx_' + mag + ' ' + d['filter'] + 'mag ' + d['color1'] + ' ' + d['color2'] + ' AIRMASS SEx_' + magerr + ' ' + d['filter'] + 'err SEx_Xpos_ABS SEx_Ypos_ABS > ' + search_params['TEMPDIR'] + 'input.asc' ,['' + search_params['TEMPDIR'] + 'input.asc'] )
                                                                                                                                                                                                                                                                                                          
            import photo_abs_new                
            
            good = photo_abs_new.run_through('illumination',infile='' + search_params['TEMPDIR'] + 'input.asc',output='' + search_params['TEMPDIR'] + 'photo_res',extcoeff=d['color1'],sigmareject=6,step='STEP_1',bandcomp=d['filter'],color1which=d['color1'],color2which=d['color2'])
            
            import astropy.io.fits as pyfits
            cols = [] 
            for key in ['corr_data','color1_good','color2_good','magErr_good','X_good','Y_good','airmass_good']: 
                cols.append(pyfits.Column(name=key, format='E',array=good[key]))
            hdu = pyfits.PrimaryHDU()
            hdulist = pyfits.HDUList([hdu])
            print cols
            tbhu = pyfits.BinTableHDU.from_columns(cols)
            hdulist.append(tbhu)
            hdulist[1].header['EXTNAME']='STDTAB'
                                                                                                                                                                                                                                                                                                          
            path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':search_params['cluster']}
            outcat = path + 'PHOTOMETRY/ILLUMINATION/fit_' + im_type + '_' + search_params['SUPA'] + '_' +  type + '.cat'                
            os.system('rm ' + outcat)
            hdulist.writeto(outcat)
                                                                                                                                                                                                                                                                                                          
            save_exposure({'fit_cat_' + im_type + '_' + type: outcat,'airmass_add':'yes'},SUPA,FLAT_TYPE)
            save_fit(good['fits'],im_type,type,SUPA,FLAT_TYPE)



def nightrun():
    import MySQLdb, sys, os, re, time, utilities, pyfits
    from copy import copy
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()

    keystop = ['PPRUN']
    list = reduce(lambda x,y: x + ',' + y, keystop)
    command="SELECT " + list + " from illumination_db where zp_star_ is not null and PPRUN!='KEY_N/A' GROUP BY PPRUN"
    print command
    c.execute(command)
    results=c.fetchall()
    db_keys = describe_db(c)
    h = []
    for line in results: 
        dtop = {}
        for i in range(len(keystop)):
            dtop[keystop[i]] = line[i]

        directory = 'run_' + dtop['PPRUN'] 

        os.system('mkdir ' +  os.environ['sne'] + '/plots/' + directory )
        os.system('rm ' + os.environ['sne'] + '/plots/' + directory + '/*')

        keys = ['cluster','ROTATION']
        list = reduce(lambda x,y: x + ',' + y, keys)
        command="SELECT " + list + " from illumination_db where zp_star_ is not null and PPRUN='" + dtop['PPRUN'] + "' GROUP BY cluster,ROTATION"
        print command
        c.execute(command)
        results=c.fetchall()
        db_keys = describe_db(c)
        h = []
        for line in results: 
            d = {}
            for i in range(len(keys)):
                d[keys[i]] = line[i]
                                                                                                                                                                                                                                                             
            if 1:
                #print d
                if 1:
                    crit = reduce(lambda x,y: x + ' AND ' + y,[str(y) + "='" + str(d[y]) + "'" for y in keys]) 
                    file = directory + '/' + reduce(lambda x,y: x + 'AND' + y,[str(y)[0:4] + "_" + str(d[y])  for y in keys]) 
                    #print crit
                
                    command = "SELECT * from illumination_db where zp_star_ is not null and " + crit
                                                                                                                                                                                                                                                             
                    #print command
                    c.execute(command)
                    results = c.fetchall()
                    #print results
                    fit_files = [] 
                    for j in range(len(results)):
                        dict = {} 
                        for i in range(len(results[j])):  
                            dict[db_keys[i]] = results[j][i]
                        #print dict['SUPA'], dict['cluster'], dict['pasted_cat'], dict['matched_cat_star']
                        fit_files.append(dict['fit_cat__star'])
                                            
                    #print fit_files
                    dict = get_files(dict['SUPA'],dict['FLAT_TYPE'])
                    #print dict.keys()
                    search_params = initialize(dict['filter'],dict['cluster'])
                    search_params.update(dict)
                                               
                    from copy import copy
                    import photo_abs_new
                    reload(photo_abs_new)
                    files = reduce(lambda x,y: x + ' ' + y,fit_files)
                    #print files
                    tempfile = '' + search_params['TEMPDIR'] + 'spit'
                    command = 'ldacpaste -i ' + files + ' -t STDTAB -o ' + tempfile
                    print command
                    utilities.run(command)
                    hdulist = pyfits.open(tempfile)
                    args = {}
                    for column in hdulist["STDTAB"].columns:
                        args[column.name] = hdulist["STDTAB"].data.field(column.name)
                    photo_abs_new.calcDataIllum(file,search_params['LENGTH1'], search_params['LENGTH2'], 1000, args['corr_data'], args['airmass_good'], args['color1_good'], args['color2_good'], args['magErr_good'], args['X_good'], args['Y_good'],rot=0)
            #except: print 'failed'

def auto_print():
    import MySQLdb, sys, os, re, time, utilities, pyfits
    from copy import copy
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()

    keys = ['FILTER','ROTATION']
    list = reduce(lambda x,y: x + ',' + y, keys)
    command="SELECT " + list + " from illumination_db where zp_star_ is not null and PPRUN!='KEY_N/A' and good_stars_star_ > 400 GROUP BY "+list
    print command
    c.execute(command)
    results=c.fetchall()
    db_keys = describe_db(c)
    h = []
    for line in results: 
        d = {}
        for i in range(len(keys)):
            d[keys[i]] = line[i]

        if 1:
            print d
            if 1:
                crit = reduce(lambda x,y: x + ' AND ' + y,[str(y) + "='" + str(d[y]) + "'" for y in keys]) 
                file = 'filt_' + reduce(lambda x,y: x + 'AND' + y,[str(y)[0:4] + "_" + str(d[y])  for y in keys]) 
                print crit
            
                command = "SELECT * from illumination_db where zp_star_ is not null and " + crit

                print command
                c.execute(command)
                results = c.fetchall()
                print results
                fit_files = [] 
                for j in range(len(results)):
                    dict = {} 
                    for i in range(len(results[j])):  
                        dict[db_keys[i]] = results[j][i]
                    print dict['SUPA'], dict['cluster'], dict['pasted_cat'], dict['matched_cat_star']
                    fit_files.append(dict['fit_cat__star'])
                                        
                print fit_files
                dict = get_files(dict['SUPA'],dict['FLAT_TYPE'])
                print dict.keys()
                search_params = initialize(dict['filter'],dict['cluster'])
                search_params.update(dict)
                                           
                from copy import copy
                import photo_abs_new
                reload(photo_abs_new)
                files = reduce(lambda x,y: x + ' ' + y,fit_files)
                print files
                tempfile = '' + search_params['TEMPDIR'] + 'spit'
                command = 'ldacpaste -i ' + files + ' -t STDTAB -o ' + tempfile
                print command
                utilities.run(command)
                hdulist = pyfits.open(tempfile)
                args = {}
                for column in hdulist["STDTAB"].columns:
                    args[column.name] = hdulist["STDTAB"].data.field(column.name)
                photo_abs_new.calcDataIllum(file,search_params['LENGTH1'], search_params['LENGTH2'], 1000, args['corr_data'], args['airmass_good'], args['color1_good'], args['color2_good'], args['magErr_good'], args['X_good'], args['Y_good'],rot=0)
            #except: print 'failed'

def describe_db(c,db='illumination_db'):
    command = "DESCRIBE illumination_db"     
    print command
    c.execute(command)
    results = c.fetchall()
    keys = []
    for line in results:
        keys.append(line[0])
    return keys    


def printer():
    import MySQLdb, sys, os, re, time, utilities, pyfits
    from copy import copy
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()
       
    if 1: #for set in [{'cluster':'HDFN', 'filters':['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']},{'cluster':'MACS2243-09', 'filters':['W-J-V','W-C-RC','W-C-IC','W-S-Z+']},{'cluster':'A2219', 'filters':['W-J-B','W-J-V','W-C-RC']}]:
        #cluster = set['cluster']
        if 1: #for filter in set['filters']:
            if 1: #try:
                print keys
                cluster = 'HDFN'                        
                filter = 'W-C-ICSF'
                ROTATION = 1
                command = "select * from illumination_db where cluster='" + cluster + "' and filter='" + filter + "' and fit_cat_galaxy is not null and crfixed='third' and good_stars_star is not null and good_stars_star>10 and ROTATION=" + str(ROTATION)

                command = "select * from illumination_db where SUPA='SUPA0011022' and zp_err_galaxy_D is not null"
                #command = "select * from illumination_db where cluster='" + cluster + "' and filter='" + filter + "' and fit_cat_galaxy is not null and crfixed='third' and ROTATION=" + str(ROTATION) + ' and good_stars_star is not null and good_stars_star>10'

                command = "SELECT * from illumination_db where zp_star_ is not null and ROTATION='0'" # where cluster='HDFN' and filter='W-J-V' and ROTATION=0"



                print command
                c.execute(command)
                results = c.fetchall()
                fit_files = [] 
                for j in range(len(results)):
                    dict = {} 
                    for i in range(len(results[j])):  
                        dict[keys[i]] = results[j][i]
                    print dict['SUPA'], dict['cluster'], dict['pasted_cat'], dict['matched_cat_star']
                    fit_files.append(dict['fit_cat__star'])
                                        
                print fit_files
                dict = get_files(dict['SUPA'],dict['FLAT_TYPE'])
                print dict.keys()
                search_params = initialize(dict['filter'],dict['cluster'])
                search_params.update(dict)
                                           
                from copy import copy
                import photo_abs_new
                reload(photo_abs_new)
                files = reduce(lambda x,y: x + ' ' + y,fit_files)
                print files
                tempfile = '' + search_params['TEMPDIR'] + 'spit'
                command = 'ldacpaste -i ' + files + ' -t STDTAB -o ' + tempfile
                print command
                utilities.run(command)
                hdulist = pyfits.open(tempfile)
                args = {}
                for column in hdulist["STDTAB"].columns:
                    args[column.name] = hdulist["STDTAB"].data.field(column.name)
                file = cluster + '_' + filter + '_' + str(ROTATION)
                file = raw_input('filename?')
                photo_abs_new.calcDataIllum(file,search_params['LENGTH1'], search_params['LENGTH2'], 1000, args['corr_data'], args['airmass_good'], args['color1_good'], args['color2_good'], args['magErr_good'], args['X_good'], args['Y_good'],rot=0)
            #except: print 'failed'

#filter = 'W-C-IC'
import pickle

#filters = ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']

#for filter in filters:
#    exposures_zero = {} 
#    exposures_one = {} 
#    print '$$$$$'
#    print 'separating into different camera rotations'
#    for exposure in exposures.keys(): 
#        print exposure,exposures[exposure]['keywords']['ROTATION']
#        if int(exposures[exposure]['keywords']['ROTATION']) == 1:
#            exposures_one[exposure] = exposures[exposure]
#        if int(exposures[exposure]['keywords']['ROTATION']) == 0:
#            exposures_zero[exposure] = exposures[exposure]
if 0:
    reopen = 0
    save = 0
    if reopen:
        f = open('' + search_params['TEMPDIR'] + 'tmppickle' + cluster + filter,'r')
        m = pickle.Unpickler(f)
        exposures, LENGTH1, LENGTH2 = m.load()
    
        print image.latest
    
    if 1: images = gather_exposures(filter,cluster)
    
    print images
    
    ''' strip down exposure list '''
    for key in exposures.keys():
        print exposures[key]['images']
    
    for image in exposures:
        if 1: image.find_seeing(exposures) # save seeing info?
        if 1: image.sextract(exposures)
        if 1: image.match_simple(exposures,cluster)
        if 1: image.phot(exposures,filter,type,LENGTH1,LENGTH2)
    
    if save:
        f = open('' + search_params['TEMPDIR'] + 'tmppickle' + cluster + filter,'w')
        m = pickle.Pickler(f)
        pickle.dump([exposures,LENGTH1,LENGTH2],m)
        f.close()


def match_cluster():

    import MySQLdb, sys, os, re, time, utilities, pyfits
    from copy import copy
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()
    db_keys = describe_db(c)
    
    keystop = ['PPRUN','ROTATION','cluster']
    list = reduce(lambda x,y: x + ',' + y, keystop)
    command="SELECT " + list + " from illumination_db where zp_star_ is not null and PPRUN='2003-07-27_W-J-B' and OBJECT='MJ2129' GROUP BY cluster,ROTATION"
    print command
    c.execute(command)
    results=c.fetchall()
    for line in results: 
        dtop = {}
        for i in range(len(keystop)):
            dtop[keystop[i]] = str(line[i])
        
        keys = ['SUPA','cluster','ROTATION','PPRUN','pasted_cat']
        list = reduce(lambda x,y: x + ',' + y, keys)
        command="SELECT " + list + " from illumination_db where zp_star_ is not null and cluster='"+dtop['cluster'] + "' and PPRUN='" + dtop['PPRUN'] + "'"#+ "' GROUP BY cluster,ROTATION"
        print command
        c.execute(command)
        results=c.fetchall()
        db_keys = describe_db(c)
        field = []
        info = []
        for line in results: 
            d = {}
            for i in range(len(keys)):
                d[keys[i]] = str(line[i])


            key = str(int(float(d['ROTATION']))) + '#' + d['SUPA'] + '#'
            field.append({'key':key,'pasted_cat':d['pasted_cat']})
            info.append([d['ROTATION'],d['SUPA']])
        print field
        a = raw_input('match?')
        if a[0] == 'y':
            match_many([[x['pasted_cat'],x['key']] for x in field])
        print info
        raw_input()
        script = reduce(lambda x,y: x + ' ' + y,[x['pasted_cat'] + ' ' + x['key'] for x in field])
        print '\n\nDONE'
        raw_input()

def make_ssc_config(list):

    ofile = '/tmp/tmp.cat'
    out = open('/tmp/tmp.ssc','w')
    import os, string, re

    keys = []
    i = -1 
    for file_name,prefix in list:
        i += 1
        print file_name
        os.system('ldacdesc -t OBJECTS -i ' + file_name + ' > ' + ofile)
        file = open(ofile,'r').readlines()
        for line in file:
        	if string.find(line,"Key name") != -1:
        		red = re.split('\.+',line)
        		key = red[1].replace(' ','').replace('\n','')
			out_key = prefix + key
        		out.write("COL_NAME = " + out_key + '\nCOL_INPUT = ' + key + '\nCOL_MERGE = AVE_REG\nCOL_CHAN = ' + str(i) + "\n#\n")
        		#print key
			keys.append(key)

    out.close()

def make_ssc_config_few(list):

    ofile = '/tmp/tmp.cat'
    out = open('/tmp/tmp.ssc','w')
    import os, string, re

    key_list = ['MAG_APER2','MAGERR_APER2','Xpos_ABS','Ypos_ABS','CLASS_STAR','MaxVal','BackGr']
    keys = []
    i = -1 
    for file_name,prefix in list:
        i += 1
        print file_name
        os.system('ldacdesc -t OBJECTS -i ' + file_name + ' > ' + ofile)
        file = open(ofile,'r').readlines()
        for line in file:
            if string.find(line,"Key name") != -1 :
                red = re.split('\.+',line)
                key = red[1].replace(' ','').replace('\n','')
                out_key = prefix + key
                if reduce(lambda x,y: x+ y, [string.find(out_key,k)!=-1 for k in key_list]):
        		    out.write("COL_NAME = " + out_key + '\nCOL_INPUT = ' + key + '\nCOL_MERGE = AVE_REG\nCOL_CHAN = ' + str(i) + "\n#\n")
        		#print key
                keys.append(key)

    out.close()


def make_ssc_config_colors(list):

    ofile = '/tmp/tmp.cat'
    out = open('/tmp/tmp.ssc','w')
    import os, string, re

    keys = []
    i = -1 
    for file_name,prefix in list:
        i += 1
        print file_name
        os.system('ldacdesc -t OBJECTS -i ' + file_name + ' > ' + ofile)
        file = open(ofile,'r').readlines()
        for line in file:
        	if string.find(line,"Key name") != -1:
        		red = re.split('\.+',line)
        		key = red[1].replace(' ','').replace('\n','')
			out_key = key + '_' + prefix
        		out.write("COL_NAME = " + out_key + '\nCOL_INPUT = ' + key + '\nCOL_MERGE = AVE_REG\nCOL_CHAN = ' + str(i) + "\n#\n")
        		#print key
			keys.append(key)

    out.close()

def threesec():
    list = [['/nfs/slac/g/ki/ki05/anja/SUBARU/MACS0417-11/PHOTOMETRY/ILLUMINATION/pasted_SUPA0105807_W-C-RC_2009-01-23_CALIB_0.0.cat','W-C-RC'],['/nfs/slac/g/ki/ki05/anja/SUBARU/MACS0417-11/PHOTOMETRY/ILLUMINATION/pasted_SUPA0105787_W-J-V_2009-01-23_CALIB_0.0.cat','W-J-V'],['/nfs/slac/g/ki/ki05/anja/SUBARU/MACS0417-11/PHOTOMETRY/ILLUMINATION/pasted_SUPA0050786_W-C-IC_2006-12-21_CALIB_0.0.cat','W-C-IC']]
    match_many(list)

def match_many(list):
    #make_ssc_config_colors(list) 
    make_ssc_config_few(list) 

    import os

    files = []
    for file,prefix in list:
        print file
        command = 'ldacaddkey -i %(inputcat)s -t OBJECTS -o %(outputcat)s -k A_WCS_assoc 0.0003 FLOAT "" \
                                        B_WCS_assoc 0.0003 FLOAT "" \
                                        Theta_assoc 0.0 FLOAT "" \
                                        Flag_assoc 0 SHORT "" ' % {'inputcat':file,'outputcat':file + '.assoc1'}
        os.system(command)
    
        #command = 'ldacrenkey -i %(inputcat)s -o %(outputcat)s -k ALPHA_J2000 Ra DELTA_J2000 Dec' % {'inputcat':file + '.assoc1','outputcat':file+'.assoc2'} 
        #os.system(command)
        files.append(file+'.assoc1')

    files_input = reduce(lambda x,y:x + ' ' + y,files)
    files_output = reduce(lambda x,y:x + ' ' + y,[z+'.assd' for z in files])

    print files
    print files_input, files_output
    
    command = 'associate -i %(inputcats)s -o %(outputcats)s -t OBJECTS -c ./photconf/fullphotom.alpha.associate' % {'inputcats':files_input,'outputcats':files_output}
    print command
    os.system(command)

    outputcat = '/tmp/final.cat'
    command = 'make_ssc -i %(inputcats)s \
    		-o %(outputcat)s\
    		-t OBJECTS -c /tmp/tmp.ssc ' % {'inputcats':files_output,'outputcat':outputcat}
    os.system(command)

def match_inside(SUPA1,SUPA2,FLAT_TYPE):

    dict1 = get_files(SUPA1,FLAT_TYPE)
    search_params1 = initialize(dict1['filter'],dict1['cluster'])
    search_params1.update(dict1)

    dict2 = get_files(SUPA2,FLAT_TYPE)
    search_params2 = initialize(dict2['filter'],dict2['cluster'])
    search_params2.update(dict2)

    import os
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':search_params1['cluster']}
    illum_path='/nfs/slac/g/ki/ki05/anja/SUBARU/ILLUMINATION/' % {'cluster':search_params1['cluster']}
    #os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/') 
    os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/SELF/') 
    from glob import glob


    catalog1 = search_params1['pasted_cat']
    catalog2 = search_params2['pasted_cat']


    #os.system('ldacrentab -i ' + catalog2 + ' -t OBJECTS STDTAB -o ' + catalog2.replace('cat','std.cat'))


    filter = search_params1['filter'] #exposures[exposure]['keywords']['filter']
    OBJECT = search_params1['OBJECT'] #exposures[exposure]['keywords']['OBJECT']
    outcat = path + 'PHOTOMETRY/ILLUMINATION/SELF/matched_' + SUPA1 + '_' + filter + '_' + '_self.cat'               
    file = 'matched_' + SUPA1 + '.cat'               
    os.system('rm ' + outcat)
    command = 'match_simple_cats.sh ' + catalog1 + ' ' + catalog2 + ' ' + outcat
    print command
    os.system(command)

    save_exposure({'matched_cat_self':outcat},SUPA1,FLAT_TYPE)

    print outcat


def getTableInfo():
    import astropy.io.fits as pyfits, sys, os, re, string, copy , string
    
    p = pyfits.open('/tmp/final.cat')
    tbdata = p[1].data
    types = []
   
    ROTS = {}
    KEYS = {} 
    for column in p[1].columns: 
        if string.find(column.name,'#') != -1:       
            print column                                           
            res = re.split('\#',column.name)
            ROT = res[0]
            IMAGE = res[1]
            KEY = res[2]
                                                                  
            if not ROTS.has_key(ROT):
                ROTS[ROT] = []
            if not len(filter(lambda x:x==IMAGE,ROTS[ROT])):
                ROTS[ROT].append(IMAGE)
    return ROTS



def diffCalcNew():
    import astropy.io.fits as pyfits, sys, os, re, string, copy , string
    
    p = pyfits.open('/tmp/final.cat')
    tbdata = p[1].data
    types = []
   
    ROTS = {}
    KEYS = {} 
    for column in p[1].columns: 
        if string.find(column.name,'#') != -1:       
            print column                                           
            res = re.split('\#',column.name)
            ROT = res[0]
            IMAGE = res[1]
            KEY = res[2]
                                                                  
            if not ROTS.has_key(ROT):
                ROTS[ROT] = []
            if not len(filter(lambda x:x==IMAGE,ROTS[ROT])):
                ROTS[ROT].append(IMAGE)

        
    print ROTS

    raw_input()

   
    #good = 0
    #for i in range(len(tbdata)):
    #    array = []
    #    for y in ROTS[ROT]:
    #        array += [tbdata.field(ROT+'#'+y+'#CLASS_STAR')[i] for y in ROTS[ROT]]
    #    array.sort()
    #    if array[-1]>0.9 and array[-2]>0.9: 
    #        good += 1 
    #print good, len(tbdata)
    #raw_input()

def selectGoodStars(EXPS):
    ''' the top two most star-like objects have CLASS_STAR>0.9 and, for each rotation, their magnitudes differ by less than 0.01 '''
    import astropy.io.fits as pyfits, sys, os, re, string, copy , string, scipy
    
    p = pyfits.open('/tmp/final.cat')
    table = p[1].data
    star_good = [] #= scipy.zeros(len(table)) 
    supas = []

    for i in range(len(table)):
        mags_ok = False 
        class_star_array = []
        include_star = []
        name = []
        for ROT in EXPS.keys():
            mags_array = []
            class_star_array += [table.field(ROT+'#'+y+'#CLASS_STAR')[i] for y in EXPS[ROT]]
            mags_array += [table.field(ROT+'#'+y+'#MAG_APER2')[i] for y in EXPS[ROT]]
            include_star += [((table.field(ROT+'#'+y+'#MaxVal')[i] + table.field(ROT+'#'+y+'#BackGr')[i]) < 27500 and table.field(ROT+'#'+y+'#CLASS_STAR')[i] > 0.5) and table.field(ROT+'#'+y+'#MAG_APER2')[i] < 40 for y in EXPS[ROT]]
            name += [{'name':EXPS[ROT][z],'rotation':ROT} for z in range(len(EXPS[ROT]))]
            mags_array.sort()
            if len(mags_array) > 1: 
                if abs(mags_array[0] - mags_array[1]) < 0.2:
                    mags_ok = True 
        class_star_array.sort()
        if mags_ok: 
            file_list=[]
            for j in range(len(include_star)): 
                if include_star[j]: 
                    file_list.append(name[j])
            if len(file_list) > 1:
                star_good.append(i)                                                            
                supas.append({'table index':i,'supa files':file_list})                        
                #print len(supas)
        if i%100==0: print i
    return star_good, supas

def diffCalc(SUPA1,FLAT_TYPE):
    dict = get_files(SUPA1,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['cluster'])
    search_params.update(dict)

    import astropy.io.fits as pyfits, sys, os, re, string, copy 
    
    print search_params['matched_cat_self']
    p = pyfits.open(search_params['matched_cat_self'])
    tbdata = p[1].data
    mask = tbdata.field('SEx_MaxVal') + tbdata.field('SEx_BackGr') < 27500 
    newtbdata = tbdata[mask]

    print len(newtbdata)

    mask = newtbdata.field('CLASS_STAR') > 0.95 
    newtbdata = newtbdata[mask]

    mask = abs(newtbdata.field('SEx_MAG_APER2') - newtbdata.field('MAG_APER2')) < 0.01 
    new2tbdata = newtbdata[mask]

    print len(new2tbdata)

    data = new2tbdata.field('SEx_MAG_APER2') - new2tbdata.field('MAG_APER2')
    magErr = new2tbdata.field('SEx_MAGERR_APER2')
    X = new2tbdata.field('Xpos_ABS')
    Y = new2tbdata.field('Ypos_ABS')

    file = 'test'

    calcDataIllum(file,search_params['LENGTH1'], search_params['LENGTH2'],data,magErr,X,Y) 

    data_save = []
    magErr_save = []
    X_save = []
    Y_save = []
    for i in range(len(data)):
        data_save.append([new2tbdata.field('SEx_MAG_APER2')[i],new2tbdata.field('MAG_APER2')[i]])
        magErr_save.append([new2tbdata.field('SEx_MAGERR_APER2')[i],new2tbdata.field('MAGERR_APER2')[i]])
        X_save.append([new2tbdata.field('Xpos_ABS')[i],new2tbdata.field('SEx_Xpos_ABS')[i]])
        Y_save.append([new2tbdata.field('Ypos_ABS')[i],new2tbdata.field('SEx_Ypos_ABS')[i]])

    return data_save, magErr_save, X_save, Y_save

def calcDataIllum(file, LENGTH1, LENGTH2, data,magErr, X, Y, rot=0):
    import numpy, math, pyfits, os                                                                              
    from ppgplot   import *

    #print size_x, size_y, bin, size_x/bin

    x = []
    y = []
    z = []
    zerr = []

    from copy import copy
    X_sort = copy(X)
    Y_sort = copy(Y)
    X_sort = numpy.sort(X_sort)
    Y_sort = numpy.sort(Y_sort)

    X_min = X_sort[0]
    Y_min = Y_sort[0]

    X_max = X_sort[-1]
    Y_max = Y_sort[-1]

    X_width = abs(X_max - X_min)
    Y_width = abs(Y_max - Y_min)

    nbin1 =10 
    nbin2 =10 

    LENGTH1 = LENGTH1
    LENGTH2 = LENGTH2

    print LENGTH1, LENGTH2
    #raw_input()

    bin1 = int(LENGTH1/nbin1)
    bin2 = int(LENGTH2/nbin2)
    
    diff_weightsum = -9999*numpy.ones([nbin1,nbin2])
    diff_invvar = -9999*numpy.ones([nbin1,nbin2])

    X_cen = []
    Y_cen = []
    data_cen = []
    zerr_cen = []

    chisq = 0
    for i in range(len(data)):
        if 1: # LENGTH1*0.3 < X[i] < LENGTH1*0.6:
            X_cen.append(X[i])
            Y_cen.append(Y[i])
            data_cen.append(data[i])
            zerr_cen.append(magErr[i])

        x.append(X[i])    
        y.append(Y[i])
        z.append(data[i])
        zerr.append(magErr[i])
        chisq += data[i]**2./magErr[i]**2.

        x_val = int((X[i])/float(bin1))  # + size_x/(2*bin)
        y_val = int((Y[i])/float(bin2))  #+ size_y/(2*bin)
        #print LENGTH1, LENGTH2, x_val, y_val, X[i], Y[i]
        #raw_input()
        #print size_x/bin+1,size_y/bin+1, x_val, y_val, X[i], Y[i]
        err = magErr[i]
        ''' lower limit on error '''
        if err < 0.04: err = 0.04
        weightsum = data[i]/err**2.
        invvar = 1/err**2.
        

        #if 1: #0 <= x_val and x_val < int(nbin1) and y_val >= 0 and y_val < int(nbin2):  #0 < x_val < size_x/bin and 0 < y_val < size_y/bin:
        #print x_val, y_val
        try:
            if diff_weightsum[x_val][y_val] == -9999:      
                diff_weightsum[x_val][y_val] = weightsum
                diff_invvar[x_val][y_val] = invvar 
            else:                 
                diff_weightsum[x_val][y_val] += weightsum 
                diff_invvar[x_val][y_val] += invvar 
        except: print 'fail'

    redchisq = chisq**0.5 / len(data)
    print 'redchisq', redchisq
    #raw_input()

    import Numeric
    x_p = Numeric.array(X_cen)
    y_p = Numeric.array(Y_cen)
    z_p = Numeric.array(data_cen)
    zerr_p = Numeric.array(zerr_cen)
    x.sort()
    y.sort()
    z.sort()



    mean = diff_weightsum/diff_invvar
    print 'mean'
    #print mean
    err = 1/diff_invvar**0.5

    print 'err'
    #print err 

    print 'writing'
    hdu = pyfits.PrimaryHDU(mean)
    pth = '/nfs/slac/g/ki/ki04/pkelly/plots/'
    f = pth + file 
    os.system('rm ' + f +   'diffmap.fits')
    hdu.writeto( f + 'diffmap.fits')      

    hdu = pyfits.PrimaryHDU(err)
    os.system('rm ' + f + 'diffinvar.fits')
    hdu.writeto( f + 'diffinvar.fits')      


    pgbeg(f + 'pos.ps'+"/cps",1,1)
    pgiden()

    #print x_p
    #print z_p 
    #print zerr_p

    #pgswin(x[0],x[-1],z[0],z[-1])

    ### plot positions
    pgpanl(1,1)
    pgswin(x[0],x[-1],y[0],y[-1])
    pgbox()
    pglab('X','Y',file)     # label the plot
    #pgsci(3)
    #pgerrb(6,x_p,z_p,zerr_p)
    pgpt(x_p,y_p,3)

    pgend()

    ### plot residuals
    pgbeg(f + 'diff.ps'+"/cps",1,2)
    pgiden()

    #print x_p
    #print z_p 
    #print zerr_p

    #pgswin(x[0],x[-1],z[0],z[-1])

    pgpanl(1,1)
    pgswin(x[0],x[-1],-0.005,0.005)
    pgbox()
    pglab('X axis','SDSS-SUBARU',file)     # label the plot
    #pgsci(3)
    #pgerrb(6,x_p,z_p,zerr_p)
    pgpt(x_p,z_p,3)

    #pgswin(y[0],y[-1],z[0],z[-1])
    pgpanl(1,2)
    pgswin(y[0],y[-1],-0.005,0.005)

    pgsci(1)
    pgbox()
    pglab('Y axis','SDSS-SUBARU',file)     # label the plot
    #pgsci(3)
    #pgerrb(6,y_p,z_p,zerr_p)
    pgpt(y_p,z_p,3)
    pgsci(1)
  


    #print x_p
    #print z_p 
    #print zerr_p

    pgend()

    return


def make_model(ROTS):
    #polyterms = [['X','X','X'],['X','X','Y'],['X','Y','Y'],['Y','Y','Y'],['X','X'],['X','Y'],['Y','Y'],['X'],['Y']]
    polyterms = [['Xpos_ABS','Xpos_ABS'],['Xpos_ABS','Ypos_ABS'],['Ypos_ABS','Ypos_ABS'],['Xpos_ABS'],['Ypos_ABS']]
    ''' break up parameters into rotation specific and exposure specific (the zeropoints) '''
    model = {'ROT_SPECIFIC':[],'EXP_SPECIFIC':[]} 
    for ROTATION in ROTS.keys():
        for term in polyterms:
            name = reduce(lambda x,y: x + 'T' + y,term)
            model['ROT_SPECIFIC'].append({'name':ROTATION+'#'+name,'rotation':ROTATION,'term':term,'value':0.1})
        for IMAGE in ROTS[ROTATION]: 
            model['EXP_SPECIFIC'].append({'name':IMAGE+'#zp','image':IMAGE,'term':['zp'],'value':0.01})

    fit = {'model':model,'fixed':[],'apply':[]}
    print fit
    return fit

def calc_model(p,X,Y,data,err):    
    for i in range(len(self.smodel)):    
        term = self.smodel[i]
        model += p[i] * reduce(lambda x,y: x * y,[self.dict[z] for z in term]) 
    status = 0
    return([status, (model-y)/err])

class phot_funct:
    def __init__(self,inputmodel,sfixed,EXPS,star_good,sapply=[],zps=0):
        ''' need to take EXPS and make a vector of parameters to pass to the fitting program as well as a dictionary '''
        self.star_good = star_good
        self.inputmodel = inputmodel
        self.allterms = self.inputmodel['ROT_SPECIFIC'] + self.inputmodel['EXP_SPECIFIC']
        self.parstart = [{'value':x['value'],'fixed':0.001} for x in self.allterms] # assign initial values to all parameters
        self.pardict = {}
        for x in range(len(self.allterms)):
            self.pardict[self.allterms[x]['name']] = x
        #self.pardict = [{self.allterms[x]['name']:x} for x in range(len(self.allterms))] # dictionary of parameter indicies for parameter names  
        self.model = [x['term'] for x in self.allterms] # make a list of the form of each term

        print 'HERE'
        print self.allterms


        self.EXPS = EXPS
        #self.p_dict = []
        #self.smodeldict = {}
        #for x in self.sinputmodel:
        #    self.smodeldict[x['name']] = x['term']
        self.sfixed = sfixed    
        self.sapply = sapply
        self.fitvars = {}

    #fa = {"y": data, "err": err, 'X':X, 'Y':Y, 'maxVal':maxVal, 'classStar':classStar}
    def calc_model(self, p, fjac=None, table=None):
        # function you can pass to mpfit
        self.dict = {'zp':1, 'table':table}
        #print p

        redchisqs = []

        rows = len(table)
        print rows
        row_num = 0
        for j in self.star_good:
            row_num += 1
            data = []
            errs = []
            models = []       
            numerators = []
            denominators = []

            for ROT in self.EXPS:
                good_exps = [] 
                for exp in self.EXPS[ROT]:
                    #print exp
                    if table.field(ROT+'#'+exp+'#MaxVal')[j] + table.field(ROT+'#'+exp+'#BackGr')[j] < 27500 and table.field(ROT+'#'+exp+'#CLASS_STAR')[j] > 0.9:
                        good_exps.append(exp)
                    #print good_exps, self.EXPS[ROT]
                    #raw_input()
                                                                                                                 
                #print good_stars, X[j], Y[j], y[j], maxVal[j], classStar[j]
                #raw_input()
                                                                                                                 
                if len(good_exps) > 0:
                    tot = len(good_exps)                                                                        
                    import scipy
                    #models = scipy.zeros(tot) 
                    #numerators = scipy.zeros(tot) 
                    #denominators = scipy.zeros(tot) 
                             
                    for exp in good_exps:                                                            

                        #print self.allterms
                        model_zp_terms = []
                        model_position_terms = []
                        for term in self.allterms:
                            if term.has_key('image'):
                                if term['image'] == exp:
                                    model_zp_terms.append(term)
                            if term.has_key('rotation'):
                                #print term['rotation'], ROT, str(term['rotation']) == str(ROT)
                                if str(term['rotation']) == str(ROT):
                                    model_position_terms.append(term)
                            
                        #print model_zp_terms, model_position_terms


                        model = 0                                                                      
                        ''' add positionally depdendent terms '''
                        for term in model_position_terms:                                           
                            #print table.field(ROT+'#'+exp+'#'+term['term'][0])[j]
                            #print self.pardict[term['name']]
                            model += p[self.pardict[term['name']]] * reduce(lambda x,y: x * y,[table.field(ROT+'#'+exp+'#'+z)[j] for z in term['term']]) 

                        ''' add the zeropoint for that image '''
                        for term in model_zp_terms:                                           
                            #print self.pardict[term['name']]
                            model += p[self.pardict[term['name']]] 

                        data.append(table.field(ROT+'#'+exp+'#MAG_APER2')[j]**2.)
                        errs.append(table.field(ROT+'#'+exp+'#MAGERR_APER2')[j]**2.)
                        models.append(model)
                        numerators.append((model-table.field(ROT+'#'+exp+'#MAG_APER2')[j])/table.field(ROT+'#'+exp+'#MAGERR_APER2')[j]**2.)
                        denominators.append(1./table.field(ROT+'#'+exp+'#MAGERR_APER2')[j]**2.)


            if len(data)>0:
                '''  we have already subtracted the image-dependent zeropoint so we just need to subtract the instrinsic magnitude of the star, which we get from an average '''                                                                                            
                average = reduce(lambda x,y: x + y,numerators) / reduce(lambda x,y: x + y, denominators)           
                #print average                                                                                       
                chisq = 0                                                                                            
                for k in range(len(data)):                                                                           
                    chisq += abs(models[k] - data[k] - average) / errs[k]                                            
                #print chisq                                                                                         
                #print models[k], y[j][k], average, err[j][k]                                                        
                redchisq = chisq/float(len(data))                                                              
                #ydiff = y[j]['0'][0] - y[j]['0'][1]                                                                 
                #moddiff = models[0] - models[1]                                                                     
                                                                                                                     
                if 0: #abs(moddiff - ydiff) < 0.001:                                                                 
                    print X[j]                                                                                       
                    print Y[j]                                                                                       
                    print y[j]                                                                                       
                    print err[j]                                                                                     
                                                                                                                     
                    print models                                                                                     
                    print 'moddiff', models[0] - models[1]                                                           
                    print 'y diff', y[j][0] - y[j][1]                                                                
                    print chisq                                                                                      
                    print redchisq                                                                                   
                    raw_input()                                                                                      
                redchisqs.append(redchisq)       
                #redchisqs.append(abs(moddiff-ydiff)/err[j][0])                                                                                                                                                                                                             
            if row_num%500 == 0: print j 
        status = 0
        import Numeric
        redchisqs = Numeric.array(redchisqs)
        #print redchisqs
        return([status,redchisqs ])
                                                                                                                  
    def calc_sigma(self, p, fjac=None, y=None, err=None, X=None, Y=None):
        # function you can pass to mpfit
        self.dict = {'zp':1., 'color1':color1, 'color2':color2, 'airmass':airmass, 'X':X, 'Y':Y}
        model = 0       
        for i in range(len(self.smodel)):   
            term = self.smodel[i]
            #print term
            model += p[i] * reduce(lambda x,y: x * y,[self.dict[z] for z in term]) 
        status = 0
        return([model, (model-y)/err])


def calcIllum(size_x, size_y, bin, fit):
    import numpy, math, pyfits, os                                                                              
    fitvars = fit['class'].fitvars
    x,y = numpy.meshgrid(numpy.arange(0,size_x,bin),numpy.arange(0,size_y,bin))
    F=0.1
    print 'calculating'
    #epsilon = fitvars['X']*x + fitvars['Y']*y + fitvars['XTX']*x**2 + fitvars['YTY']*y**2 + fitvars['XTY']*x*y + fitvars['XTYTY']*x*y*y + fitvars['XTXTY']*x*x*y + fitvars['XTXTX']*x*x*x  + fitvars['YTYTY']*y*y*y 

    epsilon = fitvars['X']*x + fitvars['Y']*y + fitvars['XTX']*x**2 + fitvars['YTY']*y**2 + fitvars['XTY']*x*y 

    epsilon = fitvars['X']*x + fitvars['Y']*y + fitvars['XTX']*x**2 + fitvars['YTY']*y**2 + fitvars['XTY']*x*y 
    #correction = 10.**(epsilon/2.5)
    print 'writing'
    hdu = pyfits.PrimaryHDU(epsilon)
    os.system('rm /tmp/correction.fits')
    hdu.writeto('/tmp/correction.fits')
    print 'done'

    return

def random_cmp(x,y):
    import random
    a = random.random()
    b = random.random()
    if a > b: return 1
    else: return -1

def linear_fit():
    maxSigIter=50
    solutions = [] 

    import pickle
    ''' get data '''
    EXPS = getTableInfo()
    print EXPS
    
    #ROTS, data, err, X, Y, maxVal, classStar = diffCalcNew()
    #save = {'ROTS': ROTS, 'data':data,'err':err,'X':X,'Y':Y,'maxVal':maxVal,'classStar':classStar}
    #uu = open('/tmp/store','w')
    #import pickle
    #pickle.dump(save,uu)
    #uu.close()
   
    ''' EXPS has all of the image information for different rotations '''

    ''' make model '''
    #fit = make_model(EXPS)
    #position_fit = make_position_model(EXPS)
    print fit
    if 1:
        star_good,supas = selectGoodStars(EXPS)               
        uu = open('/tmp/store','w')
        import pickle
        pickle.dump({'star_good':star_good,'supas':supas},uu)
        uu.close()

    import pickle
    f=open('/tmp/store','r')
    m=pickle.Unpickler(f)
    d=m.load()

    star_good = d['star_good']
    supas = d['supas']

    print len(star_good)

    if 0:

        l = range(len(star_good))                     
        print l[0:10]
        l.sort(random_cmp)
        print l[0:10]
                                                      
        ''' shorten star_good, supas '''
        star_good = [star_good[i] for i in l[0:800]]
        supas = [supas[i] for i in l[0:800]]


    print len(star_good)

    print EXPS 

    print EXPS.keys(), EXPS[EXPS.keys()[0]]
    print len(supas), len(star_good)
    print supas[0:10]

    columns = []
    column_dict = {}


    ''' position-dependent terms in design matrix '''
    position_columns = []
    index = -1
    #position_fit = [['Xpos_ABS','Xpos_ABS'],['Xpos_ABS','Ypos_ABS'],['Ypos_ABS','Ypos_ABS'],['Xpos_ABS'],['Ypos_ABS']]
    #cheby_fit = [{'f':lambda x,y:x,'name':'T1X'},{'f':lambda x,y:2*x**2.-1,'name':'T2X'},{'f':lambda x,y:4*x**3.-3*x,'name':'T3X'},{'f':lambda x,y:y,'name':'T1Y'},{'f':lambda x,y:2*y**2.-1,'name':'T2Y'},{'f':lambda x,y:4*y**3.-3*y,'name':'T3Y'}]

    #cheby_fit = [{'f':lambda x,y:x,'name':'T1X'},{'f':lambda x,y:2*x**2.-1,'name':'T2X'},{'f':lambda x,y:y,'name':'T1Y'},{'f':lambda x,y:2*y**2.-1,'name':'T2Y'}]

    cheby_fit = [{'f':lambda x,y:x,'name':'T0'},{'f':lambda x,y:y,'name':'T1'},{'f':lambda x,y:2*x**2.-1,'name':'T2'},{'f':lambda x,y:2*y**2.-1,'name':'T3'},{'f':lambda x,y:(2*x**2.-1)*(2.*y**2.-1),'name':'T4'}]
    for ROT in EXPS.keys():
        for term in cheby_fit:
            index += 1
            name = str(ROT) + '#' + term['name'] # + reduce(lambda x,y: x + 'T' + y,term)
            position_columns.append({'name':name,'term':term['f'],'rotation':ROT,'index':index})
    print position_columns

    ''' zero point terms in design matrix '''
    zp_columns = [] 
    for ROT in EXPS.keys():
        for exp in EXPS[ROT]:
            zp_columns.append({'name':'zp_'+exp,'image':exp,'im_rotation':ROT})
    print zp_columns
   
    mag_columns = []
    for star in supas:
        mag_columns.append({'name':'mag_' + str(star['table index'])})
    print mag_columns



    ''' total number of fit parameters summed over each rotation + total number of images of all rotations + total number of stars to fit '''
    x_length = len(position_columns) + len(zp_columns) + len(mag_columns) 
    y_length = reduce(lambda x,y: x + y,[len(star['supa files']) for star in supas]) 
    print x_length, y_length

    import scipy
    from pysparse import spmatrix

    A = scipy.zeros([y_length,x_length])
    B = scipy.zeros(y_length)

    #A = spmatrix.ll_mat(y_length,x_length)
    Af = open('A','w')
    #B = spmatrix.ll_mat(y_length)
    #B = scipy.zeros(y_length)
    Bf = open('b','w')

    comp_mag = scipy.zeros(len(supas))
    print y_length, x_length

    
    import astropy.io.fits as pyfits
    p = pyfits.open('/tmp/final.cat')
    table = p[1].data

    Bstr = ''
    row_num = -1
    supa_num = -1
    degeneracy_break = {} 
    for ROT in EXPS.keys():
        degeneracy_break[ROT] = False
    #degeneracy_break = False
    ''' each star '''
    for star in supas:
        supa_num += 1
        comp_mag[supa_num] = table.field(str(star['supa files'][0]['rotation']) + '#' + star['supa files'][0]['name'] + '#MAG_APER2')[star['table index']]
        ''' each exp of each star '''
        for exp in star['supa files']:
            row_num += 1
            col_num = -1 
            rotation = exp['rotation'] 
            sigma = table.field(str(rotation) + '#' + exp['name'] + '#MAGERR_APER2')[star['table index']] 
            #if sigma < 0.001: sigma = 0.001
            sigma = sigma * 1000. 
            #print table.field(str(rotation) + '#' + exp['name'] + '#MAGERR_APER2')[star['table index']]
            for c in position_columns: 
                col_num += 1
                if c['rotation'] == rotation:
                    n = str(rotation) + '#' + exp['name'] + '#Xpos_ABS'
                    #term_cont = [str(rotation) + '#' + exp['name'] + '#' + par for par in c['term']]
                    #A[row_num][col_num] = reduce(lambda x,y: x * y,[table.field(z)[star['table index']] for z in term_cont])/sigma
                    coord_conv = lambda x:(2.*x-0-10000)/(10000-0) 
                    #print c['term'],c['term'](1,1)
                    x = table.field(str(rotation) + '#' + exp['name'] + '#Xpos_ABS')[star['table index']]
                    y = table.field(str(rotation) + '#' + exp['name'] + '#Ypos_ABS')[star['table index']]
                    x = coord_conv(x)
                    y = coord_conv(y)
                    #print table.field(str(rotation) + '#' + exp['name'] + '#Xpos_ABS')[star['table index']], table.field(str(rotation) + '#' + exp['name'] + '#Ypos_ABS')[star['table index']]

                    #print x,y
                    #print c['term'](x,y)
                    #raw_input()
                    A[row_num,col_num] = c['term'](x,y)/sigma
                    Af.write(str(row_num) + ' ' + str(col_num) + ' ' + str(c['term'](x,y)/sigma) + '\n')
            for c in zp_columns:
                col_num += 1
                #print c['image'], exp['name']
                #if not degeneracy_break and c['image'] == exp['name']:
                if not degeneracy_break[c['im_rotation']] and c['image'] == exp['name']:
                    degeneracy_break[c['im_rotation']] = True
                    A[row_num,col_num] = 1./sigma
                    Af.write(str(row_num) + ' ' + str(col_num) + ' ' + str(1./sigma) + '\n')
                    #print col_num
            ''' magnitude column '''
            col_num += 1
            #print supa_num,  col_num, row_num, x_length, y_length
            A[row_num,col_num + supa_num] = 1./sigma
            Af.write(str(row_num) + ' ' + str(col_num + supa_num) + ' ' + str(1./sigma) + '\n')
            B[row_num] = table.field(str(rotation) + '#' + exp['name'] + '#MAG_APER2')[star['table index']]/sigma
            Bstr += str(table.field(str(rotation) + '#' + exp['name'] + '#MAG_APER2')[star['table index']]/sigma) + ' '

    Bf.write(Bstr[:-1])
    Bf.close()
    Af.close()

    raw_input()
    print A[0,0:30], B[0:10], scipy.shape(A), scipy.shape(B)

    Af = open('/tmp/B','w')
    for i in range(len(B)):
        Af.write(str(B[i]) + '\n')
    Af.close()

    import re, os
    os.system('a.out < A')
    bout = open('x','r').read()
    res = re.split('\s+',bout[:-1])
    U = [float(x) for x in res]

    #from scipy import linalg
    #print 'doing linear algebra'
    #U = linalg.lstsq(A,B)
    #print U[0][0:30]

    raw_input()
    if 0:
        from pysparse.pysparseUmfpack import PysparseUmfpackSolver                          
        from pysparse.pysparseMatrix import PysparseMatrix
        from pysparse import spmatrix, precon, itsolvers
        A = PysparseMatrix(matrix=A)
        print 'initialized'
        S = PysparseUmfpackSolver(A)
        print 'initialized'
        S.solve(B)
        raw_input()
        import numpy
        x = numpy.empty(len(B))
        print A.shape, B.shape, x.shape
        raw_input()
        Aprime = A.to_csr()
        info, iter, relres = itsolvers.qmrs(Aprime,B,x,1e-12,2000)
        print 'done with linear algebra'
        raw_input()
        print len(U), len(U[0]),len(U[:][0]), len(position_columns), len(zp_columns)
        print U[0] 
        print scipy.shape(A), scipy.shape(U[0]), len(U[0]) , scipy.shape(B), scipy.shape(A)
        print 'hey'
        print len(U[0][len(position_columns) + len(zp_columns) :]) , len(comp_mag )
        print U[0][len(position_columns) + len(zp_columns) :] -comp_mag 
        print U[0][:len(position_columns) + len(zp_columns)]

    position_fit = [['Xpos_ABS','Xpos_ABS'],['Xpos_ABS','Ypos_ABS'],['Ypos_ABS','Ypos_ABS'],['Xpos_ABS'],['Ypos_ABS']]
    import re
    for ROT in EXPS.keys():
        print 'ROT', ROT
        fitvars = {} 
        for ele in position_columns:                      
            res = re.split('#',ele['name'])
            if res[0] == ROT:
                fitvars[ele['name'][2:]] = U[ele['index']] 
                print ele['name'], fitvars[ele['name'][2:]]

        size_x=10000
        size_y=10000
        bin=100
        import numpy, math, pyfits, os                                                                              
        x,y = numpy.meshgrid(numpy.arange(0,size_x,bin),numpy.arange(0,size_y,bin))
        F=0.1
        print 'calculating'
        #epsilon = fitvars['Xpos_ABS']*x + fitvars['Ypos_ABS']*y + fitvars['Xpos_ABSTXpos_ABS']*x**2 + fitvars['Ypos_ABSTYpos_ABS']*y**2 + fitvars['Xpos_ABSTYpos_ABS']*x*y 

        coord_conv = lambda x:(2.*x-0-10000)/(10000-0) 
        #print c['term'],c['term'](1,1)
        x = coord_conv(x)
        y = coord_conv(y)

        epsilon = fitvars['T0']*x + fitvars['T1']*y + fitvars['T2']*(2*x**2.-1) + fitvars['T3']*(2*y**2.-1) + fitvars['T4']*(2*x**2.-1)*(2.*y**2.-1)

        #epsilon = fitvars['T1X']*x + fitvars['T2X']*(x**2.) + fitvars['T1Y']*y + fitvars['T2Y']*(y**2) + fitvars['T3Y']*(x*y) 
        #correction = 10.**(epsilon/2.5)
        print 'writing'
        hdu = pyfits.PrimaryHDU(epsilon)
        os.system('rm /tmp/correction' + ROT + '.fits')
        hdu.writeto('/tmp/correction' + ROT + '.fits')
        print 'done'
                                                                                                                                                                                                                          
    return









            




def fit():
    maxSigIter=50
    solutions = [] 

    import pickle
    ''' get data '''
    EXPS = getTableInfo()
    print EXPS
    
    #ROTS, data, err, X, Y, maxVal, classStar = diffCalcNew()
    #save = {'ROTS': ROTS, 'data':data,'err':err,'X':X,'Y':Y,'maxVal':maxVal,'classStar':classStar}
    #uu = open('/tmp/store','w')
    #import pickle
    #pickle.dump(save,uu)
    #uu.close()
   
    ''' EXPS has all of the image information for different rotations '''

    ''' make model '''
    fit = make_model(EXPS)
    print fit
    star_good = selectGoodStars(EXPS)
    uu = open('/tmp/store','w')
    import pickle
    pickle.dump(star_good,uu)
    uu.close()

    import pickle
    f=open('/tmp/store','r')
    m=pickle.Unpickler(f)
    star_good=m.load()






    fit['class'] = phot_funct(fit['model'],fit['fixed'],EXPS,star_good,fit['apply'])

    import astropy.io.fits as pyfits
    p = pyfits.open('/tmp/final.cat')
    table = p[1].data

    import copy
    table_save = copy.copy(table)
    for i in range(maxSigIter):
        fa = {"table": table_save}
        func = fit['class'].calc_model 

        #functkw takes input data arrays
        #parinfo takes initial guess and constraints on parameters 
        #import optimize
        #params, covar, info, mesg, ier = optimize.leastsq(func,guess,args = (points,vals,errs), full_output=True)
        import mpfit
        m =  mpfit.mpfit(func, functkw=fa,
                         parinfo=fit['class'].parstart,
                         maxiter=1000, quiet=0)
        print m.params, m.perror 
        if (m.status <= 0):
            print 'error message = ', m.errmsg
            condition = Numeric.zeros(len(data))
            break
        print m.params,m.perror
        #fits = [{'vars':['zp','color1coeff','color1coeff2'],'parinfo':[{'value':p[0],'fixed':0},{'value':p[1],'fixed':0},{'value':p[2],'fixed':0},'function':phot_funct_secondorder,'fit_type':'no_airmass'}]
        fit['class'].fitvars = {}
        for ele in range(len(fit['class'].smodel)):                              
            print ele, fit['class'].smodel
            name = make_name(fit['class'].smodel[ele])
            print ele, fit['class'].fitvars, name, m.params[ele] 
            fit['class'].fitvars[name] = m.params[ele]          
            fit['class'].fitvars[name + '_err'] = m.perror[ele]
        perror = copy.copy(m.perror)
                                                                                                                                                                                                               
        # Compute a 3 sigma rejection criterion
        print m.params, data_rec[0], data[0]
        #condition, redchisq = SigmaCond(params, data_save, data,
        #                           airmass_save, airmass,
        #                           color1_save, color1, color2_save, color2, err_save, err, sigmareject)
                                                                                                                                                                                                               


        calcIllum(10000, 10000, 100, fit)

        if len(data_save) > 1:                                                                     
            (mo_save, reddm) = fit['class'].calc_sigma(m.params, airmass_save, color1_save, color2_save, data_save, err_save, X_save, Y_save)
            #reddm = (data-mo)/err
            redchisq = Numeric.sqrt(Numeric.sum(Numeric.power(reddm, 2)) / (len(reddm) - 1))
            dm = data_save-mo_save
            #dm_save = data_save - mo_save
            print len(data_save), len(mo_save)
            dm_save = data_save - mo_save
            mean =  Numeric.sum(dm)/len(dm)
            sigma = Numeric.sqrt(Numeric.sum(Numeric.power(mean-dm, 2)) / (len(dm) - 1))
            # you can pick either 
            #condition = Numeric.less(Numeric.fabs(dm_save), float(sigmareject) * sigma)
            condition = Numeric.less(Numeric.fabs(dm_save), float(sigmareject) * err_save)
        else:
            condition = Numeric.zeros(len(data_save))
          
        print redchisq 
        # Keep everything (from the full data set!) that is within
        # the 3 sigma criterion
        #data_sig = Numeric.compress(condition, data_save)
        data = Numeric.compress(condition, data_rec)
        err = Numeric.compress(condition, err_save)
        X = Numeric.compress(condition, X_save)
        Y = Numeric.compress(condition, Y_save)
        new_len = len(data)
        
        if float(new_len)/float(save_len) < 0.5:
            print "Rejected more than 50% of all measurements."
            print "Aborting this fit."
            break
        
        # No change
        if new_len == old_len:
            print "Converged! (%d iterations)" % (i+1, )
            print "Kept %d/%d stars." % (new_len, save_len)
            break
    #print params, perror, condition
    meanerr = Numeric.sum(err_save)/len(err_save)

def make_name(name): 
    if len(name) > 1:                               
        name = reduce(lambda x,y: x + 'T' + y,name)
    else: 
        name = name[0]
    return name


