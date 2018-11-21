#./parallel_manager.sh ./create_skysub_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ".sub" TWOPASS
global tmpdir
import os
#os.system('mkdir -p ' + tmpdir)
astrom = 'solve-field'
import traceback, tempfile

def variance(data,err):

    d = 0
    w = 0

    for i in range(len(data)):
        w += 1/err[i]**2.
        d += data[i]/err[i]**2.

    mean = d/w

    w = 0
    d = 0
    for i in range(len(data)):
        w += 1/err[i]**2.
        d += 1/err[i]**2.*(data[i] - mean)**2.

    weight_variance = d/w    
    import scipy
    variance = scipy.var(data)

    n = 0
    d = 0
    for i in range(len(data)):
        n += 1.
        d += 1/err[i]*abs(data[i] - mean)

    redchi = d/n

    return variance, weight_variance, redchi


def random_cmp(x,y):
    import random
    a = random.random()
    b = random.random()
    if a > b: return 1
    else: return -1

def starStats(supas):
    dict = {} 
    dict['rot'] = 0
    dict['sdss'] = 0
    dict['sdss_exists'] = 0
    for s in supas:
        if s['sdss']: dict['sdss'] += 1
        if s['sdss_exists']: dict['sdss_exists'] += 1
        s = s['supa files']
        rot1 = 0
        rot0 = 0
        rot2 = 0
        for ele in s:
            if not dict.has_key(ele['name']):
                dict[ele['name']] = 0 
            dict[ele['name']] += 1
            if ele['rotation'] == '1':rot1 = 1
            if ele['rotation'] == '0':rot0 = 1
            if ele['rotation'] == '2':rot2 = 1
        if rot0 + rot1 + rot2 > 1:
            dict['rot'] += 1
            
    #print dict['rot'], 'rot'
    for key in dict.keys():
        print key, dict[key]

    return dict


def length_swarp(SUPA,FLAT_TYPE,CHIPS):
    import os, re, utilities, bashreader, sys, string
    from copy import copy
    from glob import glob
    dict = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':search_params['OBJNAME']}

    all_chip_dict = {}
    NUMScommas = reduce(lambda x,y: str(x) + ',' + str(y),CHIPS.keys())
    all_chip_dict['CHIPS'] = NUMScommas

    print sorted(CHIPS.keys())
    NUMS = []
    start = 1
    crpix1s = []
    crpix2s = []
    for CHIP in CHIPS.keys():
        NUMS.append(CHIP)        
        

        if len(CHIPS[CHIP]) == 0:
            print CHIP
        if len(CHIPS[CHIP]) > 0:

            crpix = CHIPS[CHIP] 
            import re                                                                                                                               
            p = re.compile('\_\d+O')
            file = p.sub('_' + str(CHIP) + 'O',search_params['file'])
            print file, CHIP
            
            naxis = utilities.get_header_kw(file,['NAXIS1','NAXIS2'])
            print naxis, CHIP
            
            for kw in ['NAXIS1','NAXIS2']:
                crpix[kw] = float(naxis[kw])
                print naxis[kw]
            print file
            
            if start == 1:
                crpixzero = copy(crpix)
                crpixhigh = copy(crpix)
                start = 0
            from copy import copy 
            print  float(crpix['CRPIX1'])  < float(crpixzero['CRPIX1']), float(crpix['CRPIX2'])  < float(crpixzero['CRPIX2'])
            if float(crpix['CRPIX1']) + 0   >= float(crpixzero['CRPIX1']):
                crpixzero['CRPIX1'] = copy(crpix['CRPIX1'])
            if float(crpix['CRPIX2'])  + 0 >= float(crpixzero['CRPIX2']):
                crpixzero['CRPIX2'] = copy(crpix['CRPIX2'])
                                                                                                                              
            if float(crpix['CRPIX1']) - 0  <= float(crpixhigh['CRPIX1']):
                crpixhigh['CRPIX1'] = copy(crpix['CRPIX1'])
            if float(crpix['CRPIX2']) - 0  <= float(crpixhigh['CRPIX2']):
                crpixhigh['CRPIX2'] = copy(crpix['CRPIX2'])
            
            crpix1s.append(copy(crpix['CRPIX1']))
            crpix2s.append(copy(crpix['CRPIX2']))
                                                                                                                                                   
            print crpix['CRPIX1'], crpix['CRPIX2'], crpixzero['CRPIX1'], crpixzero['CRPIX2'], crpixhigh['CRPIX1'], crpixhigh['CRPIX2']#, crpixhigh
            print crpix.keys()
            for kw in ['CRPIX1','CRPIX2','CRVAL1','CRVAL2','NAXIS1','NAXIS2']:
                all_chip_dict[kw+ '_' + str(CHIP)] = crpix[kw]


    #plot_chips(crpix1s,crpix2s)
    for i in range(len(crpix1s)): 
        print crpix1s[i],crpix2s[i], NUMS[i] 
    crpix1s.sort()
    crpix2s.sort()

    print len(crpix1s), crpix1s, crpix2s, crpix1s[-1] - crpix1s[0] + crpix['NAXIS1'], crpix2s[-1] - crpix2s[0] + crpix['NAXIS2']

    print all_chip_dict                                                                                                                                                                                    
    
    LENGTH1 =  abs(float(crpixhigh['CRPIX1']) - float(crpixzero['CRPIX1'])) + float(crpix['NAXIS1'])
    LENGTH2 =  abs(float(crpixhigh['CRPIX2']) - float(crpixzero['CRPIX2'])) + float(crpix['NAXIS2']) 
    
    print LENGTH1, LENGTH2, crpixzero['CRPIX1'], crpixzero['CRPIX2'], crpixhigh['CRPIX1'], crpixhigh['CRPIX2']#, crpixhigh   
    all_chip_dict.update({'crfixednew':'third','LENGTH1':LENGTH1,'LENGTH2':LENGTH2,'CRPIX1ZERO':crpixzero['CRPIX1'],'CRPIX2ZERO':crpixzero['CRPIX2'],'CRVAL1':crpix['CRVAL1'],'CRVAL2':crpix['CRVAL2']})     
    save_exposure(all_chip_dict,SUPA,FLAT_TYPE)                                                                                                                                                           
    return all_chip_dict

def fix_radec(SUPA,FLAT_TYPE):
    #cats = [{'im_type': 'DOMEFLAT', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.DOMEFLAT.fixwcs.rawconv'}, {'im_type': 'SKYFLAT', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.SKYFLAT.fixwcs.rawconv'}, {'im_type': 'OCIMAGE', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.OCIMAGE.fixwcs.rawconv'}] 
    #outfile = '' + search_params['TEMPDIR'] + 'stub'
    #cats = [{'im_type': 'MAIN', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS..fixwcs.rawconv'}, {'im_type': 'D', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.D.fixwcs.rawconv'}]

    import astropy, astropy.io.fits as pyfits, sys, os, re, string, copy
    from config_bonn import cluster, tag, arc, filters
    ppid = str(os.getppid())

    #chips = length(SUPA,FLAT_TYPE)

    #import time
    #time.sleep(2)

    dict = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':search_params['OBJNAME']}

    from copy import copy
    chips = {}
    NUMS = []
    at_least_one = False 
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
        res = re.split('_',res[-1])
        params['directory'] = res[0]

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
        
        hdu= pyfits.open(search_params['pasted_cat'])
        
        table = hdu[2].data 
        
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
        cat = open(BASE + 'cat','w')
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
        os.system(' mkreg.pl -xcol 0 -ycol 1 -c -rad ' + str(rad) + ' -wcs -colour ' + colour + ' ' + BASE + 'cat')
                                                                                                                                                                                    
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
        return 'fixed'
    
    else: 

        save_exposure({'fixradecCR':-1},SUPA,FLAT_TYPE)
        return 'noheader'


def mk_tab(list):
    import astropy, astropy.io.fits as pyfits
    from pyfits import Column        
    import numarray 
    cols = []
    for ele in list:
        array = ele[0]
        name = ele[1]
        vec = numarray.array(array)                    
        cols.append(Column(name=name,format='1E',array=array))
    coldefs = pyfits.ColDefs(cols)
    hdu = pyfits.BinTableHDU.from_columns(coldefs)
    return hdu

def merge(t1,t2):
    import astropy, astropy.io.fits as pyfits
    t = t1.columns + t2[1].columns
    hdu = pyfits.BinTableHDU.from_columns(t)
    return hdu

def cutout(infile,mag,color='red'):
    import os, utilities
    ppid = str(os.getppid())

    print ppid + 'a'

    #pylab.show()                 

    outfile = raw_input('name of output file?')

    color = raw_input('color of regions?')

    limits = ['lower_mag','upper_mag','lower_diff','upper_diff']
    lim_dict = {}
    for lim in limits:
        print lim + '?'
        b = raw_input()
        lim_dict[lim] = b

    utilities.run('ldacfilter -i ' + infile + ' -t PSSC\
                    -c "(((SEx_' + mag + '>' + str(lim_dict['lower_mag']) + ') AND (SEx_' + mag + '<' + str(lim_dict['upper_mag']) + ')) AND (magdiff>' + str(lim_dict['lower_diff']) + ')) AND (magdiff<' + str(lim_dict['upper_diff']) + ');"\
                    -o cutout1.' + ppid,['cutout1.' + ppid])
    utilities.run('ldactoasc -b -q -i cutout1.' + ppid + '  -t PSSC\
            -k Ra Dec > ' + tmpdir + outfile,[outfile])
    utilities.run('mkreg.pl -c -rad 8 -xcol 0 -ycol 1 -wcs -colour ' + color + ' ' + tmpdir +  +  outfile)

def get_median(cat,key):
    import astropy, astropy.io.fits as pyfits, sys, os, re, string, copy

    p = pyfits.open(cat)
    magdiff = p[1].data.field(key)
    magdiff.sort()

    return magdiff[int(len(magdiff)/2)] 

def coordinate_limits(cat):
    import astropy, astropy.io.fits as pyfits, sys, os, re, string, copy

    p = pyfits.open(cat)

    good_entries = p[2].data

    if 1:
        mask = abs(good_entries.field('ALPHA_J2000')) > 0.0001  
        good_entries = good_entries[mask] 
        mask = abs(good_entries.field('ALPHA_J2000')) <  400 
        good_entries = good_entries[mask]
        mask = abs(good_entries.field('DELTA_J2000')) > 0.0001
        good_entries = good_entries[mask]
        mask = abs(good_entries.field('DELTA_J2000')) < 300 
        good_entries = good_entries[mask]
        mask = 100000 > abs(good_entries.field('Xpos')) 
        good_entries = good_entries[mask]
        mask = abs(good_entries.field('Xpos')) > 0.00001 
        good_entries = good_entries[mask]
        mask = 100000 > abs(good_entries.field('Ypos')) 
        good_entries = good_entries[mask]
        mask = abs(good_entries.field('Ypos')) > 0.00001 
        good_entries = good_entries[mask]
    
    ra = good_entries.field('ALPHA_J2000')
    ra.sort()
    dec = good_entries.field('DELTA_J2000')
    dec.sort()

    print cat, 'cat'

    print ra[:100]
    print dec[:100]

    print ra[-100:]
    print dec[-100:]
    return ra[0],ra[-1],dec[0],dec[-1]

def combine_cats(cats,outfile,search_params):
    #cats = [{'im_type': 'DOMEFLAT', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.DOMEFLAT.fixwcs.rawconv'}, {'im_type': 'SKYFLAT', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.SKYFLAT.fixwcs.rawconv'}, {'im_type': 'OCIMAGE', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.OCIMAGE.fixwcs.rawconv'}] 
    #outfile = '' + search_params['TEMPDIR'] + 'stub'
    #cats = [{'im_type': 'MAIN', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS..fixwcs.rawconv'}, {'im_type': 'D', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.D.fixwcs.rawconv'}]

    import astropy, astropy.io.fits as pyfits, sys, os, re, string, copy
    from config_bonn import cluster, tag, arc, filters
    ppid = str(os.getppid())


    tables = {} 
    colset = 0
    cols = []
    for catalog in cats: 
        file = catalog['cat'] 
        os.system('mkdir ' + search_params['TEMPDIR'] )
        aper = tempfile.NamedTemporaryFile(dir=search_params['TEMPDIR']).name
        os.system('ldactoasc -i ' + catalog['cat'] + ' -b -s -k MAG_APER MAGERR_APER -t OBJECTS > ' + aper)
        cat1 = tempfile.NamedTemporaryFile(dir=search_params['TEMPDIR']).name
        os.system('asctoldac -i ' + aper + ' -o ' + cat1 + ' -t OBJECTS -c ' + os.environ['bonn'] + '/photconf/MAG_APER.conf')
        allconv = tempfile.NamedTemporaryFile(dir=search_params['TEMPDIR']).name
        os.system('ldacjoinkey -i ' + catalog['cat'] + ' -p ' + cat1 + ' -o ' + allconv + '  -k MAG_APER1 MAG_APER2 MAGERR_APER1 MAGERR_APER2')
        tables[catalog['im_type']] = pyfits.open(allconv)
        #if filter == filters[0]:
        #    tables['notag'] = pyfits.open('' + search_params['TEMPDIR'] + 'all.conv' )
    
    for catalog in cats:
        for i in range(len(tables[catalog['im_type']][1].columns)): 
            print catalog['im_type'], catalog['cat']
            if catalog['im_type'] != '':
                tables[catalog['im_type']][1].columns[i].name = tables[catalog['im_type']][1].columns[i].name + catalog['im_type'] 
            else:
                tables[catalog['im_type']][1].columns[i].name = tables[catalog['im_type']][1].columns[i].name
            cols.append(tables[catalog['im_type']][1].columns[i])
    
    print cols
    print len(cols)
    hdu = pyfits.PrimaryHDU()
    hduIMHEAD = pyfits.BinTableHDU.from_columns(tables[catalog['im_type']][2].columns)
    hduOBJECTS = pyfits.BinTableHDU.from_columns(cols) 
    hdulist = pyfits.HDUList([hdu])
    hdulist.append(hduIMHEAD)
    hdulist.append(hduOBJECTS)
    hdulist[1].header['EXTNAME']='FIELDS'
    hdulist[2].header['EXTNAME']='OBJECTS'
    print file
    os.system('rm ' + outfile)
    import re
    res = re.split('/',outfile)
    os.system('mkdir -p ' + reduce(lambda x,y: x + '/' + y,res[:-1]))
    hdulist.writeto(outfile)
    print outfile , '$#######$'
    #print 'done'

def paste_cats(cats,outfile): #cats,outfile,search_params):
      
  
    import astropy, astropy.io.fits as pyfits, sys, os, re, string, copy        
    from config_bonn import cluster, tag, arc, filters
    ppid = str(os.getppid())
    tables = {} 
    colset = 0
    cols = []
   
    table = pyfits.open(cats[0])

    data = [] 
    nrows = 0

    good_cats = []
    ''' get rid of empty tables '''
    for catalog in cats:
        cattab = pyfits.open(catalog)
        if not str(type(cattab[2].data)) == "<type 'NoneType'>":
            good_cats.append(catalog)
    cats = good_cats

    for catalog in cats:
        cattab = pyfits.open(catalog)
        nrows += cattab[2].data.shape[0]

    hduOBJECTS = pyfits.BinTableHDU.from_columns(table[2].columns, nrows=nrows) 
   
    rowstart = 0
    rowend = 0
    for catalog in cats:
        cattab = pyfits.open(catalog)
        rowend += cattab[2].data.shape[0]
        for i in range(len(cattab[2].columns)): 
            hduOBJECTS.data.field(i)[rowstart:rowend]=cattab[2].data.field(i)
        rowstart = rowend


    # update SeqNr
    print rowend,len(        hduOBJECTS.data.field('SeqNr')), len(range(1,rowend+1))
    hduOBJECTS.data.field('SeqNr')[0:rowend]=range(1,rowend+1)

    #hdu[0].header['EXTNAME']='FIELDS'


    hduIMHEAD = pyfits.BinTableHDU.from_columns(table[1])

    print cols
    print len(cols)
    hdu = pyfits.PrimaryHDU()
    hdulist = pyfits.HDUList([hdu])
    hdulist.append(hduIMHEAD)
    hdulist.append(hduOBJECTS)
    hdulist[1].header['EXTNAME']='FIELDS'
    hdulist[2].header['EXTNAME']='OBJECTS'
    print file

    os.system('rm ' + outfile)
    hdulist.writeto(outfile)
    print outfile , '$#######$'
    #print 'done'

def imstats(SUPA,FLAT_TYPE):
    import os, re, utilities, bashreader, sys, string
    from copy import copy
    from glob import glob
    dict = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':search_params['OBJNAME']}
    print dict['files']
    import commands
    tmp_dicts = [] 
    for file in dict['files']:
        op = commands.getoutput('imstats ' + dict['files'][0]) 
        print op
        res = re.split('\n',op)
        for line in res:
            if string.find(line,'filename') != -1:
                line = line.replace('$ imstats: ','')
                res2 = re.split('\t',line)
                                                               
        res3 = re.split('\s+',res[-1]) 

        tmp_dict = {}
        for i in range(len(res3)):
            tmp_dict[res2[i]] = res3[i] 
        tmp_dicts.append(tmp_dict)
    print tmp_dicts

    median_average = 0
    sigma_average = 0
    for d in tmp_dicts:
        print d.keys()
        sigma_average += float(d['sigma'])
        median_average += float(d['median'])

    dict['sigma_average'] = sigma_average / len(tmp_dicts)
    dict['median_average'] = median_average / len(tmp_dicts)

    print dict['sigma_average'], dict['median_average']

    save_exposure(dict,SUPA,FLAT_TYPE)

def save_fit_WHATISTHIS(fits,im_type,type,SUPA,FLAT_TYPE):
    import MySQLdb, sys, os, re, time 
    from copy import copy
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()


    for fit in fits:
        #which_solution += 1
        user_name = os.environ['USER']
        time_now = time.asctime() 
        user = user_name #+ str(time.time())
        
        dict = {} 
        #copy array but exclude lists                                                   
        for ele in fit['class'].fitvars.keys():
            if ele != 'condition' and ele != 'model_name' and ele != 'fixed_name': 
                dict[ele + '_' + type + '_' + im_type] = fit['class'].fitvars[ele]
    save_exposure(dict,SUPA,FLAT_TYPE)
    db2.close()


def select_analyze():
    import MySQLdb, sys, os, re, time, string 
    from copy import copy
    db2,c = connect_except()
    command = "DESCRIBE illumination_db"
    print command
    c.execute(command)
    results = c.fetchall()
    keys = []
    for line in results:
        keys.append(line[0])
    command = "SELECT * from illumination_db where zp_err_galaxy_D is null and PPRUN='2002-06-04_W-J-V'" # where OBJNAME='HDFN' and filter='W-J-V' and ROTATION=0"
    command = "SELECT * from illumination_db where color1_star > 0.2 and OBJNAME!='HDFN' limit 2" # where matched_cat_star is null" # where OBJNAME='HDFN' and filter='W-J-V' and ROTATION=0"

    first = True 
    while len(results) > 100 or first:
        first = False
        command= "SELECT * from illumination_db where (OBJNAME like 'A%' or OBJNAME like 'MACS%') and (pasted_cat is null or pasted_cat like '%None%') and CORRECTED='True' " # and PPRUN='2003-04-04_W-C-IC'"                                                                                     
        command= "SELECT * from illumination_db where SUPA like '%I' and Corrected='True' and filter='W-J-V'" # and PPRUN='2003-04-04_W-C-IC'"  

        #command= "SELECT * from illumination_db where SUPA='SUPA0011100'" # and PPRUN='2003-04-04_W-C-IC'"  
        #command= "SELECT * from illumination_db where (OBJNAME like 'A%' or OBJNAME like 'MACS%') and SUPA='SUPA0021827'" # and PPRUN='2003-04-04_W-C-IC'"  
        #command = "select * from illumination_db where SUPA='SUPA0028506'"
        #command = "select * from illumination_db where (OBJECT like '%0018short%') and (FILTER='W-J-B' or FILTER='W-S-Z+')" # or OBJECT like '%0018short%')" # and pasted_cat is null" # and color1_star_ is null"
        print command
        c.execute(command)
        results = c.fetchall()
        print len(results)
        #print results
        dicts = [] 
        for j in range(len(results)):
            dict = {} 
            for i in range(len(results[j])):  
                dict[keys[i]] = results[j][i]
            #print dict['SUPA'], dict['file'], dict['OBJNAME'], dict['pasted_cat'], dict['matched_cat_star']
            #good = raw_input()
            d_update = get_files(dict['SUPA'],dict['FLAT_TYPE'])
            go = 0
            if d_update.has_key('TRIED'):
                if d_update['TRIED'] != 'YES':
                    go = 1
            else: go = 1

            if string.find(str(dict['TIME']),'N') == -1:
                #print dict['TIME']
                if time.time() - float(dict['TIME']) > 600:
                    go = 1
                else: go = 0
            else: go = 1
            if 1: # go:
                #print str(time.time())
                save_exposure({'ACTIVE':'YES','TIME':str(time.time())},dict['SUPA'],dict['FLAT_TYPE'])
                os.system('rm -R ' + tmpdir)
                analyze(dict['SUPA'],dict['FLAT_TYPE'],dict)
                save_exposure({'ACTIVE':'FINISHED'},dict['SUPA'],dict['FLAT_TYPE'])

def analyze(SUPA,FLAT_TYPE,params={}):
    #try:
    import sys, os, string
    #os.system('rm -rf ' + search_params['TEMPDIR'] + '*')
    trial = True 
    ppid = str(os.getppid())
    try:
        #imstats(SUPA,FLAT_TYPE) 
        if string.find(str(params['CRPIX1ZERO']),'None') != -1:
            length(SUPA,FLAT_TYPE)
        if string.find(str(params['fwhm']),'None') != -1 or str(params['fwhm'])=='0.3':
            find_seeing(SUPA,FLAT_TYPE)      
        #sextract(SUPA,FLAT_TYPE)
        print 'finished'
        #match_simple(SUPA,FLAT_TYPE)
        #phot(SUPA,FLAT_TYPE)
        #get_sdss_obj(SUPA,FLAT_TYPE)
        #apply_photometric_calibration(SUPA,FLAT_TYPE)
        print 'finished'
    except:
        ppid_loc = str(os.getppid())
        print traceback.print_exc(file=sys.stdout)
        if ppid_loc != ppid: sys.exit(0) 
        if trial: raise Exception 

    #except KeyboardInterrupt:
    #    raise
    #except: 
    #    ppid_loc = str(os.getppid())
    #    print sys.exc_info()
    #    print 'something else failed',ppid, ppid_loc 
    #    if ppid_loc != ppid: sys.exit(0) 
#   #     os.system('rm -rf /tmp/' + ppid)
##
#    os.system('rm -rf /tmp/' + ppid)
#

def get_files(SUPA,FLAT_TYPE=None):    
    import MySQLdb, sys, os, re                                                                     

    db2,c = connect_except()

    command = "DESCRIBE illumination_db"
    #print command
    c.execute(command)
    results = c.fetchall()
    keys = []
    for line in results:
        keys.append(line[0])

    command = "SELECT * from illumination_db where SUPA='" + SUPA + "'" # AND FLAT_TYPE='" + FLAT_TYPE + "'"
    #print command
    c.execute(command)
    results = c.fetchall()
    dict = {} 
    for i in range(len(results[0])):
        dict[keys[i]] = results[0][i]
    #print dict 

    file_pat = dict['file'] 
    import re, glob
    res = re.split('_\d+O',file_pat)
    pattern = res[0] + '_*O' + res[1]

    files = glob.glob(pattern)
    dict['files'] = files

    db2.close()
    return dict


def get_a_file(OBJNAME,FILTER,PPRUN):    
    ''' get a single file w/ OBJNAME FILTER PPRUN'''

    import MySQLdb, sys, os, re                                                                     

    db2,c = connect_except()

    command = "DESCRIBE illumination_db"
    #print command
    c.execute(command)
    results = c.fetchall()
    keys = []
    for line in results:
        keys.append(line[0])

    command="SELECT * from illumination_db where FILTER='" + FILTER + "' and OBJNAME='" + OBJNAME + "' and PPRUN='" + PPRUN + "' limit 1"
    #print command
    c.execute(command)
    results = c.fetchall()
    dict = {} 
    for i in range(len(results[0])):
        dict[keys[i]] = results[0][i]
    #print dict 

    file_pat = dict['file'] 
    import re, glob
    res = re.split('_\d+O',file_pat)
    pattern = res[0] + '_*O' + res[1]

    files = glob.glob(pattern)
    dict['files'] = files

    db2.close()
    return dict

def get_fits(OBJNAME,FILTER,PPRUN):    
    import MySQLdb, sys, os, re                                                                     
    db2,c = connect_except()

    command="SELECT * from fit_db where FILTER='" + FILTER + "' and OBJNAME='" + OBJNAME + "' and PPRUN='" + PPRUN + "'"
    print command
    c.execute(command)
    results=c.fetchall()
    db_keys = describe_db(c,'fit_db')
    dtop = {}   
    for line in results: 
        for i in range(len(db_keys)):
            dtop[db_keys[i]] = str(line[i])

    db2.close()
    return dtop

def connect_except():
    import MySQLdb, sys, os, re                                                                             
    notConnect = True
    tried = 0
    while notConnect:
        tried += 1                                                                                                     
        try:
            db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')  
            c = db2.cursor()
            notConnect = False
        except:
            print traceback.print_exc(file=sys.stdout)
            import random, time
            randwait = int(random.random()*30)
            print 'rand wait', randwait
            time.sleep(randwait)
            if tried > 15: sys.exit(0)
    #print 'done'
    return db2,c

def save_exposure(dict,SUPA=None,FLAT_TYPE=None):
    if SUPA != None and FLAT_TYPE != None:
        dict['SUPA'] = SUPA
        dict['FLAT_TYPE'] = FLAT_TYPE

    db2,c = connect_except()
    
    #command = "CREATE TABLE IF NOT EXISTS illumination_db ( id MEDIUMINT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id))"
    #print command
    #c.execute("DROP TABLE IF EXISTS illumination_db")
    #c.execute(command)

    from copy import copy
    floatvars = {}  
    stringvars = {}
    #copy array but exclude lists                                                   
    import string
    letters = string.ascii_lowercase + string.ascii_uppercase.replace('E','') + '_' + '-' + ','
    for ele in dict.keys():
        type = 'float'
        for l in letters:
            if string.find(str(dict[ele]),l) != -1: 
                type = 'string'
        if type == 'float':  
            floatvars[ele] = str(float(dict[ele])) 
        elif type == 'string':
            stringvars[ele] = dict[ele] 
                                                                                                                                                                                                           
    # make database if it doesn't exist
    print 'floatvars', floatvars
    print 'stringvars', stringvars
    
    for column in stringvars: 
        try:
            command = 'ALTER TABLE illumination_db ADD ' + column + ' varchar(240)'
            c.execute(command)  
        except: nope = 1 
    
    for column in floatvars: 
        try:
            command = 'ALTER TABLE illumination_db ADD ' + column + ' float(30)'
            c.execute(command)  
        except: nope = 1 

    # insert new observation 

    SUPA = dict['SUPA'] 
    flat = dict['FLAT_TYPE']
    c.execute("SELECT SUPA from illumination_db where SUPA = '" + SUPA + "' and flat_type = '" + flat + "'")
    results = c.fetchall() 
    print results
    if len(results) > 0:
        print 'already added'
    else:
        command = "INSERT INTO illumination_db (SUPA,FLAT_TYPE) VALUES ('" + dict['SUPA'] + "','" + dict['FLAT_TYPE'] + "')"
        print command
        c.execute(command) 

    import commands

     
    vals = ''
    for key in stringvars.keys():
        print key, stringvars[key]
        vals += ' ' + key + "='" + str(stringvars[key]) + "',"

    for key in floatvars.keys():
        print key, floatvars[key]
        vals += ' ' + key + "='" + floatvars[key] + "',"
    vals = vals[:-1]

    command = "UPDATE illumination_db set " + vals + " WHERE SUPA='" + dict['SUPA'] + "' AND FLAT_TYPE='" + dict['FLAT_TYPE'] + "'" 
    print command
    c.execute(command)
        

    print vals
        

    #names = reduce(lambda x,y: x + ',' + y, [x for x in floatvars.keys()])
    #values = reduce(lambda x,y: str(x) + ',' + str(y), [floatvars[x] for x in floatvars.keys()])
    #names += ',' + reduce(lambda x,y: x + ',' + y, [x for x in stringvars.keys()])
    #values += ',' + reduce(lambda x,y: x + ',' + y, ["'" + str(stringvars[x]) + "'" for x in stringvars.keys()])

        
    #command = "INSERT INTO illumination_db (" + names + ") VALUES (" + values + ")"
    #print command
    #os.system(command)

    db2.close()


def initialize(filter,OBJNAME):
    import os, re, bashreader, sys, string, utilities
    from glob import glob
    from copy import copy

    dict = bashreader.parseFile(os.environ['bonn'] + 'progs.ini')
    for key in dict.keys():
        os.environ[key] = str(dict[key])
    import os
    ppid = str(os.getppid())
    PHOTCONF = os.environ['bonn'] + '/photconf/'
    #TEMPDIR = '/usr/work/pkelly/' + ppid + '/'
    TEMPDIR = tmpdir 
    os.system('mkdir ' + TEMPDIR)
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':OBJNAME}
    search_params = {'path':path, 'OBJNAME':OBJNAME, 'filter':filter, 'PHOTCONF':PHOTCONF, 'DATACONF':os.environ['DATACONF'], 'TEMPDIR':TEMPDIR} 

    return search_params


def update_dict(SUPA,FLAT_TYPE):    
    import utilities
    dict = get_files(SUPA,FLAT_TYPE)
    kws = utilities.get_header_kw(dict['file'],['ROTATION','OBJECT','GABODSID','CONFIG','EXPTIME','AIRMASS','INSTRUM','PPRUN','BADCCD']) # return KEY/NA if not SUBARU 
    save_exposure(kws,SUPA,FLAT_TYPE)
    

