import numpy, sys, os, pylab, astropy.io.fits as pyfits, ldac, math



def open_and_get_shearcat(filename, tablename):
    #
    # for opening and retrieving shear cat.
    # 
    return  ldac.openObjectFile(filename, tablename)
    

#class ello

def avg_shear(g1array, g2array):
    avg1 = numpy.mean(g1array)
    avg2 = numpy.mean(g2array)
    # leave open possibility of weighted average
    return [avg1,avg2]

    


def avg_shear_aniscorr(g1array, g2array, epol1, epol2):
    # g1 array : numpy array of g1
    # g2 array : numpy array of g2
    # e1po1 array: array of e1 correction at gal position
    # e2pol array: array of e2 correction at gal position
    # Average shear in bins of the ell correction
    # this may be defunct.

    # get indices of sorted (by epol) arrays
    indx = numpy.lexsort((g1array,epol1))
    indy = numpy.lexsort((g2array,epol2))
    
    sortedx = []
    sortedy = []
    binsy =[0] # first bin 0
    binsx =[0] # 
    binwidth = len(g1array) / 10 # 10 bins
    for j in range(1,10):
        binsx.append(epol1[ind[j*binwidth]]+0.00001)
        binsy.append(epol2[ind[j*binwidth]]+0.00001)

    binsx.append(epol1[ind[-1]]+0.00001)
    binsy.append(epol2[ind[-1]]+0.00001)
    

    
    for i in range(len(g1array)):
        sortedx.append([g1array[indx[i]],epol1[indx[i]]])
        sortedy.append([g2array[indx[i]],epol2[indx[i]]])

    xarr = numpy.array(sortedx)
    yarr = numpy.array(sortedy)
    xavgs = []
    yavgs = []
    
    for j in range(10):
        xavgs.append(numpy.average(xarr[binsx[j]:binsx[j+1],0]))
        yavgs.append(numpy.average(yarr[binsy[j]:binsy[j+1],0]))


    return xavgs, binsx, yavgs, binsy
    # lets make 10 bins


def avg_epol_gamma(g1array, g2array, epol1, epol2):
    # g1 array : numpy array of g1
    # g2 array : numpy array of g2
    # e1po1 array: array of e1 correction at gal position
    # e2pol array: array of e2 correction at gal position

    avg1 = numpy.mean(g1array*epol1)
    err1 = numpy.std(g1array*epol1)/math.sqrt(len(epol1)*1.0)
    err1bs = do_bootstrap_error(g1array*epol1)
    avg2 = numpy.mean(g2array*epol2)
    err2 = numpy.std(g2array*epol2)/math.sqrt(len(epol2)*1.0)
    err2bs = do_bootstrap_error(g2array*epol2)
    # print avg1,avg2,err1,err2
    return avg1,avg2,err1,err2,err1bs, err2bs 


