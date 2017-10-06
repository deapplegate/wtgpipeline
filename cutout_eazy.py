import math, re, sys
import pylab  # matplotlib

def plot_res(file_name,outbase):
    import MySQLdb                                                  
    import os, sys, anydbm, time
    import lib, scipy, pylab 
    from scipy import arange
   
    print file_name 
    
    file = open(file_name,'r').readlines()
    results = []
    for line in file:
        if line[0] != '#':
            import re                                     
            res = re.split('\s+',line)
            if float(res[8]) > 0.95:
                #for i in range(len(res)):
                #    print res[i],i
                results.append([float(res[1]),float(res[7])])
    
    diff = []
    z = []
    z_spec = []
    for line in results:
        diff_val = (line[0] - line[1])/(1 + line[1])
        diff.append(diff_val)
        z.append(line[0])
        z_spec.append(line[1])
    
    list = diff[:]  
    import pylab   
    varps = [] 
    a, b, varp = pylab.hist(diff,bins=arange(-0.2,0.2,0.016))
    print a,b,varp
    varps.append(varp[0])
    
    diffB = []
    for d in diff:
        if abs(d) < 0.08:
            diffB.append(d)
    diff = diffB
    list = scipy.array(diff)
    mu = list.mean()
    sigma = list.std()
    
    print 'mu', mu
    print 'sigma', sigma
    
    from scipy import stats
    pdf = scipy.stats.norm.pdf(b, mu, sigma)
    print 'pdf', pdf
    
    height = scipy.array(a).max()
    
    pylab.plot(b,len(diff)*pdf/pdf.sum(),'r')
    
    pylab.xlabel("(PhotZ - SpecZ)/(1 + SpecZ)")
    pylab.ylabel("Number of Galaxies")
    pylab.title(['mu ' + str(mu),'sigma ' + str(sigma)])
    pylab.savefig(outbase + '/RedshiftErrors.png')
    pylab.clf()
    
    pylab.scatter(z_spec,z)
    pylab.plot(scipy.array([0,4]),scipy.array([0,4]),color='red')
    pylab.xlim(0,4)
    pylab.ylim(0,4)
    pylab.ylabel("PhotZ")
    pylab.xlabel("SpecZ")
    pylab.savefig(outbase + '/RedshiftScatter04.png')
    pylab.clf()

    pylab.scatter(z_spec,z)
    pylab.plot(scipy.array([0,1]),scipy.array([0,1]),color='red')
    pylab.xlim(0,1)
    pylab.ylim(0,1)
    pylab.ylabel("PhotZ")
    pylab.xlabel("SpecZ")
    pylab.savefig(outbase + '/RedshiftScatter01.png')
    pylab.clf()

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
    

import astropy.io.fits as pyfits
import os
import os, sys, bashreader, commands
from utilities import *
from config_bonn import appendix, cluster, tag, arc, filters, filter_root, appendix_root

cluster = sys.argv[1] #'MACS0717+37'
path='/nfs/slac/g/ki/ki05/anja/SUBARU/%s/' % cluster

plot_res('./OUTPUT/photz.zout','./OUTPUT/')

type='all'

filecommand = open('record.analysis','w')

BASE="coadd"
image = BASE + '.fits'

images = []
filters.reverse()
ims = {}
ims_seg = {}
for filter in filters[0:3]:
    params = {'path':path, 
              'filter_root': filter_root, 
              'cluster':cluster, 
              'filter':filter,
              'appendix':appendix, }
    print params
    # now run sextractor to determine the seeing:              
    image = '%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits' %params 
    images.append(image)
    print 'reading in ' + image        
    seg_image = '/%(path)s/%(filter)s/PHOTOMETRY/coadd.apertures.fits' % params
    ims[filter] = pyfits.open(image)[0].data
    print 'read in ' + image        
    #ims_seg[filter] = pyfits.open(seg_image)[0].data

os.system('mkdir ' + os.environ['sne'] + '/photoz/' + cluster + '/')
os.system('chmod o+rx ' + os.environ['sne'] + '/photoz/' + cluster + '/')

from glob import glob
ffile = os.environ['sne'] + '/photoz/' + cluster + '/all.tif'
if not glob(ffile):
    os.system('stiff ' + reduce(lambda x,y:x + ' ' + y,images) + ' -OUTFILE_NAME ' + ffile + ' -BINNING 1 -GAMMA_FAC 1.6')
    os.system('convert ' + os.environ['sne'] + '/photoz/' + cluster + '/all.tif ' + os.environ['sne'] + '/photoz/' + cluster + '/fix.tif')

import Image
im = Image.open(os.environ['sne'] + '/photoz/' + cluster + '/fix.tif')

catalog = '%(path)s/PHOTOMETRY/%(cluster)s.slr.cat' %params 
p_cat = pyfits.open(catalog)[1].data

outputcat = '%(path)s/PHOTOMETRY/%(cluster)s.1.spec.bpz.tab' % params 


