#adam: this is an older version of shearprofile.py from ~/wtgpipeline, which probably won't be needed anymore, but should be saved anyway
from numpy import *
from scipy.optimize import brenth
from scipy.optimize import fsolve
from scipy.integrate import quad
from readtxtfile  import readtxtfile
#import leastsq, fitmodel

pixelscale = .2 #arcsec / pixel

v_c = 299792.458 #km/s
Omega_m = .3
Omega_l = .7
h = .7
H0 = 100*h #km/s/Mpc
hubble_length = v_c/H0
rho_c0 = 2.775e11 * h**2 # M_sol Mpc^-3

G=4.3e-9 # Newton's const   in Mpc (km/s)^2 M_sol^{-1}

class Profile(object):
    def __init__(self, r, E, Eerr, B, Berr, n):
        self.r = r
        self.E = E
        self.Eerr = Eerr
        self.B = B
        self.Berr = Berr
        self.n = n

##################################################

def bootstrapshearprofile(x,y,e1,e2,sigma2,range,bins=30,center=(5000,5000),
                          wcs=False, logbin=False):

    profiles = [ shearprofile(x,y,e1,e2,sigma2,range,bins,center,wcs,logbin) ]

    nelements = len(x)
    for i in xrange(1000):
        asample = random.randint(0,nelements,nelements)
        profiles.append(shearprofile(x[asample], y[asample],e1[asample],e2[asample],sigma2[asample],range,bins,center,wcs,logbin))

    E = []
    Eerr = [[],[]]
    B = []
    Berr = [[],[]]
    for i in xrange(len(profiles[0].r)):

        Es = [profile.E[i] for profile in profiles]

        E_cr = ConfidenceRegion(Es)

        E.append(float(E_cr[0][0]))

        Eerr[0].append(float(E_cr[1][0]))
        Eerr[1].append(float(E_cr[2][0]))
        

        Bs = [profile.B[i] for profile in profiles]

        B_cr = ConfidenceRegion(Bs)

        B.append(float(B_cr[0][0]))
        
        Berr[0].append(float(B_cr[1][0]))
        Berr[1].append(float(B_cr[2][0]))

    return Profile(profiles[0].r, array(E), array(Eerr), array(B), array(Berr), profiles[0].n)
        
        

def shearprofile(x,y,e1,e2,sigma2,range,bins=30,center=(6000,6000),
                 wcs = False,  logbin=False):

    errors = (sigma2 is not None)

    xrel = x - center[0]
    if (wcs):
        xrel = xrel*cos(y*M_PI/360.)

    yrel = y - center[1]
    dr = sqrt(xrel**2 + yrel**2)
    
    #range in pixels or arcseconds
    
    rmin,rmax = range
    if logbin:
        dr = log(dr)
        rmin = log(rmin)
        rmax = log(rmax)

        leftedges, binwidth = linspace(rmin, rmax, bins+1, endpoint=True, retstep=True)

        rbin = exp(leftedges)

        rbin = (rbin[1:] + rbin[:-1])/2.


    else:
        leftedges, binwidth = linspace(rmin, rmax, bins, endpoint=False, retstep=True)
        rbin = leftedges + binwidth/2.


    # Set up binning grid:
    

    Ebin = zeros(bins, dtype=float64)
    Ebinerr = zeros(bins, dtype=float64)
    Bbin = zeros(bins)
    Bbinerr = zeros(bins)
    nbin = zeros(bins)

    index = ((dr - rmin) / binwidth).astype(int)
    
    goodentry = logical_and(index >= 0, index < bins)

    

    phi = arctan2(yrel, xrel)
    cos2phi = cos(2*phi)
    sin2phi = sin(2*phi)

    E = -(e1*cos2phi+e2*sin2phi)
    
    b1 =  e2
    b2 = -e1
    B = -(b1*cos2phi+b2*sin2phi)
  

    # Calculate tangential shear and add it to the (weighted) sum:     
    nentries = len(x)
    if errors:
        w = 1.0/sigma2;
        for cur in xrange(nentries):
            i = index[cur]
            if goodentry[cur]:
                nbin[i] += 1
                Ebin[i] += E[cur]*w[cur]
                Ebinerr[i] += w[cur] 
                Bbin[i] += B[cur]*w[cur]
                Bbinerr[i] += w[cur]

    else:
        for cur in xrange(nentries):
            i = index[cur]
            if goodentry[cur]:
                nbin[i] += 1 
                Ebin[i] += E[cur]
                Ebinerr[i] += E[cur]*E[cur]
                Bbin[i] += B[cur] 
                Bbinerr[i] += B[cur]*B[cur]


           

