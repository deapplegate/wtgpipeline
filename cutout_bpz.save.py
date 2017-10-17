import math, re, sys
import pylab  # matplotlib
import os
import astropy.io.fits as pyfits,random, scipy
if not 'sne' in os.environ:
    os.environ['sne'] = '/nfs/slac/g/ki/ki04/pkelly'
#os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] +':/nfs/slac/g/ki/ki04/pkelly/lib/python2.5/site-packages/PIL/'

#def mkstellarcolorplot():

def star_num(filters,catalog,starcatalog,cluster,magtype,name_suffix=''):
    print catalog, starcatalog
    p = pyfits.open(catalog)['OBJECTS'].data
    s = pyfits.open(starcatalog)
    indices = s['OBJECTS'].data.field('SeqNr')
    ddict = {}
    for index in indices:
        p.field('CLASS_STAR')[index-1] = -999 
    mask = p.field('CLASS_STAR') == -999 
    table = p[mask]
  
    dict = {} 
    for filt in filters: 
        good = scipy.ones(len(table.field('MAG_' + magtype + '-' + filters[0])))
        at = table.field('MAG_' + magtype + '-' + filt)[:] 
        aterr = table.field('MAGERR_' + magtype + '-' + filt)[:] 
        good[at==-99]  = 0
        good[aterr>0.2]  = 0
        print len(good), len(at), len(aterr)
        dict[filt] = len(at[good==1])
        #print at[good==1], aterr[good==1]

    return dict 

def save_db(cluster,dict):
    import os, re, sys, commands, MySQLdb
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    cdb = db2.cursor()

    cdb.execute("DROP TABLE IF EXISTS photoz_db")

    command = "CREATE TABLE IF NOT EXISTS photoz_db ( id MEDIUMINT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id), cluster varchar(80), extinction float(8,2), mu float(10,4),  sigma float(10,4), num_stars int(5), date_run varchar(80))"
    print command
    cdb.execute(command)

    command = 'select cluster from photoz_db where cluster="' + cluster + '"'
    cdb.execute(command)
    results=c.fetchall()                                           
    if not len(results):
        print command
        command = 'insert into photoz_db (cluster) values ("' + cluster + '")'
        cdb.execute(command)
    for key in dict.keys():
        print command
        command = 'update photoz_db set ' + key + '="' + dict[key] + '"'
        cdb.execute(command)
    
    


def histogram2d(x, y, z, bins=10, range=None, normed=False, weights=None,
                log = False,
                filename = None,
                **formating):

    import scipy
    X, Y = pylab.meshgrid(x,y)
    pylab.clf()
    pylab.xlim([0,1])
    pylab.ylim([0,1])
    pylab.pcolor(X, Y,z)
    pylab.colorbar()
    #doFormating(**formating)
    #pylab.show()
    if filename is not None:
        pylab.savefig(filename)
        pylab.clf()


def conv_filt(filt_info):

    import string

    ''' convert to list from ddictionary '''
    if type({}) == type(filt_info[0]):
        fix = []        
        for f in filt_info:
            fix.append(f['name'])
        filt_info = fix


    filters_b = []
    name_t = None
    for f in filt_info:
        if string.find(f,'MEGAPRIME') != -1:
            n = f[-1]
        if string.find(f,'SUBARU') != -1:
            import re
            res = re.split('-W',f)
            print res, f
            n = 'W' + res[1]
        if string.find(f,'WHT') != -1:
            import re
            n = f[-1] + '-WHT'
        if n != name_t:
            filters_b.append(n)
            name_t = n

    return filters_b



def filt_num(x):
    filter_order = ['U-WHT','u','B','g','V','r','R','i','I','z','Z','J','H','K']
    print x, 'x'
    x = x.replace('SUBARU','').replace('SPECIAL','').replace('WIRCAM','').replace('MEGAPRIME','').replace('-J-','')
                                                                                                                  
    from copy import copy
    import string
    for e in range(len(filter_order)):
        if string.find(x,filter_order[e]) != -1:  
            x_num = copy(e)            

    return x_num

def sort_filters(x,y):
    ''' sort filter list to make color-color plots '''

    x_num = filt_num(x)
    y_num = filt_num(y)

    print x_num, y_num
    if x_num > y_num: return 1     
    elif x_num <= y_num: return -1     


def locus():
    import os, re
    f = open('locus.txt','r').readlines()
    id = -1
    rows = {}
    colors = {}
    for i in range(len(f)):
        l = f[i]
        if l[0] != ' ':
            rows[i] = l[:-1]
        else: 
            id += 1 
            colors[rows[id]] = [float(x) for x in re.split('\s+',l[:-1])[1:]]
    print colors.keys() 
    import pylab
    #pylab.scatter(colors['ISDSS_ZSDSS'],colors['ZSDSS_JTMASS'])       
    #pylab.show()

    import pickle 
    f = open('newlocus','w')
    m = pickle.Pickler(f)
    locus = colors
    pickle.dump(locus,m)
    f.close() 

    return colors


def get_locus(): 
    import pickle
    f = open('newlocus','r')
    m = pickle.Unpickler(f)
    locus = m.load()
    return locus




