import re, cPickle
import numpy as np
import numpy
import ldac, astropy, astropy.io.fits as pyfits
import shearprofile as sp
import nfwmodel_sim as nfwsim, matching
import scipy.stats as stats
import nfwutils
#adam-old# import voigt_tools
import pickle
fl=open('/u/ki/awright/COSMOS_2017/bad_ids.pkl','rb')
bad_ids=pickle.load(fl)
fl.close()
fl=open('/u/ki/awright/COSMOS_2017/gone_ids.pkl','rb')
gone_ids=pickle.load(fl)
fl.close()
fl=open('/nfs/slac/kipac/fs1/u/awright/COSMOS_2017/id2pz_cdf.pkl','rb')
id2pz_cdf=pickle.load(fl)
fl.close()




############################################

pixscale = 0.2

def __DEFAULT_SHAPE_DISTRO__(g, binvals, sigma):
    size = len(binvals)
    return g + sigma*np.random.standard_normal(size)


###########################################

def voigtdistro(g, binvals, sigma, gamma):

    size = len(binvals)

    return g + voigt_tools.voigtSamples(sigma, gamma, size)

#########

def voigtDistro2(g, binvals, alpha, sigma1, gamma1, sigma2, gamma2):
    size = len(binvals)
    distro1 = np.random.uniform(size=size) < alpha
    distro2 = np.logical_not(distro1)

    gs = np.zeros(size)
    gs[distro1] = g[distro1]+voigt_tools.voigtSamples(sigma1, gamma1, len(gs[distro1]))
    gs[distro2] = g[distro2]+voigt_tools.voigtSamples(sigma2, gamma2, len(gs[distro2]))

    return gs


############################################

def matchById(smallcat, bigcat, smallid='SeqNr', bigid=None):
    if bigid is None:
        bigid = smallid

    seqnr = {}
    for i, x in enumerate(bigcat[bigid]):
        seqnr[x] = i
        
    keep = []
    for x in smallcat[smallid]:
        keep.append(seqnr[x])
            
    keep = np.array(keep)
    matched = bigcat.filter(keep)
    return matched

#############################################

def commonSubset(cat1, cat2, id1 = 'SeqNr', id2 = 'SeqNr'):

    ids1 = {}
    for i, x in enumerate(cat1[id1]):
        ids1[x] = i

    ids2 = {}
    for i, x in enumerate(cat2[id2]):
        ids2[x] = i

    keep1 = []
    keep2 = []

    for id, index in ids1.iteritems():
        if id in ids2:
            keep1.append(index)
            keep2.append(ids2[id])

    keep1 = np.array(keep1)
    keep2 = np.array(keep2)

    return cat1.filter(keep1), cat2.filter(keep2)
    


#############################################

def SphereDist(p1, p2):
    '''assumes already in radians, first coord is RA, second is dec'''
    dTheta = p1 - p2
    dLat = dTheta[:,1] #dec
    dLong = dTheta[:,0] #ra

    dist = 2*np.arcsin(np.sqrt(np.sin(dLat/2)**2 + np.cos(p1[:,1])*np.cos(p2[1])*np.sin(dLong/2)**2))

    return dist


