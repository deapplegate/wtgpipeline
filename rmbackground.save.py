def run(command):
        print command
        os.system(command)

def select_background(flag_file,poly_file,out_flag_file):
        cf = open('config_file','w')   
        cf.write('WEIGHT_NAMES ""\n')
        cf.write("WEIGHT_MIN -99999\n")   
        cf.write("WEIGHT_MAX 99999\n")
        cf.write("WEIGHT_OUTFLAGS 0\n")
        cf.write('FLAG_NAMES ""\n')
        cf.write("POLY_NAMES " + poly_file + "\n")
        cf.write("POLY_OUTFLAGS  1\n")
        #cf.write("POLY_OUTWEIGHTS 1.0\n")
        cf.write("FLAG_NAMES " + flag_file + "\n")
        cf.write("FLAG_MASKS 0x07\n")
        cf.write("FLAG_WMASKS 0x0\n")
        cf.write("FLAG_OUTFLAGS 1,2,4\n")
        cf.write("OUTWEIGHT_NAME " + out_flag_file + "\n")
        cf.write("OUTFLAG_NAME /tmp/trash\n")
        cf.close()
        run("ww_theli -c config_file")            


def calc_stats(image_small, flag_small, poly_file):
        out_flag_file = '/tmp/flag_file.fits'
        select_background(flag_small,poly_file,out_flag_file)
        
        import pyfits 
        
        rawim = pyfits.open(out_flag_file)
        flag = -1 * (rawim[0].data - 1)
        
        rawim = pyfits.open(image_small)
        image = rawim[0].data
        
        bgpix = flag * (image + 1000)
        
        import numpy
        
        nonzerobg = numpy.extract((bgpix!=0),bgpix) - 1000
        mdn = numpy.median(nonzerobg)
        std = nonzerobg.std()
        mean = numpy.mean(nonzerobg) 
        sum = numpy.sum(nonzerobg)
        
        print "mdn", mdn, "std", std, "mean", mean, "sum", sum
        
        sum_flag = numpy.sum(flag)
        
        print "number of pixels", sum_flag

        return {'median': mdn, 'std':std, 'mean': mean, 'pix': sum_flag, 'sum':sum}



import os, utilities
cluster = 'FIELDB'
appendix = '_all' 
path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':cluster}
obj_poly = 'M2243_obj_bright.reg' #'M2243_obj_W-J-V.reg'
bg_poly = 'M2243_bg_bright.reg' #'M2243_W-J-V.reg'
ALPHA_J2000 = 340.82489
DELTA_J2000 = -9.59580

filters = ['B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']

obj_meas = {} 
for filter in filters:
    
    params = {'path':path, 'cluster':cluster, 'filter':filter, 'appendix':appendix}                       
    
    image_file = "/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits" % params
    weight_file = "/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits" % params
    flag_file = "/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits" % params
    
    ''' make small versions of image + weight files '''
    image_small = "/%(path)s/%(filter)s/PHOTOMETRY/coadd_small.fits" % params
    #run('rm ' + image_small + '; makesubimage -500 -500 1000 1000 -c < ' + image_file + ' > ' + image_small)
    
    weight_small = "/%(path)s/%(filter)s/PHOTOMETRY/coadd_small.weight.fits" % params
    #run('rm ' + weight_small + '; makesubimage -500 -500 1000 1000 -c < ' + weight_file + ' > ' + weight_small)
    
    flag_small = "/%(path)s/%(filter)s/PHOTOMETRY/coadd_small.flag.fits" % params
    #run('rm ' + flag_small + '; makesubimage -500 -500 1000 1000 -c < ' + flag_file + ' > ' + flag_small)
    
    obj = calc_stats(image_small,flag_small,obj_poly)
    bg = calc_stats(image_small,flag_small,bg_poly)
    
    obj['flux'] = obj['sum'] - bg['median']*obj['pix']
    
    GAIN, PIXSCALE = utilities.get_header_info(image_small) 
    GAIN = float(GAIN)
    PIXSCALE = float(PIXSCALE)
    
    import math
    obj['err'] = 1.0857 * math.sqrt(obj['pix'] * bg['std']**2. + obj['flux']/GAIN) / obj['flux'] 
    
    import math
    
    obj['mag'] = 27.0 - 2.5*math.log10(obj['flux'])
    
    print 'object flux', obj['flux'], 'mag', obj['mag'], 'error', obj['err'], 'GAIN', GAIN
    
    #filters_info = utilities.make_filters_info(['W-J-V'])
    
    #get table photometric information
    #calib = utilities.get_calibrations(cluster,filters_info)
    #print calib
    
    #model = utilities.convert_modelname_to_array(calib['model_name%' + filter])
    
    #gallat, gallong = convert_to_galactic(ra,dec)
    
    #os.system('dust_getval interp=y ipath=/nfs/slac/g/ki/ki04/pkelly/DUST/maps infile=' + ebvgal + ' outfile=' + tempmap + ' noloop=y') 
    #print 'dust done'
    #command = "gawk '{print $3}' " + tempmap + " > " + templines 
    #print command
    #os.system(command)
    
    #data = utilities.zp_dust_correct(model,calib,obj['mag'],filter,"")
    #print data

    obj_meas[filter] = {}
    obj_meas[filter]['obj'] = obj
    obj_meas[filter]['bg'] = obj

tempfile = '/tmp/ofile'
ofile = open(tempfile,'w')
ofile.write("1 " + str(ALPHA_J2000) + " " + str(DELTA_J2000) + " ")
for filter in filters:
    meas = obj_meas[filter]['obj']
    ofile.write(str(meas['mag']) + " " + str(meas['err']) + " ")
ofile.write('\n')
ofile.close()


tempconf = '/tmp/tmpconf.conf'  
specialcat = '/tmp/special.cat'
tf = open(tempconf,'w')
tf.write(\
        'COL_NAME = SeqNr\nCOL_TTYPE = LONG\nCOL_HTYPE = INT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n'\
        + 'COL_NAME = ALPHA_J2000\nCOL_TTYPE = DOUBLE\nCOL_HTYPE = FLOAT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n'\
        + 'COL_NAME = DELTA_J2000\nCOL_TTYPE = DOUBLE\nCOL_HTYPE = FLOAT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n')

for filter in filters:
    tf.write(\
            'COL_NAME = MAG_SPEC_' + filter + '\nCOL_TTYPE = FLOAT\nCOL_HTYPE = FLOAT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n'\
            + 'COL_NAME = MAGERR_SPEC_' + filter + '\nCOL_TTYPE = FLOAT\nCOL_HTYPE = FLOAT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n')

        #+ 'COL_NAME = OBJECT\nCOL_TTYPE = STRING\nCOL_HTYPE = STRING\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 128\n'\
tf.close() 

run('asctoldac -i ' + tempfile + ' -o ' + specialcat + ' -c ' + tempconf + ' -t OBJECTS' )

