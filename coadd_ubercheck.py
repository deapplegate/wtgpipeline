#!/usr/bin/env python

# coadd_ubercheck.py:
# --------------------------------
# usage: ./coadd_ubercheck.py cluster filter 
# 
# contributions welcome, should be of the form, 
# of a function that only needs cluster and filter
# and looks up the rest. The main just runs the checks.
# 
# No output unless there is somethong wrong or
# verbose flag is checked.
#
#
#

import sys, os,  glob , time, re, datetime, pyfits, ldac, numpy

#import check_scamp_dates

###############################3
def make_coadd_string(filt):
    soutputstring=''
    if filt[0]=='W':
        #s = glob.glob(subdir+'/'+cluster+'/'+filt+'/SCIENCE/SUPA*_3OC*I.fits')[0][:-5]
        ending = get_ending(subdir+'/'+cluster+'/'+filt+'/SCIENCE/SUPA*_3OC*I.fits') #s[(s.find('OC')):]
        if ending.count('R'):
            soutputstring+='./submit_coadd_batch2_coma.sh '+cluster+' \"all good exposure\" '+filt+'  '+ending+ ' '+q+ ' &\n' 
            return soutputstring 
        else:
            soutputstring+='./submit_coadd_batch2_coma.sh '+cluster+' \"all exposure\" '+filt+'  '+ending+ ' '+q+ ' &\n' 
            return soutputstring
    elif len(filt)==1:
        ending = 'C'
        soutputstring+='./submit_coadd_batch2_coma.sh '+cluster+' \"all exposure\" '+filt+'  '+ending+ ' ' + q +' &\n' 
        return soutputstring
    else:
        return '' 




#############################
def get_ending(f):
    s=glob.glob(f)[0][:-5]
    end = s[(s.find('OC')):]
    return end





#############################
def is_lensing_band(cluster, filt):
    filterlist=['W-J-V','W-C-RC','W-C-IC','W-S-I+','r','g','i']
    lensing_band_file=open('/nfs/slac/g/ki/ki05/anja/SUBARU/lensing.bands')

    for line in lensing_band_file.readlines():
        ent = re.split('\s+',line)
        if ent[0]==cluster:
            if ent[1] == filt:
                lensing_band_file.close()
                return True
            else:
                lensing_band_file.close()
                return False
            
    print 'can\'t find ',cluster, 'in /nfs/slac/g/ki/ki05/anja/SUBARU/lensing.bands'
            


##############################
def is_badccd(f):
    hdul=pyfits.open(f)
    hdu = hdul[0]
    if 'BADCCD' in hdu.header:
        if hdu.header['BADCCD'] != 1:
            hdul.close()
            return True

    hdul.close()
    return False



##############################
def check_chip6(cluster, filt,v):
    if not is_lensing_band(cluster, filt):
        return
    subdir='/nfs/slac/g/ki/ki05/anja/SUBARU/'
    flist = glob.glob(subdir+'/'+cluster+'/'+filt+'/SCIENCE/SUPA*_6*I.fits')

    check_table=False
    
    for f in flist:
        hdul=pyfits.open(f)
        hdu = hdul[0]
        if 'CONFIG' in hdu.header:
            if  (hdu.header['CONFIG'] != '10_2') and  (hdu.header['CONFIG'] != '10_1'):
                if v:
                    print 'Not 10 config, continuing', f
                continue
        
        if 'BADCCD' in hdu.header:
            if hdu.header['BADCCD'] != 1:
                print 'BADCCD flag set to ',hdu.header['BADCCD'], f
            else:
                if v: print 'OK: BADCCD flag set to ',hdu.header['BADCCD'], f
        else:
            if v:
                print 'BADCCD flag not set ', f, 'checking table'
            check_table=True
            
        
        hdul.close()

    if check_table:
        table = ldac.openObjectFile(subdir+'/'+cluster+'/'+filt+'/SCIENCE/'+\
                                    cluster+'_good.cat','CHIPS_STATS')
        inc_images=table['IMAGEID']*table[cluster+'_good']
        if 6 in inc_images:
            print 'Chip 6 not removed in lensing band', cluster, filt
        

        
################################
def check_header_exist(hdu,parameter,v):
    if parameter in hdu.header:
        if v:
            print 'Header OK', parameter#, hdu.header['OBJECT'], hdu.header['FILTER'] 
        return True
    else :
        #print hdu.header
        print 'Header missing',parameter#,'...', hdu.header['OBJECT'], hdu.header['FILTER'] 
        return False