# Now work out averages and errors and finish!

    if errors:
        Ebin = Ebin / Ebinerr
        Ebinerr = sqrt(1. / Ebinerr)
        Bbin = Bbin / Bbinerr
        Bbinerr = sqrt(1. / Bbinerr)
    else:
        Ebin = Ebin / nbin
        Ebinerr = sqrt(Ebinerr / nbin - Ebin*Ebin)
        Ebinerr = Ebinerr / sqrt(nbin - 1.0)
        Bbin = Bbin / nbin
        Bbinerr = sqrt(Bbinerr / nbin - Bbin*Bbin)
        Bbinerr = Bbinerr / sqrt(nbin - 1.0)


    return Profile(rbin, Ebin, Ebinerr, Bbin, Bbinerr, nbin)

############################################################


def easyprofile(cat, range, bins=30, center=(6000,6000), logbin=True):
    return shearprofile(cat['Xpos'], cat['Ypos'], 
                        cat['gs1'], cat['gs2'], 
                        cat['sigma2_gs'], 
                        range, bins, center, wcs = False, logbin = logbin)

def easybootstrap(cat, range, bins=30, center=(5000,5000), logbin=False):
    return bootstrapshearprofile(cat['Xpos'], cat['Ypos'], 
                                 cat['gs1'], cat['gs2'], 
                                 cat['sigma2_gs'], 
                                 range, bins, center, wcs = False, logbin = logbin)


def pix2arcsec(r):

    return pixelscale*r

def pix2mpc(r, angularscale):
    
    return pix2arcsec(r)*angularscale / 1000

def mpc2pix(r, angularscale):
    
    return 1000 * r / (angularscale * pixelscale)

#################################################


def MCMCDatafile(r, E, Err, angularscale, file):
    r_mpc = pix2mpc(r, angularscale)
    output = open(file, 'w')
    for i in xrange(len(r)):
        output.write("%f  %f  %f\n" % (r_mpc[i], E[i], Err[i]))

    output.close()

def MCMC_ML_Datafile(r, E, Err, beta, angularscale, file):
    r_mpc = r * angularscale / 1000
    output = open(file, 'w')
    for i in xrange(len(r)):
        output.write("%f  %f  %f %f\n" % (r_mpc[i], E[i], Err[i], beta[i]))

    output.close()

class MCMC(object):
    def __init__(self, c, rs, ll,m):
        self.c =c
        self.rs = rs
        self.ll = ll
        self.m = m
    def __len__(self):
        return len(self.c)
    def drop(self, num):
        self.c = self.c[num:]
        self.rs = self.rs[num:]
        self.ll = self.ll[num:]

def readMCMC(file):
    data = readtxtfile(file)
    c = []
    rs = []
    ll = []
    m = []
    for i in xrange(len(data)):
        for j in xrange(int(data[i,0])):
            ll.append(data[i,1])
            c.append(data[i, 2])
            rs.append(data[i,3])
            m.append(data[i,4])
            
    return MCMC(array(c), array(rs),array(ll),array(m))


