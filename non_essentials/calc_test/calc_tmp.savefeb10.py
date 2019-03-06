def gather_exposures(filter, cluster):

    search_params = {'path':path, 'cluster':cluster, 'filter':filter, 'PHOTCONF':PHOTCONF, 'DATACONF':os.environ['DATACONF'], 'TEMPDIR':TEMPDIR,'fwhm':1.00} 
    searchstr = "/%(path)s/%(filter)s*/SCIENCE/*fits" % search_params
    print searchstr
    files = glob(searchstr)
    files.sort()
    print files
    exposures = {} 
    # first 30 files
    print files[0:30]
    for file in files: #[0:30]:
        if string.find(file,'wcs') == -1 and string.find(file,'.sub.fits') == -1:
            res = re.split('_',re.split('/',file)[-1])                                        
            print res
            if not exposures.has_key(res[0]): exposures[res[0]] = {}
            if not exposures[res[0]].has_key('images'): exposures[res[0]]['images'] = [] 
            if not exposures[res[0]].has_key('keywords'): exposures[res[0]]['keywords'] = {} 
            exposures[res[0]]['images'].append(file) # res[0] is the root of the image name
            print 'hey', file
            reload(utilities)
            if not exposures[res[0]]['keywords'].has_key('ROTATION'): #if exposure does not have keywords yet, then get them
                exposures[res[0]]['keywords']['filter'] = filter
                res2 = re.split('/',file)   
                for r in res2:
                    if string.find(r,filter) != -1:
                        print r
                        exposures[res[0]]['keywords']['date'] = r.replace(filter + '_','')
                        exposures[res[0]]['keywords']['fil_directory'] = r 
                        search_params['fil_directory'] = r
                kws = utilities.get_header_kw(file,['ROTATION','OBJECT','GABODSID']) # return KEY/NA if not SUBARU 
                for kw in kws.keys(): 
                    exposures[res[0]]['keywords'][kw] = kws[kw]
    exposures_zero = {} 
    exposures_one = {} 
    print '$$$$$'
    print 'separating into different camera rotations'
    for exposure in exposures.keys(): 
        print exposure,exposures[exposure]['keywords']['ROTATION']
        if int(exposures[exposure]['keywords']['ROTATION']) == 1:
            exposures_one[exposure] = exposures[exposure]
        if int(exposures[exposure]['keywords']['ROTATION']) == 0:
            exposures_zero[exposure] = exposures[exposure]
    return exposures


