import scipy, os

p = scipy.loadtxt('BVRI.bpz')

import pylab, os
params = {'backend' : 'ps',
     'text.usetex' : True,
      'ps.usedistiller' : 'xpdf',
      'ps.distiller.res' : 6000}
pylab.rcParams.update(params)
                                       
fig_size = [8.5,3]
params = {'axes.labelsize' : 20,
          'text.fontsize' : 22,
          'legend.fontsize' : 22,
          'xtick.labelsize' : 20,
          'ytick.labelsize' : 20,
          'scatter.s' : 0.1,
            'scatter.marker': 'o',
          'figure.figsize' : fig_size}
pylab.rcParams.update(params)









z_best = p[:,1]
z_spec = p[:,9]

z_best = z_best[z_spec > -9]
z_spec = z_spec[z_spec > -9]

pylab.scatter(z_spec, z_best, s=3, marker='o', c='black')

pylab.plot(scipy.array([0,4]),scipy.array([0,4]),color='red')
pylab.axis([0,1.5,0,1.5])
pylab.ylabel("Photometric z")
pylab.xlabel("Spectroscopic z")

pylab.savefig(os.environ['sne'] + '/photoz/papfigs/best_spec_BVRI.pdf')