def gather_exposures(OBJNAME,filters=None):

    Corrected = True
    if Corrected: pattern = 'I.fits'
    else: pattern = ''

    if not filters:
        filters =  ['B','W-J-B','W-J-V','W-C-RC','W-C-IC','I','W-S-Z+']        
    for filter_name in filters:
        search_params = initialize(filter_name,OBJNAME) 
        import os, re, bashreader, sys, string, utilities
        from glob import glob
        from copy import copy
       
        searchstr = "/%(path)s/%(filter)s/SCIENCE/*.fits" % search_params
        print searchstr
        files = glob(searchstr)

        ''' filter_name out corrected or not corrected files '''
        print files
        if Corrected: 
            files = filter(lambda x:string.find(x,'I.fits')!=-1,files) 
        elif not Corrected:
            files = filter(lambda x:string.find(x,'I.fits')==-1,files) 
        print files

        files.sort()
        #print files
        exposures =  {} 
        # first 30 files
        #print files[0:30]
        
        import MySQLdb, sys, os, re                                                                     
        db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
        c = db2.cursor()
        
        for file in files:
            if string.find(file,'wcs') == -1 and string.find(file,'.sub.fits') == -1:
                res = re.split('_',re.split('/',file)[-1])                                        
                exp_name = res[0]
                if not exposures.has_key(exp_name): exposures[exp_name] = {'images':[],'keywords':{}}
                exposures[exp_name]['images'].append(file) # exp_name is the root of the image name
                if len(exposures[exp_name]['keywords'].keys()) == 0: #not exposures[exp_name]['keywords'].has_key('ROTATION'): #if exposure does not have keywords yet, then get them
                    exposures[exp_name]['keywords']['filter'] = filter_name
                    exposures[exp_name]['keywords']['file'] = file 
                    res2 = re.split('/',file)   
                    for r in res2:
                        if string.find(r,filter_name) != -1:
                            print r
                            exposures[exp_name]['keywords']['date'] = r.replace(filter_name + '_','')
                            exposures[exp_name]['keywords']['fil_directory'] = r 
                            search_params['fil_directory'] = r
                    kws = utilities.get_header_kw(file,['CRVAL1','CRVAL2','ROTATION','OBJECT','GABODSID','CONFIG','EXPTIME','AIRMASS','INSTRUM','PPRUN','BADCCD']) # return KEY/NA if not SUBARU 
                                                                                                                                                                                      
                    ''' figure out a way to break into SKYFLAT, DOMEFLAT '''
                                                                                                                                                                                      
                    ppid = str(os.getppid())
                    command = 'dfits ' + file + ' > ' + search_params['TEMPDIR'] + '/header'
                    utilities.run(command)
                    file = open('' + search_params['TEMPDIR'] + 'header','r').read()
                    import string                    
                    if string.find(file,'SKYFLAT') != -1: exposures[exp_name]['keywords']['FLAT_TYPE'] = 'SKYFLAT' 
                    elif string.find(file,'DOMEFLAT') != -1: exposures[exp_name]['keywords']['FLAT_TYPE'] = 'DOMEFLAT' 
                    #print file, exposures[exp_name]['keywords']['FLAT_TYPE'] 
                                                                                                                                                                                      
                    file = open('' + search_params['TEMPDIR'] + 'header','r').readlines()
                    import string                    
                    for line in file:
                        print line
                        if string.find(line,'Flat frame:') != -1 and string.find(line,'illum') != -1:
                            import re                   
                            res = re.split('SET',line)
                            if len(res) > 1:
                                res = re.split('_',res[1])                                                                                                                                 
                                set = res[0]
                                exposures[exp_name]['keywords']['FLAT_SET'] = set
                                                                                                                                                                                          
                                res = re.split('illum',line)
                                res = re.split('\.',res[1])
                                smooth = res[0]
                                exposures[exp_name]['keywords']['SMOOTH'] = smooth 
                            break
                                                                                                                                                                                      
                    for kw in kws.keys(): 
                        exposures[exp_name]['keywords'][kw] = kws[kw]
                    if Corrected: 
                        exposures[exp_name]['keywords']['SUPA'] = exp_name+'I'
                    if not Corrected:
                        exposures[exp_name]['keywords']['SUPA'] = exp_name
                    exposures[exp_name]['keywords']['OBJNAME'] = OBJNAME 
                    exposures[exp_name]['keywords']['CORRECTED'] = str(Corrected) 
                    print exposures[exp_name]['keywords']
                    save_exposure(exposures[exp_name]['keywords'])

    return exposures



def find_seeing(SUPA,FLAT_TYPE):     
    import os, re, utilities, sys
    from copy import copy
    dict = get_files(SUPA,FLAT_TYPE)
    print dict['file']
    search_params = initialize(dict['filter'],dict['OBJNAME'])
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
            params['ROOT_WEIGHT'] = ROOT.replace('I','')
            NUM = re.split('O',re.split('\_',ROOT)[1])[0]
            params['NUM'] = NUM
            print ROOT
                                                                                                                     
            weightim = "/%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits" % params
            #flagim = "/%(path)s/%(fil_directory)s/WEIGHTS/globalflag_%(NUM)s.fits" % params
            #finalflagim = TEMPDIR + "flag_%(ROOT)s.fits" % params 
            os.system('mkdir -p ' + params['TEMPDIR'])

            params['finalflagim'] = weightim
            #os.system('rm ' + finalflagim)
            #command = "ic -p 16 '1 %2 %1 0 == ?' " + weightim + " " + flagim + " > " + finalflagim
            #utilities.run(command)
            
            command = "nice sex %(file)s -c %(PHOTCONF)s/singleastrom.conf.sex \
                        -FLAG_IMAGE ''\
                        -FLAG_TYPE MAX \
                        -CATALOG_NAME %(TEMPDIR)s/seeing_%(ROOT)s.cat \
                        -FILTER_NAME %(PHOTCONF)s/default.conv\
                        -CATALOG_TYPE 'ASCII' \
                        -DETECT_MINAREA 8 -DETECT_THRESH 8.\
                        -ANALYSIS_THRESH 8 \
                        -WEIGHT_IMAGE /%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT_WEIGHT)s.weight.fits\
                        -WEIGHT_TYPE MAP_WEIGHT\
                        -PARAMETERS_NAME %(PHOTCONF)s/singleastrom.ascii.flag.sex" %  params 
                                                                                                                     
            print command
            os.system(command)
            sys.exit(0)
    for child in children:  
        os.waitpid(child,0)
                                                                                                                          
                                                                                                                          
    command = 'cat ' + search_params['TEMPDIR'] + 'seeing_' +  SUPA.replace('I','*I') + '*cat > ' + search_params['TEMPDIR'] + 'paste_seeing_' + SUPA.replace('I','*I') + '.cat' 
    utilities.run(command)
                                                                                                                          
    file_seeing = search_params['TEMPDIR'] + '/paste_seeing_' + SUPA.replace('I','*I') + '.cat'
    PIXSCALE = float(search_params['PIXSCALE'])
    reload(utilities)
    fwhm = utilities.calc_seeing(file_seeing,10,PIXSCALE)

    save_exposure({'fwhm':fwhm},SUPA,FLAT_TYPE)

    print file_seeing, SUPA, PIXSCALE

def length_DONTUSE(SUPA,FLAT_TYPE):
    import os, re, utilities, bashreader, sys, string
    from copy import copy
    from glob import glob
    dict = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':search_params['OBJNAME']}

    res = re.split('SCIENCE',search_params['files'][0])                         
    res = re.split('/',res[0])
    if res[-1]=='':res = res[:-1]
    search_params['path'] = reduce(lambda x,y:x+'/'+y,res[:-1])
    search_params['fil_directory'] = res[-1]
    print search_params['path'], search_params['fil_directory'], 'list'
    save_exposure({'path':search_params['path'],'fil_directory':search_params['fil_directory']},SUPA,FLAT_TYPE)

    ''' get the CRPIX values '''
    start = 1
    #CRPIXZERO is at the chip at the bottom left and so has the greatest value!!!!
    x = []
    y = []
    chips = {} 
    NUMS = []
    all_chip_dict = {}
    for image in search_params['files']:
        print image                                                 
        res = re.split('\_\d+',re.split('\/',image)[-1])
        #print res
        imroot = "/%(path)s/%(fil_directory)s/SCIENCE/" % search_params
        im = imroot + res[0] + '_1' + res[1] 
        #print im
        crpix = utilities.get_header_kw(image,['CRPIX1','CRPIX2','NAXIS1','NAXIS2','CRVAL1','CRVAL2','IMAGEID'])
        if start == 1:
            crpixzero = copy(crpix)
            crpixhigh = copy(crpix)
            start = 0
        from copy import copy 
        print  float(crpix['CRPIX1'])  < float(crpixzero['CRPIX1']), float(crpix['CRPIX2'])  < float(crpixzero['CRPIX2'])
        if float(crpix['CRPIX1']) + 0   >= float(crpixzero['CRPIX1']):
            crpixzero['CRPIX1'] = copy(crpix['CRPIX1'])
        if float(crpix['CRPIX2'])  + 0 >= float(crpixzero['CRPIX2']):
            crpixzero['CRPIX2'] = copy(crpix['CRPIX2'])
                                                                                                                          
        if float(crpix['CRPIX1']) - 0  <= float(crpixhigh['CRPIX1']):
            crpixhigh['CRPIX1'] = copy(crpix['CRPIX1'])
        if float(crpix['CRPIX2']) - 0  <= float(crpixhigh['CRPIX2']):
            crpixhigh['CRPIX2'] = copy(crpix['CRPIX2'])

        print crpix['CRPIX1'], crpix['CRPIX2'], crpixzero['CRPIX1'], crpixzero['CRPIX2'], crpixhigh['CRPIX1'], crpixhigh['CRPIX2']#, crpixhigh
        x.append(float(crpix['CRPIX1']))
        y.append(float(crpix['CRPIX2']))

        chips[crpix['IMAGEID']] = crpix
        NUMS.append(crpix['IMAGEID'])
        for kw in ['CRPIX1','CRPIX2','NAXIS1','NAXIS2','CRVAL1','CRVAL2']:
            all_chip_dict[kw+ '_' + str(crpix['IMAGEID'])] = crpix[kw]

    NUMScommas = reduce(lambda x,y: str(x) + ',' + str(y),NUMS)
    all_chip_dict['CHIPS'] = NUMScommas

    print all_chip_dict 

    LENGTH1 =  abs(float(crpixhigh['CRPIX1']) - float(crpixzero['CRPIX1'])) + float(crpix['NAXIS1']) 
    LENGTH2 =  abs(float(crpixhigh['CRPIX2']) - float(crpixzero['CRPIX2'])) + float(crpix['NAXIS2']) 

    chips['CRPIX1ZERO'] = crpixzero['CRPIX1']
    chips['CRPIX2ZERO'] = crpixzero['CRPIX2']

    chips['NAXIS1'] = crpixzero['NAXIS1']
    chips['NAXIS2'] = crpixzero['NAXIS2']

    print LENGTH1, LENGTH2, crpixzero['CRPIX1'], crpixzero['CRPIX2'], crpixhigh['CRPIX1'], crpixhigh['CRPIX2']#, crpixhigh

    all_chip_dict.update({'crfixed':'third','LENGTH1':LENGTH1,'LENGTH2':LENGTH2,'CRPIX1ZERO':crpixzero['CRPIX1'],'CRPIX2ZERO':crpixzero['CRPIX2'],'CRVAL1':crpix['CRVAL1'],'CRVAL2':crpix['CRVAL2']})
    save_exposure(all_chip_dict,SUPA,FLAT_TYPE)

    return chips
    #return x,y

def apply_correction2(SUPA,FLAT_TYPE):

    chips = length(SUPA,FLAT_TYPE)

    for chip in [1]:
        #retrieve coefficients        

        d = get_fits(CLUSTER,FILTER,PPRUN)                
        column_prefix = sample+'$'+sample_size+'$'
        position_columns_names = re.split('\,',d[column_prefix + 'positioncolumns']) 
        fitvars = {}
        cheby_terms_dict = {}
        for ele in position_columns:                      
            res = re.split('$',ele['name'])
            fitvars[ele['name']] = float(d[sample+'$'+sample_size+'$'+ele['name']])
            for term in cheby_terms:
                if term['n'] == ele['name'][2:]:
                    cheby_terms_dict[term['n']] = term 
        cheby_terms_use =  [cheby_terms_dict[k] for k in cheby_terms_dict.keys()]
                                                                                                                          
        print cheby_terms_use, fitvars
                                                                                                                          
        ''' make images of illumination corrections '''                                                                  
        for ROT in EXPS.keys():
            size_x=LENGTH1
            size_y=LENGTH2
            bin=100
            import numpy, math, pyfits, os                                                                              
            x,y = numpy.meshgrid(numpy.arange(0,size_x,bin),numpy.arange(0,size_y,bin))
            F=0.1
            print 'calculating'
            x = coord_conv_x(x)
            y = coord_conv_y(y)
            
            epsilon = 0
            index = 0
            for term in cheby_terms_use:
                index += 1
                print index, ROT, term, fitvars[str(ROT)+'$'+term['n']]
                epsilon += fitvars[str(ROT)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)
                                                                                                                          
                                                                                                                          
            print 'writing'
            hdu = pyfits.PrimaryHDU(epsilon)
            #os.system('rm ' + tmpdir + 'correction' + ROT + filter + sample_size + '.fits')
            #hdu.writeto(tmpdir + '/correction' + ROT + filter + sample_size + '.fits')
                                                                                                                         
            path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':CLUSTER}
            illum_dir = path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + str(ROT)
            os.system('mkdir -p ' + illum_dir)
                                                                                                                         
            im = illum_dir + '/correction' + sample + sample_size + '.fits'
            save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'CLUSTER':CLUSTER,sample+'$'+sample_size+'$'+str(ROT)+'$im':im})
                                                                                                                         
            os.system('rm ' + im)
            hdu.writeto(im)




def sdss_coverage(SUPA,FLAT_TYPE):
    import commands, string                                                                                    
    dict = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)
    if 0:
        #print 'CRVAL1', search_params['CRVAL1'], search_params['CRVAL1'] == 'None'                                                                                             
        #if str(search_params['CRVAL1']) == 'None':
        #    print search_params['FLAT_TYPE'], 'FLAT_TYPE'
        
        if search_params['CRVAL1'] is None:
            length(search_params['SUPA'],search_params['FLAT_TYPE'])
                                                                                                                                                                               
        dict = get_files(SUPA,FLAT_TYPE)
        search_params.update(dict)
        print search_params['CRVAL1']
        crval1 = float(search_params['CRVAL1'])
        crval2 = float(search_params['CRVAL2'])
        query = 'select ra, dec from star where ra between ' + str(crval1-0.1) + ' and ' + str(crval1+0.1) + ' and dec between ' + str(crval2-0.1) + ' and ' + str(crval2+0.1)
        print query


        import sqlcl
        lines = sqlcl.query(query).readlines()
        print lines
        if len(lines) > 1: sdss_coverage=True 
        else: sdss_coverage=False 
        save_exposure({'sdss_coverage':sdss_coverage},SUPA,FLAT_TYPE)

    import MySQLdb, sys, os, re, time, utilities, pyfits
    from copy import copy
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()

    command = "select cov from sdss_db where OBJNAME='" + dict['OBJNAME'] + "'"
    c.execute(command)
    results=c.fetchall()
    print results
    sdss_coverage = results[0][0]

    import string
    if string.find(sdss_coverage,'True') != -1:
        cov = True
    else: cov=False

    starcat ='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/PHOTOMETRY/sdssstar.cat' % {'OBJNAME':search_params['OBJNAME']}
    galaxycat ='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/PHOTOMETRY/sdssgalaxy.cat' % {'OBJNAME':search_params['OBJNAME']}
    return cov, galaxycat, starcat

def sextract(SUPA,FLAT_TYPE):
    import os, re, utilities, bashreader, sys, string
    from copy import copy
    from glob import glob

    trial = False 
    
    dict = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':search_params['OBJNAME']}
    subpath='/nfs/slac/g/ki/ki05/anja/SUBARU/'

    print search_params

    print SUPA, FLAT_TYPE, search_params['files'] 
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

    children = []
    if 1:
        for image in search_params['files']:
            ROOT = re.split('\.',re.split('\/',image)[-1])[0]
            BASE = re.split('O',ROOT)[0]
            NUM = re.split('O',re.split('\_',ROOT)[1])[0]
            print image, search_params['CRVAL1ASTROMETRY_'+NUM]
       
        ''' copy over ASTROMETRY keywords to Corrected if they exist for the unCorrected frame '''
        if search_params['CORRECTED']=='True': # and string.find(str(search_params['CRVAL1ASTROMETRY_2']),'None') != -1:             
            ''' adding correct WCS info '''
            dict_uncorrected = get_files(SUPA[:-1],FLAT_TYPE)                                                               
            d = {}                                                                                                          
            akeys = filter(lambda x:string.find(x,'ASTROMETRY')!=-1,dict_uncorrected.keys())                                
            for key in akeys:                    
                d[key] = dict_uncorrected[key]    
                print key, d[key], SUPA[:-1]
            save_exposure(d,SUPA,FLAT_TYPE)                                                                                 
            os.system('mkdir -p ' + search_params['TEMPDIR'])                                                               
            
            dict = get_files(SUPA,FLAT_TYPE)
            search_params = initialize(dict['filter'],dict['OBJNAME'])
            search_params.update(dict)

            for key in akeys:                                                                                               
                print key, search_params[key]


        for image in search_params['files']:
            print image
            child = False 
            if not trial:
                child = os.fork()           
                if child:
                    children.append(child)

            params = copy(search_params)                                
            ROOT = re.split('\.',re.split('\/',image)[-1])[0]
            params['ROOT'] = ROOT
            params['ROOT_WEIGHT'] = ROOT.replace('I','')
            BASE = re.split('O',ROOT)[0]
            params['BASE'] = BASE 
            NUM = re.split('O',re.split('\_',ROOT)[1])[0]
            params['NUM'] = NUM
            print NUM, BASE, ROOT

            if not child:
                if (search_params['CORRECTED']!='True' or (search_params['CORRECTED']=='True' and string.find(str(search_params['CRVAL1ASTROMETRY_' + NUM]),'None') == -1)):
                    try:                                                                                                                                                                                                                                                                                                                                                                                                               
                        params['GAIN'] = 2.50 ## WARNING!!!!!!
                        print ROOT
                        finalflagim = "%(TEMPDIR)sflag_%(ROOT)s.fits" % params     
                        res = re.split('SCIENCE',image)
                        res = re.split('/',res[0])
                        if res[-1]=='':res = res[:-1]
                        params['path'] = reduce(lambda x,y:x+'/'+y,res[:-1])
                        params['fil_directory'] = res[-1]
                        weightim = "/%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits" % params
                        #flagim = "/%(path)s/%(fil_directory)s/WEIGHTS/globalflag_%(NUM)s.fits" % params
                        #finalflagim = TEMPDIR + "flag_%(ROOT)s.fits" % params 
                        params['finalflagim'] = weightim
                        im = "/%(path)s/%(fil_directory)s/SCIENCE/%(ROOT)s.fits" % params
                        crpix = utilities.get_header_kw(im,['CRPIX1','CRPIX2'])
                        
                        #if search_params['SDSS_coverage'] == 'yes': catalog = 'SDSS-R6'
                        #else: catalog = '2MASS'
                                                                                                                                                                                                                                                                                                                                                                                                                                       
                        SDSS1 = "/%(path)s/%(fil_directory)s/SCIENCE/headers_scamp_SDSS-R6/%(BASE)s.head" % params
                        SDSS2 = "/%(path)s/%(fil_directory)s/SCIENCE/headers_scamp_SDSS-R6/%(BASE)sO*.head" % params
                        from glob import glob 
                        print glob(SDSS1), glob(SDSS2)
                        head = None
                        if len(glob(SDSS1)) > 0:
                            head = glob(SDSS1)[0]
                        elif len(glob(SDSS2)) > 0:
                            head = glob(SDSS2)[0]
                                                                                                                                                                                                                                                                                                                                                                                                                                       
                        ''' see if image has been run through astrometry.net. if not, run it. '''
                        if True: 
                                                                                                                                                                                                                                                                                                                                                                                                                                       
                            if not search_params.has_key('ASTROMETRYNET_' + NUM):
                                save_exposure({'ASTROMETRYNET_' + NUM:'None'},SUPA,FLAT_TYPE)
                                dict = get_files(dict['SUPA'],dict['FLAT_TYPE'])
                                search_params.update(dict)
                                                                                                                                                                                                                                                                                                                                                                                                                                       
                            if search_params['CORRECTED']!='True' and string.find(str(search_params['CRVAL1ASTROMETRY_' + NUM]),'None') != -1: #head is None:
                                save_exposure({'ASTROMETRYNET_' + NUM:'yes'},SUPA,FLAT_TYPE)
                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                imtmp = "%(TEMPDIR)s/%(ROOT)s.tmp.fits" % params  
                                imfix = "%(TEMPDIR)s/%(ROOT)s.fixwcs.fits" % params
                                imwcs = "%(TEMPDIR)s/%(ROOT)s.wcsfile" % params
                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                command = "cp " + im + " " + imtmp
                                print command
                                utilities.run(command)
                                os.system('rm ' + imfix)
                                #command = '/nfs/slac/g/ki/ki04/pkelly/astrometry/bin//solve-field --cpulimit 60  --no-verify --no-plots --overwrite --scale-units arcsecperpix --scale-low ' + str(float(params['PIXSCALE'])-0.005) + ' --scale-high '  + str(float(params['PIXSCALE'])+0.005) + ' -N ' + imfix + ' ' + imtmp
                                command = astrom + ' --temp-dir ' + tmpdir + ' --cpulimit 100  --no-verify --no-plots --overwrite --scale-units arcsecperpix --scale-low ' + str(float(params['PIXSCALE'])-0.005) + ' --scale-high '  + str(float(params['PIXSCALE'])+0.005) + ' -N ' + imfix + ' ' + imtmp
                                print command
                                os.system(command)
                                os.system('rm ' + imtmp)
                                from glob import glob
                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                if len(glob(imfix)):
                                    command = 'imhead < ' + imfix + ' > ' +  imwcs
                                    print command
                                    os.system(command)
                                    hf = open(imwcs,'r').readlines() 
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
                                                                                                                            
                                    ''' now save the wcs '''
                                    wcsdict = {}                                                                       
                                    import commands
                                    out = commands.getoutput('gethead ' + imfix + ' CRPIX1 CRPIX2')
                                    import re
                                    res = re.split('\s+',out)
                                    os.system('sethead ' + imfix + ' CRPIX1OLD=' + res[0])
                                    os.system('sethead ' + imfix + ' CRPIX2OLD=' + res[1])
                                    for name in ['CRVAL1','CRVAL2','CD1_1','CD1_2','CD2_1','CD2_2','CRPIX1','CRPIX2']:
                                        print name + 'ASTROMETRY_' + NUM, hdict[name]
                                        wcsdict[name + 'ASTROMETRY_' + NUM] = hdict[name]                                        
                                                                                                                           
                                    save_exposure(wcsdict,SUPA,FLAT_TYPE)
                                    dict = get_files(dict['SUPA'],dict['FLAT_TYPE'])
                                    search_params.update(dict)
                                                                                                                                                                                                                                                                                                                                                                                                                                       
                            hdict = {}
                            if string.find(str(search_params['CD1_1ASTROMETRY_' + NUM]),'None') == -1: #head is None:
                                for name in ['CRVAL1','CRVAL2','CD1_1','CD1_2','CD2_1','CD2_2','CRPIX1','CRPIX2']:
                                    print name + 'ASTROMETRY', search_params[name+'ASTROMETRY_' + NUM]
                                    hdict[name] = search_params[name+'ASTROMETRY_' + NUM]                                        
                            elif head is not None:
                                ''' if no solution from astrometry.net, use the Swarp solution '''
                                hf = open(head,'r').readlines() 
                                for line in hf:
                                    import re
                                    if string.find(line,'=') != -1:
                                        res = re.split('=',line)
                                        name = res[0].replace(' ','')
                                        res = re.split('/',res[1])
                                        value = res[0].replace(' ','')
                                        print name, value
                                        hdict[name] = value
                            else: sys.exit(0)
                                                                                                                                                       
                            imfix = "%(TEMPDIR)s/%(ROOT)s.fixwcs.fits" % params
                            print imfix
                            
                            os.system('mkdir ' + search_params['TEMPDIR'])
                            command = "cp " + im + " " + imfix
                            print command
                            print 'copying file', im
                            utilities.run(command)
                            print 'finished copying'
                            
                            
                            import commands
                            out = commands.getoutput('gethead ' + imfix + ' CRPIX1 CRPIX2')
                            import re
                            res = re.split('\s+',out)
                            os.system('sethead ' + imfix + ' CRPIX1OLD=' + res[0])
                            os.system('sethead ' + imfix + ' CRPIX2OLD=' + res[1])
                            for name in ['CRVAL1','CRVAL2','CD1_1','CD1_2','CD2_1','CD2_2','CRPIX1','CRPIX2']:
                                command = 'sethead ' + imfix + ' ' + name + '=' + str(hdict[name])
                                print command
                                os.system(command)
                        ''' now run sextractor '''
                        if 1:
                            main_file = '%(TEMPDIR)s/%(ROOT)s.fixwcs.fits' % params
                            doubles_raw = [{'file_pattern':main_file,'im_type':''},]
                                           #{'file_pattern':subpath+pprun+'/SCIENCE_DOMEFLAT*/'+BASE+'OC*.fits','im_type':'D'},
                                           #{'file_pattern':subpath+pprun+'/SCIENCE_SKYFLAT*/'+BASE+'OC*.fits','im_type':'S'}]
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
                                    #print params
                                    #for par in ['fwhm','GAIN']:
                                    #    print par, type(params[par]), params[par]
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
                                    -WEIGHT_IMAGE /%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT_WEIGHT)s.weight.fits\
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
                        print traceback.print_exc(file=sys.stdout)
                        if not trial:
                            sys.exit(0)
                        if trial:
                            raise Exception
                if not trial: 
                    sys.exit(0)
        print children
        for child in children:  
            print 'waiting for', child
            os.waitpid(child,0)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
        print 'finished waiting'

    print path, SUPA, search_params['filter'], search_params['ROTATION']

    pasted_cat = path + 'PHOTOMETRY/ILLUMINATION/' + 'pasted_' + SUPA + '_' + search_params['filter'] + '_' + str(search_params['ROTATION']) + '.cat'
    print pasted_cat
    os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/')

    from glob import glob        
    outcat = search_params['TEMPDIR'] + 'tmppaste_' + SUPA + '.cat'
    newposlist = glob(search_params['TEMPDIR'] + SUPA.replace('I','*I') + '*newpos')
    print search_params['TEMPDIR'] + SUPA.replace('I','*I') + '*newpos'
    if len(newposlist) > 1:
        #command = 'ldacpaste -i ' + search_params['TEMPDIR'] + SUPA + '*newpos -o ' + pasted_cat 
        #print command
        files = glob(search_params['TEMPDIR'] + SUPA.replace('I','*I') + '*newpos')
        print files, search_params['TEMPDIR'] + SUPA.replace('I','*I') + '*newpos'
        paste_cats(files,pasted_cat)
    else:
        command = 'cp ' + newposlist[0] + ' ' + pasted_cat 
        utilities.run(command)
    save_exposure({'pasted_cat':pasted_cat},SUPA,FLAT_TYPE)

    command = "rm -rf " + search_params['TEMPDIR']  
    os.system(command)

    #fs = glob.glob(subpath+pprun+'/SCIENCE_DOMEFLAT*.tarz'.replace('.tarz','')) 
    #if len(fs) > 0: 
    #    os.system('tar xzvf ' + fs[0])
                                                            
    #fs = glob.glob(subpath+pprun+'/SCIENCE_SKYFLAT*.tarz'.replace('.tarz',''))
    #fs = glob.glob(subpath+pprun+'/SCIENCE_SKYFLAT*.tarz')
    #if len(fs) > 0: 
    #    os.system('tar xzvf ' + fs[0])


    #return exposures, LENGTH1, LENGTH2 

def get_sdss_obj_ext(SUPA, FLAT_TYPE):
    dict = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)
    
    ROTATION = str(search_params['ROTATION']) #exposures[exposure]['keywords']['ROTATION']
    
    import os
    starcat ='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/PHOTOMETRY/sdssstar%(ROTATION)s.cat' % {'ROTATION':ROTATION,'OBJNAME':search_params['OBJNAME']}
    galaxycat ='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/PHOTOMETRY/sdssgalaxy%(ROTATION)s.cat' % {'ROTATION':ROTATION,'OBJNAME':search_params['OBJNAME']}
    
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':search_params['OBJNAME']}
    illum_path='/nfs/slac/g/ki/ki05/anja/SUBARU/ILLUMINATION/' % {'OBJNAME':search_params['OBJNAME']}
    #os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/') 
    os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/STAR/') 
    os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/GALAXY/') 
    from glob import glob
    
    print starcat
    
    for type,cat in [['star',starcat]]: #,['galaxy',galaxycat]]:
        catalog = search_params['pasted_cat'] #exposures[exposure]['pasted_cat']
        ramin,ramax, decmin, decmax = coordinate_limits(catalog)    
        limits = {'ramin':ramin-0.2,'ramax':ramax+0.2,'decmin':decmin-0.2,'decmax':decmax+0.2}
        print ramin,ramax, decmin, decmax
        if len(glob(cat)) == 0:                                      
            #os.system('rm ' + cat)
            image = search_params['files'][0]
            print image
            import retrieve_test
            retrieve_test.run(image,cat,type,limits)

    save_exposure({'starcat':cat},SUPA,FLAT_TYPE)
    return cat


def get_sdss_obj(SUPA, FLAT_TYPE):
    dict = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)
    
    ROTATION = str(search_params['ROTATION']) #exposures[exposure]['keywords']['ROTATION']
    
    import os
    starcat ='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/PHOTOMETRY/sdssstar%(ROTATION)s.cat' % {'ROTATION':ROTATION,'OBJNAME':search_params['OBJNAME']}
    galaxycat ='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/PHOTOMETRY/sdssgalaxy%(ROTATION)s.cat' % {'ROTATION':ROTATION,'OBJNAME':search_params['OBJNAME']}
    
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':search_params['OBJNAME']}
    illum_path='/nfs/slac/g/ki/ki05/anja/SUBARU/ILLUMINATION/' % {'OBJNAME':search_params['OBJNAME']}
    #os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/') 
    os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/STAR/') 
    os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/GALAXY/') 
    from glob import glob
    
    print starcat
    
    for type,cat in [['star',starcat]]: #,['galaxy',galaxycat]]:
        catalog = search_params['pasted_cat'] #exposures[exposure]['pasted_cat']
        ramin,ramax, decmin, decmax = coordinate_limits(catalog)    
        limits = {'ramin':ramin-0.2,'ramax':ramax+0.2,'decmin':decmin-0.2,'decmax':decmax+0.2}
        print ramin,ramax, decmin, decmax
        if len(glob(cat)) == 0:                                      
            #os.system('rm ' + cat)
            image = search_params['files'][0]
            print image
            import retrieve_test
            retrieve_test.run(image,cat,type,limits)

    save_exposure({'starcat':cat},SUPA,FLAT_TYPE)

def match_simple(SUPA,FLAT_TYPE):
    dict = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)

    print 'hey'
    ROTATION = str(search_params['ROTATION']) #exposures[exposure]['keywords']['ROTATION']

    import os
    starcat ='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/PHOTOMETRY/sdssstar%(ROTATION)s.cat' % {'ROTATION':ROTATION,'OBJNAME':search_params['OBJNAME']}
    galaxycat ='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/PHOTOMETRY/sdssgalaxy%(ROTATION)s.cat' % {'ROTATION':ROTATION,'OBJNAME':search_params['OBJNAME']}

    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':search_params['OBJNAME']}
    illum_path='/nfs/slac/g/ki/ki05/anja/SUBARU/ILLUMINATION/' % {'OBJNAME':search_params['OBJNAME']}
    #os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/') 
    os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/STAR/') 
    os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/GALAXY/') 
    from glob import glob

    print starcat

    for type,cat in [['star',starcat]]: #,['galaxy',galaxycat]]:
        catalog = search_params['pasted_cat'] #exposures[exposure]['pasted_cat']
        ramin,ramax, decmin, decmax = coordinate_limits(catalog)    
        limits = {'ramin':ramin-0.2,'ramax':ramax+0.2,'decmin':decmin-0.2,'decmax':decmax+0.2}
        print ramin,ramax, decmin, decmax
        if len(glob(cat)) == 0:                                      
            #os.system('rm ' + cat)
            image = search_params['files'][0]
            print image
            import retrieve_test
            retrieve_test.run(image,cat,type,limits)

        filter = search_params['filter'] #exposures[exposure]['keywords']['filter']
        #GABODSID = exposures[exposure]['keywords']['GABODSID']
        OBJECT = search_params['OBJECT'] #exposures[exposure]['keywords']['OBJECT']
        print catalog
        outcat = path + 'PHOTOMETRY/ILLUMINATION/' + type + '/' + 'matched_' + SUPA + '_' + filter + '_' + ROTATION + '_' + type + '.cat'
        outcat_dir = path + 'PHOTOMETRY/ILLUMINATION/' + type + '/' + ROTATION + '/' + OBJECT + '/'
        os.system('mkdir -p ' + outcat_dir)
        file = 'matched_' + SUPA + '.cat'               
        linkdir = illum_path + '/' + filter + '/' + ROTATION + '/' + OBJECT + '/'              
        #outcatlink = linkdir + 'matched_' + exposure + '_' + OBJNAME + '_' + GABODSID + '.cat' 
        outcatlink = linkdir + 'matched_' + SUPA + '_' + search_params['OBJNAME'] + '_' + type + '.cat' 
        os.system('mkdir -p ' + linkdir)
        os.system('rm ' + outcat)
        command = 'match_simple.sh ' + catalog + ' ' + cat + ' ' + outcat
        print command
        os.system(command)

        os.system('rm ' + outcatlink)
        command = 'ln -s ' + outcat + ' ' + outcatlink
        print command
        os.system(command)

        save_exposure({'matched_cat_' + type:outcat},SUPA,FLAT_TYPE)

        print type, 'TYPE!'
        print outcat, type
        #exposures[exposure]['matched_cat_' + type] = outcat

    #return exposures

