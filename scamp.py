import tempfile, os, re, scipy

nnw = os.environ['util'] + '/default.nnw'
params = os.environ['kpno'] + '/process_kpno/default.param'
config = os.environ['kpno'] + '/process_kpno/config'
conv = os.environ['util'] + '/default.conv'
assoc_params = os.environ['kpno'] + '/process_kpno/assoc.param'
psf_params = os.environ['kpno'] + '/process_kpno/psf.param'
assoc_config = os.environ['kpno'] + '/process_kpno/assoc.sex'


def get_night(jdobs):
    import time, calendar

    #a = time.strptime("08:21:39.077 2010-05-07","%H:%M:%S.077 %Y-%m-%d")

    #b = time.localtime(calendar.timegm(a))    

    mjdobs = jdobs - 2400000.5 

    year,month,day = (1998,12,31) # GABODSID reference

    hour,min,sec = (19,0,0) # Tucson offset
    
    timefrac = hour + min / 60.0 + sec / 3600.0;

    A = year * 367.0;
    B = int((month + 9.0) / 12.0);
    C = int(((year + B) * 7.0) / 4.0);
    D = int((275.0 * month) / 9.0);
    E = day + 1721013.5 + (timefrac / 24.0);
    if (((100.0 * year) + month - 190002.5) >= 0) : F =  1.0 
    else: -1.0;
    julian_date = A - C + D + E - (0.5 * F) + 0.5 - 2400001.0 + 0.5;
    
    print "Julian date of reference time: %f" % julian_date
    print "Days passed since reference time: %f\n"  % (mjdobs-julian_date)

    return int(mjdobs-julian_date)




''' in arcseconds '''
def get_scale(file):

    import commands

    cd1_1 = float(commands.getoutput('gethead ' + file + ' CD1_1'))
    cd1_2 = float(commands.getoutput('gethead ' + file + ' CD1_2'))

    scale = (cd1_1**2. + cd1_2**2.)**0.5 * 3600.

    return scale




def av_difference(diff, errors):

    errors[errors < 0.02] = 0.02
    average = scipy.average(diff,weights=1./errors**2.)
                                                               
    ''' reject outliers (similar to SDSS calibration?) '''
    mask = abs(diff - average)/errors < 6.
    diff = diff[mask]
    errors = errors[mask]
                                                               
                                                               
    print  diff.tolist(), errors.tolist(), average
                                                               
    average = scipy.average(diff,weights=1./errors**2.)
    mask = abs(diff - average)/errors < 3.
    diff = diff[mask]
    errors = errors[mask]
                                                               
    print diff.tolist(), errors.tolist(), average
                                                               
    average = float(scipy.average(diff,weights=1./errors**2.))

    return average




class entryExit(object):
    def __init__(self,f):
        self.f = f
    
    def __call__(self, *args):
        import MySQLdb
        from time import strftime
        db2 = MySQLdb.connect(db='calib')
        c = db2.cursor()

        run_name,dummy,snpath = args 
        print run_name, snpath

        def status(stat,error=None):
            command = "SELECT * from STATUS where SN='" + snpath + "' and RUN='" + run_name + "' and FUNCTION='" + str(self.f.__name__) + "'"
            print command
            c.execute(command)                                                                                                       
            results = c.fetchall()
            if not len(results):
                command = "INSERT INTO STATUS (SN,RUN,FUNCTION) VALUES ('" + snpath + "','" + run_name + "','" + str(self.f.__name__) +"')"
                print command 
                c.execute(command) 


            command = "UPDATE STATUS set STATUS='" + stat + "' WHERE SN='" + snpath + "' and RUN='" + run_name + "' and FUNCTION='" + str(self.f.__name__) + "'" 
            print command 
            c.execute(command) 

            command = "UPDATE STATUS set TIME='" + strftime("%Y-%m-%d %H:%M:%S") + "' WHERE SN='" + snpath + "' and RUN='" + run_name + "' and FUNCTION='" + str(self.f.__name__) + "'" 
            print command 
            c.execute(command) 

            try:
                command = "UPDATE STATUS set EXCEPTION='" + str(error).replace("'","").replace('"','').replace('?','').replace('_','').replace('-','') + "' WHERE SN='" + snpath + "' and RUN='" + run_name + "' and FUNCTION='" + str(self.f.__name__) + "'"  
                print command 
                c.execute(command) 
            except: print 'failed update'







        status('start')
        try:
            self.f(*args)
        except KeyboardInterrupt:
            import traceback, sys
            s = traceback.format_exc() #file=sys.stdout)
            print s
            print 'saving exception'
            status('interrupt',error=s)
            raise KeyboardInterrupt
        
        except:
            import traceback, sys
            s = traceback.format_exc() #file=sys.stdout)
            print s
            status('fail',error=s)
            raise Exception
        status('finished')
        print 'done'


def extract_psf(catalog, fwhm, ellip, xml, psfdir, color):

    import os, string
    found = False
    for mask in ['0x00fe','0x00ff','0x00fc']:
        for minsn in ['20','30','10']:
            print catalog, fwhm, ellip, xml, psfdir, color
            command = '/usr/local/bin/psfex ' + catalog + ' -CHECKIMAGE_TYPE NONE -CHECKPLOT_TYPE FWHM,ELLIPTICITY -CHECKPLOT_NAME ' + fwhm + ',' + ellip + ' -XML_NAME ' + xml + ' -CHECKPLOT_DEV PSC -SAMPLE_FWHMRANGE 1.0,10.0 -PSF_DIR ' + psfdir +   ' -SAMPLE_MINSN ' + minsn + ' -SAMPLE_FLAGMASK ' + mask 
            print command 
            os.system(command)
            from vo.table import parse                     
            votable = parse(xml,pedantic=False)
            table =  votable.get_first_table()
            beta_psfex = table.array['MoffatBeta_Mean'][0]
            fwhm_psfex = table.array['FWHM_Mean'][0]
            fwhm_psfex_min = table.array['FWHM_Min'][0]
            fwhm_psfex_max = table.array['FWHM_Max'][0]
            chi2_psfex = table.array['Chi2_Mean'][0]
            ellipticity_psfex = table.array['Ellipticity_Mean'][0]
            asymmetry_psfex = table.array['Asymmetry_Mean'][0]
                                                           
            print beta_psfex, fwhm_psfex, chi2_psfex
                                                                                                                                                                                                                                                                                                       
            if fwhm_psfex != 0:
                if string.find(color,'SDSS') != -1: aperture_corr = 0                             
                else: aperture_corr = correct(10.,fwhm_psfex,beta_psfex)
                                                                                                  
                print aperture_corr
                                                                                                  
                if str(aperture_corr)!= 'nan' and 0.1 < fwhm_psfex < 10 and chi2_psfex < 12 and aperture_corr < 0.2: 
                    found = True
                    break
        if found: break
                                                                                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                                                   
    if str(aperture_corr)== 'nan' or fwhm_psfex > 10 or fwhm_psfex < 0.1: # or chi2_psfex > 5:
        print catalog, aperture_corr, fwhm_psfex, chi2_psfex 
        print 'PSF problem'
        
        raise Exception


    return fwhm_psfex, fwhm_psfex_min, fwhm_psfex_max, beta_psfex, chi2_psfex, ellipticity_psfex, asymmetry_psfex, aperture_corr



def copy_images_sdss(run, night, sn):
    from config import datb, prog, path
    import glob, string, anydbm, os, re, os, colorlib, sys
    
    gh = anydbm.open(datb + sn,'c')
    
    print sn
    ra = gh['galradeg']
    dec = gh['galdecdeg'] 
    
    os.system('gunzip ' + path + sn + '/SDSS/g/*') 
    files = glob.glob(path + sn + '/SDSS/g/*.fit' ) 
    if len(files) == 0: 
        os.system('python clean_up.py ' + sn)
    #mktemplate(sn,files[0],gh) 
    #template = path + sn + '/SDSS/template.fits' 
    
    for filt in ['z','u','g','r','i']:           
        print filt
        base_dict = {}
        os.system('rm ' + path + sn + '/SDSS/coadd' + filt + '.fits')
        os.system('gunzip ' + path + sn + '/SDSS/' + filt + '/*') 
        files_glob = glob.glob(path + sn + '/SDSS/' + filt + '/*.fit' ) 
    
        print files_glob
        print files_glob, files

        dir_bg = '/Volumes/mosquitocoast/patrick/kpno/' + run + '/' + night + '/' + sn + '/SDSS_' + filt + '_raw/' 
        os.system('rm ' + dir_bg + '*')
        os.system('mkdir -p ' + dir_bg)
    
        factors = []
        noskyfiles = []
        for file in files_glob: 
            dict = {}
            import colorlib
            dict = colorlib.values(dict,file,sn,image_type='coadd')
            print dict, file

            import math
            file_zp = 2.5*math.log10(53.907456) - (float(dict['aa' + filt]) + float(dict['airmass' + filt])*float(dict['kk' + filt]))

            print file_zp, filt, file

            import commands

            image = dir_bg + file.split('/')[-1] + 's'
            
            command = 'cp ' + file + ' ' + image
            print command
            os.system(command)  


            command = 'sethead ' + image + ' MAGZP=' + str(file_zp)
            print command
            os.system(command)


            ''' need to switch so that RA is CRVAL1 '''
            ctype1 = commands.getoutput('gethead ' + image + ' CTYPE2')                                
            ctype2 = commands.getoutput('gethead ' + image + ' CTYPE1')                                

            crval1= commands.getoutput('gethead ' + image + ' CRVAL2')                                
            crval2= commands.getoutput('gethead ' + image + ' CRVAL1')                                


            #crpix1= commands.getoutput('gethead ' + image + ' CRPIX2')                                
            #crpix2= commands.getoutput('gethead ' + image + ' CRPIX1')                                

            CD2_1 = commands.getoutput('gethead ' + image + ' CD1_1')                                
            CD1_2 = commands.getoutput('gethead ' + image + ' CD2_2')                                
            CD2_2 = commands.getoutput('gethead ' + image + ' CD1_2')                                
            CD1_1 = commands.getoutput('gethead ' + image + ' CD2_1')                                

            if string.find(ctype2,'DEC') != -1:

                os.system('sethead ' + image + ' CTYPE2=' + ctype2) 
                os.system('sethead ' + image + ' CTYPE1=' + ctype1) 

                #os.system('sethead ' + image + ' CRPIX2=' + crpix2) 
                #os.system('sethead ' + image + ' CRPIX1=' + crpix1) 


                os.system('sethead ' + image + ' CRVAL2=' + crval2) 
                os.system('sethead ' + image + ' CRVAL1=' + crval1) 
                                                                                                            
                os.system('sethead ' + image + ' CD1_2=' + CD1_2) 
                os.system('sethead ' + image + ' CD2_2=' + CD2_2) 
                os.system('sethead ' + image + ' CD2_1=' + CD2_1) 
                os.system('sethead ' + image + ' CD1_1=' + CD1_1) 
                                                                                                            
                os.system('sethead ' + image + ' EQUINOX=2000.0')



            


def new_run_db():
    import MySQLdb
    db2 = MySQLdb.connect(db='calib')
    c = db2.cursor()
    command = 'DROP TABLE STATUS'
    c.execute(command)
    command = "CREATE TABLE IF NOT EXISTS STATUS (  FUNCTION varchar(80), TIME varchar(80), SN varchar(80), RUN varchar(80), ERROR varchar(80), STATUS varchar(80), FILTERS varchar(80), EXCEPTION varchar(1000))"  
    print command
    c.execute(command)

def new_astrom_db():
    import MySQLdb
    db2 = MySQLdb.connect(db='calib')
    c = db2.cursor()
    command = 'DROP TABLE ASTROM'
    #c.execute(command)
    command = 'CREATE TABLE IF NOT EXISTS ASTROM ( SN varchar(80), RUN varchar(80), ASTREF VARCHAR(80), REFSIGMAONE VARCHAR(80), REFSIGMATWO VARCHAR(80), REFSIGMAONEHSN VARCHAR(80), REFSIGMATWOHSN VARCHAR(80), SCAMPMSG VARCHAR(200))'
    print command
    c.execute(command)



def new_db():
    import MySQLdb
    db2 = MySQLdb.connect(db='calib')
    c = db2.cursor()
    command = 'DROP TABLE CALIB'
    #c.execute(command)
    command = "CREATE TABLE IF NOT EXISTS CALIB (  AIRMASS varchar(80), FILT varchar(80), SN varchar(80), JD varchar(150), RELZP FLOAT(8,4), SDSSZP FLOAT(8,4), SLRZP FLOAT(8,4), STARS INT, DATEOBS varchar(80), NAME varchar(80), RUN varchar(80), UT varchar(80), EXPTIME FLOAT(15,4), FILES varchar(80), FWHM FLOAT(10,4), CHI FLOAT(10,4), GALLAT FLOAT(10,4), GALLONG FLOAT(10,4), DUSTCORR FLOAT(10,4), APERCORR FLOAT(10,4), PEEK varchar(80), SDSSCOV varchar(80), DUSTCORRSFD float(10,4), SDSSNUM FLOAT(10,4), SLRNUM INTEGER, EXPTIMECORR FLOAT(10,4), SLRREDCHI FLOAT(10,4), CCDSUM varchar(80), SNTY varchar(80), ELLIPTICITY float(10,4), ASYMMETRY FLOAT(10,4), SDSSZPERR FLOAT(10,4), SLRZPERR FLOAT(10,4), BOOTSTRAPNUM INTEGER, BETA FLOAT(10,4), BOOTSTRAPS VARCHAR(200), STRIPE varchar(80), SDSSDUSTZP float(10,4), SDSSDUSTZPERR float(10,4), SDSSDUSTNUM float(10,4), NIGHT float(10,4), sdssphotozp float(10,4), broadlined float(10,4), ebv float(10,4))"

    #command = "CREATE TABLE IF NOT EXISTS CALIB (  AIRMASS varchar(80), FILT varchar(80), SN varchar(80), JD varchar(150), RELZP FLOAT(8,4), SDSSZP FLOAT(8,4), SLRZP FLOAT(8,4), STARS INT, DATEOBS varchar(80), NAME varchar(80), RUN varchar(80), UT varchar(80), EXPTIME FLOAT(15,4), FILES varchar(80), FWHM FLOAT(10,4), CHI FLOAT(10,4), GALLAT FLOAT(10,4), GALLONG FLOAT(10,4), DUSTCORR FLOAT(10,4), APERCORR FLOAT(10,4), PEEK varchar(80), SDSSCOV varchar(80), DUSTCORRSFD float(10,4), SDSSNUM FLOAT(10,4), SLRNUM INTEGER, EXPTIMECORR FLOAT(10,4), SLRREDCHI FLOAT(10,4), CCDSUM varchar(80), SNTY varchar(80), ELLIPTICITY float(10,4), ASYMMETRY FLOAT(10,4), SDSSZPERR FLOAT(10,4), SLRZPERR FLOAT(10,4), BOOTSTRAPNUM INTEGER, BETA FLOAT(10,4), BOOTSTRAPS VARCHAR(200), STRIPE varchar(80), SDSSDUSTZP float(10,4), SDSSDUSTZPERR float(10,4), SDSSDUSTNUM float(10,4), NIGHT float(10,4), sdssphotozp float(10,4), broadlined float(10,4), SDSSSLRZP float(10,4). sdssslrzperr float(10,4), sdssslrnum float(10,4), sdssslrredchi float(10,4). sdssbootstrapnum float(10,4), sdssbootstraps float(10,4))"
    print command
    c.execute(command)


