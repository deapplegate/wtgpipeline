#! /usr/bin/env python
#adam-example# ./adam_bpz_wrapper.py 2>&1 | tee -a OUT-adam_bpz_wrapper_${cluster}.log
#adam-example# ipython -i adam_bpz_wrapper.py
#adam-does# This code is an adaptation of do_photometry.py, which doesn't use lephare at all, but uses the properly calibrated photometry to get photoz's using the "bpz.py" package
#ADVICE: when starting fresh with a new cluster. first search for #adam-Warning# in this code and change stuff whereever there is a #adam-Warning#

## INFO ON NEWEST BPZ WRAPPER AND HOW IT'S DIFFERENT FROM OLD ONES
## do_photometry.py do_multiple_photoz.py: original files that run bpz
## adam_do_photometry.py adam_do_multiple_photoz.py: my adaptations to make bpz work initially
## adam_bpz_wrapper.py: my most recent bpz running thing, which will incorporate elements of both adam_do_photometry.py and adam_do_multiple_photoz.py
## 	* will have HYBRID W-S-I+ mags in there
## 	* specific: allows you the option to change spec and ONLY_TYPE to use bpz primarily as a check on your magnitude ZP if you choose. Use these options
##		#adam-specz# iaper = 'ONLY_TYPE_non-specz_absent'
##		#adam-specz# spec = True
##		#adam-specz# ONLY_TYPE='yes' #Use only the redshift information instead of photo-z. Uses no priors on z, just fits for type.
##		#adam-specz# this option means the ascii catalog this code produces will consist solely of detections which have a matching spec-z
## 	* perhaps-SHNT: will do some experimenting with FC (vary between .05 and .9, just to see)
##		'ZC': None,
##		'FC':None,
## 	* perhaps: will do some experimenting with X/Y
## 	* perhaps: do some plotting like in adam_plot_bpz_output.py

#adam-note# python /nfs/slac/kipac/fs1/u/awright/InstallingSoftware_extension/bpz-1.99.3//bpz.py /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpzAPER1CWWSB_capak.list1_0.cat -COLUMNS /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/spec.APER1._aper.CWWSB_capak.list.cat.columns -MAG no -SPECTRA CWWSB_capak.list -PRIOR hdfn_SB -CHECK yes -PLOTS yes -VERBOSE no -ZMAX 4.0 -PLOTS yes -INTERP 8 -PROBS_LITE /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpzAPER1CWWSB_capak.list1_0.probs -OUTPUT /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpzAPER1CWWSB_capak.list1_0.bpz
#adam-note#  inputfile= /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.cat
#adam-note#  outputfile= /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.APER1.1.CWWSB_capak.list.all.EVERY.cat

#adam-BPZ-note# bpz fits for zp_offset every time, it never actually uses it that time through, it just allows you to change things for the next time if you want

## These environment variables should be set before running this code:
ns=globals()
import os,sys
env_vars=os.environ.keys()
vars_ok=True
if not os.environ['BPZPATH'] in os.environ['PYTHONPATH']:
	print "BPZPATH isn't in PYTHONPATH!"
	vars_ok=False
needed_keys=[ "cluster","BPZPATH","sne","INSTRUMENT","SUBARUDIR","subdir","subarudir","bonn","NUMERIX"]
for k in needed_keys:
	if not k in env_vars:
		print "NEED ENVIRONMENT VARIABLE: ",k
		vars_ok=False
if vars_ok==False:
	print "should run this first: . bpz.ini"
	sys.exit()
subarudir = os.environ['subdir']
cluster =  os.environ['cluster']

import re, string, numpy,scipy
from glob import glob
import astropy.io.fits as pyfits

#adam-Warning### inputs you might want to change
DETECT_FILTER="W-C-RC"
#this is the filter to use for "M_0", the mag most comparable to SDSS/2MASS/etc. deepest filter
M_0_filt="SUBARU-10_3-1-W-C-IC"
M_0_filt2="SUBARU-10_2-1-W-C-IC" #this is the backup filter to use for "M_0" if M_0_filt isn't available
#adam-tmp# M_0_filt="SUBARU-10_2-1-W-S-I+"
#adam-tmp# M_0_filt2="SUBARU-10_3-1-W-S-I+"
#Turns out I-band is a much closer match for BPZ prior
#adam-old##for MACS1115 we want: 'SUBARU-10_3-1-W-C-RC', 'SUBARU-10_2-1-W-C-RC'
#adam-old# M_0_filt="SUBARU-10_2-1-W-C-RC"
#adam-old# M_0_filt2="SUBARU-10_3-1-W-C-RC"