def extractField(cat, size, snratio, maxradii = 4000, center = None, ra='ra', dec = 'dec', id = 'id', pixscale = pixscale):
    # extracts objects directly from bpz catalog w/ respect to position, from a random center position
    # uses periodic boundary conditions
    # fieldsize is (x,y) with units of pixels. Why? Cause I'm evil -- and lazy



    min_ra = np.min(cat[ra])
    max_ra = np.max(cat[ra])
    delta_ra = max_ra - min_ra
    min_dec = np.min(cat[dec])
    max_dec = np.max(cat[dec])
    delta_dec = max_dec - min_dec
    
    if center is None:
        center_x = np.random.uniform(min_ra, max_ra)
        center_y = np.random.uniform(min_dec, max_dec)
        center = [center_x, center_y]
        center = np.array(center)*(np.pi / 180.)


    ids = []
    ras = []
    decs = []
    sizes = []
    snratios = []
    for i in [-1, 0, 1]:
        for j in [ -1, 0, 1]:
            ids.extend(cat[id])
            ras.extend(cat[ra] + (i * delta_ra))
            decs.extend(cat[dec] + (j * delta_dec))
            sizes.extend(size)
            snratios.extend(snratio)

    ids = np.array(ids)
    points = np.pi * np.column_stack([ras, decs]) / 180.
    sizes = np.array(sizes)
    snratios = np.array(snratios)

    dr_rad = SphereDist(points, center)
    dr_pix = 3600.*180. * dr_rad / (np.pi * pixscale)

    inField = dr_pix < maxradii

    cols = [pyfits.Column(name = 'SeqNr', format = 'J', array = ids[inField]),
            pyfits.Column(name = 'r_pix', format = 'E', array = dr_pix[inField]),
            pyfits.Column(name = 'size', format = 'E', array = sizes[inField]),
            pyfits.Column(name = 'snratio', format = 'E', array = snratios[inField])]
    cols = ldac.LDACCat(pyfits.new_table(pyfits.ColDefs(cols)))
    cols.hdu.header.update('EXTNAME', 'OBJECTS')
    cols.hdu.header.update('CENTERX', center[0])
    cols.hdu.header.update('CENTERY', center[1])

    return cols

##########################

def bootstrapField(cat, size, snratio, galdensity = 150, maxradii = 4000, id = 'ID', pixscale = pixscale, ngals = None):
    #creates bootstrap realizations with galaxies randomly distributed throughout the field.
    #galdensity is numbers / square arcmin

    maxRdist = maxradii / np.sqrt(2.)
    area = 4*(maxRdist * pixscale / 60)**2

    if ngals is None and galdensity is not None:


        ngals = galdensity * area

    else:

        galdensity = float(ngals) / area


    xs = np.random.uniform(0, maxRdist, ngals)
    ys = np.random.uniform(0, maxRdist, ngals)
    dr_pix = np.sqrt(xs**2 + ys**2)

    bootstrap = np.random.randint(0, len(cat), ngals)

    ids = cat[id][bootstrap]
    sizes = size[bootstrap]
    snratios = snratio[bootstrap]


    cols = [pyfits.Column(name = 'SeqNr', format = 'J', array = ids),
            pyfits.Column(name = 'r_pix', format = 'E', array = dr_pix),
            pyfits.Column(name = 'size', format = 'E', array = sizes),
            pyfits.Column(name = 'snratio', format = 'E', array = snratios)]
    cols = ldac.LDACCat(pyfits.new_table(pyfits.ColDefs(cols)))
    cols.hdu.header.update('EXTNAME', 'OBJECTS')
    cols.hdu.header.update('GDENSITY', galdensity)
    cols.hdu.header.update('CENTERX', 0.)
    cols.hdu.header.update('CENTERY', 0.)

    return cols

    

##########################

def pick_snratio(sizes, size_distro, sn_distro, size_bin = 0.2):

    size_cat = matching.Catalog(sizes, np.zeros(len(sizes)), np.arange(len(sizes)))
    size_distro_cat = matching.Catalog(size_distro, 
                                       np.zeros(len(size_distro)), 
                                       np.arange(len(size_distro)))
                                                  
    trie = matching.buildTrie(size_distro_cat)

    snratios = np.zeros_like(sizes)

    for i in np.arange(len(sizes)):

        matches = np.array(trie.findNeighbors(np.array((0, sizes[i])), size_bin), dtype=np.int32)

        available_sns = sn_distro[matches]
        navailable = len(available_sns)

        if navailable == 0:
            deltaSize = np.abs(size_distro - sizes[i])
            available_sns = sn_distro[deltaSize == min(deltaSize)]
            navailable = len(available_sns)

        snratios[i] = available_sns[np.random.randint(0, navailable, 1)]

    return snratios


