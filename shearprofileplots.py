from shearprofile import *
from pylab import *



###########################################



def plotprofile(range, r, E, Eerr, B=None, Berr=None, plotlog=False, ct='b', cx='r'):

    print plotlog

    r_arc = pix2arcsec(r)

    if plotlog:
        r_arc = log(r_arc)
        Eerrup = log(E + Eerr) - log(E)
        Eerrdn = log(E) - log(E - Eerr)
        Eerr = row_stack([Eerrdn, Eerrup])
        E = log(E)
    

    if B is not None:
        subplot(2,1,1)

    print r_arc.shape, E.shape, Eerr.shape
    errorbar(r_arc, E, Eerr, fmt='%so' % ct)
    if not plotlog:
        axhline(0,c='k')
        axis([range[0]*pixelscale, range[1]*pixelscale, -.25, .25])
        xlabel('Radius (arcseconds)')
        ylabel('g_t')
    else:
        xlabel('log(Radius) [log(arcseconds)]')
        ylabel('log(g_t)')


    if B is not None:
        subplot(2,1,2)
        errorbar(r_arc, B, Berr, fmt='%so' % cx)
        axis([range[0]*pixelscale, range[1]*pixelscale, -.15, .15])
        axhline(0,c='k')
        xlabel('Radius (arcseconds)')
        ylabel('g_x')

#########################################


def plotBestFit(mcmc, r, z, D_A, beta, angularscale):

    bestfit = mcmc.ll == min(mcmc.ll)
    plot(pix2arcsec(r), NFWShear(pix2mpc(r, angularscale), mcmc.c[bestfit][0], mcmc.rs[bestfit][0], z, D_A, beta), 'r-')
    


def easyplotprofile(cat, range, bins=30, center=(6000,6000), logbin = False, **keywords):

    profile = easyprofile(cat, range, bins, center, logbin = logbin)
    plotprofile(range, profile.r, profile.E, profile.Eerr, plotlog=False, **keywords )

def easyplotprofile2(cat, range, bins=30, center=(6000,6000), logbin=True, **keywords):

        profile = easyprofile(cat, range, bins, center, logbin = logbin)
        plotprofile(range, profile.r, profile.E, profile.Eerr, profile.B, profile.Berr, **keywords )

###############################################################