def phot(SUPA,FLAT_TYPE): 
    dict = get_files(SUPA,FLAT_TYPE)
    print dict.keys()
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)

    filter = dict['filter']

    import utilities
    info = {'B':{'filter':'g','color1':'gmr','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0},\
        'W-J-B':{'filter':'g','color1':'gmr','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0},\
        'W-J-V':{'filter':'g','color1':'gmr','color2':'rmi','EXTCOEFF':-0.1202,'COLCOEFF':0.0},\
        'W-C-RC':{'filter':'r','color1':'rmi','color2':'gmr','EXTCOEFF':-0.0925,'COLCOEFF':0.0},\
        'W-C-IC':{'filter':'i','color1':'imz','color2':'rmi','EXTCOEFF':-0.02728,'COLCOEFF':0.0},\
        'W-S-I+':{'filter':'i','color1':'imz','color2':'rmi','EXTCOEFF':-0.02728,'COLCOEFF':0.0},\
        'W-S-Z+':{'filter':'z','color1':'imz','color2':'rmi','EXTCOEFF':0.0,'COLCOEFF':0.0}}
    
    import mk_saturation_plot,os,re
    os.environ['BONN_TARGET'] = search_params['OBJNAME']
    os.environ['INSTRUMENT'] = 'SUBARU'

    stars_0 = []
    stars_90 = []

    ROTATION = dict['ROTATION']
    print ROTATION 
    import os
    ppid = str(os.getppid())
    from glob import glob
    for im_type in ['']: #,'D','S']:
        for type in ['star']: #,'galaxy']:
            file = dict['matched_cat_' + type]
            print file
            print file
            if type == 'galaxy':
                mag='MAG_AUTO' + im_type      
                magerr='MAGERR_AUTO' + im_type
                class_star = "<0.9"
            if type == 'star':
                mag='MAG_APER2' + im_type      
                magerr='MAGERR_APER2' + im_type
                class_star = ">0.9" 
            
            print 'filter', filter
            os.environ['BONN_FILTER'] = filter 
            filt = re.split('_',filter)[0]
            d = info[filt]
            print file
            utilities.run('ldacfilter -i ' +  file + ' -o ' + search_params['TEMPDIR'] + 'good.stars' + ' -t PSSC\
                        -c "(Flag!=-99);"',['' + search_params['TEMPDIR'] + 'good.stars'])

            utilities.run('ldacfilter -i ' + search_params['TEMPDIR'] + 'good.stars -o ' + search_params['TEMPDIR'] + 'good.colors -t PSSC\
                -c "((((SEx_' + mag + '!=0 AND ' + d['color1'] + '<900) AND ' + d['color1'] + '!=0) AND ' + d['color1'] + '>-900) AND ' + d['color1'] + '!=0);"',['' + search_params['TEMPDIR'] + 'good.colors'])
            print '' + search_params['TEMPDIR'] + 'good.colors'
            utilities.run('ldaccalc -i ' + search_params['TEMPDIR'] + 'good.colors -t PSSC -c "(' + d['filter'] + 'mag - SEx_' + mag + ');"  -k FLOAT -n magdiff "" -o ' + search_params['TEMPDIR'] + 'all.diffA.cat' ,[search_params['TEMPDIR'] + 'all.diffA.cat'] )

            median = get_median('' + search_params['TEMPDIR'] + 'all.diffA.cat','magdiff')
            utilities.run('ldacfilter -i ' + search_params['TEMPDIR'] + 'all.diffA.cat -o ' + search_params['TEMPDIR'] + 'all.diffB.cat -t PSSC\
                -c "((magdiff > ' + str(median -1.25) + ') AND (magdiff < ' + str(median + 1.25) + '));"',['' + search_params['TEMPDIR'] + 'good.colors'])
            utilities.run('ldaccalc -i ' + search_params['TEMPDIR'] + 'all.diffB.cat -t PSSC -c "(SEx_MaxVal + SEx_BackGr);"  -k FLOAT -n MaxVal "" -o ' + search_params['TEMPDIR'] + 'all.diff.cat' ,['' + search_params['TEMPDIR'] + 'all.diff.cat'] )
            command = 'ldactoasc -b -q -i ' + search_params['TEMPDIR'] + 'all.diff.cat -t PSSC -k SEx_' + mag + ' ' + d['filter'] + 'mag SEx_FLUX_RADIUS ' + im_type + ' SEx_CLASS_STAR' + im_type + ' ' + d['filter'] + 'err ' + d['color1'] + ' MaxVal > ' + search_params['TEMPDIR'] + 'mk_sat_all'
            #print command
            utilities.run(command,['' + search_params['TEMPDIR'] + 'mk_sat_all'] )
            import commands
            length = commands.getoutput('wc -l ' + search_params['TEMPDIR'] + 'mk_sat_all')
            print 'TOTAL # of STARS:', length
            cuts_to_make = ['MaxVal>27500.0','Clean!=1','SEx_IMAFLAGS_ISO'+im_type + '!=0','SEx_CLASS_STAR'+im_type+ class_star,'SEx_Flag'+im_type+'!=0',]
            files = ['' + search_params['TEMPDIR'] + 'mk_sat_all']
            titles = ['raw']
            for cut in cuts_to_make:
                #print 'making cut:', cut
                cut_name = cut.replace('>','').replace('<','')
                os.system('rm ' + cut_name)
                command = 'ldacfilter -i ' + search_params['TEMPDIR'] + 'all.diff.cat -o ' + search_params['TEMPDIR'] + '' + cut_name + ' -t PSSC\
                       -c "(' + cut + ');"'
                utilities.run(command,['' + search_params['TEMPDIR'] + '' + cut_name])
                import glob
                #print len(glob.glob('' + search_params['TEMPDIR'] + '' + cut_name)), glob.glob('' + search_params['TEMPDIR'] + '' + cut_name)
                if len(glob.glob('' + search_params['TEMPDIR'] + '' + cut_name)) > 0:
                    utilities.run('ldactoasc -b -q -i ' + search_params['TEMPDIR'] + '' + cut_name + '  -t PSSC\
                        -k SEx_' + mag + ' ' + d['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + d['filter'] + 'err ' + d['color1'] + ' > ' + search_params['TEMPDIR'] + '' + cut_name + '.cat',['' + search_params['TEMPDIR'] + '' + cut_name + '.cat'])

                    length = commands.getoutput('wc -l ' + search_params['TEMPDIR'] + '' + cut_name + '.cat')
                    print 'TOTAL # of STARS CUT:', length
                    titles.append(cut_name)
                    files.append('' + search_params['TEMPDIR'] + '' + cut_name + '.cat')
                    #run('ldactoasc -b -q -i cutout1.' + ppid + '  -t PSSC\
                    #        -k Ra Dec > ' + search_params['TEMPDIR'] + '' + outfile,['' + search_params['TEMPDIR'] + '' + outfile])
                    #run('mkreg.pl -c -rad 8 -xcol 0 -ycol 1 -wcs -colour ' + color + ' ' + search_params['TEMPDIR'] + '' + outfile)

            utilities.run('ldacfilter -i ' + search_params['TEMPDIR'] + 'all.diff.cat -o ' + search_params['TEMPDIR'] + 'good.stars -t PSSC\
                    -c "(MaxVal<27500 AND SEx_IMAFLAGS_ISO'+im_type+'=0);"',['' + search_params['TEMPDIR'] + 'good.stars'])

                  #-c "((MaxVal<27500 AND SEx_CLASS_STAR'+im_type+class_star + ') AND SEx_IMAFLAGS_ISO'+im_type+'=0);"',['' + search_params['TEMPDIR'] + 'good.stars'])

                  #-c "(MaxVal<27500 AND SEx_IMAFLAGS_ISO'+im_type+'=0);"',['' + search_params['TEMPDIR'] + 'good.stars' + ppid])
            
            utilities.run('ldactoasc -b -q -i ' + search_params['TEMPDIR'] + 'good.stars  -t PSSC\
                    -k SEx_' + mag + ' ' + d['filter'] + 'mag SEx_FLUX_RADIUS' + im_type + ' SEx_CLASS_STAR'+im_type+' ' + d['filter'] + 'err ' + d['color1'] + ' > ' + search_params['TEMPDIR'] + 'mk_sat',['' + search_params['TEMPDIR'] + 'mk_sat'])
                              
            
            if len(glob.glob('' + search_params['TEMPDIR'] + 'mk_sat')) > 0:
                files.append('' + search_params['TEMPDIR'] + 'mk_sat')
                titles.append('filtered')
            print files, titles
            mk_saturation_plot.mk_saturation_all(files,titles,filter)
            #cutout('' + search_params['TEMPDIR'] + 'good.stars' + ppid,mag)
          
            print mag

            val = raw_input("Look at the saturation plot?")
            if len(val)>0:
                if val[0] == 'y' or val[0] == 'Y':
                    mk_saturation_plot.mk_saturation(search_params['TEMPDIR'] + '/mk_sat',filter)
            
            val = raw_input("Make a box?")
            if len(val)>0:
                if val[0] == 'y' or val[0] == 'Y':
                    mk_saturation_plot.use_box(filter)
                    lower_mag,upper_mag,lower_diff,upper_diff = re.split('\s+',open('box' + filter,'r').readlines()[0])
            
                    utilities.run('ldacfilter -i ' + search_params['TEMPDIR'] + '/good.stars -t PSSC\
                                -c "(((SEx_' + mag + '>' + lower_mag + ') AND (SEx_' + mag + '<' + upper_mag + ')) AND (magdiff>' + lower_diff + ')) AND (magdiff<' + upper_diff + ');"\
                                -o ' + search_params['TEMPDIR'] + '/filt.mag.new.cat',[search_params['TEMPDIR'] + '/filt.mag.new.cat'])

                    raw_input()
                    os.system('mv ' + search_params['TEMPDIR'] + '/filt.mag.new.cat ' + search_params['TEMPDIR'] + '/good.stars')
            #val = [] 
            #val = raw_input("Look at the saturation plot?")
            #if len(val)>0:
            #    if val[0] == 'y' or val[0] == 'Y':
            #        mk_saturation_plot.mk_saturation('' + search_params['TEMPDIR'] + 'mk_sat' + ppid,filter)
                    # make stellar saturation plot                              
            #lower_mag,upper_mag,lower_diff,upper_diff = re.split('\s+',open('box' + filter,'r').readlines()[0])
            lower_mag = str(10)
            upper_mag = str(14.0)
            lower_diff = str(5)
            upper_diff = str(9)
            if type == 'star': 
                lower_mag = str(13.2)
             
            utilities.run('ldactoasc -b -q -i ' + search_params['TEMPDIR'] + 'good.stars -t PSSC -k SEx_Xpos_ABS SEx_Ypos_ABS > ' + search_params['TEMPDIR'] + 'positions',[search_params['TEMPDIR'] + 'positions'] )
            
            utilities.run('ldacaddkey -i ' + search_params['TEMPDIR'] + 'good.stars -o ' + search_params['TEMPDIR'] + 'filt.airmass.cat -t PSSC -k AIRMASS 0.0 FLOAT "" ',[search_params['TEMPDIR'] + 'filt.airmass.cat']  )
                                                                                                                                                                                                                                                                                                          
            utilities.run('ldacfilter -i ' + search_params['TEMPDIR'] + 'filt.airmass.cat -o ' + search_params['TEMPDIR'] + 'filt.crit.cat -t PSSC\
              -c "((magdiff>-900) AND magdiff<900) AND SEx_' + mag + '!=0) ;"',['' + search_params['TEMPDIR'] + 'filt.crit.cat'])
            utilities.run('ldacfilter -i ' + search_params['TEMPDIR'] + 'filt.crit.cat -o ' + search_params['TEMPDIR'] + 'all.colors.cat -t PSSC\
                    -c "(((' + d['color1'] + '<900 AND ' + d['color2'] + '<900) AND ' + d['color1'] + '>-900) AND ' + d['color2'] + '>-900);"',['' + search_params['TEMPDIR'] + 'all.colors.cat'])
            
            utilities.run('ldactoasc -b -q -i ' + search_params['TEMPDIR'] + 'all.colors.cat -t PSSC -k SEx_' + mag + ' ' + d['filter'] + 'mag ' + d['color1'] + ' ' + d['color2'] + ' AIRMASS SEx_' + magerr + ' ' + d['filter'] + 'err SEx_Xpos_ABS SEx_Ypos_ABS > ' + search_params['TEMPDIR'] + 'input.asc' ,['' + search_params['TEMPDIR'] + 'input.asc'] )
            
            import photo_abs_new                
            
            good = photo_abs_new.run_through('illumination',infile='' + search_params['TEMPDIR'] + 'input.asc',output='' + search_params['TEMPDIR'] + 'photo_res',extcoeff=d['color1'],sigmareject=6,step='STEP_1',bandcomp=d['filter'],color1which=d['color1'],color2which=d['color2'])
            
            import astropy, astropy.io.fits as pyfits
            cols = [] 
            for key in ['corr_data','color1_good','color2_good','magErr_good','X_good','Y_good','airmass_good']: 
                cols.append(pyfits.Column(name=key, format='E',array=good[key]))
            hdu = pyfits.PrimaryHDU()
            hdulist = pyfits.HDUList([hdu])
            print cols
            tbhu = pyfits.BinTableHDU.from_columns(cols)
            hdulist.append(tbhu)
            hdulist[1].header['EXTNAME']='STDTAB'
            
            path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':search_params['OBJNAME']}
            outcat = path + 'PHOTOMETRY/ILLUMINATION/fit_' + im_type + '_' + search_params['SUPA'] + '_' +  type + '.cat'                
            os.system('rm ' + outcat)
            hdulist.writeto(outcat)
            save_exposure({'fit_cat_' + im_type + '_' + type: outcat,'airmass_add':'yes'},SUPA,FLAT_TYPE)
            save_fit(good['fits'],im_type,type,SUPA,FLAT_TYPE)

def nightrun():
    import MySQLdb, sys, os, re, time, utilities, pyfits
    from copy import copy
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()

    keystop = ['PPRUN']
    list = reduce(lambda x,y: x + ',' + y, keystop)
    command="SELECT " + list + " from illumination_db where zp_star_ is not null and PPRUN!='KEY_N/A' GROUP BY PPRUN"
    print command
    c.execute(command)
    results=c.fetchall()
    db_keys = describe_db(c)
    h = []
    for line in results: 
        dtop = {}
        for i in range(len(keystop)):
            dtop[keystop[i]] = line[i]

        directory = 'run_' + dtop['PPRUN'] 

        os.system('mkdir ' +  os.environ['sne'] + '/plots/' + directory )
        os.system('rm ' + os.environ['sne'] + '/plots/' + directory + '/*')

        keys = ['OBJNAME','ROTATION']
        list = reduce(lambda x,y: x + ',' + y, keys)
        command="SELECT " + list + " from illumination_db where zp_star_ is not null and PPRUN='" + dtop['PPRUN'] + "' GROUP BY OBJNAME,ROTATION"
        print command
        c.execute(command)
        results=c.fetchall()
        db_keys = describe_db(c)
        h = []
        for line in results: 
            d = {}
            for i in range(len(keys)):
                d[keys[i]] = line[i]
                                                                                                                                                                                                                                                             
            if 1:
                #print d
                if 1:
                    crit = reduce(lambda x,y: x + ' AND ' + y,[str(y) + "='" + str(d[y]) + "'" for y in keys]) 
                    file = directory + '/' + reduce(lambda x,y: x + 'AND' + y,[str(y)[0:4] + "_" + str(d[y])  for y in keys]) 
                    #print crit
                
                    command = "SELECT * from illumination_db where zp_star_ is not null and " + crit
                    #print command
                    c.execute(command)
                    results = c.fetchall()
                    #print results
                    fit_files = [] 
                    for j in range(len(results)):
                        dict = {} 
                        for i in range(len(results[j])):  
                            dict[db_keys[i]] = results[j][i]
                        #print dict['SUPA'], dict['OBJNAME'], dict['pasted_cat'], dict['matched_cat_star']
                        fit_files.append(dict['fit_cat__star'])
                                            
                    #print fit_files
                    dict = get_files(dict['SUPA'],dict['FLAT_TYPE'])
                    #print dict.keys()
                    search_params = initialize(dict['filter'],dict['OBJNAME'])
                    search_params.update(dict)
                                               
                    from copy import copy
                    import photo_abs_new
                    reload(photo_abs_new)
                    files = reduce(lambda x,y: x + ' ' + y,fit_files)
                    #print files
                    tempfile = '' + search_params['TEMPDIR'] + 'spit'
                    command = 'ldacpaste -i ' + files + ' -t STDTAB -o ' + tempfile
                    print command
                    utilities.run(command)
                    hdulist = pyfits.open(tempfile)
                    args = {}
                    for column in hdulist["STDTAB"].columns:
                        args[column.name] = hdulist["STDTAB"].data.field(column.name)
                    photo_abs_new.calcDataIllum(file,search_params['LENGTH1'], search_params['LENGTH2'], 1000, args['corr_data'], args['airmass_good'], args['color1_good'], args['color2_good'], args['magErr_good'], args['X_good'], args['Y_good'],rot=0)
            #except: print 'failed'

def auto_print():
    import MySQLdb, sys, os, re, time, utilities, pyfits
    from copy import copy
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()

    keys = ['FILTER','ROTATION']
    list = reduce(lambda x,y: x + ',' + y, keys)
    command="SELECT " + list + " from illumination_db where zp_star_ is not null and PPRUN!='KEY_N/A' and good_stars_star_ > 400 GROUP BY "+list
    print command
    c.execute(command)
    results=c.fetchall()
    db_keys = describe_db(c)
    h = []
    for line in results: 
        d = {}
        for i in range(len(keys)):
            d[keys[i]] = line[i]

        if 1:
            print d
            if 1:
                crit = reduce(lambda x,y: x + ' AND ' + y,[str(y) + "='" + str(d[y]) + "'" for y in keys]) 
                file = 'filt_' + reduce(lambda x,y: x + 'AND' + y,[str(y)[0:4] + "_" + str(d[y])  for y in keys]) 
                print crit
            
                command = "SELECT * from illumination_db where zp_star_ is not null and " + crit

                print command
                c.execute(command)
                results = c.fetchall()
                print results
                fit_files = [] 
                for j in range(len(results)):
                    dict = {} 
                    for i in range(len(results[j])):  
                        dict[db_keys[i]] = results[j][i]
                    print dict['SUPA'], dict['OBJNAME'], dict['pasted_cat'], dict['matched_cat_star']
                    fit_files.append(dict['fit_cat__star'])
                                        
                print fit_files
                dict = get_files(dict['SUPA'],dict['FLAT_TYPE'])
                print dict.keys()
                search_params = initialize(dict['filter'],dict['OBJNAME'])
                search_params.update(dict)
                                           
                from copy import copy
                import photo_abs_new
                reload(photo_abs_new)
                files = reduce(lambda x,y: x + ' ' + y,fit_files)
                print files
                tempfile = '' + search_params['TEMPDIR'] + 'spit'
                command = 'ldacpaste -i ' + files + ' -t STDTAB -o ' + tempfile
                print command
                utilities.run(command)
                hdulist = pyfits.open(tempfile)
                args = {}
                for column in hdulist["STDTAB"].columns:
                    args[column.name] = hdulist["STDTAB"].data.field(column.name)
                photo_abs_new.calcDataIllum(file,search_params['LENGTH1'], search_params['LENGTH2'], 1000, args['corr_data'], args['airmass_good'], args['color1_good'], args['color2_good'], args['magErr_good'], args['X_good'], args['Y_good'],rot=0)
            #except: print 'failed'

def describe_db(c,db=['illumination_db']):
    if type(db) != type([]):
        db = [db]
    keys = []
    for d in db:
        command = "DESCRIBE " + d 
        #print command
        c.execute(command)
        results = c.fetchall()
        for line in results:
            keys.append(line[0])
    return keys    


def printer():
    import MySQLdb, sys, os, re, time, utilities, pyfits
    from copy import copy
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()
       
    if 1: #for set in [{'OBJNAME':'HDFN', 'filters':['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']},{'OBJNAME':'MACS2243-09', 'filters':['W-J-V','W-C-RC','W-C-IC','W-S-Z+']},{'OBJNAME':'A2219', 'filters':['W-J-B','W-J-V','W-C-RC']}]:
        #OBJNAME = set['OBJNAME']
        if 1: #for filter in set['filters']:
            if 1: #try:
                print keys
                OBJNAME = 'HDFN'                        
                filter = 'W-C-ICSF'
                ROTATION = 1
                command = "select * from illumination_db where OBJNAME='" + OBJNAME + "' and filter='" + filter + "' and fit_cat_galaxy is not null and crfixed='third' and good_stars_star is not null and good_stars_star>10 and ROTATION=" + str(ROTATION)

                command = "select * from illumination_db where SUPA='SUPA0011022' and zp_err_galaxy_D is not null"
                #command = "select * from illumination_db where OBJNAME='" + OBJNAME + "' and filter='" + filter + "' and fit_cat_galaxy is not null and crfixed='third' and ROTATION=" + str(ROTATION) + ' and good_stars_star is not null and good_stars_star>10'

                command = "SELECT * from illumination_db where zp_star_ is not null and ROTATION='0'" # where OBJNAME='HDFN' and filter='W-J-V' and ROTATION=0"



                print command
                c.execute(command)
                results = c.fetchall()
                fit_files = [] 
                for j in range(len(results)):
                    dict = {} 
                    for i in range(len(results[j])):  
                        dict[keys[i]] = results[j][i]
                    print dict['SUPA'], dict['OBJNAME'], dict['pasted_cat'], dict['matched_cat_star']
                    fit_files.append(dict['fit_cat__star'])
                                        
                print fit_files
                dict = get_files(dict['SUPA'],dict['FLAT_TYPE'])
                print dict.keys()
                search_params = initialize(dict['filter'],dict['OBJNAME'])
                search_params.update(dict)
                                           
                from copy import copy
                import photo_abs_new
                reload(photo_abs_new)
                files = reduce(lambda x,y: x + ' ' + y,fit_files)
                print files
                tempfile = '' + search_params['TEMPDIR'] + 'spit'
                command = 'ldacpaste -i ' + files + ' -t STDTAB -o ' + tempfile
                print command
                utilities.run(command)
                hdulist = pyfits.open(tempfile)
                args = {}
                for column in hdulist["STDTAB"].columns:
                    args[column.name] = hdulist["STDTAB"].data.field(column.name)
                file = OBJNAME + '_' + filter + '_' + str(ROTATION)
                file = raw_input('filename?')
                photo_abs_new.calcDataIllum(file,search_params['LENGTH1'], search_params['LENGTH2'], 1000, args['corr_data'], args['airmass_good'], args['color1_good'], args['color2_good'], args['magErr_good'], args['X_good'], args['Y_good'],rot=0)
            #except: print 'failed'

#filter = 'W-C-IC'
import pickle

#filters = ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']

#for filter in filters:
#    exposures_zero = {} 
#    exposures_one = {} 
#    print '$$$$$'
#    print 'separating into different camera rotations'
#    for exposure in exposures.keys(): 
#        print exposure,exposures[exposure]['keywords']['ROTATION']
#        if int(exposures[exposure]['keywords']['ROTATION']) == 1:
#            exposures_one[exposure] = exposures[exposure]
#        if int(exposures[exposure]['keywords']['ROTATION']) == 0:
#            exposures_zero[exposure] = exposures[exposure]
if 0:
    reopen = 0
    save = 0
    if reopen:
        f = open('' + search_params['TEMPDIR'] + 'tmppickle' + OBJNAME + filter,'r')
        m = pickle.Unpickler(f)
        exposures, LENGTH1, LENGTH2 = m.load()
    
        print image.latest
    
    if 1: images = gather_exposures(filter,OBJNAME)
    
    print images
    
    ''' strip down exposure list '''
    for key in exposures.keys():
        print exposures[key]['images']
    
    for image in exposures:
        if 1: image.find_seeing(exposures) # save seeing info?
        if 1: image.sextract(exposures)
        if 1: image.match_simple(exposures,OBJNAME)
        if 1: image.phot(exposures,filter,type,LENGTH1,LENGTH2)
    
    if save:
        f = open('' + search_params['TEMPDIR'] + 'tmppickle' + OBJNAME + filter,'w')
        m = pickle.Pickler(f)
        pickle.dump([exposures,LENGTH1,LENGTH2],m)
        f.close()

def get_sdss(dict):
    import MySQLdb, sys, os, re, time, utilities, pyfits
    from copy import copy
    import os
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)

    starcat ='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/PHOTOMETRY/sdssstar%(ROTATION)s.cat' % {'ROTATION':search_params['ROTATION'],'OBJNAME':search_params['OBJNAME']}
    galaxycat ='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/PHOTOMETRY/sdssgalaxy%(ROTATION)s.cat' % {'ROTATION':search_params['ROTATION'],'OBJNAME':search_params['OBJNAME']}
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':search_params['OBJNAME']}
    illum_path='/nfs/slac/g/ki/ki05/anja/SUBARU/ILLUMINATION/' % {'OBJNAME':search_params['OBJNAME']}
    #os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/') 
    os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/STAR/') 
    os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/GALAXY/') 
    from glob import glob
    print starcat
    for type,cat in [['star',starcat]]: #,['galaxy',galaxycat]]:
        catalog = search_params['pasted_cat'] #exposures[exposure]['pasted_cat']
        ramin,ramax, decmin, decmax = coordinate_limits(catalog)    
        limits = {'ramin':ramin-0.2,'ramax':ramax+0.2,'decmin':decmin-0.2,'decmax':decmax+0.2}
        print ramin,ramax, decmin, decmax
        if len(glob(cat)) == 0:                                      
            #os.system('rm ' + cat)
            image = search_params['files'][0]
            print image
            import retrieve_test
            retrieve_test.run(image,cat,type,limits)

    return starcat



def match_OBJNAME_new(OBJNAME=None,FILTER=None,PPRUN=None):

    associate = {'W-S-I+':['W-C-IC','W-C-RC'],'W-S-G+':['W-J-V','W-J-B'],'W-J-U':['W-J-B']}

    if OBJNAME is None: 
        batchmode = True
    else: batchmode = False
    
    trial = False 
    
    import MySQLdb, sys, os, re, time, utilities, pyfits
    from copy import copy
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()
    db_keys = describe_db(c,['illumination_db','fit_db'])

    keystop = ['PPRUN','ROTATION','OBJNAME']
    list = reduce(lambda x,y: x + ',' + y, keystop)

    if OBJNAME is None:
        command="SELECT * from illumination_db where zp_star_ is not null and PPRUN='2002-06-04_W-J-V' and OBJECT='MACSJ1423.8' GROUP BY OBJNAME,ROTATION"       
        #command="SELECT * from illumination_db where OBJNAME like '%2243%' and filter='W-J-V' GROUP BY OBJNAME,pprun,filter "
        #command="SELECT * from illumination_db where file not like '%CALIB%' and OBJECT like '%1423%' GROUP BY OBJNAME,pprun,filter"
        #command="SELECT * from illumination_db where file not like '%CALIB%' GROUP BY OBJNAME,pprun,filter"
        command="SELECT * from illumination_db where file not like '%CALIB%' GROUP BY OBJNAME,pprun,filter"
        command="SELECT * from illumination_db where file not like '%CALIB%' and SUPA not like '%I' and OBJNAME='MACS1423+24' and filter='W-J-V' GROUP BY OBJNAME,pprun,filter"
        #command="SELECT * from illumination_db where file not like '%CALIB%' and SUPA not like '%I' and OBJNAME like 'MACS1824%' and filter='W-C-IC' and PPRUN !='KEY_N/A' GROUP BY pprun,filter, OBJNAME" # ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
        command="SELECT * from illumination_db where  file not like '%CALIB%' and SUPA not like '%I' and PPRUN !='KEY_N/A' and fixradecCR=1 and PPRUN='2007-07-18_W-J-B' and OBJNAME='MACS2211-03' GROUP BY pprun,filter, OBJNAME ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
        command="SELECT * from illumination_db where  file not like '%CALIB%' and SUPA not like '%I' and PPRUN !='KEY_N/A' and fixradecCR=1 and OBJNAME like 'MACS1423%'  GROUP BY pprun,filter,OBJNAME" # ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
        #command="SELECT * from illumination_db i left join fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.file not like '%CALIB%' and i.SUPA not like '%I' and i.PPRUN !='KEY_N/A' and i.fixradecCR=1 and i.OBJNAME like 'MACS1423%'and f.linearfit=0 GROUP BY i.pprun,i.filter,i.OBJNAME" # ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
        command="SELECT * from illumination_db i left join fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.file not like '%CALIB%' and i.SUPA not like '%I' and i.PPRUN !='KEY_N/A' and i.fixradecCR=1 and i.OBJNAME like 'Zw3146%' and i.filter='W-J-V' GROUP BY i.pprun,i.filter,i.OBJNAME" # ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
        command="SELECT * from illumination_db i left join fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.file not like '%CALIB%' and i.SUPA not like '%I' and i.PPRUN !='KEY_N/A' and  i.OBJNAME like '%MACS0850%' GROUP BY i.OBJNAME limit 1" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
        #command="SELECT * from illumination_db i where OBJNAME like '%MACS0850%' GROUP BY i.OBJNAME ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
        #command="SELECT * from (illumination_db i left join fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME)) left join sdss_db s on (s.OBJNAME = i.OBJNAME) where i.file not like '%CALIB%' and i.SUPA not like '%I' and i.PPRUN !='KEY_N/A' and  f.linearfit is null GROUP BY i.pprun,i.filter,i.OBJNAME ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
        #command="SELECT * from illumination_db i left join fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.file not like '%CALIB%' and i.SUPA not like '%I' and i.PPRUN !='KEY_N/A' and i.fixradecCR=1 and f.linearfit is null and i.PPRUN='2002-12-03_W-C-RC' GROUP BY i.pprun,i.filter,i.OBJNAME" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
    else:
        #command="SELECT * from illumination_db i left join fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.file not like '%CALIB%' and i.SUPA not like '%I' and i.objname='"+OBJNAME+"' and i.pprun='"+PPRUN+"' and i.filter='" + FILTER + "' GROUP BY i.pprun,i.filter,i.OBJNAME ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
        command="SELECT * from illumination_db where  file not like '%CALIB%' and  PPRUN !='KEY_N/A'  and OBJNAME like '" + OBJNAME + "' and FILTER like '" + FILTER + "' and PPRUN='" + PPRUN + "' GROUP BY pprun,filter,OBJNAME" # ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"

    print command
    c.execute(command)
    results=c.fetchall()
    for line in results: 
        'start next'
        if 1: #try: 
            dtop = {}  
            for i in range(len(db_keys)):
                dtop[db_keys[i]] = str(line[i])
            res = re.split('\/',dtop['file'])

            command="SELECT * from illumination_db i left join fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.OBJNAME='" + dtop['OBJNAME'] + "' and i.pasted_cat is not NULL"
            print command
            c.execute(command)
            results2=c.fetchall()
            rotation_runs = {} 
            for line in results2: 
                dict = {}  
                for i in range(len(db_keys)):
                    dict[db_keys[i]] = str(line[i])
                GID = float(dict['GABODSID'])
                config_list = [[575,691,'8'],[691,871,'9'],[817,1309,'10_1'],[1309,3470,'10_2'],[3470,4000,'10_3']]
                CONFIG_IM = None
                for config in config_list:
                    if config[0] < GID < config[1]:
                        CONFIG_IM = config[2]
                        break
                if float(dict['EXPTIME']) > 10.0:
                    if not dict['PPRUN'] in rotation_runs:                                                                                                                               
                        rotation_runs[dict['PPRUN']] = {'ROTATION':{dict['ROTATION']:'yes'},'FILTER':dict['filter'],'CONFIG_IM':CONFIG_IM,'EXPTIME':dict['EXPTIME'],'file':dict['file'],'linearfit':dict['linearfit'],'OBJNAME':dict['OBJNAME'],'catalog':dict['catalog']}
                    rotation_runs[dict['PPRUN']]['ROTATION'][dict['ROTATION']] = 'yes'

            print rotation_runs

            help_list = {} 
            good_list = {}
            for y in rotation_runs.keys():
                if rotation_runs[y]['CONFIG_IM'] != '8' and  rotation_runs[y]['CONFIG_IM'] != '9' and len(rotation_runs[y]['ROTATION'].keys()) > 1:
                    good_list[y] = rotation_runs[y]
                else:
                    help_list[y] = rotation_runs[y]

            orphan_list = {}
            matched_list = {}

            for y in help_list.keys():
                matched = False
                for x in good_list.keys():
                    if help_list[y]['FILTER'] == good_list[x]['FILTER']:
                        matched_list[y] = help_list[y]
                        matched = True
                        break 
                if matched == False:
                    orphan_list[y] = help_list[y]

            print good_list
            print help_list
            print 'good' 
            for key in sorted(good_list.keys()): print key, good_list[key]['EXPTIME'], good_list[key]['file']
            print 'help' 
            for key in sorted(help_list.keys()): print key, help_list[key]['EXPTIME'],help_list[key]['file']
            print 'matched'
            for key in sorted(matched_list.keys()): print key, matched_list[key]['EXPTIME'],matched_list[key]['file']
            print 'orphaned'
            for key in sorted(orphan_list.keys()): print key, orphan_list[key]['EXPTIME'],orphan_list[key]['file']

            ''' first run the good images '''

            for run in good_list.keys():
                if float(good_list[run]['linearfit']) != 1:
                    print good_list[run]['linearfit']
                    match_OBJNAME_specific(good_list[run]['OBJNAME'],goodlist[run]['FILTER'],goodlist[run]['PPRUN'])

            ''' create a master catalog '''
            input = [[good_list[x]['catalog'],good_list[x]['FILTER']] for x in good_list.keys()]    
            print input

            #mk_sdss_like_catalog(input)

            match_many_multi_band(input)

            ''' use the master catalog to fix remaining runs '''

            ## need to figure out which band/color to use
    
            


def match_OBJNAME_specific(OBJNAME,FILTER,PPRUN):

    FILTER = dtop['filter']
    PPRUN = dtop['PPRUN']
    OBJNAME = dtop['OBJNAME']

    command="SELECT * from illumination_db where  OBJNAME='" + dtop['OBJNAME'] + "' pasted_cat is not NULL"
    c.execute(command)
    results2=c.fetchall()
    for line in results2: 
        dtop = {}  
        for i in range(len(db_keys)):
            dtop[db_keys[i]] = str(line[i])
        res = re.split('\/',dtop['file'])
        for j in range(len(res)):
            if res[j] == 'SUBARU':
                break
        
    print dtop['filter'], dtop['PPRUN'], dtop['OBJNAME'], CLUSTER 
    save_fit({'PPRUN':PPRUN,'OBJNAME':OBJNAME,'FILTER':FILTER})
    keys = ['SUPA','OBJNAME','ROTATION','PPRUN','pasted_cat','filter','ROTATION','files']
    list = reduce(lambda x,y: x + ',' + y, keys)
    #command="SELECT * from illumination_db where zp_star_ is not null and OBJNAME='"+dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "'"#+ "' GROUP BY OBJNAME,ROTATION"

    command="SELECT * from illumination_db where  OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and filter like '" + dtop['filter'] + "' and pasted_cat is not NULL"
    print command
    c.execute(command)
    results=c.fetchall()
    print results
    field = []
    info = []
    for line in results: 
        d = {}
        for i in range(len(db_keys)):
            d[db_keys[i]] = str(line[i])
                                                                                                                                                                             
        ana = '' #raw_input('analyze ' + d['SUPA'] + '?')
        if len(ana) > 0:
            if ana[0] == 'y':
                analyze(d['SUPA'],d['FLAT_TYPE'])

        ''' use SCAMP CRVAL, etc. ''' 
        a= 'okay'
        if int(float(d['fixradecCR'])) != 1: # or str(d['fixradecCR']) == '-1':
            a = fix_radec(d['SUPA'],d['FLAT_TYPE'])

        if a!='noheader':
            key = str(int(float(d['ROTATION']))) + '$' + d['SUPA'] + '$' 
            field.append({'key':key,'pasted_cat':d['pasted_cat'],'ROT':d['ROTATION']})
            info.append([d['ROTATION'],d['SUPA'],d['OBJNAME']])

    print field

    if 0:
        linear_fit(OBJNAME,FILTER,PPRUN)
    #if len(results) > 0:
    if 1:    
        if d['CRVAL1'] == 'None':
            length(d['SUPA'],d['FLAT_TYPE'])
                
        cov,galaxycat,starcat = sdss_coverage(d['SUPA'],d['FLAT_TYPE']) 

        print cov
                                                                                                                                                                             
        ''' get SDSS matched stars, use photometric calibration to remove color term ''' 
        if 1: #SDSS:
            if cov: #d['starcat'] == 'None':
                print d['SUPA'], d['FLAT_TYPE'], d['OBJECT'], d['CRVAL1'], d['CRVAL2']
                ''' retrieve SDSS catalog '''
                print d['pasted_cat']
                #get_sdss_obj(d['SUPA'],d['FLAT_TYPE'])
                sdssmatch = get_cats_ready(d['SUPA'],d['FLAT_TYPE'],galaxycat,starcat)
                #apply_photometric_calibration(d['SUPA'],d['FLAT_TYPE'],starcat) 
                ''' convert SDSS catalog to smaller form -- don't take out color terms -- those are fit for in final fit '''
                #convert_SDSS_cat(d['SUPA'],d['FLAT_TYPE']) 
                print 'calibration done'
            d = get_files(d['SUPA'],d['FLAT_TYPE'])
            print d
    #a = raw_input('match?')
    #if 1: #len(a) > 0:
    #    if 1: #a[0] == 'y':                                             
            #sdss = get_sdss(d)
            print field
            input = [[x['pasted_cat'],x['key'],x['ROT']] for x in field]    

            print input
            print len(input)

            if len(input) > 8: 
                input_short = []
                rot0 = filter(lambda x:x[1][0]=='0',input)[0:3]
                rot1 = filter(lambda x:x[1][0]=='1',input)[0:3]
                input = rot0 + rot1
                print 'new', input

            print input
            print len(input)
            #input = add_correction_new(input,OBJNAME,FILTER,PPRUN)
            print input
            print sdssmatch, '/nfs/slac/g/ki/ki05/anja/SUBARU/MACS1423+24/PHOTOMETRY/ILLUMINATION/catalog_2002-06-04_W-J-V.cat'
            
            global true_sdss
            true_sdss = True 

            if cov: 
                #input.append([galaxysdssmatch,'SDSS',None])
                if true_sdss:
                    input.append([sdssmatch,'SDSS',None])
                #input.append(['/nfs/slac/g/ki/ki05/anja/SUBARU/MACS2129-07/PHOTOMETRY/ILLUMINATION/catalog_2002-06-04_W-J-V.cat','SDSS',None])
                #input.append(['/nfs/slac/g/ki/ki05/anja/SUBARU/MACS1423+24/PHOTOMETRY/ILLUMINATION/catalog_2002-06-04_W-J-V.cat' , 'SDSS',None])
                if not true_sdss:
                    input.append(['/nfs/slac/g/ki/ki05/anja/SUBARU/MACS0911+17/PHOTOMETRY/ILLUMINATION/catalog_2003-04-04_W-J-V.cat','SDSS',None])
            print input,cov
            match_many(input)
            print 'matched'
            linear_fit(OBJNAME,FILTER,PPRUN)

    #script = reduce(lambda x,y: x + ' ' + y,[x['pasted_cat'] + ' ' + x['key'] for x in field])
    print '\n\nDONE'
    if batchmode:
        os.system('rm -rf ' + tmpdir)
    #raise /
#except KeyboardInterrupt:
#    raise 
#except: 
#    print traceback.print_exc(file=sys.stdout)
#    print 'fail'
#    if batchmode:
#        os.system('rm -rf ' + tmpdir)
#    if trial:
#        raise Exception


def match_OBJNAME(OBJNAME=None,FILTER=None,PPRUN=None):

    if OBJNAME is None: 
        batchmode = True
    else: batchmode = False
    
    trial = False 
    start = 1

    while True: 
        import MySQLdb, sys, os, re, time, utilities, pyfits                                       
        from copy import copy
        db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
        c = db2.cursor()
        db_keys_f = describe_db(c,['illumination_db'])
                                                                                                   
        keystop = ['PPRUN','ROTATION','OBJNAME']
        list = reduce(lambda x,y: x + ',' + y, keystop)

        if 1: #OBJNAME is None or start == 0:
            command="SELECT * from illumination_db where zp_star_ is not null and PPRUN='2002-06-04_W-J-V' and OBJECT='MACSJ1423.8' GROUP BY OBJNAME,ROTATION"       
            #command="SELECT * from illumination_db where OBJNAME like '%2243%' and filter='W-J-V' GROUP BY OBJNAME,pprun,filter "
            #command="SELECT * from illumination_db where file not like '%CALIB%' and OBJECT like '%1423%' GROUP BY OBJNAME,pprun,filter"
            #command="SELECT * from illumination_db where file not like '%CALIB%' GROUP BY OBJNAME,pprun,filter"
            command="SELECT * from illumination_db where file not like '%CALIB%' GROUP BY OBJNAME,pprun,filter"
            command="SELECT * from illumination_db where file not like '%CALIB%' and SUPA not like '%I' and OBJNAME='MACS1423+24' and filter='W-J-V' GROUP BY OBJNAME,pprun,filter"
            #command="SELECT * from illumination_db where file not like '%CALIB%' and SUPA not like '%I' and OBJNAME like 'MACS1824%' and filter='W-C-IC' and PPRUN !='KEY_N/A' GROUP BY pprun,filter, OBJNAME" # ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
            command="SELECT * from illumination_db where  file not like '%CALIB%' and SUPA not like '%I' and PPRUN !='KEY_N/A' and fixradecCR=1 and PPRUN='2007-07-18_W-J-B' and OBJNAME='MACS2211-03' GROUP BY pprun,filter, OBJNAME ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
            command="SELECT * from illumination_db where  file not like '%CALIB%' and SUPA not like '%I' and PPRUN !='KEY_N/A' and fixradecCR=1 and OBJNAME like 'MACS1423%'  GROUP BY pprun,filter,OBJNAME" # ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
            #command="SELECT * from illumination_db i left join fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.file not like '%CALIB%' and i.SUPA not like '%I' and i.PPRUN !='KEY_N/A' and i.fixradecCR=1 and i.OBJNAME like 'MACS1423%'and f.linearfit=0 GROUP BY i.pprun,i.filter,i.OBJNAME" # ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
            command="SELECT * from illumination_db i left join fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.file not like '%CALIB%' and i.SUPA not like '%I' and i.PPRUN !='KEY_N/A' and i.fixradecCR=1 and i.OBJNAME like 'Zw3146%' and i.filter='W-J-V' GROUP BY i.pprun,i.filter,i.OBJNAME" # ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
            command="SELECT * from illumination_db i left join fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.file not like '%CALIB%' and i.SUPA not like '%I' and i.PPRUN !='KEY_N/A' and  (f.linearfit!=1 or f.linearfit is null) GROUP BY i.pprun,i.filter,i.OBJNAME ORDER BY RAND() " # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"

            command="  select i.* from temp i left join fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.PPRUN !='KEY_N/A' and i.file not like '%CALIB%' and (f.linearfit!=1 or f.linearfit is null) GROUP BY i.pprun,i.filter,i.OBJNAME ORDER BY RAND() " # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
            #command="SELECT * from fit_db where (linearfit!=1 or linearfit is null) GROUP BY pprun,filter,OBJNAME ORDER BY RAND() limit 1 " # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
            #command="SELECT * from (illumination_db i left join fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME)) left join sdss_db s on (s.OBJNAME = i.OBJNAME) where i.file not like '%CALIB%' and i.SUPA not like '%I' and i.PPRUN !='KEY_N/A' and  f.linearfit is null GROUP BY i.pprun,i.filter,i.OBJNAME ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
            #command="SELECT * from illumination_db i left join fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.file not like '%CALIB%' and i.SUPA not like '%I' and i.PPRUN !='KEY_N/A' and i.fixradecCR=1 and f.linearfit is null and i.PPRUN='2002-12-03_W-C-RC' GROUP BY i.pprun,i.filter,i.OBJNAME" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
        #else:
        #    command="SELECT * from illumination_db i left join fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.file not like '%CALIB%' and i.SUPA not like '%I' and i.objname='"+OBJNAME+"' and i.pprun='"+PPRUN+"' and i.filter='" + FILTER + "' GROUP BY i.pprun,i.filter,i.OBJNAME ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"

            #command="SELECT * from fit_db where (linearfit!=1 or linearfit is null) and objname='"+OBJNAME+"' and pprun='"+PPRUN+"' and filter='" + FILTER + "' GROUP BY pprun,filter,OBJNAME ORDER BY RAND() limit 1 " # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"

            #command="SELECT * from fit_db where objname='"+OBJNAME+"' and pprun='"+PPRUN+"' and filter='" + FILTER + "' GROUP BY pprun,filter,OBJNAME ORDER BY RAND() limit 1 " # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
        #    command="SELECT * from illumination_db where  file not like '%CALIB%' and  PPRUN !='KEY_N/A'  and OBJNAME like '" + OBJNAME + "' and FILTER like '" + FILTER + "' and PPRUN='" + PPRUN + "' GROUP BY pprun,filter,OBJNAME" # ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
        start = 0
        print command
        c.execute(command)
        f_results=c.fetchall()
        #for line in results[0]:
        print len(f_results)
        print f_results[0]

        if len(f_results) == 0: break
        if len(f_results) > 0: 
            line = f_results[0]
            'start next'
            try: 
                global tmpdir
                dtop = {}  
                for i in range(len(db_keys_f)):
                    dtop[db_keys_f[i]] = str(line[i])
                #res = re.split('\/',dtop['file'])
                #for j in range(len(res)):
                #    if res[j] == 'SUBARU':
                #        break
                FILTER = dtop['filter']
                PPRUN = dtop['PPRUN']
                OBJNAME = dtop['OBJNAME']
              
                print dtop['filter'], dtop['PPRUN'], dtop['OBJNAME']

                save_fit({'PPRUN':PPRUN,'OBJNAME':OBJNAME,'FILTER':FILTER})
                keys = ['SUPA','OBJNAME','ROTATION','PPRUN','pasted_cat','filter','ROTATION','files']
                list = reduce(lambda x,y: x + ',' + y, keys)
                #command="SELECT * from illumination_db where zp_star_ is not null and OBJNAME='"+dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "'"#+ "' GROUP BY OBJNAME,ROTATION"
                                                                                                                                                                                                                                                                                                                                                                                                    
                db_keys = describe_db(c,['illumination_db'])
                command="SELECT * from illumination_db where  OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and filter like '" + dtop['filter'] + "' and pasted_cat is not NULL"
                print command
                c.execute(command)
                results=c.fetchall()
                field = []
                info = []
                if len(results) > 0:
                    for line in results:                                                                                                                                                                                                                                                                                                                                                                 
                        d = {}
                        for i in range(len(db_keys)):
                            d[db_keys[i]] = str(line[i])
                                                                                                                                                                                             
                        ana = '' #raw_input('analyze ' + d['SUPA'] + '?')
                        if len(ana) > 0:
                            if ana[0] == 'y':
                                analyze(d['SUPA'],d['FLAT_TYPE'])
                                                                                                                                                                                                                                                                                                                                                                                                        
                        ''' use SCAMP CRVAL, etc. ''' 
                        a= 'okay'
                        if int(float(d['fixradecCR'])) != 1: # or str(d['fixradecCR']) == '-1':
                            a = fix_radec(d['SUPA'],d['FLAT_TYPE'])
                                                                                                                                                                                                                                                                                                                                                                                                        
                        if a!='noheader':
                            key = str(int(float(d['ROTATION']))) + '$' + d['SUPA'] + '$' 
                            field.append({'key':key,'pasted_cat':d['pasted_cat'],'ROT':d['ROTATION']})
                            info.append([d['ROTATION'],d['SUPA'],d['OBJNAME']])
                                                                                                                                                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                                                                                                                        
                    if 0:
                        linear_fit(OBJNAME,FILTER,PPRUN)
                    #if len(results) > 0:
                    if 1:    
                        if d['CRVAL1'] == 'None':
                            length(d['SUPA'],d['FLAT_TYPE'])
                                
                        cov,galaxycat,starcat = sdss_coverage(d['SUPA'],d['FLAT_TYPE']) 
                                                                                                                                                                                                                                                                                                                                                                                                        
                        print cov
                                                                                                                                                                                             
                        ''' get SDSS matched stars, use photometric calibration to remove color term ''' 
                        if 1: #SDSS:
                            if cov: #d['starcat'] == 'None':
                                print d['SUPA'], d['FLAT_TYPE'], d['OBJECT'], d['CRVAL1'], d['CRVAL2']
                                ''' retrieve SDSS catalog '''
                                print d['pasted_cat']
                                #get_sdss_obj(d['SUPA'],d['FLAT_TYPE'])
                                sdssmatch = get_cats_ready(d['SUPA'],d['FLAT_TYPE'],galaxycat,starcat)
                                #apply_photometric_calibration(d['SUPA'],d['FLAT_TYPE'],starcat) 
                                ''' convert SDSS catalog to smaller form -- don't take out color terms -- those are fit for in final fit '''
                                #convert_SDSS_cat(d['SUPA'],d['FLAT_TYPE']) 
                                print 'calibration done'
                            d = get_files(d['SUPA'],d['FLAT_TYPE'])
                            print d
                    #if 1: #len(a) > 0:
                    #    if 1: #a[0] == 'y':                                             
                            #sdss = get_sdss(d)
                            print field
                            input = [[x['pasted_cat'],x['key'],x['ROT']] for x in field]    
                                                                                                                                                                                                                                                                                                                                                                                                        
                            print input
                            print len(input)
                                                                                                                                                                                                                                                                                                                                                                                                        
                            if len(input) > 8: 
                                input_short = []
                                i = 0
                                while len(input_short) < 8 and len(input_short)<len(input):
                                    i += 1
                                    rot0 = filter(lambda x:float(x[1][0])==0,input)[0:i] 
                                    rot1 = filter(lambda x:float(x[1][0])==1,input)[0:i]
                                    rot2 = filter(lambda x:float(x[1][0])==2,input)[0:i]
                                    input_short = rot0 + rot1 + rot2
                                input = input_short
                                print 'new', input
                            #input = add_correction_new(input,OBJNAME,FILTER,PPRUN)
                            #print sdssmatch, '/nfs/slac/g/ki/ki05/anja/SUBARU/MACS1423+24/PHOTOMETRY/ILLUMINATION/catalog_2002-06-04_W-J-V.cat'
                            
                            global true_sdss
                            true_sdss = True 
                            if cov: 
                                #input.append([galaxysdssmatch,'SDSS',None])
                                if true_sdss:
                                    input.append([sdssmatch,'SDSS',None])
                                #input.append(['/nfs/slac/g/ki/ki05/anja/SUBARU/MACS2129-07/PHOTOMETRY/ILLUMINATION/catalog_2002-06-04_W-J-V.cat','SDSS',None])
                                #input.append(['/nfs/slac/g/ki/ki05/anja/SUBARU/MACS1423+24/PHOTOMETRY/ILLUMINATION/catalog_2002-06-04_W-J-V.cat' , 'SDSS',None])
                                if not true_sdss:
                                    input.append(['/nfs/slac/g/ki/ki05/anja/SUBARU/MACS0911+17/PHOTOMETRY/ILLUMINATION/catalog_2003-04-04_W-J-V.cat','SDSS',None])
                            print input,cov
                            match_many(input)
                            print 'matched'
                            linear_fit(OBJNAME,FILTER,PPRUN)
                                                                                                                                                                                                                                                                                                                                                                                                    
                #script = reduce(lambda x,y: x + ' ' + y,[x['pasted_cat'] + ' ' + x['key'] for x in field])
                print '\n\nDONE'
                if batchmode:
                    os.system('rm -rf ' + tmpdir)
                #raise /
            except KeyboardInterrupt:
                raise 
            except: 
                #print d['PPRUN'], d['OBJNAME'] 
                print traceback.print_exc(file=sys.stdout)
                print 'fail'
                if batchmode:
                    os.system('rm -rf ' + tmpdir)
                if trial:
                    raise Exception

def add_correction_new(cat_list,OBJNAME,FILTER,PPRUN):

    import scipy, re, string, os

    ''' create chebychev polynomials '''
    cheby_x = [{'n':'0x','f':lambda x,y:1.},{'n':'1x','f':lambda x,y:x},{'n':'2x','f':lambda x,y:2*x**2-1},{'n':'3x','f':lambda x,y:4*x**3.-3*x}] 
    cheby_y = [{'n':'0y','f':lambda x,y:1.},{'n':'1y','f':lambda x,y:y},{'n':'2y','f':lambda x,y:2*y**2-1},{'n':'3y','f':lambda x,y:4*y**3.-3*y}]
    cheby_terms = []
    cheby_terms_no_linear = []
    for tx in cheby_x:
        for ty in cheby_y:
            if not ((tx['n'] == '0x' and ty['n'] == '0y')): # or (tx['n'] == '0x' and ty['n'] == '1y') or (tx['n'] == '1x' and ty['n'] == '0y')) :
                cheby_terms.append({'n':tx['n'] + ty['n'],'fx':tx['f'],'fy':ty['f']})
            if not ((tx['n'] == '0x' and ty['n'] == '0y') or (tx['n'] == '0x' and ty['n'] == '1y') or (tx['n'] == '1x' and ty['n'] == '0y')) :
                cheby_terms_no_linear.append({'n':tx['n'] + ty['n'],'fx':tx['f'],'fy':ty['f']})
   
    cov = 1

    if cov:
        samples = [['sdss',cheby_terms,True]] #,['nosdss',cheby_terms_no_linear,False]] #[['nosdss',cheby_terms_no_linear],['sdss',cheby_terms]]
    else: 
        samples = [['nosdss',cheby_terms_no_linear,False]]

    sample = 'sdss'
    sample_size = 'all'
    import re, time                                                                                                                
    dt = get_a_file(OBJNAME,FILTER,PPRUN)                
    d = get_fits(OBJNAME,FILTER,PPRUN)                
    print d.keys()
    column_prefix = sample+'$'+sample_size+'$'
    position_columns_names = re.split('\,',d[column_prefix + 'positioncolumns']) 
    print position_columns_names, 'position_columns_names'
    fitvars = {}
    cheby_terms_dict = {}
    print column_prefix, position_columns_names
    for ele in position_columns_names:                      
        print ele
        if type(ele) != type({}):
            ele = {'name':ele}
        res = re.split('$',ele['name'])
        if string.find(ele['name'],'zp_image') == -1:
            fitvars[ele['name']] = float(d[sample+'$'+sample_size+'$'+ele['name']]) 
            for term in cheby_terms:
                if term['n'] == ele['name'][2:]:
                    cheby_terms_dict[term['n']] = term 
                                                                                     
    zp_images = re.split(',',d[sample+'$'+sample_size+'$zp_images'])
    zp_images_names = re.split(',',d[sample+'$'+sample_size+'$zp_images_names'])
    
    for i in range(len(zp_images)):
        fitvars[zp_images_names[i]] = float(zp_images[i])
    
    cheby_terms_use =  [cheby_terms_dict[k] for k in cheby_terms_dict.keys()]

    print cheby_terms_use, fitvars

    CHIPS = [int(x) for x in re.split(',',dt['CHIPS'])]
    LENGTH1, LENGTH2 = dt['LENGTH1'], dt['LENGTH2']

    per_chip = True

    coord_conv_x = lambda x:(2.*x-0-LENGTH1)/(LENGTH1-0) 
    coord_conv_y = lambda x:(2.*x-0-LENGTH2)/(LENGTH2-0) 

    ''' make images of illumination corrections '''                                                                  
    cat_grads = []
    for cat in cat_list:
        
        import astropy, astropy.io.fits as pyfits
        p = pyfits.open(cat[0])
        tab = p["OBJECTS"].data
        print str(type(tab))
        if str(type(tab)) != "<type 'NoneType'>":
            print tab.field('MAG_AUTO')[0:10]                          
                                                                       
            ROT = str(int(float(cat[2])))
                                                                       
            print cat
            
                                                    
            x = coord_conv_x(scipy.array(tab.field('Xpos_ABS')[:]))
            y = coord_conv_y(scipy.array(tab.field('Ypos_ABS')[:]))
                                                                       
            CHIPS = tab.field('CHIP')
                                                                       
            chip_zps = []
            for i in range(len(CHIPS)):
                chip_zps.append(float(fitvars['zp_' + str(int(CHIPS[i]))]))
                                                                       
            chip_zps = scipy.array(chip_zps)
                                                                       
            ''' save pattern w/ chip zps '''
                                                                       
            trial = False 
            children = []
            
            ''' correct w/ polynomial '''
            epsilonC = 0
            index = 0                                                  
            for term in cheby_terms_use:
                index += 1
                print index, ROT, term, fitvars[str(ROT)+'$'+term['n']]
                epsilonC += fitvars[str(ROT)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)
            ''' add the zeropoint '''
            epsilonC += chip_zps 
            ''' save pattern w/o chip zps '''

            print LENGTH1, LENGTH2
            print epsilonC[2000:2020]
            print x[2000:2020]
            print y[2000:2020]
            print tab.field('Xpos_ABS')[2000:2020]
            print tab.field('Ypos_ABS')[2000:2020]


            tab.field('MAG_AUTO')[:] = tab.field('MAG_AUTO')[:] - epsilonC
            print tab.field('MAG_AUTO')[0:20]
            new_name = cat[0].replace('.cat','.gradient.cat')
            os.system('rm ' + new_name)
            p.writeto(new_name)
            cat_grads.append([new_name,cat[1],ROT])
    return cat_grads 




    
def add_gradient(cat_list):
    import astropy, astropy.io.fits as pyfits, os
    cat_grads = []
    for cat in cat_list:
        print cat
        p = pyfits.open(cat[0])
        tab = p["OBJECTS"].data
        print tab.field('MAG_AUTO')[0:10] 
        tab.field('MAG_AUTO')[:] = tab.field('MAG_AUTO') + 5./10000.*tab.field('Xpos_ABS')
        new_name = cat[0].replace('.cat','.gradient.cat')
        os.system('rm ' + new_name)
        p.writeto(new_name)
        cat_grads.append([new_name,cat[1]])
    return cat_grads 

def add_correction(cat_list):
    import astropy, astropy.io.fits as pyfits, os
    cat_grads = []
    
    EXPS = getTableInfo()

    cheby_x = [{'n':'0x','f':lambda x,y:1.},{'n':'1x','f':lambda x,y:x},{'n':'2x','f':lambda x,y:2*x**2-1},{'n':'3x','f':lambda x,y:4*x**3.-3*x}] 

    cheby_y = [{'n':'0y','f':lambda x,y:1.},{'n':'1y','f':lambda x,y:y},{'n':'2y','f':lambda x,y:2*y**2-1},{'n':'3y','f':lambda x,y:4*y**3.-3*y}]

    #func = lambda x,y: [cheby_x_dict[f[0:2]](x,y)*cheby_y_dict[f[2:]](x,y) for f in fitvars]

    import scipy
    x = scipy.array([-0.5,0,1])
    y = scipy.array([-0.5,0,0.5])
    
    for cat in cat_list:
        for ROT in EXPS.keys():
            for SUPA in EXPS[ROT]:
                import re
                print SUPA, cat
                res = re.split('$',cat[1])
                file = res[1]
                print file, cat 
                if file == SUPA: rotation = ROT

        import pickle              
        f=open(tmpdir + '/fitvars' + rotation,'r')
        m=pickle.Unpickler(f)
        fitvars=m.load()

        cheby_terms = []
        for tx in cheby_x:
            for ty in cheby_y:
                if fitvars.has_key(tx['n']+ty['n']): # not ((tx['n'] == '0x' and ty['n'] == '0y')): # or (tx['n'] == '0x' and ty['n'] == '1y') or (tx['n'] == '1x' and ty['n'] == '0y')) :
                    cheby_terms.append({'n':tx['n'] + ty['n'],'fx':tx['f'],'fy':ty['f']})

        print EXPS
            
        print cat
        p = pyfits.open(cat[0])
        tab = p["OBJECTS"].data
        print tab.field('MAG_AUTO')[0:10] 

        x = coord_conv_x(tab.field('Xpos_ABS'))
        y = coord_conv_y(tab.field('Ypos_ABS'))

        epsilon = 0                                                       
        for term in cheby_terms:
            epsilon += fitvars[term['n']]*term['fx'](x,y)*term['fy'](x,y)

        print epsilon[0:20]
        tab.field('MAG_AUTO')[:] = tab.field('MAG_AUTO')[:] - epsilon 
        print tab.field('MAG_AUTO')[0:20]
        new_name = cat[0].replace('.cat','.gradient.cat')
        os.system('rm ' + new_name)
        p.writeto(new_name)
        cat_grads.append([new_name,cat[1]])
    return cat_grads 

def make_ssc_config(list):

    ofile = tmpdir + '/tmp.cat'
    out = open(tmpdir + '/tmp.ssc','w')
    import os, string, re

    keys = []
    i = -1 
    for file_name,prefix in list:
        i += 1                                                                                                                        
        print file_name
        os.system('ldacdesc -t OBJECTS -i ' + file_name + ' > ' + ofile)
        file = open(ofile,'r').readlines()
        for line in file:
            if string.find(line,"Key name") != -1:
                red = re.split('\.+',line)            
                key = red[1].replace(' ','').replace('\n','')
                out_key = prefix + key
                out.write("COL_NAME = " + out_key + '\nCOL_INPUT = ' + key + '\nCOL_MERGE = AVE_REG\nCOL_CHAN = ' + str(i) + "\n#\n")
                #print key
            keys.append(key)

    out.close()

def make_ssc_multi_color(list):

    ofile = tmpdir + '/tmp.cat'
    out = open(tmpdir + '/tmp.ssc','w')
    import os, string, re

    #key_list = ['CHIP','Flag','MAG_AUTO','MAGERR_AUTO','MAG_APER2','MAGERR_APER2','Xpos_ABS','Ypos_ABS','CLASS_STAR','MaxVal','BackGr','stdMag_corr','stdMagErr_corr','stdMagColor_corr','stdMagClean_corr','stdMagStar_corr','Star_corr','ALPHA_J2000','DELTA_J2000']

    Ns = []
    keys = {} 
    i = -1 
    for file_name,filter in list:
        key_list = [['ALPHA_J2000','ALPHA_J2000'],['DELTA_J2000','DELTA_J2000'],['stdMag_corr',filter+'mag'],['stdMagErr_corr',filter+'err'],['stdMagClean_corr','Clean'],]
        i += 1
        Ns.append('N_0' + str(i) + ' = 1)')
        print file_name
        for key in key_list:
            out_key = key[1] 
            in_key = key[0]
            #if reduce(lambda x,y: x+ y, [string.find(out_key,k)!=-1 for k in key_list]):
            if not key[1] in keys: 
                out.write("COL_NAME = " + out_key + '\nCOL_INPUT = ' + in_key + '\nCOL_MERGE = AVE_REG\nCOL_CHAN = ' + str(i) + "\n#\n")
            print key
            keys[key[1]] = True

    out.close()
    print out 

    return Ns


def make_ssc_config_few(list):

    ofile = tmpdir + '/tmp.cat'
    out = open(tmpdir + '/tmp.ssc','w')
    import os, string, re

    key_list = ['CHIP','Flag','MAG_AUTO','MAGERR_AUTO','MAG_APER2','MAGERR_APER2','Xpos_ABS','Ypos_ABS','CLASS_STAR','MaxVal','BackGr','stdMag_corr','stdMagErr_corr','stdMagColor_corr','stdMagClean_corr','stdMagStar_corr','Star_corr','ALPHA_J2000','DELTA_J2000']
    keys = []
    i = -1 
    for file_name,prefix,rot in list:
        i += 1
        print file_name
        os.system('ldacdesc -t OBJECTS -i ' + file_name + ' > ' + ofile)
        file = open(ofile,'r').readlines()
        for line in file:
            if string.find(line,"Key name") != -1 :
                red = re.split('\.+',line)
                key = red[1].replace(' ','').replace('\n','')
                out_key = prefix + key
                if reduce(lambda x,y: x+ y, [string.find(out_key,k)!=-1 for k in key_list]):
                    out.write("COL_NAME = " + out_key + '\nCOL_INPUT = ' + key + '\nCOL_MERGE = AVE_REG\nCOL_CHAN = ' + str(i) + "\n#\n")
                print key
                keys.append(key)

    out.close()

def make_ssc_config_colors(list):

    ofile = tmpdir + '/tmp.cat'
    out = open(tmpdir + '/tmp.ssc','w')
    import os, string, re

    keys = []
    i = -1 
    for file_name,prefix in list:
        i += 1
        print file_name
        os.system('ldacdesc -t OBJECTS -i ' + file_name + ' > ' + ofile)
        file = open(ofile,'r').readlines()
        for line in file:
            if string.find(line,"Key name") != -1:
                red = re.split('\.+',line)
                key = red[1].replace(' ','').replace('\n','')
                out_key = key + '_' + prefix
                out.write("COL_NAME = " + out_key + '\nCOL_INPUT = ' + key + '\nCOL_MERGE = AVE_REG\nCOL_CHAN = ' + str(i) + "\n#\n")
                #print key
            keys.append(key)

    out.close()

def threesec():
    list = [['/nfs/slac/g/ki/ki05/anja/SUBARU/MACS0417-11/PHOTOMETRY/ILLUMINATION/pasted_SUPA0105807_W-C-RC_2009-01-23_CALIB_0.0.cat','W-C-RC'],['/nfs/slac/g/ki/ki05/anja/SUBARU/MACS0417-11/PHOTOMETRY/ILLUMINATION/pasted_SUPA0105787_W-J-V_2009-01-23_CALIB_0.0.cat','W-J-V'],['/nfs/slac/g/ki/ki05/anja/SUBARU/MACS0417-11/PHOTOMETRY/ILLUMINATION/pasted_SUPA0050786_W-C-IC_2006-12-21_CALIB_0.0.cat','W-C-IC']]
    match_many(list,True)

def match_many(list,color=False):

    if color:
        make_ssc_config_colors(list) 
        print color
    else:
        make_ssc_config_few(list) 


    import os 
    os.system('rm -rf ' + tmpdir + '/assoc/')
    os.system('mkdir ' + tmpdir + '/assoc/')

    import os
    files = []
    for file,prefix,rot in list:
        print file

        #os.system('ldactoasc -i ' + file + ' -t OBJECTS -k ALPHA_J2000 DELTA_J2000 > ' +  file[-11:] + '.cat')
        #os.system('mkreg.pl -c -rad 3 -xcol 0 -ycol 1 -wcs ' +  file[-11:] + '.cat')


        command = 'ldacaddkey -i %(inputcat)s -t OBJECTS -o %(outputcat)s -k A_WCS_assoc 0.0003 FLOAT "" \
                                        B_WCS_assoc 0.0003 FLOAT "" \
                                        Theta_assoc 0.0 FLOAT "" \
                                        Flag_assoc 0 SHORT "" ' % {'inputcat':file,'outputcat':file + '.assoc1'}
        os.system(command)
    
        #command = 'ldacrenkey -i %(inputcat)s -o %(outputcat)s -k ALPHA_J2000 Ra DELTA_J2000 Dec' % {'inputcat':file + '.assoc1','outputcat':file+'.assoc2'} 
        #os.system(command)
        files.append(file+'.assoc1')
    import re
    files_input = reduce(lambda x,y:x + ' ' + y,files)

    files_output = reduce(lambda x,y:x + ' ' + y,[tmpdir + '/assoc/'+re.split('\/',z)[-1] +'.assd' for z in files])

    print files
    print files_input, files_output
    
    command = 'associate -i %(inputcats)s -o %(outputcats)s -t OBJECTS -c %(bonn)s/photconf/fullphotom.alpha.associate' % {'inputcats':files_input,'outputcats':files_output, 'bonn':os.environ['bonn']}
    print command
    os.system(command)
    print 'associated'

    outputcat = tmpdir + '/final.cat'
    command = 'make_ssc -i %(inputcats)s \
            -o %(outputcat)s\
            -t OBJECTS -c %(tmpdir)s/tmp.ssc ' % {'tmpdir': tmpdir, 'inputcats':files_output,'outputcat':outputcat}
    os.system(command)

def match_many_multi_band(list,color=False):
    Ns = make_ssc_multi_color(list)

    import os 
    os.system('rm -rf ' + tmpdir + '/assoc/')
    os.system('mkdir ' + tmpdir + '/assoc/')

    import os
    files = []
    for file,filter in list:
        print file

        #os.system('ldactoasc -i ' + file + ' -t OBJECTS -k ALPHA_J2000 DELTA_J2000 > ' +  file[-11:] + '.cat')
        #os.system('mkreg.pl -c -rad 3 -xcol 0 -ycol 1 -wcs ' +  file[-11:] + '.cat')


        command = 'ldacaddkey -i %(inputcat)s -t OBJECTS -o %(outputcat)s -k A_WCS_assoc 0.0003 FLOAT "" \
                                        B_WCS_assoc 0.0003 FLOAT "" \
                                        Theta_assoc 0.0 FLOAT "" \
                                        Flag_assoc 0 SHORT "" ' % {'inputcat':file,'outputcat':file + '.assoc1'}
        os.system(command)
    
        #command = 'ldacrenkey -i %(inputcat)s -o %(outputcat)s -k ALPHA_J2000 Ra DELTA_J2000 Dec' % {'inputcat':file + '.assoc1','outputcat':file+'.assoc2'} 
        #os.system(command)
        files.append(file+'.assoc1')
    import re
    files_input = reduce(lambda x,y:x + ' ' + y,files)

    files_output = reduce(lambda x,y:x + ' ' + y,[tmpdir + '/assoc/'+re.split('\/',z)[-1] +'.assd' for z in files])

    print files
    print files_input, files_output
    
    command = 'associate -i %(inputcats)s -o %(outputcats)s -t OBJECTS -c %(bonn)s/photconf/fullphotom.alpha.associate' % {'inputcats':files_input,'outputcats':files_output, 'bonn':os.environ['bonn']}
    print command
    os.system(command)
    print 'associated'

    outputcat = tmpdir + '/multiband.cat'
    command = 'make_ssc -i %(inputcats)s \
            -o %(outputcat)s\
            -t OBJECTS -c %(tmpdir)s/tmp.ssc ' % {'tmpdir': tmpdir, 'inputcats':files_output,'outputcat':outputcat}
    os.system(command)
    print outputcat, 'outputcat'

    ''' now filter out the ones with incomplete colors '''

    filt= '(' + reduce(lambda x,y: '(' + x + '  AND (' + y + ')',Ns)
    print filt
                                                                                                                 
    finalcat = tmpdir + '/multiband_final.cat'
    command = 'ldacfilter -i ' + outputcat + ' -t PSSC -o ' + finalcat + ' -c "' + filt + ';" '
    print command
    import utilities
    utilities.run(command,[finalcat])
    print finalcat, 'finalcat'



def match_inside(SUPA1,SUPA2,FLAT_TYPE):

    dict1 = get_files(SUPA1,FLAT_TYPE)
    search_params1 = initialize(dict1['filter'],dict1['OBJNAME'])
    search_params1.update(dict1)

    dict2 = get_files(SUPA2,FLAT_TYPE)
    search_params2 = initialize(dict2['filter'],dict2['OBJNAME'])
    search_params2.update(dict2)

    import os
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':search_params1['OBJNAME']}
    illum_path='/nfs/slac/g/ki/ki05/anja/SUBARU/ILLUMINATION/' % {'OBJNAME':search_params1['OBJNAME']}
    #os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/') 
    os.system('mkdir -p ' + path + 'PHOTOMETRY/ILLUMINATION/SELF/') 
    from glob import glob


    catalog1 = search_params1['pasted_cat']
    catalog2 = search_params2['pasted_cat']


    #os.system('ldacrentab -i ' + catalog2 + ' -t OBJECTS STDTAB -o ' + catalog2.replace('cat','std.cat'))


    filter = search_params1['filter'] #exposures[exposure]['keywords']['filter']
    OBJECT = search_params1['OBJECT'] #exposures[exposure]['keywords']['OBJECT']
    outcat = path + 'PHOTOMETRY/ILLUMINATION/SELF/matched_' + SUPA1 + '_' + filter + '_' + '_self.cat'               
    file = 'matched_' + SUPA1 + '.cat'               
    os.system('rm ' + outcat)
    command = 'match_simple_cats.sh ' + catalog1 + ' ' + catalog2 + ' ' + outcat
    print command
    os.system(command)

    save_exposure({'matched_cat_self':outcat},SUPA1,FLAT_TYPE)

    print outcat

def getTableInfo():
    import astropy, astropy.io.fits as pyfits, sys, os, re, string, copy , string
    
    p = pyfits.open(tmpdir + '/final.cat')
    tbdata = p[1].data
    types = []
   
    ROTS = {}
    KEYS = {} 
    for column in p[1].columns: 
        if string.find(column.name,'$') != -1:       
            print column                                           
            res = re.split('\$',column.name)
            ROT = res[0]
            IMAGE = res[1]
            KEY = res[2]
            if not ROTS.has_key(ROT):
                ROTS[ROT] = []
            if not len(filter(lambda x:x==IMAGE,ROTS[ROT])) and IMAGE!='SUPA0011082':
                ROTS[ROT].append(IMAGE)
    return ROTS


def diffCalcNew():
    import astropy, astropy.io.fits as pyfits, sys, os, re, string, copy , string
    
    p = pyfits.open(tmpdir + '/final.cat')
    tbdata = p[1].data
    types = []
   
    ROTS = {}
    KEYS = {} 
    for column in p[1].columns: 
        if string.find(column.name,'$') != -1:       
            print column                                           
            res = re.split('\$',column.name)
            ROT = res[0]
            IMAGE = res[1]
            KEY = res[2]
                                                                  
            if not ROTS.has_key(ROT):
                ROTS[ROT] = []
            if not len(filter(lambda x:x==IMAGE,ROTS[ROT])):
                ROTS[ROT].append(IMAGE)

        
    print ROTS


   
    #good = 0
    #for i in range(len(tbdata)):
    #    array = []
    #    for y in ROTS[ROT]:
    #        array += [tbdata.field(ROT+'$'+y+'$CLASS_STAR')[i] for y in ROTS[ROT]]
    #    array.sort()
    #    if array[-1]>0.9 and array[-2]>0.9: 
    #        good += 1 
    #print good, len(tbdata)

def starConstruction(EXPS):
    ''' the top two most star-like objects have CLASS_STAR>0.9 and, for each rotation, their magnitudes differ by less than 0.01 '''
    import astropy, astropy.io.fits as pyfits, sys, os, re, string, copy , string, scipy
    
    p = pyfits.open(tmpdir + '/final.cat')
    table = p[1].data

    from copy import copy 
    w = []
    for ROT in EXPS.keys():
        for y in EXPS[ROT]:
            w.append(copy(table.field(ROT+'$'+y+'$MAG_AUTO')))
    medians = []
    stds = []
    for i in range(len(w[0])):
        non_zero = []
        for j in range(len(w)): 
            if w[j][i] != 0:
                non_zero.append(w[j][i])
        if len(non_zero) != 0:
            medians.append(float(scipy.median(non_zero)))
            stds.append(float(scipy.std(non_zero)))
        else: 
            medians.append(float(-99))
            stds.append(99)
            
    print medians[0:99]
    tnew = mk_tab([[medians,'median'],[stds,'std']])
    tall = merge(tnew,p)
    print 'done merging'

def selectGoodStars(EXPS,cov,LENGTH1,LENGTH2):
    ''' the top two most star-like objects have CLASS_STAR>0.9 and, for each rotation, their magnitudes differ by less than 0.01 '''
    import astropy, astropy.io.fits as pyfits, sys, os, re, string, copy , string, scipy
    
    p = pyfits.open(tmpdir + '/final.cat')
    #print p[1].columns
    table = p[1].data
    star_good = [] #= scipy.zeros(len(table)) 
    supas = []
    from copy import copy 

    ''' if there is an image that does not match, throw it out '''
    Finished = False 
    while not Finished:
        temp = copy(table)
        for ROT in EXPS.keys():                                                                            
            for y in EXPS[ROT]:
                mask = temp.field(ROT+'$'+y+'$MAG_AUTO') != 0.0  
                good_entries = temp[mask]
                temp = good_entries
                print len(good_entries.field(ROT+'$'+y+'$MAG_AUTO'))
                mask = temp.field(ROT+'$'+y+'$MAG_AUTO') < 27  
                good_entries = temp[mask]
                temp = good_entries
                print len(good_entries.field(ROT+'$'+y+'$MAG_AUTO'))
                mask = 0 < temp.field(ROT+'$'+y+'$MAG_AUTO') 
                good_entries = temp[mask]
                temp = good_entries
                print len(good_entries.field(ROT+'$'+y+'$MAG_AUTO'))
                print ROT,y,  temp.field(ROT+'$'+y+'$MaxVal')[0:10],temp.field(ROT+'$'+y+'$BackGr')[0:10] 
                mask = (temp.field(ROT+'$'+y+'$MaxVal') + temp.field(ROT+'$'+y+'$BackGr')) < 26000
                good_entries = temp[mask]
                temp = good_entries
                good_number = len(good_entries.field(ROT+'$'+y+'$MAG_AUTO'))
                print ROT,y, good_number , EXPS
                if good_number == 0:
                    TEMP = {}
                    for ROTTEMP in EXPS.keys():
                        TEMP[ROTTEMP] = []
                        for yTEMP in EXPS[ROTTEMP]: 
                            if y != yTEMP:                           
                                TEMP[ROTTEMP].append(yTEMP)                              
                    EXPS = TEMP
                    break
        if good_number != 0:                        
            Finished = True 

    print len(temp), 'temp'
    zps = {}

    print EXPS.keys(), EXPS
    for ROT in EXPS.keys():
        for y in EXPS[ROT]:
            s = good_entries.field(ROT+'$'+y+'$MAG_AUTO').sum()
            print s
            print s/len(good_entries)
            zps[y] = s/len(good_entries)
    print zps

    from copy import copy    
    tab = {}


    for ROT in EXPS.keys():
        for y in EXPS[ROT]:
            keys = [ROT+'$'+y+'$CHIP',ROT+'$'+y+'$Xpos_ABS',ROT+'$'+y+'$Ypos_ABS',ROT+'$'+y+'$MAG_AUTO',ROT+'$'+y+'$MAGERR_AUTO',ROT+'$'+y+'$MaxVal',ROT+'$'+y+'$BackGr',ROT+'$'+y+'$CLASS_STAR',ROT+'$'+y+'$Flag',ROT+'$'+y+'$ALPHA_J2000',ROT+'$'+y+'$DELTA_J2000']                                                                                            
            if cov:
                keys = [ROT+'$'+y+'$CHIP',ROT+'$'+y+'$Xpos_ABS',ROT+'$'+y+'$Ypos_ABS',ROT+'$'+y+'$MAG_AUTO',ROT+'$'+y+'$MAGERR_AUTO',ROT+'$'+y+'$MaxVal',ROT+'$'+y+'$BackGr',ROT+'$'+y+'$CLASS_STAR',ROT+'$'+y+'$Flag' ,'SDSSstdMag_corr','SDSSstdMagErr_corr','SDSSstdMagColor_corr','SDSSstdMagClean_corr','SDSSStar_corr',ROT+'$'+y+'$ALPHA_J2000',ROT+'$'+y+'$DELTA_J2000']
                #print 'SDSS', table.field('SDSSstdMag_corr')[-1000:]
            for key in keys: 
                tab[key] = copy(table.field(key))
                print keys
    for i in range(len(table)):
        mags_ok = False 
        star_ok = False
        class_star_array = []
        include_star = []
        in_box = []
        name = []
        mags_diff_array = []
        mags_good_array = []
        from copy import copy
        for ROT in EXPS.keys():
            #for y in EXPS[ROT]:
            #    if table.field(ROT+'$'+y+'$MAG_AUTO')[i] != 0.0:
            mags_diff_array += [zps[y] - tab[ROT+'$'+y+'$MAG_AUTO'][i] for y in EXPS[ROT]]
            mags_good_array += [tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0 for y in EXPS[ROT]]
            #in_box += [1000 < tab[ROT+'$'+y+'$Xpos_ABS'][i] < 9000 and 1000 < tab[ROT+'$'+y+'$Ypos_ABS'][i] < 7000  for y in EXPS[ROT]]
            if 0: #tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0:  
                print LENGTH1, LENGTH2, (tab[ROT+'$'+y+'$MaxVal'][i] + tab[ROT+'$'+y+'$BackGr'][i]) < 20000  ,  tab[ROT+'$'+y+'$Flag'][i]==0 , tab[ROT+'$'+y+'$MAG_AUTO'][i] < 30 , tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0 , tab[ROT+'$'+y+'$MAGERR_AUTO'][i]<0.05 , ((tab[ROT+'$'+y+'$Xpos_ABS'][i]-LENGTH1/2.)**2.+(tab[ROT+'$'+y+'$Ypos_ABS'][i]-LENGTH2/2.)**2.) < (LENGTH1/2.)**2

            if 0: # 0 < tab[ROT+'$'+EXPS[ROT][0]+'$Xpos_ABS'][i] < 200 or 0 < tab[ROT+'$'+EXPS[ROT][0]+'$Ypos_ABS'][i] < 200:
                print LENGTH1, LENGTH2, [((tab[ROT+'$'+y+'$Xpos_ABS'][i]-LENGTH1/2.)**2.+(tab[ROT+'$'+y+'$Ypos_ABS'][i]-LENGTH2/2.)**2.) < ((LENGTH1/2.)**2 + (LENGTH2/2.)**2.) for y in EXPS[ROT][0:2]] 
                print [[tab[ROT+'$'+y+'$Xpos_ABS'][i]-LENGTH1/2., tab[ROT+'$'+y+'$Ypos_ABS'][i]-LENGTH2/2., tab[ROT+'$'+y+'$Xpos_ABS'][i],tab[ROT+'$'+y+'$Ypos_ABS'][i]] for y in EXPS[ROT][0:2]]

                print [[tab[ROT+'$'+y+'$Xpos_ABS'][i], tab[ROT+'$'+y+'$Ypos_ABS'][i], tab[ROT+'$'+y+'$Xpos_ABS'][i],tab[ROT+'$'+y+'$Ypos_ABS'][i]] for y in EXPS[ROT][0:2]]

            #include_star += [( tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0  ) for y in EXPS[ROT]] # and 

            include_star += [((tab[ROT+'$'+y+'$MaxVal'][i] + tab[ROT+'$'+y+'$BackGr'][i]) < 25000  and  tab[ROT+'$'+y+'$Flag'][i]==0 and tab[ROT+'$'+y+'$MAG_AUTO'][i] < 30 and tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0 and tab[ROT+'$'+y+'$MAGERR_AUTO'][i]<0.05 and ((tab[ROT+'$'+y+'$Xpos_ABS'][i]-LENGTH1/2.)**2.+(tab[ROT+'$'+y+'$Ypos_ABS'][i]-LENGTH2/2.)**2.) < (LENGTH1/2.)**2)  for y in EXPS[ROT]] # and 

            #include_star += [((tab[ROT+'$'+y+'$MaxVal'][i] + tab[ROT+'$'+y+'$BackGr'][i]) < 25000  and  tab[ROT+'$'+y+'$Flag'][i]==0 and tab[ROT+'$'+y+'$MAG_AUTO'][i] < 30 and tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0 and tab[ROT+'$'+y+'$MAGERR_AUTO'][i]<0.05)  for y in EXPS[ROT]] # and 


            #in_circ = lambda x,y,r: (x**2.+y**2.)<r**2.

            #include_star += [((tab[ROT+'$'+y+'$MaxVal'][i] + tab[ROT+'$'+y+'$BackGr'][i]) < 25000  and  tab[ROT+'$'+y+'$Flag'][i]==0 and tab[ROT+'$'+y+'$MAG_AUTO'][i] < 30 and tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0 and tab[ROT+'$'+y+'$MAGERR_AUTO'][i]<0.05 and in_circ(tab[ROT+'$'+y+'$Xpos_ABS'][i]-LENGTH1/2.,tab[ROT+'$'+y+'$Ypos_ABS'][i]-LENGTH2/2,LENGTH) for y in EXPS[ROT]]

            #include_star += [((tab[ROT+'$'+y+'$MaxVal'][i] + tab[ROT+'$'+y+'$BackGr'][i]) < 25000  and  tab[ROT+'$'+y+'$Flag'][i]==0 and tab[ROT+'$'+y+'$MAG_AUTO'][i] < 30 and tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0 and tab[ROT+'$'+y+'$MAGERR_AUTO'][i]<0.05) for y in EXPS[ROT]]
            #for y in EXPS[ROT]:
            #    print (tab[ROT+'$'+y+'$MaxVal'][i] + tab[ROT+'$'+y+'$BackGr'][i]) < 27500  , tab[ROT+'$'+y+'$Flag'][i]==0 , tab[ROT+'$'+y+'$MAG_AUTO'][i] < 40 , tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0
            name += [{'name':EXPS[ROT][z],'rotation':ROT} for z in range(len(EXPS[ROT]))]
            class_star_array += [tab[ROT+'$'+y+'$CLASS_STAR'][i] for y in EXPS[ROT]]
        class_star_array.sort()
        #if len(mags_array) > 1: 
        #    if 1: #abs(mags_array[0] - mags_array[1]) < 0.5:
        #        mags_ok = True 
        #    if 1: #abs(class_star_array[-1]) > 0.01: # MAIN PARAMETER!
        #        star_ok = True 
        if abs(class_star_array[-1]) > -9: # MAIN PARAMETER!
                star_ok = True 
        if star_ok: #mags_ok and star_ok: 
            list = []
            for k in range(len(mags_good_array)):
                if mags_good_array[k]: 
                    list.append(mags_diff_array[k])                     
            if len(list) > 1:
                median_mag_diff = scipy.median(list)                                                                                       
                #print median_mag_diff, mags_diff_array, class_star_array, include_star
                file_list=[]
                #print in_box, include_star
                for j in range(len(include_star)): 
                    if include_star[j] and abs(mags_diff_array[j] - median_mag_diff) < 1.:  # MAIN PARAMETER!
                        file_list.append(name[j])
                
                if cov:
                    if tab['SDSSstdMag_corr'][i] != 0.0: sdss_exists = 1
                    else: sdss_exists = 0
                    if 40. > tab['SDSSstdMag_corr'][i] > 0.0 and 5 > tab['SDSSstdMagColor_corr'][i] > -5: sdss = 1 # and tab['SDSSstdMagClean_corr'][i]==1: sdss = 1 
                    else: sdss = 0
                else: 
                    sdss = 0 
                    sdss_exists = 0
                #if 40. > tab['SDSSstdMag_corr'][i] > 0.0: sdss = 1 

                if len(file_list) > 1:
                    star_good.append(i)                                                            
                    supas.append({'table index':i,'supa files':file_list, 'sdss':sdss, 'sdss_exists':sdss_exists})                        
        if i%2000==0: print i

    return EXPS, star_good, supas

def diffCalc(SUPA1,FLAT_TYPE):
    dict = get_files(SUPA1,FLAT_TYPE)
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)

    import astropy, astropy.io.fits as pyfits, sys, os, re, string, copy 
    
    print search_params['matched_cat_self']
    p = pyfits.open(search_params['matched_cat_self'])
    tbdata = p[1].data
    mask = tbdata.field('SEx_MaxVal') + tbdata.field('SEx_BackGr') < 27500 
    newtbdata = tbdata[mask]

    print len(newtbdata)

    mask = newtbdata.field('CLASS_STAR') > 0.95 
    newtbdata = newtbdata[mask]

    mask = abs(newtbdata.field('SEx_MAG_APER2') - newtbdata.field('MAG_APER2')) < 0.01 
    new2tbdata = newtbdata[mask]

    print len(new2tbdata)

    data = new2tbdata.field('SEx_MAG_APER2') - new2tbdata.field('MAG_APER2')
    magErr = new2tbdata.field('SEx_MAGERR_APER2')
    X = new2tbdata.field('Xpos_ABS')
    Y = new2tbdata.field('Ypos_ABS')

    file = 'test'

    calcDataIllum(file,search_params['LENGTH1'], search_params['LENGTH2'],data,magErr,X,Y) 

    data_save = []
    magErr_save = []
    X_save = []
    Y_save = []
    for i in range(len(data)):
        data_save.append([new2tbdata.field('SEx_MAG_APER2')[i],new2tbdata.field('MAG_APER2')[i]])
        magErr_save.append([new2tbdata.field('SEx_MAGERR_APER2')[i],new2tbdata.field('MAGERR_APER2')[i]])
        X_save.append([new2tbdata.field('Xpos_ABS')[i],new2tbdata.field('SEx_Xpos_ABS')[i]])
        Y_save.append([new2tbdata.field('Ypos_ABS')[i],new2tbdata.field('SEx_Ypos_ABS')[i]])

    return data_save, magErr_save, X_save, Y_save