class image:
    def __init__(self,exposure):
        self.exposure = exposure
       
        self.gain = float(self.exposure['keywords']['PIXSCALE'])
        self.pixscale = float(self.exposure['keywords']['PIXSCALE'])

    def get_root(self,image):


        
    def find_seeing(self):     
        ''' quick run through for seeing '''
        children = []
        for image in exposure['images']:                                                                                 
            child = os.fork()
            if child:
                children.append(child)
            else:
                params = copy(search_params)     
                params['GAIN'] = self.gain 
                params['PIXSCALE'] = self.pixscale 
                
                ROOT = re.split('\.',re.split('\/',image)[-1])[0]
                params['ROOT'] = ROOT
                NUM = re.split('O',re.split('\_',ROOT)[1])[0]
                params['NUM'] = NUM
                print ROOT
                                                                                                                         
                weightim = "/%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits" % params
                #flagim = "/%(path)s/%(fil_directory)s/WEIGHTS/globalflag_%(NUM)s.fits" % params
                #finalflagim = TEMPDIR + "flag_%(ROOT)s.fits" % params 
                params['finalflagim'] = weightim
                #os.system('rm ' + finalflagim)
                #command = "ic -p 16 '1 %2 %1 0 == ?' " + weightim + " " + flagim + " > " + finalflagim
                #utilities.run(command)
                #raw_input()
                                                                                                                         
                
                command = "sex /%(path)s/%(fil_directory)s/SCIENCE/%(ROOT)s.fits -c %(PHOTCONF)s/singleastrom.conf.sex \
                            -FLAG_IMAGE ''\
                            -FLAG_TYPE MAX\
                            -CATALOG_NAME %(TEMPDIR)s/seeing_%(ROOT)s.cat \
                            -FILTER_NAME %(PHOTCONF)s/default.conv\
                            -CATALOG_TYPE 'ASCII' \
                            -DETECT_MINAREA 8 -DETECT_THRESH 8.\
                            -ANALYSIS_THRESH 8 \
                            -WEIGHT_IMAGE /%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits\
                            -WEIGHT_TYPE MAP_WEIGHT\
                            -PARAMETERS_NAME %(PHOTCONF)s/singleastrom.ascii.flag.sex" %  params 
                                                                                                                         
                print command
                os.system(command)
                sys.exit(0)
        for child in children:  
            os.waitpid(child,0)
                                                                                                                              
                                                                                                                              
        command = 'cat ' + TEMPDIR + 'seeing_' +  kw + '*cat > ' + TEMPDIR + 'paste_seeing_' + kw + '.cat' 
        utilities.run(command)
                                                                                                                              
        file_seeing = TEMPDIR + '/paste_seeing_' + kw + '.cat'
        PIXSCALE = float(exposure['keywords']['PIXSCALE'])
        reload(utilities)
        print file_seeing, kw, PIXSCALE, exposure['keywords']['PIXSCALE'] 
        fwhm = utilities.calc_seeing(file_seeing,10,PIXSCALE)
    
    
    def sextract(self,exposures):
        #from config_bonn import appendix, cluster, tag, arc, filter_root
        import utilities
        import os, re, bashreader, sys, string
        from glob import glob
        from copy import copy
    
        dict = bashreader.parseFile('progs.ini')
        for key in dict.keys():
            os.environ[key] = str(dict[key])
    
    
        TEMPDIR = '/tmp/'
        PHOTCONF = './photconf/'
    
        path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':cluster}
    
        
        print exposures.keys()
        print exposures_zero.keys()
        print exposures_one.keys()
                    
        print 'hey2!!!!!!'
        print exposures
        first = exposures[exposures.keys()[0]]
        first['images'] = first['images']
        exposures = {exposures.keys()[0]: first}
    
    
    
    
        #exp_tmp = {}
        #for exposure in exposures.keys()[2:4]:
        #    exp_tmp[exposure] = exposures[exposure]
        #exposures = exp_tmp
    
    
        #exposures = {exposures.keys()[0]: exposures[exposures.keys()[0:4]]}
        print exposures
    
    
        print 'stop1'
        #temporary method
    
        measure_fwhm = 1
    
        for kw in exposures.keys(): # now go through exposure by exposure
            exposure = exposures[kw]
            print kw, exposure['images']
            print exposure['images']
            
            ''' get the CRPIX values '''
            start = 1
            for image in exposure['images']:
                print image                                                 
                res = re.split('\_\d+',re.split('\/',image)[-1])
                #print res
                imroot = "/%(path)s/%(fil_directory)s/SCIENCE/" % search_params
                im = imroot + res[0] + '_1' + res[1] 
                #print im
                crpix = utilities.get_header_kw(image,['CRPIX1','CRPIX2','NAXIS1','NAXIS2'])
                if start == 1:
                    crpixzero = copy(crpix)
                    crpixhigh = copy(crpix)
                    start = 0
                from copy import copy 
                if float(crpix['CRPIX1'])  > float(crpixzero['CRPIX1']) and float(crpix['CRPIX2'])  > float(crpixzero['CRPIX2']):
                    crpixzero = copy(crpix)
    
                if float(crpix['CRPIX1'])  < float(crpixhigh['CRPIX1']) and float(crpix['CRPIX2'])  < float(crpixhigh['CRPIX2']):
                    crpixhigh = copy(crpix)
    
                print crpix, crpixzero, crpixhigh
            LENGTH1 =  abs(float(crpixhigh['CRPIX1']) - float(crpixzero['CRPIX1'])) + float(crpix['NAXIS1']) 
            LENGTH2 =  abs(float(crpixhigh['CRPIX2']) - float(crpixzero['CRPIX2'])) + float(crpix['NAXIS2']) 
            print crpixhigh['CRPIX1'], crpixzero['CRPIX1'], crpix['NAXIS1'], crpix['NAXIS2']
    
    
    
            print exposure['images']
            'exposures'
    
            children = []
            for image in exposure['images']:
                child = os.fork()
                if child:
                    children.append(child)
                else:
                    print fwhm 
                    params = copy(search_params)  
                    
                    finalflagim = TEMPDIR + "flag_%(ROOT)s.fits" % params 
    
                    weightim = "/%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits" % params
                    #flagim = "/%(path)s/%(fil_directory)s/WEIGHTS/globalflag_%(NUM)s.fits" % params
                    #finalflagim = TEMPDIR + "flag_%(ROOT)s.fits" % params 
                    params['finalflagim'] = weightim
                    im = "/%(path)s/%(fil_directory)s/SCIENCE/%(ROOT)s.fits" % params
                    crpix = utilities.get_header_kw(im,['CRPIX1','CRPIX2'])
    
                    command = "sex /%(path)s/%(fil_directory)s/SCIENCE/%(ROOT)s.fits -c %(PHOTCONF)s/phot.conf.sex \
                    -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
                    -CATALOG_NAME %(TEMPDIR)s/%(ROOT)s.cat \
                    -FILTER_NAME %(DATACONF)s/default.conv\
                    -FILTER  Y \
                    -FLAG_TYPE MAX\
                    -FLAG_IMAGE ''\
                    -SEEING_FWHM %(fwhm).3f \
                    -DETECT_MINAREA 10 -DETECT_THRESH 10 -ANALYSIS_THRESH 10 \
                    -MAG_ZEROPOINT 27.0 \
                    -GAIN %(GAIN).3f \
                    -WEIGHT_IMAGE /%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits\
                    -WEIGHT_TYPE MAP_WEIGHT" % params
                    #-CHECKIMAGE_TYPE BACKGROUND,APERTURES,SEGMENTATION\
                    #-CHECKIMAGE_NAME /%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.background.fits,/%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.apertures.fits,/%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.segmentation.fits\
                                                                                                                                                                                                          
                    catname = "%(TEMPDIR)s/%(ROOT)s.cat" % params
                    filtcatname = "%(TEMPDIR)s/%(ROOT)s.filt.cat" % params
                    print command
                    utilities.run(command,[catname])
    
                    utilities.run('ldacfilter -i ' + catname + ' -o ' + filtcatname + ' -t LDAC_OBJECTS\
                                -c "(CLASS_STAR > 0.5);"',[filtcatname])
    
                    import commands
                    lines = commands.getoutput('ldactoasc -s -b -i ' + filtcatname + ' -t LDAC_OBJECTS | wc -l')
                    import re
                    res = re.split('\n',lines)
                    print lines
                    if int(res[-1]) == 0: sys.exit(0)
    
                    command = 'scamp ' + filtcatname + " -SOLVE_PHOTOM N -ASTREF_CATALOG SDSS-R6 -CHECKPLOT_TYPE NONE -WRITE_XML N "  
    
                    print command
                    utilities.run(command)
    
    
                    #headfile = "%(TEMPDIR)s/%(ROOT)s.head" % params
    
                    headfile = "%(TEMPDIR)s/%(ROOT)s.filt.head" % params
                    hf = open(headfile,'r').readlines() 
                    hdict = {}
                    for line in hf:
                        import re
                        if string.find(line,'=') != -1:
                            res = re.split('=',line)
                            name = res[0].replace(' ','')
                            res = re.split('/',res[1])
                            value = res[0].replace(' ','')
                            print name, value
                            hdict[name] = value
                   
                    imfix = "/tmp/%(ROOT)s.fixwcs.fits" % params
    
                    command = "cp " + im + " " + imfix
                    utilities.run(command)
    
                    for name in ['CRVAL1','CRVAL2','CD1_1','CD1_2','CD2_1','CD2_2','CRPIX1','CRPIX1']:
                        command = 'sethead ' + imfix + ' ' + name + '=' + hdict[name]
                        print command
                        os.system(command)
    
                    command = "sex /tmp/%(ROOT)s.fixwcs.fits -c %(PHOTCONF)s/phot.conf.sex \
                    -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
                    -CATALOG_NAME %(TEMPDIR)s/%(ROOT)s.fixwcs.cat \
                    -FILTER_NAME %(DATACONF)s/default.conv\
                    -FILTER  Y \
                    -FLAG_TYPE MAX\
                    -FLAG_IMAGE ''\
                    -SEEING_FWHM %(fwhm).3f \
                    -DETECT_MINAREA 5 -DETECT_THRESH 5 -ANALYSIS_THRESH 5 \
                    -MAG_ZEROPOINT 27.0 \
                    -GAIN %(GAIN).3f \
                    -WEIGHT_IMAGE /%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits\
                    -WEIGHT_TYPE MAP_WEIGHT" % params
                    #-CHECKIMAGE_TYPE BACKGROUND,APERTURES,SEGMENTATION\
                    #-CHECKIMAGE_NAME /%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.background.fits,/%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.apertures.fits,/%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.segmentation.fits\
                    catname = "%(TEMPDIR)s/%(ROOT)s.cat" % params
                    print command
                    utilities.run(command,[catname])
    
                    command = 'ldacconv -b 1 -c R -i ' + TEMPDIR + params['ROOT'] + '.fixwcs.cat -o ' + TEMPDIR + params['ROOT'] + '.conv'
                    print command
                    utilities.run(command)
                    # Xpos_ABS is difference of CRPIX and zero CRPIX
                    command = 'ldaccalc -i ' + TEMPDIR + params['ROOT'] + '.conv -o ' + TEMPDIR + params['ROOT'] + '.newpos -t OBJECTS -c "(Xpos + ' + str(float(crpixzero['CRPIX1']) - float(crpix['CRPIX1'])) + ');" -k FLOAT -n Xpos_ABS "" -c "(Ypos + ' + str(float(crpixzero['CRPIX2']) - float(crpix['CRPIX2'])) + ');" -k FLOAT -n Ypos_ABS "" -c "(Ypos*0 + ' + str(params['NUM']) + ');" -k FLOAT -n CHIP "" ' 
    
                    #command = 'ldaccalc -i ' + TEMPDIR + params['ROOT'] + '.conv -o ' + TEMPDIR + params['ROOT'] + '.newpos -t OBJECTS -c "(' + str(crpix['CRPIX1']) + ' - Xpos);" -k FLOAT -n Xpos_ABS "" -c "(' + str(crpix['CRPIX2']) + ' - Ypos);" -k FLOAT -n Ypos_ABS "" -c "(Ypos*0 + ' + str(params['NUM']) + ');" -k FLOAT -n CHIP "" ' 
                    print command
                    utilities.run(command)
                    sys.exit(0)
            for child in children:  
                #print 'waiting for' child
                os.waitpid(child,0)
    
    
            from glob import glob
            outcat = TEMPDIR + 'tmppaste_' + kw + '.cat'
    
            newposlist = glob(TEMPDIR + kw + '*newpos')
            if len(newposlist) > 1:
                command = 'ldacpaste -i ' + TEMPDIR + kw + '*newpos -o ' + outcat 
                print command
            else:
                command = 'cp ' + newposlist[0] + ' ' + outcat 
    
            utilities.run(command)
    
    
            os.system('ldactoasc -i ' + outcat + ' -b -s -k MAG_APER MAGERR_APER -t OBJECTS > /tmp/' + kw + 'aper')
            os.system('asctoldac -i /tmp/' + kw + 'aper -o /tmp/' + kw + 'cat1 -t OBJECTS -c ./photconf/MAG_APER.conf')
    
            outfinal = TEMPDIR + 'paste_' + kw + '.cat'
            os.system('ldacjoinkey -i ' + outcat + ' -p /tmp/' + kw + 'cat1 -o ' + outfinal + ' -k MAG_APER1 MAG_APER2 MAGERR_APER1 MAGERR_APER2')
    
            exposures[kw]['pasted_cat'] = outfinal
    
        return exposures, LENGTH1, LENGTH2 
    
    def match_simple(self,exposures,cluster):
        import os
        print exposures
        starcat ='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/PHOTOMETRY/sdssstar.cat' % {'cluster':cluster}
        galaxycat ='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/PHOTOMETRY/sdssgalaxy.cat' % {'cluster':cluster}
    
        path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':cluster}
        illum_path='/nfs/slac/g/ki/ki05/anja/SUBARU/ILLUMINATION/' % {'cluster':cluster}
        #os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/') 
        os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/STAR/') 
        os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/GALAXY/') 
        from glob import glob
    
    
        for type,cat in [['galaxy',galaxycat],['star',starcat]]:
            if len(glob(cat)) == 0:                                      
                image = exposures[exposures.keys()[0]]['images'][0]
                print image
                import retrieve_test
                retrieve_test.run(image,cat,type)
    
            for exposure in exposures.keys():                        
                print exposure + 'aa'
                catalog = exposures[exposure]['pasted_cat']
                filter = exposures[exposure]['keywords']['filter']
                ROTATION = exposures[exposure]['keywords']['ROTATION']
                #GABODSID = exposures[exposure]['keywords']['GABODSID']
                OBJECT = exposures[exposure]['keywords']['OBJECT']
                print catalog
                outcat = path + 'PHOTOMETRY/ILLUMINATION/' + type + '/' + 'matched_' + exposure + '_' + filter + '_' + ROTATION + '_' + type + '.cat'               
                outcat_dir = path + 'PHOTOMETRY/ILLUMINATION/' + type + '/' + ROTATION + '/' + OBJECT + '/'
                os.system('mkdir -p ' + outcat_dir)
                file = 'matched_' + exposure + '.cat'               
                linkdir = illum_path + '/' + filter + '/' + ROTATION + '/' + OBJECT + '/'              
                #outcatlink = linkdir + 'matched_' + exposure + '_' + cluster + '_' + GABODSID + '.cat' 
                outcatlink = linkdir + 'matched_' + exposure + '_' + cluster + '_' + type + '.cat' 
                os.system('mkdir -p ' + linkdir)
                os.system('rm ' + outcat)
                command = 'match_simple.sh ' + catalog + ' ' + cat + ' ' + outcat
                print command
                os.system(command)
    
                exposures[exposure]['matched_cat_' + type] = outcat
                os.system('rm ' + outcatlink)
                command = 'ln -s ' + outcat + ' ' + outcatlink
                print command
                os.system(command)
    
        return exposures
    
    def phot(self,exposures,filter,type,LENGTH1,LENGTH2): 
        import utilities
        info = {'B':{'filter':'g','color1':'gmr','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0},\
            'W-J-B':{'filter':'g','color1':'gmr','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0},\
            'W-J-V':{'filter':'g','color1':'gmr','color2':'rmi','EXTCOEFF':-0.1202,'COLCOEFF':0.0},\
            'W-C-RC':{'filter':'r','color1':'rmi','color2':'gmr','EXTCOEFF':-0.0925,'COLCOEFF':0.0},\
            'W-C-IC':{'filter':'i','color1':'imz','color2':'rmi','EXTCOEFF':-0.02728,'COLCOEFF':0.0},\
            'W-S-Z+':{'filter':'z','color1':'imz','color2':'rmi','EXTCOEFF':0.0,'COLCOEFF':0.0}}
        
        import mk_saturation_plot,os,re
        os.environ['BONN_TARGET'] = cluster
        os.environ['INSTRUMENT'] = 'SUBARU'
    
        stars_0 = []
        stars_90 = []
    
        for exposure in exposures.keys():
    
            ROTATION = exposures[exposure]['keywords']['ROTATION']
            print ROTATION 
            import os
            ppid = str(os.getppid())
            from glob import glob
            for type in ['galaxy','star']:
    
                file = exposures[exposure]['matched_cat_' + type]
                print file
                if type == 'galaxy':
                    mag='MAG_AUTO'       
                    magerr='MAGERR_AUTO'
                if type == 'star':
                    mag='MAG_APER2'       
                    magerr='MAGERR_APER2'
    
                
                for filter in [filter]:                                                                                                                                                                                                                                                               
                    print 'filter', filter
                    os.environ['BONN_FILTER'] = filter 
                    dict = info[filter]
                    print base + file  
                    utilities.run('ldacfilter -i ' + base + file + ' -o /tmp/good.stars' + ppid + ' -t PSSC\
                                -c "(Flag!=-99);"',['/tmp/good.stars' + ppid])
               
                    #command = 'ldacfilter -i ' + base + file + ' -o /tmp/good.stars' + ppid + ' -t PSSC -c "(((SEx_IMAFLAGS_ISO=0 AND SEx_CLASS_STAR>0.0) AND (SEx_Flag=0)) AND Flag=0);"'
    
    
                    #print command
                    #raw_input()
                    #utilities.run(command,['/tmp/good.stars' + ppid])
                         
                
                    #run('ldacfilter -i ' + base + file + ' -o /tmp/good.stars -t PSSC\
                   #             -c "(SEx_CLASS_STAR>0.00);"',['/tmp/good.stars'])
                                                                                                                                                                                                                                                                                                     
                    utilities.run('ldacfilter -i /tmp/good.stars' + ppid + ' -o /tmp/good.colors' + ppid + ' -t PSSC\
                                -c "(' + dict['color1'] + '>-900) AND (' + dict['color2'] + '>-900);"',['/tmp/good.colors'])
                
                    #utilities.run('ldacfilter -i /tmp/good.stars' + ppid  + ' -o /tmp/good.colors' + ppid + ' -t PSSC\
                    #            -c "(' + dict['color1'] + '>-900) AND (' + dict['color2'] + '>-900);"',['/tmp/good.colors' + ppid])
                
                    utilities.run('ldaccalc -i /tmp/good.colors' + ppid + ' -t PSSC -c "(' + dict['filter'] + 'mag - SEx_' + mag + ');"  -k FLOAT -n magdiff "" -o /tmp/all.diff.cat' + ppid ,['/tmp/all.diff.cat' + ppid] )
                
                    #utilities.run('ldactoasc -b -q -i /tmp/all.diff.cat' + ppid + ' -t PSSC -k SEx_' + mag + ' ' + dict['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + dict['filter'] + 'err ' + dict['color1'] + ' > /tmp/mk_sat' + ppid,['/tmp/mk_sat' + ppid] )
    
                    utilities.run('ldactoasc -b -q -i /tmp/all.diff.cat' + ppid + ' -t PSSC -k SEx_FLUX_MAX ' + dict['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + dict['filter'] + 'err ' + dict['color1'] + ' > /tmp/mk_sat' + ppid,['/tmp/mk_sat' + ppid] )
    
                    #utilities.run('ldactoasc -b -q -i ' + base + file + ' -t PSSC -k SEx_' + mag + ' ' + dict['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + dict['filter'] + 'err ' + dict['color1'] + ' > /tmp/mk_sat' + ppid,['/tmp/mk_sat' + ppid] )
                
                
                #    run('ldactoasc -b -q -i ' + base + file + ' -t PSSC -k SEx_' + mag + '_' + filter +  ' ' + dict['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + dict['filter'] + 'err ' + dict['color1'] + ' > /tmp/mk_sat',['/tmp/mk_sat'] )
                    val = [] 
                    val = raw_input("Look at the saturation plot?")
                    if len(val)>0:
                        if val[0] == 'y' or val[0] == 'Y':
                            mk_saturation_plot.mk_saturation('/tmp/mk_sat' + ppid,filter)
                            # make stellar saturation plot                              
               
                    #lower_mag,upper_mag,lower_diff,upper_diff = re.split('\s+',open('box' + filter,'r').readlines()[0])
    
    
                    lower_mag = str(10)
                    upper_mag = str(14.0)
                    lower_diff = str(5)
                    upper_diff = str(9)
                    if type == 'star': 
                        lower_mag = str(13.2)
                     
                    
                    #utilities.run('ldacfilter -i /tmp/all.diff.cat' + ppid + ' -t PSSC\
                    #            -c "(((SEx_' + mag + '>' + lower_mag + ') AND (SEx_' + mag + '<' + upper_mag + ')) AND (magdiff>' + lower_diff + ')) AND (magdiff<' + upper_diff + ');"\
                    #            -o /tmp/filt.mag.cat' + ppid ,['/tmp/filt.mag.cat' + ppid])
    
                    #utilities.run('ldacfilter -i /tmp/all.diff.cat' + ppid + ' -t PSSC\
                    #            -c "(((' + dict['filter'] + 'mag>' + lower_mag + ') AND (' + dict['filter'] + 'mag<' + upper_mag + ')) AND (magdiff>' + lower_diff + ')) AND (magdiff<' + upper_diff + ');"\
                    #            -o /tmp/filt.mag.cat' + ppid ,['/tmp/filt.mag.cat' + ppid])
                
                    utilities.run('ldactoasc -b -q -i /tmp/all.diff.cat' + ppid + ' -t PSSC -k SEx_Xpos_ABS SEx_Ypos_ABS > /tmp/positions' + ppid,['/tmp/positions' + ppid] )
                
                    utilities.run('ldacaddkey -i /tmp/all.diff.cat' + ppid + ' -o /tmp/filt.airmass.cat' + ppid + ' -t PSSC -k AIRMASS 0.0 FLOAT "" ',['/tmp/filt.airmass.cat' + ppid]  )
                    
                    utilities.run('ldactoasc -b -q -i /tmp/filt.airmass.cat' + ppid + ' -t PSSC -k SEx_' + mag + ' ' + dict['filter'] + 'mag ' + dict['color1'] + ' ' + dict['color2'] + ' AIRMASS SEx_' + magerr + ' ' + dict['filter'] + 'err SEx_Xpos_ABS SEx_Ypos_ABS > /tmp/input.asc' + ppid ,['/tmp/input.asc' + ppid] )
                                                                                                                                                                                                                                                                                                     
                    #utilities.run('ldactoasc -b -q -i /tmp/filt.airmass.cat -t PSSC -k SEx_' + mag + ' ' + dict['filter'] + 'mag ' + dict['color1'] + ' ' + dict['color2'] + ' AIRMASS SEx_' + magerr + ' ' + dict['filter'] + 'err SEx_Ra SEx_Dec > /tmp/input.asc',['/tmp/input.asc'] )
                        
                    # fit photometry
                    #utilities.run("./photo_abs_new.py --input=/tmp/input.asc \
                    #    --output=/tmp/photo_res --extinction="+str(dict['EXTCOEFF'])+" \
                    #    --color="+str(dict['COLCOEFF'])+" --night=-1 --label="+dict['color1']+" --sigmareject=3\
                    #     --step=STEP_1 --bandcomp="+dict['filter']+" --color1="+dict['color1']+" --color2="+dict['color2'])
                                                                                                                                                                                                                                                                                                     
                    import photo_abs_new                
                    
                    good_stars = photo_abs_new.run_through('illumination',infile='/tmp/input.asc' + ppid,output='/tmp/photo_res',extcoeff=dict['color1'],sigmareject=3,step='STEP_1',bandcomp=dict['filter'],color1which=dict['color1'],color2which=dict['color2'])
                  
                    if int(ROTATION) == 0: 
                        stars_0.append(good_stars)
    
                    if int(ROTATION) == 1: 
                        stars_90.append(good_stars)
    
    
        from copy import copy
    
    
        print 'running calcDataIllum'
       
    
        if len(stars_0)> 0:
            dict = copy(stars_0[0])                                                                                                                                                                        
            blank_0 = {} 
            for key in dict.keys():
                blank_0[key] = []
                for i in range(len(stars_0)): 
                    for j in range(len(stars_0[i][key])): blank_0[key].append(stars_0[i][key][j]) 
                    #print key, blank[key]
            
            photo_abs_new.calcDataIllum('illumination',LENGTH1, LENGTH2, 1000, blank_0['corr_data'], blank_0['airmass_good'], blank_0['color1_good'], blank_0['color2_good'], blank_0['magErr_good'], blank_0['X_good'], blank_0['Y_good'],rot=0)
    
    
        if len(stars_90)> 0:
            dict = copy(stars_90[0])                                                                                                                                                                              
            blank_90 = {} 
            for key in dict.keys():
                blank_90[key] = []
                for i in range(len(stars_90)): 
                    for j in range(len(stars_90[i][key])): blank_90[key].append(stars_90[i][key][j]) 
                    #print key, blank[key]                                                                            
            photo_abs_new.calcDataIllum('illumination',LENGTH1, LENGTH2, 1000, blank_90['corr_data'], blank_90['airmass_good'], blank_90['color1_good'], blank_90['color2_good'], blank_90['magErr_good'], blank_90['X_good'], blank_90['Y_good'],rot=0)
            #photo_abs_new.calcDataIllum('illumination',1000, blank_90['corr_data'], blank_90['airmass_good'], blank_90['color1_good'], blank_90['color2_good'], blank_90['magErr_good'], blank_90['X_good'], blank_90['Y_good'],rot=1)


from config_bonn import cluster
filter = 'W-C-IC'
import pickle

#filters = ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']

#for filter in filters:

if reopen:
    f = open('/tmp/tmppickle' + cluster + filter,'r')
    m = pickle.Unpickler(f)
    exposures, LENGTH1, LENGTH2 = m.load()

    print image.latest

if 1: images = gather_exposures(filter,cluster)

print images

''' strip down exposure list '''
for key in exposures.keys():
    print exposures[key]['images']




for image in exposures:
    if 1: image.find_seeing(exposures) # save seeing info?
    if 1: image.sextract(exposures)
    if 1: image.match_simple(exposures,cluster)
    if 1: image.phot(exposures,filter,type,LENGTH1,LENGTH2)

if save:
    f = open('/tmp/tmppickle' + cluster + filter,'w')
    m = pickle.Pickler(f)
    pickle.dump([exposures,LENGTH1,LENGTH2],m)
    f.close()