def add_image(image,snpath,color,name,run):
    import commands
    import colorlib, anydbm
    if snpath[0:2] == 'sn':
        colorlib.asiago(snpath)  
        gh = anydbm.open(snpath)
        SNTY = gh['snty']
    else: SNTY = 'other'
    
    AIRMASS = commands.getoutput('gethead ' + image + ' AIRMASS')
    if AIRMASS == '': AIRMASS = '-99'
    JD = commands.getoutput('gethead ' + image + ' JD')
    if JD == '': JD = '-99'        
    NIGHTID = int(get_night(float(JD)))
    

    DATEOBS = commands.getoutput('gethead ' + image + ' DATE-OBS')
    CCDSUM = commands.getoutput('gethead ' + image + ' CCDSUM')
    UT = commands.getoutput('gethead ' + image + ' UT')
    EXPTIME = str(float(commands.getoutput('gethead ' + image + ' EXPTIME')))
    FILES = commands.getoutput('gethead ' + image + ' FILES')
    print AIRMASS, JD, DATEOBS, UT, EXPTIME, FILES, image
    import MySQLdb
    db2 = MySQLdb.connect(db='calib')
    c = db2.cursor()
    command = "SELECT * from CALIB where SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'"
    print command
    c.execute(command)                                                                                                       
    results = c.fetchall()
    if not len(results):
        command = "INSERT INTO CALIB (SN,FILT,NAME,RUN,AIRMASS,JD,DATEOBS,UT,EXPTIME,FILES,CCDSUM,SNTY,NIGHT) VALUES ('" + snpath + "','" + color + "','" + name + "','" + run + "'," + AIRMASS + "," + JD + ",'" + DATEOBS + "','" + UT + "'," + EXPTIME + ",'" + FILES + "','" + CCDSUM +"','" + SNTY + "'," + str(NIGHTID) + ")"
        print command 
        c.execute(command) 

def get_zp(fin):
    import commands
    zp = float(commands.getoutput('gethead ' + fin + ' MAGZP'))
    background = float(commands.getoutput('gethead ' + fin + ' SKYVAL'))
    return zp, background

def get_zp_SDSS(fin):
    import commands
    zp = float(commands.getoutput('gethead ' + fin + ' MAGZP'))
    return zp

def correct(radius,fwhm,beta,infi=1000):
    ''' http://stsdas.stsci.edu/cgi-bin/gethelp.cgi?psfmeasure '''
    ''' I(r) = (1 + (r/alpha)**2)) ** (-beta) '''

    import math    

    alpha = fwhm/(2.*math.sqrt(2.**(1./beta) - 1.))

    #f = lambda x: math.pi * (x**2. + fwhm**2.) * (x**2/fwhm**2. + 1.)**(-1.*beta) / (beta - 1)

    frac = (1. + (radius/alpha)**2.)**(1-beta)

    print frac

    return -2.5*math.log10(1-frac)

def convert_to_galactic(alpha,delta):

    gallongs = []
    gallats = []
    import ephem
    for coord_in_ra, coord_in_dec in zip(alpha, delta):

        coord = ephem.Equatorial( str(coord_in_ra*(24./360.)), str(coord_in_dec), epoch='2000') # input needs to be in HOURS as a STRING
        g = ephem.Galactic(coord, epoch='2000') # output is in degrees not hours--it's latitude/longitude
 
        spt = re.split('\:',str(g.lat))

        gallat = float(spt[0]) / abs(float(spt[0])) * (abs(float(spt[0])) + float(spt[1])/60. + float(spt[2])/3600. )
        spt = re.split('\:',str(g.long))

        gallong = float(spt[0]) / abs(float(spt[0])) *  (abs(float(spt[0])) + float(spt[1])/60. + float(spt[2])/3600. )
        
        gallongs.append(gallong)
        gallats.append(gallat)

    return scipy.array(gallongs), scipy.array(gallats)


def getTempFile(dir='/tmp', prefix='',suffix=''):
    import os
    thefile, thefilename = tempfile.mkstemp(dir=dir,
                                          prefix=prefix,
                                          suffix=suffix)
    os.close(thefile)
    return thefilename


def getDust(alpha, delta, pg10=True):
    dustpos_filename = getTempFile(dir='/tmp', prefix='dustpos')
    ebvgal_filename = getTempFile(dir='/tmp', prefix='ebvgal')
    peekapplied_filename = getTempFile(dir='/tmp', prefix='peekapplied')
    def cleanUp():
        if os.path.exists(dustpos_filename):
            os.remove(dustpos_filename)
        if os.path.exists(ebvgal_filename):
            os.remove(ebvgal_filename)

    try:
        gallong, gallat = convert_to_galactic(alpha, delta)

        dustpos_file = open(dustpos_filename, 'w')
        for pos in zip(gallong, gallat):
            dustpos_file.write('%f %f\n' % pos)
        dustpos_file.close()

        #command = 'dust_getval interp=y ipath=/Volumes/mosquitocoast/patrick/kpno/sfd/ infile=%s outfile=%s noloop=y' % (dustpos_filename, ebvgal_filename)            
        if pg10:
            command = 'value = dust_getval(infile=\'%s\',outfile=\'%s\',corrpg10=corrpg10,/interp,/pg10)\nopenw,1,"%s"\nprintf,1,corrpg10\nclose,1' % (dustpos_filename, ebvgal_filename, peekapplied_filename)            
        else:
            command = 'value = dust_getval(infile=\'%s\',outfile=\'%s\',/interp)' % (dustpos_filename, ebvgal_filename)            

        c = open('c.pro','w')
        c.write(command)
        c.close()
        command = 'idl < c.pro'
        print command
        os.system(command) 

        _isFileCorrupted = not (os.path.exists(ebvgal_filename) and os.path.getsize(ebvgal_filename) > 0)
        if _isFileCorrupted:
            raise RuntimeError('Dust file corrupted or not produced!')

        ebvgal_file = open(ebvgal_filename)
        ebv = scipy.array([float(lines.split()[2]) for lines in ebvgal_file.readlines()])
        if pg10:
            peekapplied_file = open(peekapplied_filename)
            peekapplied = scipy.array([float(lines.split()[0]) for lines in peekapplied_file.readlines()])
        else: peekapplied = None

        return ebv, scipy.array(gallong), scipy.array(gallat), peekapplied


    finally:
        cleanUp()

def convertradec(agalra,agaldec):
    import string

    if len(str(agalra).split(':')[0]) < 2:
        agalra = '0' + str(agalra)

    if len(str(agaldec).replace('-','').split(':')[0]) < 2:
        if string.find(str(agaldec),'-') != -1:
            agaldec = '-0' + str(agaldec).replace('-','') 
        else:
            agaldec = '0' + str(agaldec).replace('-','') 

    agalra = str(agalra).replace(':','')
    agaldec = str(agaldec).replace(':','')

    dlist = range(3)
    rlist = range(3)
    rlist[0] = agalra[0:2] 
    rlist[1] = agalra[2:4] 
    rlist[2] = agalra[4:] 

    if agaldec[0] != '-': agaldec = '+' + agaldec
    dsign = agaldec[0]
    print dsign
    dmul = float(dsign + '1')
    dlist[0] = agaldec[1:3] 
    dlist[1] = agaldec[3:5]
    dlist[2] = agaldec[5:] 
    if dlist[2] == '  ':
        dlist[2] = '00'
    print dlist, string.find( dlist[0], ' ')
    u = string.find( dlist[0], ' ')
    radeg = (360/24.0)*string.atof(rlist[0]) + (360.0/(24.0*60))*string.atof(rlist[1]) + (360.0/(24.0*60.0*60.0))*string.atof(rlist[2])         
    decdeg = dmul * (string.atof(dlist[0]) + (1/60.0)*string.atof(dlist[1]) + string.atof(dlist[2])*(1/(60.0*60.0))                           )

    return radeg, decdeg

def getradec(file):

    import commands, math, string, re, os
    out = commands.getoutput('gethead ' + file + ' RA DEC')
    print out
    agalra, agaldec = re.split('\s+',out)
    print commands.getoutput('gethead ' + file + ' OBJECT')

    print commands.getoutput('gethead ' + file + ' CRVAL1 CRVAL2 CRPIX1 CRPIX2')

    radeg, decdeg = convertradec(agalra, agaldec)
    EPOCH = commands.getoutput('gethead ' + file + ' EPOCH')
    epoch = EPOCH.replace(' ','')

    import ephem
    m = ephem.Equatorial(str(radeg*(24./360.)),str(decdeg),epoch=epoch)
    m2000 = ephem.Equatorial(m,epoch='2000.0')
    aradeg_2000, adecdeg_2000 = (m2000.ra), (m2000.dec)
    radeg_2000, decdeg_2000 = convertradec(aradeg_2000, adecdeg_2000)

    print agalra, aradeg_2000, agaldec, adecdeg_2000

    print radeg, radeg_2000, decdeg, decdeg_2000


    return radeg, decdeg


def solve(file,radeg,decdeg):
    import os


    import random
    n  = str(int(random.random()*100000))



    os.system('rm cancel' + n)



    command = 'solve-field --new-fits none --cancel cancel' + n + ' --match none --rdls none --keep-xylist none --corr none --skip-solved --no-verify --no-plots --overwrite --scale-units arcminwidth --scale-low 7 --scale-high 13  --no-tweak --ra ' + str(radeg) + ' --dec ' + str(decdeg) + ' --radius 0.4 --skip-solved --solved ./wcs/' + file.replace("./",'').replace('.fits','.wcs') + ' --wcs ./wcs/' + file.replace("./",'').replace('.fits','.wcs') + ' ' + file

    import subprocess, time

    import time
    solved = False


    
    fcancel = open('./wcs/' + file.replace("./",'').replace('.fits','.running'),'w')
    fcancel.write('cancel')
    fcancel.close()




    try:
        print command
        p = subprocess.Popen(command,shell=True)                       
        for increment in range(1200 * 20):
            time.sleep(0.05)      
            if increment % 100 == 0: print (increment / 20), 'seconds', p.poll()
            if p.poll() is not None:
                solved = True
                break
    except KeyboardInterrupt:
        print 'continuing'

    #if solved == False:
    fcancel = open('cancel' + n,'w')
    fcancel.write('cancel')
    fcancel.close()
    print 'cancelled'
    print 'finished'
    #os.system('rm ' + './wcs/' + file.replace("./",'').replace('.fits','.running'))
    import time

    return radeg, decdeg

def run_first():
    from glob import glob
    import commands, os

    #for pattern in ['Mar5_binned_269','Mar9_binned_269','Mar9_unbinned_269']:

    for pattern in ['work_unbinned_269','work_binned_269']: #,'Oct4_binned_269','Oct6_unbinned_269','Oct6_binned_269']: #'May3_binned_269','May3_unbinned_269','May4_binned_269','May4_unbinned_269','May5_binned_0','May5_unbinned_0','May6_binned_0','May6_unbinned_0',]:
        os.system('mkdir -p ./wcs/' + pattern)
        fs = glob('./' + pattern + '/a*.fits') #+ glob('./Mar5_unbinned_269/a008*.fits') + glob('./Mar5_unbinned_269/a010*.fits')                                                 
        for f in fs: 
            out = commands.getoutput('gethead ' + f + ' IMAGETYP')
            object = commands.getoutput('gethead ' + f + ' OBJECT')
            print object
            print out
            import string
            running = './wcs/' + f.replace("./",'').replace('.fits','.running').replace('.fringe','')
            wcs = './wcs/' + f.replace("./",'').replace('.fits','.wcs').replace('.fringe','')
            if not glob(wcs) and not glob(running) and string.find(out,'object') != -1 and string.find(object,'flat') == -1 and string.find(object,'focus') == -1 and string.find(object,'zero')==-1:
                radeg, decdeg = getradec(f)
                solve(f,radeg,decdeg)



def find_astrom(dirname='work',bintype='binned',rotangle_num='269'):
    #import reduce_im 
    #filt_dict, rotangle_num = reduce_im.get_info(dirname) 
    from glob import glob
    pattern = './' + dirname + '_' + bintype + '_' + rotangle_num + '/a*.fits'
    fs = glob(pattern)
    print fs, pattern

    import commands
    obs_dict = {} 
    obs = []
    obs_group=[]
    for f in fs: 
        out = commands.getoutput('gethead ' + f + ' IMAGETYP')
        object = commands.getoutput('gethead ' + f + ' OBJECT')
        filt = commands.getoutput('gethead ' + f + ' FILTERS')
        print f
        print object
        print out
        import string
        if string.find(out,'object') != -1 and string.find(object,'BAD') == -1 and string.find(f,'bgsub') == -1 and string.find(f,'seg') == -1:
            if filt == 'z' and string.find(f,'fringe') == -1:
                f = f.replace('.fits','.fringe.fits')

            telra, teldec = getradec(f)
            WCSOK = commands.getoutput('gethead ' + f + ' WCSOK')
            jd = commands.getoutput('gethead ' + f + ' JD')
            import os
            os.system('mv ./wcs/'  + f.replace('.fits','.wcs') + ' ./wcs/'  + f.replace('.fits','.wcs').replace('.fringe',''))
            if glob('./wcs/' + f.replace('.fits','.wcs').replace('.fringe','')) or len(WCSOK) > 0:
                wcs = True
                #if not glob('./wcs/'  + f.replace('.fits','.wcs')):
                    #import os
                    #os.system('cp ' + f + ' ' + './wcs/'  + f.replace('.fits','.wcs').replace('.fringe',''))
            else: wcs = False
            obs.append({'file':f,'wcs':wcs,'ra':telra,'dec':teldec,'jd':float(jd)})

    obs_group.append(obs)

    print obs
    print obs_group


    obs_good = filter(lambda x: x['wcs'],obs)

    print obs_good

    import scipy
    for i in range(len(obs)):

        if True: #obs[i]['file'] == './work_binned_269/a*.fits':
            WCSOK = commands.getoutput('gethead ' + obs[i]['file'] + ' WCSOK')                                                                                                                                      
            OBJECT = commands.getoutput('gethead ' + obs[i]['file'] + ' OBJECT FILTERS')
            print WCSOK, len(WCSOK), OBJECT, obs[i]['file']
            if not len(WCSOK): # and string.find(obs[i]['file'],'a0215') != -1:
                if not obs[i]['wcs']:                                                                                                                                                         

                    print obs[i]['ra'], obs[i]['dec']
                    dists = [] 
                    for a in obs:
                        dist = ((obs[i]['ra'] - a['ra'])**2. + (obs[i]['dec'] - a['dec'])**2. )**0.5
                        dists.append(dist)
                    print dists
                    ref = zip(dists,obs)
                              
                    ''' find good observations taken on same night '''
                    obs_good = filter(lambda x: x[1]['wcs'] and abs(x[1]['jd'] - obs[i]['jd']) < 0.5, ref)
                                                                                                                                                                                                                    
                    print obs_good, obs[i]
                    obs_good.sort()
                    print obs_good, '1'
                    
                    print obs_good                                                                                                                                                                                                
                    print obs_good[0], obs[i]   

                    wcs_f = './wcs/' + obs_good[0][1]['file'].replace('.fringe','').replace('.fits','.wcs')
                    if not glob(wcs_f):
                        os.system('cp ' + obs_good[0][1]['file'] + ' ' + wcs_f)
                    #    print wcs_f, 'link'
                                                                                                                                                                                                                    
                    
                    import os
                    command = 'gethead ./wcs/' + obs_good[0][1]['file'].replace('.fringe','').replace('.fits','.wcs') + ' CRVAL1'
                    print command
                    crval1 = commands.getoutput(command)
                    print crval1
                             
                    command = 'gethead ./wcs/' + obs_good[0][1]['file'].replace('.fringe','').replace('.fits','.wcs') + ' CRVAL2'
                    print command
                    crval2 = commands.getoutput(command)
                                                                                                                                                                                              
                                                                                                                                                                                              
                    EPOCH = commands.getoutput('gethead ' + obs_good[0][1]['file'] + ' EPOCH')
                    epoch = EPOCH.replace(' ','')
                                                                                                                                                                                              
                    ''' convert RA and DEC to obsevation epoch '''
                    import ephem
                    print crval1, crval2
                    m = ephem.Equatorial(str(float(crval1)*(24./360.)),str(crval2),epoch='2000.0')
                    mepoch = ephem.Equatorial(m,epoch=epoch)
                    acrval1_obs, acrval2_obs= (mepoch.ra), (mepoch.dec)
                    crval1_obs, crval2_obs = convertradec(acrval1_obs, acrval2_obs)
                                                                                                                                                                                              
                    crval1_new_obs = obs[i]['ra'] - obs_good[0][1]['ra'] + float(crval1_obs)
                    crval2_new_obs = obs[i]['dec'] - obs_good[0][1]['dec'] + float(crval2_obs)
                                                                                                                                                                                              
                    import ephem
                    m = ephem.Equatorial(str(float(crval1_new_obs)*(24./360.)),str(crval2_new_obs),epoch=epoch)
                    m2000 = ephem.Equatorial(m,epoch='2000.0')
                    acrval1_new, acrval2_new = (m2000.ra),(m2000.dec)
                    crval1_new, crval2_new = convertradec(acrval1_new, acrval2_new)
                                                                                                                                                                                              
                    print obs_good[0][1]['ra']
                    print obs_good[0][1]['dec']
                    print obs[i]['ra'], obs[i]['dec']
                    print crval1_new, crval2_new, crval1, crval2, obs[i]
                    print obs_good[0][1], obs[i]
                    
                    command = 'sethead ' + obs[i]['file'] + " CRVAL1=" + str(crval1_new) + ""
                    os.system(command)
                    command = 'sethead ' + obs[i]['file'] + " CRVAL2=" + str(crval2_new) + ""
                    print command
                    os.system(command)

                    ''' need float header types, not string '''
                                                                                                                                                                                              
                    for key in ['CD1_1','CD1_2','CD2_1','CD2_2','CRPIX1','CRPIX2','EQUINOX']:
                        f2 = 'gethead ./wcs/' + obs_good[0][1]['file'].replace('.fringe','').replace('.fits','.wcs') + ' ' + key
                        print f2
                        val = commands.getoutput(f2)
                        command = 'sethead ' + obs[i]['file'] + ' ' + key + '=' + val #+ 'E+00'
                        print command
                        os.system(command)
                                                                                                                                                                                              
                    command = 'cphead ./wcs/' + obs_good[0][1]['file'].replace('.fringe','').replace('.fits','.wcs') + ' ' + obs[i]['file'] + ' WCSAXES LONPOLE LONGPOLE IMAGEW IMAGEH CTYPE1 CTYPE2 CUNIT1 CUNIT2'
                    print command
                    os.system(command)
                    diff = ((obs_good[0][1]['ra'] - obs[i]['ra'])**2. + (obs_good[0][1]['dec'] - obs[i]['dec'])**2.)**0.5
                    print diff, obs_good[0][1], obs[i]
                                                                                                                                                                                                                    
                    if diff < 10/3600.: 
                        import os
                        command = 'sethead ' + obs[i]['file'] + ' WCSOK=GOOD' 
                        print command
                        os.system(command)
                    else:
                        orchestrate(obs[i]['file'])
            
                    print diff

                else:
                    for key in ['CD1_1','CD1_2','CD2_1','CD2_2','CRPIX1','CRPIX2','CRVAL1','CRVAL2','EQUINOX']:
                        f2 = 'gethead ./wcs/' + obs[i]['file'].replace('.fringe','').replace('.fits','.wcs') + ' ' + key
                        print f2
                        val = commands.getoutput(f2)
                        command = 'sethead ' + obs[i]['file'] + ' ' + key + '=' + val #+ 'E+00'
                        print command
                        import os
                        os.system(command)
                                                                                                                                                                                              
                    command = 'cphead ./wcs/' + obs[i]['file'].replace('.fringe','').replace('.fits','.wcs') + ' ' + obs[i]['file'] + ' WCSAXES LONPOLE LONGPOLE IMAGEW IMAGEH CTYPE1 CTYPE2 CUNIT1 CUNIT2 '
                                                                                                                                                                                              
                    print command
                    os.system(command)
                    status = test_scamp(obs[i]['file'])    
                                                                                                                                                                                              
                command = 'sethead ' + obs[i]['file'] + " NAXIS=2"
                os.system(command)