def linear_fit(OBJNAME,FILTER,PPRUN,CAT_TYPE=None):
    print OBJNAME,FILTER, PPRUN, tmpdir
    SDSS=True
    maxSigIter=50
    solutions = [] 

    quick = False 

    fit_db = {}

    import pickle
    ''' get data '''
    EXPS = getTableInfo()
    
    for ROT in EXPS.keys():
        print EXPS[ROT]
        save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,str(ROT)+'images':len(EXPS[ROT]),str(ROT)+'supas':reduce(lambda x,y:x+','+y,EXPS[ROT])})
    print EXPS

    ''' create chebychev polynomials '''
    cheby_x = [{'n':'0x','f':lambda x,y:1.,'order':0},{'n':'1x','f':lambda x,y:x,'order':1},{'n':'2x','f':lambda x,y:2*x**2-1,'order':2},{'n':'3x','f':lambda x,y:4*x**3.-3*x,'order':3}] 
    cheby_y = [{'n':'0y','f':lambda x,y:1.,'order':0},{'n':'1y','f':lambda x,y:y,'order':1},{'n':'2y','f':lambda x,y:2*y**2-1,'order':2},{'n':'3y','f':lambda x,y:4*y**3.-3*y,'order':3}]
    cheby_terms = []
    cheby_terms_no_linear = []
    for tx in cheby_x:
        for ty in cheby_y:
            if 1: #tx['order'] + ty['order'] <=3:
                if not ((tx['n'] == '0x' and ty['n'] == '0y')): # or (tx['n'] == '0x' and ty['n'] == '1y') or (tx['n'] == '1x' and ty['n'] == '0y')) : 
                    cheby_terms.append({'n':tx['n'] + ty['n'],'fx':tx['f'],'fy':ty['f']})
                if not ((tx['n'] == '0x' and ty['n'] == '0y') or (tx['n'] == '0x' and ty['n'] == '1y') or (tx['n'] == '1x' and ty['n'] == '0y')) :
                    cheby_terms_no_linear.append({'n':tx['n'] + ty['n'],'fx':tx['f'],'fy':ty['f']})

    
    #ROTS, data, err, X, Y, maxVal, classStar = diffCalcNew()
    #save = {'ROTS': ROTS, 'data':data,'err':err,'X':X,'Y':Y,'maxVal':maxVal,'classStar':classStar}
    #uu = open(tmpdir + '/store','w')
    #import pickle
    #pickle.dump(save,uu)
    #uu.close()
   
    ''' EXPS has all of the image information for different rotations '''

    ''' make model '''
    #fit = make_model(EXPS)
    #position_fit = make_position_model(EXPS)
    print fit

    ''' see if in sdss, linear or not ''' 
    dt = get_files(EXPS[EXPS.keys()[0]][0])
    import re
    CHIPS = [int(x) for x in re.split(',',dt['CHIPS'])]
    LENGTH1, LENGTH2 = dt['LENGTH1'], dt['LENGTH2']
    print LENGTH1, LENGTH2 

    cov, galaxycat, starcat = sdss_coverage(dt['SUPA'],dt['FLAT_TYPE']) 
    save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sdss_coverage':str(cov)})

    if not quick:
        EXPS, star_good,supas = selectGoodStars(EXPS,cov,LENGTH1,LENGTH2)               
        uu = open(tmpdir + '/selectGoodStars','w')
        import pickle
        pickle.dump({'EXPS':EXPS,'star_good':star_good,'supas':supas},uu)
        uu.close()

    import pickle
    f=open(tmpdir + '/selectGoodStars','r')
    m=pickle.Unpickler(f)
    d=m.load()

    EXPS = d['EXPS']
    star_good = d['star_good']
    supas = d['supas']

    info = starStats(supas)



    print len(star_good)

    #cheby_terms_use = cheby_terms_no_linear
    fitvars_fiducial = False

    if cov:
        if info['sdss'] > 400:
            samples = [['sdss','cheby_terms',True]]#,['nosdss',cheby_terms_no_linear,False]] #[['nosdss',cheby_terms_no_linear],['sdss',cheby_terms]]
            print 'all terms'
        else:
            samples = [['sdss','cheby_terms_no_linear',True]]#,['nosdss',cheby_terms_no_linear,False]] #[['nosdss',cheby_terms_no_linear],['sdss',cheby_terms]]
            print 'no linear terms'

        #samples = [['nosdss',cheby_terms_no_linear,False]] #[['nosdss',cheby_terms_no_linear],['sdss',cheby_terms]]
    else: 
        samples = [['nosdss','cheby_terms_no_linear',False]]
    #samples = [['sdss',cheby_terms_no_linear]]

    for sample,which_terms,cov in samples:
    	cheby_terms_use = locals()[which_terms] 
        import scipy
        import astropy, astropy.io.fits as pyfits
        p = pyfits.open(tmpdir + '/final.cat')
        table = p[1].data
        
        from copy import copy  
        tab = {}
        for ROT in EXPS.keys():
            for y in EXPS[ROT]:
                keys = [ROT+'$'+y+'$CHIP',ROT+'$'+y+'$Xpos_ABS',ROT+'$'+y+'$Ypos_ABS',ROT+'$'+y+'$MAG_AUTO',ROT+'$'+y+'$MAGERR_AUTO',ROT+'$'+y+'$MaxVal',ROT+'$'+y+'$BackGr',ROT+'$'+y+'$CLASS_STAR',ROT+'$'+y+'$Flag',ROT+'$'+y+'$ALPHA_J2000',ROT+'$'+y+'$DELTA_J2000']                                                                                            
                if cov:
                    keys = [ROT+'$'+y+'$CHIP',ROT+'$'+y+'$Xpos_ABS',ROT+'$'+y+'$Ypos_ABS',ROT+'$'+y+'$MAG_AUTO',ROT+'$'+y+'$MAGERR_AUTO',ROT+'$'+y+'$MaxVal',ROT+'$'+y+'$BackGr',ROT+'$'+y+'$CLASS_STAR',ROT+'$'+y+'$Flag' ,'SDSSstdMag_corr','SDSSstdMagErr_corr','SDSSstdMagColor_corr','SDSSstdMagClean_corr','SDSSStar_corr',ROT+'$'+y+'$ALPHA_J2000',ROT+'$'+y+'$DELTA_J2000']

                for key in keys: 
                    tab[key] = copy(table.field(key))
        
        coord_conv_x = lambda x:(2.*x-0-LENGTH1)/(LENGTH1-0) 
        coord_conv_y = lambda x:(2.*x-0-LENGTH2)/(LENGTH2-0) 

        print LENGTH1, LENGTH2

        save_fit({'FILTER':FILTER,'OBJNAME':OBJNAME,'PPRUN':PPRUN,'supas':len(supas),'sdss_stars':len(filter(lambda x:x['sdss'],supas))})
        supas_copy = copy(supas)


        ''' find the color term '''
        if True:
            data = []
            magErr = []
            color = []

            for star in supas:                                                                                                                   
                ''' each exp of each star '''
                if star['sdss'] and sample=='sdss':
                    for exp in star['supa files']:
                        if 2 > tab['SDSSstdMagColor_corr'][star['table index']] > -2:
                            rotation = exp['rotation']                                                                                                       
                            sigma = tab['SDSSstdMagErr_corr'][star['table index']]
                            data.append(tab[str(rotation)+'$'+exp['name']+'$MAG_AUTO'][star['table index']] - tab['SDSSstdMag_corr'][star['table index']])  
                            magErr.append(tab['SDSSstdMagErr_corr'][star['table index']])
                            color.append(tab['SDSSstdMagColor_corr'][star['table index']])

            color.sort()


            
            if False:        
                A = scipy.zeros([len(data),2])                   
                B = scipy.zeros(len(data))
                                                                 
                for i in range(len(data)):
                    A[i][0] = color[i]/magErr[i]                
                    A[i][1] = 1./magErr[i]
                    B[i] = data[i]/magErr[i]
                                                                 
                print A
                print B

                     
                from scipy import linalg                  
                print 'doing linear algebra'
                U = linalg.lstsq(A,B)[0]
                print U
                print A
                print B
                print scipy.shape(U)
                print scipy.shape(A)
                print scipy.shape(B)
                                                          
                print scipy.shape(A), len(U), 
                Bprime = scipy.dot(A,U)  
                print scipy.shape(Bprime),scipy.shape(B)
                Bdiff = (abs(abs(B-Bprime))).sum()/len(B)
                print (B-Bprime)[:300]
                print U[0:20]
                print Bdiff, 'reduced chi-squared'
                                                          
                a = [-100,100]
                m = [U[1]-100*U[0],U[1]+U[0]*100]
                print a, m
                #plot_color(color, data,  a, m)

        for sample_size in ['all']: #'rand1','rand1']: #,'rand2','rand3','rand4','all']: #,'rand3']:

            ''' take a random sample of half '''
            if sample_size != 'all':     
                ## changing the CLASS_STAR criterion upwards helps as does increasing the sigma on the SDSS stars
                print len(supas)
                l = range(len(supas_copy))                     
                print l[0:10]
                l.sort(random_cmp)
                print l[0:10]
                ''' shorten star_good, supas '''
                supas = [supas_copy[i] for i in l[0:len(supas_copy)/2]]
            else:
                supas = copy(supas_copy)


            print len(supas), 'supas', supas[0]

            columns = []
            column_dict = {}
            
            ''' position-dependent terms in design matrix '''
            position_columns = []
            index = -1
                                                                                                                                                      
            for ROT in EXPS.keys():
                for term in cheby_terms_use:
                    index += 1
                    name = str(ROT) + '$' + term['n'] # + reduce(lambda x,y: x + 'T' + y,term)
                    position_columns.append({'name':name,'fx':term['fx'],'fy':term['fy'],'rotation':ROT,'index':index})
            #print position_columns
            columns += position_columns
            
            ''' zero point terms in design matrix '''
            per_chip = False # have a different zp for each chip on each exposures 
            same_chips =   True# have a different zp for each chip but constant across exposures

            if not per_chip:
                zp_columns = []                                                             
                for ROT in EXPS.keys():
                    for exp in EXPS[ROT]:
                        index += 1
                        zp_columns.append({'name':'zp_image_'+exp,'image':exp,'im_rotation':ROT,'index':index})

            if per_chip:
                zp_columns = []                                                             
                for ROT in EXPS.keys():
                    for exp in EXPS[ROT]:
                        for chip in CHIPS:
                            index += 1
                            zp_columns.append({'name':'zp_image_'+exp + '_' + chip,'image':exp,'im_rotation':ROT, 'chip':chip,'index':index})

            if not per_chip and same_chips:
                for chip in CHIPS:
                    index += 1
                    zp_columns.append({'name':'zp_'+str(chip),'image':'chip_zp','chip':chip,'index':index})


            if cov:
                index += 1
                zp_columns.append({'name':'zp_SDSS','image':'sdss','index':index})
            columns += zp_columns
           
            if cov and true_sdss:
                index += 1
                color_columns=[{'name':'SDSS_color','image':'sdss_color_term','index':index}]
            else: color_columns = []
            columns += color_columns
            
            mag_columns = []
            for star in supas:
                mag_columns.append({'name':'mag_' + str(star['table index'])})
            columns += mag_columns

            print len(columns)
            
            column_names = [x['name'] for x in columns] #reduce(lambda x,y: x+y,columns)] 
            print column_names[0:100]
            
            ''' total number of fit parameters summed over each rotation + total number of images of all rotations + total number of stars to fit '''

            tot_exp = 0
            for ROT in EXPS.keys():
                for ele in EXPS[ROT]:
                    tot_exp += 1

            x_length = len(position_columns) + len(zp_columns) + len(color_columns) + len(mag_columns) 
            print len(columns), x_length
            x_length = len(columns)
            y_length = reduce(lambda x,y: x + y,[len(star['supa files'])*2 for star in supas]) # double number of rows for SDSS
            print x_length, y_length
            print star['supa files']
            print 
            Bstr = ''                   
            row_num = -1
            supa_num = -1
            ''' each star '''
            print 'creating matrix....'
            sigmas = []
            inst = []
            data = {} 
            magErr = {} 
            whichimage = {}
            X = {} 
            Y = {} 
            color = {}
            chipnums = {}
            Star = {}
            catalog_values = {}
            for ROT in EXPS.keys():
                data[ROT] = []
                magErr[ROT] = []
                X[ROT] = []
                Y[ROT] = []
                color[ROT] = []
                whichimage[ROT] = []
                chipnums[ROT] = []
                Star[ROT] = []

            chip_dict = {}

            x_positions = {}
            y_positions = {}

            for star in supas:   
                supa_num += 1
                ''' each exp of each star '''
                if 1:
                    star_A = []
                    star_B = []
                    star_B_cat = []
                    sigmas = []
                    for exp in star['supa files']:                                                                                              
                        row_num += 1           
                        col_num = -1 
                        rotation = exp['rotation'] 
                        x = tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS'][star['table index']]
                        y = tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS'][star['table index']]

                        #if x < 2000 or y < 2000 or abs(LENGTH1 - x) < 2000 or abs(LENGTH2 - y) < 2000:
                        #    sigma = 1.5 * tab[str(rotation) + '$' + exp['name'] + '$MAGERR_AUTO'][star['table index']] 
                        #else:
                        sigma = tab[str(rotation) + '$' + exp['name'] + '$MAGERR_AUTO'][star['table index']] 

                        chip = int(tab[str(rotation) + '$' + exp['name'] + '$CHIP'][star['table index']] )
                        if not chip_dict.has_key(str(chip)):
                            chip_dict[str(chip)] = ''
                            print chip_dict.keys(), CHIPS

                        if sigma < 0.001: sigma = 0.001
                        sigma = sigma # * 1000. 
                        #sigma = 1
                        for c in position_columns: 
                            col_num += 1
                            if c['rotation'] == rotation:
                                n = str(rotation) + '$' + exp['name'] + '$Xpos_ABS'
                                x = tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS'][star['table index']]
                                y = tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS'][star['table index']]
                                x_positions[row_num] = x
                                y_positions[row_num] = y
                                x = coord_conv_x(x)
                                y = coord_conv_y(y)
                                value = c['fx'](x,y)*c['fy'](x,y)/sigma
                                star_A.append([row_num,col_num,value])
                        first_exposure = True 
                        for c in zp_columns:
                            col_num += 1
                            #if not degeneracy_break[c['im_rotation']] and c['image'] == exp['name']:
                            if not per_chip:
                                if (first_exposure is not True  and c['image'] == exp['name']):  
                                    value = 1./sigma
                                    star_A.append([row_num,col_num,value])
                                if same_chips and c.has_key('chip'):
                                    if (c['chip'] == chip) and chip != CHIPS[0]:  
                                        value = 1./sigma                       
                                        star_A.append([row_num,col_num,value])
                                first_exposure = False
                            if per_chip:
                                if (first_column is not True and c['image'] == exp['name'] and c['chip'] == chip):  
                                    value = 1./sigma
                                    star_A.append([row_num,col_num,value])
                        
                        ''' fit for the color term dependence for SDSS comparison '''
                        if cov and true_sdss:
                            col_num += 1
                        
                        ''' magnitude column -- include the correct/common magnitude '''
                        col_num += 1
                        value = 1./sigma
                        star_A.append([row_num,col_num+supa_num,value])
                        ra = tab[str(rotation) + '$' + exp['name'] + '$ALPHA_J2000'][star['table index']]
                        dec = tab[str(rotation) + '$' + exp['name'] + '$DELTA_J2000'][star['table index']]

                        value = tab[str(rotation) + '$' + exp['name'] + '$MAG_AUTO'][star['table index']]/sigma
                        catalog_values[col_num+supa_num] = {'inst_value':value*sigma,'ra':ra,'dec':dec,'sigma':sigma} # write into catalog
                        #print catalog_values, col_num+supa_num

                        x_long = tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS'][star['table index']]
                        y_long = tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS'][star['table index']]
                        x = coord_conv_x(x_long)
                        y = coord_conv_y(y_long)
                        if fitvars_fiducial:
                            value += add_single_correction(x,y,fitvars_fiducial)
                        star_B.append([row_num,value])


                        sigmas.append(sigma)

                    inst.append({'type':'sdss','A_array':star_A, 'B_array':star_B, 'sigma_array': sigmas})
                                       
                ''' only include one SDSS observation per star '''
                if star['sdss'] and sample=='sdss' and tab['SDSSStar_corr'][star['table index']] == 1:
                                
                    star_A = []
                    star_B = []
                    sigmas = []
                    ''' need to filter out bad colored-stars '''
                    if 1: #-5 < tab['SDSSstdMagColor_corr'][star['table index']] < 5:
                        row_num += 1                                                                                                                                      
                        col_num = -1 
                        exp = star['supa files'][0]
                        rotation = exp['rotation'] 
                        #sigma = tab[str(rotation) + '$' + exp['name'] + '$MAGERR_AUTO'][star['table index']] 
                        sigma = tab['SDSSstdMagErr_corr'][star['table index']]#/300. 
                        if sigma < 0.005: sigma = 0.005

                        #if sigma < 1000: sigma =10000 
                        for c in position_columns:
                            col_num += 1
                        first_column = True
                        for c in zp_columns:
                            col_num += 1
                            ''' remember that the good magnitude does not have any zp dependence!!! '''
                            #if (first_column is not True  and c['image'] == exp['name']) or c['image'] == 'sdss':
                            if c['image'] == 'sdss': 
                                value = 1./sigma
                                star_A.append([row_num,col_num,value])
                                x_positions[row_num] = x
                                y_positions[row_num] = y

                            first_column = False
                                                                                                                                                                          
                        ''' fit for the color term dependence for SDSS comparison '''
                        if true_sdss:
                            col_num += 1
                        
                            ''' fit for the color term dependence '''                      
                            value = tab['SDSSstdMagColor_corr'][star['table index']]/sigma
                            star_A.append([row_num,col_num,value])

                        col_num += 1
                        ''' magnitude column -- include the correct/common magnitude '''
                        value = 1./sigma
                        star_A.append([row_num,col_num+supa_num,value])

                        #value = (tab[str(rotation)+'$'+exp['name']+'$MAG_AUTO'][star['table index']] - tab['SDSSstdMag_corr'][star['table index']])/sigma
                        #print  tab[str(rotation)+'$'+exp['name']+'$MAG_AUTO'][star['table index']], tab['SDSSstdMag_corr'][star['table index']]
                        
                        value = tab['SDSSstdMag_corr'][star['table index']]/sigma
                        star_B.append([row_num,value])
                        sigmas.append(sigma)
                        
                        inst.append({'type':'sdss','A_array':star_A, 'B_array':star_B, 'sigma_array': sigmas})
                        
                        ''' record star information '''
                        if True:
                            for exp in star['supa files']:
                                rotation = str(exp['rotation'])
                                data[rotation].append(tab[str(rotation)+'$'+exp['name']+'$MAG_AUTO'][star['table index']] - tab['SDSSstdMag_corr'][star['table index']]) 
                                Star[rotation].append(tab['SDSSStar_corr'][star['table index']])
                                magErr[rotation].append(tab['SDSSstdMagErr_corr'][star['table index']])
                                whichimage[rotation].append(exp['name'])
                                X[rotation].append(tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS'][star['table index']])
                                Y[rotation].append(tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS'][star['table index']])
                                color[rotation].append(tab['SDSSstdMagColor_corr'][star['table index']])
                                chipnums[rotation].append(tab[str(rotation) + '$' + exp['name'] + '$CHIP'][star['table index']])
                        #print star_A, star_B, sigmas, sigma
                        #raw_input()


            print EXPS
            for rot in EXPS.keys():
                print data.keys()
                print rot, len(data[str(rot)])

            ''' save the SDSS matches '''
            sdss_matches = {'data':data,'magErr':magErr,'whichimage':whichimage,'X':X,'Y':Y,'color':color}

            uu = open(tmpdir + '/sdss','w')
            import pickle
            pickle.dump(sdss_matches,uu)
            uu.close()

            ''' do fitting '''
            #if 1: #not quick:
            for attempt in ['first','rejected']:
                ''' make matrices/vectors '''                                                                                                                           
                Ainst_expand = []
                for z in inst:
                    for y in z['A_array']:
                        Ainst_expand.append(y)
                                                                                                                                                                        
                Binst_expand = []
                for z in inst:
                    for y in z['B_array']:
                        Binst_expand.append(y)
                print len(Binst_expand)
                ''' this gives the total number of rows added '''
                                                                                                                                                                        
                sigmas = []
                for z in inst:
                    for y in z['sigma_array']:
                        sigmas.append(y)
                print len(Binst_expand)
                                                                                                                                                                        
                ylength = len(Binst_expand)
                print y_length, x_length
                print len(Ainst_expand), len(Binst_expand)
                print 'lengths'
                A = scipy.zeros([y_length,x_length])
                B = scipy.zeros(y_length)

                import copy
                if attempt == 'first': rejectlist = 0*copy.copy(B)
                                                                                                                                                                        
                Af = open('A','w')
                Bf = open('b','w')

                rejected = 0
                rejected_x = []
                rejected_y = []
                all_x = []
                all_y = []
                all_resids = []
                if attempt == 'rejected':
                    for ele in Ainst_expand:                                                      
                        if rejectlist[ele[0]] == 0: 
                            if x_positions.has_key(ele[0]) and y_positions.has_key(ele[0]):  
                                all_x.append(float(str(x_positions[ele[0]]))) 
                                all_y.append(float(str(y_positions[ele[0]])))
                                all_resids.append(float(str(resids_sign[ele[0]])))
                        if rejectlist[ele[0]] == 0: 
                            Af.write(str(ele[0]) + ' ' + str(ele[1]) + ' ' + str(ele[2]) + '\n') 
                            #print ele, y_length, x_length
                            #print ele
                            A[ele[0],ele[1]] = ele[2]
                        else: 
                            rejected += 1
                            if x_positions.has_key(ele[0]) and y_positions.has_key(ele[0]): 
                                rejected_x.append(float(str(x_positions[ele[0]])))
                                rejected_y.append(float(str(y_positions[ele[0]])))
                else:
                    for ele in Ainst_expand:                                                      
                        Af.write(str(ele[0]) + ' ' + str(ele[1]) + ' ' + str(ele[2]) + '\n') 
                        #print ele, y_length, x_length
                        #print ele 
                        A[ele[0],ele[1]] = ele[2]

                for ele in Binst_expand:
                    if rejectlist[ele[0]] == 0: 
                        B[ele[0]] = ele[1]
                if attempt == 'rejected' and rejected > 0:
                    print rejected, 'rejected' 

                    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':OBJNAME}
                    illum_dir = path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + PPRUN + '/'
                    import Numeric
                    print all_resids[0:100]
                    print all_x[0:100] 
                    print all_y[0:100] 

                    os.system('mkdir -p ' + illum_dir)
                    calcDataIllum(sample + 'reducedchi'+str(ROT)+FILTER,LENGTH1,LENGTH2,Numeric.array(all_resids),Numeric.ones(len(all_resids)),Numeric.array(all_x),Numeric.array(all_y),pth=illum_dir,rot=0) 

                    dtmp = {} 
                    dtmp[sample+'$'+sample_size+'$rejected']=rejected
                    dtmp[sample+'$'+sample_size+'$totalmeasurements']=rejected

                    import Numeric 
                    import ppgplot
                    x_p = Numeric.array(rejected_x)
                    y_p = Numeric.array(rejected_y)

                    import copy
                    x = sorted(copy.copy(x_p))
                    y = sorted(copy.copy(y_p))

                    illum_dir = path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + PPRUN + '/'
                    import os
                    os.system('mkdir ' + illum_dir)
                    reject_plot = illum_dir + sample + 'rejects.ps'

                    dtmp[sample+'$'+sample_size+'$reject_plot']=reject_plot

                    dtmp.update({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'linearfit':'1'})
                    save_fit(dtmp)
                        
                    import tempfile 
                    t = tempfile.NamedTemporaryFile(dir='/tmp/').name 

                    ppgplot.pgbeg(t + '/cps',1,1)                                       
                    ppgplot.pgiden()
                                                             
                    #print x_p
                    #print z_p 
                    #print zerr_p
                                                             
                    #pgswin(x[0],x[-1],z[0],z[-1])
                                                             
                    ### plot positions
                    ppgplot.pgpanl(1,1)
                    ppgplot.pgswin(x[0],x[-1],y[0],y[-1])
                    ppgplot.pgbox()
                    ppgplot.pglab('X','Y','rejected points')     # label the plot
                    #pgsci(3)
                    #pgerrb(6,x_p,z_p,zerr_p)
                    print x_p[0:100], y_p[0:100]
                    print type(x_p), type(y_p)

                    print 'plotting'
                    ppgplot.pgpt(x_p,y_p,3)
                    print 'plotted'
                                                             
                    ppgplot.pgend()
                    print reject_plot
                    os.system('mv ' + t + ' ' + reject_plot)

                Bstr = reduce(lambda x,y:x+' '+y,[str(z[1]) for z in Binst_expand])
                Bf.write(Bstr)
                Bf.close()
                Af.close()
                                                                                                                                                                        
                print 'finished matrix....'
                print len(position_columns), len(zp_columns)
                print A[0,0:30], B[0:10], scipy.shape(A), scipy.shape(B)
                print A[1,0:30], B[0:10], scipy.shape(A), scipy.shape(B)
                print 'hi!'
                                                                                                                                                                        
                Af = open(tmpdir + '/B','w')
                for i in range(len(B)):
                    Af.write(str(B[i]) + '\n')
                Af.close()
                
                print 'solving matrix...'
                import re, os
                os.system('rm x')
                os.system('sparse < A')
                bout = open('x','r').read()
                res = re.split('\s+',bout[:-1].replace('nan','0'))
                T = [float(x) for x in res][:x_length]

                params = {}
                for i in range(len(T)):
                    if i < len(column_names):
                        params[column_names[i]] = T[i]
                    if catalog_values.has_key(i):
                        catalog_values[i]['mag'] = T[i]
                        #print catalog_values[i]

                U = [float(x) for x in res][:x_length]

                print 'finished solving...'
                
                #from scipy import linalg
                #print 'doing linear algebra'
                #U = linalg.lstsq(A,B)
                #print U[0][0:30]
                
                ''' calculate reduced chi-squared value'''
                print scipy.shape(A), len(U), x_length, len(res)
                Bprime = scipy.dot(A,U)  
                print scipy.shape(Bprime),scipy.shape(B)
                Bdiff = (abs(abs(B-Bprime))).sum()/len(B)
                resids = abs(B-Bprime)
                resids_sign = B-Bprime
                rejectlist = [] 
                rejectnums = 0
                for i in range(len(resids)): 
                    if resids[i] > 5: 
                        rejectlist.append(1) 
                        rejectnums += 1
                    else: rejectlist.append(0)
                print (B-Bprime)[:300]
                print len(resids), rejectnums
                print U[0:20]
                print x[0:20]
                reducedchi = Bdiff
                
                print reducedchi, 'reduced chi-squared'
                #save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'reducedchi$'+sample+'$'+sample_size:Bdiff})
                                                                                             
                data_directory = '/nfs/slac/g/ki/ki04/pkelly/illumination/'
                                                                                            
                position_fit = [['Xpos_ABS','Xpos_ABS'],['Xpos_ABS','Ypos_ABS'],['Ypos_ABS','Ypos_ABS'],['Xpos_ABS'],['Ypos_ABS']]
                import re
                ''' save fit information '''
                #print  sample+'$'+sample_size+'$' + str(ROT) + '$positioncolumns',reduce(lambda x,y: x+','+y,[z['name'] for z in position_columns]) 


                if cov: 
                    save_columns = position_columns + zp_columns + color_columns 
                else:
                    save_columns = position_columns + zp_columns
               
                dtmp = {}
                o = zp_columns + position_columns
                #for ROT in EXPS.keys():
                    #dtmp['zp_' + ROT] = params['zp_' + ROT]
                fitvars = {}
                zp_images = ''
                zp_images_names = ''
                for ele in save_columns:                      
                    print ele
                    res = re.split('$',ele['name'])
                    import string
                    if string.find(ele['name'],'zp_image') == -1:
                        fitvars[ele['name']] = U[ele['index']]             
                        term_name = sample+'$'+sample_size+'$'+ele['name']
                        print term_name
                        dtmp[term_name]=fitvars[ele['name']]
                        print ele['name'], fitvars[ele['name']]
                    else:
                        zp_images += str(U[ele['index']]) + ','
                        zp_images_names += ele['name'] + ','

                zp_images = zp_images[:-1]
                zp_images_names = zp_images_names[:-1]

                term_name = sample+'$'+sample_size+'$zp_images'
                print term_name
                dtmp[term_name]=zp_images
                print dtmp[term_name]
                
                term_name = sample+'$'+sample_size+'$zp_images_names'
                print term_name
                dtmp[term_name]=zp_images_names
                print dtmp[term_name]

                import string

                print dtmp.keys()
                use_columns = filter(lambda x: string.find(x,'zp_image') == -1,[z['name'] for z in save_columns] ) + ['zp_images','zp_images_names']

                positioncolumns = reduce(lambda x,y: x+','+y,use_columns)

                print positioncolumns
                #print positioncolumns, sample+'$'+sample_size + '$positioncolumns' 
                #save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,sample+'$'+sample_size+'$positioncolumns':positioncolumns})
                dtmp[sample+'$'+sample_size+'$positioncolumns'] = positioncolumns
                dtmp[sample+'$'+sample_size+'$reducedchi']=reducedchi

                #term_name = sample+'$'+sample_size+'$0x1y'
                #print term_name, '!!!!!'
                #if 0: 
                    #print fitvars['1$0x1y'], '1$0x1y'            
                    #term_name = sample+'$'+sample_size+'$1$0x1y'
                    #dtmp[term_name] = 1.
                    #term_name = sample+'$'+sample_size+'$0$1x0y'
                    #dtmp[term_name] = 1.
                    #fitvars['1$0x1y'] = 1.
                    #fitvars['0$1x0y'] = 1.
                    #print fitvars
                    #raw_input()

                print dtmp.keys()
                print 'stop'
                print dtmp[sample + '$' + sample_size + '$positioncolumns'], sample + '$' + sample_size + '$positioncolumns', PPRUN, FILTER, OBJNAME
                dtmp.update({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'linearfit':'1'})
                print dtmp
                
                save_fit(dtmp)

            if 1:
                ''' save the corrected catalog '''
                
                tmp = {}    
                import astropy, astropy.io.fits as pyfits
                cols = [] 

                stdMag_corr = []
                stdMagErr_corr = []
                stdMagColor_corr = []
                stdMagClean_corr = []
                ALPHA_J2000 = []
                DELTA_J2000 = []
                SeqNr = []
                Star_corr = []
                sn = -1

                for i in catalog_values.keys():
                    entr = catalog_values[i]
                    sn += 1
                    SeqNr.append(sn)
                    stdMag_corr.append(entr['mag'])
                    ALPHA_J2000.append(entr['ra'])
                    DELTA_J2000.append(entr['dec'])
                    stdMagErr_corr.append(entr['sigma'])
                    stdMagColor_corr.append(0)
                    stdMagClean_corr.append(1)
                    Star_corr.append(1)

                print 'data start'
                import Numeric 
                cols.append(pyfits.Column(name='stdMag_corr', format='E',array=Numeric.array(stdMag_corr)))
                cols.append(pyfits.Column(name='stdMagErr_corr', format='E',array=Numeric.array(stdMagErr_corr)))
                cols.append(pyfits.Column(name='stdMagColor_corr', format='E',array=Numeric.array(stdMagColor_corr)))
                cols.append(pyfits.Column(name='stdMagClean_corr', format='E',array=Numeric.array(stdMagClean_corr)))
                cols.append(pyfits.Column(name='ALPHA_J2000', format='E',array=Numeric.array(ALPHA_J2000)))
                cols.append(pyfits.Column(name='DELTA_J2000', format='E',array=Numeric.array(DELTA_J2000)))
                cols.append(pyfits.Column(name='SeqNr', format='E',array=Numeric.array(SeqNr)))
                cols.append(pyfits.Column(name='Star_corr', format='E',array=Numeric.array(Star_corr)))
               
                path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':OBJNAME}
                outcat = path + 'PHOTOMETRY/ILLUMINATION/' + 'catalog_' + PPRUN + '.cat'
                print cols
                hdu = pyfits.PrimaryHDU()
                hdulist = pyfits.HDUList([hdu])
                tbhu = pyfits.BinTableHDU.from_columns(cols)
                hdulist.append(tbhu)
                hdulist[1].header['EXTNAME']='OBJECTS'
                os.system('rm ' + outcat)
                hdulist.writeto( outcat )
                print 'wrote out new cat'
                print outcat

                save_fit({'FILTER':FILTER,'OBJNAME':OBJNAME,'PPRUN':PPRUN,'catalog':outcat})
                #save_exposure({type + 'atch':outcat},SUPA,FLAT_TYPE)
                #tmp[type + 'sdssmatch'] = outcat



            ''' make diagnostic plots '''
            if 1:
                import re, time
                d = get_fits(OBJNAME,FILTER,PPRUN)                
                print d.keys()
                column_prefix = sample+'$'+sample_size+'$'
                position_columns_names = re.split('\,',d[column_prefix + 'positioncolumns']) 
                print position_columns_names, 'position_columns_names'
                fitvars = {}
                cheby_terms_dict = {}
                print column_prefix, position_columns_names
                for ele in position_columns_names:                      
                    print ele
                    if type(ele) != type({}):
                        ele = {'name':ele}
                    res = re.split('$',ele['name'])
                    if string.find(ele['name'],'zp_image') == -1:
                        fitvars[ele['name']] = float(d[sample+'$'+sample_size+'$'+ele['name']]) 
                        for term in cheby_terms:
                            if term['n'] == ele['name'][2:]:
                                cheby_terms_dict[term['n']] = term 

                zp_images = re.split(',',d[sample+'$'+sample_size+'$zp_images'])
                zp_images_names = re.split(',',d[sample+'$'+sample_size+'$zp_images_names'])

                for i in range(len(zp_images)):
                    fitvars[zp_images_names[i]] = float(zp_images[i])

                print fitvars




                cheby_terms_use =  [cheby_terms_dict[k] for k in cheby_terms_dict.keys()]

                print cheby_terms_use, fitvars

                ''' make images of illumination corrections '''                                                                  
                for ROT in EXPS.keys():
                    size_x=LENGTH1
                    size_y=LENGTH2 
                    bin=100
                    import numpy, math, pyfits, os                                                                              
                    x,y = numpy.meshgrid(numpy.arange(0,size_x,bin),numpy.arange(0,size_y,bin))
                    F=0.1
                    print 'calculating'
                    x = coord_conv_x(x)
                    y = coord_conv_y(y)

                    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':OBJNAME}
                    illum_dir = path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + PPRUN + '/' + str(ROT)
                    os.system('mkdir -p ' + illum_dir)
                    
                    epsilon = 0
                    index = 0
                    for term in cheby_terms_use:
                        index += 1
                        print index, ROT, term, fitvars[str(ROT)+'$'+term['n']]
                        epsilon += fitvars[str(ROT)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)

                    ''' save pattern w/o chip zps '''

                    print 'writing'
                    hdu = pyfits.PrimaryHDU(epsilon)
                                                                                                                                 
                    im = illum_dir + '/nochipzps' + sample + sample_size +  '.fits'
                    save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,sample+'$'+sample_size+'$'+str(ROT)+'$im':im})
                                                                                                                                 
                    os.system('rm ' + im)
                    hdu.writeto(im)

                    ''' save pattern w/ chip zps '''

                    if per_chip or same_chips:
                        print CHIPS, 'CHIPS'                                                                                          
                        for CHIP in CHIPS:
                            if str(dt['CRPIX1_' + str(CHIP)]) != 'None':
                                xmin = float(dt['CRPIX1ZERO']) - float(dt['CRPIX1_' + str(CHIP)])                                          
                                ymin = float(dt['CRPIX2ZERO']) - float(dt['CRPIX2_' + str(CHIP)])
                                xmax = xmin + float(dt['NAXIS1_' + str(CHIP)])
                                ymax = ymin + float(dt['NAXIS2_' + str(CHIP)])
                                                                                                                                          
                                print xmin, xmax, ymin, ymax, CHIP, 'CHIP'
                                                                                                                                          
                                print int(xmin/bin), int(xmax/bin), int(ymin/bin), int(ymax/bin), CHIP, 'CHIP', bin, scipy.shape(epsilon)
                                                                                                                                          
                                print epsilon[int(xmin/bin):int(xmax/bin)][int(ymin/bin):int(ymax/bin)]
                                print fitvars.keys()
                                print 'zp', fitvars['zp_' + str(CHIP)]
                                epsilon[int(ymin/bin):int(ymax/bin),int(xmin/bin):int(xmax/bin)] += float(fitvars['zp_' + str(CHIP)])
                                                
                    print 'writing'
                    hdu = pyfits.PrimaryHDU(epsilon)
                                                                                                                                 
                    im = illum_dir + '/correction' + sample + sample_size +  '.fits'
                    save_fit({'linearplot':1,'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,sample+'$'+sample_size+'$'+str(ROT)+'$im':im})
                                                                                                                                 
                    os.system('rm ' + im)
                    hdu.writeto(im)

                    print 'done'

            if cov:                                                                                                                                 
                ''' calculate SDSS plot differences, before and after '''
                for ROT in EXPS.keys():
                    data[ROT] = scipy.array(data[ROT])
                    print scipy.array(data[ROT]), ROT
                    print EXPS

                    color[ROT] = scipy.array(color[ROT])
                    
                    ''' apply the color term measured from the data '''
                    zp_correction = scipy.array([float(fitvars['zp_image_'+x]) for x in whichimage[ROT]])
                    #data1 = data[ROT] - fitvars['SDSS_color']*color[ROT]  - zp_correction 
                
                    if true_sdss:
                        data1 = data[ROT] + fitvars['SDSS_color']*color[ROT] - zp_correction 
                    else:
                        data1 = data[ROT] - zp_correction 

                    #print data1, data[ROT], fitvars['SDSS_color'], color[ROT], zp_correction
                    #print len(data1)
                    data2 = data1 - (data1/data1*scipy.median(data1))
                    
                    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':OBJNAME}
                    illum_dir = path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + PPRUN + '/' + str(ROT) + '/'

                    for kind,keyvalue in [['star',1]]: #['galaxy',0],

                        calcDataIllum(sample + kind + 'nocorr'+str(ROT)+FILTER,10000,8000,data2,magErr[ROT],X[ROT],Y[ROT],pth=illum_dir,rot=0,good=[Star[ROT],keyvalue]) 

                        dtmp = {}

                        var = variance(data2,magErr[ROT])
                        print var

                        dtmp['sdssstdnocorr$' + str(ROT)] = var[1]**0.5
                        dtmp['sdssredchinocorr$' + str(ROT)] = var[2]

                        #plot_color(color[ROT], data2)

                        import scipy
                        
                        #print X[ROT]
                        x = coord_conv_x(scipy.array(X[ROT]))
                        y = coord_conv_y(scipy.array(Y[ROT]))
                                                                                                                                  
                        #epsilon = 0                                                       
                        #for term in cheby_terms:
                        #    data += fitvars[term[str(ROT)+'$'+'n']]*term['fx'](x,y)*term['fy'](x,y)
                                                                                                                                        
                        epsilon=0
                        for term in cheby_terms_use:
                            epsilon += fitvars[str(ROT)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)
                                                                                                                                        
                        chipcorrect = []
                        for chip in chipnums[ROT]:
                            chipcorrect.append(fitvars['zp_' + str(int(float(chip)))])
                        chipcorrect = scipy.array(chipcorrect)
                        epsilon += chipcorrect
                                                                                                                                        
                                                                                                                                        
                        calcim = sample+kind+'correction'+str(ROT)+FILTER
                        calcDataIllum(calcim,10000,8000,epsilon,magErr[ROT],X[ROT],Y[ROT],pth=illum_dir,rot=0,good=[Star[ROT],keyvalue])

                        data2 -= epsilon
                                                                                                                                        
                        #print whichimage[ROT][0:100]
                        #data1 = data[ROT] - zp_correction 
                        #data2 = data1 - (data1/data1*scipy.median(data1))
                        #plot_color(color[ROT], data2)
                        
                        #print magErr[ROT][0:20]
                        calcim = sample+kind+'rot'+str(ROT)+FILTER
                        #print illum_dir
                        calcDataIllum(calcim,10000,8000,data2,magErr[ROT],X[ROT],Y[ROT],pth=illum_dir,rot=0,good=[Star[ROT],keyvalue])

                        var = variance(data2,magErr[ROT])
                        print 'second', var
                        dtmp['sdssstdcorr$' + str(ROT)] = var[1]**0.5
                        dtmp['sdssredchicorr$' + str(ROT)] = var[2]

                        dtmp.update({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME})
                        save_fit(dtmp)

                        print 'calcDataIllum', im, calcim, len(data[ROT])
                        #print params['SDSS_color'], 'SDSS_color'
                        print OBJNAME, FILTER, PPRUN, tmpdir

    return


def construct_correction(OBJNAME,FILTER,PPRUN):

    import scipy, re, string, os

    ''' create chebychev polynomials '''
    cheby_x = [{'n':'0x','f':lambda x,y:1.},{'n':'1x','f':lambda x,y:x},{'n':'2x','f':lambda x,y:2*x**2-1},{'n':'3x','f':lambda x,y:4*x**3.-3*x}] 
    cheby_y = [{'n':'0y','f':lambda x,y:1.},{'n':'1y','f':lambda x,y:y},{'n':'2y','f':lambda x,y:2*y**2-1},{'n':'3y','f':lambda x,y:4*y**3.-3*y}]
    cheby_terms = []
    cheby_terms_no_linear = []
    for tx in cheby_x:
        for ty in cheby_y:
            if not ((tx['n'] == '0x' and ty['n'] == '0y')): # or (tx['n'] == '0x' and ty['n'] == '1y') or (tx['n'] == '1x' and ty['n'] == '0y')) :
                cheby_terms.append({'n':tx['n'] + ty['n'],'fx':tx['f'],'fy':ty['f']})
            if not ((tx['n'] == '0x' and ty['n'] == '0y') or (tx['n'] == '0x' and ty['n'] == '1y') or (tx['n'] == '1x' and ty['n'] == '0y')) :
                cheby_terms_no_linear.append({'n':tx['n'] + ty['n'],'fx':tx['f'],'fy':ty['f']})
   
    cov = 1

    if cov:
        samples = [['sdss',cheby_terms,True]] #,['nosdss',cheby_terms_no_linear,False]] #[['nosdss',cheby_terms_no_linear],['sdss',cheby_terms]]
    else: 
        samples = [['nosdss',cheby_terms_no_linear,False]]

    sample = 'sdss'
    sample_size = 'all'
    import re, time                                                                                                                
    dt = get_a_file(OBJNAME,FILTER,PPRUN)                
    d = get_fits(OBJNAME,FILTER,PPRUN)                
    print d.keys()
    column_prefix = sample+'$'+sample_size+'$'
    position_columns_names = re.split('\,',d[column_prefix + 'positioncolumns']) 
    print position_columns_names, 'position_columns_names'
    fitvars = {}
    cheby_terms_dict = {}
    print column_prefix, position_columns_names
    for ele in position_columns_names:                      
        print ele
        if type(ele) != type({}):
            ele = {'name':ele}
        res = re.split('$',ele['name'])
        if string.find(ele['name'],'zp_image') == -1:
            fitvars[ele['name']] = float(d[sample+'$'+sample_size+'$'+ele['name']]) 
            for term in cheby_terms:
                if term['n'] == ele['name'][2:]:
                    cheby_terms_dict[term['n']] = term 
                                                                                     
    zp_images = re.split(',',d[sample+'$'+sample_size+'$zp_images'])
    zp_images_names = re.split(',',d[sample+'$'+sample_size+'$zp_images_names'])
                                                                                     
    for i in range(len(zp_images)):
        fitvars[zp_images_names[i]] = float(zp_images[i])
                                                                                     
    cheby_terms_use =  [cheby_terms_dict[k] for k in cheby_terms_dict.keys()]

    print cheby_terms_use, fitvars
    
    CHIPS = [int(x) for x in re.split(',',dt['CHIPS'])]
    LENGTH1, LENGTH2 = dt['LENGTH1'], dt['LENGTH2']

    per_chip = True

    coord_conv_x = lambda x:(2.*x-0-LENGTH1)/(LENGTH1-0) 
    coord_conv_y = lambda x:(2.*x-0-LENGTH2)/(LENGTH2-0) 

    ''' make images of illumination corrections '''                                                                  
    for ROT in [0,1]: #EXPS.keys():
        size_x=LENGTH1
        size_y=LENGTH2 
        bin=100
        import numpy, math, pyfits, os                                                                              
        x,y = numpy.meshgrid(numpy.arange(0,size_x,bin),numpy.arange(0,size_y,bin))
        F=0.1
        print 'calculating'
        x = coord_conv_x(x)
        y = coord_conv_y(y)
                                                                                                                                
        path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':OBJNAME}
        illum_dir = path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + PPRUN + '/' + str(ROT)
        os.system('mkdir -p ' + illum_dir)
        
        epsilon = 0
        index = 0
        for term in cheby_terms_use:
            index += 1
            print index, ROT, term, fitvars[str(ROT)+'$'+term['n']]
            epsilon += fitvars[str(ROT)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)
                                                                                                                                
        ''' save pattern w/o chip zps '''
                                                                                                                                
        print 'writing'
        hdu = pyfits.PrimaryHDU(epsilon)
                                                                                                                     
        im = illum_dir + '/nochipzps' + sample + sample_size +  '.fits'
        save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,sample+'$'+sample_size+'$'+str(ROT)+'$im':im})
                                                                                                                     
        os.system('rm ' + im)
        hdu.writeto(im)
                                                                                                                                
        ''' save pattern w/ chip zps '''

        trial = False 
        Test = False
        children = []
        if 1: #per_chip or same_chips:
            child = False                                                            
            for CHIP in CHIPS:
                if not trial:
                    child = os.fork()           
                    if child:
                        children.append(child)
                                                                             
                if not child:
                    if str(dt['CRPIX1_' + str(CHIP)]) != 'None':            
                        xmin = int(float(dt['CRPIX1ZERO'])) - int(float(dt['CRPIX1_' + str(CHIP)]))   
                        ymin = int(float(dt['CRPIX2ZERO'])) - int(float(dt['CRPIX2_' + str(CHIP)]))
                        xmax = xmin + int(dt['NAXIS1_' + str(CHIP)])
                        ymax = ymin + int(dt['NAXIS2_' + str(CHIP)])
                        
                        print xmin, xmax, xmax - xmin, ymin, ymax, ymax-ymin, CHIP, 'CHIP'
                        print int(xmin/bin), int(xmax/bin), int(ymin/bin), int(ymax/bin), CHIP, 'CHIP', bin, scipy.shape(epsilon)
                        print epsilon[int(xmin/bin):int(xmax/bin)][int(ymin/bin):int(ymax/bin)]
                        print fitvars.keys()
                        print 'zp', fitvars['zp_' + str(CHIP)]
                        epsilon[int(ymin/bin):int(ymax/bin),int(xmin/bin):int(xmax/bin)] += float(fitvars['zp_' + str(CHIP)])
                        x,y = numpy.meshgrid(numpy.arange(xmin,xmax,1),numpy.arange(ymin,ymax,1))
                        
                        x = coord_conv_x(x)
                        y = coord_conv_y(y)
                                                                                                                                                  
                        ''' correct w/ polynomial '''
                        epsilonC = 0
                        index = 0                                                                                                                
                                                                                                                                                  
                        #sum = [lambda u,v: fitvars[str(ROT)+'$'+term['n']]*term['fx'](u,v)*term['fy'](u,v) for term in cheby_terms_use]
                        #print sum
                        #p = lambda d,e: reduce(lambda a,b: a(d,e) + b(d,e), sum)
                                
                        for term in cheby_terms_use:
                            index += 1
                            print index, ROT, term, fitvars[str(ROT)+'$'+term['n']]
                            
                            epsilonC += fitvars[str(ROT)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)
                                                                                                                                                  
                        ''' add the zeropoint '''
                        epsilonC += float(fitvars['zp_' + str(CHIP)])
                                                                                                                                                
                        ''' save pattern w/o chip zps '''
                                                                                                                                                  
                        import math
                        print 'writing/converting to linear flux units'
                        hdu = pyfits.PrimaryHDU(10.**(epsilonC/2.5))
                        im = '/tmp/' + str(ROT) + '_' + str(CHIP) + '.fits'
                        os.system('rm ' + im)
                        hdu.writeto(im)
           
                    import sys
                    print 'exiting'
                    #if not trial:
                    if not trial:
                        sys.exit(0)
            for c in children:  
                os.waitpid(c,0)

        print 'finished'

        print 'writing'

        ''' apply the corrections to the images '''

        import MySQLdb, sys, os, re                                                                     
        db2,c = connect_except()
                                                                                                                             
        command  ="select file from illumination_db where SUPA not like '%I' and OBJNAME='" + OBJNAME + "' and PPRUN='" + PPRUN + "' and ROTATION='" + str(ROT) + "'"
        print command
        c.execute(command)
        results=c.fetchall()
        db_keys = describe_db(c,'illumination_db')
        files = []
        for line in results: 
            files.append(str(line[0]))
        db2.close()

        print files

        trial = False 

        for file in files:
            children = []
            for CHIP in CHIPS:
                child = False                                                            
                if not trial:
                    child = os.fork()           
                    if child:
                        children.append(child)
                                                                             
                if not child:

                    RUN = re.split('\_',PPRUN)[0]                                                                
                    
                    p = re.compile('\_\d+O')                                               
                    file_chip = p.sub('_' + str(CHIP) + 'O',file)#.replace('.fits','.sub.fits')
                    import commands
                    info = commands.getoutput('dfits ' + file_chip + ' | fitsort -d ROTATION')
                    print info, file_chip
                    CHIP_ROT = str(int(re.split('\s+',info)[1]))

                    file_short = re.split('\/',file_chip)[-1] 
                    SUPA = re.split('\_',file_short)[0]
                    print SUPA
                    if Test:
                        file_short = file_short.replace(SUPA,SUPA+'I') 
                        file_chip.replace(SUPA,SUPA+'I')

                    if int(CHIP_ROT) == int(ROT):
                        im = '/tmp/' + str(CHIP_ROT) + '_' + str(CHIP) + '.fits'        
                        print im
                        weight_file = file_chip.replace('SCIENCE','WEIGHTS').replace('.fits','.weight.fits')
                        flag_file = file_chip.replace('SCIENCE','WEIGHTS').replace('.fits','.flag.fits')
                        print file_chip, weight_file
                        
                        directory = reduce(lambda x,y: x + '/' + y, re.split('\/',file_chip)[:-1])
                        print directory, 'directory' ,file 
                                                                                                                     
                        filter_dir = directory.replace(FILTER+'_'+RUN,FILTER) 

                        if Test:
                            out_directory = os.environ['subdir'] + '/TEST/' + FILTER + '_' + RUN + '/SCIENCE/' 
                            out_filter_dir = os.environ['subdir'] + '/TEST/' + FILTER + '/SCIENCE/'
                            out_file =  os.environ['subdir'] + '/TEST/' + FILTER + '_' + RUN + '/SCIENCE/' +  file_short.replace('.fits','I.fits')
                            out_weight_file = out_file.replace('SCIENCE','WEIGHTS').replace('.fits','.weight.fits')
                            out_flag_file = out_file.replace('SCIENCE','WEIGHTS').replace('.fits','.flag.fits')
                            os.system('mkdir -p ' + out_directory)
                            os.system('mkdir -p ' + out_directory.replace('SCIENCE','WEIGHTS'))
                                                                                                                     
                            ''' make link to the header information '''                                                   
                            from glob import glob
                            print directory
                            
                            os.system('mkdir -p ' + out_filter_dir)
                            print filter_dir, directory, out_filter_dir, out_directory, 'dirs'
                                                                                                                         
                            print filter_dir+ '/head*'
                            print glob(filter_dir+ '/head*')
                            for file_scamp in glob(filter_dir+ '/head*'):
                                command = 'ln -s ' +  file_scamp +  ' ' + out_filter_dir 
                                print command
                                os.system(command)

                            os.system('rm ' + out_weight_file)                                                            
                            command = 'ln -s  ' + weight_file + ' ' + out_weight_file
                            print command
                            os.system(command)
                                                                                                                          
                            os.system('rm ' + out_flag_file)
                            command = 'ln -s  ' + flag_file + ' ' + out_flag_file
                            print command
                            os.system(command)
                                                                                                                         
                            command = 'sethead ' + out_file + ' OBJNAME=TEST' 
                            print command
                            os.system(command)
                        else:
                            out_file =  os.environ['subdir'] + '/' + OBJNAME + '/' + FILTER + '/SCIENCE/' +  file_short.replace('.fits','I.fits')

                        command = "ic '%1 %2 *' " + file_chip + " " + im + "> " + out_file 
                        print command
                        os.system(command)

                    import sys
                    if not trial:
                        sys.exit(0)
                
            for child in children:  
                os.waitpid(child,0)
            print 'finished'

