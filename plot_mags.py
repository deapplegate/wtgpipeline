
import astropy, astropy.io.fits as pyfits, os
from config_bonn import cluster, tag, arc, magnitude, filters


path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':cluster}



#filters = ['W-C-RC','W-C-IC','W-S-Z+']



from ppgplot import *
from Numeric import *
from utilities import *


filters_info = make_filters_info(filters)
calib = get_calibrations(cluster,filters_info)










for filter in filters:


    pgbeg("/XTERM")
    pgiden()

    file = '/%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.each%(tag)s.cat' % {'path' : path, 'filter': filter, 'cluster': cluster, 'tag': tag}
    out_file = '/%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.each%(tag)s.ldac.cat' % {'path' : path, 'filter': filter, 'cluster': cluster, 'tag': tag}
    print file

    command = 'ldacconv -b 1 -c R -i ' + file + ' -o ' + out_file
    print command
    os.system(command)
    
    tempfile = '/tmp/' + cluster + 'outkey'

    dust_correct(out_file,tempfile)

    
    hdulist = pyfits.open(tempfile)
    table = hdulist["OBJECTS"].data

    magnitude = 'MAG_AUTO'

    model = convert_modelname_to_array(calib['model_name%' + filter])
    data,thresh = zp_dust_correct(model,calib,table,filter,magnitude,color='no')

    print 'hey'


    pgswin(0,10,20,30)


    y = array(0 + data)
    print len(table.field('FLUX_RADIUS')), len(y)
    x = array(0 + table.field('FLUX_RADIUS'))
    print x[0:100], y[0:100]
    pgpt(x,y,1)
    pgbox()


    low_rad = float(raw_input('low radius?'))

    #mask = table.field('FLUX_RADIUS') > value
    #masked = table[mask] 


    high_rad = float(raw_input('high radius?'))

    #mask = table.field('FLUX_RADIUS') < value
    #masked = table[mask] 

    magnitudes = []
    for i in range(len(data)):
        if low_rad < x[i] < high_rad:
            magnitudes.append(data[i])
        

    #masked = table

    pgeras()
    #data_uncal = masked.field(magnitude + '_' + filter)
    print data[0:20]
    #print data_uncal[0:20]
    #thresh = table.field('THRESHOLD')
    mags_array = array(magnitudes)
    #pgbox()
    pghist(len(mags_array),mags_array,23,30,40)    
    #print thresh[0]
    print filter                                     
    pgend()
    raw_input('next?')
