#adam-use# I THINK: you run redsequence.py before plot_rederr.py. This code identifies red-sequence galaxies!
# usage: python redsequence [options]
# 	Identifies and fits the red sequence using apparent magnitude and one color.
# 	Option of identifying star column and only using objects larger.
import pylab

params_pylab = {'backend' : 'ps',
     'text.usetex' : False,
      'ps.usedistiller' : 'xpdf',
      'ps.distiller.res' : 6000}
pylab.rcParams.update(params_pylab)
                                       
fig_size = [5,5]
params_pylab = {'axes.labelsize' : 14,
          'text.fontsize' : 14,
          'legend.fontsize' : 12,
          'xtick.labelsize' : 10,
          'ytick.labelsize' : 10,
          'scatter.s' : 0.1,
            'scatter.marker': 'o',
          'figure.figsize' : fig_size}
pylab.rcParams.update(params_pylab)


def sortit(x,y):
    if x[0] > y[0]: return -1
    else: return 1 


def sortit_rev(x,y):
    if x[0] > y[0]: return 1
    else: return -1 


def fit_starcolumn(size, savepng):
    import pylab, scipy
  
    boxes = [] 
    coords = []
    for increment in [0,0.03]:# ,0.075,0.1]: #1,0.125,0.15,0.175]: 
        #print size
        a,b,varp = pylab.hist(size,bins=scipy.arange(0+increment,2+increment,0.06)) 
        #print a, b
        boxes += list(a)
        coords += list(b[:-1] + scipy.ones(len(b[:-1]))*(0.03))
   
    tot = scipy.array(boxes).sum() 
    print tot
    all = zip(coords,boxes)
    all.sort(sortit_rev)
    print all

    sum = 0
    max = 0
    min = 1000000
    foundCenter = False
    from copy import copy
    print all, 'all'
    for x,y in all:
        print x, y, sum, tot
        sum += y
        if float(sum)/tot > 0.05:            
            if y > max and not foundCenter: 
                max = copy(y)
                max_x = copy(x)
                print 'max', max
            if y/max < 0.98 and not foundCenter:
                center = copy(max_x)
                print center, 'center'
                foundCenter = True
            if foundCenter:
                print 'min', min, y
                if min > y: 
                    min = copy(y)                 
                    min_x = copy(x)
                print y, min
                if y/float(min) > 1.05: 
                    right = copy(min_x)
                    break

    left = center - 1.*abs(right-center)
    print center,right, 'center, right' 

        
    print len(boxes), len(coords) 
    pylab.clf()
    pylab.scatter(coords,boxes)
    pylab.xlim(0,2.5)
    pylab.xlabel('SIZE (arcsec)')
    pylab.axvline(x=center,ymin=-10,ymax=10)
    pylab.axvline(x=left,ymin=-10,ymax=10)
    pylab.axvline(x=right,ymin=-10,ymax=10)
    pylab.savefig(savepng)
    pylab.clf()

    return left, right

