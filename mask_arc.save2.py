import os, sys
#  ldactoasc -b -s -i all.arc.cat -t OBJECTS -k MAG_APER_W-S-Z+ MAG_APER_W-C-RC MAG_APER_W-J-V MAG_AUTO ALPHA_J2000_W-C-RC ALPHA_J2000_W-J-V FLUX_APER_W-J-V

cluster = 'MACS2243-09'
appendix = '_all' 
path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':cluster}
poly_file = 'M2243small.reg'

children = []

for filter in ['B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']:

    child = os.fork()
    if child:
        children.append(child)
    else:
        
        params = {'path':path, 'cluster':cluster, 'filter':filter, 'appendix':appendix}                       
        out_flag_file = "/%(path)s/%(filter)s/PHOTOMETRY/coadd.flag.arc.fits" % params
        out_weight_file = "/%(path)s/%(filter)s/PHOTOMETRY/coadd.weight.arc.fits" % params
                                                                                                              
        image_file = "/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits" % params
        image_small = "/%(path)s/%(filter)s/PHOTOMETRY/coadd.small.fits" % params
        final_image_file = "/%(path)s/%(filter)s/PHOTOMETRY/coadd.arc.fits" % params
        background_file = "/%(path)s/%(filter)s/PHOTOMETRY/coadd.background.fits" % params
        background_file_arc = "/%(path)s/%(filter)s/PHOTOMETRY/coadd.arc.background.fits" % params
        background_image_file = "/%(path)s/%(filter)s/PHOTOMETRY/coadd.backsub.fits" % params
        weight_file = "/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits" % params

        orig_weight_small = "/%(path)s/%(filter)s/PHOTOMETRY/coadd.weight.arc.orig.fits" % params
        final_weight_file = "/%(path)s/%(filter)s/PHOTOMETRY/coadd.weight.arc.final.fits" % params
        final_weight_small = "/%(path)s/%(filter)s/PHOTOMETRY/coadd.weight.arc.small.fits" % params
        flag_file = "/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits" % params

        cf = open('config_file_' + filter,'w')   
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
        
        cf.write("OUTWEIGHT_NAME " + out_weight_file + "\n")
        cf.write("OUTFLAG_NAME " + out_flag_file + "\n")
            
        cf.close()
           
             
        #os.system("ww_theli -c config_file_" + filter)            
        #command = "ic '%1 1 - -1 * %2 *' " + out_weight_file + " " + weight_file + " > " + final_weight_file 

        #command = "ic '%1 1 - -1 * %2 *' " + out_weight_file + " " + weight_file + " > " + final_weight_file 
        #command = "ic '%1 1 - -1 * ' " + out_weight_file + " " + weight_file + " > " + final_weight_file 
        #print command
        #os.system(command)
                                                                                                              
        #command = "ic '%1 %2 -' " + image_file + " " + background_file + " > " + background_image_file 
        #print command
        #os.system(command)

        #command = "ic '%1 1 - -1 * %2 *' " + out_weight_file + " " + background_image_file + " > " + final_image_file 
        #print command
        #os.system(command)
                          

        command = 'rm ' + image_small + '; makesubimage -500 -500 1000 1000 -c < ' + image_file + ' > ' + image_small 
        print command 
        #os.system(command)

        command = 'rm ' + final_weight_small + '; makesubimage -500 -500 1000 1000 -c < ' + final_weight_file + ' > ' + final_weight_small 
        print command 
        #os.system(command)


        command = 'rm ' + orig_weight_small + '; makesubimage -500 -500 1000 1000 -c < ' + weight_file + ' > ' + orig_weight_small 
        print command 
        #os.system(command)

        command = "rm " + background_image_file + ";ic '%1 %2 -' " + image_small + " " + background_file_arc + " > " +  background_image_file
        print command
        #os.system(command)

        command = "mv $subdir/" + cluster + "/" + filter + "/PHOTOMETRY/coadd.small.fits $subdir/" + cluster + "/" + filter + "/PHOTOMETRY/coadd_small.fits"
        print command
        os.system(command)
        

        command = "create_skysub_final.sh $subdir/" + cluster + "/" + filter + "/ PHOTOMETRY small .sub TWOPASS"
        print command
        os.system(command)

                                                                                                              
                                                                                                              
                                                                                                              
        #raw_input()
        #os.system('rm /tmp/maskfile')
        #command = "ic '%1 1 - -1 *'  " + out_weight_file + " > /tmp/maskfile"
        #print command
        #os.system(command)
        #os.system('rm ' + final_weight_file)
        #command = "ic '%1 %2 *' /tmp/maskfile "  + weight_file + " > " + final_weight_file
        sys.exit(0)

for child in children:
    os.waitpid(child,0)

print 'DONE!!!!'