def mkcolorcolor(filt,catalog,starcatalog,cluster,magtype,name_suffix=''):
    print catalog, filt
    locus_c = get_locus()

    locus_c_old = locus()
    import os
    base = os.environ['sne'] + '/photoz/' + cluster + '/'
    file_web = 'stars' + name_suffix + '.html'        
    print base + file_web
    f = open(base + file_web ,'w',0)
    from datetime import datetime
    f2 = datetime.now()
    f.write('created ' + f2.strftime("%Y-%m-%d %H:%M:%S") + '<br>\n')
    f.write(name_suffix + '<br>\n')
    print filt
    filt.sort(sort_filters)
    print filt

    ''' group filters '''
    groups = {}
    for ft in filt:
        num = filt_num(ft)
        if not num in groups:
            groups[num] = []
        groups[num].append(ft)

    print groups
    print catalog


    print catalog, starcatalog

    p = pyfits.open(catalog)['OBJECTS'].data

    s = pyfits.open(starcatalog)
    indices = s['OBJECTS'].data.field('SeqNr')
    ddict = {}
    for index in indices:
        p.field('CLASS_STAR')[index-1] = -999 

    mask = p.field('CLASS_STAR') == -999 
    p = p[mask]

    print len(p)


    #mask = p.field('FWHM_WORLD')*3600. < 1.1 
    #p = p[mask]

    print len(p)        


    #while not plot:

    list = []
    for g in sorted(groups.keys()):
        list.append(groups[g])

    print list

    l_new = []
    l_fs = {}

    locus_ddict = {}
    for filt in list:
        for f2 in filt:
            a_short = f2.replace('+','').replace('C','')[-1]  
            print filt, a_short
                                                                   
            import string

            ok = True                                           
            if string.find(f2,'MEGAPRIME') != -1:
                a_short = 'MP' + a_short.upper() + 'SUBARU'
            elif string.find(f2,'SUBARU') != -1:
                if string.find(f2,"W-S-") != -1:
                    a_short = 'WS' + a_short.upper() + 'SUBARU'
                else:
                    a_short = a_short.upper() + 'JOHN'

                #if string.find(f2,"-1-") == -1:
                #    ok = False
            
            if ok:                                                       
                l_new.append([filt,a_short])                           
                l_fs[a_short] = 'yes'
                print a_short, filt
                if not a_short in locus_ddict: locus_ddict[a_short] = []
                locus_ddict[a_short].append(f2)

    print locus_ddict

    print l_fs

    list = ['RJOHN','IJOHN','WSZSUBARU'] 

    list = ['BJOHN','VJOHN','RJOHN','IJOHN']

    #list = ['RJOHN','VJOHN','IJOHN','WSZSUBARU','BJOHN']

    import re
    good_fs = []

    print l_fs
    for k1 in locus_c.keys():
        res = re.split('_',k1)
        print res
        if l_fs.has_key(res[0]) and l_fs.has_key(res[1]):
            print res[0], res[1], list, list[0] == res[0]
            print string.find(res[0],'MEGAPRIME-10_2-1-u') != -1
            if True: #string.find(res[0],'MPUSUBARU') != -1: # and res[1] != 'MPUSUBARU': #True: #filter(lambda z: z==res[0], list) and filter(lambda z: z==res[1], list): 
                good_fs.append([res[0],res[1]])

    print l_fs, locus_ddict, good_fs

    print good_fs

    for f1A,f1B in good_fs:         
        for f2A,f2B in good_fs:         
            print f1A, f1B
            if f1A!=f1B and f2A!=f2B and (f1A != f2A or f1B != f2B) and string.find(f1A + f2A + f1B + f2B,'MPUSUBARU') != -1:
                import random
                for a in [locus_ddict[f1A][random.randint(0,len(locus_ddict[f1A])-1)]]:
                    for b in [locus_ddict[f1B][random.randint(0,len(locus_ddict[f1B])-1)]]:
                        for c in [locus_ddict[f2A][random.randint(0,len(locus_ddict[f2A])-1)]]:
                            for d in [locus_ddict[f2B][random.randint(0,len(locus_ddict[f2B])-1)]]:

                                print a,b,c,d                                                                                                                       
                                import string                                                                                                   
                                def fix(q): 
                                    if string.find(q,'MEGA') != -1:         
                                        import re                           
                                        res = re.split('-',q)               
                                        q = 'MEGAPRIME-0-1-' + res[-1]      
                                    print q                                 
                                    return q                                
                                                                                       
                                import pylab                                           
                                                                                       
                                pylab.clf()                                            
                                
                                if 0: #a==b or ==f2B:                                
                                    print a,b,c,d
                                    print f1A,f1B,f2A,f2B
                                                                                       
                                #pylab.savefig(outbase + '/RedshiftErrors.png')        
                                table = p                                             
                                                                                      
                                print 'MAG_' + magtype + '-' + a                                 
                                print a,b,c                                           
                                #print table.field('MAG_ISO-' + a)                    
                                print magtype, 'MAG_' + magtype + '-' + a

                                zpcorr = {'RJOHN':0.0561109, 'WSZSUBARU':0.02313778, 'WSISUBARU': -0.04197, 'VJOHN': -0.091787, 'MPUSUBARU': -0.04319, 'MPRSUBARU':0.00954, 'MPGSUBARU': -0.059051}

                                zpcorr = dict(zip(['RJOHN', 'WSZSUBARU', 'WSISUBARU', 'VJOHN', 'BJOHN', 'IJOHN'], [ 0.0, 0.01571196,  0.00405996, -0.05531905,  0.04641784, -0.00286244]))

                                zpcorr = dict(zip(['RJOHN', 'WSZSUBARU', 'VJOHN', 'MPUSUBARU', 'BJOHN', 'IJOHN'],[0.0, 0.16363356, -0.13339831, -0.60397947, -0.39826345,  0.10153089] ))

                                zpcorr = dict(zip(['RJOHN','BJOHN','VJOHN','IJOHN'],[0.0,0.0,-0.03,0.024]))

                                zpcorr = dict(zip(['RJOHN','BJOHN','VJOHN','WSZSUBARU','IJOHN'],[0.0,0.0416,-0.05945,0.01619,-0.0028]))

                                zpcorr = dict(zip(['RJOHN','BJOHN','VJOHN','WSZSUBARU','IJOHN'],[0.0,-0.13871001,-0.01459012, 0.02050701,-0.00349759])) #[0.,-0.16933,-0.04595,0.06188,0.0303]))
                                zpcorr = dict(zip(['RJOHN','BJOHN','VJOHN','WSZSUBARU','IJOHN'],[0., -0.0481614, -0.03835155, 0.04469805, 0.03616314])) #[0., -0.06746946, -0.00798711,  0.01964501,  0.00293682])) 

                                zpcorr = dict(zip(['RJOHN', 'BJOHN', 'VJOHN', 'WSZSUBARU', 'IJOHN'],[0., 0.056, 0.062, 0.067,   0.065])) #[0., -0.06746946, -0.00798711,  0.01964501,  0.00293682])) 
                                #zpcorr = dict(zip(['RJOHN', 'BJOHN', 'VJOHN', 'WSZSUBARU', 'IJOHN'],[0.0, -0.45059467,-0.15827509, 0.18687479, 0.1177458 ]))

                                
                                file2 = os.environ['subdir'] + '/' + cluster + '/PHOTOMETRY/pat_slr.calib.pickle'   
                                from glob import glob
                                if glob(file2):
                                    import pickle            
                                    f2 = open(file2,'r')
                                    m = pickle.Unpickler(f2)
                                    a2 = m.load()
                                    results = a2['results']
                                    zpcorr = results['full']
                                    print zpcorr

                                print zpcorr
                                at = table.field('MAG_' + magtype + '-' + a)[:] 
                                bt = table.field('MAG_' + magtype + '-' + b)[:] 
                                ct = table.field('MAG_' + magtype + '-' + c)[:] 
                                dt = table.field('MAG_' + magtype + '-' + d)[:] 

                                aterr = table.field('MAGERR_' + magtype + '-' + a)[:] 
                                bterr = table.field('MAGERR_' + magtype + '-' + b)[:] 
                                cterr = table.field('MAGERR_' + magtype + '-' + c)[:] 
                                dterr = table.field('MAGERR_' + magtype + '-' + d)[:] 

                                import scipy                               
                                good = scipy.ones(len(at))
 
                                good[at==-99]  = 0
                                good[bt==-99]  = 0
                                good[ct==-99]  = 0
                                good[dt==-99]  = 0

                                good[aterr>0.3]  = 0
                                good[bterr>0.3]  = 0
                                good[cterr>0.3]  = 0
                                good[dterr>0.3]  = 0

                                bt = bt[good==1]                                      
                                ct = ct[good==1]                                      
                                dt = dt[good==1]                                      
                                at = at[good==1]                                      

                                bterr = bterr[good==1]                                      
                                cterr = cterr[good==1]                                      
                                dterr = dterr[good==1]                                      
                                aterr = aterr[good==1]                                      

                                                                                      
                                ''' apply modified zeropoints ''' 
                                if False:                                                      
                                    import scipy
                                    at = at - scipy.ones(len(at))*zpcorr[f1A]                                                      
                                    bt = bt - scipy.ones(len(bt))*zpcorr[f1B]                                                     
                                    ct = ct - scipy.ones(len(ct))*zpcorr[f2A]                                                     
                                    dt = dt - scipy.ones(len(dt))*zpcorr[f2B]                                                     

                                if len(at) and len(bt) and len(ct) and len(dt) and len(locus_c[f1A + '_' + f1B])==len(locus_c[f2A + '_' + f2B]):                   
                                    x = at - bt                                       
                                    y = ct -dt                                        


                                    xerr = (aterr**2. + bterr*2.)**0.5                                       
                                    yerr = (cterr**2. + dterr**2.)**0.5                                        
                                                                                      
                                    x = x[:]                                      
                                    y = y[:]                                      


                                
                                                                                      
                                    print x[0:100], y[0:100]                                        


                                    pylab.clf()
                                    
                                    pylab.xlabel(a + ' - ' + b)                            
                                    pylab.ylabel(c + ' - ' + d)                            

                                    pylab.errorbar(x,y,xerr=xerr,yerr=yerr,fmt=None,c='blue')                            
                                    pylab.scatter(x,y,s=1,c='red')                            

                                    pylab.xlim([sorted(x)[3],sorted(x)[-3]])
                                    pylab.ylim([sorted(y)[3],sorted(y)[-3]])
                                                                                      
                                    #pylab.scatter(locus_c[f1A + '_' + f1B],locus_c[f2A + '_' + f2B],color='red',s=2.)                  

                                    pylab.scatter(locus_c_old[f1A + '_' + f1B],locus_c_old[f2A + '_' + f2B],color='green',s=1.)                  
                                    print len(x), 'x'
                                                                                      
                                    #pylab.axis([sorted(x)[5],sorted(x)[-5],sorted(y)[5
                                    file = name_suffix + a+ b+ c+ d + '.png'    
                                    print file
                                    pylab.savefig(base + file)                        
                                    #pylab.show()
                                    pylab.clf()                                       
                                                                                      
                                    f.write('<img src=' + file + '>\n')               
                                plot = False                                          
                                print len(at), len(bt), len(ct), len(dt), len(locus_c[f1A + '_' + f1B])==len(locus_c[f2A + '_' + f2B]), f1A, f2A, f1B, f2B



                            






    f.close()


    return file_web