def AdamMass(cc, rs, rmax, z):
         
    Hz=H(z)
    Hz2=Hz**2;
    
    delta=200.0/3*cc**3/(log(1+cc) - cc/(1+cc))

    rhoc = rhoC(z)


    x=rmax/rs

    return 4*pi*rs**3*delta*rhoc*(log(1+x)-x/(1+x))



def ConfidenceRegion(dist, interval = .68, bins = 50, range = None, useLog = False, useMedian = False):

    if useLog:
        counts, left_edges = histogram(log(dist), bins, range)
    else:
        counts, left_edges = histogram(dist, bins, range)
    counts = counts[:-1]
    left_edges = left_edges[:-1]

    center = left_edges + (left_edges[1] - left_edges[0])/2.


    total_objs = sum(counts)
    
    if useMedian:
        maxl = median(dist)
        
    else:
        
        step = 1
        threshold = max(counts)
        maxl = center[counts == threshold]
        if useLog:
            maxl = exp(maxl)

        try:
            maxl = mean(maxl)
        except:
            pass

    x = sort(dist)
    
    # Initialize interval
    min_int = [None,None]
    
    try:
        
        # Number of elements in trace
        n = len(x)
        
        # Start at far left
        start, end = 0, int(n*interval)
        hi, lo = x[end], x[start]
        
        # Initialize minimum width to large value
        min_width = inf


        while end < n and lo <= maxl:



            # Endpoints of interval
            hi, lo = x[end], x[start]
            
            if lo <= maxl <= hi:
        
                # Width of interval
                width = hi - lo
            
                # Check to see if width is narrower than minimum
                if width < min_width:
                    min_width = width
                    min_int = [lo, hi]
            
            # Increment endpoints
            start +=1
            end += 1
        

    
    except IndexError:
        print 'Too few elements for interval calculation'
        raise IndexError
    
    err = array([maxl - min_int[0], min_int[1] - maxl])

    return maxl, err


def ConfidenceRegionFromPDF(xsamples, pdf, interval = .68, step=1):
    #assumes pdf is sampled at even spaces

    assert((pdf > 0).all())

    maxl = xsamples[pdf == max(pdf)]
    threshold = max(pdf)

    total = pdf.sum()
    
    contained = 0.
    while (contained < interval*total):
        threshold = threshold - step
        contained = pdf[pdf >= threshold].sum()

    left = min(xsamples[pdf >= threshold])
    right = max(xsamples[pdf >= threshold])

    return (maxl, maxl - left, right - maxl)


def NFWIntegratedMass(c, r_s, rmax, z):

    rho_c = rhoC(z)

    def wrapper(x):
        return NFWDensity(x, c, r_s, rho_c)*x**2

    y, abserr = quad(wrapper, 0, rmax, limit=1000)
    return  4*pi*y



def NFWShear(r, c, rs, z, D_lens):

    rho_c_over_sigma_c = 15000*(h**2) * D_lens * beta([1e6], z) * (Omega_m*(1+z)**3 + Omega_l) / v_c**2
    
    delta_c = deltaC(c)
    amp = rs*delta_c*rho_c_over_sigma_c

    x = (r/rs).astype(float64)

    g = zeros(r.shape, dtype=float64)

    xless = x[x < 1]
    a = arctanh(sqrt((1-xless)/(1+xless)))
    b = sqrt(1-xless**2)
    c = (xless**2) - 1
    
    g[x<1] = 8*a/(b*xless**2) + 4*log(xless/2)/xless**2 - 2/c + 4*a/(b*c)

    xgre = x[x>1]
    a = arctan(sqrt((xgre-1)/(1+xgre)))
    b = sqrt(xgre**2-1)
    
    g[x>1] = 8*a/(b*xgre**2) + 4*log(xgre/2)/xgre**2 - 2/b**2 + 4*a/b**3

    g[x == 1] = 10./3 + 4*log(.5)

    return amp*g

