#! /usr/bin/env python
from matplotlib.pylab import *
import astropy.io.fits as pyfits
import ldac
pfl='/gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/PHOTOMETRY/panstarrsstar.cat'
sfl='/gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/PHOTOMETRY/sdssstar.cat'

pfo=pyfits.open(pfl)
sfo=pyfits.open(sfl)
scat=ldac.LDACCat(sfo[1])
pcat=ldac.LDACCat(pfo[1])

for k in scat.keys():
    if k.endswith('mag'): 
        print 'sdss',k,scat[k].min(),scat[k][scat[k]>0].mean(),scat[k].max()
        print 'pans',k,pcat[k].min(),pcat[k][pcat[k]>0].mean(),pcat[k].max()

from astropy.coordinates import SkyCoord
from astropy import units as u
sdss = SkyCoord(ra=scat['Ra']*u.degree, dec=scat['Dec']*u.degree)
pans = SkyCoord(ra=pcat['Ra']*u.degree, dec=pcat['Dec']*u.degree)

idx, d2d, d3d = pans.match_to_catalog_sky(sdss)

def match_range(matchmin=0.0,matchmax=0.8,pancat=pcat,sdsscat=scat):
    match_array=(matchmin<d2d.arcsec)*(d2d.arcsec<matchmax)
    mpancat=pancat.filter(match_array)
    plot(mpancat['Ra'],mpancat['Dec'],'bo',label='panstarrs')
    midx=idx[match_array]
    msdsscat=sdsscat.filter(midx)
    plot(msdsscat['Ra'],msdsscat['Dec'],'rx',label='sdss')
    show()

def match_range(matchmin=0.0,matchmax=0.8,pancat=pans,sdsscat=sdss):
    match_array=(matchmin<d2d.arcsec)*(d2d.arcsec<matchmax)
    mpancat=pancat[match_array]
    plot(mpancat.ra.deg,mpancat.dec.deg,'bo',label='panstarrs')
    midx=idx[match_array]
    msdsscat=sdsscat[midx]
    plot(msdsscat.ra.deg,msdsscat.dec.deg,'rx',label='sdss')
    show()

# match_range(matchmin=0.0,matchmax=2.0)
matchmin=0.0
matchmax=2.0
match_array=(matchmin<d2d.arcsec)*(d2d.arcsec<matchmax)
mpancat=pcat.filter(match_array)
#plot(mpancat['Ra'],mpancat['Dec'],'bo',label='panstarrs')
midx=idx[match_array]
msdsscat=scat.filter(midx)
#plot(msdsscat['Ra'],msdsscat['Dec'],'rx',label='sdss')


keys2plot=[ 'gmag', 'rmag', 'imag', 'Bmag', 'Vmag', 'Rmag', 'Imag', 'zmag', 'gerr', 'rerr', 'ierr', 'Berr', 'Verr', 'Rerr', 'Ierr', 'zerr', 'gmr', 'rmi', 'imz', 'BmV', 'VmR', 'RmI', 'Imz', 'gmrerr', 'rmierr', 'imzerr', 'BmVerr', 'VmRerr', 'RmIerr', 'Imzerr']
shortkeys=[k for k in keys2plot if not k.endswith('err')]

ion()

f=figure()
magkeys2plot=[ 'gmag', 'rmag', 'imag', 'Bmag', 'Vmag', 'Rmag', 'Imag', 'zmag' ]
for index,k in enumerate(magkeys2plot):
    ax=f.add_subplot(3,3,index+1)
    linesk=plot(msdsscat[k],mpancat[k],'.',label=k)
    title(k)
    ax.set_xlim(14,24)
    ax.set_ylim(14,24)
    grid()
f.set_tight_layout(True)
f.suptitle('X axis=SDSS and Y axis=PANSTARRS')
f.savefig('plt_mags_panstarrs_sdss_compare')
show()
sys.exit()

import config_bonn
import utilities
from my_cluster_params import ic_cldata,clusters_refcats
OBJNAME='MACS1226+21'
OBJNAME='RXJ2129'
FILTERs,FILTERs_matching_PPRUNs,PPRUNs=ic_cldata[OBJNAME]['FILTERs'],ic_cldata[OBJNAME]['FILTERs_matching_PPRUNs'],ic_cldata[OBJNAME]['PPRUNs']
fig=figure(figsize=(9,12))
for index,f in enumerate(FILTERs):
    other_info = config_bonn.info[f]
    filters_info = utilities.make_filters_info([f])
    compband = filters_info[0][1]
    color1 = other_info['color1']
    print f+'|  color1=', color1,' compband=',compband
    k=compband+'mag'
    sdssmag,pansmag=msdsscat[k],mpancat[k]
    magfilt=logical_and(0<sdssmag,0<pansmag)*logical_and(40>sdssmag,40>pansmag)
    k=color1
    fig=figure(figsize=(9,12))
    ax=fig.add_subplot(1,1,1)
    #ax=fig.add_subplot(3,2,index+1)
    linesk=plot(msdsscat[k][magfilt],mpancat[k][magfilt],'.',label=k)
    title('plotting color='+k+' within mag range: 0<'+f+'<40 | X axis=SDSS and Y axis=PANSTARRS')
    plot([-.5,2],[-.5,2],'k--')
    ax.set_xlim(-.5,2)
    ax.set_ylim(-.5,2)
    grid()
    fig.set_tight_layout(True)

for index,f in enumerate(FILTERs):
    other_info = config_bonn.info[f]
    filters_info = utilities.make_filters_info([f])
    compband = filters_info[0][1]
    color1 = other_info['color1']
    print f+'|  color1=', color1,' compband=',compband
    k=compband+'mag'
    sdssmag,pansmag=msdsscat[k],mpancat[k]
    magfilt=logical_and(0<sdssmag,0<pansmag)*logical_and(40>sdssmag,40>pansmag)
    k=color1
    Scolor,Pcolor=msdsscat[color1][magfilt],mpancat[color1][magfilt]

print "msdsscat and mpancat"

s=msdsscat
p=mpancat
clip=logical_and(0<s['zmag'],s['zmag']<40)*logical_and(p['zmag']>0,40>p['zmag'])
s=msdsscat.filter(clip)
p=mpancat.filter(clip)

zoff=s['zmag']-p['zmag']

f=figure()
ax1=f.add_subplot(221)
plot(s['Ra'], zoff,'k.')
title('(Zmag SDSS - Zmag PANS) vs. Ra')
ax2=f.add_subplot(222)
title('(Zmag SDSS - Zmag PANS) vs. Dec')
plot(s['Dec'], zoff,'k.')
ax3=f.add_subplot(223)
hist2d(s['ra'], s['Dec'],bins=100,weights=zoff)
colorbar()
#zoff=
title('(Zmag SDSS - Zmag PANS) in 2D bins')
ax4=f.add_subplot(224)
title('histogram (Zmag SDSS - Zmag PANS)')
hist(zoff,bins=20)
show()