def plot_res(file_name,outbase,SPECTRA,type='bpz'):
    import os, sys, anydbm, time
    import lib, scipy, pylab 
    from scipy import arange
   
    print file_name 
    
    file = open(file_name,'r').readlines()
    results = []
    anjaplot = open('anjaplot','w')
    anjaplot.write('# Z_PHOT Z_MIN Z_MAX ODDS Z_SPEC\n')
    
    
    diff = []
    z = []
    z_spec = []
    for line in file:
        if line[0] != '#':
            import re                                     
            res = re.split('\s+',line)
            if res[0] == '': res = res[1:]
            if type is 'bpz':
                anjaplot.write(res[1] + ' ' + res[2] + ' ' + res[3] + ' ' + res[5] + ' ' + res[9] + '\n') 
                if float(res[5]) > 0.4:
                    #for i in range(len(res)):
                    #    print res[i],i
                    #print res
                    if True: #float(res[9]) > 0:
                        results.append([float(res[1]),float(res[9])])
            elif type is 'eazy': 
                if  float(res[8]) > 0.5:
                    results.append([float(res[2]),float(res[1])])

    
    for line in results:                             
        #print line
        diff_val = (line[0] - line[1])/(1 + line[1])
        diff.append(diff_val)
        z.append(line[0])
        z_spec.append(line[1])

    #print results    
    anjaplot.close()

    #print diff, file_name
    
    list = diff[:]  
    import pylab   
    varps = [] 
    #print diff        
    a, b, varp = pylab.hist(diff,bins=arange(-0.2,0.2,0.016),color='blue',edgecolor='black')
    #print a,b,varp
    varps.append(varp[0])
    
    diffB = []
    for d in diff:
        if abs(d) < 0.1:
            diffB.append(d)
    diff = diffB
    list = scipy.array(diff)
    mu = list.mean()
    sigma = list.std()
    
    #print 'mu', mu
    #print 'sigma', sigma
    
    from scipy import stats
    pdf = scipy.stats.norm.pdf(b, mu, sigma)
    #print 'pdf', pdf
    
    height = scipy.array(a).max()
    
    pylab.plot(b,len(diff)*pdf/pdf.sum(),color='red')

    print b,len(diff)*pdf/pdf.sum()
    
    pylab.xlabel("(PhotZ - SpecZ)/(1 + SpecZ)")
    pylab.ylabel("Number of Galaxies")
    pylab.title(['mu ' + str(mu),'sigma ' + str(sigma)])
    print outbase
    os.system('mkdir -p ' + outbase + '/' + SPECTRA)
    pylab.savefig(outbase + '/' + SPECTRA + '/RedshiftErrors.png')
    #pylab.show()

    #save_db(cluster,{'mu':mu,'sigma':sigma})

    pylab.clf()


    
    pylab.scatter(z_spec,z)
    pylab.plot(scipy.array([0,4]),scipy.array([0,4]),color='red')
    pylab.xlim(0,4)
    pylab.ylim(0,4)
    pylab.ylabel("PhotZ")
    pylab.xlabel("SpecZ")
    pylab.savefig(outbase + '/' + SPECTRA + '/RedshiftScatter04.png')

    pylab.clf()

    pylab.scatter(z_spec,z)
    pylab.plot(scipy.array([0,1.3]),scipy.array([0,1.3]),color='red')
    pylab.xlim(0,1.3)
    pylab.ylim(0,1.3)
    pylab.ylabel("PhotZ")
    pylab.xlabel("SpecZ")
    pylab.savefig(outbase + '/' + SPECTRA + '/RedshiftScatter01.png')

    #pylab.show()
    pylab.clf()
    print outbase + '/RedshiftScatter01.png'

