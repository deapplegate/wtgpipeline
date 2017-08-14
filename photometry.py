
def do_multiple(OBJNAME):
    #!/usr/bin/env python
    import os, sys, bashreader, commands
    from utilities import *
    from config_bonn import appendix, cluster, tag, arc, filters, filter_root, appendix_root
    
    dict = bashreader.parseFile('progs.ini')
    for key in dict.keys():
        os.environ[key] = str(dict[key])
    
    
    TEMPDIR = '/tmp/'
    PHOTCONF = './photconf/'
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%s/' % cluster
    #type='each'
    type='all'
    
    filecommand = open('record.analysis','w')
    
    BASE="coadd"
    image = BASE + '.fits'
    
    print 'Finished Loading Config, utils'
    
    if type == 'all' or type == 'each':
        children = []
        for filter in filters:
            child = os.fork()
            if child:
                children.append(child)
            else:
                params = {'path':path, 
                          'filter_root': filter_root, 
                          'cluster':cluster, 
                          'filter':filter,
                          'appendix':appendix, 
                          'PHOTCONF':PHOTCONF, 
                          'TEMPDIR': TEMPDIR}
                print params
                # now run sextractor to determine the seeing:              
                command = 'sex %(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits -c %(PHOTCONF)s/singleastrom.conf.sex \
                            -FLAG_IMAGE /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits \
                            -FLAG_TYPE MAX\
                            -CATALOG_NAME %(TEMPDIR)s/seeing_%(filter)s.cat \
                            -FILTER_NAME %(PHOTCONF)s/default.conv\
                            -CATALOG_TYPE "ASCII" \
                            -DETECT_MINAREA 10 -DETECT_THRESH 10.\
                            -ANALYSIS_THRESH 5 \
                            -PARAMETERS_NAME %(PHOTCONF)s/singleastrom.ascii.param.sex' %  params 
                print command
                os.system(command)
                sys.exit(0)
        for child in children: 
            os.waitpid(child,0)
        
        print 'DONE W/ SEEING'
        
    fwhms = {} 
    for filter in filters:
        file_header = '/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits' % {'TEMPDIR': TEMPDIR, 'filter':filter, 'path': path, 'cluster': cluster, 'appendix':appendix}
        GAIN, PIXSCALE, EXPTIME = get_header_info(file_header) 
        print GAIN, PIXSCALE
    
        fwhms[filter] = {'FILTER':filter,'GAIN':GAIN,'PIXSCALE':PIXSCALE, 'EXPTIME': EXPTIME}
    
        if type == 'all' or type == 'each':
            file_seeing = '%(TEMPDIR)s/seeing_%(filter)s.cat' % {'TEMPDIR': TEMPDIR, 'filter':filter}
            NLINES=50
            print 'filter', filter
            fwhms[filter]['SEEING'] = calc_seeing(file_seeing,NLINES,PIXSCALE)
    
    
    if type == 'all' or type == 'each':
        fwhms_comp=[fwhms[x] for x in fwhms.keys()] 
        fwhms_comp.sort(compare) 
        seeing_worst = fwhms_comp[0]['SEEING']
        filter_worst = fwhms_comp[0]['FILTER']
        print fwhms
        print 'SEEING', filter_worst, seeing_worst
        for x in fwhms.keys():
            print x, fwhms[x]
    
        
        import commands
    
        for filter in filters: 
            print filter
    
            params = {'seeing_orig':float(fwhms[filter]['SEEING']), 'seeing_new':float(seeing_worst),'PIXSCALE':float(PIXSCALE), 'path':path, 'cluster': cluster, 'appendix': appendix, 'filter':filter, 'path':path, 'DATACONF': os.environ['DATACONF']}
    
            command = 'mkdir %(DATACONF)s/default.conv %(path)s/%(filter)s/PHOTOMETRY/' % params 
            os.system(command)
            if filter != filter_worst:
                print params
                command = 'python create_gausssmoothing_kernel.py %(seeing_orig).3f %(seeing_new).3f %(PIXSCALE).3f %(path)s/%(filter)s/PHOTOMETRY/' % params 
                print command
                os.system(command)
            else:
                command = 'cp %(DATACONF)s/default.conv %(path)s/%(filter)s/PHOTOMETRY/gauss.conv' % params 
                os.system(command)
        
    
          
    
    children = [] 
    for filter in filters: 
        os.system("mkdir /" + path + "/" + filter + "/PHOTOMETRY/")
        os.system("rm /" + path + "/" + filter + "/PHOTOMETRY/" + BASE + ".all" + tag + ".cat")
    
        child = os.fork()
        if child:
            children.append(child)
        else:
    
            command = "rm /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.all.cat" % {'path':path, 'filter':filter}
            print command 
            os.system(command)
    
            if type == 'all':
    
                params = {'path':path, 
                          'filter_root': filter_root, 
                          'appendix_root':appendix_root,
                          'cluster':cluster, 
                          'filter':filter, 
                          'appendix':appendix, 
                          'PHOTCONF':PHOTCONF, 
                          'fwhm': seeing_worst, 
                          'BASE':BASE, 
                          'GAIN':float(fwhms[filter]['GAIN']),
                          'DATACONF':os.environ['DATACONF'], 
                          'tag':tag}
    
                if filter != filter_worst:
                    ''' convolve image -- no background subtraction -- high detection threshold -- no dual detection '''                 
                    command = "sex /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits -c %(PHOTCONF)s/phot.conf.sex \
                    -PARAMETERS_NAME %(PHOTCONF)s/phot.param.short.sex \
                    -CATALOG_NAME /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.all%(tag)s.cat \
                    -FILTER_NAME /%(path)s/%(filter)s/PHOTOMETRY/gauss.conv \
                    -FILTER  Y \
                    -SEEING_FWHM %(fwhm).3f \
                    -DETECT_MINAREA 3 -DETECT_THRESH 10000 -ANALYSIS_THRESH 10000 \
                    -MAG_ZEROPOINT 27.0 \
                    -FLAG_TYPE OR\
                    -FLAG_IMAGE /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits \
                    -GAIN %(GAIN).3f \
                    -CHECKIMAGE_NAME /%(path)s/%(filter)s/PHOTOMETRY/coadd.filtered.fits\
                    -CHECKIMAGE_TYPE FILTERED\
                    -BACK_TYPE MANUAL\
                    -BACK_VALUE 0.0\
                    -WEIGHT_IMAGE /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits \
                    -WEIGHT_TYPE MAP_WEIGHT" % params
                else: 
                    command = 'cp /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits /%(path)s/%(filter)s/PHOTOMETRY/coadd.filtered.fits' % params 
                
                print command
                print 'making filtered image'
                os.system(command)
    
                ''' detection images -- one flag image --- one filter -- detect on lensing band ''' 
                command = "sex /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix_root)s/coadd.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.filtered.fits -c %(PHOTCONF)s/phot.conf.sex \
                -PARAMETERS_NAME %(PHOTCONF)s/phot.param.short.sex \
                -CATALOG_NAME /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.all%(tag)s.cat \
                -FILTER_NAME %(DATACONF)s/default.conv \
                -FILTER  Y \
                -SEEING_FWHM %(fwhm).3f \
                -DETECT_MINAREA 3 -DETECT_THRESH 1.5 -ANALYSIS_THRESH 1.5 \
                -MAG_ZEROPOINT 27.0 \
                -FLAG_TYPE OR\
                -FLAG_IMAGE /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits \
                -GAIN %(GAIN).3f \
                -CHECKIMAGE_NAME /%(path)s/%(filter)s/PHOTOMETRY/coadd.background.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.apertures.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.segmentation.fits\
                -CHECKIMAGE_TYPE BACKGROUND,APERTURES,SEGMENTATION\
                -WEIGHT_IMAGE /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix_root)s/coadd.weight.fits,/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits \
                -WEIGHT_TYPE MAP_WEIGHT" % params
    
                print command
                print 'measuring filtered image'
                os.system(command)
    
                #command = "sex /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits,/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits -c %(PHOTCONF)s/phot.conf.sex \
                #-PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
                #-CATALOG_NAME /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.all%(tag)s.cat \
                #-DETECT_MINAREA 10 -DETECT_THRESH 10 -ANALYSIS_THRESH 10 \
                #-MAG_ZEROPOINT 27.0 \
                #-FLAG_TYPE MAX\
                #-FLAG_IMAGE '' \
                #-GAIN %(GAIN).3f \
                #-WEIGHT_IMAGE /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits,'' \
                #-WEIGHT_TYPE MAP_WEIGHT" % params
    
    
    
            elif type == 'each':                                                                                                                                                                                                                                         
                params = {'path':path, 'filter_root': filter_root, 'cluster':cluster, 'filter':filter, 'appendix':appendix, 'PHOTCONF':PHOTCONF, 'fwhm': seeing_worst, 'BASE':BASE, 'GAIN':float(fwhms[filter]['GAIN']),'DATACONF':os.environ['DATACONF'], 'tag':tag}
                                                                                                                                                                                                                                                                      
                command = "sex /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits -c %(PHOTCONF)s/phot.conf.sex \
                -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
                -CATALOG_NAME /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.each%(tag)s.cat \
                -FILTER_NAME %(DATACONF)s/default.conv \
                -FILTER  Y \
                -SEEING_FWHM %(fwhm).3f \
                -DETECT_MINAREA 3 -DETECT_THRESH 3 -ANALYSIS_THRESH 3 \
                -MAG_ZEROPOINT 27.0 \
                -FLAG_TYPE OR\
                -FLAG_IMAGE /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits \
                -GAIN %(GAIN).3f \
                -WEIGHT_IMAGE /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits \
                -WEIGHT_TYPE MAP_WEIGHT" % params
    
            elif type == 'arc':
    
                params = {'path':path, 'filter_root': filter_root, 'cluster':cluster, 'filter':filter, 'appendix':appendix, 'PHOTCONF':PHOTCONF, 'BASE':BASE, 'GAIN':float(fwhms[filter]['GAIN']),'DATACONF':os.environ['DATACONF'], 'tag':tag}
    
    
                #command = "sex /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits,/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits -c %(PHOTCONF)s/phot.conf.sex \
    
                commandA = "sex /%(path)s/%(filter_root)s/PHOTOMETRY/coadd.small.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.small.fits -c %(PHOTCONF)s/phot.conf.sex \
                -PHOT_APERTURES 70,100 \
                -BACK_SIZE 10 \
                -BACK_FILTERSIZE 2 \
                -BACKPHOTO_TYPE GLOBAL \
                -BACK_TYPE AUTO \
                -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
                -CATALOG_NAME /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.arc.all%(tag)s.cat \
                -FILTER_NAME %(DATACONF)s/default.conv,%(DATACONF)s/default.conv\
                -FILTER  Y \
                -DETECT_MINAREA 3 -DETECT_THRESH 0.5 -ANALYSIS_THRESH 0.5  \
                -MAG_ZEROPOINT 27.0 \
                -INTERP-TYPE NONE\
                -FLAG_TYPE MAX\
                -FLAG_IMAGE \"\"\
                -SATUR_LEVEL 30000.0  \
                -MAG_ZEROPOINT 27.0 \
                -GAIN %(GAIN).3f \
                -CHECKIMAGE_NAME /%(path)s/%(filter)s/PHOTOMETRY/coadd.arc.background.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.arc.apertures.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.arc.segmentation.fits\
                -CHECKIMAGE_TYPE BACKGROUND,APERTURES,SEGMENTATION\
                -WEIGHT_IMAGE /%(path)s/%(filter_root)s/PHOTOMETRY/coadd.weight.arc.small.fits,%(path)s/%(filter)s/PHOTOMETRY/coadd.weight.arc.small.fits\
                -WEIGHT_TYPE NONE" % params
    
                params['BACK_VALUE'] = 0
                if filter == 'W-J-V':
                    params['BACK_VALUE'] = -0.02
    
                commandB = "sex /%(path)s/%(filter_root)s/PHOTOMETRY/coadd_small.sub.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd_small.sub.fits -c %(PHOTCONF)s/phot.conf.sex \
                -PHOT_APERTURES 70,100 \
                -BACK_SIZE 64 \
                -BACK_FILTERSIZE 3 \
                -BACKPHOTO_TYPE GLOBAL \
                -BACK_TYPE MANUAL \
                -BACK_VALUE -0.02 \
                -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
                -CATALOG_NAME /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.arc.all%(tag)s.cat \
                -FILTER_NAME %(DATACONF)s/default.conv,%(DATACONF)s/default.conv\
                -FILTER  Y \
                -DETECT_MINAREA 3 -DETECT_THRESH 0.5 -ANALYSIS_THRESH 0.5  \
                -MAG_ZEROPOINT 27.0 \
                -INTERP-TYPE NONE\
                -FLAG_TYPE MAX\
                -FLAG_IMAGE \"\"\
                -SATUR_LEVEL 30000.0  \
                -MAG_ZEROPOINT 27.0 \
                -GAIN %(GAIN).3f \
                -CHECKIMAGE_NAME /%(path)s/%(filter)s/PHOTOMETRY/coadd.arc.apertures.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.arc.segmentation.fits\
                -CHECKIMAGE_TYPE APERTURES,SEGMENTATION\
                -WEIGHT_IMAGE /%(path)s/%(filter_root)s/PHOTOMETRY/coadd.weight.arc.small.fits,%(path)s/%(filter)s/PHOTOMETRY/coadd.weight.arc.small.fits\
                -WEIGHT_TYPE MAP_WEIGHT" % params
                    
                command = commandB
    
            #-WEIGHT_IMAGE /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits,%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits\
            print command
            filecommand.write(command + '\n')
            sys.exit(0)
    
        
    for child in children: 
        os.waitpid(child,0)
    
    print 'DONE!!!!'