def test_scamp(file):

    import os

    os.system('rm test.cat')


    
    nnw = os.environ['util'] + '/default.nnw'
    params = os.environ['kpno'] + '/process_kpno/default.param'
    config = os.environ['kpno'] + '/process_kpno/config'
    conv = os.environ['util'] + '/default.conv'

    command = 'sex ' + file + ' -c ' + config + ' -CATALOG_NAME test.cat '   + ' -STARNNW_NAME ' + nnw + ' -PARAMETERS_NAME ' + params + ' -FILTER_NAME ' + conv

    print command

    os.system(command)


    config_scamp = os.environ['kpno'] + '/process_kpno/config_scamp' 

    os.system('rm test.head')

    command = 'scamp test.cat -c ' + config_scamp
    print command

    os.system(command)

    f = open('test.head').readlines()
    d = {}
    for l in f:
        a = l.split('=')
        if len(a) == 2:
            try:
                d[a[0]] = float(a[1].split('/')[0])
            except: print
    if (d['ASTRRMS1'] < 0.001/3600) or (d['ASTRRMS1'] > 1.2/3600):        
        good = False
    else: good = True

    print good, d['ASTRRMS1']

    print d['ASTRRMS1'], d['ASTRRMS1']

    command = 'delhead ' + file + ' WCSOK'
    print command
    os.system(command)
    print file

    if good:
        import os
        command = 'sethead ' + file + ' WCSOK=GOOD'
        print command
        os.system(command)

    print file , good, d

    return good 

def return_cat(cat='test.cat'):
    import astropy.io.fits as pyfits
    p = pyfits.open(cat)
    a = [[p[2].data.field(x)[i] for x in ['FLUX_RADIUS','ALPHA_J2000','DELTA_J2000','MAG_ISO']] for i in range(len(p[2].data))]
    a.sort()
    a.reverse()

    return a    

def orchestrate(file):
    ''' here we pick out the five brightest galaxies in the frame as the potential host galaxies, whose coordinates we know '''
    import commands, string
    object = commands.getoutput('gethead ' + file + ' OBJECT')
    import re
    res = re.split('\s+',object)
    print res
    snpath = False
    for i in res: 
        if string.find(i,'sn') != -1:
            snpath = i
        elif string.find(i,'20') != -1 or string.find(i,'19') != -1:
            snpath = 'sn' + i

    if snpath or string.find(i,'M87')!=-1:
        print snpath                                                             
        import colorlib
        import anydbm        
        if string.find(i,'M87')!=-1:
            galra, galdec =  187.7059304,  12.3911231
        elif string.find(i,'RXJ')!=-1:
            galra, galdec =  162.0147,  31.6429 
        else:
            colorlib.asiago(snpath)
            colorlib.galaxyposition(snpath)
            gh = anydbm.open(snpath)                                      
            galra, galdec = float(gh['galradeg']), float(gh['galdecdeg'])
                                                                                 
        status = test_scamp(file)    
                                                                                 
        if not status:
            a = return_cat()
        
            for gal in a[0:5]:
                    
                import os
                command = 'gethead ' + file + ' CRVAL1'
                print command
                crval1 = commands.getoutput(command)
                print crval1
                                                                                 
                command = 'gethead ' + file + ' CRVAL2'
                print command
                crval2 = commands.getoutput(command)
                                                                                 
                print gal
                                                                                 
                crval1_new = galra - gal[1] + float(crval1)
                                                                                 
                crval2_new = galdec - gal[2] + float(crval2) 
                                                                                 
                print galra, gal[1], crval1
                                                                                 
                command = 'sethead ' + file + ' CRVAL1=' + str(crval1_new)
                os.system(command)
                command = 'sethead ' + file + ' CRVAL2=' + str(crval2_new)
                os.system(command)
                                                                                 
                status = test_scamp(file)
                                                                                 
                
                                                                                 
                if status: 
                    print file, status
                    import os
                    #os.system('cp ' + file + ' ./wcs/' + file.replace('.fits','.wcs').replace('.fringe',''))
                    break
                                                                                 
        return status
                                                                                 
def group_SN(dirname='work',bintype='binned',time_split=False,rotangle_num='269'):            
    import commands, os, string, re
    #filt_dict, rotangle_num = reduce_im.get_info(dirname) 
    from glob import glob

    fs = []
    for bintype in ['binned','unbinned']:
        fs += glob('./' + dirname + '_' + bintype + '_' + rotangle_num + '/a*.fits')

    print fs


    dict = {}
    for f in fs:

        object = commands.getoutput('gethead ' + f+ ' OBJECT')            
        filter = commands.getoutput('gethead ' + f+ ' FILTERS')            
        exptime = commands.getoutput('gethead ' + f+ ' EXPTIME')            
        if filter == 'z' and string.find(f,'fringe') == -1:
            WCSOK = commands.getoutput('gethead ' + f.replace('.fits','.fringe.fits')+ ' WCSOK')            
        else: 
            WCSOK = commands.getoutput('gethead ' + f + ' WCSOK')            

                                                                              
        if float(exptime) > 20. and len(WCSOK) and string.find(object,'zero') == -1 and string.find(object,'focus') == -1 and string.find(f,'fringe') == -1 and string.find(object,'flat') == -1: 
            import re
            if string.find(object,'M87') != -1: snpath = 'M87'
            elif string.find(object,'RXJ') != -1: snpath = 'RXJ1048'
            elif object[0:3] == 'R11': snpath = 'R1142'
            elif object[0:3] == 'R034': snpath = 'R0340'
            elif object[0:3] == 'R030': snpath = 'R0308'
            elif object[0:3] == 'R002': snpath = 'R0023'
            else: 
                res = re.split('\s+',object)
                snpath = res[0]
                if snpath[0:2] != 'sn' and (snpath[0:2]=='19' or snpath[0:2]=='20'): snpath = 'sn' + snpath

            print snpath, object, res

            JD = float(commands.getoutput('gethead ' + f+ ' JD')            )

            key_current = None

            if time_split:
                current_number = 0
                for key in dict.keys():                                           
                    snpath_key, number = key.split('_')
                    if snpath_key == snpath:
                        if number > current_number: 
                            current_number = int(number)
                        if abs(float(dict[key]['JD']) - JD) < 2./24.: 
                            key_current = key
                            break
                if key_current is None:
                    key_current = snpath + '_' + str(current_number + 1)
                    dict[key_current] = {}
                    dict[key_current]['JD'] = JD
                    dict[key_current]['IMAGES'] = []
        
            else:
                key_current = snpath
                if not dict.has_key(key_current): 
                    dict[key_current] = {}
                    dict[key_current]['IMAGES'] = []

            if filter == 'z' and string.find(f,'fringe') == -1:
                f = f.replace('.fits','.fringe.fits')
            dict[key_current]['IMAGES'].append([filter,f])

    print dict.keys()

    for key in dict.keys():
        os.system('mkdir ./' + dirname + '_night/' + key)
        for filter, f in dict[key]['IMAGES']:
            os.system('mkdir -p ./' + dirname + '_night/' + key + '/' + filter + '_raw')
            #os.system('rm ' + ' ./' + dirname + '_night/' + key + '/' + filter + '_raw/*fits')
            os.system('ln -s ../../../' + f + ' ./' + dirname + '_night/' + key + '/' + filter + '_raw/')