def correct_image():
    ''' make diagnostic plots '''                                                                                           
    if 1:
        import re
        d = get_fits(CLUSTER,FILTER,PPRUN)                
        column_prefix = sample+'$'+sample_size+'$'
        position_columns_names = re.split('\,',d[column_prefix + 'positioncolumns']) 
        fitvars = {}
        cheby_terms_dict = {}
        for ele in position_columns:                      
            res = re.split('$',ele['name'])
            fitvars[ele['name']] = float(d[sample+'$'+sample_size+'$'+ele['name']])
            for term in cheby_terms:
                if term['n'] == ele['name'][2:]:
                    cheby_terms_dict[term['n']] = term 
        cheby_terms_use =  [cheby_terms_dict[k] for k in cheby_terms_dict.keys()]
                                                                                                                          
        print cheby_terms_use, fitvars
                                                                                                                          
        ''' make images of illumination corrections '''                                                                  
        for ROT in EXPS.keys():
            size_x=LENGTH1
            size_y=LENGTH2
            bin=100
            import numpy, math, pyfits, os                                                                              
            x,y = numpy.meshgrid(numpy.arange(0,size_x,bin),numpy.arange(0,size_y,bin))
            F=0.1
            print 'calculating'
            x = coord_conv_x(x)
            y = coord_conv_y(y)
            
            epsilon = 0
            index = 0
            for term in cheby_terms_use:
                index += 1
                print index, ROT, term, fitvars[str(ROT)+'$'+term['n']]
                epsilon += fitvars[str(ROT)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)
                                                                                                                          
                                                                                                                          
            print 'writing'
            hdu = pyfits.PrimaryHDU(epsilon)


