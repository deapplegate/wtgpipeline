import commands
import os

from glob import glob

for filter in ['W-J-V']:
    command = 'gethead ' + os.environ['subdir'] + '/HDFN/' + filter + '/SCIENCE/BADROTATION/SUPA*I.fits ROTATION'
    print command
    fs = commands.getoutput(command)
    import re
    res = re.split('\n',fs)
    files = []
    for r in res:
        res2 = re.split('\s+',r)        
        if float(res2[1]) == 40:
            files.append(res2[0])
            res3 = re.split('\_',res2[0])
            print res3
            os.system('rm ' + os.environ['subdir'] + '/HDFN/' + filter + '/SCIENCE/cat_scamp*/' + res3[0] + '*') 
    print files 

    if False:
        os.system('mkdir ' + os.environ['subdir'] + '/HDFN/' + filter + '/SCIENCE/BADROTATION/')                                                                                                        
        os.system('mkdir ' + os.environ['subdir'] + '/HDFN/' + filter + '/WEIGHTS/BADROTATION/')
                                                                                                                                                                                                        
        for f in files:
            os.system('mv ' + os.environ['subdir'] + '/HDFN/' + filter + '/SCIENCE/' + f +  ' ' + os.environ['subdir'] + '/HDFN/' + filter + '/SCIENCE/BADROTATION/')
            os.system('mv ' + os.environ['subdir'] + '/HDFN/' + filter + '/WEIGHTS/' + f.replace('I.fits','I.weight.fits') +  ' ' + os.environ['subdir'] + '/HDFN/' + filter + '/WEIGHTS/BADROTATION/')
                                                                                                                                                                                                        
            #raw_input()
            #f2 = re.split('\_',f)[0]
            #os.system('rm ' + os.environ['subdir'] + '/HDFN/' + filter + '/SCIENCE/astrom_photom_scamp_SDSS-R6/'