#################################
def check_header_value(hdu,parameter,value,v):
    if parameter in hdu.header:
        if  hdu.header[parameter] == value:
            if v:
                print 'Header OK', parameter
                
            return True
        else :
            print 'Header wrong parameter',': ', hdu.header[parameter],' should be ', value
    else :
        print 'Header missing',parameter,'... ', 
        return False
    

#################################
def check_ic_headers(cluster, filt,v):

    subdir='/nfs/slac/g/ki/ki05/anja/SUBARU/'
    #flist = glob.glob[subdir+'/'+cluster+'/'+filt+'/SCIENCE/SUPA*I.fits']
    flist = glob.glob(subdir+'/'+cluster+'/'+filt+'/SCIENCE/coadd_'+cluster+'*/coadd.fits')
    
    
    # check ic dates
    
    # OBJECT, FILTER, SEEING, EXPTIME, and GAIN
    
    for thisf in flist:
        if thisf.find('pretty')>0:
            continue

        
        if v: print thisf
        hdul = pyfits.open(thisf)
        if len(hdul)==0:
            print 'HDU List empty. ',thisf
            continue;
            
        hdu=hdul[0]
        hdu.verify('silentfix')
        flag=True
        flag = flag and check_header_exist(hdu,'SEEING',v)
        flag = flag and check_header_exist(hdu,'EXPTIME',v)
        flag = flag and check_header_exist(hdu,'GAIN',v)
        flag = flag and check_header_value(hdu,'OBJECT',cluster,v)
        flag = flag and check_header_value(hdu,'FILTER',filt,v)
        if not flag:
            print 'problem with',thisf

        #
        
        #if hduic.header['PPRRUN_US'] == hduic.header['PPRUN']:
        #    if v:
        #        print 'Preprocessing run:',hduic.header['PPRUN'], '  IC run:',hduic.header['PPRRUN_US']

        
        
        #check_header_value(hdu,'OBJECT',cluster,v)
        #check_header_value(hdu,'FILTER',filt,v)
        hdul.close()
        
        

#################################
def check_coadd_size(cluster, filt,v):
    
    subdir='/nfs/slac/g/ki/ki05/anja/SUBARU/'
    flist = glob.glob(subdir+'/'+cluster+'/'+filt+'/SCIENCE/coadd_'+cluster+'*/coadd.fits')

    ideal_filesize = 400008960
    
    

    
    for f in flist:
        if f.find('pretty')>0 or f.find('old')>0:
            continue
        
        if os.path.getsize(f) != ideal_filesize:
            print f ,'has size',str(os.path.getsize(f)), 'not ', str(ideal_filesize)
        else:
            if v:
                print f,'is OK'
        
    flistweight = glob.glob(subdir+'/'+cluster+'/'+filt+'/SCIENCE/coadd_'+cluster+'*/coadd.weight.fits')
    
    for f in flistweight:
        if f.find('pretty')>0 or f.find('old')>0:
            continue
        if os.path.getsize(f) != ideal_filesize:
            print f ,'has size',str(os.path.getsize(f)), 'not ', str(ideal_filesize)
        else:
            if v:
                print f,'is OK'

    flistweight = glob.glob(subdir+'/'+cluster+'/'+filt+'/SCIENCE/coadd_'+cluster+'*/coadd.flag.fits')
    
    for f in flistweight:
        if f.find('pretty')>0 or f.find('old')>0:
            continue
        if os.path.getsize(f) != 100010880:
            print f ,'has size',str(os.path.getsize(f)), 'not ', str(100010880)
        else:
            if v:
                print f,'is OK'


    
########################




