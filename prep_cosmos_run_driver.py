#! /usr/bin/env python
#adam-does# RUNNING COSMOS MASS BIAS CALCULATION step 1 of 4
#adam-example# ./prep_cosmos_run_driver.py '/nfs/slac/g/ki/ki18/anja/SUBARU/cosmossims2017/' 'UGRIZ'
import sys
import prep_cosmos_run as pcr

if __name__ == '__main__':
	import adam_quicktools_ArgCleaner
	argv=adam_quicktools_ArgCleaner.ArgCleaner(sys.argv)
	datadir = argv[0]
	filterset = argv[1]
	filtersetdir=datadir+'/'+filterset+'/'

	print "running prepSourceFiles"
	pcr.prepSourceFiles(filterset, datadir)
	print "running createMasterFields"
	pcr.createMasterFields(filtersetdir)
	print "running createBootstrapFields"
	pcr.createBootstrapFields(filtersetdir)
	print "running createCatalogs"
	pcr.createCatalogs(filtersetdir)