iaper = '1' #this is now just a tag I use where "1" just means nothing out of the ordinary. Probably used to mean something more significant. Other example: #adam-old# iaper = '1_M_0_Iband'
ONLY_TYPE="no" #if this is "yes", then you're essentially using bpz to evaluate how good your magnitude ZPs are (make sure spec=True)
spec = False
print 'inputs you might want to change: iaper =',iaper,' ONLY_TYPE=',ONLY_TYPE,' spec=',spec,' DETECT_FILTER=',DETECT_FILTER," M_0_filt=",M_0_filt," M_0_filt2=",M_0_filt2

## inputs you probably don't want to change
SPECTRA='CWWSB_capak.list' #SPECTRA options are: CWWSB_capak.list/CWWSB4.list/ZEBRA.list/CWWSB_capak_uz.list/CWWSB_capak_ub.list/CWWSB_capak_u.list/CWWSB4_txitxo.list
AP_TYPE = '_aper' #AP_TYPE options are: '_iso'
magflux = 'FLUX' #magflux is "FLUX" or "MAG", that's it
magtype = 'APER1' #magtype options are: 'ISO'; magtype = 'APER'
print 'inputs you probably dont want to change: SPECTRA=',SPECTRA,' AP_TYPE=',AP_TYPE,' magflux=',magflux,' magtype=',magtype

photdir = subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + AP_TYPE + '/'
bpzoutdir = photdir
#adam-tmp# bpzoutdir = photdir+ 'BPZ-prior_Imag-ZP_from_BPZ/'
if not os.path.isdir(bpzoutdir):
	os.makedirs(bpzoutdir)
#adam-new# changed this to the PureStarCalib version, which I think should be the file type we move forward with from now on#adam-Warning#
inputcat = photdir + cluster + '.calibrated_PureStarCalib.cat'
inputcat_alter_ldac = photdir + cluster + '.calibrated_PureStarCalib.alter.cat'
print ' inputcat=',inputcat , ' inputcat_alter_ldac=',inputcat_alter_ldac

def parsebpz(catalog):
    '''this makes the ascii cat into an ldaccat'''
    from utilities import run
    f = open(catalog,'r').readlines()
    keys = []
    for line in f:
        if line[0:2] == '# ':
            res2 = re.split('\s+',line[:-1])
            print res2
            keys.append('BPZ_' + res2[2])
        if line[0] != '#':
            break

    tempconf = '/tmp/' + os.environ['USER'] + 'photoz.conf'
    conflist = open(tempconf,'w')
    for key in keys:
        if key == 'BPZ_ID' :
            conflist.write('COL_NAME = SeqNr\nCOL_TTYPE = LONG\nCOL_HTYPE = INT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n')
        else:
            conflist.write('COL_NAME = ' + key + '\nCOL_TTYPE = DOUBLE\nCOL_HTYPE = FLOAT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n')
    conflist.close()
    tempcat = '/tmp/' + os.environ['USER'] + 'zs.cat'
    run('asctoldac -i ' + catalog + ' -o ' + catalog + '.tab' + ' -c ' + tempconf + ' -t STDTAB',[tempcat] )
    print catalog + '.tab'

def join_cats(cs,outputfile):
    tables = {}
    i = 0
    cols = []
    seqnr = 0
    for c in cs:
        if len(c) == 2:
            TAB = c[1]
            c = c[0]
        else: TAB = 'STDTAB'
        i += 1
        print c
        tables[str(i)] = pyfits.open(c)
        for column in  tables[str(i)][TAB].columns:
            if column.name == 'SeqNr':
                if not seqnr:
                    seqnr += 1
                else:
                    column.name = column.name + '_' + str(seqnr)
                    seqnr += 1

            cols.append(column)

    #print cols
    print len(cols)
    hdu = pyfits.PrimaryHDU()
    hduSTDTAB = pyfits.BinTableHDU.from_columns(cols)
    hdulist = pyfits.HDUList([hdu])
    hdulist.append(hduSTDTAB)
    hdulist[1].header['EXTNAME'] = 'STDTAB'
    os.system('rm ' + outputfile)
    print outputfile
    hdulist.writeto(outputfile)

