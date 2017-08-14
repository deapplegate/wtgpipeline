def run(command):
        print command
        os.system(command)

def select_background(flag_file,poly_file,out_flag_file):

        import tempfile
        f0 = tempfile.NamedTemporaryFile(dir='/tmp/',suffix='.fits').name 
        f1 = tempfile.NamedTemporaryFile(dir='/tmp/',suffix='.fits').name 



        os.system('rm ' + f0)
        os.system('rm ' + f1)
        import pyraf
        from pyraf import iraf
        pyraf.iraf.imarith(flag_file,'*',0,f0,pixtype="integer")
        pyraf.iraf.imarith(f0,'+',1,f1,pixtype="integer")
        cf = open('config_file','w')   
        cf.write('WEIGHT_NAMES ""\n')
        #cf.write('WEIGHT_NAMES /tmp/flag0.fits\n')
        cf.write("WEIGHT_MIN -99999\n")   
        cf.write("WEIGHT_MAX 99999\n")
        cf.write("WEIGHT_OUTFLAGS 0\n")
        cf.write('FLAG_NAMES ""\n')
        cf.write("POLY_NAMES " + poly_file + "\n")
        cf.write("POLY_OUTFLAGS 1\n")
        #cf.write("POLY_OUTWEIGHTS 1.0\n")
        cf.write('FLAG_NAMES ' + f1 + '\n')
        cf.write("FLAG_MASKS 0x07\n")
        cf.write("FLAG_WMASKS 0x0\n")
        cf.write("FLAG_OUTFLAGS 1,2,4\n")
        cf.write("OUTWEIGHT_NAME " + out_flag_file + "\n")
        cf.write("OUTFLAG_NAME /dev/null\n")
        cf.close()
        run("ww_theli -c config_file")            

        os.system('rm ' + f0)
        os.system('rm ' + f1)


def calc_stats(image_small, flag_small, poly_file):
        import tempfile
        out_flag_file = tempfile.NamedTemporaryFile(dir='/tmp/',suffix='.fits').name 

        select_background(flag_small,poly_file,out_flag_file)

        print out_flag_file
        raw_input()
        
        import pyfits, os 
        
        #rawim = pyfits.open(out_flag_file)
        #os.system('rm ' + out_flag_file)

        #flag = -1 * (rawim[0].data - 1)

        print image_small
        
        rawim = pyfits.open(image_small)
        image = rawim[0].data

        f_test = open(poly_file,'r').read()
        import string
        if string.find(f_test,'image') == -1 and string.find(f_test,'physical') == -1:
            print 'wrong coordinates?', poly_file
            raw_input()



        def get_stat(boxes):
            bgpix = [] 
            for b in boxes:
                a = image[b['left'][1]:b['right'][1],b['left'][0]:b['right'][0]]
                print b['left'][1],b['right'][1],b['left'][0],b['right'][0]
                bgpix += a.flatten().tolist()
            bgpix = scipy.array(bgpix)
            print bgpix
            ''' do not include zero value pixels ''' 
            nonzerobg = bgpix[bgpix != 0]  #bgpix[bgpix != 0] #bgpix[bgpix != 0] #bgpix[bgpix != 0] #bgpix[bgpix != 0] #bgpix[bgpix != 0] #bgpix[bgpix != 0] #bgpix[bgpix != 0] #bgpix[bgpix != 0] #scipy.extract((bgpix!=0),bgpix) - 1000
            nonzerobg = nonzerobg[nonzerobg !=0] 
            mdn = scipy.median(nonzerobg)
            std = nonzerobg.std()
            mean = scipy.mean(nonzerobg) 
            sum = scipy.sum(nonzerobg)
            print "mdn", mdn, "std", std, "mean", mean, "sum", sum
            return {'median': mdn, 'std':std, 'mean': mean, 'sum':sum}

        import scipy
        f = open(poly_file,'r').readlines()
        boxes = []
        for l in f:
            import string
            if string.find(l,'polygon') != -1:
                l = l.replace('polygon(','').replace(')','').replace('\n','')
                print l
                import re
                res = re.split('\,',l)
                p = [float(a) for a in res]
                print p
                if len(p) > 6:
                    xs = sorted([p[0],p[2],p[4],p[6]])                                                                           
                    ys = sorted([p[1],p[3],p[5],p[7]])
                    print xs, ys
                    
                    boxes.append({'left':[max(0,int(xs[0])),max(0,int(ys[0]))],'right':[max(0,int(xs[-1])),max(0,int(ys[-1]))]})

        list = []
        for each in boxes:
            dict = get_stat([each])
            
            list.append([dict['median'],each]) 

        list.sort()
        print list

        if len(list) > 1: list = list[:-1]

        out = get_stat([x[1] for x in list])

        print out            
        return out
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


def measure(snpath,gh,regfile,colors=['u','g','r','i','z']):
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

        bg = calc_stats(image_file,flag_file,poly_file)

        print bg
