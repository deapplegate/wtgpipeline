
def run_sextract(image,psf_fwhm=1):

    import os
    PHOTCONF = os.environ['bonn'] + '/photconf/'
    params = {'image':image, 'catalog':'/tmp/' + image.split('/')[-1] + '.patcat', 'PHOTCONF':PHOTCONF, 'psf_fwhm':psf_fwhm}
    
    command = "sex %(image)s -c %(PHOTCONF)s/phot.conf.sex \
    -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
    -CATALOG_NAME %(catalog)s \
    -FILTER_NAME %(PHOTCONF)s/default.conv\
    -FILTER  Y \
    -FLAG_TYPE MAX \
    -FLAG_IMAGE '' \
    -SEEING_FWHM %(psf_fwhm).3f \
    -DETECT_MINAREA 8 -DETECT_THRESH 8 -ANALYSIS_THRESH 8 \
    -MAG_ZEROPOINT 27.0 \
    " % params
    
    print '\n', command
    os.system(command)

def plot_regions(xs,ys,file='regstart.reg',save=False):
    import os
    reg = open(file + '.reg','w')
    reg.write('global color=red dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\nphysical\n')
    for x,y in zip(xs,ys):
        reg.write('circle(' + str(x) + ',' + str(y) + ',4)#' + '\n')
    reg.close()



def hist(size):
    import pylab
    from scipy import arange
    a, b, varp = pylab.hist(size,bins=arange(0,5,0.3),color='blue',edgecolor='black')
    seeing = -99 
    tot = 0
    for i in range(len(a)):
        if a[i] > tot: 
            tot = a[i]
            seeing = (b[i] + b[i+1])/2.

    print a, b, varp
    print seeing*0.2
    return seeing*0.2







supa = 'SUPA0033028'
cluster = 'RXJ1720'


supa = 'SUPA0017066'
cluster = 'MACS0018+16'
filt = 'W-C-IC'

imtype = ''
path = '/nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/' + filt + '/SCIENCE/' + imtype + 'coadd_' + cluster + '_' + supa + '/'

#rotation = 0

diffs = [] 
errs = []
radii = []
xs_all = []
ys_all = []

for chip in [1,2,3,4,5,7,8,9,10]:
    image_root = path + supa + '_' + str(chip) + 'OCFSFI.sub'
    image = image_root + '.fits'
    image_resam = image_root + '.' + cluster + '_' + supa + '.resamp.fits'

    import pyfits, commands

    crpix1 = float(commands.getoutput('gethead ' + image + ' CRPIX1'))
    crpix2 = float(commands.getoutput('gethead ' + image + ' CRPIX2'))
    rotation = int(float(commands.getoutput('gethead ' + image + ' ROTATION')))

    print crpix1, crpix2
    print image, image_resam
    run_sextract(image)
    p = pyfits.open('/tmp/' + image.split('/')[-1] + '.patcat')[2]
    psf_fwhm = hist(p.data.field('FLUX_RADIUS'))
    run_sextract(image_resam,psf_fwhm)

    
    import pyfits
    p_resam = pyfits.open('/tmp/' + image_resam.split('/')[-1] + '.patcat')[2]

    print 'making KDTrees'
    from scipy import spatial
    data = zip(p.data.field('X_WORLD'),p.data.field('Y_WORLD'))
    if rotation == 0:
        data_pixel = zip(4080 - p.data.field('Y_IMAGE'),p.data.field('X_IMAGE'))
    else:
        data_pixel = zip(p.data.field('X_IMAGE'),p.data.field('Y_IMAGE'))
    kdtree = spatial.KDTree(data_pixel)

    data_resam = zip(p_resam.data.field('X_WORLD'),p_resam.data.field('Y_WORLD'))
    data_resam_pixel = zip(p_resam.data.field('X_IMAGE'),p_resam.data.field('Y_IMAGE'))


    kdtree_resam = spatial.KDTree(data_resam_pixel)

    #print done
    print 'now match'

    match = kdtree.query_ball_tree(kdtree_resam,20.)

    match_broad = kdtree.query_ball_tree(kdtree_resam,30.)

    xs = []
    ys = []

    for i in range(len(data)):

        if p.data.field('CLASS_STAR')[i] > 0.35 and len(match[i]) == 1 and len(match_broad[i]) == 1 and p_resam.data.field('FLAGS')[match[i]] == 0 and p.data.field('FLAGS')[i] == 0 and p.data.field('FLUX_MAX')[i] < 25000: # and radius < 15./60.:    

            ''' in detail not quite right need extra factor '''
            #radius = ((p_resam.data.field('X_WORLD')[match[i][0]] - 215.940262)**2. + (p_resam.data.field('Y_WORLD')[match[i][0]] - 24.099972)**2.)**0.5

            radius = 0.2/3600.*((p.data.field('X_IMAGE')[i] - crpix1)**2. + (p.data.field('Y_IMAGE')[i] - crpix2)**2.)**0.5

            #radius = ((p_resam.data.field('X_WORLD')[match[i][0]] - 215.940262)**2. + (p_resam.data.field('Y_WORLD')[match[i][0]] - 24.099972)**2.)**0.5
            if 1: #radius < 15./60:
                print match[i]                                                                          
                print data[i], data_resam[match[i][0]], match[i]
                print data_pixel[i], data_resam_pixel[match[i][0]], match[i]
                diffs.append(p_resam.data.field('MAG_AUTO')[match[i][0]] - p.data.field('MAG_AUTO')[i])
                errs.append(p.data.field('MAGERR_AUTO')[i])
                xs.append(p.data.field('X_IMAGE')[i])
                ys.append(p.data.field('Y_IMAGE')[i])

                xs_all.append(p.data.field('X_IMAGE')[i] - crpix1)
                ys_all.append(p.data.field('Y_IMAGE')[i] - crpix2)


                radii.append(radius)

    plot_regions(xs,ys,'/tmp/' + image.split('/')[-1])



import pylab
pylab.clf()
pylab.rcParams.update({'text.usetex' : True, 'axes.labelsize': 20})
print radii
print len(radii), len(diffs)
import scipy
diffs = scipy.array(diffs)
radii = scipy.array(radii)

if 1: #False:
    mask = (diffs < 0.05) * (diffs > -0.05)
    polycoeffs = scipy.polyfit(radii[mask],diffs[mask],1)
    yfit = scipy.polyval(polycoeffs,sorted(radii))
pylab.errorbar(radii,diffs,yerr=errs,fmt='ro',mfc='red',mec='gray',color='gray')
pylab.scatter(radii,diffs,color='red')
pylab.plot(sorted(radii),yfit,'b-',color='blue')
pylab.ylim([-0.07,0.07])
pylab.ylabel('$M_{SWarp}$ - $M_{original}$ (counts)')
pylab.xlabel('Distance from Field Center (degrees)')
pylab.savefig(supa + '_old_SWarp.pdf')
#pylab.show()
pylab.clf()
pylab.scatter(xs_all, ys_all, c=diffs)

pylab.xlabel('X')
pylab.xlabel('Y')
pylab.savefig(supa + '_old_position_SWarp.pdf')
pylab.show()
        
    
print match
    


























