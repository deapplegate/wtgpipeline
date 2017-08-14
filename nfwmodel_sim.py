##########################
# Implements an NFW model for investigation 
# of redshift and contamination effects
###########################

import pymc, numpy as np, scipy.stats as stats
import nfwutils
import nfwmodeltools as tools
import cPickle


########################

__cvs_id__ = "$Id: nfwmodel_sim.py,v 1.4 2011-02-11 02:55:04 dapple Exp $"


#########################

__DEFAULT_OMEGA_M__ = 0.3
__DEFAULT_OMEGA_L__ = 0.7
__DEFAULT_h__ = 0.7
__DEFAULT_PIXSCALE__ = 0.2  #arcsec / pix
__DEFAULT_SIZE__ = np.array([10000,10000]) #pixels
__DEFAULT_CENTER__ = np.array([5000,5000])  #cluster location

v_c = 299792.458 #km/s

#########################


######################
# SIMULATION
######################



def create_nfwmodel_shapedata(concentration, scale_radius , zcluster, ngals, 
                              zs, rs):


    realBetas = nfwutils.beta_s(zs, zcluster)

    gamma = realBetas*tools.NFWShear(rs, concentration, scale_radius, zcluster)
    kappa = realBetas*tools.NFWKappa(rs, concentration, scale_radius, zcluster)

    g = gamma / ( 1 - kappa )

    return g, gamma, kappa

    
###################

def create_realistic_zdata(ngals, pdf_range, zsigma):

    baseZs = np.zeros(ngals)

    inMainDist = np.random.uniform(0, 1, ngals) < 0.60
    nMain = np.ones_like(inMainDist)[inMainDist].sum()
    nSecond = ngals - nMain
    

    a = 1.678 / 5.606
    c = 5.606
    baseZs[inMainDist] = 0.8*stats.gengamma.rvs(a, c, size=nMain)

    a = 2.
    c = 1.
    baseZs[np.logical_not(inMainDist)] = 0.8*stats.gengamma.rvs(a, c, size=nSecond)


    actualZs = baseZs  + zsigma*np.random.standard_normal(ngals)
    actualZs[actualZs < 0] = 0.

    probs = []
    for z in pdf_range:
        probs.append( stats.norm.pdf( z, baseZs, zsigma) )

    pdz = np.column_stack(probs)

    extended_pdf_range = np.arange(-2, 0, 0.01)
    probs = []
    for z in extended_pdf_range:
        probs.append( stats.norm.pdf( z, baseZs, zsigma) )

    extended_pdz = np.column_stack(probs)
    out_of_bounds_prob = extended_pdz.sum(axis=-1)
    
    pdz[:,0] = pdz[:,0] + out_of_bounds_prob
    

    return actualZs, pdz

######################

def dopePDZ(actualZs, scatterUp=0.05, scatterDown=0.05):


    probs = np.random.uniform(0., 1., len(actualZs))

    scatterUp = probs < scatterUp
    scatterDown = probs > (1 - scatterDown)

    actualZs[scatterUp] = actualZs[scatterUp] + np.random.uniform(0.25, 1.5, len(actualZs[scatterUp]))
    actualZs[scatterDown] = actualZs[scatterDown] - np.random.uniform(0.25, 1.5, len(actualZs[scatterDown]))
    
    actualZs[actualZs < 0] = 0.

def shiftPDZ(actualZs, shift=0.1):

    actualZs[:] = actualZs + shift

#####################

def pix2mpc(radii_pix, pixscale, zcluster):

    return radii_pix * pixscale * (1./3600.) * (np.pi / 180. ) * nfwutils.angulardist(zcluster)


######################


def create_nfw_realsim(ngals, concentration, scale_radius , zcluster,  
                       shape_sigma, zsigma, pdf_range=np.arange(0, 5.0, 0.01), doping = None,
                       pixscale = __DEFAULT_PIXSCALE__):


    radii_pix = np.random.uniform(100, 5000, size=ngals)

    radii_mpc = pix2mpc(radii_pix, pixscale, zcluster)

    actualZs, pdz = create_realistic_zdata(ngals, zsigma = zsigma, pdf_range = pdf_range)


    if doping:
        doping(actualZs)

    ghats = create_nfwmodel_shapedata(concentration, scale_radius , zcluster, 
                                      ngals, actualZs, radii_mpc) + \
                                      shape_sigma*np.random.standard_normal(ngals)

    betas = nfwutils.beta_s(actualZs, zcluster)

    dz = pdf_range[1] - pdf_range[0]

    inRange = np.max(pdz, axis=-1) > 1e-3

    return radii_pix[inRange], radii_mpc[inRange], ghats[inRange], actualZs[inRange], betas[inRange], pdz[inRange], dz


