def find_seeing(SUPA,FLAT_TYPE):     
    import os, re, utilities, sys
    from copy import copy
    dict = get_files(SUPA,FLAT_TYPE)
    print dict['file']
    search_params = initialize(dict['filter'],dict['cluster'])
    search_params.update(dict)

    print dict['files']

    #params PIXSCALE GAIN

    ''' quick run through for seeing '''
    children = []
    for image in search_params['files']:                                                                                 
        child = os.fork()
        if child:
            children.append(child)
        else:
            params = copy(search_params)     
            
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
            
            command = "nice sex %(file)s -c %(PHOTCONF)s/singleastrom.conf.sex \
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
                                                                                                                          
                                                                                                                          
    command = 'cat ' + search_params['TEMPDIR'] + 'seeing_' +  SUPA + '*cat > ' + search_params['TEMPDIR'] + 'paste_seeing_' + SUPA + '.cat' 
    utilities.run(command)
                                                                                                                          
    file_seeing = search_params['TEMPDIR'] + '/paste_seeing_' + SUPA + '.cat'
    PIXSCALE = float(search_params['PIXSCALE'])
    reload(utilities)
    fwhm = utilities.calc_seeing(file_seeing,10,PIXSCALE)

    save_exposure({'fwhm':fwhm},SUPA,FLAT_TYPE)

    print file_seeing, SUPA, PIXSCALE


def find_files(directories):

    exposures = {}

    import glob
    files = glob.glob(directories + '/SCIENCE/*fits')
    print files





