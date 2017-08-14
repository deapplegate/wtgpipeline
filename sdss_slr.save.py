
import MySQLdb, sys, os, re, time, string                                                                                                                          

def describe_db(c,db=['illumination_db']):
    if type(db) != type([]):
        db = [db]
    keys = []
    for d in db:
        command = "DESCRIBE " + d 
        #print command
        c.execute(command)
        results = c.fetchall()
        for line in results:
            keys.append(line[0])
    return keys    


def make_database():

    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-sr01')
    c = db2.cursor()

    command = 'drop table if exists sdssdust'
    c.execute(command)

    command = 'create table if not exists sdssdust (stripe int, fieldid bigint not null, primary key (fieldid), field int, run int, rerun int, camcol int, mustart float(12,8), ramin float(12,8), ramax float(12,8), decmin float(12,8), decmax float(12,8), u float(10,4), g float(10,4), r float(10,4), i float(10,4), z float(10,4), racenter float(12,8), deccenter float(12,8), gallat float(12,8), gallong float(12,8), EBV float(12,8), slrstatus VARCHAR(80), downloadstatus VARCHAR(80), starfile VARCHAR(200) )'
    print command
    c.execute(command)                

    command = "load data local infile '/nfs/slac/g/ki/ki04/pkelly/SLR/SDSSchunks_pkelly50.csv' into table sdssdust fields terminated by ',' lines terminated by '\n' ignore 1 lines"
    print command
    c.execute(command)

def sdss_cat(run,rerun,camcol,field):   

    field = int(field) 
    field_OR = '(' + reduce(lambda x,y: x + ' or ' + y, ['s.field=' + str(x) for x in [field,field+1,field+2,field+3,field+4,field+5]]) + ')'

    query = 'select ccFlag, t.j as psfmag_J, sqrt(1/t.jivar) as psfmagerr_J, s.psfmag_u, s.psfmag_g, s.psfmag_r, s.psfmag_i, s.psfmag_z, s.psfmagerr_u, s.psfmagerr_g, s.psfmagerr_r, s.psfmagerr_i, s.psfmagerr_z from twomass as t, star as s where t.objID=s.objID and ' + field_OR + ' and s.run=' + str(run) + ' and s.rerun=' + str(rerun) + ' and s.camcol=' + str(camcol) + ' and t.jivar != 0 and flags & dbo.fPhotoFlags(\'BLENDED\') = 0 and ccFlag = "000" '

    print query

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

def download(): 

    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-sr01')
    c = db2.cursor()

    db_keys_t = describe_db(c,['sdssdust'])
                                                                          
    command='SELECT * from sdssdust where slrstatus is null order by rand() limit 2'  
                                                                          
    print command                                                  
    c.execute(command)                                             
    results=c.fetchall()                                           
    random_dict = {}
    line = results[0]
    dtop2 = {}  
    for i in range(len(db_keys_t)):
        dtop2[db_keys_t[i]] = str(line[i])

    sdss_cat(dtop2['run'],dtop2['rerun'],dtop2['camcol'],dtop2['field'])







def run_slr(FIELDID=None,):
    from copy import copy


    loop = True
    while loop:        
        
        db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-sr01')
        c = db2.cursor()

        db_keys_t = describe_db(c,['sdssdust'])

        if FIELDID is None:
            command='SELECT * from sdssdust where slrstatus is null'  
        else:
            command='SELECT * from sdssdust where FIELDID="' + FIELDID + '"' 
            loop = False

        print command                                                  
        c.execute(command)                                             
        results=c.fetchall()                                           
        random_dict = {}
        line = results[0]
        dtop2 = {}  
        for i in range(len(db_keys_t)):
            dtop2[db_keys_t[i]] = str(line[i])

        if 1:
            ''' get detection filter '''                                                                                                                              
            subdir = '/nfs/slac/g/ki/ki05/anja/SUBARU/' 
            from datetime import datetime
            if False: #len(results) > 0:
                commandst = 'update sdssdust set magstatus="not ready" where fieldid="' + dtop2['fieldid'] + '"'
                c.execute(commandst)                                             
            else:
                os.system('mkdir -p ' + os.environ['sne'] + '/scamp/')
                import os

                commandst = 'update sdssdust set magstatus="started ' + str(datetime.now()) + '" where fieldid="' + dtop2['fieldid'] + '"'
                c.execute(commandst)                                             
                commandst = 'update sdssdust set logfile="' + logfile + '" where fieldid="' + dtop2['fieldid'] + '"'
                c.execute(commandst)                                             
                try:
                    print dtop2['fieldid']
                    
                    lensing_band = get_lensing_filts(subdir, dtop2['fieldid'])[0]
                    print lensing_band

                    import subprocess
                    os.chdir(os.environ['bonn'])

                    command = 'python run_slr.py ' + dtop2['fieldid'] + ' detect=' + lensing_band + ' aptype=aper APER1 '
                    print command 
                    a = subprocess.call(command,shell=True)
                    if float(a) != 0: 
                        commandst = 'update sdssdust set magstatus="failed ' + str(datetime.now()) + '" where fieldid="' + dtop2['fieldid'] + '"'
                    else:
                        commandst = 'update sdssdust set magstatus="finished" where fieldid="' + dtop2['fieldid'] + '"'
                    c.execute(commandst)                                             
                except KeyboardInterrupt:
                    raise
                except:
                    import traceback
                    print traceback.print_exc(file=sys.stdout)
                    commandst = 'update sdssdust set magstatus="failed ' + str(datetime.now()) + '" where fieldid="' + dtop2['fieldid'] + '"'
                    c.execute(commandst)                                             
                                                                                                                                                                      
            print 'finished'