def fit(colors, c1, c2, m, savepng):
    import pylab, scipy
 
    ''' essentially fine resolution binning ''' 
    boxes = [] 
    coords = []
    for increment in [0,0.025,0.05,0.075,0.1,0.125,0.15,0.175]: 
        a,b,varp = pylab.hist(colors,bins=scipy.arange(-4+increment,4+increment,0.2)) 
        #print a, b
        boxes += list(a)
        coords += list(b[:-1] + scipy.ones(len(b[:-1]))*(0.1))

    print len(colors), colors, 'len'
   
    tot = scipy.array(boxes).sum() 
    print tot

    solutions = []
    for version in ['reverse']: #:,'forward']:

        left = -99
        center = -99

        all = zip(coords,boxes)
        if version == 'reverse':
            all.sort(sortit)                               
        if version == 'forward':
            all.sort(sortit_rev)                               

        print all
        pylab.clf()
        pylab.scatter(coords,boxes)
        #pylab.show()
        print 'plotted'
                                                       
        sum = 0
        max_y = 0
        min = 1000000
        foundCenter = False
        from copy import copy
        print all, 'all'
                                                       
        rev = zip(all[:][1],all[:][0])        
                                                       
        a = zip(boxes, coords)
        a.sort()
        peak = a[-1][1]

        foundCenter = False
                                                       
                                                       
        for x,y in all:
            print x, y, sum, tot

            print max_y, min, foundCenter, peak



        




            sum += y
            #print all[-1][0], all[0][0]

        
            if sum > 0: 
                if    float(tot)/sum > 0.05 and y > 100: #True: # (all[-1][0] < all[0][0] and x < peak ) or (all[-1][0] > all[0][0] and x > peak ): #            
                    if y > max_y and not foundCenter:      
                        max_y = copy(y)
                        max_x = copy(x)
                        print 'max', max_y
                    print y/max_y, (max_y-y)
                    if y/max_y < 0.98 and (max_y-y) > 15 and not foundCenter:
                        center = copy(max_x)
                        print center, 'center', max_y
                        foundCenter = True
                #center = peak
                if foundCenter:
                    print 'min', min, y
                    if min > y: 
                        min = copy(y)                 
                        min_x = copy(x)
                    print y, min, x
                    if y/float(min) > 1.04: 
                        left = copy(min_x)
                        print peak, left, center, 'FOUND ONE'
                        break


        if left != -99:
            if left > center:
                left = center - max(0.05,abs(center - left))
            right = center + max(0.4,1.*abs(left-center))
            print center, left, right, peak
            print right - peak, peak - left
            if True: #right - peak > 0 and peak - left > 0:
                solutions.append([center,left,right])

    ''' pick out the narrower solution '''
    if len(solutions) > 1:
        if solutions[0][0] - solutions[0][1] < solutions[1][0] - solutions[1][1]: 
            solution = solutions[0]
        else: solution = solutions[1]
    else: solution = solutions[0]


    center, left, right = solution


    
    print center, left, right        
    print len(boxes), len(coords) 

    #print boxes, coords
    pylab.clf()
    pylab.scatter(coords,boxes)
    pylab.xlabel(c1 + ' - ' + c2)
    pylab.axvline(x=center,ymin=-10,ymax=10)
    pylab.axvline(x=left,ymin=-10,ymax=10)
    pylab.axvline(x=right,ymin=-10,ymax=10)
    pylab.savefig(savepng)

    return left, right