####################################            
    

def createCutoutSuite(zs, 
                      massrange, 
                      goodbpz, 
                      sizes, 
                      snratios,
                      outputdir, 
                      simcats = None,
                      sourcecat = None,
                      shape_distro = __DEFAULT_SHAPE_DISTRO__,
                      shape_distro_kw_sets = 100*[{'sigma' : 0.25}],
                      idcol = 'ID'):

    if simcats is None:
        simcats = []
        for i in range(len(shape_distro_kw_sets)):
            simsource = extractField(sourcecat, sizes, snratios)
            simcats.append(simsource)


    for curz in zs:
        print 'z = %2.2f' % curz
        for cur_mass in massrange:
            print '\tmass = %2.2f' % (cur_mass / 1e14)

            for i, simsource, kw_set in zip(range(len(simcats)), simcats, shape_distro_kw_sets):

                print '\t\t%d' % i

		#adam-old# base = '%s/cutout_z=%1.2f_mass=%2.2f_%d' % (outputdir, curz, cur_mass / 1e14, i)
                base = '%s/cutout_z_drawn_z=%1.2f_mass=%2.2f_%d' % (outputdir, curz, cur_mass / 1e14, i)

                #cur_rs = nfwutils.rscaleConstM(cur_mass, 4.0, curz, 500)
                cur_rs = nfwutils.RsMassInsideR(cur_mass, 4.0, curz, 1.5)


		simsource, simbpz = commonSubset(simsource, goodbpz,id2=idcol)


                simcat, momento = createCatalog(simbpz,
                                                simsource['size'],
                                                simsource['snratio'],
                                                4.0, 
                                                cur_rs,
                                                curz,
                                                ngals = None,
                                                shape_distro = shape_distro,
                                                shape_distro_kw = kw_set, 
                                                radii_pix = simsource['r_pix'],
                                                idcol = idcol)

    

                simcat.saveas('%s.cat' % base, clobber=True)
                output = open('%s.momento' % base, 'wb')
                cPickle.dump(momento, output, -1)
                output.close()


#########################



        
        



##########################
### cs.createCutoutSuite(zs, rsrange, mcosmos30, bpz, ones(len(bpz)), ones(len(bpz)), pdzrange, pdzs, '/u/ki/dapple/nfs12/cosmos/simulations/2010-11-16/extended', cs.__DEFAULT_SHAPE_DISTRO__, 100*[{'sigma' : 0.25}])

###cs.createCutoutSuite(zs, rsrange, mcosmos30, bpz, ones(len(bpz)), ones(len(bpz)), pdzrange, pdzs, '/u/ki/dapple/nfs12/cosmos/simulations/2010-11-16/extended', shape_distro_kw_sets = 100*[{'sigma' : 0.25}])

#def createSimSuite(zs, rsrange, goodbpz, pdzrange, pdzs, outputdir):
#
#
#    for curz in zs:
#        print 'z = %2.2f' % curz
#        for cur_rs in rsrange:
#            print '\trs = %2.2f' % cur_rs
#            for i in np.arange(15):
#                print '\t\t%d' % i
#                simcat, momento = createCatalog(goodbpz, 
#                                                4.0, 
#                                                cur_rs,
#                                                curz, 
#                                                21300, 
#                                                shape_distro_args = [0.25],
#                                                maxpix = 4000)
#                
#                base = '%s/sim_z=%1.2f_rs=%1.2f_%d' % (outputdir, curz, cur_rs, i)
#                simpdz = pdzfile_utils.associatePDZ(pdzs, simcat['z_id'])
#                simcat.saveas('%s.cat' % base, clobber=True)
#                output = open('%s.momento' % base, 'wb')
#                cPickle.dump(momento, output)
#                output.close()
#                output = open('%s.pdz' % base, 'wb')
#                cPickle.dump((pdzrange, simpdz), output)
#                output.close()
#
#
#
###########################    