def scale(val):
    #    return 10**(-0.4*(val+48.60))
    return (-0.4*(val+48.60))
    

def scaleerr(val):
    #    return 10**(-0.4*(val+48.60))
    return (-0.4*(val))

def plot(file,outfile):
    #    for file in files:
    print file
    f=open(file,'r')
    lines=f.readlines()
    
    mag=[]
    magerr=[]
    lambdamean=[]
    lambdawidth=[]
    
    specmag=[]
    speclambda=[]
    specmag1=[]
    speclambda1=[]

    oldval=9999999.
    flag=0
    
    gal1info={}
    
    gal2info={}
    
    for line in lines:
        entries=re.split('\s+',line)
        if entries[0]=='GAL-1':
            gal1info['Model'] = entries[2]
            gal1info['Library'] = entries[3]
            

            
        if entries[0]=='GAL-2':
            gal2info['Model'] = entries[2]
            gal2info['Library'] = entries[3]
            


        if entries[0]!='':
            continue

        length=len(entries)

        
        
        if length > 4:
            # filter part
            if float(entries[1]) < 90:
                mag.append(scale(float(entries[1])))
                magerr.append(scaleerr(float(entries[2])))
                # magerr.append(0)
                lambdamean.append(float(entries[3]))
                lambdawidth.append(float(entries[4])/2)
        elif entries[1]>100 :
            if (oldval > entries[1]) and (float(oldval)/float(entries[1]) > 10) :
                flag=1

            if not flag:                                
                if float(entries[1]) < 12000 and float(entries[2]) < 25 and \
                   float(entries[1]) > 2000 and float(entries[2]) > 10:
                    speclambda.append(float(entries[1]))
                    specmag.append(scale(float(entries[2])))
                    oldval=entries[1]
            else :
                if float(entries[1]) < 12000 and float(entries[2]) < 25 and \
                   float(entries[1]) > 2000 and float(entries[2]) > 10:
                    speclambda1.append(float(entries[1]))
                    specmag1.append(scale(float(entries[2])))
                    oldval=entries[1]
                    
    pylab.xlabel("Lambda; Gal1 Model"+ gal1info['Model']+", lib:"+gal1info['Library']+\
                 ", Gal2: Model"+ gal2info['Model']+", lib:"+gal2info['Library'])
    
    pylab.ylabel("Log10(Flux)")
    pylab.plot(speclambda,specmag,'b-')
    #pylab.plot(speclambda1,specmag1,'g-')
    pylab.errorbar(lambdamean,mag,xerr=lambdawidth,yerr=magerr,fmt='ro')
    

    print "showing"
    pylab.savefig(outfile)
    pylab.clf()
    #pylab.show()

def plot_bpz_probs(id,file,outfile):    
    import re, scipy
    a = re.split('\(',file[0])
    b = re.split('\)',a[-1])
    r = [float(x) for x in re.split('\,',b[0])]
    x_axis = scipy.arange(r[0],r[1],r[2])

    for l in file:
        res = re.split('\s+',l)
        if l[0] != '#':
            if int(res[0]) == int(id):        
                arr = scipy.array([float(x) for x in res[1:-1]])
                import copy
                x_axis = x_axis[arr>0]
                x_axis = scipy.array([x_axis[0]-0.01] + list(x_axis) + [x_axis[-1]+0.01])
                arr = arr[arr>0]
                arr = scipy.array([0] + list(arr) + [0])
                
                pylab.fill(x_axis, arr,'b')
                pylab.xlabel('z')
                pylab.ylabel('P')
                pylab.savefig(outfile)
                pylab.clf()
    

