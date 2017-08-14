import os, sys
#  ldactoasc -b -s -i all.arc.cat -t OBJECTS -k MAG_APER_W-S-Z+ MAG_APER_W-C-RC MAG_APER_W-J-V MAG_AUTO ALPHA_J2000_W-C-RC ALPHA_J2000_W-J-V FLUX_APER_W-J-V

cluster = 'MACS0417-11'
appendix = '_all' 
path= os.environ['sne'] + '/arc' 
poly_file = path + '/arc_C1.reg'

children = []

for filter in ['B-WHT','U-WHT','W-C-IC','W-C-RC','W-J-V']:

    #child = os.fork()
    #if child:
    #    children.append(child)
    #else:
    if True:
        params = {'path':path, 'cluster':cluster, 'filter':filter, 'appendix':appendix}                       

        image_file = "%(path)s/2arcmin_%(filter)s.fits" % params

        final_image_file = "%(path)s/2arcmin_%(filter)s.masked.fits" % params

        weight_file = "%(path)s/2arcmin_%(filter)s.weightpat.fits" % params

        flag_file = "%(path)s/2arcmin_%(filter)s.flag.fits" % params

        input_flag_file = "%(path)s/flag.fits" % params

        cf = open('config_file_' + filter,'w')   
        cf.write('WEIGHT_NAMES ""\n')
        cf.write("WEIGHT_MIN -99999\n")   
        cf.write("WEIGHT_MAX 99999\n")
        cf.write("WEIGHT_OUTFLAGS 0\n")
            
                                                                                                              
        cf.write("POLY_NAMES " + poly_file + "\n")

        cf.write("POLY_OUTFLAGS  1\n")
        cf.write("POLY_OUTWEIGHTS 0\n")
        cf.write('FLAG_NAMES ' + input_flag_file + '\n') #" + flag_file + "\n")
        cf.write("FLAG_MASKS 0x07\n")
        cf.write("FLAG_WMASKS 0x0\n")
        cf.write("FLAG_OUTFLAGS 1,2,4\n")
        
        cf.write("OUTWEIGHT_NAME " + weight_file + "\n")
        cf.write("OUTFLAG_NAME " + flag_file + "\n")


            
        cf.close()


        command = "ic '%1 0 * ' " + image_file + " > " + input_flag_file
        print command
        #os.system(command)
           
        command = "ww_theli -c config_file_" + filter             
        print command 
        os.system(command)            
        command = "ic '%1 1 - -1 * %2 *' " + image_file + " " + weight_file + " > " + final_image_file 
        print command

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
                          

        #command = 'rm ' + image_small + '; makesubimage -500 -500 1000 1000 -c < ' + image_file + ' > ' + image_small 
        #print command 
        #os.system(command)

        #command = 'rm ' + final_weight_small + '; makesubimage -500 -500 1000 1000 -c < ' + final_weight_file + ' > ' + final_weight_small 
        #print command 
        #os.system(command)


        #command = 'rm ' + orig_weight_small + '; makesubimage -500 -500 1000 1000 -c < ' + weight_file + ' > ' + orig_weight_small 
        #print command 
        #os.system(command)

        #command = "rm " + background_image_file + ";ic '%1 %2 -' " + image_small + " " + background_file_arc + " > " +  background_image_file
        #print command
        #os.system(command)

        #command = "mv $subdir/" + cluster + "/" + filter + "/PHOTOMETRY/coadd.small.fits $subdir/" + cluster + "/" + filter + "/PHOTOMETRY/coadd_small.fits"
        #print command
        #os.system(command)
        

        #command = "create_skysub_final.sh $subdir/" + cluster + "/" + filter + "/ PHOTOMETRY small .sub TWOPASS"
        #print command
        #os.system(command)

        #raw_input()
        #os.system('rm /tmp/maskfile')
        #command = "ic '%1 1 - -1 *'  " + out_weight_file + " > /tmp/maskfile"
        #print command
        #os.system(command)
        #os.system('rm ' + final_weight_file)
        #command = "ic '%1 %2 *' /tmp/maskfile "  + weight_file + " > " + final_weight_file
        sys.exit(0)

#for child in children:
#    os.waitpid(child,0)

print 'DONE!!!!'