def NFWKappa(r, c, rs, z, D_lens):

  rho_c_over_sigma_c = 15000*(h**2) * D_lens * beta([1e6],z) * (Omega_m*(1+z)**3 + Omega_l) / v_c**2
  
  delta_c = deltaC(c)
  amp = 2*rs*delta_c*rho_c_over_sigma_c
  
  x = (r/rs).astype(float64)

  kappa = zeros(r.shape, dtype=float64)
    
  xless = x[x<1]
  a = arctanh(sqrt((1-xless)/(1+xless)))
  b = sqrt(1-xless**2)
  c = 1./(xless**2 - 1)
  kappa[x<1] = c*(1 - 2.*a/b)

  xgre = x[x>1]
  a = arctan(sqrt((xgre-1)/(1+xgre)))
  b = sqrt(xgre**2-1)
  c = 1./(xgre**2 - 1)
  kappa[x>1] = c*(1 - 2.*a/b)

  kappa[x == 1] = 1./3.;


  return kappa*amp;

2
######################################


def NFW_ML(r, rs, clusterz, D_lens, beta_s, beta_s2, c = 4., stepcor = 1.):

    nfw_shear = beta_s*NFWShear(r, c, rs, clusterz, D_lens)
    nfw_kappa = beta_s*NFWKappa(r, c, rs, clusterz, D_lens)

    g = (1 + (beta_s2 / beta_s**2 - 1)*nfw_kappa)*nfw_shear/(1 - nfw_kappa)
#    g[abs(g) > 1] = 1/g[abs(g) > 1]

    g = g / stepcor

    return g

###

class NFW_ML_Fit(object):

    def __init__(self, clusterz, c, stepcor, beta_s, beta_s2):
        self.clusterz = clusterz
        self.c = c
        self.Dl = angulardist(self.clusterz)
        self.stepcor = stepcor
        self.beta_s = beta_s
        self.beta_s2 = beta_s2

    def __call__(self, x, rs):

        return NFW_ML(x, rs, self.clusterz, self.Dl, self.beta_s, self.beta_s2, 
                      self.c, self.stepcor)

###

def runNFW_ML(r, g, gerr, beta_s, beta_s2, clusterz, c = 4., stepcor = 1., guess = 1.0):

    nfw_ml = NFW_ML_Fit(clusterz, c, stepcor, beta_s, beta_s2)

    print g, gerr

    rs, isCon = leastsq.leastsq(nfw_ml, [guess], r, g, gerr, fullOutput=False)    

    if not isCon:
        return None

    return rs

 #   fit = fitmodel.FitModel(r, g, gerr, nfw_ml, fitmodel.ChiSqStat, guess = [guess])
 #   fit.fit()
 #   if fit.have_fit:
 #       return fit.par_vals['rs']
 #   else:
 #       return None

    


#####################################################

def calcTangentialShear(cat, center, pixscale, xcol='Xpos', ycol='Ypos', 
                        g1col='gs1', g2col='gs2'):

    center = array(center)
    positions = column_stack([cat[xcol], cat[ycol]])
    dX = positions - center

    delta = sqrt(dX[:,0]**2 + dX[:,1]**2)

    r = delta*pixscale

    phi = arctan2(dX[:,1], dX[:,0])
    cos2phi = cos(2*phi)
    sin2phi = sin(2*phi)

    e1 = cat[g1col]
    e2 = cat[g2col]

    E = -(e1*cos2phi+e2*sin2phi)

    b1 =  e2
    b2 = -e1
    B = -(b1*cos2phi+b2*sin2phi)

    

    return r, E, B


############################

def calcWLViolationCut(r, beta, sigma_v = 1300, kappathresh = .1):

    #r in arcseconds

    X = pi/(3600*180)  #convert arcseconds to radians

    kappa = 2*pi*beta*(sigma_v**2)/((v_c**2)*r*X)

    return kappa < kappathresh

############################


#r in arcseconds below