def convert_to_mags(base,mag_cat,outputfile):

    ## see adam_plot_bpz_output.py for helpful plots of this stuff 
    print "convert_to_mags| mag_cat=",mag_cat
    mag = pyfits.open(mag_cat)[1]
    cat = base + '.bpz'

    purepath=sys.path
    addpath=[os.environ['BPZPATH']]+purepath
    sys.path=addpath
    from useful import ejecuta,get_header,put_header,get_str,put_str,get_data,get_2Darray,put_2Darray,params_file,params_commandline,view_keys,match_resol,overlap,match_objects,match_min,match_min2
    from coeio import loaddata, loadfile, params_cl, str2num, loaddict, findmatch1, pause  #, prange, plotconfig
    sys.path=purepath+['/u/ki/awright/InstallingSoftware/pythons/']

    bpzstr = loadfile(cat)
    bpzparams = {}
    i = 0
    while bpzstr[i][:2] == '##':
        line = bpzstr[i][2:]
        if '=' in line:
            [key, value] = string.split(line, '=')
            bpzparams[key] = value
        i = i + 1

    columns = bpzparams.get('COLUMNS', base+'.columns')
    flux_comparison = bpzparams.get('FLUX_COMPARISON', base+'.flux_comparison')
    zs=get_2Darray(cat) #Read the whole file

    all=get_2Darray(flux_comparison) #Read the whole file
    ncols=len(all[0,:])
    ''' need to get the number of filters '''
    nf=(ncols-5)/3
    filters=get_str(columns,0,nf)

    #print ' bpzparams["FLUX_COMPARISON"]=',bpzparams["FLUX_COMPARISON"]
    print 'convert_to_mags| zs=',zs
    print 'convert_to_mags| filters=',filters
    print 'convert_to_mags| len(all[:,0])=',len(all[:,0])
    print 'convert_to_mags| len(all[0,:])=',len(all[0,:])
    ''' need to retrieve the flux predicted, flux observed, and flux_error '''
    ID=scipy.array(all[:,0])  # FLUX (from spectrum for that TYPE)
    ft=scipy.array(all[:,5:5+nf])  # FLUX (from spectrum for that TYPE)
    fo=scipy.array(all[:,5+nf:5+2*nf])  # FLUX (OBSERVED)
    efo=scipy.array(all[:,5+2*nf:5+3*nf])  # FLUX_ERROR (OBSERVED)
    print 'convert_to_mags| len(ft)=',len(ft)
    print 'convert_to_mags| -2.5*scipy.log10(ft)=',-2.5*scipy.log10(ft)

    i = 0
    cols = []

    ''' if column not already there, then add it '''
    cols.append(pyfits.Column(name='SeqNr', format = 'J', array = ID))
    cols.append(pyfits.Column(name='NFILT', format = 'J', array = mag.data.field('NFILT')))
    ft_non0_spots=ft>0

    #adam-plots# in order to mkek the comparison plots (place notes below into func right here, or do ns.update(locals()) and paste into terminal)
    if 1: #adam-plots# here is how I made the comparison plots (put into func)
        from matplotlib.pylab import *
        import imagetools
        mag_info={}
        for i in range(len(filters)):
        	#print filters[i], i, ft[:,i]
        	for column in mag.columns:
        		#if 'MAG_APER1-' + filters[i] == column.name or 'MAG_APER-' + filters[i] == column.name:
        		if 'MAG_APER1-' + filters[i] == column.name:
        			if 'MAG_APER1-' + filters[i] == column.name: measured = mag.data.field('MAG_APER1-'+filters[i]).copy()
				#if 'MAG_APER-' + filters[i] == column.name: measured = mag.data.field('MAG_APER-'+filters[i])[:,1].copy()
        			measured_bad=(measured==-99)#+(measured==99)
        			measured_good=logical_not(measured_bad)
        			print column.name," measured_bad.sum(), measured_good.sum()=", measured_bad.sum(), measured_good.sum()
        			if measured_good.sum() > 0:
        				''' subsitute where there are -99 values '''
        				if not measured.shape==ft[:,i].shape: raise Exception('not measured.shape==ft[:,i].shape')

        				measured_b4=measured.copy()

					replace_spots=ft_non0_spots[:,i]*measured_bad
					if not replace_spots.any():
						print column.name, " no suitable replacements found"
						break

					ft_bads=-2.5*scipy.log10(ft[:,i][replace_spots])
        				measured_goods=measured[measured_good]
				        measured_final=measured.copy()
				        measured_final[replace_spots] =  -2.5*scipy.log10(ft[:,i][replace_spots])
					#only -99 right now #measured_final[measured_final==99] = -99
        				print column.name, "min/mean/max of measured_goods: ",measured_goods.min(),measured_goods.mean(),measured_goods.max()
        				mag_info[column.name]={}
        				mag_info[column.name]["measured_b4"]=measured_b4
        				mag_info[column.name]["measured_final"]=measured_final
        				mag_info[column.name]["measured_goods"]=measured_goods
        				mag_info[column.name]["ft_bads"]=ft_bads
        
        keys1=mag_info.keys()
        keys2=['measured_final', 'measured_goods', 'measured_b4','ft_bads']
        for k1 in keys1:
        	f=figure();f,axes=imagetools.AxesList(f,(2,2))
        	f.suptitle(k1)
        	for ax,k2 in zip(axes,keys2):
        		ax.set_title(k2)
        		ax.hist(mag_info[k1][k2],bins=100)
        	f.savefig("/u/ki/awright/wtgpipeline/plots/plt_do_multiple_photoz-"+k1)
    for i in range(len(filters)):
        print '\nfilters[i]=',filters[i] , ' i=',i , ' ft[:,i]=',ft[:,i]
        added = False
        for column in mag.columns:
            #adam-old# #if 'MAG_APER-' + filters[i] == column.name:
            if 'MAG_APER1-' + filters[i] == column.name:
                measured = mag.data.field('MAG_APER1-'+filters[i]).copy()
                #adam-old# measured = mag.data.field('MAG_APER-'+filters[i])[:,1]
		#adam-old# measured_bad=measured==-99
		#adam-old# measured_good=measured!=-99
		measured_bad=(measured==-99)#+(measured==99)
		measured_good=logical_not(measured_bad)
		print column.name," measured_bad.sum(), measured_good.sum()=", measured_bad.sum(), measured_good.sum()
                if measured_good.any(): #if any good dets
                    ''' subsitute where there are -99 values '''
		    if not measured.shape==ft[:,i].shape: raise Exception('not measured.shape==ft[:,i].shape')
                    print column.name, "measured.shape=",measured.shape
                    #adam: we want values that are measured==-99 and ft's corresponding spots are ft!=0
                    replace_spots=ft_non0_spots[:,i]*measured_bad
                    if not replace_spots.any():
			    print column.name, " no suitable replacements found"
		            break
                    measured_final=measured.copy()
                    measured_final[replace_spots] =  -2.5*scipy.log10(ft[:,i][replace_spots])
                    ft_bads=-2.5*scipy.log10(ft[:,i][replace_spots])
		    #only -99 right now# measured_final[measured_final==99] = -99
		    print column.name, "min/mean/max of measured_final: ",measured_final.min(),measured_final.mean(),measured_final.max()
		    print column.name, "min/mean/max of ft_bads: ",ft_bads.min(),ft_bads.mean(),ft_bads.max()
                    cols.append(pyfits.Column(name='HYBRID_MAG_APER1-' + filters[i], format = '1E', array = measured_final))
                    added = True
                    print column.name, 'measured', filters[i]
                    break

        if not added: #if no good dets, then all HYBRID_MAG is bpz_MAG (this makes perfect sense, but hopefully we never run into this!
	    print 'BETTER BE W-S-I+ here. Sextractor measured MAG_APER1-'+filters[i]+' has NO good detections, so HYBRID_MAG_APER1-'+filters[i]+' will be ENTIRELY based on bpz output magnitudes!'
            cols.append(pyfits.Column(name='HYBRID_MAG_APER1-'+filters[i], format = '1E', array = -2.5*scipy.log10(ft[:,i])))

    cols_dont_double=[]
    for column_name in mag.columns.names:
        if string.find(column_name,'MAG') == -1 and string.find(column_name,'FLUX') != -1:#if it has "FLUX" and doesn't have "MAG" in it
            col_to='DATA_' + column_name.replace('FLUX','MAG')
            cols_dont_double.append(col_to)

    for ii,(column_name,column_format) in enumerate(zip(mag.columns.names,mag.columns.formats)):
        if string.find(column_name,'MAG') == -1 and string.find(column_name,'FLUX') != -1:#if it has "FLUX" and doesn't have "MAG" in it
            col_to='DATA_' + column_name.replace('FLUX','MAG')
	    a = -2.5*scipy.log10(mag.data.field(column_name))
	    a[mag.data.field(column_name) == 0] = -99
	    cols.append(pyfits.Column(name='DATA_' + column_name.replace('FLUX','MAG'), format = column_format, array = a))
        else:
            col_to='DATA_' + column_name
            if col_to in cols_dont_double:
                    continue
	    a = mag.data.field(column_name)
	    cols.append(pyfits.Column(name='DATA_' + column_name, format = column_format, array = a))

    print ' len(cols)=',len(cols)
    #adam-fixed# There are duplicate columns apparently!
    hdu = pyfits.PrimaryHDU()
    hduSTDTAB = pyfits.BinTableHDU.from_columns(cols)
    hdulist = pyfits.HDUList([hdu])
    hdulist.append(hduSTDTAB)
    hdulist[1].header['EXTNAME']='OBJECTS'
    print ' outputfile=',outputfile
    hdulist.writeto(outputfile,overwrite=True)
    #ns.update(locals())