@entryExit        
def run_swarp(run,night,snpath,filters=['u','g','r','i','z']):
    from glob import glob
    import commands
    import os, string

    #run=os.getcwd().split('/')[-1]
    
    pattern = '/Volumes/mosquitocoast/patrick/kpno/' + run + '/' + night + '/' + snpath + ''
    print pattern        
    sns = glob(pattern)

    print sns

    #sns = ['1997do',  '1998dx',  '1999aw',  '2000bh',  '2000cf',  '2000cn',  '2001az',  '2001bf',  '2002ax',  '2002de',  '2002dj',  '2002hd',  '2002he',  '2003D',  '2003ch',  '2003fa',  '2005dv']

    #sns = ['1990O_2455265.93831']
    #sns = ['2002de_2455265.92582']
    print pattern
    print sns


    for sndir in sns:

        scale = '0.60'

        #os.chdir(orig_directory)

        import re
        res = re.split('/',sndir)            
        snpath = res[-1].split('_')[0]

        print snpath, 'snpath'

        
        import retrieve_2mass
        if string.find(snpath,'RXJ') == -1 and not glob('/Volumes/mosquitocoast/patrick/kpno/' + run + '/' + night + '/' + snpath + '/J_raw_bg/'):
            reload(retrieve_2mass).run(run,'work_night',snpath)

        if string.find(snpath,'RXJ') == -1:
            import get_sdss                                                                                          
            if not glob('/Volumes/mosquitocoast/patrick/kpno/' + run + '/' + night + '/' + snpath + '/SDSS_u_raw/'):
                found = reload(get_sdss).run(snpath)
                print found
                if found:
                    copy_images_sdss(run, night, snpath)
            else: found = True
        else: found = False

        #filters = ['J','u','g','r','i','z']
        #if found: filters += ['SDSS_u','SDSS_g','SDSS_r','SDSS_i','SDSS_z']


        pattern = sndir + '/*_raw' 
        filters = [x.split('/')[-1].replace('_raw','') for x in glob(pattern)]

        print filters

        #filters = ['SDSS_u','SDSS_g','SDSS_r','SDSS_i','SDSS_z']

        

    
        files = {}

        for filt in filters:
            #pattern = './' + dirname + '_night/' + sndir + '/' + filt + '_raw/*fits' 
            pattern = sndir + '/' + filt + '_raw/*fits' 
            print pattern
            fs = filter(lambda x: string.find(x,'cr.fits')==-1 and string.find(x,'weight.fits')==-1,glob(pattern))
            print fs
            fs = filter(lambda x: string.find(x,'resam') == -1,fs)
            if len(fs):
                files[filt] = fs


        
        import MySQLdb
        db2 = MySQLdb.connect(db='calib')
        c = db2.cursor()
        command = "UPDATE STATUS set FILTERS='" + reduce(lambda x,y: x + ',' + y,[z.replace('_','') for z in files.keys()]) + "' WHERE SN='" + snpath + "' and RUN='" + run + "'" # and FUNCTION='" + str(self.f.__name__) + "'" 
        print command 
        c.execute(command) 





        print files
            
        from glob import glob
        pattern = os.environ['sdss'] + '/sn' + snpath + '/g/regg.fits'
        print pattern
        sns = []

        if True: #snpath =='1996bv':                

            sns.append(snpath)

            if True:

                for file in fs:                                                                                                                                                                
                    detector = commands.getoutput('gethead ' + file + ' DETECTOR')
                    os.system('mkdir ' + sndir + '/u')
                    os.system('mkdir ' + sndir + '/g')
                    os.system('mkdir ' + sndir + '/r')
                    os.system('mkdir ' + sndir + '/i')
                    os.system('mkdir ' + sndir + '/z')
                    os.system('mkdir ' + sndir + '/J')
                                                                                                                                                                                               
                    if found:
                        os.system('mkdir ' + sndir + '/SDSS_u') 
                        os.system('mkdir ' + sndir + '/SDSS_g')
                        os.system('mkdir ' + sndir + '/SDSS_r')
                        os.system('mkdir ' + sndir + '/SDSS_i')
                        os.system('mkdir ' + sndir + '/SDSS_z')
                                                                                                                                                                                               
                if True:
                    #for filt in filters:                                                                                                                                   
                        #os.system('mkdir -p ' + sndir + '/' + filt + '_sdss')
                        #os.system('ln -s  ' + os.environ['sdss'] + '/sn' + snpath + '/' + filt + '/reg' + filt + '.fits ' + sndir + '/' + filt + '_sdss/reg.fits')
                                                                                                                                                                                         
                    headers = ['CRVAL1','CRVAL2','CRPIX1','CRPIX2','CD1_1','CD2_2','CD2_1','CD2_2']
                    import commands
                    info = commands.getoutput('gethead ' + os.environ['sdss'] + '/sn' + snpath + '/g/regg.fits ' + reduce(lambda x,y: x + ' ' + y, headers))
                    
                    import re
                    print info
                    res = re.split('\s+',info)
                    pairs = zip(headers,res)
                    if False:
                        hfile = file.replace('_raw','').replace('.fits','.head')  
                        print hfile
                        header = open(hfile,'w')                  
                        for key,value in pairs:
                            header.write(key + ' = ' + value +'\n')
                        header.write('END')
                        header.close()                
                                                                                                                                                                                     
                    os.system('rm ' + file.replace('_raw','').replace('.fits','.head'))
                                                                                                                                                                                     
                    command = 'ln -s  ' + os.environ['sdss'] + '/sn' + snpath + '/' + filt + '/reg' + filt + '.fits ' + file.replace('_raw','').replace('.fits','.head')
                    print command
                    os.system(command)
                                                                                                                                                                                               
                    #fs.append('/Volumes/mosquitocoast/patrick/sdss/sn2005da/2MASS/926645J.fits')                                                                                                   
                                                                                                                                                                                                   
                    for filt in files.keys():
                        for file in files[filt]:
                            from copy import copy
                            
                            nnw = os.environ['util'] + '/default.nnw'
                            params = os.environ['kpno'] + '/process_kpno/default.param'
                            config = os.environ['kpno'] + '/process_kpno/config'
                            conv = os.environ['util'] + '/default.conv'
                        
                            os.system('sex ' + file + ' -c ' + config + ' -CATALOG_NAME ' + file + '.cat '  + ' -STARNNW_NAME ' + nnw + ' -PARAMETERS_NAME ' + params + ' -FILTER_NAME ' + conv ) 
                            print file
                                                                                                                                                                                                   
                    config_scamp = os.environ['kpno'] + '/process_kpno/config_scamp' 
                    xml_file = os.environ['kpno'] + '/' + run + '/' + night + '/' + snpath + '/scamp.xml'
                    all_files = reduce(lambda x,y: x + y, files.values())
                    command = 'scamp ' + reduce(lambda x,y: x + ' ' + y, [x+'.cat' for x in all_files])  + ' -c ' + config_scamp + ' -ASTREF_CATALOG 2MASS -ASTREF_WEIGHT 5 -ASTRINSTRU_KEY DETECTOR -MATCH_RESOL 5.0 -XML_NAME ' + xml_file # -ASTRINSTRU_KEY INSTRUME'
                    print command
                    os.system(command)
                    print fs

                    xml_file = os.environ['kpno'] + '/' + run + '/' + night + '/' + snpath + '/scamp.xml'
                    temp = open(xml_file,'r').read().replace('datatype="*"','datatype="char"')

                    xml_fix = xml_file.replace('.xml','_fix.xml')                                                           
                    new_xml = open(xml_fix,'w')
                    new_xml.write(temp)
                    new_xml.close()
                                                                                                          
                    from vo.table import parse                     
                    votable = parse(xml_fix,pedantic=False)
                    index = 0
                    for table in votable.iter_tables():
                        print index
                        if index == 1:
                            astref = table.array['AstRef_Catalog'][0]
                            refSigma1, refSigma2 = table.array['AstromSigma_Reference'][0]
                            refSigma1_hSN, refSigma2_hSN = table.array['AstromSigma_Reference_HighSN'][0]
                        if index == 4:                            
                            if len(table.array['Msg']) > 0:
                                msg = reduce(lambda x,y: x + y, table.array['Msg'])
                            else: msg = ''
                        index += 1
                                                                                                          

                    gh = {}                                                                                                          
                    gh['astref'] = astref
                    gh['refSigmaone'] = str(refSigma1)
                    gh['refSigmatwo'] = str(refSigma2)
                    gh['refSigmaonehSN'] = str(refSigma1_hSN)
                    gh['refSigmatwohSN'] = str(refSigma2_hSN)
                    gh['scampmsg'] = msg
                                                                                                          

                    
                    import MySQLdb                                                                                                                                              
                    db2 = MySQLdb.connect(db='calib')
                    c = db2.cursor()

                    command = "SELECT * from ASTROM where SN='" + snpath + "' and RUN='" + run+ "'" 
                    print command
                    c.execute(command)                                                                                                       
                    results = c.fetchall()
                    if not len(results):
                        command = "INSERT INTO ASTROM (SN,RUN) VALUES ('" + snpath + "','" + run+ "')"
                        print command 
                        c.execute(command) 

                    for key in gh.keys():
                        command = "UPDATE ASTROM set " + key + "='" + str(gh[key]) + "' WHERE SN='" + snpath + "' and RUN='" + run + "'"  
                        print command 
                        c.execute(command)                                                                                                                       



                    print astref, refSigma1, refSigma2, refSigma1_hSN, refSigma2_hSN 




                    file = all_files[1] + '.head'
                    print file
                    f = open(file).readlines()                                                    
                    d = {}
                    for l in f:
                        a = l.split('=')
                        if len(a) == 2:
                            try:
                                d[a[0]] = float(a[1].split('/')[0])
                            except: print
                                                                                                                 
                    #print d['ASTRRMS1']*3600. , d['ASTRRMS2']*3600.



            import anydbm, colorlib

            if string.find(snpath,'M87')!=-1:
                ra, dec =  187.7059304,  12.3911231

            elif string.find(snpath,'RXJ')!=-1:
                ra, dec =  162.0147,  31.6429 

            else: 
                colorlib.asiago(snpath)
                colorlib.galaxyposition(snpath)
                gh = anydbm.open(snpath)
                ra = gh['galradeg']
                dec = gh['galdecdeg'] 
            factor = 1.


            for filt in files.keys(): 
                index = 0
                print files[filt], filt
                file_output = "/".join(files[filt][0].replace('_raw','').split('/')[:-1]) + '/reg' + '.fits'
                weight_output = "/".join(files[filt][0].replace('_raw','').split('/')[:-1]) + '/reg' + '.weight.fits'
                print file_output, weight_output
                os.system('mkdir -p ' + "/".join(files[filt][0].replace('_raw','').split('/')[:-1]))
                detector = commands.getoutput('gethead ' + files[filt][0] + ' DETECTOR')
                import pyraf
                from pyraf import iraf

                if string.find(filt,'J') == -1 and string.find(filt,'SDSS') == -1:

                    back = ' -SUBTRACT_BACK Y '

                    pattern = "/".join(files[filt][0].replace('_raw','').split('/')[:-1]) + '/reg*.fits'
            
                    ''' first make individual coadds '''
                    index = 0

                    files_input = []
                    weights_input = []
                    exps = []
                    for file in files[filt]:
                        #file = files[filt][0]                                                                                            
                        index += 1
                        single_output = "/".join(files[filt][0].replace('_raw','').split('/')[:-1]) + '/reg' + str(index) + '.fits'
                        single_weight = "/".join(files[filt][0].replace('_raw','').split('/')[:-1]) + '/reg' + str(index) + '.weight.fits'

                        factor = '1'
                        base = '/Volumes/mosquitocoast/patrick/kpno/' + run + '/' 
                        flat_file = (base + commands.getoutput('gethead ' + file + ' FLATCOR').split('./')[1]).split('.f')[0] + '.fits' 
                        print flat_file, 'flat_file'


                        command ='gethead ' + file + '  EXPTIME'
                        print command
                                                                                                                                         
                        EXPTIME = commands.getoutput(command)
                        print file, EXPTIME
                        detector = commands.getoutput('gethead ' + file + ' DETECTOR')
                        CCDSUM = commands.getoutput('gethead ' + file + ' CCDSUM')
                        print detector, CCDSUM 

                        weight_file = file.replace('.fits','.weight.fits')
                        if detector == 't2kb':
                        
                            os.system('rm ' + weight_file)

                            bin = CCDSUM[0]                                                                                                                         
                            if run == 'kpno_Dec2010':
                                badpixel = os.environ['kpno'] + '/process_kpno/badpix_bin' + bin + '_dec2010_t2kb.fits'
                            else:
                                badpixel = os.environ['kpno'] + '/process_kpno/badpix_bin' + bin + '_t2kb.fits'        
                            print badpixel, weight_file
                            iraf.imarith(flat_file,'*',badpixel,weight_file)
                            print 'produced?',
                            print weight_file, badpixel, flat_file, detector
                        else: 
                            #weight_file = flat_file 
                            os.system('ln -s ' + flat_file + ' ' + weight_file)

                        files_input.append(file)
                        weights_input.append(weight_file)


                        os.system('sethead ' + file + ' FILES=' + file.split('/')[-1])

                        os.system('sethead ' + file + ' SATURATE=50000')

                        if CCDSUM == '2 2': BACK_SIZE = 100
                        else: BACK_SIZE = 200
                        #if run == 'kpno_May2010' and filt == 'z': BACK_SIZE=200 # residual gradients from using Oct. fringe correction

                        command = '/usr/local/bin/swarp ' + file + '  -PIXELSCALE_TYPE MANUAL -PIXEL_SCALE ' + scale + ' ' + back + '  -BACK_SIZE ' + str(BACK_SIZE) + ' -WEIGHT_IMAGE ' + weight_file + ' -WEIGHT_TYPE MAP_WEIGHT  -IMAGEOUT_NAME ' + single_output + '  -WEIGHTOUT_NAME ' + single_weight + ' -BLANK_BADPIXELS Y -COPY_KEYWORDS CCDSUM,AIRMASS,DATE-OBS,DETECTOR,JD,UT,ZD,MAGZP,SKYVAL,FILTERS,EXPTIME,FILES -FSCALE_KEYWORD NONE -FSCALE_DEFAULT ' + factor + ' -CENTER_TYPE MANUAL -CENTER ' + str(ra) + ',' + str(dec) + '  -IMAGE_SIZE 2500,2500 -HEADER_SUFFIX .fits.head -COMBINE_TYPE MEDIAN -FSCALASTRO_TYPE FIXED'  
                        print command
        
                        os.system(command)

                        single_flag = single_output.replace('.fits','.flag.fits')

                        command = 'ww -WEIGHT_NAMES ' + single_weight + ' -WEIGHT_MIN 0.0001 -WEIGHT_MAX 1000000 -FLAG_NAMES "" -OUTFLAG_NAME ' + single_flag 
                        print command
                        os.system(command)
                        print 'finished'

                        print single_output, single_weight, file
            
                        exps.append([float(EXPTIME) , single_output, single_weight, single_flag, file])

                    ''' make a coadd for all images '''


                    ''' get relative zps of input images '''

                    if len(exps) == 1:

                        exptime, image, weight_image, flag_image, file = exps[0] 

                        dateobs = commands.getoutput('gethead ' + image + ' DATE-OBS')

                        ims = [{'dateobs': dateobs, 'average':0.0, 'fwhm':-99, 'image':image, 'flag':image.replace('.fits','.flag.fits'), 'weight': image.replace('.fits','weight.fits'), 'file':file}]

                    else: 

                        exps.sort(reverse=True) # with REVERSE
                    
                        ''' pick out longest exposure as detection image '''
                    
                        detect_image = exps[0][1]

                        dummy = open('dummy.list','w')
                        dummy.write('1 -9999 -9999\n')
                        dummy.close()

                        ims = []

                        ''' APERTURE corrections taken into account here '''
                        for exptime, image, weight_image, flag_image, file in exps:

                            catalog = image + '.swarp.cat' 
                            add = ' -WEIGHT_TYPE MAP_WEIGHT,MAP_WEIGHT -WEIGHT_IMAGE ' + detect_image.replace('.fits','.weight.fits') + ',' + image.replace('.fits','.weight.fits') + ' -MAG_ZEROPOINT 0 '
                            command = '/usr/local/bin/sex ' + detect_image + ',' + image + ' -c ' + assoc_config + '  -CATALOG_NAME ' + catalog + add  +  ' -FLAG_IMAGE ' + image.replace('.fits','.flag.fits') + ' -ASSOC_DATA 1 -ASSOC_NAME dummy.list -ASSOC_PARAMS 2,3 -ASSOC_RADIUS 3 -ASSOC_TYPE NEAREST -ASSOCSELEC_TYPE ALL' 
                            print command
                            os.system(command)


                            ''' measure psf '''

                            
                            fwhm = image.replace('.fits','.fwhm')
                            ellip = image.replace('.fits','.ellip')
                            xml = image.replace('.fits','.xml')
                            psfdir = reduce(lambda x,y: x+ y, ['/' + z for z in image.split('/')[:-1]]) + '/'

                            fwhm_psfex, fwhm_psfex_min, fwhm_psfex_max, beta_psfex, chi2_psfex, ellipticity_psfex, asymmetry_psfex, aperture_corr = extract_psf(catalog, fwhm, ellip, xml, psfdir, filt)

                            print image, fwhm_psfex, beta_psfex, chi2_psfex, aperture_corr
                            import astropy.io.fits as pyfits, scipy

                            print pyfits.open(detect_image + '.swarp.cat')[2].columns
                            p_detect = pyfits.open(detect_image + '.swarp.cat')[2].data
                            mask_detect = scipy.logical_and(p_detect.field('FLAGS')==0,p_detect.field('IMAFLAGS_ISO')==0)

                            p_image = pyfits.open(image + '.swarp.cat')[2].data
                            mask_image = scipy.logical_and(p_image.field('FLAGS')==0,p_image.field('IMAFLAGS_ISO')==0)

                            mask = scipy.logical_and(mask_detect,mask_image)


                            if image == detect_image:
                                detect_apercorr = aperture_corr

                            print p_image.field('MAG_APER') , aperture_corr , p_detect.field('MAG_APER') , detect_apercorr, mask
                            diff = p_image[mask].field('MAG_APER') - aperture_corr - (p_detect[mask].field('MAG_APER') - detect_apercorr)
                            errors =  (p_image[mask].field('MAGERR_APER')**2. + p_detect[mask].field('MAGERR_APER')**2.)**0.5
                        
                            average = av_difference(diff, errors)  

                            dateobs = commands.getoutput('gethead ' + image + ' DATE-OBS')

                            ims.append({'dateobs': dateobs, 'average':average, 'fwhm':fwhm_psfex, 'image':image, 'flag':image.replace('.fits','.flag.fits'), 'weight': image.replace('.fits','.weight.fits'), 'file': file})

                        def sortit(x,y,key='average'):    
                            if x[key] < y[key]:
                                return 1
                            else: return -1
                                                          
                            
                        ims.sort(cmp=sortit,reverse=True)
                                                          
                        print ims

                    print ims
                    files_input = [a['file'] for a in ims] 
                    weights_input = [a['file'].replace('.fits','.weight.fits') for a in ims] 
                    relzps_input = [a['average'] for a in ims] 

                    print files_input, weights_input, exps

                    weight_file = reduce(lambda x,y: x + ',' + y, [p for p in weights_input])
                    file = reduce(lambda x,y: x + ',' + y, files_input)
                    factor = reduce(lambda x,y: x + ',' + y, [str(10.**(float(z)/2.5)) for z in relzps_input]) # positive sign here; if you have a negative relzp, want to multiply by a number less than one to scale the flux down

                    fs = reduce(lambda x,y: x + ',' + y, [f.split('/')[-1] for f in files_input])
                    os.system('sethead ' + file + ' FILES=' + fs)

                    if CCDSUM == '2 2': BACK_SIZE = 100
                    else: BACK_SIZE = 200

                    command = '/usr/local/bin/swarp ' + file + '  -PIXELSCALE_TYPE MANUAL -PIXEL_SCALE ' + scale + ' ' + back + '  -BACK_SIZE ' + str(BACK_SIZE) + ' -WEIGHT_IMAGE ' + weight_file + ' -WEIGHT_TYPE MAP_WEIGHT  -IMAGEOUT_NAME ' + file_output + '  -WEIGHTOUT_NAME ' + weight_output + ' -BLANK_BADPIXELS Y -COPY_KEYWORDS CCDSUM,AIRMASS,DATE-OBS,DETECTOR,JD,UT,ZD,MAGZP,SKYVAL,FILTERS,FILES -FSCALE_KEYWORD NONE -FSCALE_DEFAULT ' + factor + ' -CENTER_TYPE MANUAL -CENTER ' + str(ra) + ',' + str(dec) + '  -IMAGE_SIZE 2500,2500 -HEADER_SUFFIX .fits.head -COMBINE_TYPE WEIGHTED -FSCALASTRO_TYPE FIXED'  
                    print command
                    os.system(command)

                    ''' rerun with larger size background subtraction '''
                    if CCDSUM == '2 2': BACK_SIZE = 1000
                    else: BACK_SIZE = 2000
                    command = '/usr/local/bin/swarp ' + file + '  -PIXELSCALE_TYPE MANUAL -PIXEL_SCALE ' + scale + ' ' + back + '  -BACK_SIZE ' + str(BACK_SIZE) + ' -WEIGHT_IMAGE ' + weight_file + ' -WEIGHT_TYPE MAP_WEIGHT  -IMAGEOUT_NAME ' + file_output.replace('.fits','.back.fits') + '  -WEIGHTOUT_NAME ' + weight_output + ' -BLANK_BADPIXELS Y -COPY_KEYWORDS CCDSUM,AIRMASS,DATE-OBS,DETECTOR,JD,UT,ZD,MAGZP,SKYVAL,FILTERS,FILES -FSCALE_KEYWORD NONE -FSCALE_DEFAULT ' + factor + ' -CENTER_TYPE MANUAL -CENTER ' + str(ra) + ',' + str(dec) + '  -IMAGE_SIZE 2500,2500 -HEADER_SUFFIX .fits.head -COMBINE_TYPE WEIGHTED -FSCALASTRO_TYPE FIXED'  
                    print command
                    os.system(command)


                    command = 'ww -WEIGHT_NAMES ' + weight_output + ' -WEIGHT_MIN 0.0001 -WEIGHT_MAX 1000000 -FLAG_NAMES "" -OUTFLAG_NAME ' + file_output.replace('.fits','.flag.fits') 
                    print command
                    os.system(command)
                    print single_output, single_weight, file, weight_output, 'HERE'

                    ''' resample to SDSS size '''
                    if CCDSUM == '2 2': BACK_SIZE = 4000
                    else: BACK_SIZE = 4000

                    if True: # #sdss_file:
                        sdss_file = glob(os.environ['sdss'] + '/' + snpath + '/g/regg.fits')
                        if sdss_file:
                            scale_sdss = get_scale(sdss_file[0])                           
                        else: 
                            scale_sdss = 0.39591065735999997 

                        command = '/usr/local/bin/swarp ' + file + '  -PIXELSCALE_TYPE MANUAL ' + back + '  -BACK_SIZE ' + str(BACK_SIZE) + ' -WEIGHT_IMAGE ' + weight_file + ' -WEIGHT_TYPE MAP_WEIGHT  -IMAGEOUT_NAME ' + file_output.replace('.fits','.sdss.fits') + '  -WEIGHTOUT_NAME ' + weight_output.replace('weight.fits','sdss.weight.fits') + ' -BLANK_BADPIXELS Y -COPY_KEYWORDS CCDSUM,AIRMASS,DATE-OBS,DETECTOR,JD,UT,ZD,MAGZP,SKYVAL,FILTERS,FILES -FSCALE_KEYWORD NONE -FSCALE_DEFAULT ' + factor + ' -HEADER_SUFFIX .fits.head -COMBINE_TYPE WEIGHTED -FSCALASTRO_TYPE FIXED  -CENTER_TYPE MANUAL -CENTER ' + str(ra) + ',' + str(dec) + '  -IMAGE_SIZE 1500,1500 -PIXEL_SCALE ' + str(scale_sdss) 
                        print command
                        os.system(command)
                        print 'coadding'

                    command = 'ww -WEIGHT_NAMES ' + weight_output + ' -WEIGHT_MIN 0.0001 -WEIGHT_MAX 1000000 -FLAG_NAMES "" -OUTFLAG_NAME ' + file_output.replace('.fits','.flag.fits') 
                    print command
                    os.system(command)
                    print single_output, single_weight, file, weight_output, 'HERE'

                else: 
                    
                    file = reduce(lambda x,y: x + ',' + y, files[filt])
                    from pyraf import iraf

                    ''' make weight files for 2mass data '''

                    for f in files[filt]:
                        import scipy, pyfits                                                                             
                        rawim = pyfits.open(f.replace('J_raw','J_raw_bg'))[0].data
                        map = scipy.ones(rawim.shape) 
                        map[scipy.isnan(rawim)] = 0
                                                                                                                         
                        fitsobj = pyfits.HDUList()
                        hdu = pyfits.PrimaryHDU()
                        hdu.data = map 
                        fitsobj.append(hdu)
                        os.system('rm ' + f.replace('.fits','.weight.fits'))
                        fitsobj.writeto(f.replace('.fits','.weight.fits'))

                        ''' 2MASS saturation value '''
                        if string.find(filt,'J') != -1:
                            os.system('sethead ' + f + ' SATURATE=40000')

                    weight_file = reduce(lambda x,y: x + ',' + y, [p.replace('.fits','.weight.fits') for p in files[filt]])

                    print weight_file


                    zps = [] 
                    #backgrounds = []
                    for f in files[filt]:
                        zp= get_zp_SDSS(f)
                        zps.append(zp)
                        #backgrounds.append(background*(' + scale + ')**2.)
    
                    factors = []
                    for i in range(len(files[filt])):
                        factors.append(str(pow(10,-1.*(zps[i]-zps[0])/2.5)))
                       

                    factor = reduce(lambda x,y: x + ',' + y, factors)
                    #bgs = reduce(lambda x,y: x + ',' + y, [str(b) for b in backgrounds])
                    #back = ' -BACK_TYPE MANUAL -BACK_DEFAULT ' + str(bgs) + ' '
                    back = ' -SUBTRACT_BACK Y '

                    command = '/usr/local/bin/swarp ' + file + '  -PIXELSCALE_TYPE MANUAL -PIXEL_SCALE ' + scale + ' ' + back + '  -BACK_SIZE 1000 -WEIGHT_IMAGE ' + weight_file + ' -WEIGHT_TYPE MAP_WEIGHT  -IMAGEOUT_NAME ' + file_output + '  -WEIGHTOUT_NAME ' + weight_output + ' -BLANK_BADPIXELS Y -COPY_KEYWORDS MAGZP,SKYVAL,FILTERS -FSCALE_KEYWORD NONE -FSCALE_DEFAULT ' + factor + ' -CENTER_TYPE MANUAL -CENTER ' + str(ra) + ',' + str(dec) + '  -IMAGE_SIZE 2500,2500 -HEADER_SUFFIX .fits.head'  
                    print command
                    os.system(command)
                    command = 'ww -WEIGHT_NAMES ' + weight_output + ' -WEIGHT_MIN 0.0001 -WEIGHT_MAX 1000000 -FLAG_NAMES "" -OUTFLAG_NAME ' + file_output.replace('.fits','.flag.fits') 
                    print command
                    os.system(command)




        