def run():
    from optparse import OptionParser
    
    usage = "usage: python redsequence [options] \n\nIdentifies and fits the red sequence using apparent magnitude and one color.\nOption of identifying star column and only using objects larger.\n"
    parser = OptionParser(usage)
    
    parser.add_option("-c", "--cluster", 
                      help="name of cluster (i.e. MACS0717+37)")
    parser.add_option("-d", "--detectband", 
                      help="detection band (i.e. W-J-V)",default='W-J-V')
    parser.add_option("--c1", 
                      help="name of first filter in 'galaxy color' (i.e. MAG_APER1-SUBARU-COADD-1-W-J-V)",default='MAG_APER1-SUBARU-COADD-1-W-J-V')
    parser.add_option("--c2", 
                      help="name of second filter in 'galaxy color' (i.e. MAG_APER1-SUBARU-COADD-1-W-C-RC)",default='MAG_APER1-SUBARU-COADD-1-W-C-RC')
    parser.add_option("-m",'--m', 
                      help="name of filter to be used as 'galaxy magnitude' (default is '--c2')",default=None)
    parser.add_option("-s", "--starcolumn", 
                      help="add to filter out star column",action="store_true",default=False)
    parser.add_option('--lm', 
                      help="limiting magnitude applied to 'galaxy magnitude'",default=False)
    parser.add_option('-r',"--center_radius",  
                      help="maximum galaxy radius from cluster center (in arcsec) (default=440)",default=660.)
    parser.add_option("-l","--location",  
                      help="write output directory",default=None)
    parser.add_option("-w","--web",  
                      help="instead write to web (Pat's space)",action="store_true",default=False)
    parser.add_option("-z", "--z", 
                      help="see what the photometric redshifts are of redsequence galaxies (requires redshift catalog, obviously)",action='store_true',default=False)
    parser.add_option("--cat",
                      help="name of alternate input catalog (if you don't want to use the default photometry catalog)",default=None)
    parser.add_option("--existingcolor",
                        help="use existing colors of red sequence fit",action="store_true",default=False)    
    parser.add_option("-e","--existing",
                        help="use existing red sequence fit",action="store_true",default=False)    
    
    (options, args) = parser.parse_args()
    
    if options.m is None:
        options.m = options.c2
    
    if options.location is not None and options.web:
        print 'Either specify location or web but not both at once'
        raise Exception
    
    if options.location is None and options.web is False:
        options.location = '/nfs/slac/g/ki/ki05/anja/SUBARU/' + options.cluster + '/PHOTOMETRY_' + options.detectband + '_iso/'
    elif options.web:
        options.location = '/nfs/slac/g/ki/ki04/pkelly/photoz/' + options.cluster + '/CWWSB_capak.list/'
    
    if options.location[-1] != '/': 
        options.location = options.location + '/'
    print options.location
    import os
    
    
    
    
    
    
    if options.existingcolor or options.existing:
        dir = '/nfs/slac/g/ki/ki05/anja/SUBARU/' + options.cluster + '/LENSING_' + options.detectband + '_' + options.detectband + '_aper/good/'
        dict = {} 
	print 'file', dir + 'redseqfit_2.orig'
        redseqfit = open(dir + 'redseqfit_2.orig','r').readlines()
        slope = float(redseqfit[1].split('=')[1].split('*')[0])
        intercept = float(redseqfit[1][:-1].split('+')[1])
    
        upper_intercept = float(redseqfit[3][:-1].split('+')[1])
        lower_intercept = float(redseqfit[4][:-1].split('+')[1])
    
    
        polycoeffs = [slope, intercept]
        std = (upper_intercept - intercept) / 1.2
         
        info = open(dir + 'redseq_all.params','r').readlines()
        print info, dir + 'redseq_all.params'
        for l in info:
            if len(l.split(':')) > 1:
                key, value = l[:-1].split(': ')
                dict[key] = value
    
        print dict
    
        #options.center_radius = dict['radcut']        
    
        def prefix(filt):
            if filt is 'g' or filt is 'r' or filt is 'u':
                return 'MAG_APER1-MEGAPRIME-COADD-1-' + filt
            else:
                return 'MAG_APER1-SUBARU-COADD-1-' + filt


        dict['slope'] = slope
        dict['intercept'] = intercept
        dict['lower_intercept'] = lower_intercept
        dict['upper_intercept'] = upper_intercept
   
        if options.existing: 
            options.m = prefix(dict['xmag'])
            options.c1 = prefix(dict['greenmag'])
            options.c2 = prefix(dict['redmag'])
            options.lm = dict['magcut2']
            print 'finished'        
        elif options.existingcolor:
            options.c1 = prefix(dict['greenmag'])
            options.c2 = prefix(dict['redmag'])

    cluster = options.cluster
    c1 = options.c1
    c2 = options.c2
    m = options.m
    
    
    
    
    
    
    if options.z:
        import astropy, astropy.io.fits as pyfits        
        cat = '/nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/PHOTOMETRY_' + options.detectband + '_aper/' + cluster + '.APER1.1.CWWSB_capak.list.all.bpz.tab'
        p = pyfits.open(cat)
        photoz = p['STDTAB'].data
        zero_IDs = len(photoz[photoz.field('SeqNr')==0])
        if zero_IDs > 0:
            print 'Wrong photoz catalog?', cat
            print str(zero_IDs) + ' many SeqNr=0' 
            raise Exception
    
        print cat
    
    if options.cat is None: #not hasattr(options,'cat'):
        input_mags = '/nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/PHOTOMETRY_' + options.detectband + '_aper/' + cluster + '.slr.alter.cat'
    else: input_mags = options.cat
    
    import astropy, astropy.io.fits as pyfits, os, sys, pylab, do_multiple_photoz, commands, re, math, scipy
    from copy import copy
    print 'input magnitude catalog:', input_mags, options.cat, hasattr(options,'cat')
    
    filterlist = do_multiple_photoz.get_filters(input_mags,'OBJECTS')
    #print filterlist
   
    print input_mags 
    w = pyfits.open(input_mags)
    mags = w['OBJECTS'].data
    
    #print mags.field('Xpos')
    
    mask = mags.field(c1) > -90 
    if options.z: photoz = photoz[mask]
    mags = mags[mask]
        
    mask = mags.field(c2) > -90 
    if options.z: photoz = photoz[mask]
    mags = mags[mask]
    
    mask = mags.field(m) > -90 
    if options.z: photoz = photoz[mask]
    mags = mags[mask]
    
    mask = mags.field('Flag') == 0 
    if options.z: photoz_star = photoz[mask]
    mags_star = mags[mask]
    
    
    #mask = mags_star.field(c2) < 23   
    
    ''' get cluster redshift '''
    command = 'grep ' + cluster + ' ' + '/nfs/slac/g/ki/ki05/anja/SUBARU/'  + '/clusters.redshifts ' 
    print command
    cluster_info = commands.getoutput(command)
    cluster_redshift = float(re.split('\s+',cluster_info)[1])
    print cluster_redshift
    
    if options.lm: 
        mag_cut = float(options.lm)
    else:
        ''' compute faint magnitude cutoff '''
        if m[-6:] == 'W-C-RC' or m[-1] == 'r':
            mag_cut = 21.5 + 2.5*math.log10((cluster_redshift/0.19)**2.)
        if m[-5:] == 'W-J-V' or m[-5:] == 'W-J-B' or m[-1] == 'g':
            mag_cut = 22. + 2.5*math.log10((cluster_redshift/0.19)**2.)

    if not options.center_radius:
        ''' compute radial size of cut '''
        options.center_radius = 400 / (z/0.4) 

    options.center_radius = 400
    
        
        
    print mag_cut, options.lm
    
    if True: #not options.existing:
        ''' identify star column (optional) '''
        if options.starcolumn:
            savepng =  '/nfs/slac/g/ki/ki04/pkelly/photoz/' + cluster + '/seeing.png'
            left, right = fit_starcolumn(mags_star[mask].field('FLUX_RADIUS')*0.2,savepng)
        
            savepng = options.location + 'column.png'
        
            pylab.axvline(x=left,ymin=-10,ymax=100)
            pylab.axvline(x=right,ymin=-10,ymax=100)
            pylab.scatter(mags.field('FLUX_RADIUS')*0.2,mags.field(m),s=0.25)
            pylab.xlim(0,2.5)
            pylab.xlabel('SIZE (arcsec)')
            pylab.ylabel(m)
            pylab.savefig(savepng)
            pylab.clf()
        
            mask = mags.field('FLUX_RADIUS')*0.2 > right 
            if options.z: photoz = photoz[mask]
            mags = mags[mask]
    
    
        
        ''' select galaxies near center of field '''
        #options.center_radius=240
        mask = ((mags.field('Xpos') - 5000.*scipy.ones(len(mags)))**2. +  (mags.field('Ypos') - 5000.*scipy.ones(len(mags)))**2.)**0.5  * 0.2 < float(options.center_radius)
        if options.z: photoz = photoz[mask]
        mags = mags[mask]

        print len(mags)
        if options.z: print len(photoz)
      
        from copy import copy 
        mags_mask = copy(mags) 
        x = copy(mags.field(m))
        y = copy(mags.field(c1)-mags.field(c2))

        print mags.field(c1), mags.field(c2), c1, c2
        
        mask = x < mag_cut 

        print mag_cut
        #print x, y
        
        savedir= options.location 
        os.system('mkdir -p ' + savedir)
        
        savepng =  options.location + 'redselection.png'
       
        print options.center_radius, len(y[mask]) 
        left, right = fit(y[mask],c1,c2,m,savepng)
    
   
        if options.z: 
            mask = photoz.field('NFILT') > 3                                                                                                                                                             
            reg_mags = mags_mask[mask]
            reg_photoz = photoz[mask]        
            mask = photoz.field('BPZ_ODDS') > 0.95 
            reg_mags = mags_mask[mask]
            reg_photoz = photoz[mask]        

            print len(reg_photoz)
            
            print 'making reg'
            reg = open('all.reg','w')
            reg.write('global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source\nphysical\n')
            for i in range(len(reg_mags.field('Xpos'))):
                reg.write('circle('+str(reg_mags.field('Xpos')[i]) + ',' + str(reg_mags.field('Ypos')[i]) + ',' + str(5) + ') # color=red width=2 text={' + str(reg_photoz.field('BPZ_Z_B')[i]) + '}\n')
            reg.close()
                                                                                                                                                                                                         
            print 'finished reg'
    
    
    
    
    
    
        
        mask = x < mag_cut 
        if options.z: 
            photoz2 = photoz[mask]
            mags_mask = mags_mask[mask]
        x2 = x[mask]
        y2 = y[mask]
        
        #print sorted(x2)
        print savepng
        
        print left, right 
    
    
        
    
    
    
    
    
    
        if not options.existing:
            mask =  y2 > left               
            if options.z: 
                photoz2 = photoz2[mask]
                mags_mask = mags_mask[mask]
            x2 = x2[mask]
            y2 = y2[mask]
            
            mask =  y2 < right
            if options.z: 
                photoz2 = photoz2[mask]
                mags_mask = mags_mask[mask]
            x2 = x2[mask]
            y2 = y2[mask]
        
        if not options.existing: polycoeffs = scipy.polyfit(x2,y2,1)
        print polycoeffs
    
        yfit = scipy.polyval(polycoeffs, x2)
        
        print x2, yfit
        if not options.existing: std = scipy.std(abs(yfit - y2))
        print std
        mask = abs(yfit - y2) < std*2.5 
        if options.z: photoz3 = photoz2[mask]
        x3 = x2[mask]
        y3 = y2[mask]
        
        if not options.existing: polycoeffs = scipy.polyfit(x3,y3,1)
    
        print polycoeffs
        yfit = scipy.polyval(polycoeffs, sorted(x2))
        print x2, yfit
        if not options.existing: std = scipy.std(abs(yfit - y2))
        print std
        std_fac = 1.2 
    
    
    mask = abs(yfit - y2) < std*std_fac 
    if options.z: 
        photoz2 = photoz2[mask]
        mags_mask = mags_mask[mask]
        print photoz2.field('SeqNr')
        print photoz2.field('BPZ_Z_B')
    
        fred = '/nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/PHOTOMETRY_' + options.detectband + '_aper/' + cluster + '.redseq'
    
        f = open(fred,'w')
        for id in photoz2.field('SeqNr'):
            f.write(str(id) + '\n')
        f.close()        
    
        
        reg = open('regseq.reg','w')
        reg.write('global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source\nphysical\n')
        for i in range(len(mags_mask.field('Xpos'))):
            reg.write('circle('+str(mags_mask.field('Xpos')[i]) + ',' + str(mags_mask.field('Ypos')[i]) + ',' + str(5) + ') # color=green width=2 text={' + str(photoz2.field('BPZ_Z_B')[i]) + '}\n')
        reg.close()
    
    
    
    
    
    
        
    
    pylab.clf()
    
    savepng = options.location + 'redhistogram.png'
    savepdf = options.location + 'redhistogram.pdf'
    
    if options.z:
        lower_lim = cluster_redshift - 0.3
        if lower_lim < 0: lower_lim = 0.0001
        print photoz2.field('BPZ_Z_B')
        a,b,varp = pylab.hist(photoz2.field('BPZ_Z_B'),bins=scipy.arange(lower_lim,cluster_redshift+0.3,0.01),color='red')
        pylab.axvline(x=cluster_redshift,ymin=0,ymax=100,color='blue',linewidth=3)
        pylab.xlabel('Redshift')
	pylab.ylabel('Galaxies')
        pylab.savefig(savepng)
        pylab.savefig(savepdf)
    
        
        reg = open('reg.reg','w')
        reg.write('global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source\nphysical\n')
        for i in range(len(mags_mask.field('Xpos'))):
            reg.write('circle('+str(mags_mask.field('Xpos')[i]) + ',' + str(mags_mask.field('Ypos')[i]) + ',' + str(5) + ') # color=blue width=2 text={' + str(photoz2.field('BPZ_Z_B')[i]) + '}\n')
        reg.close()
    
    
    
    
    
    
    
    
    
    
    
    pylab.clf()
    pylab.plot(sorted(x2),yfit,'b-')
    pylab.plot(sorted(x2),yfit+scipy.ones(len(yfit))*std*std_fac,'b-')
    pylab.plot(sorted(x2),yfit-scipy.ones(len(yfit))*std*std_fac,'b-')
    pylab.scatter(x,y,color='red',s=0.5)
    pylab.axhline(y=left,xmin=-10,xmax=100)
    pylab.axvline(x=mag_cut,ymin=-10,ymax=10)
    pylab.axhline(y=right,xmin=-10,xmax=100)
    pylab.xlabel(m)
    pylab.ylabel(c1 + ' - ' + c2) 
    
    if options.z:
        mask = abs(photoz.field('BPZ_Z_B') - cluster_redshift) <  0.04 
        mags = mags[mask]
        photoz = photoz[mask]
    
    
        mask = photoz.field('NFILT') > 4
        mags = mags[mask]
        photoz = photoz[mask]
    
        print 'priormag'
        print photoz.field('priormag') 
        print 'nfilt'
        print photoz.field('NFILT') 
    
    
    
        import pylab
        x = mags.field(m)
        y = mags.field(c1)-mags.field(c2)
        pylab.scatter(x,y,s=0.5)
    
        
        reg = open('reg.reg','w')
        reg.write('global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source\nphysical\n')
        for i in range(len(mags.field('Xpos'))):
            reg.write('circle('+str(mags.field('Xpos')[i]) + ',' + str(mags.field('Ypos')[i]) + ',' + str(5) + ') # color=red width=2 text={' + str(photoz.field('BPZ_Z_B')[i]) + '}\n')
        reg.close()
    
    
    
    
    
    
    pylab.xlim(sorted(x)[0],sorted(x)[-2])
    span = (sorted(y)[-2]-sorted(y)[2])/2
    if span > 1: span=1
    median = scipy.median(scipy.array(y))
    pylab.ylim(median -2, median + 2)
    
    savepng =  options.location + 'cmd.png'
    pylab.savefig(savepng)
    
    pylab.clf()
    pylab.scatter(mags.field('Xpos'),mags.field('Ypos'), s=0.02)
    pylab.xlim([0,10000])
    pylab.ylim([0,10000])
    pylab.xlabel('X Pixel')
    pylab.ylabel('Y Pixel')
    
    savepng =  options.location + '/positions.png'
    print savepng
    pylab.savefig(savepng)
    
    
    s = "\nBest fit: y = "+str(polycoeffs[0])+"*x +"+str(polycoeffs[1]) + '\n'
    s += "\nCut: y < "+str(polycoeffs[0])+"*x +"+str(polycoeffs[1]+std_fac*std) + '\n'
    s += "Cut: y > "+str(polycoeffs[0])+"*x +"+str(polycoeffs[1]-std_fac*std ) + '\n'
    s += "x < "+str(mag_cut) + '\n'
    s += 'x = ' + m + '\n'
    s += 'y = ' + c1 + ' - ' + c2 + '\n'
    
    
    print s
    
    f = open(options.location + '/redseqfit','w')
    f.write(s)
    f.close()


    from datetime import datetime
    t2 = datetime.now()
   
    print options.location 
    f = open(options.location + '/redsequence.html','w')
    f.write('<html><tr><td>' + t2.strftime("%Y-%m-%d %H:%M:%S") + '</td></tr><tr><td><h2>Photometric Redshifts of the Red Sequence</h2></td></tr><tr><td><img src="redhistogram.png"></img></td></tr><tr><td><img src="seeing.png"></img></td></tr><<tr><td><img src="column.png"></img></td></tr><tr><td><img src="redselection.png"></img></td></tr><tr><td><img src="cmd.png"></img></td></tr><tr><td><img src="positions.png"></img></td></tr><tr><td>' + s.replace('\n','<br>') + '</td></tr>        </html>')
    
    print 'Wrote output to:', options.location
    print 'Best fit parameters in:', options.location + '/redseqfit'

if __name__ == '__main__':
    run()
