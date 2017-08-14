import os

cluster = 'MACS2243-09'
appendix = '_all' 
path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':cluster}
poly_file = 'MACS2243mask2.reg'

for filter in ['B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']:

    params = {'path':path, 'cluster':cluster, 'filter':filter, 'appendix':appendix} 
    out_flag_file = "/%(path)s/%(filter)s/PHOTOMETRY/coadd.flag.arc.fits" % params
    out_weight_file = "/%(path)s/%(filter)s/PHOTOMETRY/coadd.weight.arc.fits" % params
    weight_file = "/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits" % params

    cf = open('config_file_' + filter,'w')   
    cf.write("WEIGHT_NAMES " + weight_file + "\n")
    cf.write("WEIGHT_MIN -99999\n")   
    cf.write("WEIGHT_MAX 99999\n")
    cf.write("WEIGHT_OUTFLAGS 0\n")
        
    cf.write('FLAG_NAMES ""\n')

    cf.write("POLY_NAMES " + poly_file + "\n")
    cf.write("POLY_OUTFLAGS  1\n")
    #cf.write("POLY_OUTWEIGHTS 0.0\n")
    cf.write("FLAG_MASKS 0x07\n")
    cf.write("FLAG_WMASKS 0x0\n")
    cf.write("FLAG_OUTFLAGS 1,2,4\n")
    
    cf.write("OUTWEIGHT_NAME " + out_weight_file + "\n")
    cf.write("OUTFLAG_NAME " + out_flag_file + "\n")
        
    cf.close()
       
         
    os.system("ww_theli -c config_file_" + filter)            