from utilities import *
def run(cluster):

    ratio = []
    import os
    import os, sys, bashreader, commands
    from config_bonn import appendix, tag, arc, filters, filter_root, appendix_root

    type='all'
    AP_TYPE = ''
    magtype = 'APER1'
    DETECT_FILTER = ''
    SPECTRA  = 'CWWSB_capak.list'
    LIST = None
    if len(sys.argv) > 2:
        for s in sys.argv:
            if s == 'spec':
                type = 'spec' 
            elif s == 'rand': 
                type = 'rand'
            elif s == 'all': 
                type = 'all'
            elif s == 'picks': 
                type = 'picks'
            elif s == 'ISO': 
                magtype = 'ISO'
            elif s == 'APER1': 
                magtype = 'APER1'

            import string
            if string.find(s,'detect') != -1:
                import re
                rs = re.split('=',s)
                DETECT_FILTER= '_' + rs[1]
            if string.find(s,'aptype') != -1:
                import re
                rs = re.split('=',s)
                AP_TYPE='_' + rs[1]
            if string.find(s,'spectra') != -1:
                import re
                rs = re.split('=',s)
                SPECTRA=rs[1]
            if string.find(s,'spectra') != -1:
                import re
                rs = re.split('=',s)
                SPECTRA=rs[1]
            if string.find(s,'list') != -1:
                import re
                rs = re.split('=',s)
                LIST=rs[1]



    print DETECT_FILTER

    print cluster
    
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%s/' % cluster
    
    
    filecommand = open('record.analysis','w')
    
    BASE="coadd"
    image = BASE + '.fits'

    from glob import glob
    
    images = []
    filters.reverse()
    print filters
    ims = {}
    ims_seg = {}

    params = {'path':path, 
              'filter_root': filter_root, 
              'cluster':cluster, 
              'appendix':appendix, 
               'DETECT_FILTER':DETECT_FILTER,                    
                'AP_TYPE': AP_TYPE
                }


    params['SPECTRA'] = SPECTRA
    params['type'] = type 
    params['magtype'] = magtype
    outputcat = '%(path)s/PHOTOMETRY%(DETECT_FILTER)s%(AP_TYPE)s/%(cluster)s.%(magtype)s.1.%(SPECTRA)s.%(type)s.bpz.tab' % params 

    catalog = '%(path)s/PHOTOMETRY%(DETECT_FILTER)s%(AP_TYPE)s/%(cluster)s.slr.cat' %params           
    starcatalog = '%(path)s/PHOTOMETRY%(DETECT_FILTER)s%(AP_TYPE)s/%(cluster)s.stars.calibrated.cat' %params           
    import do_multiple_photoz, os
    filterlist = do_multiple_photoz.get_filters(catalog,'OBJECTS')
    print filterlist
                                                                                                                        
    filters = conv_filt(filterlist)
    y = {} 
    for f in filters: 
        y[f] = 'yes'
    filters = y.keys()
    filters.sort(sort_filters)
    print filters

    stars_dict = star_num(filterlist,catalog,starcatalog,cluster,'APER1',name_suffix='')

    os.system('mkdir -p ' + os.environ['sne'] + '/photoz/' + cluster + '/' + SPECTRA + '/') 

    if False:

        pagemain = open(os.environ['sne'] + '/photoz/' + cluster + '/' + SPECTRA + '/index.html','w')    
        pagemain.write('<table align=left><tr><td colspan=5 class="dark"><h1>' + cluster + '</h1></td></tr><tr><td colspan=5><a href=http://www.slac.stanford.edu/~pkelly/photoz/' + cluster + '/stars.html>Stellar Color-Color Plots</a><td></tr><tr><td colspan=5><a href=redsequence.html>Red Sequence Redshifts</a><td></tr><tr><td><a href=objects.html>Photoz Plots</a><td></tr><tr><td><a href=thecorrections.html>Correction Plots</a><td></tr><tr><td><a href=zdistribution.html>Z Distribution</a><td></tr></table>\n')
        pagemain.close()
        p = pyfits.open(outputcat)['STDTAB'].data
        pylab.clf()
        pylab.hist(p.field('BPZ_ODDS'),bins=scipy.arange(0,1,0.02))
        pylab.xlabel('ODDS')
        pylab.ylabel('Number of Galaxies')
        pylab.savefig(os.environ['sne'] + '/photoz/' + cluster + '/' + SPECTRA +'/odds.png')
        cut = 0.5
        p = p[p.field('BPZ_ODDS')>cut]
        pylab.clf()
        pylab.hist(p.field('BPZ_Z_B'),bins=scipy.arange(0,4,0.02))
        pylab.xlabel('Photometric Redshift')
        pylab.ylabel('Number of Galaxies (ODDS > ' + str(cut) + ')')
        pylab.savefig(os.environ['sne'] + '/photoz/' + cluster + '/' + SPECTRA +'/zdist.png')
        pagemain = open(os.environ['sne'] + '/photoz/' + cluster + '/' + SPECTRA + '/zdistribution.html','w')  
        pagemain.write('<img src=zdist.png></a>')
        pagemain.write('<img src=odds.png></a>')
        pagemain.close()
        pylab.clf()
        
        import flux_comp 
        corrections, plot_dict, title_dict = reload(flux_comp).calc_comp(cluster,DETECT_FILTER.replace('_',''),AP_TYPE,SPECTRA,type='all',plot=True)
        print corrections
        pagemain = open(os.environ['sne'] + '/photoz/' + cluster + '/' + SPECTRA + '/thecorrections.html','w')  

        def s(a,b): 
            if corrections[a] < corrections[b]:
                return 1
            else: return -1

        keys2 = corrections.keys()
        keys2.sort(s)

        import scipy 
        from scipy import stats
        kernel = scipy.array([scipy.stats.norm.pdf(i,1.) for i in [4,3,2,1,0,1,2,3,4]])
        kernel = kernel / kernel.sum()

        pagemain.write('<br>CORRECTIONS<br><ul>')
        ims = ''
        nums = '<br><br>NUMBER OF GOOD STARS<br><ul>\n'
        for key in keys2:
            if key != 'ID' and key != 'Z_S':
                file = os.environ['sne'] + '/photoz/' + cluster + '/' + SPECTRA + '/' + key + '.png'
                pylab.clf()
                o = pylab.hist(plot_dict[key],bins=100,range=[0.5,1.5])
                y_smooth = scipy.convolve(o[0],kernel,'same')#[5:-5]
                print o[1], y_smooth, len(o[1]), len(y_smooth)
                #pylab.linewidth = 4
                xs = o[1][:-1]+scipy.ones(len(o[1][:-1]))*(o[1][1]-o[1][0])*0.5
                ys = y_smooth 
                pylab.plot(xs,ys,'r',linewidth=2)
                pylab.suptitle(title_dict[key])
                print o
                pylab.savefig(file)
                ims += '<img src=' + key + '.png></a>\n'
                a = zip(y_smooth,xs)
                a.sort()
                max = a[-1][1]
                pagemain.write(key + ' median=' + str(corrections[key]) + ' smoothed peak=' + str(max) +   '<br>')
                nums += key + ' ' + str(stars_dict[key]) + '<br>\n'
        pagemain.write('</ul>' + nums +  '</ul>' + ims)
        pagemain.close()

    os.system('mkdir -p ' + os.environ['sne'] + '/photoz/' + cluster)           

    #mkcolorcolor(filterlist,catalog,starcatalog,cluster,'APER1',name_suffix='aperapercalib')

    #mkcolorcolor(filterlist,catalog,starcatalog,cluster,',name_suffix='')
    if False:
        mkcolorcolor(filterlist,catalog,starcatalog,cluster,'APER1',name_suffix='')

    #import sys
    #sys.exit(0)        

    print catalog

    #catalog = '/u/ki/dapple/subaru/MACS2243-09/PHOTOMETRY_W-J-V_iso/MACS2243-09.aper.slr.cat' 
    #file = mkcolorcolor(filterlist,catalog,starcatalog,cluster,'ISO',name_suffix='isomags_apercalib')

    #catalog = '/u/ki/dapple/subaru/MACS2243-09/PHOTOMETRY_W-J-V_iso/MACS2243-09.slr.cat' 
    #file = mkcolorcolor(filterlist,catalog,starcatalog,cluster,'ISO',name_suffix='isomags_isocalib')


    #catalog = '/u/ki/dapple/subaru/MACS2243-09/PHOTOMETRY_W-J-V_aper/MACS2243-09.slr.cat' 
    #file = mkcolorcolor(filterlist,catalog,starcatalog,cluster,'APER1',name_suffix='apermags_apercalib')


    #print file

    ffile = os.environ['sne'] + '/photoz/' + cluster + '/all.tif'

    print filters
    if not glob(ffile):

        print filters[1:4]
        for filt in filters[1:4]:                                                                 
            #filter = filter.replace('MEGAPRIME-0-1-','').replace('SUBARU-10_2-1-','').replace('SUBARU-10_2-2-','').replace('SUBARU-10_1-1-','').replace('SUBARU-10_1-2-','')#.replace('SUBARU-8-1-','')
            params = {'path':path, 
                      'filter_root': filter_root, 
                      'cluster':cluster, 
                      'filter':filt,
                      'DETECT_FILTER': DETECT_FILTER,  
                        'AP_TYPE':AP_TYPE,
                      'appendix':appendix, }
            print params
            # now run sextractor to determine the seeing:              
            image = '%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits' %params 
            images.append(image)
            print 'reading in ' + image        
            seg_image = '/%(path)s/%(filter)s/PHOTOMETRY/coadd.apertures.fits' % params
            ims[filt] = pyfits.open(image)[0].data
            print 'read in ' + image        
            #ims_seg[filter] = pyfits.open(seg_image)[0].data

        print images
        
        os.system('mkdir ' + os.environ['sne'] + '/photoz/' + cluster + '/')
        os.system('chmod o+rx ' + os.environ['sne'] + '/photoz/' + cluster + '/')
        
        from glob import glob
        os.system('stiff ' + reduce(lambda x,y:x + ' ' + y,images) + ' -OUTFILE_NAME ' + ffile + ' -BINNING 1 -GAMMA_FAC 1.6')
        os.system('convert ' + os.environ['sne'] + '/photoz/' + cluster + '/all.tif ' + os.environ['sne'] + '/photoz/' + cluster + '/fix.tif')
    
    print ffile
    
    import Image
    im = Image.open(os.environ['sne'] + '/photoz/' + cluster + '/fix.tif')
    
    
    
    
    
    
    

    print catalog
    p_cat = pyfits.open(catalog)[1].data
    
    #outputcat = '%(path)s/PHOTOMETRY/all_bpz1_' % params 
    #spec = True 

    picks = False 
 
    #SPECTRA =  'CWWSB4_txitxo.list' 
    #SPECTRA = 'CWWSB_capak.list' # use Peter Capak's SEDs

    print SPECTRA

    
    
    
    

    outbase = os.environ['sne'] + '/photoz/' + cluster + '/'

    os.system('mkdir -p ' + outbase + '/' + SPECTRA + '/')

    SeqNr_file = open('SeqNr_file','w')

    if type == 'spec':
        probsout = '%(path)s/PHOTOMETRY%(DETECT_FILTER)s%(AP_TYPE)s/%(cluster)s.%(magtype)s.1.%(SPECTRA)s.%(type)s.probs' % params  
        #outputcat = '%(path)s/PHOTOMETRY/%(cluster)s.1.all.bpz.tab' % params 

        print probsout, outputcat.replace('.tab','')
        f = open(probsout,'r').readlines()
        fz_temp = open(outputcat.replace('.tab',''),'r').readlines()

        fz = []
        for l in fz_temp: 
            if l[0] != '#': fz.append(l)
        
            
        import re 
                                                                                            
        res = re.split('\s+',f[0])
        print res[4]
        res2 = re.split('\,',res[4].replace('z=arange(','').replace(')',''))
        print res2
        import scipy
        increment = float(res2[2])
        #matrix = scipy.array(zs*
    
        print zip(f[1:],fz[:])[1] #zs

        end = int(1./increment)

        zs = (scipy.arange(float(res2[0]),1.+increment,increment))

        prob_matrix = scipy.zeros((end,end))


        for l,zf in zip(f[1:],fz[:]):
            #print l, zf
            import re
            resz = re.split('\s+',zf[:-1])
            if resz[0] == '': resz = resz[1:]
            #print resz
            z_spec = float(resz[9])
            odds = float(resz[5])
            res = re.split('\s+',l[:-1])
            if res[-1] == '': res = res[:-1]
            #print res
            pdz = scipy.array([float(x) for x in res[1:]])
            from copy import copy
            zs_copy = copy(zs)
            #zs_copy = zs_copy[pdz != 0]
            #pdz = pdz[pdz != 0]
            #print zs_copy, pdz, resz[9]
            for i in range(len(zs_copy))[:end]: #z,p in zip(zs_copy, pdz):
                if odds > 0.95 and z_spec < 1.:
                    prob_matrix[i,int(z_spec/increment)] += pdz[i] 

            #print prob_matrix
            
            #pdz.append(
        print 'done calculating'            


        X, Y = pylab.meshgrid(zs_copy,zs_copy)

        print prob_matrix.shape, X.shape, Y.shape


        pylab.clf()


        print prob_matrix.max()

        prob_matrix[prob_matrix>1] =1. 

        pylab.pcolor(X, Y,-1.*prob_matrix,cmap='gray',alpha=0.9,shading='flat',edgecolors='None')


        pylab.plot([0,1],[0,1],color='red')
        pylab.xlabel('SpecZ')
        pylab.ylabel('PhotZ')

        pylab.savefig(outbase + '/' + SPECTRA + '/RedshiftPDZ01.png')
        #pylab.pcolor(X, Y,prob_matrix,cmap='gray',alpha=0.9,shading='flat',edgecolors='None')
        #pylab.colorbar()
        #doFormating(**formating)
        #histogram2d(zs_copy,zs_copy,prob_matrix)    

    #for l in f[1:]:
    #    res = re.split('\s+',l)
    #    print res
        
    

    if True: #glob(outputcat.replace('.tab','')):
        plot_res(outputcat.replace('.tab',''),outbase, SPECTRA)

    print 'plot_res'
     
    print outputcat
    bpz_cat = pyfits.open(outputcat)[1].data

    

    
   
    print outputcat
    gals = [] 

    set = range(len(bpz_cat))
    if type == 'rand':
        set = range(100)



    f_nums = [e[:-1] for e in open('SeqNr_save','r').readlines()]
    
    for i in set: #[0:25]: #[75227,45311,53658, 52685, 64726]:
        print i
        line = bpz_cat[i]
        print line, outputcat
        text = ''
    
    #for x,y,side,index in [[4800,4900,200,1],[5500,5500,100,2],[4500,5500,300,2]]:
    
        text += '<tr>\n'
        SeqNr = int(line['SeqNr'])
        fileNumber = str(int(line['BPZ_NUMBER']))
        params['fileNumber'] = str(fileNumber)
    
        base = '%(path)s/PHOTOMETRY%(DETECT_FILTER)s%(AP_TYPE)s/%(cluster)s.%(magtype)s.1.%(SPECTRA)s.%(type)s' % params
        probs =  '%(path)s/PHOTOMETRY%(DETECT_FILTER)s%(AP_TYPE)s/%(cluster)s.%(magtype)s.1.%(SPECTRA)s.%(type)s.probs' % params
        print probs

        print base, probs

    
        resid = line['BPZ_Z_B'] - line['BPZ_Z_S']

        z = line['BPZ_Z_B']
    
        ODDS = line['BPZ_ODDS']

        

        if True: #line['BPZ_ODDS'] > 0.5 and 0.6 < line['BPZ_Z_B'] < 0.8 and 0.2 < line['BPZ_Z_S'] < 0.4: #abs(resid) > 0.2: #abs(resid) > 0.04 and 0.4 < line['BPZ_Z_S'] < 0.6: #True: #SeqNr==24778: # SeqNr == 4441 or SeqNr==1285: #abs(resid) > 0.1:    