def add_dummy_ifilter(catalog, outputfile):
    ''' This puts SeqNr in the first column. And it drops the "APER-" columns while keeping the "APER1-" columns
	NEW : This function in also adds "new Subaru W-S-I+ filter" in there if it's not there already '''

    cols = []
    tables = pyfits.open(catalog)['OBJECTS']

    for col in ['SeqNr']:
	array = tables.data.field(col)
	arshape = array.shape
        cols.append(pyfits.Column(name=col, format = 'J', array = array))

    already_there=False
    for column in tables.columns:
        if column.name=='SeqNr':continue
        if "APER-" in column.name:
		print outputfile+" won't contain this column: ",column.name
		continue
	if "W-S-I+" in column.name:
		already_there=True
        cols.append(column)

    #what to do if W-S-I+ isn't there. Add in flux=0 and fluxerr=0 
    if already_there==False:
	#all would be non-observations (nonobs==0 for bpz and nonobs==-99 for sextractor flux/mag/fluxerr/magerr
        cols.append(pyfits.Column(name="MAG_APER1-SUBARU-10_3-1-W-S-I+",format='1E',array=numpy.zeros(arshape)-99))
        cols.append(pyfits.Column(name="MAGERR_APER1-SUBARU-10_3-1-W-S-I+",format='1E',array=numpy.zeros(arshape)))
        cols.append(pyfits.Column(name="FLUX_APER1-SUBARU-10_3-1-W-S-I+",format='1E',array=numpy.zeros(arshape)-99))
        cols.append(pyfits.Column(name="FLUXERR_APER1-SUBARU-10_3-1-W-S-I+",format='1E',array=numpy.zeros(arshape)-99))
        cols.append(pyfits.Column(name="FLUX_APER1-SUBARU-10_3-1-W-S-I+_bpz_inputs",format='1E',array=numpy.zeros(arshape)))
        cols.append(pyfits.Column(name="FLUXERR_APER1-SUBARU-10_3-1-W-S-I+_bpz_inputs",format='1E',array=numpy.zeros(arshape)))
    print 'add_dummy_ifilter| len(cols)=',len(cols)
    hdu = pyfits.PrimaryHDU()
    #old#hduSTDTAB = pyfits.BinTableHDU.from_columns(cols)
    hduSTDTAB = pyfits.BinTableHDU.from_columns(cols)
    hdulist = pyfits.HDUList([hdu,hduSTDTAB])
    hdulist[1].header['EXTNAME']='OBJECTS'
    print 'add_dummy_ifilter| outputfile=',outputfile
    hdulist.writeto(outputfile,overwrite=True)