def sdss_cat(ra,dec,rad=20):   

    query = 'select top 500 ccFlag, t.j as psfmag_J, sqrt(1/t.jivar) as psfmagerr_J, s.psfmag_u, s.psfmag_g, s.psfmag_r, s.psfmag_i, s.psfmag_z, s.psfmagerr_u, s.psfmagerr_g, s.psfmagerr_r, s.psfmagerr_i, s.psfmagerr_z from twomass as t, dbo.fGetNearbyObjEq(' + str(ra) + ',' + str(dec) + ',' + str(rad) +') as p, star as s where t.objID=s.objID and s.objID=p.objID and t.jivar != 0 and flags & dbo.fPhotoFlags(\'BLENDED\') = 0 and ccFlag = "000" order by p.distance'

    import sqlcl                                                    
    lines = sqlcl.query(query).readlines()
    print lines
    print lines[0]        
    keys = lines[0][:-1].split(',')
    sdss = []
    if lines[0] != 'No objects have been found':
        for l in lines[1:]:           
            d = dict(zip(keys,[float(x) for x in l.split(',')]))
            #d['stripe'] = d['dbo.fStripeOfRun(run)']
            sdss.append(d)
    else:
        sdss = [] 

    return sdss



def sdss_coverage(ra,dec,rad=0.2):
    import commands, string

    keys = ['ra','dec','psfMag_u', 'psfMagErr_u','psfMag_g', 'psfMagErr_g','psfMag_r', 'psfMagErr_r','psfMag_i', 'psfMagErr_i','psfMag_z', 'psfMagErr_z']

    keys += ['petroMag_u', 'petroMagErr_u','petroMag_g', 'petroMagErr_g','petroMag_r', 'petroMagErr_r','petroMag_i', 'petroMagErr_i','petroMag_z', 'petroMagErr_z','dbo.fStripeOfRun(run)']

    query = 'select ' + reduce(lambda x,y: x + ',' + y, keys) + ' from star where ra between ' + str(ra-rad) + ' and ' + str(ra+rad) + ' and dec between ' + str(dec-rad) + ' and ' + str(dec+rad) + " AND flags & dbo.fPhotoFlags('BLENDED') = 0" 
    print query
    import sqlcl
    lines = sqlcl.query(query).readlines()
    print lines        
    sdss = []
    if lines[0] != 'No objects have been found':
        for l in lines[1:]:           
            d = dict(zip(keys,[float(x) for x in l.split(',')]))
            d['stripe'] = d['dbo.fStripeOfRun(run)']
            sdss.append(d)
    else:
        sdss = [] 

    return sdss


def vizier(ra,dec,catalog):
    #output = '/tmp/' + str(ra) + str(dec)
    command = 'vizquery -mime=fits -source=2MASS-PSC -c="' + str(ra) + ' ' + str(dec) + '" -c.rm=15 > ' + catalog 
    import astropy.io.fits as pyfits, os    
    print command
    import commands
    out = commands.getoutput(command)
    print out
    p = pyfits.open(catalog)

    data = p[1].data
    keys=['RAJ2000','DEJ2000','Jmag','e_Jmag','Cflg','Qflg','Rflg','Bflg','Xflg']
    array = []
    for i in range(len(data)):
        d = dict(zip(['ra','dec','Jmag','e_Jmag','Cflg','Qflg','Rflg','Bflg','Xflg'],[data.field(key)[i] for key in keys]))
        array.append(d)

    #os.system('rm ' + output)

    print p[1].columns
    return array 

def get_image_dict(run,night,snpath,colors=['g','J','u','r','i','z','SDSS_u','SDSS_g','SDSS_r','SDSS_i','SDSS_z']):
    image_dict = {}
    ''' run sextractor on each band '''
    for color in colors:
        from glob import glob
        pattern = '/Volumes/mosquitocoast/patrick/kpno/' + run + '/' + night + '/' + snpath + '/' + color + '/reg?.fits' 
        ims = glob(pattern)
        image_dict[color] = {'singles':[],'coadd':None}
        for image in ims:
            name = image.split('/')[-1].split('.fits')[0]
            image_dict[color]['singles'].append([name,image])
        image_dict[color]['coadd'] = [['reg','/Volumes/mosquitocoast/patrick/kpno/' + run + '/' + night + '/' + snpath + '/' + color + '/reg.fits']]
    return image_dict


