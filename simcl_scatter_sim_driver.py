#! /usr/bin/env python
#adam-does# RUNNING COSMOS MASS BIAS CALCULATION step 1 of 4
#adam-example# ./prep_cosmos_run_driver.py '/nfs/slac/g/ki/ki18/anja/SUBARU/cosmossims2017/' 'UGRIZ'
import sys,os
import prep_cosmos_run as pcr

if __name__ == '__main__':
	import adam_quicktools_ArgCleaner
	argv=adam_quicktools_ArgCleaner.ArgCleaner(sys.argv)
	datadir = argv[0]
	filterset = argv[1]
	filtersetdir=datadir+'/'+filterset+'/'

	print 'simcl_scatter_sim_driver.py: datadir=',datadir,' filterset=',filterset  
	print "running prepSourceFiles"
	pcr.prepSourceFiles(filterset, datadir)
	##adam: bpzfile = '%s/%s/bpz.cat' % (datadir,filterset)

## now instead of doing the `pcr.createCatalogs` stuff as before
## I'll be using ss.createPrecutSimFiles instead to make the catalogs

import scatter_sims as ss, compare_masses as cm
from readtxtfile import readtxtfile
import numpy as np
worklist = readtxtfile('simclusterlist')
clusters = [x[0] for x in worklist]
filters = [x[1] for x in worklist]
images = [x[2] for x in worklist]
redshifts = cm.readClusterRedshifts()
properredshifts = np.array([redshifts[x] for x in clusters])



## method #1: using cm.readAnjaMasses
anjamasses = cm.readAnjaMasses(dir='/u/ki/dapple/subaru/doug/publication/ccmass_2012-07-31')
for cluster, filter, image, z in zip(clusters, filters, images, properredshifts):
	try:
		clusterdir = '/u/ki/dapple/subaru/%s/LENSING_%s_%s_aper/%s' % (cluster, filter, filter, image)
		reconfile='%s/cosmos_rscut.cat' % (clusterdir)
		mass=anjamasses[(cluster, filter, image)][0]
		print ' cluster=',cluster , ' filter=',filter , ' image=',image , ' mass=',mass , ' z=',z
		
		#bpzfile   :'/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat'
		#reconfile :'/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17/%s/bpz.cat' % (cluster)
		#adam-old# ss.createPrecutSimFiles(cluster, filter, image, mass, z, \
		#adam-old# 	bpzfile='/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat', \
		#adam-old# 	reconfile='/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17/%s/bpz.cat' % (cluster), \
		#adam-old# #bpzfile   :'/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat'
		#adam-old# #reconfile :'/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17/%s/bpz.cat' % (cluster)
	except KeyError:
		print 'KeyError for cluster=',cluster , ' filter=',filter , ' image=',image , ' z=',z
		continue
	cutoutfiles = ss.createPrecutSimFiles(cluster, filter, image, mass, z, \
		bpzfile='%s/bpz.cat' % (filtersetdir), \
		reconfile=reconfile, outdir=filtersetdir)
	#adam-old# bpzfile='/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat', \
	print ' cluster-',cluster , '-files:', cutoutfiles
	clustersubdir='%s/%s/' % (filtersetdir,cluster)
	os.makedirs(clustersubdir)
	for cofl in cutoutfiles:
		os.system('ln -s %s %s' % (cofl, clustersubdir))
	#old# ss.createPrecutSimFiles('MACS0025-12', 'W-J-V', 'good', 5e14, 0.56, '/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat', '/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17/MACS0025-12/bpz.cat', '/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17/fake/')

sys.exit()
# run_ml_sim_bias.py has these inputs:
# workdir = sys.argv[1]
# subdir = sys.argv[2]
# outfile = sys.argv[3]
# nsamples = int(sys.argv[4])
workdir = '/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17/'
subdir = 'contam0p10/BVRIZ/'
## this worked## ./run_ml_sim_bias.py /u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17/ contam0p10/BVRIZ/ testout_run_ml_sim_bias.log 5

## method #2: using ss.readMLMasses
masses, errs, massgrid, scale_radii = ss.readMLMasses(workdir, subdir, clusters)
########I also found the missing script, scatter_sims.py, so the file names make sense.  Here's what I called:
########ss.createPrecutSimFiles('MACS0025-12', 'W-J-V', 'good', 5e14, 0.56, '/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat', '/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17/MACS0025-12/bpz.cat', '/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17/fake/')
########so: cluster name, filter name, image name, target mass (should be best fit), target redshift (should be cluster redshift), new photo-z catalogue for truth, the BPZ output file where cuts for the cluster field were made, and the outputdir.
########Then, to run a mass fit for one of the catalogs
########./maxlike_simdriver.py -o test.out -i ~/nfs12/cosmos/simulations/clusters_2012-05-17/fake/cutout_z_drawn_z=0.56_mass=5.00_20.cat -p ~/nfs12/cosmos/simulations/clusters_2012-05-17-highdensity/BVRIZ.pdz.cat -b ~/nfs12/cosmos/simulations/clusters_2012-05-17-highdensity/BVRIZ.rawbpz.cat
########The files passed in with the -p and -b options should be the BPZ and converted P(z) files from running on cosmos with a subset of filters, ie like in ~dapple/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_*
########So you should be able to create a new set of sim files and go into production. Let me know when you hit the next bug or snag!
for cluster, filter, image, mass, z in zip(clusters, filters, images,masses,properredshifts):
	#tmp# ss.createPrecutSimFiles(cluster, filter, image, mass, z, '/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat', '/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17/%s/bpz.cat' % (cluster), '/nfs/slac/g/ki/ki18/anja/SUBARU/cosmos/simcl_start_with_dougs/')
	print ' cluster=',cluster , ' filter=',filter , ' image=',image , ' mass=',mass , ' z=',z
	#old# ss.createPrecutSimFiles('MACS0025-12', 'W-J-V', 'good', 5e14, 0.56, '/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat', '/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17/MACS0025-12/bpz.cat', '/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17/fake/')
