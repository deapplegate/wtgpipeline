
def output_calibrations():
    asconf = '/tmp/ascout.conf'
    asc = open(asconf,'w')
    for filter in colors:
        asc.write('#\nCOL_NAME = ' + mag_name + '_color_' + filter + '\nCOL_TTYPE= FLOAT\nCOL_HTYPE= FLOAT\nCOL_COMM= ""\nCOL_UNIT= ""\nCOL_DEPTH= 1\n')
            #asc.write('#\nCOL_NAME = ' + mag_name_err + '_color_' + filter + '\nCOL_TTYPE= FLOAT\nCOL_HTYPE= FLOAT\nCOL_COMM= ""\nCOL_UNIT= ""\nCOL_DEPTH= 1\n')
        
        asc.write('#\nCOL_NAME = PhotSeqNr\nCOL_TTYPE= LONG\nCOL_HTYPE= INT\nCOL_COMM= ""\nCOL_UNIT= ""\nCOL_DEPTH= 1\n')
        asc.close()
        
        command = "asctoldac -i " + outrename1 + " -o " + outrename2 + " -t OBJECTS -c " + asconf
        print command
        os.system(command)
        
        input = reduce(lambda x,y: x + " " + y,[mag_name + '_color_' + filter for filter in colors] + ['PhotSeqNr'])
        
        command = "ldacjoinkey -t OBJECTS -i " + inputtable + " -p " + outrename2 + " -o " + outputtable + " -k " + input
        print command
        os.system(command)
    return

import sys, astropy, astropy.io.fits as pyfits, os
from utilities import *

table_name = sys.argv[1]
cluster = 'MACS0911+17' #sys.argv[2]
filters = ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+'] #sys.argv[3:]
magnitude = 'MAG_APER2'

# filter extinction information
filters_dat = [['W-J-B','b',4.031,0],['W-J-V','v',3.128,1],['W-C-RC','r',2.548,2],['W-C-IC','i',1.867,3],['W-S-Z+','z',1.481,4]]

filters_info = []
for filter in filters:
	for filter_dat in filters_dat:
		if filter_dat[0] == filter:
			filters_info.append(filter_dat)


#get table photometric information
calib = get_calibrations(cluster)
print calib

#open input table
hdulist = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/PHOTOMETRY/cat/all.cat')
temptable = hdulist["OBJECTS"].data
mask = temptable.field('CLASS_STAR_W-C-IC') > 0.8
temptable2 = temptable[mask]
mask = temptable2.field('MAGERR_AUTO_W-C-RC') < 0.01 
temptable3 = temptable2[mask]
mask = temptable3.field('Flag_W-C-RC') == 0 
table = temptable3[mask]

#open Stetson table
hdulist = pyfits.open('/nfs/slac/g/ki/ki02/xoc/anja/Stetson/Stetson_std_2.0.cat')
table_stet = hdulist["STDTAB"].data

hdulist = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/PHOTOMETRY/cat/all_merg.cat')
table_merge = hdulist["PSSC"].data

#print hdulist["PSSC"].columns

from copy import copy
lists = {} 
cols = []
for filter in filters:
    model = convert_modelname_to_array(calib['model_name%' + filter])
    print model
    fixed = convert_modelname_to_array(calib['fixed_name%' + filter])
    data = zp_correct(model,calib,table,filter,magnitude)
    lists['Mag_' + filter] = copy(data)
    cols.append(pyfits.Column(name='Mag_'+filter, format='E',array=data))

for filter in filters:
    model = convert_modelname_to_array(calib['model_name%' + filter])
    print model
    fixed = convert_modelname_to_array(calib['fixed_name%' + filter])
    data = apply_color_term(model,calib,table_merge,filter,magnitude)
    lists['SDSS_' + filter] = copy(data)
    cols.append(pyfits.Column(name='SDSS_'+filter, format='E',array=data))

#open output table
hdu = pyfits.PrimaryHDU()
hdulist = pyfits.HDUList([hdu])

print cols
tbhu = pyfits.BinTableHDU.from_columns(cols)
hdulist.append(tbhu)
hdulist[1].header['EXTNAME']='STDTAB'
os.system('rm output.cat')
hdulist.writeto('output.cat')

from ppgplot import *

#pgbeg("/XWINDOW",1,1)

pgbeg("colcol.ps/cps",1,1)
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


x = (lists['Mag_W-J-V']) - (lists['Mag_W-C-RC'])
y = (lists['Mag_W-C-RC']) - (lists['Mag_W-C-IC'])


#x = (lists['Mag_W-J-B']) - (lists['Mag_W-J-V'])
#y = (lists['Mag_W-J-V']) - (lists['Mag_W-C-RC'])


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

#x = (lists['SDSS_W-J-B']) - (lists['SDSS_W-J-V'])
#y = (lists['SDSS_W-J-V']) - (lists['SDSS_W-C-RC'])

#x = (lists['SDSS_W-C-RC']) - (lists['SDSS_W-C-IC'])
#y = (lists['SDSS_W-C-IC']) - (lists['SDSS_W-S-Z+'])


x = (lists['SDSS_W-J-V']) - (lists['SDSS_W-C-RC'])
y = (lists['SDSS_W-C-RC']) - (lists['SDSS_W-C-IC'])

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
pgpt(plotxsub,plotysub,3)


pgsci(3)
pgpt(plotxsdss,plotysdss,3)

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