def createCatalog(bpz,
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
                  contam_kw = {},
                  idcol = 'ID'):

    # ngals == None -> no bootstrapping
    # bpz is ldac bpz output

    momento = {'concentration'   : concentration,   
               'scale_radius'    : scale_radius,    
               'zcluster'        : zcluster,        
               'ngals'           : ngals,          
               'shape_distro'    : shape_distro.func_name,
               'shape_distro_args' : shape_distro_args,
               'shape_distro_kw' : shape_distro_kw,
               'maxpix'          : maxpix,
               'radii_pix'        : radii_pix
               }

    bootstrap = True
    if ngals == None:
        bootstrap = False
        ngals = len(bpz)

    if radii_pix is None:
        x_pix = np.random.uniform(0, maxpix, ngals)
        y_pix = np.random.uniform(0, maxpix, ngals)
        radii_pix = np.sqrt(x_pix**2 + y_pix**2)
    
    radii_mpc = radii_pix * pixscale * (1./3600.) * (np.pi / 180. ) * sp.angulardist(zcluster)

    chosenZs = bpz
    chosenSizes = bpz_sizes
    chosenSNratios = bpz_snratios
    if bootstrap:
        indices = np.random.randint(0, len(bpz), ngals)
        chosenZs = bpz.filter(indices)
        chosenSizes = bpz_sizes[indices]
        chosenSNratios = bpz_snratios[indices]


    print "adam-look: running createCatalog in cosmos_sim.py"
    z_id=chosenZs[idcol]
    zbins=numpy.arange(0,6.01,.01)
    z_drawn=-1*np.ones(len(chosenZs))
    print '!!!', len(z_drawn)
    for id_indx, id in enumerate(z_id):
	    try:
	    	    cdf=id2pz_cdf[id]
	    except:
		    if id in gone_ids:
			    print "adam-look: gone id ",id
			    continue
		    else:
			    raise
	    x=numpy.random.rand()
	    try:
	    	zval=(zbins[cdf<=x])[-1]
	    except:
		    if id in bad_ids:
			    print "adam-look: bad id ",id
		    	    continue
		    else:
			    raise
            z_drawn[id_indx] = zval
    
    good_draws = z_drawn > -1
    z_drawn = z_drawn[good_draws]
    radii_pix = radii_pix[good_draws]
    radii_mpc = radii_mpc[good_draws]
    chosenZs = chosenZs.filter(good_draws)
    chosenSizes = chosenSizes[good_draws]
    chosenSNratios = chosenSNratios[good_draws]
    ngals = len(z_drawn)
    


    true_shears, true_gamma, true_kappa = nfwsim.create_nfwmodel_shapedata(concentration, scale_radius,
                                                   zcluster, ngals, 
                                                   z_drawn, 
                                                   radii_mpc)

    true_beta = nfwutils.beta_s(z_drawn, zcluster)



    ghats = shape_distro(true_shears, np.column_stack([chosenSizes, chosenSNratios]), 
                         *shape_distro_args, **shape_distro_kw)


    
    cols = [ pyfits.Column(name = 'Seqnr', format = 'J', array = np.arange(ngals)), 
             pyfits.Column(name = 'r_pix', format = 'E', array = radii_pix), 
             pyfits.Column(name = 'r_mpc', format = 'E', array = radii_mpc),
             pyfits.Column(name = 'z', format = 'E', array = z_drawn),
             pyfits.Column(name = 'z_id', format = 'J', array = chosenZs[idcol]),
             pyfits.Column(name = 'ghats', format = 'E', array = ghats),
             pyfits.Column(name = 'true_shear', format = 'E', array = true_shears),
             pyfits.Column(name = 'true_z', format = 'E', array = z_drawn),
             pyfits.Column(name = 'true_beta', format = 'E', array = true_beta),
             pyfits.Column(name = 'true_gamma', format = 'E', array = true_gamma),
             pyfits.Column(name = 'true_kappa', format = 'E', array = true_kappa)]


    
    simcat = pyfits.new_table(pyfits.ColDefs(cols))
    simcat.header.update('EXTNAME', 'OBJECTS')
    simcat.header.update('concen', concentration)
    simcat.header.update('r_s', scale_radius)
    simcat.header.update('z', zcluster)


    return ldac.LDACCat(simcat), momento


