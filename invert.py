def fix_radec(SUPA,FLAT_TYPE):
    NUMS = []
    at_least_one = False 
    print dict['file']
    for image in dict['files']:
        params = copy(search_params)     
        ROOT = re.split('\.',re.split('\/',image)[-1])[0]
        params['ROOT'] = ROOT
        BASE = re.split('O',ROOT)[0]
        params['BASE'] = BASE 
        NUM = re.split('O',re.split('\_',ROOT)[1])[0]
        params['NUM'] = NUM
        print NUM, BASE, ROOT, image
        params['GAIN'] = 2.50 ## WARNING!!!!!!
        print ROOT
        finalflagim = "%(TEMPDIR)sflag_%(ROOT)s.fits" % params     
        res = re.split('SCIENCE',image)
        res = re.split('/',res[0])
        if res[-1]=='':res = res[:-1]
        params['path'] = reduce(lambda x,y:x+'/'+y,res[:-1])
        params['fil_directory'] = res[-1]
        print params['fil_directory']
        res = re.split('_',res[-1])
    
        ''' if three second exposure, use the headers in the directory '''
        if string.find(dict['fil_directory'],'CALIB') != -1:
            params['directory'] = params['fil_directory'] 
        else: 
            params['directory'] = res[0]


        print params['directory']
        print BASE
        SDSS = "/%(path)s/%(directory)s/SCIENCE/headers_scamp_SDSS-R6/%(BASE)s.head" % params   # it's not a ZERO!!!
        TWOMASS = "/%(path)s/%(directory)s/SCIENCE/headers_scamp_2MASS/%(BASE)s.head" % params
        NOMAD = "/%(path)s/%(directory)s/SCIENCE/headers_scamp_NOMAD*/%(BASE)s.head" % params

        SDSS = SDSS.replace('I_','_').replace('I.','.')
                                                                                                     
        from glob import glob 
        print SDSS
        print SDSS, TWOMASS, NOMAD
        print glob(SDSS), glob(TWOMASS), glob(NOMAD)
        head = None
        heads = []
        if len(glob(TWOMASS)) > 0:
            heads.append(glob(TWOMASS)[0])
        if len(glob(TWOMASS.replace('.head','O*.head'))) > 0:
            heads.append(glob(TWOMASS.replace('.head','O*.head'))[0])
        if len(glob(NOMAD)) > 0:
            heads.append(glob(NOMAD)[0])
        if len(glob(NOMAD.replace('.head','O*.head'))) > 0:
            heads.append(glob(NOMAD.replace('.head','O*.head'))[0])

        print heads


        ''' pick out latest SCAMP solution not SDSS '''
        if len(heads) > 0:
            a = [[os.stat(f).st_mtime,f] for f in heads ]
            a.sort()
            print a 
            head = a[-1][1]
            print head 
       
        ''' if SDSS exists, use that '''
        if len(glob(SDSS)) > 0:
            head = glob(SDSS)[0]
        if len(glob(SDSS.replace('.head','O*.head'))) > 0:
            head = glob(SDSS.replace('.head','O*.head'))[0]

        print head, SDSS, glob(SDSS)


        #else:
        #    raise Exception



        print head, SDSS
          
        w = {}

        if head is not None:
            keys = []
            hf = open(head,'r').readlines()                                                                    
            print head
            for line in hf:
                at_least_one = True
                import re
                if string.find(line,'=') != -1:
                    res = re.split('=',line)
                    name = res[0].replace(' ','')
                    res = re.split('/',res[1])
                    value = res[0].replace(' ','')
                    print name, value
                    if string.find(name,'CD')!=-1 or string.find(name,'PV')!=-1 or string.find(name,'CR')!=-1 or string.find(name,'NAXIS') != -1:
                        w[name] = float(value)
                        print line, w[name]
                        keys.append(name)
        from copy import copy
        chips[NUM] = copy(w)
        print w 
        NUMS.append(NUM)

    if at_least_one:

        chip_dict = length_swarp(SUPA,FLAT_TYPE,chips)                                                                                                                                          
        vecs = {}        
        for key in keys:
            vecs[key] = []
        vecs['good_scamp'] = []
        
        try:
            hdu= pyfits.open(search_params['pasted_cat']) 
            print search_params['pasted_cat']
            table = hdu['OBJECTS'].data 
        except:
            import calc_tmpsave
            calc_tmpsave.sextract(search_params['SUPA'],search_params['FLAT_TYPE'])

            hdu= pyfits.open(search_params['pasted_cat'])                 
            print search_params['pasted_cat']
            table = hdu['OBJECTS'].data 

        print type(table)

        if str(type(table)) == "<type 'NoneType'>":

            save_exposure({'fixradecCR':-2},SUPA,FLAT_TYPE)
            return -2 

        else:

        
            CHIP = table.field('CHIP')                                                                                                                                                                     
            print keys                                                                                                                                                                                    
            print chips.keys()
            for k in chips.keys():
                print chips[k].has_key('CRVAL1'), k
            print keys
            for i in range(len(CHIP)):
                NUM = str(int(CHIP[i]))
                good = False
                for key in keys:
                    if chips[NUM].has_key(key):
                        good = True
                        vecs[key].append(float(chips[NUM][key]))
                    else:
                        vecs[key].append(-1.)
                if good:
                    vecs['good_scamp'].append(1)
                else:
                    vecs['good_scamp'].append(0)
                                                                                                                                                                                                           
            print vecs['good_scamp']
                                                                                                                                                                                                           
                                                                                                                                                                                                           
            print vecs.keys()
            import scipy
            for key in vecs.keys():
                vecs[key] = scipy.array(vecs[key])
                print vecs[key][0:20], key
                                                                                                                                                                                        
            ra_cat = table.field('ALPHA_J2000')
            dec_cat = table.field('DELTA_J2000')
            
            x0 = (table.field('Xpos') - vecs['CRPIX1'])
            y0 = (table.field('Ypos') - vecs['CRPIX2'])
                                                                                                                                                                                                           
                                                                                                                                                                                                           
            x0_ABS = (table.field('Xpos') + chip_dict['CRPIX1ZERO'] - vecs['CRPIX1'])
            y0_ABS = (table.field('Ypos') + chip_dict['CRPIX2ZERO'] - vecs['CRPIX2'])
                                                                                                                                                                                                           
                                                                                                                                                                                        
            x = x0*vecs['CD1_1'] + y0*vecs['CD1_2']
            y = x0*vecs['CD2_1'] + y0*vecs['CD2_2']
                                                                                                                                                                                        
            r = (x**2. + y**2.)**0.5
                                                                                                                                                                                        
            xi_terms = {'PV1_0':scipy.ones(len(x)),'PV1_1':x,'PV1_2':y,'PV1_3':r,'PV1_4':x**2.,'PV1_5':x*y,'PV1_6':y**2.,'PV1_7':x**3.,'PV1_8':x**2.*y,'PV1_9':x*y**2.,'PV1_10':y**3.}
                                                                                                                                                                                        
            pv1_keys = filter(lambda x: string.find(x,'PV1') != -1, vecs.keys())
            print 'pv1_keys', pv1_keys
            xi = reduce(lambda x,y: x + y, [xi_terms[k]*vecs[k] for k in pv1_keys])
                                                                                                                                                                                        
            eta_terms = {'PV2_0':scipy.ones(len(x)),'PV2_1':y,'PV2_2':x,'PV2_3':r,'PV2_4':y**2.,'PV2_5':y*x,'PV2_6':x**2.,'PV2_7':y**3.,'PV2_8':y**2.*x,'PV2_9':y*x**2.,'PV2_10':x**3.}
                                                                                                                                                                                        
            pv2_keys = filter(lambda x: string.find(x,'PV2') != -1, vecs.keys())
            print 'pv2_keys', pv2_keys
            eta = reduce(lambda x,y: x + y, [eta_terms[k]*vecs[k] for k in pv2_keys])
                                                                                                                                                                                        
            print xi[0:10],eta[0:10], len(eta)
            print vecs.keys(), vecs['CD1_1'][0],vecs['CD1_2'][0],vecs['CD2_2'][0],vecs['CD2_1'][0]
            import math
                                                                                                                                                                                        
            ra_out = []
            dec_out = []
            os.system('mkdir -p ' + tmpdir)
            cat = open(tmpdir + '/' + BASE + 'cat','w')
            for i in range(len(xi)):
                XI = xi[i] / 180.0   * math.pi                                                     
                ETA = eta[i] / 180.0 * math.pi
                CRVAL1 = vecs['CRVAL1'][i]/180.0* math.pi
                CRVAL2 = vecs['CRVAL2'][i]/180.0 * math.pi
                p = math.sqrt(XI**2. + ETA**2.) 
                c = math.atan(p)
                                                                             
                a = CRVAL1 + math.atan((XI*math.sin(c))/(p*math.cos(CRVAL2)*math.cos(c) - ETA*math.sin(CRVAL2)*math.sin(c)))
                d = math.asin(math.cos(c)*math.sin(CRVAL2) + ETA*math.sin(c)*math.cos(CRVAL2)/p)
                                                                                                                                                                                        
                ra = a*180.0/math.pi
                dec = d*180.0/math.pi
                if i % 100== 0:
                    print 'ra_cat','dec_cat',ra,ra_cat[i], dec, dec_cat[i]    
                    print (ra-ra_cat[i])*3600.,(dec-dec_cat[i])*3600.
                ''' if no solution, give a -999 value '''
                if vecs['good_scamp'][i] != 1: 
                    import random
                    ra = -999  - 200*random.random()
                    dec = -999  - 200*random.random()          
                ra_out.append(ra)
                dec_out.append(dec)
                cat.write(str(ra) + ' ' + str(dec) + '\n')
                #cat.write(str(ra[i]) + ' ' + str(dec[i]) + '\n')
            cat.close()
            import random
            index = int(random.random()*4)
            colour = ['red','blue','green','yellow'][index]
            rad = [1,2,3,4][index]
            #os.system(' mkreg.pl -xcol 0 -ycol 1 -c -rad ' + str(rad) + ' -wcs -colour ' + colour + ' ' + BASE + 'cat')
                                                                                                                                                                                        
            hdu[2].data.field('Xpos_ABS')[:] = scipy.array(x0_ABS)
            hdu[2].data.field('Ypos_ABS')[:] = scipy.array(y0_ABS)
            hdu[2].data.field('ALPHA_J2000')[:] = scipy.array(ra_out)
            hdu[2].data.field('DELTA_J2000')[:] = scipy.array(dec_out)
            table = hdu[2].data 
                                                                                                                                                                                        
            print 'BREAK'
            print ra_out[0:10], table.field('ALPHA_J2000')[0:10]
            print 'BREAK'
            print dec_out[0:10], table.field('DELTA_J2000')[0:10]
            print SUPA, search_params['pasted_cat']
                                                                                                                                                                                        
            os.system('rm ' + search_params['pasted_cat'])
            hdu.writeto(search_params['pasted_cat'])
                                                                                                                                                                                                           
            save_exposure({'fixradecCR':1},SUPA,FLAT_TYPE)
            return 1 
    
    else: 
        save_exposure({'fixradecCR':-1},SUPA,FLAT_TYPE)
        return -1 