@entryExit
def run_sextractor(run,night,snpath):
    import re, commands, pyfits, os

    ''' delete output cat '''
    output_cat= '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/photometry.fits' 
    os.system('rm ' + output_cat)


    #ra, dec = 108.87, 23.42 

    ''' first retrieve 2MASS measurements '''

    base = '/Volumes/mosquitocoast/patrick/kpno/' + run + '/' + night + '/' + snpath + '/'
    detect_image = '/Volumes/mosquitocoast/patrick/kpno/' + run + '/' + night + '/' + snpath + '/g/reg.fits'
    print detect_image
    ra, dec = [float(x) for x in re.split('\s+',commands.getoutput('gethead ' + detect_image + ' CRVAL1 CRVAL2'))]

    def mk_match(array, listfile):
        posfile = open('posfile','w')                                                
        for a in array:
            #print a
            posfile.write(str(a['ra']) + ' ' + str(a['dec']) + '\n')
        posfile.close()
                                                                                     
        import commands
        xys = commands.getoutput('sky2xy ' + detect_image + ' @posfile').split('\n')
        for i in range(len(array)):
            #print xys[i]            
            l = filter(lambda x:x!='', xys[i].split('->')[1].split(' '))
            #print l
            x = l[0]
            y = l[1]
            array[i]['x'] = x
            array[i]['y'] = y
                                                                                     
        #print array
        file = open(listfile,'w')
         
        for i in range(len(array)):
            a = array[i]
            file.write(str(i) + ' ' + a['x'] + ' ' + a['y'] + '\n')
        file.close()

        reg = open(listfile + '.reg','w')
        print listfile + '.reg'
        reg.write('global color=green dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\nphysical\n')
        for i in range(len(array)):
            a = array[i]
            reg.write('circle(' + str(a['x']) + ',' + str(a['y']) + ',21)' + '\n')
        reg.close()


    ''' first identify objects w/o close neighbors '''
    import astropy.io.fits as pyfits, scipy, os

    
    
    
    
    
    
    

    cols = []


    ''' retrieve SDSS stars, make XY list, and cross match ''' 
    sdss_array = sdss_coverage(ra,dec)
    if sdss_array:
        mk_match(sdss_array,'sdss.list')
        sdss_catalog = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/sdss.cat' 
        command = '/usr/local/bin/sex ' + detect_image + ' -c ' + assoc_config + '  -CATALOG_NAME ' + sdss_catalog + ' -ASSOC_DATA 1 -ASSOC_NAME sdss.list -ASSOC_PARAMS 2,3 -ASSOC_RADIUS 3 -ASSOC_TYPE NEAREST -ASSOCSELEC_TYPE ALL -WEIGHT_IMAGE ' + detect_image.replace('.fits','.weight.fits') + ' -FLAG_IMAGE ' + detect_image.replace('.fits','.flag.fits') 
        add = ' -WEIGHT_TYPE MAP_WEIGHT -WEIGHT_IMAGE ' + detect_image.replace('.fits','.weight.fits') + ' -MAG_ZEROPOINT 0 '
        os.system(command + add)
        p = pyfits.open(sdss_catalog)
        vector_assoc=p[2].data.field('VECTOR_ASSOC')
        cols.append(pyfits.Column(name='SDSS_NEIGHBORS',format='1J',array=p[2].data.field('NUMBER_ASSOC')))
        flags = scipy.zeros(len(vector_assoc))
        flags[vector_assoc==0]  = 1 # cross match returns zero if no match 
        cols.append(pyfits.Column(name='FLAGS_SDSS',format='1J', array=flags))
        for key in sdss_array[0].keys():
            
            vals = scipy.array([sdss_array[int(i)][key] for i in vector_assoc])
            vals[vector_assoc==0] = -99               
            cols.append(pyfits.Column(name=key,format='DN',array=vals))



    filters = ['J','g','r','i','z','u']
    from glob import glob
    if sdss_array and glob('/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/SDSS_u/'):
        filters = ['SDSS_u','SDSS_g','SDSS_r','SDSS_i','SDSS_z'] + filters




    ''' add 2MASS '''
    twomass_field= '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/2mass_field.cat' 
    twomass = vizier(ra, dec, twomass_field)
    print twomass_field
    twomass_list = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/2mass.list'
    mk_match(twomass,twomass_list)
    #twomass_field= '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/2mass_field.cat' 
    #twomass = vizier(ra, dec, twomass_field)
    #print twomass_field
    #mk_match(twomass,twomass_list)

    image_dict = get_image_dict(run,night,snpath) 

    print image_dict
    
    ''' run sextractor on each band '''


    for color in filters: 
        for name, image in image_dict[color]['coadd'] + image_dict[color]['singles']:
                add_image(image,snpath,color,name,run)                                                                                                                      

    for color in filters: 
        for name, image in image_dict[color]['coadd'] + image_dict[color]['singles']:
            print name, image
            checkimage = '/Volumes/mosquitocoast/patrick/kpno/' + run + '/' + night + '/' + snpath + '/' + color + '/' + name + '.apers.fits' 
            catalog = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/' + color + '/' + name + '.cat' 
            psf_catalog = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/' + color + '/' + name + '.psf.cat' 
            psf = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/' + color + '/' + name + '.psf'

            import string

            if color == 'J' or string.find(color,'SDSS') != -1:
                import scipy, pyfits                                                                             
                rawim = pyfits.open(image)[0].data
                print 'image', image, rawim.shape, color, name
                map = scipy.ones(rawim.shape)*0.5/0.396 
                fitsobj = pyfits.HDUList()
                hdu = pyfits.PrimaryHDU()
                hdu.data = map 
                fitsobj.append(hdu)
                os.system('rm ' + image.replace('.fits','.rms.fits'))
                fitsobj.writeto(image.replace('.fits','.rms.fits'))
                zp= get_zp_SDSS(image)
                add = ' -GAIN 10 -WEIGHT_TYPE MAP_WEIGHT,MAP_RMS -WEIGHT_IMAGE ' + detect_image.replace('.fits','.weight.fits') + ',' + image.replace('.fits','.rms.fits') + ' -MAG_ZEROPOINT ' + str(zp)

            else:
                add = ' -WEIGHT_TYPE MAP_WEIGHT,MAP_WEIGHT -WEIGHT_IMAGE ' + detect_image.replace('.fits','.weight.fits') + ',' + image.replace('.fits','.weight.fits') + ' -MAG_ZEROPOINT 0 '
            command = '/usr/local/bin/sex ' + detect_image + ',' + image + ' -c ' + assoc_config + '  -CATALOG_NAME ' + catalog + add  +  ' -FLAG_IMAGE ' + image.replace('.fits','.flag.fits') + ' -ASSOC_DATA 1 -ASSOC_NAME ' + twomass_list + ' -ASSOC_PARAMS 2,3 -ASSOC_RADIUS 3 -ASSOC_TYPE NEAREST -ASSOCSELEC_TYPE ALL -CHECKIMAGE_TYPE APERTURES -CHECKIMAGE_NAME ' + checkimage #+ ' -SATUR_LEVEL 1500 -SATUR_KEY "" '
            print command
            import os
            os.system(command)
            fwhm = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/' + color + '/' + name + 'fwhm.ps' 
            ellip = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/' + color + '/' + name + 'ellip.ps' 
            xml = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/' + color + '/' + name + 'psf.xml' 
            psfdir = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/' + color + '/' 

            
            fwhm_psfex, fwhm_psfex_min, fwhm_psfex_min, beta_psfex, chi2_psfex, ellipticity_psfex, asymmetry_psfex, aperture_corr = extract_psf(catalog, fwhm, ellip, xml, psfdir, color)

            plate_scale = get_scale(detect_image)

            print plate_scale
            print 'plate_scale'

            SEEING_FWHM = str(float(fwhm_psfex) * plate_scale)

            print SEEING_FWHM

            ''' rerun SExtractor to identify stars '''
            command = '/usr/local/bin/sex ' + detect_image + ',' + image + ' -c ' + assoc_config + ' -SEEING_FWHM ' + SEEING_FWHM + ' -CATALOG_NAME ' + catalog + add  +  ' -FLAG_IMAGE ' + image.replace('.fits','.flag.fits') + ' -ASSOC_DATA 1 -ASSOC_NAME ' + twomass_list + ' -ASSOC_PARAMS 2,3 -ASSOC_RADIUS 3 -ASSOC_TYPE NEAREST -ASSOCSELEC_TYPE ALL -CHECKIMAGE_TYPE APERTURES -CHECKIMAGE_NAME ' + checkimage #+ ' -SATUR_LEVEL 1500 -SATUR_KEY "" '
            print command
            import os
            os.system(command)



                

            if True: #name != 'reg':
                import MySQLdb
                db2 = MySQLdb.connect(db='calib')
                c = db2.cursor()
                command = "UPDATE CALIB set FWHM=" + str(fwhm_psfex) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
                print command 
                c.execute(command)                                                                                                                       

                command = "UPDATE CALIB set CHI=" + str(chi2_psfex) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
                c.execute(command)                                                                                                                       
                if sdss_array:
                    command = "UPDATE CALIB set STRIPE=" + str(sdss_array[0]['stripe']) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
                    c.execute(command)                                                                                                                       

                command = "UPDATE CALIB set BETA=" + str(beta_psfex) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
                c.execute(command)                                                                                                                       
                print name, image 





                print name, image 


                command = "UPDATE CALIB set ELLIPTICITY=" + str(ellipticity_psfex) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
                c.execute(command)                                                                                                                       
                print name, image 

                command = "UPDATE CALIB set ASYMMETRY=" + str(asymmetry_psfex) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
                c.execute(command)                                                                                                                       
                print name, image 




                print aperture_corr
        
        if False:
            command = '/usr/local/bin/sex ' + detect_image + ',' + image + ' -c ' + assoc_config + ' -PSF_NAME ' + psf + ' -PARAMETERS_NAME ' + psf_params + ' -CATALOG_NAME ' + psf_catalog + ' -ASSOC_DATA 1 -ASSOC_NAME ' + twomass_list + ' -ASSOC_PARAMS 2,3 -ASSOC_RADIUS 3 -ASSOC_TYPE NEAREST -ASSOCSELEC_TYPE ALL -WEIGHT_IMAGE ' + detect_image.replace('.fits','.weight.fits') + ',' + image.replace('.fits','.weight.fits') +  ' -FLAG_IMAGE ' + image.replace('.fits','.flag.fits')  
            print command
            os.system(command)
        print image


    #twomass=False
    fwhm = {}


    ''' add dust extinction values and aperture correction '''                                                                             
    color = 'g'
    catalog = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/' + color + '/reg.cat' 
    print catalog
    p = pyfits.open(catalog)    
    print p[2].columns
    alpha = p[2].data.field('ALPHA_J2000')
    delta = p[2].data.field('DELTA_J2000')
    ebv_SFD, gallong, gallat, dummy = getDust(alpha,delta,pg10=False)
    ebv, gallong, gallat, peekapplied = getDust(alpha,delta)

    #ebv = ebv - scipy.ones(len(ebv))*0.04
    print peekapplied

    print ebv, ebv_SFD
    print alpha, delta
    cols.append(pyfits.Column(name='EBV',format='DN', array=ebv))
    cols.append(pyfits.Column(name='GALLONG',format='DN', array=gallong))
    cols.append(pyfits.Column(name='GALLAT',format='DN', array=gallat))

    ''' include columns for measurements of other images '''

    #extinctions = {'u':5.155,'g':3.793,'r':2.751,'i':2.086,'z':1.479,'J':0.92,'SDSS_u':5.155,'SDSS_g':3.793,'SDSS_r':2.751,'SDSS_i':2.086,'SDSS_z':1.479}

    ''' recomputed '''
    #extinctions = {'u':4.877,'g':3.6394,'r':2.678,'i':2.0088,'z':1.529,'J':0.92,'SDSS_u':4.887,'SDSS_g':3.698,'SDSS_r':2.0855,'SDSS_i':2.0855,'SDSS_z':1.528} # Cardelli???

    ''' from schlafly (heavy vs light extinction) '''
    if True: #ebv[0] < 0.2:
        extinctions = {'u':4.157,'g':3.167,'r':2.202,'i':1.61,'z':1.244,'J':0.72,'SDSS_u':4.239,'SDSS_g':3.303,'SDSS_r':2.285,'SDSS_i':1.698,'SDSS_z':1.263}
    else:
        extinctions = {'u':4.75,'g':3.63,'r':2.529,'i':1.85,'z':1.43,'J':0.82,'SDSS_u':4.902,'SDSS_g':3.703,'SDSS_r':2.589,'SDSS_i':1.9243,'SDSS_z':1.4552}
    
    print extinctions, ebv[0]

    print filters

    for color in filters: #,['JCAT',0.92]]:


        coeff = extinctions[color]
        dust_corr = ebv*coeff 
        dust_corr_SFD = ebv_SFD*coeff 

        cols.append(pyfits.Column(name='DUST_'+color,format='DN', array=dust_corr))

        print image_dict[color]['coadd']+ image_dict[color]['singles']

        for name, image in image_dict[color]['coadd'] + image_dict[color]['singles']:

            import commands
            EXPTIME = float(commands.getoutput('gethead ' + image + ' EXPTIME'))

            from glob import glob
            catalog = image.replace('.fits','.cat') #'/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/' + color + '/reg.cat'                                
            p = pyfits.open(catalog)
            print p
            print catalog
            
            from vo.table import parse
            xml = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/' + color + '/' + name + 'psf.xml' 
            votable = parse(xml,pedantic=False)
            table =  votable.get_first_table()
            beta_psfex = table.array['MoffatBeta_Mean'][0]
            fwhm_psfex = table.array['FWHM_Mean'][0]

            
            aperture_corr = correct(10.,fwhm_psfex,beta_psfex)

            
            import MySQLdb
            db2 = MySQLdb.connect(db='calib')
            c = db2.cursor()

            import math
            if EXPTIME != 0:
                print image, name, EXPTIME                                                                                                                                          
                exptimecorr = - 2.5*math.log10(EXPTIME/76.0)  
            else: exptimecorr = 0.

            import string
            if string.find(color,'SDSS') != -1: 
                aperture_corr = 0
                #dust_corr = scipy.zeros(len(dust_corr)) 
                exptimecorr = 0.
            if string.find(color,'J') != -1: 
                exptimecorr = 0.
                print dust_corr

            #if string.find(color,'SDSS') != -1 or string.find(color,'J') != -1: 


            command = "UPDATE CALIB set EXPTIMECORR=" + str(exptimecorr) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
            c.execute(command)                                                                                                                       
            correction = dust_corr + aperture_corr + exptimecorr 

            

            if string.find(color,'SDSS') != -1: 
                print aperture_corr, correction                        
                print fwhm_psfex, beta_psfex, name, image, exptimecorr
                                                                       
                print color

            cols.append(pyfits.Column(name='APERTURE_CORR_'+name+'_'+color,format='DN', array=scipy.ones(len(p[2].data))*aperture_corr))
            cols.append(pyfits.Column(name='FWHM_Mean_'+name+'_'+color,format='DN', array=scipy.ones(len(p[2].data))*table.array['FWHM_Mean'][0]))
            cols.append(pyfits.Column(name='FWHM_Min_'+name+'_'+color,format='DN', array=scipy.ones(len(p[2].data))*table.array['FWHM_Min'][0] ))
            cols.append(pyfits.Column(name='FWHM_Max_'+name+'_'+color,format='DN', array=scipy.ones(len(p[2].data))*table.array['FWHM_Max'][0] ))
            cols.append(pyfits.Column(name='MoffatBeta_Mean_'+name+'_'+color,format='DN', array=scipy.ones(len(p[2].data))*table.array['MoffatBeta_Mean'][0]))
            cols.append(pyfits.Column(name='MoffatBeta_Min_'+name+'_'+color,format='DN', array=scipy.ones(len(p[2].data))*table.array['MoffatBeta_Min'][0] ))
            cols.append(pyfits.Column(name='MoffatBeta_Max_'+name+'_'+color,format='DN', array=scipy.ones(len(p[2].data))*table.array['MoffatBeta_Max'][0] ))
            fwhm[color] = table.array['FWHM_Mean'][0]
            
            print color, aperture_corr, dust_corr[0], fwhm_psfex, beta_psfex

            import MySQLdb
            db2 = MySQLdb.connect(db='calib')
            c = db2.cursor()

            
            command = "UPDATE CALIB set APERCORR=" + str(aperture_corr) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
            c.execute(command)                                                                                                                       
            command = "UPDATE CALIB set DUSTCORR=" + str(dust_corr[0]) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
            c.execute(command)                                                                                                                       
            command = "UPDATE CALIB set DUSTCORRSFD=" + str(dust_corr_SFD[0]) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
            c.execute(command)                                                                                                                       
            command = "UPDATE CALIB set PEEK=" + str(peekapplied[0]) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
            print command
            c.execute(command)                                                                                                                       

            command = "UPDATE CALIB set SDSSCOV=" + str(len(sdss_array)) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
            c.execute(command)                                                                                                                       
            command = "UPDATE CALIB set GALLAT=" + str(gallat[0]) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 



            command = "UPDATE CALIB set GALLAT=" + str(gallat[0]) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
            c.execute(command)                                                                                                                       
            command = "UPDATE CALIB set GALLONG=" + str(gallong[0]) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
            print command
            c.execute(command)                                                                                                                       

            
            for col in p[2].columns:
                cols.append(pyfits.Column(name=col.name+'_'+name+'_'+color,format=col.format, array=p[2].data.field(col.name)))
            
            cols.append(pyfits.Column(name='MAG_APERDUST_'+name+'_'+color,format=col.format, array=(p[2].data.field('MAG_APER') - (aperture_corr + exptimecorr) )   ))
            cols.append(pyfits.Column(name='MAGERR_APERDUST_'+name+'_'+color,format=col.format, array=p[2].data.field('MAGERR_APER')))
            cols.append(pyfits.Column(name='MAG_APERCORR_'+name+'_'+color,format=col.format, array=(p[2].data.field('MAG_APER') - correction)   ))
            cols.append(pyfits.Column(name='MAGERR_APERCORR_'+name+'_'+color,format=col.format, array=p[2].data.field('MAGERR_APER')))

    max_fwhm = sorted(fwhm.values())[-1] 
    print max_fwhm, fwhm

    ''' find close neighbors '''
    catalog = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/g/reg.cat' 
    pobj = pyfits.open(catalog)
    objl = open('objl.list','w')
    reg = open('obj.reg','w')
    reg.write('global color=green dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\nphysical\n')
    for i,x,y in zip(range(len(pobj[2].data)),pobj[2].data.field('X_IMAGE'),pobj[2].data.field('Y_IMAGE')):
        objl.write(str(i) + ' ' + str(x) + ' ' + str(y) + ' 1\n')
        reg.write('circle(' + str(x) + ',' + str(y) + ',21)' + '\n')
    objl.close()
    reg.close()
    catalog = '/Volumes/mosquitocoast/patrick/kpno/' + run + '/' + night +'/' + snpath + '/g/neighbors.cat' 

    ''' closer '''
    command = '/usr/local/bin/sex ' + detect_image + ' -c ' + assoc_config + ' -CATALOG_NAME ' + catalog + ' -ASSOC_DATA 1 -ASSOC_NAME objl.list -ASSOC_PARAMS 2,3,4 -ASSOC_RADIUS ' + str(max_fwhm/2.*6.) + ' -ASSOC_TYPE SUM -ASSOCSELEC_TYPE ALL ' + ' -WEIGHT_IMAGE ' + detect_image.replace('.fits','.weight.fits') +  ' -FLAG_IMAGE ' + detect_image.replace('.fits','.flag.fits')  + ' -WEIGHT_TYPE MAP_WEIGHT'
    print command
    os.system(command)
    p = pyfits.open(catalog)
    col = pyfits.Column(name='NEIGHBORS',format='1J',array=p[2].data.field('NUMBER_ASSOC'))
    cols.append(col)

    ''' farther away '''
    command = '/usr/local/bin/sex ' + detect_image + ' -c ' + assoc_config + ' -CATALOG_NAME ' + catalog + ' -ASSOC_DATA 1 -ASSOC_NAME objl.list -ASSOC_PARAMS 2,3,4 -ASSOC_RADIUS 20 -ASSOC_TYPE SUM -ASSOCSELEC_TYPE ALL ' + ' -WEIGHT_IMAGE ' + detect_image.replace('.fits','.weight.fits') +  ' -FLAG_IMAGE ' + detect_image.replace('.fits','.flag.fits')  + ' -WEIGHT_TYPE MAP_WEIGHT'
    print command
    os.system(command)
    p = pyfits.open(catalog)
    FAR_NEIGHBORS = p[2].data.field('NUMBER_ASSOC')
    print len(FAR_NEIGHBORS), len(pobj[2].data)        
    print p[2].data.field('X_IMAGE')
    print pobj[2].data.field('X_IMAGE')
    col = pyfits.Column(name='FAR_NEIGHBORS',format='1J',array=FAR_NEIGHBORS)
    cols.append(col)


    
    
    
    
    
    
    twomass_catalog = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/2mass.cat' 
    command = '/usr/local/bin/sex ' + detect_image + ' -c ' + assoc_config + '  -CATALOG_NAME ' + twomass_catalog + ' -ASSOC_DATA 1 -ASSOC_NAME ' + twomass_list + ' -ASSOC_PARAMS 2,3 -ASSOC_RADIUS 3 -ASSOC_TYPE NEAREST -ASSOCSELEC_TYPE ALL -WEIGHT_IMAGE ' + detect_image.replace('.fits','.weight.fits') + ' -FLAG_IMAGE ' + detect_image.replace('.fits','.flag.fits')  + ' -WEIGHT_TYPE MAP_WEIGHT'
    print command
    os.system(command)
    p = pyfits.open(twomass_catalog)
    vector_assoc=p[2].data.field('VECTOR_ASSOC')
    neighbors=p[2].data.field('NUMBER_ASSOC')
    print vector_assoc        

    Cflg = scipy.array([twomass[int(i)]['Cflg'][0] for i in vector_assoc])
    Qflg = scipy.array([twomass[int(i)]['Qflg'][0] for i in vector_assoc])
    Rflg = scipy.array([twomass[int(i)]['Rflg'][0] for i in vector_assoc])
    Bflg = scipy.array([twomass[int(i)]['Bflg'][0] for i in vector_assoc])
    Xflg = scipy.array([int(twomass[int(i)]['Xflg']) for i in vector_assoc])

    for key in ['Cflg','Qflg','Rflg','Bflg']: #,'Xflg']:
        vals = scipy.array([twomass[int(i)][key][0] for i in vector_assoc])
        print vals[:200], key
        cols.append(pyfits.Column(name=key,format='10A', array=vals))

    for key in ['Xflg']: #,'Xflg']:
        vals = scipy.array([int(twomass[int(i)][key]) for i in vector_assoc])
        #print vals[:200], key
        cols.append(pyfits.Column(name=key,format='1L', array=vals))

    for key in ['Jmag','e_Jmag']:
        vals = scipy.array([twomass[int(i)][key] for i in vector_assoc])
        if key == 'Jmag':
            vals[vector_assoc==0] = -99 # cross match returns zero if no match 
            for key_use in ['MAG_PSF_reg_JCAT','MAG_AUTO_reg_JCAT','MAG_APER_reg_JCAT']: 

                cols.append(pyfits.Column(name=key_use,format='DN',array=vals))

            for key_use in ['MAG_APERCORR_reg_JCAT']:
                coeff = extinctions['J']
                dust_corr = ebv*coeff 
                print len(dust_corr), len(vals)
                print len(vector_assoc)
                print cols
                Jmag = vals - dust_corr
                Jmag[vals==-99] = -99
                cols.append(pyfits.Column(name=key_use,format='DN',array=Jmag))


            flags = scipy.zeros(len(vals))
            flags[vector_assoc==0]  = 1 # cross match returns zero if no match 
            flags[Cflg!='0']  = 1 
            #flags[Qflg!='A']  = 1 
            #flags[Rflg!='2']  = 1 
            #flags[Bflg!='1']  = 1 
            #flags[Xflg!=0]  = 1  
            #flags[FAR_NEIGHBORS!=1] = 1
            #print FAR_NEIGHBORS[:300]
            print flags[:300], len(flags[flags==0])

            


            cols.append(pyfits.Column(name='FLAGS_reg_JCAT',format='1J', array=flags))
            cols.append(pyfits.Column(name='IMAFLAGS_ISO_reg_JCAT',format='1J', array=scipy.zeros(len(flags))))
            cols.append(pyfits.Column(name='CHI2_PSF_reg_JCAT',format='DN', array=scipy.ones(len(flags))))
        elif key == 'e_Jmag':
            for key_use in ['MAGERR_PSF_reg_JCAT','MAGERR_AUTO_reg_JCAT','MAGERR_APER_reg_JCAT','MAGERR_APERCORR_reg_JCAT']: 
                cols.append(pyfits.Column(name=key_use,format='DN',array=vals))
    output = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
    output.writeto(output_cat)