#outputcat = '%(path)s/PHOTOMETRY/all_bpz1_' % params 

plot_res(outputcat.replace('.tab',''),os.environ['sne'] + '/photoz/' + cluster + '/')
print outputcat


spec = True 

if not spec:
    outputcat = '%(path)s/PHOTOMETRY/%(cluster)s.1.all.bpz.tab' % params 
bpz_cat = pyfits.open(outputcat)[1].data


gals = [] 

for i in range(len(bpz_cat)): #[75227,45311,53658, 52685, 64726]:
    print i
    line = bpz_cat[i]
    print line
    text = ''

#for x,y,side,index in [[4800,4900,200,1],[5500,5500,100,2],[4500,5500,300,2]]:

    text += '<tr>\n'
    SeqNr = int(line['BPZ_ID'])
    fileNumber = str(int(line['BPZ_NUMBER']))
    params['fileNumber'] = str(fileNumber)

    if spec: 
        base = '%(path)s/PHOTOMETRY/%(cluster)s.1.spec' % params
        probs =  '%(path)s/PHOTOMETRY/all.spec.cat.bpz1.probs' % params
    else:
        base = '%(path)s/PHOTOMETRY/all_bpz1_%(fileNumber)s' % params
        probs =  '%(path)s/PHOTOMETRY/all_bpz1_%(fileNumber)s.probs' % params
    print probs
    probs_f = open(probs,'r').readlines()


    resid = line['BPZ_Z_B'] - line['BPZ_Z_S']

    ODDS = line['BPZ_ODDS']

    if 0.38 < line['BPZ_Z_B'] < 0.42: #abs(resid) > 0.15: # and ODDS > 0.95:        

        mask = p_cat.field('SeqNr') == SeqNr                                                                                                   
        temp = p_cat[mask]
        x = int(temp.field('Xpos')[0])
        y = 10000 - int(temp.field('Ypos')[0])
        
        resid = line['BPZ_Z_B'] - line['BPZ_Z_S']
        if resid > 0: 
            color='green'
            resid_str = ' <font color=' + color + '>+' + str(resid) + '</font> '
        else: 
            color='red'        
            resid_str = ' <font color=' + color + '>' + str(resid) + '</font> '
        
        t = ['BPZ_Z_B','BPZ_ODDS','BPZ_CHI-SQUARED']
        text += '<td>' + str(SeqNr) + ' ' + str(line['BPZ_Z_B']) + resid_str  + str(line['BPZ_ODDS']) + ' ' + str(line['BPZ_T_B']) + '</td>\n'
        
        print x,y
        side = 100 #x = temp.field('Xpos')[0]
                                                                                                                                               
        index = SeqNr
                                                                                                                                               
        outfile = os.environ['sne'] + '/photoz/' + cluster + '/' + str(index) + '.png' 
        plot_bpz_probs(index, probs_f, outfile)
                                                                                                                                               
        #file = 'Id%09.f.spec' % index
        #outfile = os.environ['sne'] + '/photoz/' + str(index) + '.png' 
        #print outfile
        #plot(file,outfile)
        
        text += '<td><img height=400px src=' + str(index)  + '.png></img></td>\n'
        text += '<td><img height=400px src=' + str(index)  + 'spec.png></img></td>\n'
        images = []

        file = '/nfs/slac/g/ki/ki04/pkelly/photoz/' + cluster + '/' +  str(SeqNr) + 'spec.png' #print 'SAVING', outdir + outimg
        command = 'python ' + os.environ['BPZPATH'] + '/plots/sedplot.py ' + base + ' ' + str(SeqNr) + ' ' + file
        print command
        os.system(command)
        try:
            p = im.crop([x-side,y-side,x+side,y+side])
            image = os.environ['sne'] + '/photoz/' + cluster + '/' + str(index) + '.jpg'  
            os.system('rm ' + image)
            p.save(image,'JPEG')
        except: print 'fail'
        text += '<td><img src=' + str(index)  + '.jpg></img></td>\n'
        text += '</tr>\n'
        #os.system('stiff ' + image_seg + ' -OUTFILE_NAME ' + image_seg.replace('fits','tif'))
        gals.append([line['BPZ_T_B'],text])
        page = open(os.environ['sne'] + '/photoz/' + cluster + '/index.html','w')
        t = '<head><link href="http://www.slac.stanford.edu/~pkelly/photoz/table.css" rel="stylesheet" type="text/css"></head>' 
        t += '<table><tr><td colspan=5 class="dark"><h1>' + cluster + '</h1></td></tr>\n'
        t += '<tr><td colspan=2><img height=400px src=RedshiftErrors.png></img></td>\n'
        t += '<td><img height=400px src=RedshiftScatter04.png></img></td>\n'
        t += '<td><img height=400px src=RedshiftScatter01.png></img></td></tr>\n'
        page.write(t)
        gals.sort()
        for gal in gals:
            page.write(gal[1])
        page.write('<table>\n')
        page.close()

        if len(gals) > 100:
            break



''' make SED plots '''