########################
def check_scamp_dates(cluster, filt,v):
    # This chunk is desined to check that the 
    # dates of the scamp headders against the
    # dates of the coadds.
    
    subdir='/nfs/slac/g/ki/ki05/anja/SUBARU/'

    compdate = datetime.datetime(2010, 3, 28)
    compfilterdate = datetime.date(2001, 03, 28)
    #the above is a complete coincidence
    
    # things to check:
    #  - first that all of the coadds are of a later date than
    #    the headders
    #  - and that the early data has been scamped later than Apr 1.
    
    
    
    if len(filt)==0:
        return
        
    fd1 = re.split('_',filt)
    cl_filt_cat = open('cluster_cat_filters.dat')
    for line in cl_filt_cat.readlines():
        set = re.split('\s+', line)
        if set[0] == cluster:
            db=set[1]
    cl_filt_cat.close()
    
    if len(fd1)==1 or  len(fd1)==3:
        filenames=subdir+'/'+cluster+'/'+filt+'/SCIENCE/headers_scamp_photom_'+db+'/*'

        if len(glob.glob(filenames))==0:
            print 'No header files in ',filenames
            return

        
        testfile=glob.glob(filenames)[0]
        
        t = os.path.getmtime(testfile)
        headertime = datetime.datetime.fromtimestamp(t)
        
        coaddname=subdir+'/'+cluster+'/'+filt+'/SCIENCE/coadd_'+cluster+'_all/coadd.fits'

        if not os.path.exists(coaddname):
            print coaddname, 'doesn\'t exist, recoadd'
            return

        t2 = os.path.getmtime(coaddname)
        coaddtime = datetime.datetime.fromtimestamp(t2)

        if os.path.getsize(coaddname)<1:
            print coaddname+' is null re-coadd...'
            # outputstring+= make_coadd_string(filt)  
            #continue
            return

        if headertime > coaddtime:
            #print 'checking '+filt+' Need to coadd '+cluster+' (='+ time.ctime(t)+') '+filt +' (='+ time.ctime(t2)+')'
            print 'headers (='+ time.ctime(t)+') '+ 'newer than the coadd, remake (='+ time.ctime(t2)+')', cluster, filt  
            # outputstring+= make_coadd_string(filt)            
            
        else:
            if v:
                print 'checking '+filt+" ... is OK "

            
        if fd1[0][0]=='W' and len(fd1)==1:
            # Subaru data, find the preprocessings:
            dirlist=glob.glob(subdir+'/'+cluster+'/'+filt+'_*')
            for ppr in dirlist:
                pprdate = re.split('_',ppr)[-1]
                if pprdate == 'CALIB':
                    continue
                
                fd2 = re.split('-',pprdate)
                

                if len(fd2)!=3:
                    continue
                
                if not (fd2[0].isdigit() and fd2[1].isdigit() and\
                        fd2[2].isdigit()):
                    continue
                
                filterdate = datetime.date(int(fd2[0]),\
                                           int(fd2[1]),int(fd2[2]))
    
                if filterdate < compfilterdate:        
                    if headertime < compdate:
                        print 'checking '+filt+'_'+pprdate+\
                              ' Early data: need to rerun scamp '+\
                              cluster+'(='+ time.ctime(t)+')'+filt+\
                              '(='+ time.ctime(t2)+')'
                        # outputstring='./do_Subaru_register_4batch.sh `grep '+\
                        #                  cluster+' cluster_cat_filters.dat `'

                        #print 'RUN: '+outputstring
                        #print 'THEN: source '+ outputfile
                            
                    else:
                        if v: print 'checking '+filt+'_'+pprdate+' Early data: OK'
                
                else:
                    if v: print 'checking '+filt+' Later data: OK'

        



######################    
def check_header_consistency(cluster, filt,v):
    
    cl_filt_cat = open('cluster_cat_filters.dat')
    for line in cl_filt_cat.readlines():
        set = re.split('\s+', line)
        if set[0] == cluster:
            db=set[1]

    cl_filt_cat.close()
    filelist = glob.glob('/nfs/slac/g/ki/ki05/anja/SUBARU/'+\
                         cluster+'/'+filt+'/SCIENCE/headers_scamp_photom_'+\
                         db+'/*_7.head')


    if len(filelist)==0:
        return
    
    if v:
        print 'checking','/nfs/slac/g/ki/ki05/anja/SUBARU/'+\
                         cluster+'/'+filt+'/SCIENCE/headers_scamp_photom_'+\
                         db+'/*_7.head' 
    
    vallist=[]
    for f in filelist:
        headfile=open(f)
        for line in headfile.readlines():
            ent = re.split('\s+',line)
            if ent[0]=='CRPIX1':
                vallist.append(float(ent[2]))
                break
        headfile.close()


    if len(filelist)!=len(vallist):
        print 'header files missing CRPIX values?  Look at',cluster,filt

    

    firstval=vallist[0]
    for val in vallist:
        if abs(val - firstval) > 1000:
            print 'Large dfference in CRPIX values: ',cluster,filt ,val,firstval  
        

