
import sys, os , re
import datetime, string
from glob import glob

if len(sys.argv) < 2: print 'python find_bad.py CLUSTER_NAME'
cluster = sys.argv[1]
subdir = '/nfs/slac/g/ki/ki05/anja/SUBARU/' 

list = glob(subdir + '/' + cluster + '/*_*/SCIENCE/')
backmask_list = []
blank_list = []
good_list = []
for dir in list:

    dir = dir.replace('SCIENCE/','')

    pattern = dir + '/SCIENCE/reg/*reg'
    wlist = glob(pattern)

    if len(wlist) == 0:
        if string.find(dir,'CALIB') == -1:
            blank_list.append(re.split(cluster.replace('+','plus'),dir.replace('+','plus'))[1].replace('plus','+'))
    else:
        backmask_bad = False
        for weightfile in wlist:                                                                  
            helldate = datetime.datetime(2010,02,02)                                             
            savedate = datetime.datetime(2010,03,26)                                           
            #if not os.path.exists(weightfile):                                                 
            #    return False                                                                   
            moddate = datetime.datetime.fromtimestamp(os.path.getmtime(weightfile))            
            if moddate < helldate:                                                  
                backmask_bad = True
        print dir
        if backmask_bad: backmask_list.append(re.split(cluster.replace('+','plus'),dir.replace('+','plus'))[1].replace('plus','+'))
        else: good_list.append(re.split(cluster.replace('+','plus'),dir.replace('+','plus'))[1].replace('plus','+'))
print 'list', list
print '\n\ngood_list (Modified since Feb 2 BUT NOT NECESSARILY BACKMASKED!):', good_list
print '\n\nbackmask_list (Region files exist but modified before Feb 2):',backmask_list
print '\n\nblank_list (No region files exist):',blank_list

import commands
op = commands.getoutput('grep ' + cluster + ' ' + subdir + '/lensing.bands') 
print '\n\nlensing band', op
print '\n\nInstructions:'
print 'If lensing band is in the backmask_list, then need to do backmasking'
print 'If non-lensing band is in backmask_list, then nothing to do'
print 'If any run is on blank_list, need to start from scratch'
