
def SIS(theta,zs,zl,s=0.2,sigma_v=1000.,w=-1.):

    c = 300000. # km s^-1

    import advanced_calc, math

    radius = 2*math.pi/(360.*60.*60)*theta
    
    einstein_radius = 4 * math.pi * (sigma_v/c)**2. * ( advanced_calc.compute(zs,w) - advanced_calc.compute(zl,w)) / advanced_calc.compute(zs,w) 

    kappa = einstein_radius / (2.*radius)

    decrement = (5.*s - 2)*kappa

    return kappa, decrement 


def plot_it():
    import scipy, pylab
  
    pylab.clf() 
    decre = [] 
    rad = []
    for theta in scipy.arange(10,300,5):
        print theta
        rad.append(theta/60.)
        print SIS(theta,1.0,0.45,s=0.1)
        decre.append(SIS(theta,1.0,0.45,s=0.1)[1])

    pylab.axhline(0,c='black')
    pylab.plot(rad,decre)
    pylab.xlabel('Radius (Arcmin)',size='x-large')
    pylab.ylabel(r'$\delta$N/N',size='x-large')
    pylab.ylim([-1,0.2])
    pylab.savefig('expectation.png')











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


def plot_cmd(data_all,red_dict,file_name,cluster_redshift,title=''):
    import pylab, scipy
    from copy import copy
    pylab.clf()
    data_cmd = copy(data_all)
    mask = (data_cmd.field(red_dict['m']) > -90) * (data_cmd.field(red_dict['c1']) > -90) * (data_cmd.field(red_dict['c2']) > -90)
    data_cmd = data_cmd[mask]
    mask = ((data_cmd.field('Xpos') - 5000.*scipy.ones(len(data_cmd)))**2. +  (data_cmd.field('Ypos') - 5000.*scipy.ones(len(data_cmd)))**2.)**0.5  * 0.2 < float(180)
    data_cmd = data_cmd[mask]
    x = data_cmd.field(red_dict['m'])
    y = data_cmd.field(red_dict['c1']) - data_cmd.field(red_dict['c2'])
    x2 = scipy.arange(x.min(),x.max(),1)
    yfit = x2*red_dict['slope']
    pylab.plot(sorted(x2),yfit+scipy.ones(len(yfit))*red_dict['intercept'],'b-')
    pylab.plot(sorted(x2),yfit+scipy.ones(len(yfit))*red_dict['upper_intercept'],'b-')
    pylab.plot(sorted(x2),yfit+scipy.ones(len(yfit))*red_dict['lower_intercept'],'b-')
    pylab.scatter(x,y,color='red',s=0.1, label='All Galaxies')
    photoz = data_cmd[(data_cmd.field('BPZ_Z_B') > cluster_redshift - 0.05) * (data_cmd.field('BPZ_Z_B') < cluster_redshift + 0.05)]
    if len(photoz) > 0:        
        x_photoz = photoz.field(red_dict['m'])                                           
        y_photoz = photoz.field(red_dict['c1']) - photoz.field(red_dict['c2'])
        pylab.scatter(x_photoz,y_photoz,s=0.5, color='black', label='+- 0.05 Cluster z')
    pylab.axvline(x=red_dict['lm'],ymin=-10,ymax=10)
    pylab.xlim([sorted(x)[5],sorted(x)[-5]])
    pylab.ylim([sorted(y)[5],sorted(y)[-5]])
    pylab.xlabel(red_dict['m'].split('-')[-1])
    pylab.ylabel(red_dict['c1'].split('-')[-1] + ' - ' + red_dict['c2'].split('-')[-1]) 
    pylab.title(title)
    pylab.legend()
    pylab.savefig(file_name)



def plot_cc(data_all,red_dict,file_name,cluster_redshift,title=''):
    import pylab, scipy
    from copy import copy
    pylab.clf()
    data_cmd = copy(data_all)
    pylab.scatter(data_cmd.field(prefix('W-C-RC'))-data_cmd.field(prefix('W-S-Z+')),data_cmd.field(prefix('W-J-V'))-data_cmd.field(prefix('W-C-RC')),color='red',s=0.1, label='All Galaxies')
    pylab.ylabel('V-R',size='x-large')
    pylab.xlabel('R-Z',size='x-large')
    pylab.xlim([-0.3,1.5])
    pylab.ylim([-0.3,1.5])
    pylab.title(title)
    pylab.legend()
    pylab.savefig(file_name)












#convert_probs_to_fits(probs)

#probs =  '%(path)s/PHOTOMETRY%(DETECT_FILTER)s%(AP_TYPE)s/%(cluster)s.%(magtype)s.1.%(SPECTRA)s.%(type)s.probs' % params