def residual_plots():
    for ROT in EXPS.keys():
        print 'ROT', ROT
        fitvars = {} 
        for ele in position_columns:                      
            res = re.split('$',ele['name'])
            if res[0] == ROT:
                fitvars[ele['name'][2:]] = U[ele['index']] 
                save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'CLUSTER':CLUSTER,sample+'$'+sample_size+'$'+ele['name'].replace('$','$'):fitvars[ele['name'][2:]]})
                print ele['name'], fitvars[ele['name'][2:]]
        
        if 0:
            uu = open(tmpdir + '/fitvars' + ROT,'w')
            import pickle
            pickle.dump(fitvars,uu)
            uu.close()
        
        size_x=8000
        size_y=10000
        bin=100
        import numpy, math, pyfits, os                                                                              
        x,y = numpy.meshgrid(numpy.arange(0,size_x,bin),numpy.arange(0,size_y,bin))
        F=0.1
        print 'calculating'

        x = coord_conv_x(x)
        y = coord_conv_y(y)
        
        epsilon = 0
        for term in cheby_terms_use:
            epsilon += fitvars[term['n']]*term['fx'](x,y)*term['fy'](x,y)
        
        print 'writing'
        hdu = pyfits.PrimaryHDU(epsilon)
        #os.system('rm ' + tmpdir + '/correction' + ROT + filter + sample_size + '.fits')
        #hdu.writeto(tmpdir + '/correction' + ROT + filter + sample_size + '.fits')
                                                                                                                                               
        path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':CLUSTER}
        illum_dir = path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + str(ROT)
        os.system('mkdir -p ' + illum_dir)
                                                                                                                                               
        im = illum_dir + '/correction' + sample + sample_size + '.fits'
        save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'CLUSTER':CLUSTER,sample+'$'+sample_size+'$'+str(ROT)+'$im':im})
                                                                                                                                               
        os.system('rm ' + im)
        hdu.writeto(im)
        
        #print 'done'
        
        epsilon = 10.**(epsilon/2.5)
        
        #correction = 10.**(epsilon/2.5)
        # xaxis is always vertical!!!
        #print 'writing'
        #hdu = pyfits.PrimaryHDU(epsilon)
        #os.system('rm ' + tmpdir + '/fcorrection' + ROT + filter + '.fits')
        #hdu.writeto(tmpdir + '/fcorrection' + ROT + filter + '.fits')
        #print 'done'
    return