@entryExit
def select_stars(run,night,snpath):    
    ''' REMEMBER SATURATE !@#$!@#%@%^#%&!@#$%!@#$!@#$!#$^$%^ MAXVAL '''

    input_cat= '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/photometry.fits' 


    #mask = (p.field('MAGERR_PSF_u') < 0.3) * (p.field('MAGERR_PSF_g') < 0.1) * (p.field('MAGERR_PSF_r') < 0.1) * (p.field('MAGERR_PSF_i') < 0.1) * (p.field('MAGERR_PSF_z') < 0.3) 

    image_dict = get_image_dict(run,night,snpath) 

    for ap_type in ['APERCORR']:

        
        import pylab, pyfits, scipy    


        print input_cat

        porig = pyfits.open(input_cat)
        p = porig[1].data        
        
        reg = open('regstart.reg','w')
        reg.write('global color=blue dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\nphysical\n')
        for x,y in zip(p.field('X_IMAGE_reg_g'),p.field('Y_IMAGE_reg_g')):
            reg.write('circle(' + str(x) + ',' + str(y) + ',18)#' + '\n')
        reg.close()
                                       
        from copy import copy

        ''' if seeing is really bad (unfocused) use FLUX_RADIUS ''' 


        masks = [] 
        for star_select in ['u','g','r','i','z']:

            ok = 0                                             
            seeings = p.field('FWHM_Mean_reg_' + star_select)[0]
            if seeings < 4 and star_select != 'u':
                radius_var = 'FWHM_IMAGE'
            else:
                radius_var = 'FLUX_RADIUS'


            radius_var = 'FLUX_RADIUS'
                                                               
            print radius_var

            ''' need to isolate the star column '''
            
            mask = p.field('FLAGS_reg_' + star_select) == 0
            array = p[mask]
            mask = array.field('IMAFLAGS_ISO_reg_' + star_select) == 0
            save_array = array[mask]

            if 0:
                pylab.clf()
                pylab.scatter(p.field(radius_var + '_reg_' + star_select),p.field('MAG_' + ap_type + '_reg_' + star_select),c='red')      
                                                                                                                                         
                pylab.xlim([0,10])
                pylab.ylim([-20,0])
                pylab.xlabel(radius_var + '_reg_' + star_select)
                pylab.ylabel('MAG_' + ap_type + '_reg_' + star_select)
                #pylab.savefig('/Users/pkelly/Dropbox/star' + star_select + '1.pdf')
                pylab.savefig('/Volumes/mosquitocoast/patrick/kpno/' + run + '/work_night/' + snpath + '/starcolumn'+star_select+'.pdf')




            from copy import copy

            array = copy(save_array)                                                                                    
            pylab.clf()
            a,b,varp = pylab.hist(array.field(radius_var + '_reg_' + star_select),bins=scipy.arange(1.0,8,0.1))    

            #pylab.savefig('/Users/pkelly/Dropbox/star' + star_select + 'hist.pdf')
            z = zip(a,b)
            z.sort()
            max_meas = z[-1][1]


            print max_meas


            def get_width_upper(max, width, upper, array_in):
               
                from copy import copy 
                array = copy(array_in)
                ''' now pick objects somewhat larger than star column '''
                print array.field(radius_var + '_reg_' + star_select)
                mask = array.field(radius_var + '_reg_' + star_select) > max+width 
                array = array[mask]
                rads = array.field(radius_var + '_reg_' + star_select)#[mask]
                mask = rads < max+width + 0.6 
                array = array[mask]
                mags = array.field('MAG_' + ap_type + '_reg_' + star_select)
                mags.sort()
                ''' take 20% percentile and subtract 0.5 mag '''
                print star_select, max, width, upper
                if len(mags) == 0:
                    upper = 99
                else:
                    upper = mags[int(len(mags)*0.2)] #+ 0.5
                                                                                                                            
                array = copy(array_in)
                print max
                maskA = array.field('MAG_' + ap_type + '_reg_' + star_select) < upper #+ 0.5 
                maskB  = array.field(radius_var + '_reg_' + star_select) < max + width 
                maskC = array.field(radius_var + '_reg_' + star_select) > max - width 
                mask = scipy.logical_and(maskA,maskB,maskC)
                array = array[mask]
                rads = array.field(radius_var + '_reg_' + star_select)
                                                                                
                pylab.clf()                                            
                a,b,varp = pylab.hist(array.field(radius_var + '_reg_' + star_select),bins=scipy.arange(1.0,8,0.04))    
                z = zip(a,b)
                z.sort()
                max = z[-1][1]

                #pylab.savefig('/Users/pkelly/Dropbox/star' + star_select + 'hist2.pdf')

                if star_select == 'u':                                                                                                                            
                    width = 2.0*scipy.std(rads) 
                else:
                    width = 4.0*scipy.std(rads) 

                print 'width', width, 'max', max, 'upper', upper, 'rads', rads

                return max, width, upper


            max, width, upper = get_width_upper(max_meas, 0.3, 100, copy(save_array))            

            print max, max_meas, width, upper

            max, width, upper = get_width_upper(max, width, upper, copy(save_array))            

            #max, width, upper = get_width_upper(max, width, upper, copy(save_array))            

                                                                                                                       
            pylab.clf()
            pylab.scatter(p.field(radius_var + '_reg_' + star_select),p.field('MAG_' + ap_type + '_reg_' + star_select))
            #pylab.scatter(array.field(radius_var + '_reg_' + star_select),array.field('MAG_' + ap_type + '_reg_' + star_select),c='red')
            pylab.axvline(x=max - width,c='red')
            pylab.axvline(x=max + width,c='red')


            #pylab.axvline(x=p.field('FWHM_Min_reg_' + star_select)[0],c='red')
            #pylab.axvline(x=p.field('FWHM_Max_reg_' + star_select)[0],c='red')


            pylab.axhline(y=upper,c='red')

            if False:
                mask = save_array.field('CLASS_STAR_reg_' + star_select) > 0.9                                                         
                print save_array.field('CLASS_STAR_reg_' + star_select)
                pm = save_array[mask]
                pylab.scatter(pm.field(radius_var + '_reg_' + star_select),pm.field('MAG_' + ap_type + '_reg_' + star_select),c='red')

            pylab.xlim([0,10])
            pylab.ylim([-20,0])
            pylab.xlabel(radius_var + '_reg_' + star_select)
            pylab.ylabel('MAG_' + ap_type + '_reg_' + star_select)
            #pylab.savefig('/Users/pkelly/Dropbox/star' + star_select + '.pdf')
            pylab.savefig('/Volumes/mosquitocoast/patrick/kpno/' + run + '/work_night/' + snpath + '/starcolumn'+star_select+'.pdf')
            #pylab.show()

            pylab.clf()
            pylab.scatter(p.field(radius_var + '_reg_' + star_select),p.field('FLUX_APER_reg_' + star_select))
            #pylab.scatter(array.field(radius_var + '_reg_' + star_select),array.field('MAG_' + ap_type + '_reg_' + star_select),c='red')
            pylab.axvline(x=max - width,c='red')
            pylab.axvline(x=max + width,c='red')
            #pylab.axhline(y=upper,c='red')
            pylab.xlim([0,10])
            pylab.ylim([0,60000])
            pylab.xlabel(radius_var + '_reg_' + star_select)
            pylab.ylabel('FLUX_' + ap_type + '_reg_' + star_select)
            pylab.savefig('/Volumes/mosquitocoast/patrick/kpno/' + run + '/work_night/' + snpath + '/starflux'+star_select+'.pdf')




            
            ''' select star column '''
            mask = p.field(radius_var + '_reg_' + star_select) > max - width 
            mask *= p.field(radius_var + '_reg_' + star_select) < max + width 
            mask *= p.field('MAG_' + ap_type + '_reg_' + star_select) < upper #+ 0.5

            masks.append(scipy.array([int(x) for x in mask]))

        #masks.append(p.field('FLAGS_J')==0)

        star_mask = reduce(lambda x,y: x + y, masks) #masks[0] + masks[1]        
        p = copy(p[star_mask > 1])
        #p = p[p.field('CLASS_STAR_reg_g') > 0.01]

        for filt in []: #'u','g','r','i','z']:
            mask = p.field('FLAGS_' + filt) != 0
            print mask
            p.field('MAG_' + ap_type + '_' + filt)[mask] = -99
            p.field('MAG_' + ap_type + '_' + filt)[mask] = -99
            print p.field('MAG_' + ap_type + '_' + filt)
        
        reg = open('regall.reg','w')
        reg.write('global color=yellow dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\nphysical\n')
        for x,y in zip(p.field('X_IMAGE_reg_g'),p.field('Y_IMAGE_reg_g')):
            reg.write('circle(' + str(x) + ',' + str(y) + ',19)#' + '\n')
        reg.close()
       
        #print p.field('FAR_NEIGHBORS') 
        mask = p.field('FAR_NEIGHBORS') == 1
        #print len(mask)
        #print p.field('FAR_NEIGHBORS')
        #print len(p[mask])
        p = copy(p[mask])
        #print len(p.field('FAR_NEIGHBORS'))
                                                                                                                                                                                                                                                                                           
        cols = []
        for col in porig[1].columns:
            cols.append(pyfits.Column(name=col.name,format=col.format, array=p.field(col.name)))
                                                                                                                                                                                                                                                                                           
        output = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
        output_cat = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/stars.fits'

        import os, scipy
        os.system('rm ' + output_cat)
        output.writeto(output_cat)

        ''' now calculate relative offsets of images away from reg image '''
        for color in ['u','g','r','i','z']:

            mask = p.field('FLAGS_reg_' + color) == 0
            p_color = p[mask]
            mask = p_color.field('IMAFLAGS_ISO_reg_' + color) == 0
            p_color = p_color[mask]
            #p_color = p

            for name, image in image_dict[color]['singles']:
                reg_image = image_dict[color]['coadd']

                print p_color.field('FLAGS_' + name + '_' + color), 'FLAGS_' + name + '_' + color, snpath
                print p_color.field('IMAFLAGS_ISO_' + name + '_' + color)

                mask = p_color.field('FLAGS_' + name + '_' + color) == 0
                p_color = p_color[mask]
                mask = p_color.field('IMAFLAGS_ISO_' + name + '_' + color) == 0
                p_color = p_color[mask]

                ''' then weighted average '''                
                errors = p_color.field('MAGERR_APERCORR_' + name + '_' + color)
                errors[errors<0.02] = 0.02
                diff =  p_color.field('MAG_APERCORR_reg_' + color) - p_color.field('MAG_APERCORR_' + name + '_' + color) 
                print p_color.field('MAG_APERCORR_' + name + '_' + color), p_color.field('MAG_APERCORR_reg_' + color)
                print 'errors','diff',errors, diff

                average = av_difference(diff, errors)  

                print name, average, 

                command = 'sethead ' + image + ' RELZP=' + str(average)
                os.system(command)

                import MySQLdb
                db2 = MySQLdb.connect(db='calib')
                c = db2.cursor()

                command = "UPDATE CALIB set RELZP=" + str(average) + " WHERE SN='" + snpath + "' and FILT='" + color + "' and NAME='" + name + "' and RUN='" + run + "'" 
                print command  
                c.execute(command)                                                                                                                       
                print image
                    








        reg = open('regstars.reg','w')
        reg.write('global color=red dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\nphysical\n')
        for x,y in zip(p.field('X_IMAGE_reg_g'),p.field('Y_IMAGE_reg_g')):
            reg.write('circle(' + str(x) + ',' + str(y) + ',20)#' + '\n')
        reg.close()

        
        if False:
            for c1, c2, lims in [[['g','r'],['u','g'],[(0.2,1.8),(2.0,5.5)]],[['r','i'],['g','r'],[(-0.5,1.0),(0.2,1.8)]],[['z','J'],['i','z'],[(-27.,-25.8),(-1.1,-0.3)]]]: #,[['z','JCAT'],['i','z'],[(-27.,-25.8),(-1.1,-0.3)]]]:                                                                                                                                                                
            #for c1, c2, lims in [[['z','J'],['i','z'],[(-27.,-25.8),(-1.1,-0.3)]],[['z','JCAT'],['i','z'],[(-27.,-25.8),(-1.1,-0.3)]]]:
                pf = copy(p)
                pylab.clf()
                #cA,cB = (pf.field('MAG_' + ap_type + '_'+c1[0])-pf.field('MAG_' + ap_type + '_'+c1[1]),pf.field('MAG_' + ap_type + '_'+c2[0])-pf.field('MAG_' + ap_type + '_'+c2[1]))
                #pylab.scatter(cA,cB,color='red')
                #pylab.errorbar(pf.field('MAG_' + ap_type + '_'+c1[0])-pf.field('MAG_' + ap_type + '_'+c1[1]),pf.field('MAG_' + ap_type + '_'+c2[0])-pf.field('MAG_' + ap_type + '_'+c2[1]),xerr=pf.field('MAGERR_' + ap_type + '_'+c1[0])+pf.field('MAGERR_' + ap_type + '_'+c1[1]),yerr=pf.field('MAGERR_' + ap_type + '_'+c2[0])+pf.field('MAGERR_' + ap_type + '_'+c2[1]),fmt=None,color='red')
                                                                                                                                                                                                                                                                                                                                                                                                    
                mask = (p.field('FLAGS_reg_' + c1[0]) + p.field('FLAGS_reg_' + c1[1]) + p.field('FLAGS_reg_' + c2[0]) + p.field('FLAGS_reg_' + c2[1])) == scipy.zeros(len(p.field('FLAGS_reg_u')))                                                                        
                p1 = copy(p[mask])
                #p1 = copy(p)
                                                                                                                                                                                                                                                                                               
                mask = (p1.field('IMAFLAGS_ISO_reg_' + c1[0]) + p1.field('IMAFLAGS_ISO_reg_' + c1[1]) + p1.field('IMAFLAGS_ISO_reg_' + c2[0]) + p1.field('IMAFLAGS_ISO_reg_' + c2[1])) == scipy.zeros(len(p1.field('IMAFLAGS_ISO_reg_u')))                                                                        
                                                                                                                                                                                                                                                                                                                                                                                                    
                p1 = copy(p1[mask])
                                                                                                                                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                                                                                                                    
                if ap_type == 'PSF':
                    mask = (p1.field('CHI2_PSF_' + c1[0]) + p1.field('CHI2_PSF_' + c1[1]) + p1.field('CHI2_PSF_' + c2[0]) + p1.field('CHI2_PSF_' + c2[1])) < 4*scipy.ones(len(p1.field('CHI2_PSF_u')))                                                                        
                    p1 = copy(p1[mask])
                                                                                                                                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                               
                #print len(p1), 'p1'
                #mask = p1.field('NEIGHBORS') == 1
                #print len(mask)
                #print p1.field('NEIGHBORS')
                #print len(p1[mask])
                #p2 = copy(p1[mask])
                
                print len(p1)                                                                                                                                                                                                                                                                               
                mask = p1.field('MAGERR_' + ap_type + '_reg_' + c1[0]) +  p1.field('MAGERR_' + ap_type + '_reg_' + c1[1]) + p1.field('MAGERR_' + ap_type + '_reg_' + c2[0]) + p1.field('MAGERR_' + ap_type + '_reg_' + c2[1]) < 1.0
                pf = copy(p1[mask])
                                                                                                                                                                                                                                                                                                                                                                                                    
                #pf = copy(p1)
                print ap_type                                                                               
                print len(pf), 'length'
                                                                                                                                                                                                                                                                                                                                                                                                    
                cA,cB = (pf.field('MAG_' + ap_type + '_reg_'+c1[0])-pf.field('MAG_' + ap_type + '_reg_'+c1[1]),pf.field('MAG_' + ap_type + '_reg_'+c2[0])-pf.field('MAG_' + ap_type + '_reg_'+c2[1]))
                print cA,cB
                pylab.scatter(cA,cB)
                                                                                                                                                                                                                                                                                                                                                                                                    
                x = pf.field('MAG_' + ap_type + '_reg_'+c1[0])-pf.field('MAG_' + ap_type + '_reg_'+c1[1])
                y = pf.field('MAG_' + ap_type + '_reg_'+c2[0])-pf.field('MAG_' + ap_type + '_reg_'+c2[1])
                xerr = (pf.field('MAGERR_' + ap_type + '_reg_'+c1[0])**2.+pf.field('MAGERR_' + ap_type + '_reg_'+c1[1])**2.)**0.5
                yerr = (pf.field('MAGERR_' + ap_type + '_reg_'+c2[0])**2.+pf.field('MAGERR_' + ap_type + '_reg_'+c2[1])**2.)**0.5
                                                                                                                                                                                                                                                                                                                                                                                                    
                pylab.errorbar(x,y,xerr=xerr,yerr=yerr,fmt=None)
                                                                                                                                                                                                                                                                                                                                                                                                    
                regf = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/reg.reg' 
                reg = open(regf,'w')
                reg.write('global color=green dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\nphysical\n')
                                                                                                                                                                                                                                                                                                                                                                                                    
                print x, y, xerr, yerr
                                                                                                                                                                                                                                                                                                                                                                                                    
                print pf.field('MAG_' + ap_type + '_reg_' + c1[1])
                print pf.field('MAGERR_' + ap_type + '_reg_' + c1[1])
                                                                                                                                                                                                                                                                                                                                                                                                    
                #print pf.field('X_IMAGE_' + c1[1])
                #print pf.field('Y_IMAGE_' + c1[1])
                                                                                                                                                                                                                                                                                                                                                                                                    
                for x,y,A,B,f in zip(pf.field('X_IMAGE_reg_g'),pf.field('Y_IMAGE_reg_g'),cA,cB,pf.field('FLUX_APER_reg_u')):
                    reg.write('circle(' + str(x) + ',' + str(y) + ',21)#' + str(A) + ',' + str(B) + ' ' + str(f) + '\n')
                reg.close()
                                                                                                                                                                                                                                                                                               
                pylab.xlabel(c1[0] + '-' + c1[1])
                pylab.ylabel(c2[0] + '-' + c2[1])
                #pylab.xlim(lims[0])
                #pylab.ylim(lims[1])
                                                                                                                                                                                                                                               
                #pylab.show()
                                                                                                                                                                                                                                                                                                                                                                                                    
                #pylab.savefig('/Users/pkelly/Dropbox/' + snpath + c1[0] + c1[1] + 'm' + c2[0] + c2[1] + '.' + ap_type + '.pdf')
                                                                                                                                                                                                                                                                                                                                                                                                    
                #pylab.savefig('/Volumes/mosquitocoast/patrick/kpno/kpno_Oct2010/work_night/' + snpath + '/' +  c1[0] + c1[1] + 'm' + c2[0] + c2[1] + '.' + ap_type + '.pdf')


