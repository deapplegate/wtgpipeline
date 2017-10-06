def plot_histo(mags):
    from ppgplot import *
    import Numeric
    pgbeg("/XWINDOW",1,1)
    pgiden()

    for filter in mags.keys():
        print len(mags[filter])
        print mags[filter][0:20]
        pgpanl(1,1)
        mags_array = Numeric.array(mags[filter])
        pghist(len(mags_array),mags_array,23,30,20,1)
        print filter, 'PLOTTING'
    pgend()
    raw_input()

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
#
import sys, astropy.io.fits as pyfits, os
from utilities import *
from config_bonn import cluster, tag, arc, magnitude, filters
import Numeric
#cluster = 'MACS2243-09' #sys.argv[2]
#cluster = 'MACS0911+17' #sys.argv[2]
#filters = ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+'] #sys.argv[3:]
#magnitude = 'MAG_APER2'
#arc = '' #.arc'

ThreeSecond = 0
dust = 1

if ThreeSecond:
    dust = 0
    table_name = '/tmp/out.cat'
    filters_info = make_filters_info(filters)
    calib = get_calibrations_threesecond(cluster,filters_info)
elif arc == '':
    table_name = '/nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/PHOTOMETRY/all' + arc + '.cat'
    filters_info = make_filters_info(filters)
    calib = get_calibrations(cluster,filters_info)
else:
    table_name = '/tmp/' + cluster + 'special.cat'#'M2243_faint.cat' #
    magnitude = 'MAG_SPEC'
    filters_info = make_filters_info(filters)
    print filters_info
    raw_input()
    calib = get_calibrations(cluster,filters_info)
    print calib
    raw_input()

print calib

tempfile = '/tmp/' + cluster + 'outkey'
if dust:
    dust_correct(table_name,tempfile)
    hdulist = pyfits.open(tempfile)
else: 
    hdulist = pyfits.open(table_name)
table = hdulist["OBJECTS"].data

cols = []
for column in hdulist["OBJECTS"].columns:
	#cols.append(column)
    cols.append(pyfits.Column(name=column.name, format=column.format,array=Numeric.array(0 + hdulist["OBJECTS"].data.field(column.name))))


#open input table
#hdulist = pyfits.open('/tmp/outkey')
#table = hdulist["OBJECTS"].data
#mask = temptable.field('CLASS_STAR_W-C-IC') > 0.8
#temptable2 = temptable[mask]
#mask = temptable2.field('MAGERR_AUTO_W-C-RC') < 0.01 
#temptable3 = temptable2[mask]
#mask = temptable3.field('Flag_W-C-RC') == 0 
#table = temptable3[mask]

#open Stetson table
#hdulist = pyfits.open('/nfs/slac/g/ki/ki05/anja/Stetson/Stetson_std_2.0.cat')
#table_stet = hdulist["STDTAB"].data

''' why was there an all_merge.cat here???'''
print table_name
raw_input()
hdulist = pyfits.open(table_name) #'/nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/PHOTOMETRY/cat/all.cat')
table_merge = hdulist["OBJECTS"].data

#hdulist = pyfits.open(table_name)
#table = hdulist["PSSC"].data

#print hdulist["PSSC"].columns

from copy import copy
lists = {} 
mags = {}
for filter in filters:
    model = convert_modelname_to_array(calib['model_name%' + filter])
    print model
    #fixed = convert_modelname_to_array(calib['fixed_name%' + filter])
    if dust:
        data,thresh = zp_dust_correct(model,calib,table,filter,magnitude)
        lists['Mag_' + filter] = copy(data)
        lists['Thresh_' + filter] = copy(thresh)
        cols.append(pyfits.Column(name='Mag_'+filter, format='E',array=data))
        cols.append(pyfits.Column(name='Thresh_'+filter, format='E',array=thresh))
    else:
        data= zp_correct(model,calib,table,filter,magnitude)
        lists['ThreeSecond_' + filter] = copy(data)
        cols.append(pyfits.Column(name='Mag_'+filter, format='E',array=data))
    mags[filter]=data

#plot_histo(mags)
#raw_input()
import sys

#open output table
hdu = pyfits.PrimaryHDU()
hdulist = pyfits.HDUList([hdu])

print cols
tbhu = pyfits.BinTableHDU.from_columns(cols)
hdulist.append(tbhu)
hdulist[1].header['EXTNAME']='STDTAB'
os.system('rm /tmp/' + cluster + 'output' + arc + '.cat')
hdulist.writeto('/tmp/' + cluster + 'output' + arc + '.cat')

sys.exit()