def fit():
    maxSigIter=50
    solutions = [] 

    import pickle
    ''' get data '''
    EXPS = getTableInfo()
    print EXPS
    
    #ROTS, data, err, X, Y, maxVal, classStar = diffCalcNew()
    #save = {'ROTS': ROTS, 'data':data,'err':err,'X':X,'Y':Y,'maxVal':maxVal,'classStar':classStar}
    #uu = open(tmpdir + '/store','w')
    #import pickle
    #pickle.dump(save,uu)
    #uu.close()
   
    ''' EXPS has all of the image information for different rotations '''

    ''' make model '''
    fit = make_model(EXPS)
    print fit
    star_good = selectGoodStars(EXPS)
    uu = open(tmpdir + '/store','w')
    import pickle
    pickle.dump(star_good,uu)
    uu.close()

    import pickle
    f=open(tmpdir + '/store','r')
    m=pickle.Unpickler(f)
    star_good=m.load()






    fit['class'] = phot_funct(fit['model'],fit['fixed'],EXPS,star_good,fit['apply'])

    import astropy, astropy.io.fits as pyfits
    p = pyfits.open(tmpdir + '/final.cat')
    table = p[1].data

    import copy
    table_save = copy.copy(table)
    for i in range(maxSigIter):
        fa = {"table": table_save}
        func = fit['class'].calc_model 

        #functkw takes input data arrays
        #parinfo takes initial guess and constraints on parameters 
        #import optimize
        #params, covar, info, mesg, ier = optimize.leastsq(func,guess,args = (points,vals,errs), full_output=True)
        




        import mpfit
        m =  mpfit.mpfit(func, functkw=fa,
                         parinfo=fit['class'].parstart,
                         maxiter=1000, quiet=0)
        print m.params, m.perror 
        if (m.status <= 0):
            print 'error message = ', m.errmsg
            condition = Numeric.zeros(len(data))
            break
        print m.params,m.perror
        #fits = [{'vars':['zp','color1coeff','color1coeff2'],'parinfo':[{'value':p[0],'fixed':0},{'value':p[1],'fixed':0},{'value':p[2],'fixed':0},'function':phot_funct_secondorder,'fit_type':'no_airmass'}]
        fit['class'].fitvars = {}
        for ele in range(len(fit['class'].smodel)):                              
            print ele, fit['class'].smodel
            name = make_name(fit['class'].smodel[ele])
            print ele, fit['class'].fitvars, name, m.params[ele] 
            fit['class'].fitvars[name] = m.params[ele]          
            fit['class'].fitvars[name + '_err'] = m.perror[ele]
        perror = copy.copy(m.perror)
                                                                                                                                                                                                               
        # Compute a 3 sigma rejection criterion
        print m.params, data_rec[0], data[0]
        #condition, redchisq = SigmaCond(params, data_save, data,
        #                           airmass_save, airmass,
        #                           color1_save, color1, color2_save, color2, err_save, err, sigmareject)
                                                                                                                                                                                                               


        calcIllum(10000, 10000, 100, fit)

        if len(data_save) > 1:                                                                     
            (mo_save, reddm) = fit['class'].calc_sigma(m.params, airmass_save, color1_save, color2_save, data_save, err_save, X_save, Y_save)
            #reddm = (data-mo)/err
            redchisq = Numeric.sqrt(Numeric.sum(Numeric.power(reddm, 2)) / (len(reddm) - 1))
            dm = data_save-mo_save
            #dm_save = data_save - mo_save
            print len(data_save), len(mo_save)
            dm_save = data_save - mo_save
            mean =  Numeric.sum(dm)/len(dm)
            sigma = Numeric.sqrt(Numeric.sum(Numeric.power(mean-dm, 2)) / (len(dm) - 1))
            # you can pick either 
            #condition = Numeric.less(Numeric.fabs(dm_save), float(sigmareject) * sigma)
            condition = Numeric.less(Numeric.fabs(dm_save), float(sigmareject) * err_save)
        else:
            condition = Numeric.zeros(len(data_save))
          
        print redchisq 
        # Keep everything (from the full data set!) that is within
        # the 3 sigma criterion
        #data_sig = Numeric.compress(condition, data_save)
        data = Numeric.compress(condition, data_rec)
        err = Numeric.compress(condition, err_save)
        X = Numeric.compress(condition, X_save)
        Y = Numeric.compress(condition, Y_save)
        new_len = len(data)
        
        if float(new_len)/float(save_len) < 0.5:
            print "Rejected more than 50% of all measurements."
            print "Aborting this fit."
            break
        
        # No change
        if new_len == old_len:
            print "Converged! (%d iterations)" % (i+1, )
            print "Kept %d/%d stars." % (new_len, save_len)
            break
    #print params, perror, condition
    meanerr = Numeric.sum(err_save)/len(err_save)

def make_name(name): 
    if len(name) > 1:                               
        name = reduce(lambda x,y: x + 'T' + y,name)
    else: 
        name = name[0]
    return name

''' reduce size od SDSS data '''
def convert_SDSS_cat(SUPA,FLAT_TYPE):
    from config_bonn import info
    import utilities, Numeric, os
    reload(utilities)
    from utilities import *

    dict = get_files(SUPA,FLAT_TYPE)
    print dict.keys()
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)

    print dict['starcat']
    import astropy, astropy.io.fits as pyfits
    hdulist1 = pyfits.open(dict['starcat'])
    #print hdulist1["STDTAB"].columns
    table = hdulist1["STDTAB"].data

    other_info = info[dict['filter']]
    filters_info = make_filters_info([dict['filter']])                     
    compband = filters_info[0][1] ## use the SDSS/other comparison band
    color1which = other_info['color1']
    print filters_info, compband
    print dict['OBJNAME']
    for key in dict.keys():
        import string
        if string.find(key,'color') != -1:
            print key
    
    cols = [pyfits.Column(name=column.name, format=column.format,array=Numeric.array(0 + hdulist1["STDTAB"].data.field(column.name))) for column in hdulist1["STDTAB"].columns]
    cols.append(pyfits.Column(name='stdMag_corr', format='E',array=Numeric.array(0 + hdulist1["STDTAB"].data.field(compband+'mag'))))
    cols.append(pyfits.Column(name='stdMagErr_corr', format='E',array=Numeric.array(0 + hdulist1["STDTAB"].data.field(compband+'err'))))
    cols.append(pyfits.Column(name='stdMagColor_corr', format='E',array=Numeric.array(0 + hdulist1["STDTAB"].data.field(color1which))))
    cols.append(pyfits.Column(name='stdMagClean_corr', format='E',array=Numeric.array(0 + hdulist1["STDTAB"].data.field('Clean'))))

    type = 'star'
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':search_params['OBJNAME']}
    outcat = path + 'PHOTOMETRY/ILLUMINATION/sdssmatch__' + search_params['SUPA'] + '_' +  type + '.cat'
    print cols
    hdu = pyfits.PrimaryHDU()
    hdulist = pyfits.HDUList([hdu])
    tbhu = pyfits.BinTableHDU.from_columns(cols)
    hdulist.append(tbhu)
    hdulist[1].header['EXTNAME']='OBJECTS'
    os.system('rm ' + outcat)
    hdulist.writeto( outcat )
    print 'wrote out new cat'

    save_exposure({'sdssmatch':outcat},SUPA,FLAT_TYPE)

def apply_photometric_calibration(SUPA,FLAT_TYPE,starcat):
    from config_bonn import info
    import utilities, Numeric, os
    reload(utilities)

    dict = get_files(SUPA,FLAT_TYPE)
    print dict.keys()
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)

    #print dict['starcat']
    import astropy, astropy.io.fits as pyfits
    hdulist1 = pyfits.open(starcat)
    #print hdulist1["STDTAB"].columns
    table = hdulist1["STDTAB"].data

    other_info = info[dict['filter']]
    filters_info = utilities.make_filters_info([dict['filter']])                     
    compband = filters_info[0][1] ## use the SDSS/other comparison band
    color1which = other_info['color1']
    print filters_info, compband
    print dict['OBJNAME']
    for key in dict.keys():
        import string
        if string.find(key,'color') != -1:
            print key
    #calib = get_calibrations_threesecond(dict['OBJNAME'],filters_info)
    #print 'calib', calib
    #raw_input()
    model = utilities.convert_modelname_to_array('zpPcolor1') #dict['model_name%'+dict['filter']])

    cols = [] #pyfits.Column(name=column.name, format=column.format,array=Numeric.array(0 + hdulist1["STDTAB"].data.field(column.name))) for column in hdulist1["STDTAB"].columns]
    print cols
    #print start

    print 'data start'
    #data = utilities.color_std_correct(model,dict,table,dict['filter'],compband+'mag',color1which) # correct standard magnitude into instrumntal system -- at least get rid of the color term
    
    from copy import copy 
    data = copy(table.field(compband+'mag'))
    print 'data done'
    
    cols.append(pyfits.Column(name='stdMag_corr', format='E',array=data))
    cols.append(pyfits.Column(name='stdMagErr_corr', format='E',array=Numeric.array(0 + hdulist1["STDTAB"].data.field(compband+'err'))))
    cols.append(pyfits.Column(name='stdMagColor_corr', format='E',array=Numeric.array(0 + hdulist1["STDTAB"].data.field(color1which))))
    cols.append(pyfits.Column(name='stdMagClean_corr', format='E',array=Numeric.array(0 + hdulist1["STDTAB"].data.field('Clean'))))

    type = 'star'
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':search_params['OBJNAME']}
    outcat = path + 'PHOTOMETRY/ILLUMINATION/sdssmatch__' + search_params['SUPA'] + '_' +  type + '.cat'
    print cols
    hdu = pyfits.PrimaryHDU()
    hdulist = pyfits.HDUList([hdu])
    tbhu = pyfits.BinTableHDU.from_columns(cols)
    hdulist.append(tbhu)
    hdulist[1].header['EXTNAME']='OBJECTS'
    os.system('rm ' + outcat)
    print 'writing out new cat'
    hdulist.writeto( outcat )
    print 'wrote out new cat'

    save_exposure({'sdssmatch':outcat},SUPA,FLAT_TYPE)