def star_gal_correlation(galarray, stararray):
    # galarray: array with galaxy positions and
    #           shears values.
    # stararray: array with star positions and
    #           ell values values.

    gal_g1arr = galarray['g1']
    gal_g2arr = galarray['g2']
    gal_xarr  = galarray['x']
    gal_yarr  = galarray['y']
    
    star_xarr  =  stararray['x']
    star_yarr  =  stararray['y'] 
    star_e1pol =  stararray['e1pol']
    star_e2pol =  stararray['e2pol']
    star_e1    =  stararray['e1']
    star_e2    =  stararray['e2']

    # create full arrays for correlations
    # star arrays : 1111... 22222... 3333...
    # gal  arrays : 1234... 12345... 1234
    #
    starlen=len(stararray['e1'])
    gallen=len(galarray['g1'])

    gal_g1corr = make_gal_corrarray(galarray['g1'],starlen)
    gal_g2corr = make_gal_corrarray(galarray['g2'],starlen)
    gal_xcorr = make_gal_corrarray(galarray['x'],starlen)
    gal_ycorr = make_gal_corrarray(galarray['y'],starlen)

    star_e1corr = make_star_corrarray(stararray['e1'],gallen)
    star_e2corr = make_star_corrarray(stararray['e2'],gallen)
    star_xcorr = make_star_corrarray(stararray['x'],gallen)
    star_ycorr = make_star_corrarray(stararray['y'],gallen)


    distcorr = numpy.sqrt((star_xcorr-gal_xcorr)*(star_xcorr-gal_xcorr)+ \
                          (star_ycorr-gal_ycorr)*(star_ycorr-gal_ycorr))

    xi_pp =  gal_g1corr*star_e1corr + gal_g2corr*star_e2corr

    #star autocorrelation
    emagarray=numpy.sqrt(stararray['e1']*stararray['e1']+stararray['e2']*stararray['e2'])
    emagautocorr=numpy.zeros((starlen*(starlen-1))/2)
    edistautocorr=numpy.zeros((starlen*(starlen-1))/2)
    
    iterator=0
    # I'm sure there's a better way to do this.
    for i in range(len(emagarray)):
        for j in range(i+1,len(emagarray)):
            emagautocorr[iterator]=emagarray[i]*emagarray[j]
            edistautocorr[iterator]=math.sqrt(((stararray['x'][i]-stararray['x'][j])*\
                                               (stararray['x'][i]-stararray['x'][j]))+\
                                              ((stararray['y'][i]-stararray['y'][j])*\
                                               (stararray['y'][i]-stararray['y'][j])))
            iterator=iterator + 1
    return xi_pp, distcorr, emagautocorr, edistautocorr
    
    

def  make_gal_corrarray( objarray, n ):
    m = len(objarray)
    a = numpy.array(numpy.zeros((n*m)))
    for k in range(n):
        a[k*m:(k+1)*m]=objarray
        
    return a

def  make_star_corrarray( objarray, n ):
    m = len(objarray)
    a = numpy.array(numpy.zeros((n*m)))
    for k in range(m):
        a[k*n:(k+1)*n]=objarray[k]
                    
    return a




def do_bootstrap_error(inputarray, nbootstraps=100):
    n = len(inputarray)
    npars=inputarray[numpy.random.random_integers(0,n-1,(n,nbootstraps))]
    meanlist = numpy.mean(npars,0)
    if len(meanlist) != nbootstraps:
        print 'averaging across wrong axis'

    return numpy.std(meanlist)



#
# switch to polar coordinates 
#
def cartesianToPolar(x, y):
    r = numpy.sqrt(x**2+y**2)
    phi = numpy.arccos(x/r)
    phi2 =  phi = 2. * numpy.pi - phi
    phi_yp = y>=0.
    phi2_yp = y<0.
    phi = phi* phi_yp +phi2*  phi2_yp

    return r, phi


#
# make the plots 
#
def make_scatter_inputs(yvals, xvals,therange, nbins=10):
    if len(yvals) != len(xvals):
        print  len(yvals), ' doeas not equal ',len(xvals) 
    
    vals, thebins = pylab.histogram(xvals, weights=yvals, bins=nbins,range=therange)
    vals_sq, thebins =  pylab.histogram(xvals, weights=yvals*yvals, bins=nbins ,range=therange)
    vals_n, thebins =  pylab.histogram(xvals, bins=nbins,range=therange)
    
    val_errs = numpy.sqrt((vals_sq/vals_n) - (vals/vals_n)*(vals/vals_n))/numpy.sqrt(vals_n) 

    bincenters=[]
    binerrs=[]
    # print 'The Bins = ', thebins
    for k in range(len(thebins)-1):
        bincenters.append((thebins[k]+thebins[k+1])/2.)
        binerrs.append((thebins[k+1]-thebins[k])/2.)
        
    # print 'bincenters = ',bincenters
    return bincenters, vals/vals_n, binerrs, val_errs


def get_percentiles(arr):
    # return 10 and 90 %iles
    sorted = numpy.sort(arr)
    n = len(sorted)
    val = n/10
    return sorted[val],sorted[n-val]
    