def run(run=None,snpath=None):

    def ex(run,snpath):
        import slr_kpno_new, os, pyfits, scipy
        #run_swarp(run,'work_night',snpath)
        from glob import glob
        if glob(os.environ['kpno'] + '/' + run + '/work_night/' + snpath + '/z/reg.fits'):
            #run_sextractor(run,'work_night',snpath)         
            #select_stars(run,'work_night',snpath)         
            #if glob(snpath + '/SDSS_g/*.fits'):
            #slr_kpno_new.all(run,'work_night',snpath)
    
            night = 'work_night'
            input_cat = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/stars.fits'

            sdss_input_cat = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/sdss_stars.fits'
            output_directory = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/'

            plots_sdss_directory = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/PLOTS_SDSS/'
            import anydbm
            hj = anydbm.open(snpath)
            RA = float(hj['snradeg'])
            DEC = float(hj['sndecdeg'])
            column_description = '/Volumes/mosquitocoast/patrick/kpno/process_kpno/QC/stars.columns'

            sdss_column_description = '/Volumes/mosquitocoast/patrick/kpno/process_kpno/QC/sdss.columns'
            import fit_locus
            reload(fit_locus)

            ''' run on SDSS catalog '''
            sdss_array = sdss_cat(RA,DEC,rad=40)
            print sdss_array[0]

            ''' make output catalog '''
            cols = [] 
            for key in sdss_array[0].keys():
                cols.append(pyfits.Column(name=key,format='DN', array=scipy.array([x[key] for x in sdss_array])))

            output = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
            os.system('rm ' + sdss_input_cat)
            output.writeto(sdss_input_cat)

            import profile

    
            fit_locus.run(sdss_input_cat,sdss_column_description,plots_directory=plots_sdss_directory,output_directory=output_directory,extension=1,RA=RA,DEC=DEC,bootstrap_num=0,run=run,snpath=snpath,prefix='SDSS')



            #fit_locus.run(input_cat,column_description,output_directory=output_directory,extension=1,RA=RA,DEC=DEC,bootstrap_num=5,run=run,snpath=snpath)
            #slr_kpno_new.sdss(run,'work_night',snpath)

    if snpath:
        ex(run,snpath)            
    else:
        #sdss_sns = ['sn1994T','sn1996cb','sn1997bo','sn1998T','sn1998cc','sn1999cc','sn1999dk','sn2001cf','sn2001cy','sn2002ck','sn2003U','sn2003ej','sn2003hu','sn2003it','sn2004A','sn2004Z','sn2004ao','sn2004bu','sn2005J','sn2005O','sn2005U','sn2005kc','sn2006C','sn2006aa','sn2006bf','sn2006bq','sn2006by','sn2006dl','sn2006qp','sn2007O','sn2007ag','sn2008D','sn2008ht','sn2009fi','sn2009gl','sn2009jv'] 


        sdss_sns = ['sn1994T','sn1996cb','sn1997bo','sn1998T','sn1998cc','sn1999cc','sn1999dk','sn2001G','sn2001cf','sn2001cy','sn2002ck','sn2002de','sn2003U','sn2003ej','sn2003hu','sn2003it','sn2004A','sn2004Z','sn2004ao','sn2004as','sn2004bg','sn2004bu','sn2005J','sn2005O','sn2005U','sn2005kc','sn2005mz','sn2006C','sn2006aa','sn2006bf','sn2006bq','sn2006by','sn2006dl','sn2006qp','sn2007O','sn2007ag','sn2008D','sn2008ht','sn2009fi','sn2009gl','sn2009jv']
        broadlined = ['sn1997dq','sn1997ef','sn1998ey','sn2002ap','sn2002bl','sn2003jd','sn2004bu','sn2004ib','sn2005da','sn2005fk','sn2005nb','sn2005kr','sn2005ks','sn2005kz','sn2006aj','sn2006nx','sn2006qk','sn2007D','sn2007I','sn2007bg','sn2007ru','sn2007eb','sn2007gx','sn2010ah','sn2010ay']


        
        import MySQLdb
        db2 = MySQLdb.connect(db='calib')
        c = db2.cursor()



        if False:
            for sn in broadlined:                                                
                command= 'update calib set broadlined=1.0 where sn="' + sn + '"'
                c.execute(command)
            print 'finished'
            raw_input()
 



        sdict = dict(zip(sdss_sns,sdss_sns))
        from glob import glob
        run = 'kpno_Dec2010'
        for run in ['kpno_Dec2010','kpno_Oct2010','kpno_Mar2010','kpno_May2010']:
            fs = glob('/Volumes/mosquitocoast/patrick/kpno/' + run + '/work_night/*')
            print fs
            go = True #False
            import slr_kpno_new
            reload(slr_kpno_new)        
            print fs
            for sn in fs[:]:
                snpath = sn.split('/')[-1]


                command = "SELECT * from STATUS where SN='" + snpath + "' and RUN='" + run + "'" #+ "' and FUNCTION='" + str(self.f.__name__) + "'"

                #command = "SELECT * from STATUS as s join calib as c on (s.sn=c.sn and s.run=c.run) where c.sdsscov=1 and s.SN='" + snpath + "' and s.RUN='" + run + "'" #+ "' and FUNCTION='" + str(self.f.__name__) + "'"
                print command
                c.execute(command)                                                                                                       
                results = c.fetchall()
                print results

                found = False
                all = sdss_sns + broadlined
                for b in all:
                    if b == snpath: 
                        print 'found'
                        found = True 

                print found 

                import string
                if string.find(snpath,'RXJ') == -1 and len(results) == 0 and glob(sn + '/z_raw/*.fits')  and glob(sn + '/SDSS_g/*.fits'):
                    print snpath

                    try:                                                                      
                        ex(run,snpath)            
                    except KeyboardInterrupt:
                        raise Exception
                    except: print 'fail'
                    print 'finished'
                print found, snpath
                if sn.split('/')[-1] == 'sn2006bq':
                    go = True 
               

def nights():

    
    import MySQLdb
    db2 = MySQLdb.connect(db='calib')
    c = db2.cursor()

    command = "SELECT SN, RUN, FILES, JD from calib where night is null"   #+ "' and FUNCTION='" + str(self.f.__name__) + "'"
    print command
    c.execute(command)                                                                                                       
    results = c.fetchall()

    for l in results:
        sn, run, files, jd = l              
        NIGHTID = int(get_night(float(jd)))
    
        command = 'update calib set NIGHT=' + str(NIGHTID) + ' where jd="' + jd + '" and sn="' + sn + '"'
        print command

        c.execute(command)






 




def f():
    from glob import glob
    import commands
    out = commands.getoutput('gethead *.fits OBJECT')

    found = {}

    for l in out.split('\n'):
        import re        
        res = re.split('\s+',l[:-1])
        print res[1]
        for b in broadlined:
            if b == 'sn' + res[1] or b == res[1]: 
                print 'found', res[1]
                found[b] = 'yes'

    print '\n', found.keys()
    



def reset():
    import MySQLdb
    db2 = MySQLdb.connect(db='calib')
    c = db2.cursor()
                                                                                                                                        
    command = "SELECT SN from CALIB where SDSSZP is not null or SLRZP is null group by sn" #+ "' and FUNCTION='" + str(self.f.__name__) + "'"
    print command
    c.execute(command)                                                                                                       
    results = c.fetchall()
    print results

    ''' BROKEN! '''
    for result in []: #results:
        command = "DELETE from status where sn='" + result[0] + "'"
        print command
        c.execute(command)

        command = "DELETE from calib where sn='" + result[0] + "'"
        print command
        c.execute(command)
        

def transfer(run,night,snpath): 
    import os, sys, re, commands
    from glob import glob

    base = os.environ['kpno'] + '/' + run + '/' + night + '/' + snpath + '/'

    fs = glob(base + '/*/reg.sdss.fits')        

    for f in fs:
        detector = commands.getoutput('gethead ' + f + ' DETECTOR')
        filt = f.split('/')[-2] + '_' + detector
        base_filt = os.environ['sdss'] + '/' +  snpath + '/' + filt + '/'
        print base_filt
        os.system('mkdir -p ' + base_filt)
        output = base_filt + 'reg' + filt + '.fits'
        os.system('rm ' + output)
        os.system('ln -s ' + f + ' ' + output)
        output = base_filt + 'reg' + filt + '.weight.fits'            
        os.system('rm ' + output)
        os.system('ln -s ' + f.replace('.fits','.weight.fits') + ' ' + output)
        


    
def test():
    run('kpno_Dec2010','sn2008gl')        