''' read in the photometric calibration and apply it to the data '''
def get_cats_ready(SUPA,FLAT_TYPE,galaxycat,starcat):

    from config_bonn import info, wavelength_order

    import utilities, Numeric, os
    reload(utilities)

    dict = get_files(SUPA,FLAT_TYPE)
    print dict.keys()
    search_params = initialize(dict['filter'],dict['OBJNAME'])
    search_params.update(dict)

    ''' figure out the correct color and magnitudes for the filter '''

    colors_in_cat = ['W-C-RC','W-S-Z+']

    def find_index(color):
        index = -99
        for i in range(len(wavelength_order)):
            if wavelength_order[i] == color:
                index = i
        if index == -99: 
            raise CantFindFilter
        return index
    
    colors_indices = [find_index(color) for color in colors_in_cat]

    print colors_indices

    
    #raw_input()


    #print dict['starcat']
    tmp = {}
    import astropy, astropy.io.fits as pyfits
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(OBJNAME)s/' % {'OBJNAME':search_params['OBJNAME']}
    for type,cat in [['star',starcat]]: #['galaxy',galaxycat],
        hdulist1 = pyfits.open(cat)                                                                                                                                                                
        #print hdulist1["STDTAB"].columns
        table = hdulist1["STDTAB"].data
        
        other_info = info[dict['filter']]
        filters_info = utilities.make_filters_info([dict['filter']])                     
        compband = filters_info[0][1] ## use the SDSS/other comparison band
        color1which = other_info['color1']
        print filters_info, compband
        print dict['OBJNAME']
        for key in dict.keys():
            import string
            if string.find(key,'color') != -1:
                print key
        #calib = get_calibrations_threesecond(dict['OBJNAME'],filters_info)
        #print 'calib', calib
        #raw_input()
        model = utilities.convert_modelname_to_array('zpPcolor1') #dict['model_name%'+dict['filter']])
        
        cols = [] #pyfits.Column(name=column.name, format=column.format,array=Numeric.array(0 + hdulist1["STDTAB"].data.field(column.name))) for column in hdulist1["STDTAB"].columns]
        print cols
        #print start
        
        print 'data start'
        #data = utilities.color_std_correct(model,dict,table,dict['filter'],compband+'mag',color1which) # correct standard magnitude into instrumntal system -- at least get rid of the color term
        
        from copy import copy 
        data = copy(table.field(compband+'mag'))
        print 'data done', 'here'
       
        print (data) 
        cols.append(pyfits.Column(name='stdMag_corr', format='E',array=data))
        #print (Numeric.array(0 + hdulist1["STDTAB"].data.field(compband+'err')))
        cols.append(pyfits.Column(name='stdMagErr_corr', format='E',array=Numeric.array(0 + hdulist1["STDTAB"].data.field(compband+'err'))))

        #print (Numeric.array(0 + hdulist1["STDTAB"].data.field(color1which)))
        cols.append(pyfits.Column(name='stdMagColor_corr', format='E',array=Numeric.array(0 + hdulist1["STDTAB"].data.field(color1which))))

        #print (Numeric.array(0 + hdulist1["STDTAB"].data.field('Clean')))
        cols.append(pyfits.Column(name='stdMagClean_corr', format='E',array=Numeric.array(0 + hdulist1["STDTAB"].data.field('Clean'))))

        #print (Numeric.array(0 + hdulist1["STDTAB"].data.field('Ra')))
        cols.append(pyfits.Column(name='ALPHA_J2000', format='E',array=Numeric.array(0 + hdulist1["STDTAB"].data.field('Ra'))))

        #print (Numeric.array(0 + hdulist1["STDTAB"].data.field('Dec')))
        cols.append(pyfits.Column(name='DELTA_J2000', format='E',array=Numeric.array(0 + hdulist1["STDTAB"].data.field('Dec'))))

        #print (Numeric.array(0 + hdulist1["STDTAB"].data.field('SeqNr')))
        cols.append(pyfits.Column(name='SeqNr', format='E',array=Numeric.array(0 + hdulist1["STDTAB"].data.field('SeqNr'))))
        length = len(hdulist1["STDTAB"].data.field('SeqNr'))
        if type == 'star':
            cols.append(pyfits.Column(name='Star_corr', format='E',array=Numeric.ones(length)))
        else: 
            cols.append(pyfits.Column(name='Star_corr', format='E',array=Numeric.zeros(length)))

        outcat = path + 'PHOTOMETRY/ILLUMINATION/' + type + 'sdssmatch__' + search_params['SUPA'] + '_' +  type + '.cat'
        print cols, 'here'
        hdu = pyfits.PrimaryHDU()
        print 'hdulist'
        hdulist = pyfits.HDUList([hdu])
        print 'tbhu'
        tbhu = pyfits.BinTableHDU.from_columns(cols)
        print 'hdulist'
        hdulist.append(tbhu)
        print 'headers'
        hdulist[1].header['EXTNAME']='OBJECTS'
        os.system('rm ' + outcat)
        print 'writing out', outcat 
        hdulist.writeto( outcat )
        print 'wrote out new cat'
        save_exposure({type + 'sdssmatch':outcat},SUPA,FLAT_TYPE)
        tmp[type + 'sdssmatch'] = outcat

    import calc_tmpsave
    outcat = path + 'PHOTOMETRY/ILLUMINATION/sdssmatch__' + search_params['SUPA'] + '_' +  type + '.cat'
    #calc_tmpsave.paste_cats([tmp['galaxysdssmatch'],tmp['starsdssmatch']],outcat,index=1)

    calc_tmpsave.paste_cats([tmp['starsdssmatch']],outcat,index=1)

    #calc_tmpsave.paste_cats([tmp['galaxysdssmatch']],outcat,index=1)
    #print tmp['galaxysdssmatch'],tmp['starsdssmatch']

    #calc_tmpsave.paste_cats([tmp['galaxysdssmatch']],outcat,index=1)
    print 'added', outcat

    return outcat 


def plot_color(color,data,a=None,m=None):
    import numpy, math, pyfits, os                                                                              
    import copy
    from ppgplot   import *

    pgbeg("/XTERM",1,1)
                                                                                                                                             
    pgiden()
    pgpanl(1,1) 
    from Numeric import *
    x = copy.copy(color) #hdulist1["OBJECTS"].data.field(color1which)
    y = copy.copy(data) #hdulist1["OBJECTS"].data.field(compband+'mag') - data
    plotx = copy.copy(x)
    ploty = copy.copy(y)
    x.sort()    
    y.sort()
    mediany = y[int(len(y)/2.)]
    lowx=-2 #x[2]
    highx=2 #x[-2]
    lowy=mediany + 1.5
    highy=mediany -1.5
    pgswin(lowx,highx,lowy,highy)
    plotx = array(plotx)
    ploty = array(ploty)
    if a is not None:
        print a, m
        pgline(array(a), array(m))
    #pylab.scatter(z,x)
    pglab('Mag','Mag - Mag(Inst)')
    #print plotx, ploty
    pgpt(plotx,ploty,3)
    
    pgbox()
    pgend()

def hold():
    if 0: #star['sdss']:
        star_A = []
        star_B = []
        sigmas = []
        for exp in star['supa files']:
            row_num += 1 
            col_num = -1 
            rotation = exp['rotation'] 
            #sigma = tab[str(rotation) + '$' + exp['name'] + '$MAGERR_AUTO'][star['table index']] 
            sigma = tab['SDSSstdMagErr_corr'][star['table index']] 
            for c in position_columns:
                col_num += 1
            first_column = True
            for c in zp_columns:
                col_num += 1
                ''' remember that the good magnitude does not have any zp dependence!!! '''
                #if (first_column is not True  and c['image'] == exp['name']) or c['image'] == 'sdss':
                if c['image'] == 'sdss': 
                    value = 1./sigma
                    star_A.append([row_num,col_num,value])
                first_column = False
            
            ''' fit for the color term dependence '''
            for c in color_columns:
                col_num += 1
                value = tab['SDSSstdMagColor_corr'][star['table index']]/sigma
                star_A.append([row_num,col_num,value])
            
            col_num += 1
            ''' magnitude column -- include the correct/common magnitude '''
            value = 1./sigma
            star_A.append([row_num,col_num+supa_num,value])
            #value = (tab[str(rotation)+'$'+exp['name']+'$MAG_AUTO'][star['table index']] - tab['SDSSstdMag_corr'][star['table index']])/sigma
            #print  tab[str(rotation)+'$'+exp['name']+'$MAG_AUTO'][star['table index']], tab['SDSSstdMag_corr'][star['table index']]
            data[rotation].append(tab[str(rotation)+'$'+exp['name']+'$MAG_AUTO'][star['table index']] - tab['SDSSstdMag_corr'][star['table index']])
            magErr[rotation].append(tab['SDSSstdMagErr_corr'][star['table index']])
            whichimage[rotation].append(exp['name'])
            X[rotation].append(tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS'][star['table index']])
            Y[rotation].append(tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS'][star['table index']])
            color[rotation].append(tab['SDSSstdMagColor_corr'][star['table index']])
            star_B.append([row_num,value])
            sigmas.append(sigma)
        inst.append({'type':'sdss','A_array':star_A, 'B_array':star_B, 'sigma_array': sigmas})

def save_fit(dict,OBJNAME=None,FILTER=None,PPRUN=None):
    if OBJNAME!= None and FILTER!= None and  PPRUN!=None:
        dict['OBJNAME'] = OBJNAME 
        dict['FILTER'] = FILTER 
        dict['PPRUN'] = PPRUN 

    db2,c = connect_except()

    db = 'fit_db'
    
    #c.execute("DROP TABLE IF EXISTS fit_db")
    command = "CREATE TABLE IF NOT EXISTS " + db + " ( id MEDIUMINT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id))"
    #print command
    c.execute(command)

    db_keys = describe_db(c,db)

    from copy import copy
    floatvars = {}  
    stringvars = {}
    #copy array but exclude lists                                                   
    import string, traceback, sys
    letters = string.ascii_lowercase + string.ascii_uppercase.replace('E','') + '_' + '-' + ','
    for ele in dict.keys():
        
            type = 'float'                               
            for l in letters:
                if string.find(str(dict[ele]),l) != -1: 
                    type = 'string'
            if type == 'float':  
                floatvars[ele] = str(float(dict[ele])) 
            elif type == 'string':
                stringvars[ele] = dict[ele] 
                                                                                                                                                                                                           
    # make database if it doesn't exist
    #print 'floatvars', floatvars
    #print 'stringvars', stringvars
    for column in stringvars: 
        stop = False
        for key in db_keys:
            import string
            if key.lower() == column.lower(): stop = True 
        if not stop:
            try:                                                                       
                if string.find(column,'reject_plot') != -1 or string.find(column,'im') != -1 or string.find(column,'positioncolumns') != -1 or string.find(column,'zp_image') != -1: 
                    command = 'ALTER TABLE ' + db + ' ADD ' + column + ' varchar(500)'
                else:
                    command = 'ALTER TABLE ' + db + ' ADD ' + column + ' varchar(100)'
                c.execute(command)  
            except:
                print traceback.print_exc(file=sys.stdout)
                                                                                                                                                                                                          
    for column in floatvars: 
        stop = False                                       
        for key in db_keys:
            import string
            if key.lower() == column.lower(): stop = True 
        if not stop:
            try:                                                                
                command = 'ALTER TABLE ' + db + ' ADD ' + column + ' float(15)'
                c.execute(command)  
            except:
                print traceback.print_exc(file=sys.stdout)

    # insert new observation 

    #print db_keys


    OBJNAME = dict['OBJNAME']                                                                                                                                     
    FILTER = dict['FILTER']
    PPRUN = dict['PPRUN']
    command = "SELECT OBJNAME from " + db + " where OBJNAME = '" + OBJNAME + "' and FILTER = '" + FILTER + "' and PPRUN='" + PPRUN + "'"
    #print command
    c.execute(command)
    #print OBJNAME, FILTER, PPRUN
    results = c.fetchall() 
    #print results
    if len(results) > 0:
        print 'already added'
    else:
        command = "INSERT INTO " + db + " (OBJNAME,FILTER,PPRUN) VALUES ('" + dict['OBJNAME'] + "','" + dict['FILTER'] + "','" + dict['PPRUN'] + "')"
        #print command
        c.execute(command) 
                                                                                                                                                                  
    import commands
                                                                                                                                                                  
    vals = ''
    for key in stringvars.keys():
        #print key, stringvars[key]
        vals += ' ' + key + "='" + str(stringvars[key]) + "',"
                                                                                                                                                                  
    for key in floatvars.keys():
        #print key, floatvars[key]
        vals += ' ' + key + "='" + floatvars[key] + "',"
    vals = vals[:-1]

    if len(vals) > 1:
        command = "UPDATE " + db + " set " + vals + " WHERE OBJNAME='" + dict['OBJNAME'] + "' AND FILTER='" + dict['FILTER'] + "' AND PPRUN='"  + dict['PPRUN'] + "'" 
        c.execute(command)
        
    #print vals
    #names = reduce(lambda x,y: x + ',' + y, [x for x in floatvars.keys()])
    #values = reduce(lambda x,y: str(x) + ',' + str(y), [floatvars[x] for x in floatvars.keys()])
    #names += ',' + reduce(lambda x,y: x + ',' + y, [x for x in stringvars.keys()])
    #values += ',' + reduce(lambda x,y: x + ',' + y, ["'" + str(stringvars[x]) + "'" for x in stringvars.keys()])
    #command = "INSERT INTO illumination_db (" + names + ") VALUES (" + values + ")"
    #print command
    #os.system(command)

def gather_exposures_all(filters=None):
    #if not filters:
    #    filters =  ['B','W-J-B','W-J-V','W-C-RC','W-C-IC','I','W-S-Z+']        

    import os, re
    from glob import glob
    dirs = glob(os.environ['subdir'] + '/*')
    print len(dirs)
    for i in range(len(dirs)):
        dir = dirs[i]
        print 'dir',dir
        subdirs = glob(dir + '/*')
        for subdir in subdirs: 
            try:
                slash = re.split('/',subdir)[-1]                                                                                                                                                                                                                
                res = re.split('_',slash)
                if len(res) > 1:
                    files = glob(subdir+'/SCIENCE/*fits')
                    if len(files)>0:
                        #search_params = initialize(filter,OBJNAME)                                                                                                                                                 
                        import os, re, bashreader, sys, string, utilities
                        from glob import glob
                        from copy import copy
                        
                        #files = glob(searchstr)
                        files.sort()
                        exposures =  {} 
                        
                        import MySQLdb, sys, os, re                                                                     
                        db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
                        c = db2.cursor()
                        
                        for file in files:
                            if string.find(file,'links') == -1 and string.find(file,'wcs') == -1 and string.find(file,'.sub.fits') == -1:
                                res = re.split('_',re.split('/',file)[-1])                                        
                                exp_name = res[0]
                                if not exposures.has_key(exp_name): exposures[exp_name] = {'images':[],'keywords':{}}
                                exposures[exp_name]['images'].append(file) # exp_name is the root of the image name
                                if len(exposures[exp_name]['keywords'].keys()) == 0: #not exposures[exp_name]['keywords'].has_key('ROTATION'): #if exposure does not have keywords yet, then get them -- this makes sure you only record each SUPA file once!!!
                                    #exposures[exp_name]['keywords']['filter'] = filter
                                    exposures[exp_name]['keywords']['file'] = file 
                                    res2 = re.split('/',file)   
                                    #for r in res2:
                                    #    if string.find(r,filter) != -1:
                                    #        print r
                                    #        exposures[exp_name]['keywords']['date'] = r.replace(filter + '_','')
                                    #        exposures[exp_name]['keywords']['fil_directory'] = r 
                                    #        search_params['fil_directory'] = r
                                    kws = utilities.get_header_kw(file,['CRVAL1','CRVAL2','ROTATION','OBJECT','GABODSID','CONFIG','EXPTIME','AIRMASS','INSTRUM','PPRUN','BADCCD','FILTER']) # return KEY/NA if not SUBARU 
                                                                                                                                                                                                                                                                
                                    ''' figure out PPRUN '''
                                    import commands
                                    readlink = commands.getoutput('readlink -f ' + file)
                                    res = re.split('SUBARU/',readlink)
                                    res = re.split('/',res[1])
                                    kws['PPRUN'] = res[0]
                                                                                                                                                                                                                                                                
                                    ''' firgure out OBJNAME '''
                                    res = re.split('SUBARU/',file)
                                    res = re.split('/',res[1])
                                    kws['OBJNAME'] = res[0]
                                    print kws['OBJNAME'], 'OBJNAME'
                                                                                                                                                                                                                                                                
                                    ''' figure out a way to break into SKYFLAT, DOMEFLAT '''
                                    ppid = str(os.getppid())
                                    command = 'dfits ' + file 
                                    file = commands.getoutput(command)
                                    import string                    
                                    if string.find(file,'SKYFLAT') != -1: exposures[exp_name]['keywords']['FLAT_TYPE'] = 'SKYFLAT' 
                                    elif string.find(file,'DOMEFLAT') != -1: exposures[exp_name]['keywords']['FLAT_TYPE'] = 'DOMEFLAT' 
                                    import string                    
                                    file = re.split('\n',file)
                                    for line in file:
                                        print line
                                        if string.find(line,'Flat frame:') != -1 and string.find(line,'illum') != -1:
                                            import re                   
                                            res = re.split('SET',line)
                                            if len(res) > 1:
                                                res = re.split('_',res[1])                                                                                                                                 
                                                set = res[0]
                                                exposures[exp_name]['keywords']['FLAT_SET'] = set
                                                                                                                                                                                                          
                                                res = re.split('illum',line)
                                                res = re.split('\.',res[1])
                                                smooth = res[0]
                                                exposures[exp_name]['keywords']['SMOOTH'] = smooth 
                                            break
                                                                                                                                                                                                      
                                    for kw in kws.keys(): 
                                        exposures[exp_name]['keywords'][kw] = kws[kw]
                                    exposures[exp_name]['keywords']['SUPA'] = exp_name
                                    #exposures[exp_name]['keywords']['OBJNAME'] = OBJNAME 
                                    print exposures[exp_name]['keywords']
                                    save_exposure(exposures[exp_name]['keywords'])
                                                                                                                                                                                                                                                                
                                    #raw_input()
            except KeyboardInterrupt:                                                                
                raise
            except: 
                ppid_loc = str(os.getppid())
                print sys.exc_info()
                print 'something else failed',ppid, ppid_loc 

    return exposures

def run_telarchive(ra,dec,objname):

    from ephem import *
    coord = Equatorial(str(ra/15.),str(dec))
    ra = str(coord.get()[0]).replace(':',' ')
    dec = str(coord.get()[1]).replace(':',' ')
   
    print 'ra','dec',ra,dec 

    import commands, re, string
    command = 'python dosearch.py --coords="' + ra + ' ' + dec + '" 6.0'
    print command
    out = commands.getoutput(command)
    #i = open('ij','w')
    #i.write(out)
    #i.close()
    #out = open('ij','r').read()

    print out
    res = re.split('\n',out)
    print res
    d = {}
    for i in res:
        res_t = re.split('\t',i)

        if len(res_t) > 1:
            if res_t[1] != '':                                                   
                name = re.split('\s+',re.split(':',res_t[1])[0])[0]
                d[name + '_info'] = ' '
                if string.find(re.split(':',res_t[1])[1],'No data found') != -1:
                    d[name + '_data'] = 0
                elif  string.find(re.split(':',res_t[1])[0],'Sloan Digital') != -1:
                    d[name + '_data'] = 1
                else: 
                    print res_t[1]
                    a = re.split(':',res_t[1])[1]
                    print a
                    b = re.split('\(',a)[1]
                    c = re.split('\s+',b)[0]
                    d[name + '_data'] = c
            else: d[name + '_info'] += res_t[2] + '; '
                
    print objname, d 
    return d 


def get_observations():
    import MySQLdb, sys, os, re, time, utilities, pyfits
    from copy import copy
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
    c = db2.cursor()
    db_keys = describe_db(c)

    command = "CREATE TABLE IF NOT EXISTS telarchive_db ( id MEDIUMINT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id))" 
    print command
    #c.execute("DROP TABLE IF EXISTS telarchive_db")
    c.execute(command)
    
    keystop = ['PPRUN','ROTATION','OBJNAME']
    list = reduce(lambda x,y: x + ',' + y, keystop)
    command="SELECT * from illumination_db LEFT OUTER JOIN telarchive_db on telarchive_db.OBJNAME=illumination_db.OBJNAME where illumination_db.OBJNAME is not null and illumination_db.OBJNAME!='HDFN' and illumination_db.OBJNAME!='COSMOS' and telarchive_db.HST_data is NULL GROUP BY illumination_db.OBJNAME" 
    print command
    c.execute(command)
    results=c.fetchall()
    for line in results: 
        dtop = {}
        for i in range(len(db_keys)):
            dtop[db_keys[i]] = str(line[i])
        print dtop['CRVAL1'],dtop['CRVAL2'],dtop['OBJNAME']
        dict = run_telarchive(float(dtop['CRVAL1']),dtop['CRVAL2'],dtop['OBJNAME'])
        OBJNAME = dtop['OBJNAME']
        dict['OBJNAME'] = OBJNAME

        floatvars = {}          
        stringvars = {}
        #copy array but exclude lists                                                   
        import string
        letters = string.ascii_lowercase + string.ascii_uppercase.replace('E','') + '_' + '-'
        for ele in dict.keys():
            print ele, dict[ele]
            type = 'float'
            for l in letters:
                if string.find(str(dict[ele]),l) != -1 or dict[ele] == ' ': 
                    type = 'string'
            if type == 'float':  
                floatvars[ele] = str(float(dict[ele])) 
            elif type == 'string':
                stringvars[ele] = dict[ele] 
                                                                                                                                                                                                               
        # make database if it doesn't exist
        print 'floatvars', floatvars
        print 'stringvars', stringvars
                                                                                                                                                                                                              
        for column in stringvars: 
            try:
                command = 'ALTER TABLE telarchive_db ADD ' + column + ' varchar(240)'
                c.execute(command)  
            except: nope = 1 
        for column in floatvars: 
            try:
                command = 'ALTER TABLE telarchive_db ADD ' + column + ' float(30)'
                c.execute(command)  
            except: nope = 1 

        c.execute("SELECT OBJNAME from telarchive_db where OBJNAME = '" + OBJNAME + "'")
        results = c.fetchall() 
        print results
        if len(results) > 0:
            print 'already added'
        else:
            command = "INSERT INTO telarchive_db (OBJNAME) VALUES ('" + OBJNAME + "')"
            print command
            c.execute(command) 
                                                                                                                                         
        import commands
        vals = ''
        for key in stringvars.keys():
            print key, stringvars[key]
            vals += ' ' + key + "='" + str(stringvars[key]) + "',"
                                                                                                                                         
        for key in floatvars.keys():
            print key, floatvars[key]
            vals += ' ' + key + "='" + floatvars[key] + "',"
        vals = vals[:-1]
                                                                                                                                         
        command = "UPDATE telarchive_db set " + vals + " WHERE OBJNAME='" + OBJNAME + "'" 
        print command
        c.execute(command)

def calcDataIllum(file, LENGTH1, LENGTH2, data,magErr, X, Y, pth='/nfs/slac/g/ki/ki04/pkelly/plots/', rot=0, good=None):
    
    import numpy, math, pyfits, os                                                                              
    from ppgplot   import *

    #print size_x, size_y, bin, size_x/bin

    x = []
    y = []
    z = []
    zerr = []

    from copy import copy
    X_sort = copy(X)
    Y_sort = copy(Y)
    X_sort = numpy.sort(X_sort)
    Y_sort = numpy.sort(Y_sort)

    X_min = X_sort[0]
    Y_min = Y_sort[0]

    X_max = X_sort[-1]
    Y_max = Y_sort[-1]

    X_width = abs(X_max - X_min)
    Y_width = abs(Y_max - Y_min)

    nbin1 =15 
    nbin2 =15 

    LENGTH1 = LENGTH1
    LENGTH2 = LENGTH2

    print LENGTH1, LENGTH2

    bin1 = int(LENGTH1/nbin1)
    bin2 = int(LENGTH2/nbin2)
    
    diff_weightsum = -9999*numpy.ones([nbin1,nbin2])
    diff_invvar = -9999*numpy.ones([nbin1,nbin2])
    diff_X = -9999*numpy.ones([nbin1,nbin2])
    diff_Y = -9999*numpy.ones([nbin1,nbin2])

    X_cen = []
    Y_cen = []
    data_cen = []
    zerr_cen = []


    chisq = 0
    for i in range(len(data)):
        if good is not None:
            use = good[0][i] == good[1]    
        else: 
            use = True
        if use:
            if 1: # LENGTH1*0.3 < X[i] < LENGTH1*0.6:                                                                                             
                X_cen.append(X[i])
                Y_cen.append(Y[i])
                data_cen.append(data[i])
                zerr_cen.append(magErr[i])
                                                                                                                                                  
            x.append(X[i])
            y.append(Y[i])
            z.append(data[i])
            zerr.append(magErr[i])
            chisq += data[i]**2./magErr[i]**2.
                                                                                                                                                  
            x_val = int((X[i])/float(bin1))  # + size_x/(2*bin)
            y_val = int((Y[i])/float(bin2))  #+ size_y/(2*bin)
            #print LENGTH1, LENGTH2, x_val, y_val, X[i], Y[i]
            #print size_x/bin+1,size_y/bin+1, x_val, y_val, X[i], Y[i]
            err = magErr[i]
            ''' lower limit on error '''
            if err < 0.04: err = 0.04
            weightsum = data[i]/err**2.
            weightX = X[i]/err**2.
            weightY = Y[i]/err**2.
            invvar = 1/err**2.
            
                                                                                                                                                  
            #if 1: #0 <= x_val and x_val < int(nbin1) and y_val >= 0 and y_val < int(nbin2):  #0 < x_val < size_x/bin and 0 < y_val < size_y/bin:
            #print x_val, y_val
            try:
                if diff_weightsum[x_val][y_val] == -9999:      
                    diff_weightsum[x_val][y_val] = weightsum
                    diff_invvar[x_val][y_val] = invvar 
                    diff_X[x_val][y_val] = weightX 
                    diff_Y[x_val][y_val] = weightY
                                                                                                                                                  
                    #print x_val, y_val, weightsum, '!!!!!'
                else:                 
                    diff_weightsum[x_val][y_val] += weightsum 
                    diff_invvar[x_val][y_val] += invvar 
                    diff_X[x_val][y_val] += weightX
                    diff_Y[x_val][y_val] += weightY
            except: fail = 'fail'

    redchisq = chisq**0.5 / len(data)
    print 'redchisq', redchisq

    import Numeric
    x_p = Numeric.array(X_cen)
    y_p = Numeric.array(Y_cen)
    z_p = Numeric.array(data_cen)
    zerr_p = Numeric.array(zerr_cen)
    x.sort()
    y.sort()
    z.sort()

    mean = diff_weightsum/diff_invvar
    print 'mean'
    #print mean
    err = 1/diff_invvar**0.5

    print 'err'
    #print err 

    print 'writing'
    hdu = pyfits.PrimaryHDU(mean)
    f = pth + file 
    os.system('rm ' + f +   'diffmap.fits')
    hdu.writeto( f + 'diffmap.fits')      

    hdu = pyfits.PrimaryHDU(err)
    os.system('rm ' + f + 'diffinvar.fits')
    hdu.writeto( f + 'diffinvar.fits')      


    ''' now make cuts with binned data '''

    mean_flat = Numeric.array(mean.flatten(1))
    print mean_flat
    err_flat = Numeric.array(err.flatten(1))
    print err_flat
    mean_X = Numeric.array((diff_X/diff_invvar).flatten(1))
    print mean_X
    mean_Y = Numeric.array((diff_Y/diff_invvar).flatten(1))
    print mean_Y

    file = f + 'diffp.ps'                                      
                                                            
    t = tempfile.NamedTemporaryFile(dir='/tmp/').name
    ### plot residuals
    pgbeg(t+"/cps",1,2)
    pgiden()
                                                            
    #print x_p
    #print z_p 
    #print zerr_p
                                                            
    #pgswin(x[0],x[-1],z[0],z[-1])
                                                            
    pgpanl(1,1)
    pgswin(x[0],x[-1],-0.4,0.4)
    pgbox()
    pglab('X axis','SDSS-SUBARU',file)     # label the plot
    #pgsci(3)
    #pgerrb(6,x_p,z_p,zerr_p)
    pgerrb(6,mean_X,mean_flat,err_flat)
    pgpt(mean_X,mean_flat,3)
                                                            
    #pgswin(y[0],y[-1],z[0],z[-1])
    pgpanl(1,2)
    pgswin(y[0],y[-1],-0.4,0.4)
                                                            
    pgsci(1)
    pgbox()
    pglab('Y axis','SDSS-SUBARU',file)     # label the plot
    #pgsci(3)
    pgerrb(6,mean_Y,mean_flat,err_flat)
    pgpt(mean_Y,mean_flat,3)
    pgsci(1)
                                                            
    pgend()
                                                            
    os.system('mv ' + t + ' ' + file)


    file = f + 'pos.ps'

    t = tempfile.NamedTemporaryFile(dir='/tmp/').name
    print file
    os.system('rm ' + file)
    pgbeg(t + '/cps',1,1)
    pgiden()

    #print x_p
    #print z_p 
    #print zerr_p

    #pgswin(x[0],x[-1],z[0],z[-1])

    ### plot positions
    pgpanl(1,1)
    pgswin(x[0],x[-1],y[0],y[-1])
    pgbox()
    pglab('X','Y',file)     # label the plot
    #pgsci(3)
    #pgerrb(6,x_p,z_p,zerr_p)
    pgpt(x_p,y_p,3)

    pgend()

    os.system('mv ' + t + ' ' + file)

    print f + 'pos.ps'+"/cps"

    file = f + 'diff.ps'

    t = tempfile.NamedTemporaryFile(dir='/tmp/').name
    ### plot residuals
    pgbeg(t+"/cps",1,2)
    pgiden()

    #print x_p
    #print z_p 
    #print zerr_p

    #pgswin(x[0],x[-1],z[0],z[-1])

    pgpanl(1,1)
    pgswin(x[0],x[-1],-0.4,0.4)
    pgbox()
    pglab('X axis','SDSS-SUBARU',file)     # label the plot
    #pgsci(3)
    #pgerrb(6,x_p,z_p,zerr_p)
    pgpt(x_p,z_p,3)

    #pgswin(y[0],y[-1],z[0],z[-1])
    pgpanl(1,2)
    pgswin(y[0],y[-1],-0.4,0.4)

    pgsci(1)
    pgbox()
    pglab('Y axis','SDSS-SUBARU',file)     # label the plot
    #pgsci(3)
    #pgerrb(6,y_p,z_p,zerr_p)
    pgpt(y_p,z_p,3)
    pgsci(1)
  


    #print x_p
    #print z_p 
    #print zerr_p

    pgend()

    os.system('mv ' + t + ' ' + file)
    return

if __name__ == '__main__': 
    import sys, os 
    tmpdir_root = sys.argv[1]   + '/' 
    os.chdir(tmpdir_root)
    tmpdir = tmpdir_root + '/tmp/'
    os.system('mkdir -p ' + tmpdir)
    astrom = 'solve-field'
    if len(sys.argv)>2:
        astrom = sys.argv[2]
    #select_analyze()
    match_OBJNAME()
else:
    if not 'loaded' in locals():
        import tempfile              
        tmpdir = tempfile.NamedTemporaryFile(dir='/usr/work/pkelly/').name
        os.system('mkdir ' + tmpdir)
        loaded = 'yes'
        print 'loaded' in locals()
