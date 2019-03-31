#! /usr/bin/env python
'''
setup_SUBARU.sh 
create_scamp_photom-middle_preview_dirs.py adam_add_GAIN_to_header_MACS1115.py adam_quicktools_fix_header_verify.py fixheaders_RXJ2129.py
my_cluster_params.py
#from simple_ic.py:
	
	CONFIG = find_config(dt['GABODSID'])
#maybe: adam_quicktools_fast_get_path_supa_chip_ending.py
#dfits /gpfs/slac/kipac/fs1/u/awright/SUBARU/*/W-*[A-Z+]/SCIENCE/*_3OCF*.fits | fitsort GABODSID GAIN CONFIG > all_gabodsid_gain_config.txt
'''
SUBARUDIR="/gpfs/slac/kipac/fs1/u/awright/SUBARU/"

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



def fl_printer(fls):
	for fl in fls:
		print '\t\t'+fl[len(SUBARUDIR)+1:]
#adam-SHNT#1)look at scribbled notes from yesterday
#adam-SHNT#3)make sure sextractor will get values from coadd.fits header!
#adam-SHNT#3)make sure to apply those masks for MACS0429!
#. SUBARU.ini
#. progs.ini
# get GABODSID        CONFIG          GAIN    SATURATION from /gpfs/slac/kipac/fs1/u/awright/SUBARU/*/W-*[A-Z+]/SCIENCE/*_3OCF*.fits, at least GABODSID is there for all of them!

def head_check(coadd_fl):
	coadd_fo= pyfits.open(coadd_fl)[0]
	head=coadd_fo.header
	csat=head['SATURATE']
	effgain=head['GAIN']
	exptime=head['EXPTIME']
	cgain=effgain/head['EXPTIME']
	printkeys=['EXPTIME','GAIN','CONFIG','GABODSID']
	for k in head.keys():
		if k.startswith('COND') or k in printkeys:
			print '\t\t\t',k,head[k]
	print '\t\t\t effgain/EXPTIME',cgain
	#SATURATE= INSTSAT[CONFIG]
	#GAIN= INSTGAIN[CONFIG]
	#change_needed = ( cgain!=GAIN )
	#if change_needed:

def fl_printer_head_check(fls):
	for fl in fls:
		print '\t\t'+fl[len(SUBARUDIR)+1:]
		head_check(fl)

INSTGAIN={}
INSTGAIN['10_3']=3.0
INSTGAIN['10_2']=2.5
INSTSAT={}
INSTSAT['10_3']=30000
INSTSAT['10_2']=27000