class SISShearFit(object):
    def __init__(self, beta, beta2, stepcor):
        self.beta = beta
        self.beta2 = beta2
        self.stepcor = stepcor
    def __call__(self, r, amp):
        return SISShear_Corrections(r, amp, self.beta, self.beta2, stepcor = self.stepcor)

def SISShear_Corrections(r, amp, beta, beta2, stepcor = 1.):
    gamma = kappa = amp / r
    g = gamma / (1 - kappa)
    g[abs(g) > 1] = abs(1/g[abs(g)>1])
    gcorr = 1 + (beta2/beta**2 - 1)*kappa
    g = gcorr*g



    g = g/stepcor
    
    return g

def SISShear(r, amp):
    return amp / r

#######################


#returns sigma
def SISSigma(A, beta):
    X = 3600*180/pi  #convert arcseconds to radians
    return sqrt((A * (v_c)**2)/ (2*pi*beta*X))  #km/s

def SISAmp(sigma_v, beta):
    X = 3600*180/pi  #convert arcseconds to radians
    return 2*pi*beta*X*(sigma_v/v_c)**2

def SISSigmaErr(A, deltaA2, beta):
    X = 3600*180/pi  #convert arcseconds to radians
    sigmav = SISSigma(A, beta)
    return sqrt( deltaA2 * ((v_c**2) / (4*pi*sigmav *beta*X))**2 )

#########################################
#########################################

def MC_SIS_ML(r, g, g_err, pdzs, zcluster, stepcor=1., guess = 1000, niters=50000):

    memotable = {}
    results = []
    for i in xrange(niters):

        zs = array([pdz() for pdz in pdzs])
        betas, memotable = beta_memo(zs, zcluster, memotable = memotable)

        zcut = zs > (zcluster*1.1)
        kappacut = calcWLViolationCut(r, betas, sigma_v = 1300)
        radiuscut = r > 60  #arcseconds

        cleancut = logical_and(logical_and(kappacut, radiuscut), zcut)


        curR = r[cleancut]
        curG = g[cleancut]
        curGerr = g_err[cleancut]
        curBeta = betas[cleancut]

        sigma_v, sigma_verr, chisq, isCon = runSIS_ML(curR, curG, curGerr, curBeta, None, stepcor = stepcor, guess = guess)


        results.append((sigma_v, sigma_verr, chisq))

    return array(results)

########################

def runSIS_ML(r, g, g_err, beta, kappacut = None, stepcor = 1., guess = 1000):

    #r in arcseconds

    X = pi/(3600*180)  #convert arcseconds to radians

    coords = zeros((r.shape[0], 2))
    coords[:,0] = r*X
    coords[:,1] = beta

    sis_ml = SIS_ML_Fit(kappacut, stepcor)

    sigma_v2, chisq, covar, isCon = leastsq.leastsq(sis_ml, [guess], coords, g, g_err, fullOutput=True)

    if not isCon:
        return -999, -999, -999, False

    return sigma_v2, sqrt(covar[0][0]), chisq, isCon


#############################


class SIS_ML_Fit(object):
    def __init__(self, kappacut = None, stepcor = 1.):
        self.kappacut = kappacut
        self.stepcor = stepcor
    def __call__(self, coords, params):
        return SIS_ML(coords, params, self.kappacut, self.stepcor)

###

def SIS_ML(coords, sigma_v2, kappacut = None, stepcor = 1.):

    r = coords[:,0]
    beta = coords[:,1]

    gamma = kappa = 2*pi*beta*(sigma_v2)/((v_c**2)*r)
    g = gamma / (1 - kappa)
   
    g[g > 1] = 1/g[g>1]

    g = g/stepcor

    if kappacut is not None:
        g[kappa > kappacut] = float('nan')

    return g

###########################

