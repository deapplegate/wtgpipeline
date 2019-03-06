def run_check(OBJNAME=None,fix=False):
    import MySQLdb, sys, os, re, time, utilities, pyfits, string                                                                                                                          
    from copy import copy

    if fix: prefix = 'fix_'
    else: prefix = ''

    loop = True
    while loop:        
        
        db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-sr01')
        c = db2.cursor()

        db_keys_t = describe_db(c,['clusters_db'])

        if OBJNAME is None and not fix:
            command='SELECT * from clusters_db where cutoutstatus is null and photozstatus like "%finished%" '  
        else:
            command='SELECT * from clusters_db where OBJNAME="' + OBJNAME + '"' 
            loop = False

        print command                                                  
        c.execute(command)                                             
        results=c.fetchall()                                           
        random_dict = {}
        line = results[0]
        dtop2 = {}  
        for i in range(len(db_keys_t)):
            dtop2[db_keys_t[i]] = str(line[i])



        ''' check to see how many filters there are '''
        filters = dtop2['info']
        import re
        num_fs = len(filters.split(' ')[2:])

        if num_fs < 0:
            commandst = 'update clusters_db set cutoutstatus="few filters" where objname="' + dtop2['objname'] + '"'
            c.execute(commandst)                                             
        else:
            ''' get detection filter '''                                                                                                                              
            subdir = '/nfs/slac/g/ki/ki05/anja/SUBARU/' 
            from datetime import datetime
	
            		
            os.system('mkdir -p ' + os.environ['sne'] + '/scamp/')
            logfile = os.environ['sne'] + '/photoz_log/' + dtop2['objname']
            import os
            os.system('rm ' + logfile)

            commandst = 'update clusters_db set ' + prefix + 'cutoutstatus="started ' + str(datetime.now()) + '" where objname="' + dtop2['objname'] + '"'
            c.execute(commandst)                                             
            commandst = 'update clusters_db set logfile="' + logfile + '" where objname="' + dtop2['objname'] + '"'
            c.execute(commandst)                                             



            
            try:



                print dtop2['objname']
                
                lensing_band = get_lensing_filts(subdir, dtop2['objname'])[0]
                print lensing_band

                import subprocess
                os.chdir(os.environ['bonn'])

                if 'redsequence' in tasks:
                    command = 'python redsequence.py -c ' + dtop2['objname'] + ' -d ' + lensing_band + ' -w -z '  
                    print command 
                    a = subprocess.call(command,shell=True)

                if 'specs' in tasks:
                    command = 'python cutout_bpz.py ' + dtop2['objname'] + ' detect=' + lensing_band + ' aptype=aper APER1 '#  + logfile
                    print command 
                    a = subprocess.call(command,shell=True)
                if float(a) != 0: 
                    commandst = 'update clusters_db set ' + prefix + 'cutoutstatus="failed ' + str(datetime.now()) + '" where objname="' + dtop2['objname'] + '"'
                else:
                    commandst = 'update clusters_db set ' + prefix + 'cutoutstatus="finished" where objname="' + dtop2['objname'] + '"'
                c.execute(commandst)                                             
            except KeyboardInterrupt:
                raise
            except:
                import traceback
                print traceback.print_exc(file=sys.stdout)
                commandst = 'update clusters_db set ' + prefix + 'cutoutstatus="failed ' + str(datetime.now()) + '" where objname="' + dtop2['objname'] + '"'
                c.execute(commandst)                                             
                                                                                                                                                                      
            print 'finished'