def convert_probs_to_fits(file):
    import scipy, pyfits
    p = open(file).readlines()[0]
    
    print 'reading in ' + file
    f = scipy.loadtxt(file)
    print 'done reading in' + file
    
    code = p[:-1].replace(')','').split('(')[-1].split(',')
    zs = scipy.arange(float(code[0]), float(code[1]), float(code[2]))
    cols = [pyfits.Column(name='SeqNr', format='J', array=f[:,0])]
    for i in range(len(zs)):
        cols.append(pyfits.Column(name='%.2f' % (zs[i]), format='D', array=f[:,i+1]))
    
    coldefs = pyfits.ColDefs(cols)
    tbhdu = pyfits.new_table(coldefs)
    
    print 'writing out fits file '
    import os
    os.system('rm ' + file + '.tab')
    tbhdu.writeto(file + '.tab')



def ds9(image,jpg,extra='',save=False):
    import pyraf, os
    from pyraf import iraf
    os.system('rm /tmp/image.fits')
    iraf.imcopy(image+'[4000:6000,4000:6000]','/tmp/image.fits')

    com = ['file /tmp/image.fits', 'zoom to fit', 'view colorbar no', 'minmax', extra, 'scale histequ' , ] # -quit >& /dev/null &")        
    for c in com:
        z = 'xpaset -p ds9 ' + c
        print z
        os.system(z)

    for rad in range(10):
        command = 'echo "circle 5000 5000 ' + str(rad*60*5) + '" | xpaset ds9 regions ' 
        print command
        os.system(command)


    if save:
        command = 'xpaset -p ds9 saveimage jpeg ' + jpg  
        os.system(command)







def prefix(filt):
    if filt is 'g' or filt is 'r' or filt is 'u':
        return 'MAG_APER1-MEGAPRIME-COADD-1-' + filt
    else:
        return 'MAG_APER1-SUBARU-COADD-1-' + filt


def anja_redsequence(cluster, detectband):

    dir = '/nfs/slac/g/ki/ki05/anja/SUBARU/ki06/lensing_2010/' + cluster + '/LENSING_' + detectband + '_' + detectband + '_aper/good/'
    print dir
    
    dict = {} 
    redseqfit = open(dir + 'redseqfit','r').readlines()
    slope = float(redseqfit[1].split('=')[1].split('*')[0])
    intercept = float(redseqfit[1][:-1].split('+')[1])
                                                                                                                                             
    upper_intercept = float(redseqfit[3][:-1].split('+')[1])
    lower_intercept = float(redseqfit[4][:-1].split('+')[1])

    expand_upper_intercept = intercept + (upper_intercept - intercept)*1.5

    expand_lower_intercept = intercept - (intercept - lower_intercept)*1.5

                                                                                                                                             
    dict['slope'] = slope
    dict['intercept'] = intercept
    dict['lower_intercept'] = expand_lower_intercept
    dict['upper_intercept'] = expand_upper_intercept
                                                                                                                                             
    polycoeffs = [slope, intercept]
    std = (upper_intercept - intercept) / 1.2
     
    info = open(dir + 'redseq.params','r').readlines()
    print info, dir + 'redseq.params'
    for l in info:
        if len(l.split(':')) > 1:
            key, value = l[:-1].split(': ')
            dict[key] = value
                                                                                                                                             
    print dict
                                                         
    dict['m'] = prefix(dict['xmag'])
    dict['c1'] = prefix(dict['bluemag'])
    dict['c2'] = prefix(dict['redmag'])
    dict['lm'] = dict['magcut']
    print 'finished'        

    return dict


def plot_regions(p,website,file='regstart.reg',save=False):
    import os
    reg = open(website + file + '.reg','w')
    reg.write('global color=red dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\nphysical\n')
    for x,y in zip(p.field('Xpos'),p.field('Ypos')):
        reg.write('circle(' + str(x) + ',' + str(y) + ',4)#' + '\n')
    reg.close()

    command = 'xpaset -p ds9 regions file ' + website + file + '.reg'
    print command
    os.system(command)

    if save:
        command = 'xpaset -p ds9 saveimage jpeg ' + website + file + '.jpg' 
        os.system(command)


                                                                                                                                             