def get_filters(cat,tab='STDTAB',SPECTRA=None):
    filters=[]
    p = pyfits.open(cat)
    for column in p[tab].columns:
        res = re.split('-',column.name)
        use = False
        if len(res) > 1 and string.find(column.name,'W-J-U') == -1 and string.find(column.name,'FWHM')==-1 and string.find(column.name,'COADD')==-1 and string.find(column.name,'MAG')!=-1 and string.find(column.name,'--')==-1:
            if SPECTRA == 'CWWSB_capak_ubvriz.list':
                use = len(filter(lambda x:x,[string.find(column.name,f)!=-1 for f in ['-u','W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']]))
            elif SPECTRA == 'CWWSB_capak_u.list':
                use = len(filter(lambda x:x,[string.find(column.name,f)!=-1 for f in ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']]))
            elif SPECTRA == 'CWWSB_capak_ub.list':
                use = len(filter(lambda x:x,[string.find(column.name,f)!=-1 for f in ['W-J-V','W-C-RC','W-S-I+','W-C-IC','W-S-Z+']]))
            elif SPECTRA == 'CWWSB_capak_uz.list':
                use = len(filter(lambda x:x,[string.find(column.name,f)!=-1 for f in ['W-J-B','W-J-V','W-C-RC','W-C-IC']]))
            else:
                use = True

            if string.find(column.name,'SUBARU') != -1 and (string.find(column.name,'10') == -1 and string.find(column.name,'9') == -1) and string.find(column.name,'8')==-1:
                use = False
            if string.find(column.name,'MEGAPRIME') != -1 and (string.find(column.name,'1') == -1 and string.find(column.name,'0') == -1):
                use = False
            if string.find(cat,'A370') != -1 and (string.find(column.name,'W-S-I+') != -1 or string.find(column.name,'8') != -1):
                use = False
            if string.find(cat, 'HDFN') != -1 and (string.find(column.name,'SUBARU-9') != -1 or string.find(column.name,'W-S-I+')!= -1 or string.find(column.name,'-2-') != -1): # or string.find(column.name,'u') != -1):
                use = False
            if string.find(cat,'A383') != -1 and (string.find(column.name,'u') != -1): # or string.find(column.name,'W-J-V') != -1):
                use = False

            ''' remove WHT data, and u-band data '''
            if string.find(column.name,'WH') != -1 or string.find(column.name,'u') != -1 or string.find(column.name,'-U') != -1: # or string.find(column.name,'B') != -1: # or (string.find(column.name,'B') != -1 and string.find(column.name,'9') != -1): # is False:
                use = False

        if use:
            try:
                dummy = int(res[-1])
            except:
                filt = reduce(lambda x,y: x+'-'+y,res[1:])
                filters.append(filt)
    fl=set(filters)
    filters=list(fl)
    print 'filters=',filters
    return filters

print "running: add_dummy_ifilter(inputcat,inputcat_alter_ldac)"
add_dummy_ifilter(inputcat,inputcat_alter_ldac)

filterlist = get_filters(inputcat_alter_ldac,'OBJECTS',SPECTRA=SPECTRA)
print ' filterlist=',filterlist , ' len(filterlist)=',len(filterlist)

## make the bpz columns and bpz input file
inputcat_alter_ascii= bpzoutdir + cluster + '.bpz_input.txt'
columns_fl= bpzoutdir + cluster + '.bpz.columns'
columns_fo= open(columns_fl,'w')
columns_num=2
ascii_cat_keys=["SeqNr"]
M_0_key=None #this gets set in the loop
M_0_key2=None #this gets set in the loop
for filt in filterlist:
	filt_col=[filt,'%i,%i' % (columns_num,1+columns_num),'AB','0.02','0.0\n']
	columns_fo.write('\t'.join(filt_col))
	ascii_cat_keys.append("FLUX_APER1-"+filt+"_bpz_inputs")
	ascii_cat_keys.append("FLUXERR_APER1-"+filt+"_bpz_inputs")
	columns_num+=2
	if M_0_filt in filt:
		M_0_key=filt
	if M_0_filt2 in filt:
		M_0_key2=filt

if M_0_key==None:
	raise Exception("the filter %s used for M_0 didn't show up in filterlist" % (M_0_filt))
else:
	ascii_cat_keys.append("MAG_APER1-"+M_0_key)
if M_0_key2==None: #raise exception for now, but in practice this backup filter isn't needed
	raise Exception("the backup filter %s used for M_0 didn't show up in filterlist, can change it to something else or drop it alltogether" % (M_0_filt2))
	print "the backup filter %s used for M_0 didn't show up in filterlist, can change it to something else or drop it alltogether" % (M_0_filt2)
else:
	ascii_cat_keys.append("MAG_APER1-"+M_0_key2)

columns_fo.write('\t'.join(['ID','1\n']))
columns_fo.write('\t'.join(['M_0',str(columns_num)+'\n']))
if spec:
	columns_num+=1
	columns_fo.write('\t'.join(['Z_S',str(columns_num)+'\n']))
	#ascii_cat_keys.append("Z_S")
columns_fo.close()

command="ldactoasc -i %s -t OBJECTS -s -b -k %s > %s" % (inputcat_alter_ldac,' '.join(ascii_cat_keys),inputcat_alter_ascii)
print "command=",command
ooo=os.system(command)
if ooo!=0: raise Exception("the line os.system(ldactoasc...) failed")

## FIX M_0 column: if there is a backup magnitude for M_0, then it has to be put into the spots where the original filter is undefined
import astropy
from astropy.io import ascii
if M_0_key2!=None:
	key1="MAG_APER1-"+M_0_key
	key2="MAG_APER1-"+M_0_key2
	## including Z_S in the bpz input ascii file (should have entirely objects with Z_S)
	Icat=ascii.read(inputcat_alter_ascii,names=ascii_cat_keys)
	M1=Icat[key1].data
	M2=Icat[key2].data
	## make new cat starting from a copy of the original
	Fcat=Icat.copy()
	badM1=M1<0
	goodM2=M2>0
	replaceM1=numpy.logical_and(badM1,goodM2)
	print "of the %s detections missing a mag in %s, we're going to replace %s of them with a mag in %s" % (badM1.sum(),M_0_key,replaceM1.sum(),M_0_key2)
	Fcat.remove_columns([key1,key2])
	Mfinal=numpy.where(replaceM1,M2,M1)
	Mfinal_col=astropy.table.column.Column(data=Mfinal,name="M_0")
	Fcat.add_column(Mfinal_col)
	Fcat.write(inputcat_alter_ascii+".tmp",format="ascii.no_header")
	os.system('mv %s %s' % (inputcat_alter_ascii+".tmp",inputcat_alter_ascii))
	ascii_cat_keys.remove(key1)
	ascii_cat_keys.remove(key2)
	ascii_cat_keys.append("M_0")

## INCLUDE Z_S column: put spec-zs in the bpz input ascii file (should have entirely objects with Z_S)
#adam-Warning# may want to mess with this if I've got spectra
if spec: #adam-specz#
	Icat=ascii.read(inputcat_alter_ascii,names=ascii_cat_keys)
	spec_file="/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/match_specz_and_bpz_cats.txt"
	Scat=ascii.read(spec_file)
	Sid=Scat['SeqNr'].data
	Iid=Icat['SeqNr'].data
	## make new cat starting from a copy of the original
	IScat=Icat.copy()
	sIid=set(Iid);sSid=set(Sid)
	# get rid of columns without specz
	Rid=numpy.array(list(sIid.difference(sSid)))
	IScat.remove_rows(Rid-1)
	#set(IScat['SeqNr'].data)==sSid
	Szs=Scat['z'].data
	specz=Szs[Sid.argsort()] #sort zs in order of increasing SeqNr
	# write new cat with added column and overwrite previous cat
	specz_col=astropy.table.column.Column(data=specz,name="Z_S")
	IScat.add_column(specz_col)
	IScat.write(inputcat_alter_ascii+".tmp",format="ascii.no_header")
	os.system('mv %s %s' % (inputcat_alter_ascii+".tmp",inputcat_alter_ascii))
	if 0: ## this is (I'm pretty sure) the wrong way to do things, but it might be useful for using bpz.py to plot specz vs. bpz_z or for having Z_S in the catalogs or something like that in the future
		zs=numpy.zeros(Iid.shape)-99
		Szs=Scat['z'].data
		zs[Sid-1]=Szs #Iid[Sid-1]==Sid
		zs_fl= photdir + cluster + '.redshifts.tmp'
		zs_fo= open(zs_fl,'w')
		#first call is SeqNr and 2nd col is Z, so loop over other file's SeqNr's, where it matches an SeqNr from this file, include the specz, where it doesn't, put in a +99
		for zspec in zs:
			zs_fo.write('%.3f \n' % (zspec))
		zs_fo.close()
		os.system('paste %s %s > %s/out.tmp' % (inputcat_alter_ascii,zs_fl, photdir))
		os.system('rm %s' % (zs_fl))
		os.system('mv %s/out.tmp %s' % (photdir,inputcat_alter_ascii))

print 'inputs for do_bpz: '
print '\tcluster: '+cluster 
print '\tDETECT_FILTER: '+DETECT_FILTER 
print '\tAP_TYPE: '+AP_TYPE 
print '\tfilterlist: ',filterlist 
print '\tinputcat_alter_ascii: ',inputcat_alter_ascii 
print '\tinputcat_alter_ldac: ',inputcat_alter_ldac 
print '\tspec: ',spec 
print '\tSPECTRA: ',SPECTRA 
print '\tmagtype: ',magtype 
print '\tmagflux: ',magflux 
print '\tONLY_TYPE: ',ONLY_TYPE 
print '\tinputcolumns: ',columns_fl 


def do_bpz(CLUSTER,DETECT_FILTER,AP_TYPE,filters,inputcat_alter_ascii,inputcat_alter_ldac, spec,SPECTRA,magtype='APER1',magflux='FLUX',ONLY_TYPE='no',inputcolumns=False):
	try:
	    SUBARUDIR=os.environ['SUBARUDIR']
	    dict = { 'SUBARUDIR':SUBARUDIR,
		'PHOTOMETRYDIR': 'PHOTOMETRY_' + DETECT_FILTER + AP_TYPE,
		'AP_TYPE': AP_TYPE,
		'ONLY_TYPE': ONLY_TYPE,
		'CLUSTER':CLUSTER,
		'BPZPATH':os.environ['BPZPATH'],
		'iaper':iaper,
		'magtype':magtype }

	    if len(filters) > 4: dict['INTERP'] = '8'
	    else: dict['INTERP'] = '0'

	    dict['SPECTRA'] = SPECTRA #'CWWSB_capak.list' # use Peter Capak's SEDs #dict['SPECTRA'] = 'CWWSB4.list' #dict['SPECTRA'] = 'CFHTLS_MOD.list'

	    for z in filters:
		f = '' + z + '.res'
		#print ' os.environ["BPZPATH"]+"/FILTER/"+f=',os.environ["BPZPATH"]+"/FILTER/"+f
		print ' glob(os.environ["BPZPATH"]+"/FILTER/"+f)=',glob(os.environ["BPZPATH"]+"/FILTER/"+f)
		if len(glob(os.environ['BPZPATH'] + '/FILTER/' + f)) == 0:
		    print 'couldnt find filter!!!'
		    raise Exception("no file of the name: os.environ['BPZPATH']+'/FILTER/'+f="+os.environ['BPZPATH'] + '/FILTER/' + f+" found!")

	    if bpzoutdir == photdir:
		base = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(iaper)s.%(SPECTRA)s.all' % dict
	    else:
		base = bpzoutdir + '%(CLUSTER)s.%(magtype)s.%(iaper)s.%(SPECTRA)s.all' % dict
	    dict['columns'] = base + '.columns'
	    if inputcolumns:
		    command_cp_columns=' '.join(["cp",inputcolumns,dict['columns']])
		    print "command_cp_columns=",command_cp_columns
		    ooo=os.system(command_cp_columns)
		    if ooo!=0: raise Exception("os.system failed!!!")

	    incat = base + '.cat'
	    catalog = base + '.bpz'
	    prob = base + '.probs'
	    flux = base + '.flux_comparison'
	    dict['catalog'] = catalog
	    dict['incat'] = incat
	    dict['prob'] = prob

	    command_cp_cat=' '.join(["cp",inputcat_alter_ascii,incat])
	    print "command_cp_cat=",command_cp_cat
	    ooo=os.system(command_cp_cat)
	    if ooo!=0: raise Exception("os.system failed!!!")

	    if magflux == 'FLUX': dict['magvar'] = 'no'
	    else: dict['magvar'] = 'yes'

	    #if pars.d['ONLY_TYPE']=='yes': #Use only the redshift information, no priors
	    # 
	    
	    command = 'python %(BPZPATH)s/bpz.py %(incat)s \
	    -COLUMNS %(columns)s \
	    -MAG %(magvar)s \
	    -SPECTRA %(SPECTRA)s \
	    -ONLY_TYPE %(ONLY_TYPE)s \
	    -PRIOR hdfn_SB \
	    -CHECK yes \
	    -PLOTS yes \
	    -VERBOSE yes \
	    -ZMAX 4.0 \
	    -INTERP %(INTERP)s \
	    -INTERACTIVE no \
	    -PROBS_LITE %(prob)s \
	    -OUTPUT %(catalog)s' % dict
	    #adam-changed# -VERBOSE yes \
	    #adam-changed# -INTERACTIVE no \
	    #adam-changed# -NEW_AB yes 
	    
	    print ' command=',command
	    ooo=os.system(command)
	    if ooo!=0: 
		ns.update(locals()) #adam-tmp#
		raise Exception("os.system failed!!!")
	    
	    print "adam-look: running parsebpz(catalog=",catalog,")"
	    parsebpz(catalog) #outputs ldac cat named catalog+".tab"
	    #adam-comment# parsebpz takes catalog and makes catalog+".tab", which is in ldac format
	    
	    ''' join the tables '''
	    output = base + '.input_and_bpz.tab'
	    join_cats([catalog+'.tab',(inputcat_alter_ldac,"OBJECTS")],output)
	    #adam-comment# now output = base + '.bpz.tab' has combination of all cats in "STDTAB" table and inputcat in "OBJECTS" table all in the one output["STDTAB"] table!
	    print ' output=',output

	    convert_to_mags(base,output,base+'.EVERY.cat')
	    ns.update(locals()) #adam-tmp#
	    #adam-expanded# convert_to_mags("/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.APER1.1.CWWSB_capak.list.all" , "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21." , "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.APER1.1.CWWSB_capak.list.all.EVERY.cat")

	    #adam-Warning# Other codes might use different final cats/output besides *EVERY.cat
	    #for example they might look for:
	    #	output_catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(iaper)s.photoz.%(SPECTRA)s.%(calib_type)s.tab' % dict
	    #cutout_bpz.make_thecorrections actually uses these:
	    #	outputcat = '%(path)s/PHOTOMETRY_%(DETECT_FILTER)s%(AP_TYPE)s/%(cluster)s.%(magtype)s.1.%(SPECTRA)s.bpz.bpz.tab' % params 
	    #	catalog = '%(path)s/PHOTOMETRY_%(DETECT_FILTER)s%(AP_TYPE)s/%(cluster)s.slr.cat' %params           
	    #	starcatalog = '%(path)s/PHOTOMETRY_%(DETECT_FILTER)s%(AP_TYPE)s/%(cluster)s.stars.calibrated.cat' %params           

	except:
	    ns.update(locals()) #adam-tmp#
	    raise

#adam-old# adam_do_multiple_photoz.do_bpz(cluster,DETECT_FILTER, AP_TYPE, filterlist,inputcat_alter_ldac, calib_type,spec,SPECTRA, magtype=magtype,magflux=magflux,ONLY_TYPE=ONLY_TYPE)
do_bpz(cluster,DETECT_FILTER, AP_TYPE, filterlist,inputcat_alter_ascii,inputcat_alter_ldac, spec,SPECTRA, magtype=magtype,magflux=magflux,ONLY_TYPE=ONLY_TYPE,inputcolumns=columns_fl)

# adam # might want to use cutout_bpz.py to make the cutout images
#########import cutout_bpz
#########cutout_bpz.run(cluster)
#########os.system('python cutout_bpz.py ' + cluster + ' spec')
print 'TO SAVE OUTPUT ZP fits: grep -A 12 "PHOTOMETRIC CALIBRATION TESTS" OUT-bpz_lasttime.log > adam_bpz_fit_ZPs-without_specz.log'
print "for more info, run this: python $BPZPATH/bpzfinalize.py %s" % (base)
#Includes calculation of modified chisq (chisq2) plus different formatting #Important: Check your results including SED fits and P(z)
print "for more info, run this: python $BPZPATH/plots/webpage.py %s i2000-2063 -DIR /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/bpz_html_sex2mag" % (base)
print "for plots, run this: adam_plot_bpz_output.py"
if not os.path.isdir( photdir + "/bpz_html_sex2mag"):
	os.makedirs( photdir + "/bpz_html_sex2mag")
os.system("python %s/bpzfinalize.py %s" % (os.environ['BPZPATH'],base))
os.system("python %s/plots/webpage.py %s i2000-2063 -DIR %s" % (os.environ['BPZPATH'],base,photdir + "/bpz_html_sex2mag"))
