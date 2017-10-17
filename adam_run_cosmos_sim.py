import re, cPickle
import numpy as np
import ldac, astropy, astropy.io.fits as pyfits
import shearprofile as sp
import nfwmodel_sim as nfwsim, matching
import scipy.stats as stats
import nfwutils, voigt_tools



############################################

pixscale = 0.2

########def createCatalog(bpz,
########		  bpz_sizes,
########		  bpz_snratios,
########		  concentration, 
########		  scale_radius, 
########		  zcluster, 
########		  ngals,
########		  shape_distro = __DEFAULT_SHAPE_DISTRO__, 
########		  shape_distro_args = [], 
########		  shape_distro_kw = {}, 
########		  maxpix=5000, 
########		  radii_pix = None,
########		  contam = None,
########		  contam_args = [],
########		  contam_kw = {}):
########
########    # ngals == None -> no bootstrapping
########    # bpz is ldac bpz output
########
########    momento = {'concentration'   : concentration,   
########	       'scale_radius'    : scale_radius,    
########	       'zcluster'        : zcluster,        
########	       'ngals'           : ngals,          
########	       'shape_distro'    : shape_distro.func_name,
########	       'shape_distro_args' : shape_distro_args,
########	       'shape_distro_kw' : shape_distro_kw,
########	       'maxpix'          : maxpix,
########	       'radii_pix'        : radii_pix
########	       }
########
########    bootstrap = True
########    if ngals == None:
########	bootstrap = False
########	ngals = len(bpz)
########
########    if radii_pix is None:
########	x_pix = np.random.uniform(0, maxpix, ngals)
########	y_pix = np.random.uniform(0, maxpix, ngals)
########	radii_pix = np.sqrt(x_pix**2 + y_pix**2)
########    
########    radii_mpc = radii_pix * pixscale * (1./3600.) * (np.pi / 180. ) * sp.angulardist(zcluster)
########
########    chosenZs = bpz
########    chosenSizes = bpz_sizes
########    chosenSNratios = bpz_snratios
########    if bootstrap:
########	indices = np.random.randint(0, len(bpz), ngals)
########	chosenZs = bpz.filter(indices)
########	chosenSizes = bpz_sizes[indices]
########	chosenSNratios = bpz_snratios[indices]
########
########
########    zkey = 'zp_best'
########    if zkey not in chosenZs:
########	zkey = 'BPZ_Z_S'
########    
########    #adam-new# Change from using single point zp_best to drawing a random sample from the p(z) dist'n
########    #adam-old# change from `true_z = chosenZs[zkey]` to z_drawn from p(z)
########    z_id=chosenZs['SeqNr']
########    import pickle
########    fl=open('/nfs/slac/kipac/fs1/u/awright/COSMOS_2017/id2pz_cdf.pkl','rb')
########    id2pz_cdf=pickle.load(fl)
########    zbins=numpy.arange(0,6.01,.01)
########    z_drawn=[]
########    for id in z_id:
########	    cdf=id2pz_cdf[id]
########	    x=numpy.random.rand()
########	    zval=(zbins[cdf<=x])[-1]
########	    z_drawn.append(zval)
########    
########    z_drawn=numpy.array(z_drawn)
########    true_shears, true_gamma, true_kappa = nfwsim.create_nfwmodel_shapedata(concentration, scale_radius,
########						   zcluster, ngals, 
########						   z_drawn, 
########						   radii_mpc)
########
########    true_beta = nfwutils.beta_s(z_drawn, zcluster)
########
########
########    print shape_distro_args
########    print shape_distro_kw
########
########    ghats = shape_distro(true_shears, np.column_stack([chosenSizes, chosenSNratios]), 
########			 *shape_distro_args, **shape_distro_kw)
########
########
########    
########    cols = [ pyfits.Column(name = 'Seqnr', format = 'J', array = np.arange(ngals)), 
########	     pyfits.Column(name = 'r_pix', format = 'E', array = radii_pix), 
########	     pyfits.Column(name = 'r_mpc', format = 'E', array = radii_mpc),
########	     #adam-old# pyfits.Column(name = 'z', format = 'E', array = chosenZs[zkey]),
########	     pyfits.Column(name = 'z', format = 'E', array = z_drawn),
########	     pyfits.Column(name = 'z_id', format = 'J', array = chosenZs['SeqNr']),
########	     pyfits.Column(name = 'ghats', format = 'E', array = ghats),
########	     pyfits.Column(name = 'true_shear', format = 'E', array = true_shears),
########	     pyfits.Column(name = 'true_z', format = 'E', array = true_z),
########	     pyfits.Column(name = 'true_beta', format = 'E', array = true_beta),
########	     pyfits.Column(name = 'true_gamma', format = 'E', array = true_gamma),
########	     pyfits.Column(name = 'true_kappa', format = 'E', array = true_kappa)]
########
########
########    
########    simcat = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
########    simcat.header['EXTNAME']= 'OBJECTS'
########    simcat.header['concen']= concentration
########    simcat.header['r_s']= scale_radius
########    simcat.header['z']= zcluster
########
########
########    return ldac.LDACCat(simcat), momento