def get_unique_set(seq):
    # not order preserving
    set = {}
    map(set.__setitem__, seq, [])
    return set.keys()



def check_chips_cat8(cluster, filt,v):
    subdir = '/nfs/slac/g/ki/ki05/anja/SUBARU/'
    if len(glob.glob(subdir+'/'+cluster+'/'+filt+'/SCIENCE/cat/chips.cat8')):
        if v:
            print glob.glob(subdir+'/'+cluster+'/'+filt+'/SCIENCE/cat/chips.cat8')
    else:
        print 'Can\'t find '+subdir+'/'+cluster+'/'+filt+'/SCIENCE/cat/chips.cat8'


def check_coadd_flags(cluster, filt,v):
    subdir = '/nfs/slac/g/ki/ki05/anja/SUBARU/'
    coaddlist = glob.glob(subdir+'/'+cluster+'/'+filt+'/SCIENCE/coadd_'+cluster+'*/coadd.flag.fits')


    
    
    for flagim in coaddlist:
        if v:
            print 'doing ',flagim
        if flagim.find('failed')>0 or flagim.find('bad')>0 or  flagim.find('rot')>0 or  flagim.find('good')>0 :
            if v:
                print 'continuing ', flagim, flagim.find('failed')>0 ,  flagim.find('bad')>0 ,   flagim.find('rot') ,   flagim.find('good')>0
            continue
        
        hdul = pyfits.open(flagim)
        if len(hdul)==0:
            print 'ignoring ',flagim
            continue
        data = hdul[0].data[:,:]
        #        if v:
        #    print 
        
        #print 'getting uniqueset'
        #set=[]
        
        #for i in range(10000):
        #    set[i] = get_unique_set(list(data.flatten()))

            
        #if v:
        #    print set
        #smallset = numpy.array(set)
        flag = (data>16).any()

        if flagim.find("SUPA")<0:
            continue
            
        if flagim.find("all")>0:
            if flag:
                print flagim, "has vals > 16: Problem "
                break
            else:
                if v:
                    print flagim, "has all vals <= 16: OK "
        else:
            if flag:
                if v:
                    print flagim, "has vals > 16: OK "
            else:
                print flagim, "has all vals <= 16: Problem "
                break


        #        -------------
        
        
        #boolarray = (data==16)
        #if v:
        #    print 0,boolarray
        #for i in [1,2,4,8]:
        #    boolarray = numpy.logical_or(boolarray, (data==i))
            #if v:
            #    print i,boolarray

        #if boolarray.all():
        #    print ' all 2^n number in flag image', flagim
        #else:
        #    if v: print flagim,' is OK'
        hdul.close()


    
    
######################
#def main(argv = sys.argv):
if __name__ == '__main__':

    argv = sys.argv
    if len(argv) < 2:
        print 'usage: ./coadd_ubercheck.py cluster  [verbose]'
        sys.exit(0)

    cluster = argv[1]
    v=0
    
    if 'verbose' in argv:
        v=1


    #    q='kipac-xocq'
    #   quelist=['long','xlong', 'kipac-xocq']
    # yes, I know that's not how its spelled.
    # for que in quelist:
    #    if que in quelist:
    #        q=que

    filterfile =  open('cluster_cat_filters.dat')
    for line in filterfile.readlines():
        set = re.split('\s+', line)
        if set[0] == cluster:
            db=set[1]
            filterset = set[2:]
    filterfile.close()

    
            
    if v :
        print ' Using verbose' 
    

    for filt in filterset:
        print 'Checking',cluster, filt
        
        if v:
            print 'Checking scamp dates', cluster, filt
        check_scamp_dates(cluster, filt,v)

        if v:
            print 'Checking IC headers', cluster, filt
        check_ic_headers(cluster, filt,v)

        if v:
            print 'Checking coadd sizes', cluster, filt
        check_coadd_size(cluster, filt,v)

        if v:
            print 'Checking chip 6', cluster, filt
        check_chip6(cluster, filt,v)

        if v:
            print 'Checking header CRPIX1', cluster, filt
        check_header_consistency(cluster, filt,v)

        if v:
            print 'Checking coadd flag values', cluster, filt
        check_coadd_flags(cluster, filt,v)
        if v:
            print 'Checking chips.cat8', cluster, filt
        check_chips_cat8(cluster, filt,v)