################################

def addPDZNoise(actualZs, zsigma, pdf_range = np.arange(0, 5.0, 0.01)):

    ngals = len(actualZs)

    baseZs = actualZs  + zsigma*np.random.standard_normal(size=ngals)
    baseZs[baseZs < 0] = 0.

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


    return pdz
    


#################################################


def addContamination(sourcebpz, source_snratio, source_size, simcat, simpdz, r500, zcluster, f500 = 0.04, pixscale = pixscale, refcat = '/u/ki/dapple/nfs12/cosmos/cosmos2.cat',
                     shape_distro = __DEFAULT_SHAPE_DISTRO__, 
                     shape_distro_args = [], 
                     shape_distro_kw = {}):

    refcat = ldac.openObjectFile(refcat).matchById(sourcebpz, selfid = 'id')

    r_max = max(simcat['r_pix'])
    area = np.pi*(r_max*pixscale / 60.)**2
    n_back = float(len(simcat)) / area

    x,y = nfwsim.stdcontamination((0,0), pixscale, f500, n_back, r500, zcluster)

    r_pix = np.sqrt(x**2 + y**2)

    r_mpc = r_pix * pixscale * (1./3600.) * (np.pi / 180. ) * sp.angulardist(zcluster)

    z = zcluster*np.ones(len(r_pix))

    toKeepAvailable = {}
    for id in sourcebpz['SeqNr']:
        toKeepAvailable[id] = True
    for id in simcat['z_id']:
        toKeepAvailable[id] = False


    zkey = 'zp_best'
    if zkey not in sourcebpz:
        zkey = 'BPZ_Z_S'
    

    toKeep = np.logical_and(np.logical_and(np.array([toKeepAvailable[id] for id in sourcebpz['SeqNr']]),
                                           refcat['mod_gal'] > 8),
                            np.logical_and(sourcebpz[zkey] > (zcluster - 0.05),
                                           sourcebpz[zkey] < (zcluster + 0.05)))


    #toKeep = np.logical_and(np.array([toKeepAvailable[id] for id in sourcebpz['SeqNr']]),
    #                        np.logical_and(sourcebpz[zkey] > (zcluster - 0.05),
    #                                       sourcebpz[zkey] < (zcluster + 0.05)))
    #
    #
    
    availablebpz = sourcebpz.filter(toKeep)
    available_snratio = source_snratio[toKeep]
    available_size = source_size[toKeep]

    selected = np.random.randint(0, len(availablebpz), len(r_pix))
    selectedbpz = availablebpz.filter(selected)
    selected_snratio = available_snratio[selected]
    selected_size = available_size[selected]
    
    
    col_collection = {'Seqnr' : -selectedbpz['SeqNr'],
            'r_pix' : r_pix,
            'r_mpc' : r_mpc,
            'z' : z,
            'z_id' : selectedbpz['SeqNr'],
            'ghats' : shape_distro(np.zeros(len(selectedbpz)), 
                                   np.column_stack([selected_size, selected_snratio]), 
                                   *shape_distro_args, **shape_distro_kw),
            'true_shear' : np.zeros_like(r_pix),
            'true_z' : zcluster*np.ones_like(r_pix),
            'true_beta' : np.zeros_like(r_pix),
            'true_gamma' : np.zeros_like(r_pix),
            'true_kappa' : np.zeros_like(r_pix)
            }
            


    cols = []
    for name, arr in col_collection.iteritems():
        if name == 'SeqNr':
            col = pyfits.Column(name = name, format = 'J', array = arr)
        else:
            col = pyfits.Column(name = name, format = 'E', array = arr)
        cols.append(col)


    contamcat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols)))


    finalcat = simcat.append(contamcat)


    return finalcat
    
