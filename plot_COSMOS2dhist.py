
def plot_hist(diff, web):

    import pylab
    from scipy import arange

    pylab.clf()

    pylab.axes([0.125,0.15,0.95-0.125,0.95-0.15])

    a, b, varp = pylab.hist(diff,bins=arange(-0.2,0.2,0.015),color='blue',edgecolor='black')
    #varps.append(varp[0])
    
    diffB = []
    for d in diff:
        if abs(d) < 0.1:
            diffB.append(d)
    diff = diffB
    list = scipy.array(diff)
    mu = list.mean()
    sigma = list.std()
    
    from scipy import stats
    pdf_x = arange(-0.2,0.2,0.005)
    pdf = scipy.stats.norm.pdf(pdf_x, mu, sigma)
    
    height = scipy.array(a).max()
    
    pylab.plot(pdf_x,3*len(diff)*pdf/pdf.sum(),color='red')
                                                                                                                     
    print b,len(diff)*pdf/pdf.sum()
    
    pylab.xlabel(r"(z$_{phot}$ - z$_{spec}$)/(1 + z$_{spec}$)")
    pylab.ylabel("Galaxies")
                                                                                                                     
    pylab.figtext(0.76,0.89,'$\mu_{\Delta z}$=%.3f' % mu, fontsize=20)
    pylab.figtext(0.76,0.85,'$\sigma_{\Delta z}$=%.3f' % sigma, fontsize=20)
    
    #os.system('mkdir -p ' + outbase + '/' + SPECTRA)
                                                                                                                     
    from datetime import datetime
    t2 = datetime.now()
                                                                                                                     
    pylab.figtext(0.16,0.89,'COSMOS-30',fontsize=20)
    pylab.savefig(web + '/RedshiftErrors.png')
    pylab.savefig(web + 'RedshiftErrors.ps')
    pylab.savefig(web+ 'RedshiftErrors.pdf')


import pyfits, os, scipy

set = 'CWWSB_capak'
web = os.environ['sne'] + '/photoz/COSMOS' + set + '/'

print 'reading in catalogs'
C = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_aper/cosmos_lephare.cat')['OBJECTS'].data
U = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_BVRIZ/COSMOS_PHOTOZ.APER.1.CWWSB_capak.list.all.bpz.tab')['STDTAB'].data

print 'doing other things'

#U = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_aper/COSMOS_PHOTOZ.APER.1.CWWSB_txitxo.list.all.bpz.tab')['STDTAB'].data

#mask = (U.field('BPZ_ODDS') > 0.95) * (U.field('BPZ_Z_B') > 0) * (U.field('BPZ_M_0') < 25) * (U.field('NFILT') == 6) * (C.field('zp_best') > 0)

mask = (U.field('BPZ_ODDS') > 0.95) * (U.field('BPZ_Z_B') > 0) *(U.field('BPZ_Z_B') < 1.2) * (U.field('BPZ_M_0') < 25) * (U.field('NFILT') == 5) * (C.field('zp_best') > 0)

C = C[mask]
U = U[mask]



xbins = scipy.arange(0,1.5,0.015)
ybins = scipy.arange(0,1.5,0.015)

prob_matrix,X,Y = scipy.histogram2d(U.field('BPZ_Z_B')-0*scipy.ones(len(U.field('BPZ_Z_B'))),C.field('zp_best'),bins=[xbins,ybins])

prob_matrix = prob_matrix / prob_matrix.max()

import pylab
#X, Y = pylab.meshgrid(zs_copy,zs_copy)
                                                                                          
print prob_matrix.shape, X.shape, Y.shape
                                                                                          
                                                                                          


import pylab

pylab.rcdefaults()
params = {'backend' : 'ps',
     'text.usetex' : True,
      'ps.usedistiller' : 'xpdf',
      'ps.distiller.res' : 6000}
pylab.rcParams.update(params)
                                       

fig_size = [8,8]
                                       

params = {'axes.labelsize' : 20,
          'text.fontsize' : 22,
          'legend.fontsize' : 22,
          'xtick.labelsize' : 20,
          'ytick.labelsize' : 20,
          'scatter.s' : 0.1,
            'scatter.marker': 'o',
          'figure.figsize' : fig_size}
pylab.rcParams.update(params)


pylab.clf()


print prob_matrix.max()
                                                                                          
prob_matrix[prob_matrix>1] =1. 


#pylab.axes([0.125,0.125,0.95-0.125,0.95-0.125])
#pylab.axes([0.125,0.25,0.95-0.125,0.95-0.25])



pylab.axes([0.125,0.15,0.95-0.125,0.95-0.15])
#pylab.axes([0.225,0.15,0.95-0.225,0.95-0.15])
pylab.axis([0,1.5,0,1.5])

pylab.pcolor(X, Y,-1.*prob_matrix,cmap='gray',alpha=0.9,shading='flat',edgecolors='None')

pylab.axhline(y=1.2,color='black')                                                                                          
pylab.plot(scipy.array([0,2]),scipy.array([0,2]),color='black')

pylab.xlabel('COSMOS-30 Redshift')
pylab.ylabel('UBVriz Redshift')
#pylab.plot([0,1],[0,1],color='red')
#pylab.xlabel('SpecZ')
#pylab.ylabel('PhotZ')


pylab.savefig(web + '2dhistCOSMOS.png') #,figsize=fig_size)
pylab.savefig(web + '2dhistCOSMOS.pdf') #,figsize=fig_size)

diff = U.field('BPZ_Z_B')-C.field('zp_best')

plot_hist(diff, web)