#        print f_nums
#        if True: #len(filter(lambda x: int(line['SeqNr']) == int(x),f_nums)): 

            probs_f = open(probs,'r').readlines()

            print line['SeqNr']
            file = '/nfs/slac/g/ki/ki04/pkelly/photoz/' + cluster + '/' +  SPECTRA + '/' + str(SeqNr) + 'spec.png' #print 'SAVING', outdir + outimg                                            
            sys.argv = ['',base,str(SeqNr),file]
            import sedplot
            print base, 'base'
            filt_info = sedplot.run()
            print filt_info 
            import math
            
            if 1: #filt_info[0]['flux'] > 0:
                ratio.append(filt_info[0]['expectedflux']/filt_info[0]['flux'])
                                                                                                                                                                                               
                                                                                                                                                                                               
            #import pylab                                        
            #from scipy import arange
            #print ratio        
            #import scipy
            #print 'ratio', scipy.median(scipy.array(ratio))
            #a, b, varp = pylab.hist(ratio,bins=arange(0,5,0.1))
            #pylab.show()
                                                                
                                                                
            #if line['BPZ_ODDS'] > 0.95 and abs(resid) > 0.2: #abs(resid) > 0.04 and 0.4 < line['BPZ_Z_S'] < 0.6: #True: #SeqNr==24778: # SeqNr == 4441 or SeqNr==1285: #abs(resid) > 0.1:    

            #if 1:
            print line['BPZ_Z_B']
            SeqNr_file.write(str(SeqNr) + '\n')
            mask = p_cat.field('SeqNr') == SeqNr                                                                                                   
            temp = p_cat[mask]
            x = int(temp.field('Xpos')[0])
            y = 10000 - int(temp.field('Ypos')[0])
    
            x_fits = int(temp.field('Xpos')[0])
            y_fits = int(temp.field('Ypos')[0])
    
            import pyraf
            from pyraf import iraf
    
            if line['BPZ_Z_S'] != 0: 
                resid = line['BPZ_Z_B'] - line['BPZ_Z_S']
                if resid > 0: 
                    color='green'
                    resid_str = ' <font color=' + color + '>+' + str(resid) + '</font> '
                else: 
                    color='red'        
                    resid_str = ' <font color=' + color + '>' + str(resid) + '</font> '
            else:
                resid = 'no spec z' 
                color = 'black'
                resid_str = ' <font color=' + color + '>' + str(resid) + '</font> '
    
            
            t = ['BPZ_Z_B','BPZ_ODDS','BPZ_CHI-SQUARED','BPZ_Z_B_MIN','BPZ_Z_B_MAX']
            text += '<td colspan=10>' + str(SeqNr) + ' z=' + str(line['BPZ_Z_B']) + ' MIN=' + str(line['BPZ_Z_B_MIN']) + ' MAX=' + str(line['BPZ_Z_B_MAX']) +  resid_str  +' ODDS=' + str(line['BPZ_ODDS']) + ' TYPE=' + str(line['BPZ_T_B']) + ' CHISQ=' + str(line['BPZ_CHI-SQUARED']) + ' x=' + str(x) + ' y=' + str(y) + '</td></tr><tr>\n'
            
            print x,y
                                                                                                                                                   
            index = SeqNr
                                                                                                                                                   
            outfile = os.environ['sne'] + '/photoz/' + cluster + '/' + SPECTRA + '/' + str(index) + '.png' 
            plot_bpz_probs(index, probs_f, outfile)
                                                                                                                                                   
            #file = 'Id%09.f.spec' % index
            #outfile = os.environ['sne'] + '/photoz/' + str(index) + '.png' 
            #print outfile
            #plot(file,outfile)
            
            text += '<td align=left><img height=400px src=' + str(index)  + '.png></img>\n'
            text += '<img height=400px src=' + str(index)  + 'spec.png></img>\n'
            images = []
    
            file = '/nfs/slac/g/ki/ki04/pkelly/photoz/' + cluster + '/' +  str(SeqNr) + 'spec.png' #print 'SAVING', outdir + outimg
            command = 'python ' + os.environ['BPZPATH'] + '/plots/sedplot.py ' + base + ' ' + str(SeqNr) + ' ' + file
            print command
    
            import sedplot
    
            #sys.argv = ['',base,str(SeqNr),file]
            #filt_info = sedplot.run()
            #print filt_info 

            #print command
            #os.system(command)
            side = 100 #x = temp.field('Xpos')[0]

            if 1: #try:
                p = im.crop([x-side,y-side,x+side,y+side])
                image = os.environ['sne'] + '/photoz/' + cluster + '/' + SPECTRA + '/' + str(index) + '.jpg'  
                os.system('rm ' + image)
                p.save(image,'JPEG')
            #except: print 'fail'

            text += '<img src=' + str(index)  + '.jpg></img></td><td colspan=20></td>\n'
            text += '</tr>\n'
            keys = ['name','wavelength','observed','flux','fluxerror','expectedflux','chioffset']
            text += '<tr><td colspan=10><table><tr>' + reduce(lambda x,y: x + y,['<td>'+n+'</td>' for n in keys]) + "</tr>"
            for f in filt_info:
                text += '<tr>' + reduce(lambda x,y: x + y,['<td>'+str(f[n])+'</td>' for n in keys]) + "</tr>"
            text += "</table></td></tr>"
    
            side = 100 #x = temp.field('Xpos')[0]
            #if x_fits - 100 < 0: x_fits = 101
            #if y_fits - 100 < 0: y_fits = 101
            #if x_fits + 100 > 9999: x_fits = 9899
            #if y_fits + 100 > 9999: y_fits = 9899
            xlow = int(x_fits-side)
            xhigh = int(x_fits+side)
            ylow = int(y_fits-side)
            yhigh = int(y_fits+side)

            if xlow < 0: xlow = ''
            if ylow < 0: ylow = ''
            if xhigh > 9999: xhigh = ''
            if yhigh > 9999: yhigh = ''

            bounds = '[' + str(xlow) + ':' + str(xhigh) + ',' + str(ylow) + ':' + str(yhigh) + ']'
            text += '<td colspan=20><table>\n'
            textim = ''
            textlabel = ''
    
            import string
    
            filters_b = conv_filt(filt_info) 

            for filt in []: #filters_b: #[1:]:
                fitsfile = '/nfs/slac/g/ki/ki04/pkelly/photoz/' + cluster + '/' + SPECTRA + '/' +  str(SeqNr) + 'cutout' + filt + '.fits' #print 'SAVING', outdir + outimg  
                jpg = '/nfs/slac/g/ki/ki04/pkelly/photoz/' + cluster + '/' + SPECTRA + '/'+  str(SeqNr) + 'cutout' + filt + '.jpg' #print 'SAVING', outdir + outimg
                os.system('rm ' + fitsfile)
                os.system('rm ' + jpg)
                bigfile = '/a/wain023/g.ki.ki05/anja/SUBARU/' + cluster + '/' + filt + '/SCIENCE/coadd_' + cluster + '_all/coadd.fits'
                iraf.imcopy(bigfile + bounds,fitsfile)
                import commands
                seeing = commands.getoutput('gethead ' + bigfile + ' SEEING')
                print 'seeing', seeing 


                import os
                #os.system("ds9 " + fitsfile + " -view info no -view panner no -view magnifier no -view buttons no -view colorbar yes -view horzgraph no -view wcs no -view detector no -view amplifier no -view physical no -zoom to fit -minmax -histequ  -invert -zoom to fit -saveas jpeg " + jpg ) # -quit >& /dev/null &")        
                #os.system("xpaset -p ds9 " + fitsfile + "  -zoom to fit -view colorbar no -minmax -histequ  -invert -zoom to fit -saveas jpeg " + jpg  + " ") # -quit >& /dev/null &")        
                print 'bounds', bigfile + bounds
    
                com = ['file ' + fitsfile, 'zoom to fit', 'view colorbar no', 'minmax', 'scale histequ' , 'saveimage jpeg ' + jpg] # -quit >& /dev/null &")        
                for c in com:
                    z = 'xpaset -p ds9 ' + c
                    print z
                    os.system(z)
                print jpg
                text += '<td><img height=200px src=' + str(SeqNr)  + 'cutout' + filt + '.jpg></img></td>\n'
                textlabel += '<td>' + filt + ' seeing ' + seeing + '</td>\n'
            text += '<tr>' + textim +  '</tr><tr>' +  textlabel + '</tr></table></td></tr><tr>'
    
            #os.system('stiff ' + image_seg + ' -OUTFILE_NAME ' + image_seg.replace('fits','tif'))
            gals.append([line['BPZ_T_B'],text])

            
            
            
            from datetime import datetime
            t2 = datetime.now()
            file = os.environ['sne'] + '/photoz/' + cluster + '/' + SPECTRA + '/objects.html'
            print file
            page = open(file,'w')
            t = '<head><link href="http://www.slac.stanford.edu/~pkelly/photoz/table.css" rel="stylesheet" type="text/css"></head>' 
            t += '<table align=left><tr><td colspan=5 class="dark"><h1>' + cluster + '</h1></td></tr><tr><td colspan=5><h4>created ' + t2.strftime("%Y-%m-%d %H:%M:%S") + '</h4></td></tr><tr><td colspan=5><a href=stars.html>Stellar Color-Color Plots</a><td></tr>\n'

            if type == 'spec':
                t += '<tr><td colspan=5 class="dark"><h2>Spectroscopic Sample</h2></td></tr>\n'
                t += '<tr><td colspan=10 align=left><img height=400px src=RedshiftErrors.png></img>\n' 
                t += '<img height=400px src=RedshiftScatter04.png></img>\n'
                t += '<img height=400px src=RedshiftScatter01.png></img>\n'
                t += '<img height=400px src=RedshiftPDZ01.png></img></td></tr>\n'
            if type == 'rand':
                t += '<tr><td colspan=5 class="dark"><h2>Random Sample of 100 Galaxies</h2></td></tr>\n'
            if type == 'picks':
                t += '<tr><td colspan=5 class="dark"><h2>Pick</h2></td></tr>\n'


            page.write(t)
            gals.sort()
            for gal in gals:
                page.write(gal[1])
            page.write('<table>\n')
            page.close()
            print 'CLOSED!!'
            if len(gals) > 100:
                break
    
    
    
    ''' make SED plots '''


if __name__ == '__main__':    
    import sys
    cluster = sys.argv[1] #'MACS0717+37'
    run(cluster)
