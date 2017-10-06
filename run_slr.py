
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

def sdss_cat(run, rerun, camcol, field):   


    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-sr01')
    c = db2.cursor()

    field = int(field)
    field_OR = '(' + reduce(lambda x,y: x + ' or ' + y, ['s.field=' + str(x) for x in [field,field+1,field+2,field+3,field+4,field+5]]) + ')'

    db_keys_t = describe_db(c,['sdsstwomass'])
                                                                          
    command='SELECT * from sdsstwomass where run=' + str(run) + ' and rerun=' + str(rerun) + ' and camcol=' + str(camcol) + ' and ' + field_OR   
                                                                          
    print command                                                  
    c.execute(command)                                             
    results=c.fetchall()                                           
    random_dict = {}
   
    sdss = [] 
    for line in results:
        dtop2 = {}                             
        for i in range(len(db_keys_t)):
            dtop2[db_keys_t[i]] = str(line[i])
        sdss.append(dtop2)
    
    return sdss


import sys
(NULL, fieldid, run, rerun, camcol, field) = sys.argv

sdss_cat(run, rerun, camcol, field)

''' make output catalog '''
cols = [] 
for key in sdss_array[0].keys():
    cols.append(pyfits.Column(name=key,format='DN', array=scipy.array([x[key] for x in sdss_array])))
                                                                                                      
output = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
os.system('rm ' + sdss_input_cat)
output.writeto(sdss_input_cat)
