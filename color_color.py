




import sys

from ppgplot import *

pgbeg("/XWINDOW",1,1)

#pgbeg("colcol.ps/cps",1,1)
pgiden()

from Numeric import *

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
print x


#x = (lists['Mag_W-C-RC']) - (lists['Mag_W-C-IC'])
#y = (lists['Mag_W-C-IC']) - (lists['Mag_W-S-Z+'])


#x = (lists['Mag_W-J-V']) - (lists['Mag_W-C-RC'])
#y = (lists['Mag_W-C-RC']) - (lists['Mag_W-C-IC'])


x = (lists['Mag_W-J-B']) - (lists['Mag_W-J-V'])
y = (lists['Mag_W-J-V']) - (lists['Mag_W-C-RC'])


#if -50 < x_val < 50 and -50 < y_val < 50:
#    x.append(x_val)		
#    y.append(y_val)

import copy 
plotx = copy.copy(x)
ploty = copy.copy(y)
x.sort()	
y.sort()
#print plotx
#print x[0], x[-1], y[0], y[-1]

#pgswin(x[10]-0.5,x[-10]+0.5,y[10]-0.5,y[-10]+0.5)

pgswin(x[10],x[-10],y[10],y[-10])

pgswin(-1,2,-1,2)
plotxsub = array(plotx)
plotysub = array(ploty)
#pylab.scatter(z,x)
pglab('V-R','R-I','')
pgbox()
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
y = (lists['SDSS_W-J-V']) - (lists['SDSS_W-C-RC'])

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
#import pyfits
#table = hdulist["PSSC"].data
#cdefs=get_coldefs()
#pyfits.Column('RA',format='E',unit='Mag')
#
#cdecs.add_col(col)
#pyfits.new_table(cdefs)
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