def prepCat(cat, clusterz, pixscale, center, betas=None):

    r, E = calcTangentialShear(cat, center, pixscale)

    if betas is None:
        betas=beta(cat["Z_BEST"],clusterz, calcAverage = False)

    kappacut = calcWLViolationCut(r, betas, sigma_v = 1300)
    radiuscut = r > 60  #arcseconds
    
    cleancut = logical_and(kappacut, radiuscut)
    
    r = r[cleancut]
    E = E[cleancut]
    Eerr = sqrt(cat['sigma2_gs'][cleancut])
    if not hasattr(betas, 'shape'):
        betas = array(len(r)*[betas])
    else:
        betas = betas[cleancut]

    return r, E, Eerr, betas

##########################

def simpleBootstrap(cat, clusterz, pixscale, center, betas=None, nbootstraps=2000, stepcor=1.082):

    r, E, Eerr, betas = prepCat(cat, clusterz, pixscale, center, betas)

    if len(r) == 0:
        return []

    masses = [runSIS_ML(r, E, Eerr, betas, stepcor = stepcor)[0]]
    nelements = len(r)
    for i in xrange(nbootstraps):
        sample = random.randint(0,nelements,nelements)
        masses.append(runSIS_ML(r[sample], E[sample], Eerr[sample], betas[sample], 
                                stepcor = stepcor)[0])

    return masses

###########################

def combinedBootstrap(cats, clusterz, pixscale, center, inputBetas, 
                     nbootstraps=2000, stepcor=1.082):

    r = []
    E = []
    Eerr = []
    betas = []

    for curCat, curBeta in zip(cats, inputBetas):
        curR, curE, curEerr, curBetas = prepCat(curCat, clusterz, pixscale, center, curBeta)
        r.extend(curR)
        E.extend(curE)
        Eerr.extend(curEerr)
        betas.extend(curBetas)

    r = array(r)
    E = array(E)
    Eerr = array(Eerr)
    betas = array(betas)

    if len(r) == 0:
        return []

    masses = [runSIS_ML(r, E, Eerr, betas, stepcor = stepcor)[0]]
    nelements = len(r)
    for i in xrange(nbootstraps):
        sample = random.randint(0,nelements,nelements)
        masses.append(runSIS_ML(r[sample], E[sample], Eerr[sample], betas[sample], 
                                stepcor = stepcor)[0])

    return masses


    

############################


class ComovingDistMemoization(object):

    def __init__(self, memotable = {}):
        self.memotable = memotable
    def __call__(self, z):

        if z in self.memotable:
            return self.memotable[z]

        def integrand(z):

            return 1./(sqrt(Omega_m*(1+z)**(3) + Omega_l))

        y, err = quad(integrand, 0, z)
    
        dist = hubble_length * y

        self.memotable[z] = dist

        return dist


comovingdist = ComovingDistMemoization()        


def angulardist(z, z2 = None):

    if z2 is None:
        return comovingdist(z) / (1+z)

    return (comovingdist(z2) - comovingdist(z)) / (1+z2)


def beta_memo(z, zcluster, memotable = {}):
    z_round = around(z,2)
    notInMemoTable = array([curZ not in memotable for curZ in z_round])
    if notInMemoTable.any():
        zs_tocalc = unique(z_round[notInMemoTable])
        new_betas = beta(zs_tocalc, zcluster, calcAverage = False)
        for curZ, curBeta in zip(zs_tocalc, new_betas):
            memotable[curZ] = curBeta

    betas = array([memotable[curZ] for curZ in z_round])

    return betas, memotable



def beta(z, zcluster):

    Ds = array([angulardist(zi) for zi in z])
    Dls = array([angulardist(zcluster, zi) for zi in z])

    Dls_over_Ds = Dls / Ds
    Dls_over_Ds[Dls <= 0] = 0

    return Dls_over_Ds
    

def beta_s(z, zcluster):

    betainf = beta([1e6], zcluster)

    beta_s = beta(z, zcluster) / betainf

    return beta_s
    