import glob,os
import utilities
import astropy.io.fits as pyfits
import astropy
from adam_quicktools_fast_get_path_supa_chip_ending import get_path_supa_chip_ending, get_supa_chip_endings_dict
from adam_quicktools_header_key_add import add_key_val
clusters=["MACS0429-02" ,"RXJ2129" ,"Zw2089"  ,"MACS1115+01"]
nocalib = lambda x: not 'CALIB' in x
for cluster in clusters:
	coadd_fls = filter(nocalib, glob.glob(SUBARUDIR+"/"+cluster+"/"+"W-*[A-Z+]/SCIENCE/coadd_"+cluster+"_all/coadd.fits"))
	for cfl in coadd_fls:
		problem_supa_coadd_fls=[]
		problem_gab_coadd_fls=[]
		fine_supa_coadd_fls=[]
		#print('\nSTARTING WITH %s' % cfl)
		cdir=os.path.dirname(cfl)
		supadir=cdir.rpartition('/')[0]
		coadd_fls_tmp = filter(nocalib, glob.glob(supadir+"/coadd_"+cluster+"_*/coadd.fits"))
		coadd_fls_other=filter( lambda x: not "coadd_"+cluster+"_gabodsid" in x and not x.endswith('all/coadd.fits') and not x.endswith('pretty/coadd.fits') and not "coadd_"+cluster+"_SUPA" in x , coadd_fls_tmp)
		coadd_fls_gab=filter( lambda x: "coadd_"+cluster+"_gabodsid" in x , coadd_fls_tmp)
		chip3_tmp=glob.glob(supadir+'/SUPA*_3OCF*.fits')
		fls_chip3=filter( lambda x: not x.endswith('sub.fits') ,chip3_tmp)
		paths,endings=get_supa_chip_endings_dict(fls_chip3)
		directory, supas = paths.popitem()
		configs_supas={'10_3':[],'10_2':[],'10_1':[],'8':[],'9':[]}
		configs_gabs={'10_3':[],'10_2':[],'10_1':[],'8':[],'9':[]}
		for supa,enddict in supas.iteritems():
			ending=max(enddict.keys(), key=len)
			supa_best_fl= directory+'/'+supa+'_'+enddict[ending][0]+ending+'.fits'
			supa_best_fo= pyfits.open( supa_best_fl)
			fitfo=supa_best_fo[0]

			gab = str(fitfo.header['GABODSID'])
			CONFIG = find_config(int(fitfo.header['GABODSID']))
			if 'CONFIG' in fitfo.header.keys():
				config = fitfo.header['CONFIG']
				assert(config==CONFIG)
			configs_supas[CONFIG].append(supa)
			configs_gabs[CONFIG].append(gab)
		for CONFIG in configs_supas.keys():
			for supa,gab in zip(configs_supas[CONFIG],configs_gabs[CONFIG]):
				supa_coadd_fl=supadir+"/coadd_"+cluster+"_"+supa+"/coadd.fits"
				try:
					supa_coadd_fo= pyfits.open(supa_coadd_fl,mode='update')
				except:
					#print 10*('cannot open '+supa_coadd_fl+'\n')
					continue
				supa_coadd_fo=supa_coadd_fo[0]
				head=supa_coadd_fo.header
				csat=head['SATURATE']
				effgain=head['GAIN']
				cgain=effgain/head['EXPTIME']
				SATURATE= INSTSAT[CONFIG]
				GAIN= INSTGAIN[CONFIG]
				change_needed = ( cgain!=GAIN )
				if change_needed:
						print 'PROBLEM: GAIN=',cgain,' should be ',GAIN,supa_coadd_fl
						print "head['SATURATE']*head['EXPTIME']=",head['SATURATE']*head['EXPTIME']
						problem_supa_coadd_fls.append(supa_coadd_fl)
						add_key_val(supa_coadd_fl,['GAIN','CONFIG'],[head['EXPTIME']*GAIN,CONFIG])

						for gab_coadd_fl in coadd_fls_gab:
							if gab_coadd_fl in problem_gab_coadd_fls:
								continue
							if gab in gab_coadd_fl:
								
								problem_gab_coadd_fls.append(gab_coadd_fl)
				else:
						#print 'FINE: GAIN=',cgain,' should be ',GAIN,supa_coadd_fl
						fine_supa_coadd_fls.append(supa_coadd_fl)

		if len(problem_supa_coadd_fls)>0:
			
			print('\nPROBLEMS!! FIX REQUIRED FOR  %s \n\t it has %s files that are FINE, they are:' % (cfl,len(fine_supa_coadd_fls)))
			fl_printer(fine_supa_coadd_fls)
			print('\t it needs these %s SUPA files fixed:\n' % (len(problem_supa_coadd_fls)))
			fl_printer(problem_supa_coadd_fls)
			#print('\t it needs these %s GAB files fixed:\n' % (len(problem_gab_coadd_fls)))
			#fl_printer_head_check(problem_gab_coadd_fls)
			print('\t these files might need fixing:\n')
			fl_printer_head_check(coadd_fls_other)
			if len(coadd_fls_other):
				for CONFIG in configs_supas.keys():
					nfls_at_conf=len(configs_supas[CONFIG])
					if nfls_at_conf>0:
						print '\t\t\t\t %s has # files =%s' % (CONFIG,nfls_at_conf)


			## check on GABODSID coadd too!
			
		else:
			print('\nAWESOME %s \n' % cfl)

#			SATURATE= INSTSAT[CONFIG]
#			GAIN= INSTGAIN[CONFIG]
#			#kws = utilities.get_header_kw(supa_best_fl,['OBJECT','GABODSID','CONFIG','EXPTIME','INSTRUM','SATURATE'])
#			#if kws['CONFIG']!='KEY_N/A':
#			#	assert(kws['CONFIG']==CONFIG)
#			#else:
#			#	supa_head['CONFIG']=CONFIG
#			#if kws['GAIN']!='KEY_N/A':
#			#	assert(kws['GAIN']==GAIN)
#			#else:
#			#	supa_head['GAIN']=GAIN
#			#if kws['SATURATE']!='KEY_N/A':
#			#	assert(kws['SATURATE']==SATURATE)
#			#else:
#			#	supa_head['SATURATE']=SATURATE
#
#                        config=fitfo.header['CONFIG']
#			assert(config==CONFIG)
#                        if not fitfo.header.__contains__('GAIN'):
#                                print cluster,filter,'lacks gain',fl
#                                if config=='10_3':
#                                        fitfo.header['GAIN']=3.0
#                                elif config=='10_2':
#                                        fitfo.header['GAIN']=2.5
#                                elif config=='10_1':
#                                        fitfo.header['GAIN']=2.5
#                                else:
#                                        raise Exception('CONFIG isnt 10_3 10_2 or 10_1 for fl='+fl)
#                        else:
#                                print 'adam-look',cluster,filter,'HAS GAIN',fl
#                        try:
#                                fitfl.close()
#                        except:
#                                print "adam-look TRY VERIFYING!"
#                                fitfo.verify('fix')
#                                fitfl.close() 
#		
#		#print supas
#		#if len(endings)>1:
#		#	print cluster, cfl, 'will be complicated'
#		#	print endings
#		#kws = utilities.get_header_kw(fl,['OBJECT','GABODSID','CONFIG','EXPTIME','INSTRUM','SATURATION'])
#		#CONFIG = find_config(kws['GABODSID'])
