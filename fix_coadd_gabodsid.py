#! /usr/bin/env python
'''
get the right gabodsid GABODSID and CONFIG keys in there
'''
## get cleaned args and import necessary tools
import sys,os,inspect                                                                                                                                                                                                                                                          
sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
#from import_tools import *

## args cleaned in ~/bonnpipeline:
import adam_quicktools_ArgCleaner
argv=adam_quicktools_ArgCleaner.ArgCleaner(sys.argv)

import astropy
import astropy.io.fits as pyfits
import utilities

def find_config(GID): #simple
    '''inputs: GID
    returns:  CONFIG_IM
    purpose: based on GABODSID, figure out which configuration the images are from
    calls:
    called_by: match_OBJNAME,match_OBJNAME'''
    #print 'find_config| START the func. inputs: GID=',GID
    config_list = [[575,691,'8'],[691,871,'9'],[817,1309,'10_1'],[1309,3470,'10_2'],[3470,9000,'10_3']]
    CONFIG_IM = None
    for config in config_list:
        if config[0] < GID < config[1]:
            CONFIG_IM = config[2]
            break

    if config is None:
            raise Exception('find_config: no configuration found for GID=%s, may need to define a new configuration for your data' % (GID) )
    #print "find_config| DONE with func"
    return CONFIG_IM

for gab_coadd_fl in argv:
	if not 'gabodsid' in gab_coadd_fl or not gab_coadd_fl.endswith('coadd.fits'):
		raise Exception('this is for fixing gabodsid coadds')

	## python header keys
	dd=utilities.get_header_kw(gab_coadd_fl,['COND1'])

	if not 'GABODSID' in dd['COND1']:
	    raise Exception('this is for fixing gabodsid coadds')
	if 'AND' in dd['COND1']:
	    raise Exception('do this by hand or generalize this script to work with AND')
	COND1=dd['COND1']

	COND_gab=COND1.split('=')[-1]
	GABODSID=int(COND_gab.split(')')[0])
	CONFIG = find_config(GABODSID)
	gab_coadd_fo= pyfits.open(gab_coadd_fl,mode='update')
	gab_coadd_fo[0].header['CONFIG']=CONFIG
	gab_coadd_fo[0].header['GABODSID']=GABODSID
	gab_coadd_fo.verify('fix')
	gab_coadd_fo.flush()
	gab_coadd_fo.close()