### /u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.cat ###w
#['gp', 'dIB484', 'F814W', 'i_max', 'dIB527', 'dH1', 'K_uv', 'NB816', 'z_s', 'IB738', 'ID_2006', 'i_auto', 'dH_uv', 'i_star', 'H', 'du_s', 'F814W_star', 'J_uv', 'dch3', 'dIB738', 'du', 'dIB827', 'IB427', 'dJ', 'dH', 'dB', 'H_uv', 'IB505', 'J3', 'dch2', 'dV', 'x', 'dip', 'IB624', 'FUV', 'dIB505', 'dJ3', 'dJ2', 'dKs', 'di_s', 'Eb-v', 'J2', 'g_s', 'J1', 'dIB624', 'dK_uv', 'dKc', 'di_c', 'zp', 'rp', 'dKnf', 'dH2', 'appflag', 'ra', 'photflag', 'dF814W', 'dNUV', 'auto_offset', 'ID_2008', 'acs_mask', 'dNB816', 'di_auto', 'H2', 'drp', 'H1', 'dIB427', 'dzp', 'dFUV', 'deep_mask', 'V_mask', 'dJ1', 'dIB767', 'z_mask', 'dg_s', 'i_mask', 'IB574', 'dzpp', 'NUV', 'zpp', 'blendflag', 'mask_NUV', 'IB679', 'Kc', 'B', 'J', 'F814W_fwhm', 'Ks', 'dIB574', 'det_fwhm', 'dIB679', 'V', 'i_fwhm', 'IB709', 'ch1', 'ch2', 'ch3', 'ch4', 'IB767', 'mask_FUV', 'dec', 'IRAC2_mask', 'ip', 'i_c', 'i_s', 'dIB709', 'dz_s', 'dJ_uv', 'r_s', 'dY_uv', 'u_s', 'Kc_mask', 'B_mask', 'auto_flag', 'tile', 'flags', 'dch1', 'IRAC1_mask', 'dch4', 'acsdata_mask', 'dNB711', 'Knf', 'y', 'dgp', 'IB827', 'ID', 'NB711', 'IB464', 'Y_uv', 'IB527', 'u', 'objID', 'dr_s', 'IB484', 'dIB464']





### /u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat ###
#['zchi', 'M_j', 'M_i', 'M_k', 'BCmass', 'BCsfr', 'zerr_chi_min', 'chipdf', 'M_g', 'M_FUV', 'M_z', 'chisq', 'L_k', 'BCsfr_min', 'M_r', 'M_u', 'zqso', 'BCmodel', 'zerr_chi_max', 'ACSstar', 'M_B', 'star_model', 'BCssfr_min', 'galaxy_model', 'ra', 'qso_model', 'DCnuv-r', 'type', 'chistar', 'BCssfr_max', 'L_nu', 'zqsochi', 'L_r', 'BCext', 'zpdf', 'zphot', 'ID', 'zerr_pdf_min', 'BCmass_min', 'dec', 'BCsfr_max', 'M_NUV', 'BCage', 'zphot2', 'BCmass_max', 'BCssfr', 'zerr_pdf_max', 'M_V', 'Ebv', 'Nbands', 'objID', 'chisq2', 'Mass_2006', 'Ext_law']`

################################

fl="/nfs/slac/g/ki/ki06/anja/SUBARU/cosmos_cats/simulations/clusters_2012-05-17/MACS0025-12/bpz.cat"
#cosmos="/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.cat"
#cosmos="/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat"
#   206963 ./clusters_2012-05-17_nooutliers/MACS0025-12/bpz.cat
#   206963 ./publication/highsn/cluster3/MACS0025-12/bpz.cat
#   133721 ./publication/highsn/cluster2/MACS0025-12/bpz.cat
#   206963 ./clusters_2012-05-17/MACS0025-12/bpz.cat
#   206963 ./clusters_2012-05-17-highdensity/MACS0025-12/bpz.cat

import cosmos_sim

cosmos_sim.createCatalog(bpz,
		  bpz_sizes,
		  bpz_snratios,
		  concentration, 
		  scale_radius, 
		  zcluster, 
		  ngals,
		  shape_distro = __DEFAULT_SHAPE_DISTRO__, 
		  shape_distro_args = [], 
		  shape_distro_kw = {}, 
		  maxpix=5000, 
		  radii_pix = None,
		  contam = None,
		  contam_args = [],
		  contam_kw = {})
## ./publication/highsn/cluster3/MACS0025-12/field_10.cat
## ./publication/highsn/BVRIZ/field_2.cat