if __name__ == "__main__":
    
    filename_gal = sys.argv[1]
    filename_star = sys.argv[2]

    if len(sys.argv)==3:
        outfilename = 'psfplots.png'
    elif len(sys.argv)==4:
        outfilename = sys.argv[3]
    else:
        print 'usage: ./quality_studies_psf.py [galaxy_shear.cat] [star.cat] [output=psfplots.png]'
        sys.exit(1)
    galcat = open_and_get_shearcat(filename_gal,'OBJECTS')
    starcat = open_and_get_shearcat(filename_star,'OBJECTS')
    
    if galcat:
        print ' got Galaxy cat'
    if starcat:
        print ' got Star cat'


    maxrg=numpy.max(starcat['rg'])
    galcat = galcat.filter(galcat['rg']>maxrg)
    galcat = galcat.filter(galcat['Flag']==0)



    gal_g1arr = numpy.array(galcat['gs1'])
    gal_g2arr = numpy.array(galcat['gs2'])

    gal_xarr = numpy.array(galcat['x'])
    gal_yarr = numpy.array(galcat['y'])

    gal_e1corr = numpy.array(galcat['e1corrpol'])
    gal_e2corr = numpy.array(galcat['e2corrpol'])


    star_xarr =  numpy.array(starcat['x'])
    star_yarr =  numpy.array(starcat['y'])

    star_e1corr =  numpy.array(starcat['e1corrpol'])
    star_e2corr =  numpy.array(starcat['e2corrpol'])

    star_e1 =  numpy.array(starcat['e1'])
    star_e2 =  numpy.array(starcat['e2'])


    
    pylab.rc('text', usetex=True)
    pylab.figure(figsize=(15,10) ,facecolor='w')
    pylab.subplots_adjust(wspace=0.3,hspace=0.3)
    pylab.subplot(231,axisbg='w')
    pylab.cool()

    # Qualtest 1 : Average shear:
    avg_gs1 = numpy.mean(gal_g1arr)
    err_gs1 = numpy.std(gal_g1arr)/math.sqrt(len(gal_g1arr*1.0))
    err_gs1bs = do_bootstrap_error(gal_g1arr)
    
    avg_gs2 = numpy.mean(gal_g2arr)
    err_gs2 = numpy.std(gal_g2arr)/math.sqrt(len(gal_g2arr*1.0))
    err_gs2bs = do_bootstrap_error(gal_g2arr)

    pylab.errorbar(y=[avg_gs2,avg_gs2],x=[avg_gs1,avg_gs1],
                   xerr=[err_gs1,err_gs1bs], yerr=[err_gs2,err_gs2bs], fmt='r.',
                   label='''$<\gamma_{1,2}> $''')

    pylab.axis([-0.04,0.04,-0.04,0.04])
    pylab.xlabel('$<\gamma_{1}>$', horizontalalignment='right')
    pylab.ylabel('$<\gamma_{2}>$')
    pylab.legend(loc=0)
    pylab.grid()



    # Qualtest  2 : Average shear in aniso corr bins.
    # e1anisocorr : left over from correction
    # e1corrpol  : the correction.
    # the anisotropy polynomial values for all the objects.
    
    bincenters, gamma1vals, binerrs, gamma1errs = \
                make_scatter_inputs(gal_g1arr, gal_e1corr, (-0.02,0.03), 10)
    bincenters2, gamma2vals, binerrs2, gamma2errs = \
                 make_scatter_inputs(gal_g2arr, gal_e2corr, (-0.02,0.03), 10)

    pylab.subplot(232,axisbg='w')
    pylab.errorbar(x=bincenters,y=gamma1vals,yerr=gamma1errs,xerr=binerrs,
                   fmt='b.',label='''$<\gamma_{1}>$''')
    pylab.errorbar(x=bincenters2,y=gamma2vals,yerr=gamma2errs,xerr=binerrs2,
                   fmt='r.',label='$<\gamma_{2}>$')

    pylab.axis([-0.05,0.05,-0.2,0.2])
   
    pylab.xlabel('$e^{*pol}_{1,2}$', horizontalalignment='right')
    pylab.ylabel('''$<\gamma_{1,2}>$''')
    pylab.legend(loc=0)
    pylab.grid()


    # Qualtest 3 : <epol gamma>
    eg1,eg2, eg1err, eg2err, eg1errbs, eg2errbs = \
             avg_epol_gamma(gal_g1arr, gal_g2arr,  gal_e1corr, gal_e1corr)

    pylab.subplot(233)
    pylab.errorbar(x=[eg1, eg1],y=[eg2,eg2],
                   xerr=[eg1err,eg1errbs], yerr=[eg2err, eg2errbs], fmt='b.',
                   label='''$<e^{pol}_{1,2}\gamma_{1,2}>$ ''')
    pylab.cool()
    pylab.legend(loc=0)
    pylab.axis([-0.0004,0.0004,-0.0004,0.0004])
    pylab.xlabel('''$<e^{pol}_{1}\gamma_{1}>$ ''', horizontalalignment='right')
    pylab.ylabel('''$<e^{pol}_{2}\gamma_{2}>$ ''')
    pylab.grid()

    # Qualtest 5 : epol * g
    pylab.subplot(234)
    galarray={'x':gal_xarr, 'y':gal_yarr, 'g1':gal_g1arr, 'g2':gal_g2arr}
    stararray={'x':star_xarr,
               'y':star_yarr,
               'e1':star_e1,
               'e2':star_e2,
               'e1pol':star_e1corr,
               'e2pol':star_e2corr}

    xi_pp, distcorr,emagautocorr, edistautocorr  = \
           star_gal_correlation(galarray, stararray)

    xv, yv, xe, ye = make_scatter_inputs(xi_pp, distcorr,(0,10000), nbins=10 )

    pylab.errorbar(x=xv,y=yv,yerr=ye,xerr=xe,fmt='b.',label='data')


    #######################
    # Here we create the random star 
    # need e1 and e2 arrays
    # First Generate same ellipticity distribution
    #######################

    # |ellipticity| distribution
    elldist = numpy.sqrt(star_e1*star_e1+star_e2*star_e2)
    rxi_ppt=[]
    distcorrt=[]
    rxivals1 = [0,0,0,0,0,0,0,0,0,0]
    rxierrs1 = [0,0,0,0,0,0,0,0,0,0]
    
    rxivalssq1 = [0,0,0,0,0,0,0,0,0,0]
    rxivals1n = [0,0,0,0,0,0,0,0,0,0]
    
    
    ntrials=10
    rxivals1_sum = numpy.zeros(ntrials)
    rxierrs1_sum = numpy.zeros(ntrials)

    
    for isim in range(10):
        # for each trial, generate random numbers to sample from
        # the ellipticity distribution
        ellindex = numpy.random.random_integers(0,len(elldist)-1)

        # Set up the array
        rand_ell_arr = numpy.zeros(len(elldist))

        # fill the array, I think there's a fast way to do this...
        for i in range(len(elldist)):
            rand_ell_arr[i] = elldist[rand_ell_arr[i]]
            
        # now the random angle 0-pi
        rand_phi_arr = numpy.random.uniform(0,math.pi,len(elldist))

        # the e1 & e2 projections
        this_e1_arr = rand_ell_arr*numpy.cos(2.*rand_phi_arr)
        this_e2_arr = rand_ell_arr*numpy.sin(2.*rand_phi_arr)
    
        # set the random star array
        stararray={'x':star_xarr,
                   'y':star_yarr,
                   'e1':this_e1_arr, 
                   'e2':this_e2_arr, 
                   'e1pol':star_e1corr,
                   'e2pol':star_e2corr}
        
        # and correlate;        
        rxi_pp, distcorr, dum1, dum2 = star_gal_correlation(galarray, stararray)
        
        rxibins1, rxivals1[isim],rxibinserr1, rxierrs1[isim]=\
                  make_scatter_inputs(rxi_pp, distcorr,therange=(0,10000), nbins=10)

        for j in range(len(rxivals1[isim])):
            rxivals1_sum[j] = rxivals1_sum[j]+rxivals1[isim][j]
            rxierrs1_sum[j] = rxierrs1_sum[j]+rxierrs1[isim][j]
        # end loop
    #
    rxivals1_sum = rxivals1_sum/10.
    rxierrs1_sum = rxierrs1_sum/(10.*math.sqrt(10))

    pylab.errorbar(x=rxibins1,y=rxivals1_sum,yerr=rxierrs1_sum,xerr=rxibinserr1,\
                   fmt='g.',label='Random')
        
    ee_bincent,ee_vals,ee_binerrs, ee_errs =\
                                   make_scatter_inputs(emagautocorr, edistautocorr,\
                                                       (0,10000), nbins=10)
    
    pylab.errorbar(x=ee_bincent, y=ee_vals, yerr=ee_errs, xerr=ee_binerrs, \
                   fmt='r.', label='stars') 
    

    pylab.xlabel('''$\Delta x$ (pixels) ''', horizontalalignment='right')
    pylab.ylabel('''$<e^{*}_{+} \gamma_{+} +e^{*}_{x} \gamma_{x} >$''')
    pylab.cool()
    pylab.grid()
    pylab.legend(loc=0)


    xisys = (numpy.abs(yv)*(yv)/ee_vals)
    xisys_err = xisys * numpy.sqrt(4.*(ye/yv)*(ye/yv) + (ee_errs/ee_vals)*(ee_errs/ee_vals))
    
    pylab.subplot(235)
    pylab.errorbar(x= xv  ,y=xisys,\
                   yerr=xisys_err  ,xerr=ee_binerrs,fmt='b.',label='xi_p-data')


    pylab.xlabel('''$\Delta x$ (pixels)  ''', horizontalalignment='right')
    pylab.ylabel('''$ \zeta^{PSF}_{+}  $''')
    pylab.cool()
    pylab.grid()


    # Quality Check 6 Radial dependence
    rset, phiset = cartesianToPolar(gal_xarr-5000,gal_yarr-5000)

    g1_rotated = gal_g1arr*numpy.cos(-2.*phiset) +  gal_g2arr*numpy.sin(-2.*phiset)
    g2_rotated = gal_g1arr*numpy.sin( 2.*phiset) +  gal_g2arr*numpy.cos(-2.*phiset)

    e1pol_rotated = gal_e1corr*numpy.cos(-2.*phiset) +  gal_e2corr*numpy.sin(-2.*phiset)
    e2pol_rotated = gal_e1corr*numpy.sin( 2.*phiset) +  gal_e2corr*numpy.cos(-2.*phiset)
    
    rot_bins,rot_vals, rot_binerrs, rot_valerrs= \
                       make_scatter_inputs(g1_rotated*e1pol_rotated,rset ,(0,5000), 10)
    rot_bins2,rot_vals2, rot_binerrs2, rot_valerrs2= \
                         make_scatter_inputs(g2_rotated*e2pol_rotated,rset ,(0,5000), 10)

    pylab.subplot(236)
    pylab.errorbar(x=rot_bins, y=rot_vals, xerr=rot_binerrs, yerr=rot_valerrs, \
                   fmt='b.',label='$<e_{r}\gamma_{r}> (r)$' )
    pylab.errorbar(x=rot_bins2, y=rot_vals2, xerr=rot_binerrs2, yerr=rot_valerrs2, \
                   fmt='r.',label='$<e_{x}\gamma_{x}> (r)$' )
    pylab.xlabel('r (pixels)')
    pylab.ylabel('$<e^{pol} \gamma>$')
    pylab.grid()
    pylab.legend(loc=0)
    pylab.savefig(outfilename,format='png')
    pylab.show()
