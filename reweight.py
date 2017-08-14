def get_ending(subdir,cluster,filt):
    from glob import glob
    l = glob(subdir + '/' + cluster + '/' + filt + '/SCIENCE/*_7*fits')
    print l[0]        
    ending = re.split('\_7',l[0].replace('.fits','').replace('.sub',''))[1]
    if ending[-1] == 'R': ending = ending[:-1]
    if ending[-1] == 'I': ending = ending[:-1]
    if ending[-1] == 'R': ending = ending[:-1]

    return ending

def get_suppression(subdir,cluster,filt):
    from glob import glob
    import datetime
    pattern = subdir + '/' + cluster + '/' + filt + '/SCIENCE/*suppression*'
    print pattern
    l = glob(pattern)
    youngest = datetime.datetime(1000,02,02)                                             
    dir = None
    for a in l:
        import string
        if string.find(a,'_test') == -1:
            moddate = datetime.datetime.fromtimestamp(os.path.getmtime(a))             
            print moddate
            print a
            if moddate > youngest: 
                dir = a
                youngest = moddate

    return dir
    
    
def get_lensing_filts(subdir,cluster):
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

            
    







import sys, os
cluster = sys.argv[1]


subdir = '/nfs/slac/g/ki/ki05/anja/SUBARU/' 

import commands, string
all_filts = commands.getoutput('grep ' + cluster + ' cluster_cat_filters.dat') 
import re
all_filts = re.split('\s+',all_filts)[2:]
lensing_filts = get_lensing_filts(subdir,cluster)
print lensing_filts

print all_filts, lensing_filts



if len(sys.argv)>2:
    option = sys.argv[2]
    for f in lensing_filts:
        ending = get_ending(subdir,cluster,f)                                                                      
        print 'MAKE SURE TO GET SUFFIX RIGHT!'
        command = './submit_coadd_batch2_coma.sh ' + cluster + ' "all good exposure" ' + f + ' ' + ending + 'I kipac-xocq &'
        print command
    import sys
    sys.exit(0)

print all_filts    

''' run through lensing bands '''
for filt in all_filts:
    if string.find(filt,'W-')!= -1:
        if len(filter(lambda x: filt==x, lensing_filts)): 
            ending = get_ending(subdir,cluster,filt)
            print ending

            suppressiondir = get_suppression(subdir,cluster,filt)
            if suppressiondir is None:
                print "COULD NOT FIND AUTOSUPPRESSION for " + filt + ", CONTINUE? (y or n)"
                good = raw_input()
                import sys
                if good[0] == 'n': sys.exit(1)

            if suppressiondir is not None:
                command = './full_suppression.sh ' + cluster + ' ' + filt + ' ' + suppressiondir + ' ' + ending + ' kipac-xocq "CLEAN REGEN SUPPRESS MOVE IC BADCCD" & '
            else:

                command = './full_suppression.sh ' + cluster + ' ' + filt + ' "" ' + ending + ' kipac-xocq "CLEAN REGEN IC BADCCD" &'
            print command
          
            os.system(command)

''' run through other bands '''
for filt in all_filts:
    if string.find(filt,'W-')!= -1:
        if not len(filter(lambda x: filt==x, lensing_filts)): 
            ending = get_ending(subdir,cluster,filt)
            print ending
            command = './full_suppression.sh ' + cluster + ' ' + filt + ' "" ' + ending + ' kipac-xocq "CLEAN REGEN IC BADCCD" &'
            print command
            os.system(command)

        #raw_input()