##########################

class Simdata(object):

    def __init__(self, x, y, g1, g2, sigma_gs, zs, pdf_range, pdz, isreal_flag, momento, zdist = None):
        
        self.x            = x          
        self.y            = y          
        self.g1           = g1         
        self.g2           = g2         
        self.sigma_gs     = sigma_gs   
        self.zs           = zs     
        self.pdf_range    = pdf_range
        self.pdz          = pdz        
        self.isreal_flag  = isreal_flag
        self.momento      = momento    
        self.zdist        = zdist

        if zdist is None:
            self.zdist        = zs


    def write(self, output_base):

        cat = open('%s.dat' % output_base, 'w')

        seqnr = np.arange(len(self.x)) + 1

        for id, x, y, g1, g2, sigma_g in zip(seqnr, self.x, self.y, self.g1, self.g2, self.sigma_gs):

            cat.write('%d %f %f %f %f %f\n' % (id, x, y, g1, g2, sigma_g))

        cat.close()


        pdzfile = open('%s.pdz' % output_base, 'w')

        dz = self.pdf_range[1] - self.pdf_range[0]

        pdzfile.write('# ID\tp_bayes(z)\twhere z=arange(%f,%f,%f)\n' % (self.pdf_range[0], self.pdf_range[-1] + dz, dz))

        for id, object in zip(seqnr, self.pdz):

            pdzfile.write('%d %s\n' % (id, ' '.join(map(str, list(object)))))

        pdzfile.close()


        zdistfile = open('%s.zdist' % output_base, 'w')
        for z in self.zdist:
            zdistfile.write('%f\n' % z)
        zdistfile.close()


        momentofile = open('%s.momento' % output_base, 'w')
        for key, val in self.momento.iteritems():
            momentofile.write('%s = %s\n' % (str(key), str(val)))

        momentofile.close()

        pklfile = open('%s.pkl' % output_base, 'wb')
        cPickle.dump(self, pklfile, -1)


#####

    @classmethod
    def read(cls, inputfile):

        pklfile = open(inputfile, 'rb')
        data = cPickle.load(pklfile)
        pklfile.close()

        return data

    


#########

def stdcontamination(center, pixscale, amp, nback, norm_radius, zcluster, generator = np.random.poisson, innerlimit = .2, outerlimit = 5):

    # uses rho = n_back * amp*e^{1 - r_norm}
    # amp is fraction of cluster galaxies at r_norm

    D_lens = nfwutils.angulardist(zcluster)

    inner_pix = innerlimit * 3600. * (180./np.pi) / ( pixscale * D_lens )
    outer_pix = outerlimit * 3600. * (180./np.pi) / ( pixscale * D_lens )
    
    dr = 100.
    r_pix = np.arange(inner_pix, outer_pix, dr) + dr/2.
    r_arcmin = r_pix * pixscale / 60
    delta_r_arcmin = dr * pixscale / 60
    r_norm = pix2mpc(r_pix, pixscale, zcluster) / norm_radius


#    area = 2*np.pi*r_arcmin*delta_r_arcmin
    area = 2*np.pi*r_pix*dr * pixscale**2 / 3600

    cluster_density = nback*amp*np.exp(1 - r_norm)

    expected_count = area * cluster_density

    print expected_count

    ngals = generator(lam = expected_count)



    x = []
    y = []
    for rbin, ngal in zip(r_pix, ngals):
        r = np.random.uniform(rbin - dr/2., rbin + dr/2., ngal)
        phi = np.random.uniform(0, 2*np.pi, ngal)
        x.extend(r*np.cos(phi))
        y.extend(r*np.sin(phi))

    x = np.array(x) + center[0]
    y = np.array(y) + center[1]

