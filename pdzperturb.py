######################
# Calculate how sensitive masses, and the mean sample mass, are to pertubations in the P(z)
#######################


import numpy as np, scipy.integrate as integrate, scipy.optimize
import nfwutils, stats, nfwmodeltools, pdzperturbtools


#####################



def createNLikelihood(mcluster, zcluster, z0, sigz0, rmin=0.75, rmax=3.0, c=4.0, massrad = 1.5, gsig = 0.25, npoints = 200000):

    rs = nfwutils.RsMassInsideR(mcluster, c, zcluster, massrad)

    linmin = rmin / np.sqrt(2)
    linmax = rmax / np.sqrt(2)
    r_points = np.sqrt(np.random.uniform(linmin, linmax, size=npoints)**2 + np.random.uniform(linmin, linmax, size=npoints)**2)

    z_points = z0 + sigz0*np.random.standard_normal(npoints)    


    gamma_inf = nfwmodeltools.NFWShear(r_points, c, rs, zcluster)
    kappa_inf = nfwmodeltools.NFWKappa(r_points, c, rs, zcluster)
    beta_s = nfwutils.beta_s(z_points, zcluster)

    g0 = beta_s*gamma_inf/(1 - beta_s*kappa_inf)

    ghat_points = g0 + gsig*np.random.standard_normal(npoints)


    dzt = 0.01
    pdzrange = np.arange(z0 - 5*sigz0, z0+5*sigz0, dzt)
    pdz = stats.Gaussian(pdzrange, z0, sigz0)*dzt

    betas = np.array(nfwutils.beta_s(pdzrange, zcluster))


    def nloglike(Mguess):
        #units of 1e14
        Mguess = Mguess*1e14

        rs_guess = nfwutils.RsMassInsideR(Mguess, c, zcluster, massrad)

        return -pdzperturbtools.nloglike_loop(r_points, z_points, ghat_points, betas, pdz, gsig, 
                                             rs_guess, c, zcluster)


    return nloglike
            

        



#####################


def calcBestMass(nloglike):

    bestmass = scipy.optimize.fminbound(nloglike, 1., 15.)

    return bestmass*1e14

######################


def calcMassWeight(likelihood):

    pass


######################


