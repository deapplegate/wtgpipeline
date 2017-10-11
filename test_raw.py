#!/usr/bin/env python
import astropy, astropy.io.fits as pyfits, sys, os, re, string
from config_bonn import cluster, tag, arc, filters

tables = {} 
colset = 0
cols = []
for filter in filters: 
    file = '//nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/' + filter + '/PHOTOMETRY/' + filter + arc + '.all' + tag + '.cat'
    os.system('ldacconv -b 1 -c R -i ' + file + ' -o /tmp/' + filter + '.all.conv.alpha')
    os.system('ldactoasc -i /tmp/' + filter + '.all.conv.alpha -b -s -k MAG_APER MAGERR_APER -t OBJECTS > /tmp/' + filter + 'aper')
    os.system('asctoldac -i /tmp/' + filter + 'aper -o /tmp/cat1 -t OBJECTS -c ./photconf/MAG_APER.conf')
    os.system('ldacjoinkey -i /tmp/' + filter + '.all.conv.alpha -p /tmp/cat1 -o /tmp/' + filter + '.all.conv  -k MAG_APER1 MAG_APER2 MAGERR_APER1 MAGERR_APER2')
    tables[filter] = pyfits.open('/tmp/' + filter + '.all.conv')
    if filter == filters[0]:
        tables['notag'] = pyfits.open('/tmp/' + filter + '.all.conv')

cols = [] 
for i in range(len(tables['notag'][1].columns)): 
    cols.append(tables['notag'][1].columns[i])

for filter in filters:
    for i in range(len(tables[filter][1].columns)): 
        tables[filter][1].columns[i].name = tables[filter][1].columns[i].name + '_' + filter    
        cols.append(tables[filter][1].columns[i])

print cols
print len(cols)
hdu = pyfits.PrimaryHDU()
hduIMHEAD = pyfits.BinTableHDU.from_columns(tables['notag'][2].columns)
hduOBJECTS = pyfits.BinTableHDU.from_columns(cols) 
hdulist = pyfits.HDUList([hdu])
hdulist.append(hduIMHEAD)
hdulist.append(hduOBJECTS)
hdulist[1].header['EXTNAME']='FIELDS'
hdulist[2].header['EXTNAME']='OBJECTS'
dir = '//nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/PHOTOMETRY/'
file = dir + 'all' + arc + '.cat'
os.system('mkdir ' + dir)
os.system('rm ' + file)
print file
hdulist.writeto(file)
print 'done'
import sys
sys.exit(0)
raw_input()
table=hdulist[0].data


from ppgplot import *

#pgbeg("A2219colors.ps/cps",1,1)
pgbeg("/XWINDOW",1,1)
pgiden()

from Numeric import *

x = []
y = []
#for dict in output_list:

#x = table.field('gmr')
#y = table.field('imz')
x = table.field('MAG_AUTO_W-J-V') - table.field('MAG_AUTO_W-C-RC')
y = table.field('MAG_AUTO_W-C-IC') - table.field('MAG_AUTO_W-S-Z+')
condition = []
for m in range(len(table.field('CLASS_STAR_W-C-RC'))):
    if table.field('CLASS_STAR_W-C-RC')[m] > 0.98 and table.field('FLAGS_W-C-RC')[m] == 0:
        condition.append(1)
    else: condition.append(0)
condition = array(condition)

x_plot = compress(condition,x)
y_plot = compress(condition,y)
#print len(x_plot), len(x)
#x = table.field('SEx_Xposz')
#y = table.field('SEx_MAG_AUTO_z') - table.field('zmag')
#print table.field('SEx_MAG_AUTO')
#print table.field('Rmag')

#x = table.field('SEx_Ra') - table.field('Ra')
#x = table.field('SEx_X_WORLD_v') - table.field('SEx_ALPHA_J2000')
#y = table.field('Ra')
#print x


#hdulist[2].columns[0].name = blah
#t = t1[1].columns + t2[1].columns
#hdu.writeto('newtable.fits')


#if -50 < x_val < 50 and -50 < y_val < 50:
#    x.append(x_val)        
#    y.append(y_val)

import copy 
plotx = copy.copy(x_plot)
ploty = copy.copy(y_plot)
x.sort()    
y.sort()
#print plotx
#print x[0], x[-1], y[0], y[-1]

#pgswin(x[10]-0.5,x[-10]+0.5,y[10]-0.5,y[-10]+0.5)

pgswin(-2,2,-2,2)
plotx = array(plotx)
ploty = array(ploty)
#pylab.scatter(z,x)
pglab('B-V','V-R','')
pgbox()
#print plotx, ploty
pgsci(2)
pgpt(plotx,ploty,1)
pgend()