#    inside_image = np.logical_and(np.logical_and(x >= 0, x < size[0]), np.logical_and(y >= 0, y < size[1]))

#    return x[inside_image], y[inside_image]

    return x, y
    



###

def deltaZdist(ngals, pdf_range):

    probs = []
    for z in pdf_range:
        probs.append( stats.norm.pdf( z, 1., 0.002) )

    pdz = np.column_stack(probs)

    

    return np.ones(ngals), pdz


###

def create_2D_nfw_contamination(num_normgals,
                                concentration,
                                scale_radius, 
                                zcluster, 
                                shape_sigma, 
                                zdist,        
                                pdf_range = np.arange(0, 5.0, 0.01),
                                zdist_arg = [],
                                zdist_keywords = {},
                                contamination = None,
                                contamination_arg = [],
                                contamination_keywords = {},
                                pixscale = __DEFAULT_PIXSCALE__, 
                                size=__DEFAULT_SIZE__, 
                                center=__DEFAULT_CENTER__):
    ''' create_nfw_contamination
    @param num_normgals   number of regular galaxies that follow distribution,
    @param scale_radius  Mpc
    @param zcluster  cluster redshift
    @param zdist    function: ngals -> true redshifts
    @param contamination  function: size, center -> x,y positions
    @param contamination_args, contamination_keywords -> to be passed to contamination
    '''

    
    x = np.random.uniform(0, size[0], num_normgals)
    y = np.random.uniform(0, size[1], num_normgals)
    radii_pix = np.sqrt((x - center[0])**2 + (y - center[1])**2)
    radii_mpc = pix2mpc(radii_pix, pixscale, zcluster)

    actualZs, actual_pdz = zdist(num_normgals, pdf_range, *zdist_arg, **zdist_keywords)

    actual_ghats = create_nfwmodel_shapedata(concentration, scale_radius, zcluster, num_normgals, actualZs, radii_mpc, shape_distro_args = [shape_sigma])

    if contamination is not None:

        x_contam, y_contam = contamination(size, center, pixscale, *contamination_arg, **contamination_keywords)
        num_contamgals = len(x_contam)
        ghat_contam = shape_sigma*np.random.standard_normal(num_contamgals)
        fakeZs, fake_pdz = zdist(num_contamgals, pdf_range, *zdist_arg, **zdist_keywords)

        x = np.hstack([x, x_contam])
        y = np.hstack([y, y_contam])
        zs = np.hstack([actualZs, fakeZs])
        pdz = np.vstack([actual_pdz, fake_pdz])
    
        ghat_t = np.hstack([actual_ghats, ghat_contam])

    else:

        zs = actualZs
        pdz = actual_pdz
        ghat_t = actual_ghats


    ngals = len(x)

    ghat_x = shape_sigma*np.random.standard_normal(ngals)

    # rotate back to g1, g2
    xrel = x - center[0]
    yrel = y - center[1]
    
    phi = -np.arctan2(yrel, xrel)
    cos2phi = np.cos(2*phi)
    sin2phi = np.sin(2*phi)

    g1 = -(ghat_t*cos2phi+ghat_x*sin2phi)
    
    b1 =  ghat_x
    b2 = -ghat_t
    g2 = -(b1*cos2phi+b2*sin2phi)

    sigma_gs = np.ones_like(g1)

    
    isreal_flag = np.ones(ngals, dtype=np.int16)
    isreal_flag[num_normgals:] = 0

    momento = {'num_normgals'             : num_normgals,                          
               'concentration'            : concentration,                         
               'scale_radius'             : scale_radius,                          
               'zcluster'                 : zcluster,                              
               'shape_sigma'              : shape_sigma,                           
               'zdist'                    : zdist,
               'zdist_arg'                : zdist_arg,
               'zdist_keywords'           : zdist_keywords,
               'pdf_range'                : pdf_range,
               'contamination'            : contamination,                         
               'contamination_args'       : contamination_arg,                    
               'contamination_keywords'   : contamination_keywords,                
               'pixscale'                 : pixscale,
               'size'                     : size,
               'center'                   : center}



    return Simdata(x, y, g1, g2, sigma_gs, zs, pdf_range, pdz, isreal_flag, momento)

#####

    
    