def select_stars(input_cat,cluster,detect_band,website):    
    ''' REMEMBER SATURATE !@#$!@#%@%^#%&!@#$%!@#$!@#$!#$^$%^ MAXVAL '''
    import pylab, pyfits, scipy    

    porig = pyfits.open(input_cat)
    p = porig[1].data        
    
    reg = open('regstart.reg','w')
    reg.write('global color=blue dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\nphysical\n')
    for x,y in zip(p.field('Xpos'),p.field('Ypos')):
        reg.write('circle(' + str(x) + ',' + str(y) + ',18)#' + '\n')
    reg.close()
                                   
    from copy import copy
    ''' if seeing is really bad (unfocused) use FLUX_RADIUS ''' 

    masks = [] 
    ok = 0                                             
    seeings = p.field('FLUX_RADIUS')[0]
    radius_var = 'FLUX_RADIUS'
    ap_type = prefix(detect_band) #'APER1-SUBARU-10_2-1-W-J-V'

    ''' need to isolate the star column '''
    
    mask = (p.field('Flag') == 0) * (p.field(ap_type) > -90)
    array = p[mask]
        
    #mask = array.field('IMAFLAGS_ISO' ) == 0
    save_array = copy(array)

    if 0:
        pylab.clf()
        pylab.scatter(p.field(radius_var  ),p.field( ap_type  ),c='red')      
                                                                                                                                 
        pylab.xlim([0,10])
        pylab.ylim([-20,0])
        pylab.xlabel(radius_var  )
        pylab.ylabel(ap_type  )
        pylab.savefig('/Volumes/mosquitocoast/patrick/kpno/' + run + '/work_night/' + snpath + '/starcolumn'+star_select+'.pdf')


    from copy import copy

    array = copy(save_array)                                                                                    
    pylab.clf()
    a,b,varp = pylab.hist(array.field(radius_var  ),bins=scipy.arange(1.0,8,0.1))    

    #pylab.savefig('/Users/pkelly/Dropbox/star'  + 'hist.pdf')
    z = zip(a,b)
    z.sort()
    max_meas = z[-1][1]





    def get_width_upper(max, width, upper, array_in):
       
        from copy import copy 
        array = copy(array_in)
        ''' now pick objects somewhat larger than star column '''
        mask = array.field(radius_var  ) > max+width 
        array = array[mask]
        rads = array.field(radius_var  )#[mask]
        mask = rads < max+width + 0.6 
        array = array[mask]
        mags = array.field(ap_type  )
        mags.sort()
        ''' take 20% percentile and subtract 0.5 mag '''
        if len(mags) == 0:
            upper = 99
        else:
            upper = mags[int(len(mags)*0.2)] #+ 0.5
                                                                                                                    
        array = copy(array_in)
        maskA = array.field(ap_type  ) < upper #+ 0.5 
        maskB  = array.field(radius_var  ) < max + width 
        maskC = array.field(radius_var  ) > max - width 
        mask = scipy.logical_and(maskA,maskB,maskC)
        array = array[mask]
        rads = array.field(radius_var  )
                                                                        
        pylab.clf()                                            
        a,b,varp = pylab.hist(array.field(radius_var  ),bins=scipy.arange(1.0,8,0.04))    
        z = zip(a,b)
        z.sort()
        max = z[-1][1]
        width = 1.0*scipy.std(rads) 
        print 'width', width, 'max', max, 'upper', upper, 'rads', rads
        return max, width, upper

    max, width, upper = get_width_upper(max_meas, 0.3, 100, copy(save_array))            
   # print max, max_meas, width, upper
    max, width, upper = get_width_upper(max, width, upper, copy(save_array))            
                                                                                                               
    pylab.clf()
    pylab.scatter(save_array.field(radius_var  ),save_array.field(ap_type  ), s=0.01)
    pylab.axvline(x=max - width,c='red')
    pylab.axvline(x=max + width,c='red')
    pylab.axhline(y=upper,c='red')

    if False:
        mask = save_array.field('CLASS_STAR_reg_' ) > 0.9                                                         
        print save_array.field('CLASS_STAR_reg_' )
        pm = save_array[mask]
        pylab.scatter(pm.field(radius_var  ),pm.field( ap_type  ),c='red')

    pylab.xlim([0,10])
    #pylab.ylim([-20,0])
    pylab.xlabel(radius_var  )
    pylab.ylabel( ap_type  )
    pylab.savefig(website + 'stars.png')
    #pylab.show()
    
    

    #reg = open('regall.reg','w')
    #reg.write('global color=yellow dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\nphysical\n')
    #for x,y in zip(p.field('X_IMAGE_reg_g'),p.field('Y_IMAGE_reg_g')):
    #    reg.write('circle(' + str(x) + ',' + str(y) + ',19)#' + '\n')
    #reg.close()
    
    return max, width

def make_segmentation_image(photdir, cluster):

    import pyfits

    p = pyfits.open(photdir + cluster + '.slr.cat')

    call = p[3].data.field('EXTRACTION_CALL')[0]

    config = p[3].data.field('EXTRACTION_CONFIG')[0]

    pattern = '${DATACONF}'
    DATACONF = '/afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/conf/reduction/'

    config = config.replace(pattern,DATACONF)


    f = open('config_temp','w')
    f.write(config)
    f.close()

    print call


    import re
    res = re.split('\s+',call)

    main = res[4:]    
    sex = res[0]
    image = res[3]
    if len(image.split(',')) > 1:
        image = image.split(',')[0]

    list = []
    for i in range(len(main)):
        if i%2==0:
            list.append([main[i],main[i+1]])
    print list

    command = sex + ' ' + image + ' -c config_temp ' 

    for l in list:
        if len(l[1].split(',')) > 1:
            command += l[0] + ' ' + l[1].split(',')[0] + ' '
        elif l[0] == '-CHECKIMAGE_TYPE':
            command += '-CHECKIMAGE_TYPE SEGMENTATION -CHECKIMAGE_NAME ' + photdir + 'segmentation.fits '
        elif l[0] == '-CATALOG_NAME':
            command += '-CATALOG_NAME ' + photdir + 'seg_catalog.tab '
        else:
            command += l[0] + ' ' + l[1] + ' '

    
    print command
    os.system(command)


