import os
from glob import glob

f = open('slr_list','r').readlines()
finished = open('finished','w')
for l in f:
    cluster = l[:-1]
    
    file = os.environ['subdir'] + '/' + cluster + '/PHOTOMETRY/' + cluster + '.ISO.1.photoz.CWWSB_capak.list.slr.tab'
    test = glob(file)

    print cluster, test

    if test:
        import datetime                                 
        compdate = datetime.datetime(2010, 6, 8)
        t = os.path.getmtime(file)
        headertime = datetime.datetime.fromtimestamp(t)

        print headertime, compdate

        if headertime > compdate:
            finished.write(cluster + '\n')
