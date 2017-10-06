def run(command):
        print command
        os.system(command)

def select_background(filt, out_flag_file):

        import tempfile
        
        



        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

        
        

        
        

        path = os.environ['sne'] + '/arc/' 
        path = '/nfs/slac/g/ki/ki06/anja/SUBARU/arc/'
        command = '/afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/ww_theli -c   /afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/conf/reduction/weights.ww -WEIGHT_NAMES ' + path + '2arcmin_' + filt + '.weight.fits -WEIGHT_MIN -1e9 -WEIGHT_MAX 1e9 -WEIGHT_OUTFLAGS 0 -FLAG_NAMES "" -POLY_NAMES ' + path + 'reg/arc_C1.reg -POLY_OUTFLAGS 1 -OUTWEIGHT_NAME test.fits -OUTFLAG_NAME '  + out_flag_file

        print command

        run(command)









def calc_stats(image_small, flag_small, poly_file,filt):
        import tempfile
        out_flag_file = tempfile.NamedTemporaryFile(dir='/tmp/',suffix='.fits').name 

        select_background(filt,out_flag_file)

        print out_flag_file
        
        import astropy.io.fits as pyfits, os 
        
        rawim = pyfits.open(out_flag_file)
        os.system('rm ' + out_flag_file)

        flag = (rawim[0].data )
        
        rawim = pyfits.open(image_small)
        image = rawim[0].data

        print flag.shape, image.shape
        
        bgpix = flag * (image )

        import astropy.io.fits as pyfits, os
        fitsobj = pyfits.HDUList()
        hdu = pyfits.PrimaryHDU()
        hdu.data = bgpix
        fitsobj.append(hdu)
        os.system('rm test.fits')
        fitsobj.writeto('test.fits')
         



        
        import numpy
       
        ''' do not include zero value pixels ''' 
        nonzerobg = bgpix[bgpix != 0] #- 1000 #bgpix[bgpix != 0] #bgpix[bgpix != 0] #bgpix[bgpix != 0] #bgpix[bgpix != 0] #bgpix[bgpix != 0] #bgpix[bgpix != 0] #bgpix[bgpix != 0] #bgpix[bgpix != 0] #numpy.extract((bgpix!=0),bgpix) - 1000
        nonzerobg = nonzerobg[nonzerobg !=0] 
        mdn = numpy.median(nonzerobg)
        std = nonzerobg.std()
        mean = numpy.mean(nonzerobg) 
        sum = numpy.sum(nonzerobg)
        
        print "mdn", mdn, "std", std, "mean", mean, "sum", sum

        raw_input()
        
        sum_flag = numpy.sum(numpy.extract((flag!=-9999),flag))
        
        print "number of pixels", sum_flag

        return {'median': mdn, 'std':std, 'mean': mean, 'pix': sum_flag, 'sum':sum}


def measure(snpath,gh,regfile):
    import os
    rec = open('recall','w')
    appendix = '' 
    #for snpath in ['sn2007bc']:
    if 1:
        letter = snpath[2:]
        obj_poly = 'reg' + letter + 'all.reg' #'M2243_obj_W-J-V.reg'
        bg_poly = regfile #'reg' + letter + 'bg.reg' #'M2243_W-J-V.reg'
        ALPHA_J2000 = 340.82489
        DELTA_J2000 = -9.59580
        
        colors = ['u','g','r','i','z']
        
        # need UPPER CASE POLYGON in reg file
        
        obj_meas = {} 
        for color in colors:
            path= os.environ['sdss'] + '/' +  snpath + '/' + color + '/'
            params = {'path':path, 'snpath':snpath, 'filter':filter, 'appendix':appendix}                       
            #image_file = "/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits" % params
            #weight_file = "/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits" % params
            #flag_file = "/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits" % params
            
            ''' make small versions of image + weight files '''
            image_small = path + 'reg' + color + '.fits' #"/nfs/slac/g/ki/ki05/anja/proposals/chandra_ao11/hi-z_cluster/lenstool/image.fits" #/%(path)s/%(filter)s/PHOTOMETRY/coadd_small.fits" % params
            #run('rm ' + image_small + '; makesubimage -500 -500 1000 1000 -c < ' + image_file + ' > ' + image_small)
            
            #weight_small = "/%(path)s/%(filter)s/PHOTOMETRY/coadd_small.weight.fits" % params
            #run('rm ' + weight_small + '; makesubimage -500 -500 1000 1000 -c < ' + weight_file + ' > ' + weight_small)
            
            flag_small =  path + 'reg' + color + '.fits' #'"a.fits"' #"/%(path)s/%(filter)s/PHOTOMETRY/coadd_small.flag.fits" % params
            #run('rm ' + flag_small + '; makesubimage -500 -500 1000 1000 -c < ' + flag_file + ' > ' + flag_small)
    
            for f in [bg_poly]:
                a = open(f,'r').read().replace('POLYGON','polygon') 
                b = open(f,'w')
                b.write(a)
                b.close()
    
            #obj = calc_stats(image_small,flag_small,obj_poly)
            bg = calc_stats(image_small,flag_small,bg_poly)
            if gh.has_key('median_bg' + color):
                print gh['median_bg' + color], 'old' 
            gh['median_bg' + color] = str(bg['median'])

            print 'median', gh['median_bg' + color], color

    gh['median1'] = 'yes'


import os, anydbm, sys












def run_back(sn):
    print sn

    gh = anydbm.open(sn,'c')
    for color,low,high in [['i',1010,1350]]: #['u',-10,50],,['r',-10,150],['i',-10,150],['z',-10,50]]: #['g',1050,2000]]: #['z',1120,1250]]: #]: #,['z',1120,1250],['H',0,30]]: #'u','g','r']:['u',1010,1250],

        import glob
        regfile = path + '/' + sn + '/bg.reg'
        measure(sn,gh,regfile)
        if 0: 
            command = 'xpaset -p ds9 file medatacube ' + path + '/' + sn + '/' + color + '/reg' + color + '.fits' 
            #command = 'xpaset -p ds9 file  ' + path + '/' + sn + '/' + color + '/reg' + color + '.fits'
            print command
            os.system(command) 

            if len(glob.glob(regfile)) == 0:
                command = 'xpaset -p ds9 regions load default.reg'
            else:
                command = 'xpaset -p ds9 regions load ' + regfile
            #command = 'xpaset -p ds9 file  ' + path + '/' + sn + '/' + color + '/reg' + color + '.fits'
            print command
            os.system(command) 
            p = raw_input()
            if len(p):
                if p[0] == 'b': gh['big'] = 'yes'
                                                                                                                  
            command = 'xpaset -p ds9 regions save  ' + regfile
            #command = 'xpaset -p ds9 file  ' + path + '/' + sn + '/' + color + '/reg' + color + '.fits'
            print command
            os.system(command) 
            print 'saving region'
            gh['saved_region'] = 'yes'

            
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

        flag_file = "%(path)s/flagzero.fits" % params

        input_flag_file = "%(path)s/flag.fits" % params

        print image_file, flag_file


        bg = calc_stats(image_file,flag_file,poly_file,filter)

        print bg
