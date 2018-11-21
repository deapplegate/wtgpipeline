import sys

from ppgplot import *

from Numeric import *

import astropy, astropy.io.fits as pyfits 

from config_bonn import cluster, arc


pickles = pyfits.open('Pickles.cat')
pickles = pickles[3].data

px = array(pickles.field('MAG_SUBARU_W-J-V') - pickles.field('MAG_SUBARU_W-C-RC'))
py = array(pickles.field('MAG_SUBARU_W-C-RC') - pickles.field('MAG_SUBARU_W-C-IC'))
print px,py


#p = pyfits.open('/tmp/' + cluster + 'output' + arc + '.cat')

p = pyfits.open('/a/wain023/g.ki.ki05/anja/SUBARU/MACS1347-11/PHOTOMETRY/MACS1347-11.slr.cat')
table = p[1].data
print table.field('MAG_AUTO_W-C-RC')
import numpy 
print  table.field('MAG_AUTO_W-J-B') - table.field('MAG_AUTO_W-J-V') #+ 0.1 
print  table.field('MAG_AUTO_W-C-RC') #- table.field('MAG_AUTO_W-C-IC')

if False:
    mask = table.field('MAG_AUTO_W-J-B')!=0
    table = table[mask]
    mask = table.field('MAG_AUTO_W-J-V')!=0
    table = table[mask]
    mask = table.field('MAG_AUTO_W-C-IC')!=0
    table = table[mask]
    mask = table.field('MAG_AUTO_W-C-RC')!=0
    table = table[mask]
    mask = table.field('MAG_AUTO_W-S-Z+')!=0
    table = table[mask]

mask = table.field('MAG_AUTO_W-J-V')!=0
table = table[mask]


pgbeg("/XWINDOW",1,1)

#pgbeg("colcol.ps/cps",1,1)
pgiden()


x = []
y = []
#for dict in output_list:

#x = table.field('umg')
#y = table.field('gmr')

#x = table.field('SEx_MAG_AUTO_W-J-B') - table.field('SEx_MAG_AUTO_W-J-V')
#y = table.field('SEx_MAG_AUTO_W-J-V') - table.field('SEx_MAG_AUTO_W-C-RC')
#x = table.field('SEx_Xposz')
#y = table.field('SEx_MAG_AUTO_z') - table.field('zmag')
#print table.field('SEx_MAG_AUTO')
#print table.field('Rmag')

#x = table.field('SEx_Ra') - table.field('Ra')
#x = table.field('SEx_X_WORLD_v') - table.field('SEx_ALPHA_J2000')
#y = table.field('Ra')


#x = (lists['Mag_W-C-RC']) - (lists['Mag_W-C-IC'])
#y = (lists['Mag_W-C-IC']) - (lists['Mag_W-S-Z+'])


#x = (lists['Mag_W-J-V']) - (lists['Mag_W-C-RC'])
#y = (lists['Mag_W-C-RC']) - (lists['Mag_W-C-IC'])


x = table.field('MAG_AUTO_W-J-B') - table.field('MAG_AUTO_W-J-V') #+ 0.1 
y = table.field('MAG_AUTO_W-C-RC') - table.field('MAG_AUTO_W-S-Z+')
print table.field('MAG_AUTO_W-J-B')

file = open('input_mags','w')

filters = ['W-J-V','W-C-RC','W-C-IC','W-S-Z+']
filters_sdss = ['g','r','i','z']


file.write('#' + str('ID').rjust(3) + ' ' + str('RA').rjust(9) + ' ' + str('Dec').rjust(8) + ' ' + str('type').rjust(4) + ' ' + str('tmixed').rjust(6) + ' '  )
for f in filters_sdss:
    file.write(str(f).rjust(6) + ' ')
    file.write(str(f+'_err').rjust(5) + ' ')
for f in filters_sdss:
    file.write(str(f+'_galext').rjust(8) + ' ')

file.write('\n')





for i in range(len(x)): 
    file.write(' ' + str(i).rjust(3) + ' ' + str(table.field('Ra_' + filters[0])[i])[0:9].rjust(9) + ' ' + str(table.field('Dec_' + filters[0])[i])[0:8].rjust(8) + ' ' + str(1).rjust(4) + ' ' + str(0).rjust(6) + ' ' )
    for f in filters:
        mag = table.field('MAG_AUTO_' + f)[i]
        if mag == 0: mag = '-' 
        file.write(str(mag)[0:6].rjust(6) + ' ')
        mag = table.field('MAGERR_AUTO_' + f)[i]
        if mag == 0: mag = '-' 
        file.write(str(mag)[0:5].rjust(5) + ' ')
    for f in filters:
        file.write(str('0.000')[0:8].rjust(8) + ' ')


    file.write('\n')
file.close()


#if -50 < x_val < 50 and -50 < y_val < 50:
#    x.append(x_val)		
#    y.append(y_val)

print x[0:10]
print y[0:10]
import copy 
plotx = copy.copy(x)
ploty = copy.copy(y)
x.sort()	
y.sort()
print plotx
print x[0], x[-1], y[0], y[-1]


#pgswin(x[10]-0.5,x[-10]+0.5,y[10]-0.5,y[-10]+0.5)


pgswin(x[10],x[-10],y[10],y[-10])

pgswin(-1,5,-1,2)
plotxsub = array(plotx)
plotysub = array(ploty)
#pylab.scatter(plotx,ploty)
pgpt(plotxsub,plotysub,5)
pgsci(3)
pgpt(px,py,3)
pgsci(1)
pglab('B-V','R-I','')
pgbox()
raw_input()
#print plotx, ploty

x = []
y = []
#for dict in output_list:
#if -50 < x_val < 50 and -50 < y_val < 50:
#    x.append(x_val)		
#    y.append(y_val)








#x = (table_merge.field('BmV'))
#y = (table_merge.field('VmR')) 

x = (lists['SDSS_W-J-B']) - (lists['SDSS_W-J-V'])
y = (lists['SDSS_W-C-RC']) - (lists['SDSS_W-C-IC'])

#x = (lists['SDSS_W-C-RC']) - (lists['SDSS_W-C-IC'])
#y = (lists['SDSS_W-C-IC']) - (lists['SDSS_W-S-Z+'])


#x = (lists['SDSS_W-J-V']) - (lists['SDSS_W-C-RC'])
#y = (lists['SDSS_W-C-RC']) - (lists['SDSS_W-C-IC'])

plotx = copy.copy(x)
ploty = copy.copy(y)
x.sort()	
y.sort()
#print plotx
#print x[0], x[-1], y[0], y[-1]
plotxsdss = array(plotx)
plotysdss = array(ploty)
#pylab.scatter(z,x)
#print plotx, ploty


pgsci(2)
pgpt(plotxsub,plotysub,1)


pgsci(3)
pgpt(plotxsdss,plotysdss,1)

x = table_stet.field('Rmag') - table_stet.field('Imag')
y = table_stet.field('Imag') - table_stet.field('Imag')
plotx = copy.copy(x)
ploty = copy.copy(y)
plotx = array(plotx)
ploty = array(ploty)

pgsci(4)
#pgpt(plotx,ploty,1)

pgend()






#input_photometric_data(table)
#import astropy, astropy.io.fits as pyfits
#table = hdulist["PSSC"].data
#cdefs=get_coldefs()
#pyfits.Column('RA',format='E',unit='Mag')
#
#cdecs.add_col(col)
#pyfits.BinTableHDU.from_columns(cdefs)
#
#fields = hdulist["PSSC"].fields
#
#mag = table.field('Mag')
#
#
#
#apply_calibrations()
#
#output_calibrations()
#
#