def test_raw(OBJNAME):
    #!/usr/bin/env python
    import pyfits, sys, os, re, string
    from config_bonn import cluster, tag, arc, filters
    
    tables = {} 
    colset = 0
    cols = []
    for filter in filters: 
        file = '//nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/' + filter + '/PHOTOMETRY/' + filter + arc + '.all' + tag + '.cat'
        os.system('ldacconv -b 1 -c R -i ' + file + ' -o /tmp/' + filter + '.all.conv.alpha')
        os.system('ldactoasc -i /tmp/' + filter + '.all.conv.alpha -b -s -k MAG_APER MAGERR_APER -t OBJECTS > /tmp/' + filter + 'aper')
        os.system('asctoldac -i /tmp/' + filter + 'aper -o /tmp/cat1 -t OBJECTS -c ./photconf/MAG_APER.conf')
        os.system('ldacjoinkey -i /tmp/' + filter + '.all.conv.alpha -p /tmp/cat1 -o /tmp/' + filter + '.all.conv  -k MAG_APER1 MAG_APER2 MAGERR_APER1 MAGERR_APER2')
        tables[filter] = pyfits.open('/tmp/' + filter + '.all.conv')
        if filter == filters[0]:
            tables['notag'] = pyfits.open('/tmp/' + filter + '.all.conv')
    
    cols = [] 
    for i in range(len(tables['notag'][1].columns)): 
        cols.append(tables['notag'][1].columns[i])
    
    for filter in filters:
        for i in range(len(tables[filter][1].columns)): 
            tables[filter][1].columns[i].name = tables[filter][1].columns[i].name + '_' + filter    
            cols.append(tables[filter][1].columns[i])
    
    print cols
    print len(cols)
    hdu = pyfits.PrimaryHDU()
    hduIMHEAD = pyfits.new_table(tables['notag'][2].columns)
    hduOBJECTS = pyfits.new_table(cols) 
    hdulist = pyfits.HDUList([hdu])
    hdulist.append(hduIMHEAD)
    hdulist.append(hduOBJECTS)
    hdulist[1].header.update('EXTNAME','FIELDS')
    hdulist[2].header.update('EXTNAME','OBJECTS')
    dir = '//nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/PHOTOMETRY/'
    file = dir + 'all' + arc + '.cat'
    os.system('mkdir ' + dir)
    os.system('rm ' + file)
    print file
    hdulist.writeto(file)
    print 'done'
    import sys
    sys.exit(0)
    raw_input()
    table=hdulist[0].data
    
    
    from ppgplot import *
    
    #pgbeg("A2219colors.ps/cps",1,1)
    pgbeg("/XWINDOW",1,1)
    pgiden()
    
    from Numeric import *
    
    x = []
    y = []
    #for dict in output_list:
    
    #x = table.field('gmr')
    #y = table.field('imz')
    x = table.field('MAG_AUTO_W-J-V') - table.field('MAG_AUTO_W-C-RC')
    y = table.field('MAG_AUTO_W-C-IC') - table.field('MAG_AUTO_W-S-Z+')
    condition = []
    for m in range(len(table.field('CLASS_STAR_W-C-RC'))):
        if table.field('CLASS_STAR_W-C-RC')[m] > 0.98 and table.field('FLAGS_W-C-RC')[m] == 0:
            condition.append(1)
        else: condition.append(0)
    condition = array(condition)
    
    x_plot = compress(condition,x)
    y_plot = compress(condition,y)
    #print len(x_plot), len(x)
    #x = table.field('SEx_Xposz')
    #y = table.field('SEx_MAG_AUTO_z') - table.field('zmag')
    #print table.field('SEx_MAG_AUTO')
    #print table.field('Rmag')
    
    #x = table.field('SEx_Ra') - table.field('Ra')
    #x = table.field('SEx_X_WORLD_v') - table.field('SEx_ALPHA_J2000')
    #y = table.field('Ra')
    #print x
    
    
    #hdulist[2].columns[0].name = blah
    #t = t1[1].columns + t2[1].columns
    #hdu.writeto('newtable.fits')
    
    
    #if -50 < x_val < 50 and -50 < y_val < 50:
    #    x.append(x_val)        
    #    y.append(y_val)
    
    import copy 
    plotx = copy.copy(x_plot)
    ploty = copy.copy(y_plot)
    x.sort()    
    y.sort()
    #print plotx
    #print x[0], x[-1], y[0], y[-1]
    
    #pgswin(x[10]-0.5,x[-10]+0.5,y[10]-0.5,y[-10]+0.5)
    
    pgswin(-2,2,-2,2)
    plotx = array(plotx)
    ploty = array(ploty)
    #pylab.scatter(z,x)
    pglab('B-V','V-R','')
    pgbox()
    #print plotx, ploty
    pgsci(2)
    pgpt(plotx,ploty,1)
    pgend()
