#######################
# Publication quality plots
#######################


import pylab
import numpy as np
import nfwutils, ldac


golden_mean = (np.sqrt(5) - 1)/2.0
screen_ratio = 0.75
fig_width = 6
fig_height = fig_width*screen_ratio
fig_size = [fig_width,fig_height]


params = {'backend' : 'ps',
         'text.usetex' : True,
          'ps.usedistiller' : 'xpdf',
          'ps.distiller.res' : 6000,
          'axes.labelsize' : 16,
          'text.fontsize' : 16,
          'legend.fontsize' : 14,
          'xtick.labelsize' : 14,
          'ytick.labelsize' : 14,
          'figure.figsize' : fig_size}
pylab.rcParams.update(params)


#################################

def betasplot():

    fig = pylab.figure()
    xmarg = 0.11
    ymarg = 0.15
    ax = pylab.axes([xmarg, ymarg, 0.95 - xmarg, 0.95 - ymarg])
    
    z = np.arange(0, 2.5, 0.002)
    
    pylab.plot(z, nfwutils.beta_s(z, 0.2), label=r'$Z_c = 0.2$')
    pylab.plot(z, nfwutils.beta_s(z, 0.5), label=r'$Z_c = 0.5$')
    pylab.plot(z, nfwutils.beta_s(z, 0.7), label=r'$Z_c = 0.7$')
    pylab.legend(loc='lower right', numpoints = 1)
    pylab.xlabel(r'$Z_b$ : Source Galaxy Redshift')
    pylab.ylabel(r'$\beta_s(Z_b; Z_c)$')


    return fig

##################################

def colorCutBias():

    fig = pylab.figure()
    xmarg = 0.12
    ymarg = 0.12
    ax = pylab.axes([xmarg, ymarg, 0.95 - xmarg, 0.95 - ymarg])


    cosmos = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/simulations/publication/highsn/APER/bpz.cat', 'STDTAB')

    
    zclusters = np.arange(0.2, 0.8, 0.05)

    beta_true = np.array([np.mean(nfwutils.beta_s(cosmos['BPZ_Z_S'], z)) \
                              for z in zclusters])
    beta_measure = np.array([np.mean(nfwutils.beta_s(cosmos['BPZ_Z_B'], z)) \
                              for z in zclusters])

    pylab.plot(zclusters, beta_measure / beta_true, 'b-', label='Limited Filters', linewidth=1.25)


    bpz = ldac.openObjectFile('/u/ki/dapple/orange/cats_2011-09-08/MACS0018+16.W-J-V.bpz.tab', 'STDTAB')
    night1 = ldac.openObjectFile('/u/ki/dapple/orange/cats_2011-09-08/MACS0018+16.W-J-V.gabodsid1728.cut_lensing.cat')
    night2 = ldac.openObjectFile('/u/ki/dapple/orange/cats_2011-09-08/MACS0018+16.W-J-V.gabodsid1729.cut_lensing.cat')
    bpz1 = bpz.matchById(night1)
    bpz2 = bpz.matchById(night2)

    aveBeta1 = np.array([np.mean(nfwutils.beta_s(bpz1['BPZ_Z_B'], x)) \
                          for x in zclusters])
    aveBeta2 = np.array([np.mean(nfwutils.beta_s(bpz2['BPZ_Z_B'], x)) \
                          for x in zclusters])

    pylab.plot(zclusters, aveBeta2 / aveBeta1, 'r-', label='Different Seeing', linewidth=1.25)

    rhcut = night1['rh'] > np.min(night2['rh'])

    bpz1a = bpz1.filter(rhcut)
    aveBeta1a = np.array([np.mean(nfwutils.beta_s(bpz1a['BPZ_Z_B'], x)) \
                              for x in zclusters])
    pylab.plot(zclusters, aveBeta2 / aveBeta1a, 'r-.', linewidth=1.25)
    

    pylab.axhline(1.0, c='k', linewidth=1.5)

    

    pylab.grid()
    pylab.axis([0.15, 0.85, 0.95, 1.24])
    pylab.xlabel('Cluster Redshift')
    pylab.ylabel(r'$<\beta_{measured}> / <\beta_{true}>$')
    pylab.legend(loc='best')

    return fig