def sextract(FILE):
    import os, re, utilities, bashreader, sys, string
    from copy import copy
    from glob import glob
    
    dict = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['cluster'])
    search_params.update(dict)
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':search_params['cluster']}
    subpath='/nfs/slac/g/ki/ki05/anja/SUBARU/'

    children = []
    print search_params

    kws = utilities.get_header_kw(search_params['files'][0],['PPRUN'])
    print kws['PPRUN']
    pprun = kws['PPRUN']

    #fs = glob.glob(subpath+pprun+'/SCIENCE_DOMEFLAT*.tarz')
    #if len(fs) > 0: 
    #    os.system('tar xzvf ' + fs[0])
    #fs = glob.glob(subpath+pprun+'/SCIENCE_SKYFLAT*.tarz')
    #if len(fs) > 0: 
    #    os.system('tar xzvf ' + fs[0])


    search_params['files'].sort()

    if 1:
        print search_params['files']                                                                                                                                                                                                                                                                                                                                                                                                                                
        for image in search_params['files']:
            print image
            child = os.fork()
            if child:
                children.append(child)
            else:
                try:
                    params = copy(search_params)     
                    ROOT = re.split('\.',re.split('\/',image)[-1])[0]
                    params['ROOT'] = ROOT
                    BASE = re.split('O',ROOT)[0]
                    params['BASE'] = BASE 
                    NUM = re.split('O',re.split('\_',ROOT)[1])[0]
                    params['NUM'] = NUM
                    print NUM, BASE, ROOT
                    params['GAIN'] = 2.50 ## WARNING!!!!!!
                    print ROOT
                    finalflagim = "%(TEMPDIR)sflag_%(ROOT)s.fits" % params     
                    weightim = "/%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits" % params
                    #flagim = "/%(path)s/%(fil_directory)s/WEIGHTS/globalflag_%(NUM)s.fits" % params
                    #finalflagim = TEMPDIR + "flag_%(ROOT)s.fits" % params 
                    params['finalflagim'] = weightim
                    im = "/%(path)s/%(fil_directory)s/SCIENCE/%(ROOT)s.fits" % params
                    crpix = utilities.get_header_kw(im,['CRPIX1','CRPIX2'])
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                    SDSS1 = "/%(path)s/%(fil_directory)s/SCIENCE/headers_scamp_SDSS-R6/%(BASE)s.head" % params
                    SDSS2 = "/%(path)s/%(fil_directory)s/SCIENCE/headers_scamp_SDSS-R6/%(BASE)sO*.head" % params
                    from glob import glob 
                    print glob(SDSS1), glob(SDSS2)
                    head = None
                    if len(glob(SDSS1)) > 0:
                        head = glob(SDSS1)[0]
                    elif len(glob(SDSS2)) > 0:
                        head = glob(SDSS2)[0]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                    if head is None:
                        command = "sex /%(path)s/%(fil_directory)s/SCIENCE/%(ROOT)s.fits -c %(PHOTCONF)s/phot.conf.sex \
                        -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
                        -CATALOG_NAME %(TEMPDIR)s/%(ROOT)s.cat \
                        -FILTER_NAME %(DATACONF)s/default.conv\
                        -FILTER  Y \
                        -FLAG_TYPE MAX\
                        -FLAG_IMAGE ''\
                        -SEEING_FWHM %(fwhm).3f \
                        -DETECT_MINAREA 3 -DETECT_THRESH 3 -ANALYSIS_THRESH 3 \
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
                                    -c "(CLASS_STAR > 0.0);"',[filtcatname])
                        if len(glob(filtcatname)) > 0:
                            import commands                                                                                                        
                            lines = commands.getoutput('ldactoasc -s -b -i ' + filtcatname + ' -t LDAC_OBJECTS | wc -l')
                            import re
                            res = re.split('\n',lines)
                            print lines
                            if int(res[-1]) == 0: sys.exit(0)
                            command = 'scamp ' + filtcatname + " -SOLVE_PHOTOM N -ASTREF_CATALOG SDSS-R6 -CHECKPLOT_TYPE NONE -WRITE_XML N "  
                            print command
                            utilities.run(command)
                            head = "%(TEMPDIR)s/%(ROOT)s.filt.head" % params
                            #headfile = "%(TEMPDIR)s/%(ROOT)s.head" % params
                    print head 
                    if head is not None:
                        hf = open(head,'r').readlines() 
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
                                                                                                                                               
                        imfix = "%(TEMPDIR)s/%(ROOT)s.fixwcs.fits" % params
                        print imfix
                        
                        os.system('mkdir ' + search_params['TEMPDIR'])
                        command = "cp " + im + " " + imfix
                        print command
                        utilities.run(command)
                       
                        import commands
                        out = commands.getoutput('gethead ' + imfix + ' CRPIX1 CRPIX2')
                        import re
                        res = re.split('\s+',out)
                        os.system('sethead ' + imfix + ' CRPIX1OLD=' + res[0])
                        os.system('sethead ' + imfix + ' CRPIX2OLD=' + res[1])
                        for name in ['CRVAL1','CRVAL2','CD1_1','CD1_2','CD2_1','CD2_2','CRPIX1','CRPIX2']:
                            command = 'sethead ' + imfix + ' ' + name + '=' + hdict[name]
                            print command
                            os.system(command)
                        main_file = '%(TEMPDIR)s/%(ROOT)s.fixwcs.fits' % params
                        doubles_raw = [{'file_pattern':main_file,'im_type':''},
                                       {'file_pattern':subpath+pprun+'/SCIENCE_DOMEFLAT*/'+BASE+'OC*.fits','im_type':'D'},
                                       {'file_pattern':subpath+pprun+'/SCIENCE_SKYFLAT*/'+BASE+'OC*.fits','im_type':'S'}]
                                       #{'file_pattern':subpath+pprun+'/SCIENCE/OC_IMAGES/'+BASE+'OC*.fits','im_type':'OC'}
                                       # ] 
                                                                                                                                  
                        print doubles_raw
                        doubles_output = []
                        print doubles_raw
                        for double in doubles_raw:
                            file = glob(double['file_pattern'])
                            if len(file) > 0:
                                params.update(double) 
                                params['double_cat'] = '%(TEMPDIR)s/%(ROOT)s.%(im_type)s.fixwcs.cat' % params
                                params['file_double'] = file[0]
                                command = "nice sex %(TEMPDIR)s%(ROOT)s.fixwcs.fits,%(file_double)s -c %(PHOTCONF)s/phot.conf.sex \
                                -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
                                -CATALOG_NAME %(double_cat)s \
                                -FILTER_NAME %(DATACONF)s/default.conv\
                                -FILTER  Y \
                                -FLAG_TYPE MAX\
                                -FLAG_IMAGE ''\
                                -SEEING_FWHM %(fwhm).3f \
                                -DETECT_MINAREA 3 -DETECT_THRESH 3 -ANALYSIS_THRESH 3 \
                                -MAG_ZEROPOINT 27.0 \
                                -GAIN %(GAIN).3f \
                                -WEIGHT_IMAGE /%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits\
                                -WEIGHT_TYPE MAP_WEIGHT" % params
                                #-CHECKIMAGE_TYPE BACKGROUND,APERTURES,SEGMENTATION\
                                #-CHECKIMAGE_NAME /%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.background.fits,/%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.apertures.fits,/%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.segmentation.fits\
                                catname = "%(TEMPDIR)s/%(ROOT)s.cat" % params
                                print command
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                                utilities.run(command,[catname])
                                command = 'ldacconv -b 1 -c R -i ' + params['double_cat']  + ' -o '  + params['double_cat'].replace('cat','rawconv')
                                print command
                                utilities.run(command)
                                #command = 'ldactoasc -b -q -i ' + params['double_cat'].replace('cat','rawconv') + '  -t OBJECTS\
                                #        -k ALPHA_J2000 DELTA_J2000 > ' + params['double_cat'].replace('cat','pos')
                                #print command
                                #utilities.run(command)
                                #print 'mkreg.pl -c -rad 8 -xcol 0 -ycol 1 -wcs -colour green ' + params['double_cat'].replace('cat','pos')
                                #utilities.run(command)
                                #print params['double_cat'].replace('cat','pos')
                                # Xpos_ABS is difference of CRPIX and zero CRPIX
                                doubles_output.append({'cat':params['double_cat'].replace('cat','rawconv'),'im_type':double['im_type']})
                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
                        print doubles_output
                        print '***********************************'
                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
                        outfile = params['TEMPDIR'] + params['ROOT'] + '.conv'
                        combine_cats(doubles_output,outfile,search_params)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                        #outfile_field = params['TEMPDIR'] + params['ROOT'] + '.field'
                        #command = 'ldacdeltab -i ' + outfile + ' -t FIELDS -o ' + outfile_field
                        #utilities.run(command)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                        command = 'ldactoasc -b -q -i ' + outfile + '  -t OBJECTS\
                                        -k ALPHA_J2000 DELTA_J2000 > ' + outfile.replace('conv','pos')
                        print command
                        utilities.run(command)
                        command = 'mkreg.pl -c -rad 8 -xcol 0 -ycol 1 -wcs -colour green ' + outfile.replace('conv','pos')
                        print command
                        utilities.run(command)
                        print outfile
                        command = 'ldaccalc -i ' + outfile + ' -o ' + params['TEMPDIR'] + params['ROOT'] + '.newpos -t OBJECTS -c "(Xpos + ' +  str(float(search_params['CRPIX1ZERO']) - float(crpix['CRPIX1'])) + ');" -k FLOAT -n Xpos_ABS "" -c "(Ypos + ' + str(float(search_params['CRPIX2ZERO']) - float(crpix['CRPIX2'])) + ');" -k FLOAT -n Ypos_ABS "" -c "(Ypos*0 + ' + str(params['NUM']) + ');" -k FLOAT -n CHIP "" ' 
                        print command
                        utilities.run(command)
                except:
                    print sys.exc_info()
                    print 'finishing' 
                    sys.exit(0)
                sys.exit(0)
        print children
        for child in children:  
            print 'waiting for', child
            os.waitpid(child,0)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
        print 'finished waiting'

    pasted_cat = path + 'PHOTOMETRY/ILLUMINATION/' + 'pasted_' + SUPA + '_' + search_params['filter'] + '_' + str(search_params['ROTATION']) + '.cat'

    from glob import glob        
    outcat = search_params['TEMPDIR'] + 'tmppaste_' + SUPA + '.cat'
    newposlist = glob(search_params['TEMPDIR'] + SUPA + '*newpos')
    print search_params['TEMPDIR'] + SUPA + '*newpos'
    if len(newposlist) > 1:
        #command = 'ldacpaste -i ' + search_params['TEMPDIR'] + SUPA + '*newpos -o ' + pasted_cat 
        #print command
        files = glob(search_params['TEMPDIR'] + SUPA + '*newpos')
        print files
        paste_cats(files,pasted_cat)
    else:
        command = 'cp ' + newposlist[0] + ' ' + pasted_cat 
        utilities.run(command)
    save_exposure({'pasted_cat':pasted_cat},SUPA,FLAT_TYPE)

    #fs = glob.glob(subpath+pprun+'/SCIENCE_DOMEFLAT*.tarz'.replace('.tarz','')) 
    #if len(fs) > 0: 
    #    os.system('tar xzvf ' + fs[0])
                                                            
    #fs = glob.glob(subpath+pprun+'/SCIENCE_SKYFLAT*.tarz'.replace('.tarz',''))
    #fs = glob.glob(subpath+pprun+'/SCIENCE_SKYFLAT*.tarz')
    #if len(fs) > 0: 
    #    os.system('tar xzvf ' + fs[0])


    #return exposures, LENGTH1, LENGTH2 
