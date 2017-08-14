def galextinct(ra, dec): 
        import urllib, os, re, string, anydbm
        gh = {}
        outpos = 'extinct'
        form = range(8)
        form[0] = "in_csys=Equatorial"
        form[1] = "in_equinox=J2000.0"
        form[2] = "obs_epoch=2000.0"
        form[3] = "lon=%(ra).7fd" % {'ra':float(ra)}
        form[4] = "lat=%(dec).7fd" % {'dec':float(dec)}
        form[5] = "pa=0.0" 
        form[6]= "out_csys=Equitorial"
        form[7]= "out_equinox=J2000.0"

        command = 'wget "http://nedwww.ipac.caltech.edu/cgi-bin/nph-calc?' + reduce(lambda x,y: str(x) + '&' + str(y),form) + '" -O /tmp/extout' + str(os.getpid())
        print command
        os.system(command)
        page = open('/tmp/extout' + str(os.getpid())).readlines()
        for q in ['U','B','V','R','J','H','K']:
                for m in page:
                        if m[0:3] == q + ' (' :
                                line = re.split('\s+', m)
                                print line
                                gh[q] = line[2]

        ebv= float(gh['B']) - float(gh['V'])
        print ebv

        return ebv

def get_lensing_filts(subdir,cluster):
    import re

    f = open(subdir + '/lensing.bands','r').readlines()
    lensing_filts = []
    record = False 
    import string
    for l in f:
        res = re.split('\s+',l)
        if res[0] != '':
            if string.find(res[0],cluster) != -1:  
                record = True
            else: record = False
    
        if record and res[1][0] == 'W':
            lensing_filts.append(res[1])

    return lensing_filts

def run():

    import re, commands

    subdir = '/nfs/slac/g/ki/ki05/anja/SUBARU/' 
    cluster = 'MACS0018+16'

    lensing_filts = get_lensing_filts(subdir,cluster)

    command = 'gethead ' + subdir + '/' + cluster + '/' + lensing_filts[0] + '/SCIENCE/coadd_' + cluster + '_all/coadd.fits CRVAL1 CRVAL2'
    print command        
    output = commands.getoutput(command)
    import re
    res = re.split('\s+',output)
    ebv = galextinct(res[0],res[1]) 

    import os, re, sys, commands, MySQLdb
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    cdb = db2.cursor()
    command = "CREATE TABLE IF NOT EXISTS photoz_db ( id MEDIUMINT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id), objname varchar(80), extinction float(8,2), offset float(10,4),  width float(10,4), num_stars int(), date_run varchar(80))"
    print command
    #c.execute("DROP TABLE IF EXISTS illumination_db")
    #c.execute(command)
    
    ''' get extinction in field '''
    
    
    #command = 'ALTER TABLE illumination_db ADD ' + column + ' varchar(240)'
    #c.execute(command)  
    
    ''' make website '''