def run():    
    import pyfits, os, redsequence, math, pylab, commands
    import os, re, sys, string, scipy, MySQLdb
    from copy import copy                                                                                                                               
    
    subarudir = os.environ['subdir']
    cluster = sys.argv[1] #'MACS1423+24'
    spec = False 
    train_first = False 
    magtype = 'APER1'
    AP_TYPE = ''
    type = 'all' 
    SPECTRA='CWWSB_capak.list'
    FILTER_WITH_LIST=None
    if len(sys.argv) > 2:
        for s in sys.argv:
            if s == 'spec':
                type = 'spec'            
                spec = True
            if s == 'rand':
                type = 'rand'
            if s == 'train':
                train_first = True
            if s == 'ISO':
                magtype = 'ISO'
            if s == 'APER1':
                magtype = 'APER1'
    
            if s == 'APER':
                magtype = 'APER'
    
            if string.find(s,'flist') != -1:
                import re
                rs = re.split('=',s)
                FILTER_WITH_LIST=rs[1]
    
            if string.find(s,'detect') != -1:
                import re
                rs = re.split('=',s)
                DETECT_FILTER=rs[1]
            if string.find(s,'spectra') != -1:
                import re
                rs = re.split('=',s)
                SPECTRA=rs[1]
            if string.find(s,'aptype') != -1:
                import re
                rs = re.split('=',s)
                AP_TYPE = '_' + rs[1]



    SEGMENTATION_IMAGE = False

    JPG_IMAGE = False

    STAR_COLUMN, ANJA_SEQUENCE, CLUSTER_REDSHIFT = False, True, True

    PLOT_CMD = True 

    PLOT_CUTS = True 

    REMAKE_CLUSTER_MASK = False 



    BPZ_CUT = 0.3
    print 'opening photometry'
    photdir = '/nfs/slac/g/ki/ki05/anja/SUBARU/ki06/photometry_2010/' +  cluster + '/PHOTOMETRY_' + DETECT_FILTER + AP_TYPE + '/'

    
    if CLUSTER_REDSHIFT: 
        command = 'grep ' + cluster + ' ' + '/nfs/slac/g/ki/ki05/anja/SUBARU/'  + '/clusters.redshifts ' 
        print command
        cluster_info = commands.getoutput(command)
        cluster_redshift = float(re.split('\s+',cluster_info)[1])
        print cluster_redshift



    probs =  photdir + '/' + cluster + '.APER1.1.CWWSB_capak.list.all.probs'
    print 'converting probabilities'
    #convert_probs_to_fits(probs)

    probs_tab = pyfits.open(probs + '.tab')

    ''' make mask '''

    minus = float('%.2f' % (cluster_redshift - 0.05))
    plus = minus + 0.1

    list = [str(x) for x in scipy.arange(minus,plus,0.01)]

    phot_clus_probs = reduce(lambda x,y: x + y, [probs_tab[1].data.field(c) for c in list])

    phot_clus_mask = phot_clus_probs < 0.01

    print phot_clus_probs, phot_clus_mask


    
    




    print probs, 'finished'

    website = os.environ['sne'] + '/magnification/' + cluster + '/' 
    os.system('mkdir -p ' + website)

    imdir = subarudir + cluster + '/' + DETECT_FILTER + '/SCIENCE/coadd_' + cluster + '_all/'

    if SEGMENTATION_IMAGE:
        make_segmentation_image(photdir,cluster)

    if JPG_IMAGE:
        ds9(imdir+'coadd.fits',website+'cluster.jpg',save=False)
        #ds9(photdir+'segmentation.fits',website+'cluster_seg.jpg',save=True)
        #ds9(photdir+'cluster_mask.fits',website+'cluster_mask.jpg',extra='xpaset -p ds9 scale limits 0 1',save=True)

    ''' start making webpage '''
    mag_page = open(website + 'index.html','w',0)
    mag_page.write('<html><h1>' + cluster + ' Magnification</h1>\n<br><img src=cluster.jpg onmouseout="this.src=\'cluster.jpg\';" onmouseover="this.src=\'cluster_seg.jpg\';"></img>\n')
    mag_page.write('<img src=cluster.jpg onmouseout="this.src=\'cluster.jpg\';" onmouseover="this.src=\'cluster_mask.jpg\';"></img><br>\n')
    mag_page.write('<img src=stars.png></img><br>\n')
    mag_page.write('Color-Magnitude Diagram<br><img src=cmd.png></img><br>\n')


    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-sr01')
    c = db2.cursor()

    if STAR_COLUMN:
        print '''finding star column'''
        width_star, max_star = select_stars(photdir + cluster + '.slr.cat',cluster,DETECT_FILTER,website)

        commandst = 'update clusters_db set widthstar=' + str(width_star) + ' where objname="' + cluster + '"'
        c.execute(commandst)                                             
        commandst = 'update clusters_db set maxstar=' + str(max_star) + ' where objname="' + cluster + '"'
        c.execute(commandst)                                             
    else:
        db_keys = describe_db(c,['clusters_db'])
        c.execute('select * from clusters_db where objname="' + cluster + '"')
        results = c.fetchall()
        line = results[0]
        dict = {}
        for i in range(len(db_keys)):
            dict[db_keys[i]] = str(line[i])
        width_star, max_star = float(dict['widthstar']), float(dict['maxstar'])
        print width_star, max_star

        
    if ANJA_SEQUENCE:    
        print '''reading Anja's red sequence '''           
        red_dict = anja_redsequence(cluster,DETECT_FILTER)
        from_stratch = False
    
    print ''' MERGING PHOTOZ AND PHOTOMETRY CATALOGS ''' 
    photoz = pyfits.open(photdir + cluster + '.APER1.1.CWWSB_capak.list.all.bpz.tab')
    photometry = pyfits.open(photdir + cluster + '.slr.cat')
    
    cols = []
    for col in photoz[1].columns:
        cols.append(col)
    for col in photometry[1].columns:
        cols.append(col)
    hdu = pyfits.PrimaryHDU()
    temp1 = pyfits.new_table(cols)
    hdulist = pyfits.HDUList([hdu])        
    hdulist.append(temp1)
    #hdulist.writeto('savetab.fits')
    
    data_all = hdulist[1].data

    print ''' APPLYING STAR CUT '''

    ''' @#$@#$^@$%&#$%& ALTERNATE CUT !!!!! '''
    data_all = data_all[data_all.field('FLUX_RADIUS') > max_star - width_star]
    phot_clus_mask = phot_clus_mask[data_all.field('FLUX_RADIUS') > max_star - width_star]

    if PLOT_CMD:
        print ''' MAKING CMD PLOT '''
        plot_cmd(data_all,red_dict,website+'cmd.png',cluster_redshift,title='ALL GALAXIES')    

    plot_cc(data_all,red_dict,website+'cmd.png',cluster_redshift,title='ALL GALAXIES')    

    if PLOT_CUTS:

        print ''' MAKING CUTS PLOT '''

        plot_var, bins, name = prefix(DETECT_FILTER), scipy.arange(21,28,0.2), 'lumfnc.png'
        pylab.clf()
        data_save = copy(data_all)
        #data_save = data_save[data_save.field('BPZ_ODDS') > BPZ_CUT]
        #data_save = data_save[(data_save.field('BPZ_Z_B') > cluster_redshift + 0.1)*(data_save.field('BPZ_Z_B') < 3)]

        data_save = data_save[phot_clus_mask]

        latepdf, latebins, patches = pylab.hist(data_save.field(plot_var)[data_save.field('BPZ_T_B')>=3],bins=bins,histtype='step',label='LATE T >= 3')
        earlypdf, earlybins, patches = pylab.hist(data_save.field(plot_var)[data_save.field('BPZ_T_B')<3],bins=bins,histtype='step',label='EARLY T < 3')
        [xmin, xmax, ymin, ymax] = pylab.axis()
        pylab.ylim([ymin,ymax*2.0])
        pylab.legend()
        pylab.xlabel(plot_var)
        pylab.ylabel('Galaxies')
        pylab.savefig(website + '/' + name)
                                                                                                                                                        
        mag_page.write('<br>Luminosity Functions<br><img src=' + name + '></img>\n')

        pylab.clf()
        earlysum = 1 
        earlylogpdf = []
        for v in earlypdf:
            earlysum += v
            earlylogpdf.append(math.log10(earlysum))

        earlylogpdf = scipy.array(earlylogpdf)

        latesum = 1 
        latelogpdf = []
        for v in latepdf:
            latesum += v
            latelogpdf.append(math.log10(latesum))

        latelogpdf = scipy.array(latelogpdf)

        print latepdf, bins, patches, latesum, latelogpdf
        print earlypdf, bins, patches, earlysum, earlylogpdf

        plot_bins = scipy.array(bins[:-1])

        earlymask = (plot_bins>22.5)*(plot_bins<25)
        earlycoeffs = scipy.polyfit(plot_bins[earlymask],earlylogpdf[earlymask],1)

        latemask = (plot_bins>22)*(plot_bins<25)
        latecoeffs = scipy.polyfit(plot_bins[latemask],latelogpdf[latemask],1)
    
        earlyline = scipy.polyval(earlycoeffs,plot_bins[earlymask])
        lateline = scipy.polyval(latecoeffs,plot_bins[latemask])

        pylab.plot(plot_bins[earlymask],earlyline,color='k')
        pylab.plot(plot_bins[latemask],lateline,color='k')

        x = plot_bins[earlymask][0]
        y = scipy.polyval(earlycoeffs,[x])[0] +0.1
        print x, y
        pylab.figtext(0.15,0.8,'s= %.2f' % earlycoeffs[0],color='r', size='x-large', ha='left') 

        x = plot_bins[latemask][0]
        y = scipy.polyval(latecoeffs,[x])[0] -0.1
        print x, y
        pylab.figtext(0.15,0.75,'s= %.2f' % latecoeffs[0],color='b', size='x-large', ha='left') 

                                           
        pylab.bar(bins[:-1],earlylogpdf, facecolor='none', edgecolor='r', linewidth=2, width=(bins[1]-bins[0]),label='EARLY T < 3')
        pylab.bar(bins[:-1],latelogpdf, facecolor='none', edgecolor='b', linewidth=2, width=(bins[1]-bins[0]),label='LATE T >= 3')
        pylab.xlabel('Apparent Magnitude')
        pylab.ylabel('log_10(N(>m))')
        pylab.legend(loc=4)

        pylab.savefig(website + '/loglum.png')

        mag_page.write('<br>LogN<br><img src=loglum.png></img>\n')


        for plot_var, bins, name in []: #['BPZ_Z_B',scipy.arange(0,1.2,0.05),'redshifts.png'],[prefix(DETECT_FILTER),scipy.arange(19,28,0.2),'mags.png']]:
                                                                                                                                                            
            pylab.clf()
            data_save = copy(data_all)
            pylab.hist(data_save.field(plot_var),bins=bins,histtype='step',label='ALL')                                       
            #data_save = data_save[data_save.field('BPZ_ODDS') > BPZ_CUT]
            data_save = data_save[phot_clus_mask]
            #pylab.hist(data_save.field(plot_var),bins=bins,histtype='step',label='ODDS > 0.3')
            pylab.hist(data_save.field(plot_var),bins=bins,histtype='step',label='NO CLUSTER GALAXIES')
            data_save = data_save[(data_save.field('BPZ_Z_B') > cluster_redshift + 0.1)] #*(data_save.field('BPZ_Z_B') < 1.2)]
            pylab.hist(data_save.field(plot_var),bins=bins,histtype='step',label='Z > Z_CLUSTER + 0.1')
            pylab.hist(data_save.field(plot_var)[data_save.field('BPZ_T_B')<3],bins=bins,histtype='step',label='EARLY T < 3')
            pylab.hist(data_save.field(plot_var)[data_save.field('BPZ_T_B')>=3],bins=bins,histtype='step',label='LATE T >= 3')
            [xmin, xmax, ymin, ymax] = pylab.axis()
            pylab.ylim([ymin,ymax*2.0])
            pylab.legend()
            pylab.xlabel(plot_var)
            pylab.ylabel('Galaxies')
            pylab.savefig(website + '/' + name)
                                                                                                                                                            
            mag_page.write('<br><img src=' + name + '></img>\n')

    xcen, ycen = 5000, 5000

    if REMAKE_CLUSTER_MASK:
        print '''opening image + segmentation image'''
        image = pyfits.open(imdir + 'coadd.fits')
        os.system('ln -s ' + imdir + 'coadd.fits ' + photdir + 'coadd_link.fits')
        segmentation = pyfits.open(photdir + 'segmentation.fits')[0].data

        weight = pyfits.open(imdir + 'coadd.weight.fits')[0].data

        photoz_mask = (data_all.field('BPZ_Z_B') > 0.3)*(data_all.field('BPZ_Z_B') < 1.2)*(data_all.field('BPZ_Z_B') < cluster_redshift + 0.1)*(data_all.field('BPZ_Z_B') > cluster_redshift - 0.1)

        diff = (data_all.field(red_dict['c1']) - data_all.field(red_dict['c2'])) - data_all.field(red_dict['m'])*red_dict['slope'] 
        ''' mask for redsequence '''
        redseq_mask = (diff > red_dict['lower_intercept']) * (diff < red_dict['upper_intercept']) # * (data_all.field(red_dict['m']) < float(red_dict['magcut']) )
                                                                                                                                                                 
        print red_dict['magcut'] 

        flag_mask = data_all.field('Flag') != 0

                                                                                                                                                                 
        mask = scipy.logical_or(photoz_mask, redseq_mask, flag_mask)

        objects_to_mask = data_all[mask]

        IDS_mask, x_mask, y_mask = objects_to_mask.field('SeqNr'), objects_to_mask.field('Xpos'), objects_to_mask.field('Ypos')

        
        areas = scipy.ones(segmentation.shape)
        areas[weight == 0] = 0.0

        print 'masking'
        for i in range(len(IDS_mask)):
            ID = IDS_mask[i]
            y = x_mask[i] 
            x = y_mask[i] 
        
            seg_num = segmentation[x,y]
        
            #print segmentation.shape
            print max(0,x-100),min(9999,x+100),max(0,y-100),min(9999,y+100)
            piece = segmentation[max(0,x-100):min(9999,x+100),max(0,y-100):min(9999,y+100)] 
            #print 
            mask = piece == seg_num 
            #print mask
            areas[max(0,x-100):min(9999,x+100),max(0,y-100):min(9999,y+100)][mask] = 0
            print areas[max(0,x-100):min(9999,x+100),max(0,y-100):min(9999,y+100)], len(IDS_mask)
            print ID
        
        fitsobj = pyfits.HDUList()
        hdu = pyfits.PrimaryHDU()
        hdu.data = areas
        fitsobj.append(hdu)
        file = photdir + 'cluster_mask.fits'
        os.system('rm ' + file)
        fitsobj.writeto(file)
        print file
    
        area = areas
    else:
        area = pyfits.open(photdir + 'cluster_mask.fits')[0].data
    
    print 'making radii'
    x,y = scipy.meshgrid(scipy.arange(area.shape[0]),scipy.arange(area.shape[1]))
    r = ((x - scipy.ones(area.shape)*xcen)**2. +  (y - scipy.ones(area.shape)*ycen)**2.)**0.5
   
    bins = scipy.arange(0,1.2,0.05)
    
    dict = {}
    #[data_all.field('BPZ_T_B')<=3,'REDOFRS','green',False]]: #,
    for mask, name, color, photoz_cut in [[data_all.field('BPZ_T_B')<4,'EARLY','red',True],[data_all.field('BPZ_T_B')>3,'LATE','blue',True]]: #,[data_all.field('BPZ_T_B')>-99,'CONTAM','green',False]]:
        print len(data_all)

        diff = (data_all.field(red_dict['c1']) - data_all.field(red_dict['c2'])) - data_all.field(red_dict['m'])*red_dict['slope'] 
        redseq_mask = (diff > red_dict['lower_intercept']) * (diff < red_dict['upper_intercept'])  #* (data_all.field(red_dict['m']) < float(red_dict['magcut']) )

        #mag_mask = (22.5 < data_all.field(prefix(DETECT_FILTER))) *  (25 > data_all.field(prefix(DETECT_FILTER)))
        if photoz_cut:
            #photoz_mask = phot_clus_mask*(data_all.field('BPZ_Z_B') > cluster_redshift + 0.1)*(data_all.field('BPZ_Z_B') < 3)*(mask)*(data_all.field(prefix('W-J-V')) < 25)#*(data_all.field(prefix(DETECT_FILTER)) < 25)

            photoz_mask = phot_clus_mask*(data_all.field('BPZ_Z_B') > cluster_redshift + 0.15)*(data_all.field('BPZ_Z_B') < 3)*(mask)#*(data_all.field(prefix('W-J-V')) < 25)#*(data_all.field(prefix(DETECT_FILTER)) < 25)
            data = data_all[photoz_mask] #*(redseq_mask==False)]
        else:
            diff = (data_all.field(red_dict['c1']) - data_all.field(red_dict['c2'])) - data_all.field(red_dict['m'])*red_dict['slope'] 
            red_of_redseq_mask = scipy.logical_or(diff > red_dict['upper_intercept'], diff < red_dict['lower_intercept'])  #* (data_all.field(red_dict['m']) < float(red_dict['magcut']) )
            data = data_all[(red_of_redseq_mask)]
        #plot_cmd(data,red_dict,website+name.replace(' ','')+'.png',cluster_redshift,title=name,)    

        plot_cc(data,red_dict,website+name.replace(' ','')+'.png',cluster_redshift,title=name,)    

        for plot_var, bins, name_plot in [['BPZ_Z_B',scipy.arange(0,1.2,0.05),'redshifts.png'],[prefix(DETECT_FILTER),scipy.arange(19,28,0.2),'mags.png']]:
                                                                                                                                                            
            pylab.clf()
            data_save = copy(data)
            pylab.hist(data_save.field(plot_var),bins=bins,histtype='step',label='ALL')                                       
            #data_save = data_save[data_save.field('BPZ_ODDS') > BPZ_CUT]
            #data_save = data_save[phot_clus_mask]
            #pylab.hist(data_save.field(plot_var),bins=bins,histtype='step',label='ODDS > 0.3')
            #pylab.hist(data_save.field(plot_var),bins=bins,histtype='step',label='NO CLUSTER GALAXIES')
            #data_save = data_save[(data_save.field('BPZ_Z_B') > cluster_redshift + 0.1)*(data_save.field('BPZ_Z_B') < 1.2)]
            #pylab.hist(data_save.field(plot_var),bins=bins,histtype='step',label='Z > Z_CLUSTER + 0.1')
            #pylab.hist(data_save.field(plot_var)[data_save.field('BPZ_T_B')<3],bins=bins,histtype='step',label='EARLY T < 3')
            #pylab.hist(data_save.field(plot_var)[data_save.field('BPZ_T_B')>=3],bins=bins,histtype='step',label='LATE T >= 3')
            [xmin, xmax, ymin, ymax] = pylab.axis()
            pylab.ylim([ymin,ymax*2.0])
            pylab.legend()
            pylab.title(name)
            pylab.xlabel(plot_var)
            pylab.ylabel('Galaxies')
            pylab.savefig(website + '/' + name + name_plot )
                                                                                                                                                            
            mag_page.write('<br><img src=' + name + name_plot + '></img>\n')







        mag_page.write('<img src=' + name.replace(' ','') + '.png></img><br>\n')
        radius = ((data.field('Xpos') - xcen)**2. + (data.field('Ypos') - ycen)**2.)**0.5 

        densities = []
        densities_error = []
        radii = []
        densities_nosub = []
        objects = []
        areas_list = []
        
        annuli = zip(scipy.arange(0,1950,150),scipy.arange(150,2100,150))
        mask = (radius < annuli[-1][1])
        data_inside = data[mask] 
        radius_inside = radius[mask]

        for low,high in annuli: #[[0,150],[150,300],[300,600],[600,1200],[1200,1600],[1600,3000],[3000,4000]]:
            print low, high
            mask_r = (r > low) * (r < high)
            #print mask_r.shape
            #print area
            #print area.shape
            subarea = area[mask_r]
            a = scipy.sum(subarea) * (0.2/60)**2.
            area_nosub = math.pi * (high**2.-low**2.) * (0.2/60.)**2.
            areas_list.append(area_nosub)
            mask = (radius_inside > low) * (radius_inside <  high)
            subset = data_inside[mask] 
            print len(subset)
            density = float(len(subset)) / a
            densities.append(density)
            densities_nosub.append(len(subset) / area_nosub)
            densities_error.append(math.sqrt(len(subset))/a)
            radii.append(scipy.average(radius_inside[mask])*0.2/60. )
            objects.append(len(subset))
        
            print radii, densities, len(subset), 'objects'

        plot_regions(data_inside,website)
        dict[color] = {'densities':densities, 'areas':areas_list, 'objects': objects, 'densities_nosub':densities_nosub, 'densities_error':densities_error, 'radii':radii, 'name':name}
    
    pylab.clf()
    for key in dict:    
        #pylab.errorbar(dict[key]['radii'],dict[key]['objects'],yerr=(dict[key]['objects'])**0.5,fmt=None,ecolor=key)
        pylab.scatter(dict[key]['radii'],dict[key]['objects'],color=key,label=dict[key]['name'])
    
    pylab.title('Area')
    pylab.xlabel('Radius (Arcmin)')
    pylab.ylabel('Objects')
    x1,x2,y1,y2 = pylab.axis()
    pylab.ylim([0,y2])
    pylab.legend()
    pylab.savefig(website + '/area.png')
                                                                                                                        
    mag_page.write('<b><img src=area.png></img>\n')

    pylab.clf()
    for key in dict:    
        #pylab.errorbar(dict[key]['radii'],dict[key]['objects'],yerr=(dict[key]['objects'])**0.5,fmt=None,ecolor=key)
        pylab.scatter(dict[key]['radii'],dict[key]['areas'],color=key,label=dict[key]['name'])
    
    pylab.title('Number of Objects')
    pylab.xlabel('Radius (Arcmin)')
    pylab.ylabel('Objects')
    x1,x2,y1,y2 = pylab.axis()
    pylab.ylim([0,y2])
    pylab.legend()
    pylab.savefig(website + '/objects.png')
                                                                                                                        
    mag_page.write('<b><img src=objects.png></img>\n')










    pylab.clf()
    for key in dict:    
        pylab.errorbar(dict[key]['radii'],dict[key]['densities'],yerr=dict[key]['densities_error'],fmt=None,ecolor=key)
        pylab.scatter(dict[key]['radii'],dict[key]['densities'],color=key,label=dict[key]['name'])
    
    pylab.title('Objects Subtracted')
    pylab.xlabel('Radius (Arcmin)')
    pylab.ylabel('Object Density (Objects/Arcmin^2)')
    x1,x2,y1,y2 = pylab.axis()
    pylab.ylim([0,y2])
    pylab.legend()
    pylab.savefig(website + '/sub.png')

    mag_page.write('<b><img src=sub.png></img>\n')
    
    
    
    pylab.clf()
    for key in dict:    
        pylab.errorbar(dict[key]['radii'],dict[key]['densities_nosub'],yerr=dict[key]['densities_error'],fmt=None,ecolor=key)
        pylab.scatter(dict[key]['radii'],dict[key]['densities_nosub'],color=key,label=dict[key]['name'])
    pylab.title('Full Annuli')
    pylab.xlabel('Radius (Arcmin)')
    pylab.ylabel('Object Density (Objects/Arcmin^2)')
    x1,x2,y1,y2 = pylab.axis()
    pylab.ylim([0,y2])
    pylab.legend()
    pylab.savefig(website + 'full.png')

    mag_page.write('<b><img src=full.png></img>\n')
    
    
    reg = open(imdir + 'all.reg','w')
    reg.write('global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source\nphysical\n')
    for i in range(len(data.field('Xpos'))):   
        reg.write('circle('+str(data.field('Xpos')[i]) + ',' + str(data.field('Ypos')[i]) + ',' + str(5) + ') # color=red width=2 text={' + str(data.field('BPZ_Z_B')[i]) + '}\n')
    reg.close()

if __name__ == '__main__':
    
    run()

