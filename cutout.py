import math, re, sys
import pylab  # matplotlib

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
    



import pyfits
import os
import os, sys, bashreader, commands
from utilities import *
from config_bonn import appendix, cluster, tag, arc, filters, filter_root, appendix_root

cluster = 'MACS1423+24'
path='/nfs/slac/g/ki/ki05/anja/SUBARU/%s/' % cluster

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
    seg_image = '/%(path)s/%(filter)s/PHOTOMETRY/coadd.apertures.fits' % params
    ims[filter] = pyfits.open(image)[0].data
    ims_seg[filter] = pyfits.open(seg_image)[0].data


os.system('stiff ' + reduce(lambda x,y:x + ' ' + y,images) + ' -OUTFILE_NAME ' + os.environ['sne'] + '/all.tif -BINNING 1 -GAMMA_FAC 1.6')
os.system('convert ' + os.environ['sne'] + '/all.tif ' + os.environ['sne'] + '/fix.tif')

import Image
im = Image.open(os.environ['sne'] + '/fix.tif')

catalog = '%(path)s/PHOTOMETRY/%(cluster)s.slr.cat' %params 

p_cat = pyfits.open(catalog)[1].data

outputcat = '%(path)s/PHOTOMETRY/%(cluster)s.1.spec.zs.tab' % params 
print outputcat
lph_cat = pyfits.open(outputcat)[1].data


page = open(os.environ['sne'] + '/photoz/index.html','w')

page.write('<table>\n')

gals = [] 

for line in lph_cat: #[75227,45311,53658, 52685, 64726]:
    print line
    text = ''

#for x,y,side,index in [[4800,4900,200,1],[5500,5500,100,2],[4500,5500,300,2]]:

    text += '<tr>\n'
    SeqNr = int(line['LPH_IDENT'])

    

    mask = p_cat.field('SeqNr') == SeqNr   
    temp = p_cat[mask]
    x = int(temp.field('Xpos')[0])
    y = 10000 - int(temp.field('Ypos')[0])


    resid = line['LPH_Z_BEST'] - line['LPH_ZSPEC']
    if resid > 0: color='green'
    else: color='red'        
    resid_str = ' <font color=' + color + '>' + str(resid) + '</font> '

    text += '<td>' + str(SeqNr) + ' ' + str(line['LPH_Z_BEST']) + resid_str  + str(line['LPH_MOD_BEST']) + ' ' + str(line['LPH_CHI_BEST']) + '</td>\n'

    print x,y
    side = 100 #x = temp.field('Xpos')[0]

    index = SeqNr
    
    file = 'Id%09.f.spec' % index
    outfile = os.environ['sne'] + '/photoz/' + str(index) + '.png' 
    print outfile
    plot(file,outfile)
    

    text += '<td><img height=400px src=' + str(index)  + '.png></img></td>\n'

    images = []
    p = im.crop([x-side,y-side,x+side,y+side])
    image = os.environ['sne'] + '/photoz/' + str(index) + '.jpg' 
    os.system('rm ' + image)
    p.save(image,'JPEG')

    text += '<td><img src=' + str(index)  + '.jpg></img></td>\n'

    text += '</tr>\n'

    #os.system('stiff ' + image_seg + ' -OUTFILE_NAME ' + image_seg.replace('fits','tif'))
    gals.append([line['LPH_MOD_BEST'],text])
    if len(gals) > 70:
        break

gals.sort()

for gal in gals:
    page.write(gal[1])



page.write('<table>\n')
page.close()

''' make SED plots '''
