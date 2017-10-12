#!/usr/bin/env python
import os
import astropy.io.fits as pyfits
ns_dmp=globals()
def parse_column_file(input,output=None,offsets=None):
    f = open(input,'r').readlines()

    dict = {}
    for l in f:
        import re
        res = re .split('\s+',l)
        print res
        if len(res) > 3:
            t = {}
            t['cols'] = res[1]
            t['offset'] = float(res[4])
            dict[res[0]] = t
        else:
            dict[res[0]] = {'cols':res[1]}

    if offsets:
        for key in dict:
            if key in offsets:
                dict[key]['offset'] += offsets[key]

    if not output: output = input + '.new'


    o = open(input,'w')
    for key in dict:
        if 'offset' in dict[key]:
            o.write(key + '\t' + dict[key]['cols'] + '\tAB\t0.02\t' + str(dict[key]['offset']) + '\n')
        else:
            o.write(key + '\t' + dict[key]['cols'] + '\n')
    o.close()

def fit_zps(dictionary):
    dictionary['INTERP'] = 0

    command = 'python %(BPZPATH)s/bpz.py %(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all_bpz%(magtype)s%(SPECTRA)s%(iaper)s_%(n)s.cat \
        -COLUMNS %(columns)s \
        -MAG %(magvar)s \
        -SPECTRA %(SPECTRA)s \
        -PRIOR hdfn_SB \
        -CHECK yes \
        -PLOTS yes  \
        -VERBOSE yes \
        -ZMAX 4.0 \
        -PLOTS yes \
        -INTERP %(INTERP)s \
    -INTERACTIVE yes \
    -ONLY_TYPE yes \
        -OUTPUT %(catalog)s' % dictionary
    print ' command=',command

    import commands

    for i in range(1):
        import os
        os.system('cat ' + dictionary['columns'])
        print 'running'
        f = commands.getoutput(command).split('\n')

        print ' f=',f
        go = False
        index = 0
        import string
        offsets = {}
        for i in range(len(f)):
            print f[i]
            if string.find(f[i],'Average') != -1:
                import re
                filts = re.split('\s+',f[i+1])[1:]
                deltas = [float(x) for x in re.split('\s+',f[i+4])[1:-1]]
                offsets = dict(zip(filts,deltas))
                break
        print ' offsets=',offsets
        print dictionary['columns']
        parse_column_file(dictionary['columns'],offsets=offsets)
    #raw_input('finished fit_zps')

def convert_to_mags(run_name,mag_cat,outputfile):

    ## see adam_plot_bpz_output.py for helpful plots of this stuff 
    import string,os,sys
    print "mag_cat=",mag_cat
    mag = pyfits.open(mag_cat)[1]
    cat = run_name + '.bpz'

    purepath=sys.path
    addpath=[os.environ['BPZPATH']]+purepath
    sys.path=addpath
    from useful import *
    from coeio import loaddata, loadfile, params_cl, str2num, loaddict, findmatch1, pause  #, prange, plotconfig
    sys.path=purepath

    bpzstr = loadfile(cat)
    bpzparams = {}
    i = 0
    while bpzstr[i][:2] == '##':
        line = bpzstr[i][2:]
        if '=' in line:
            [key, value] = string.split(line, '=')
            bpzparams[key] = value
        i = i + 1

    columns = bpzparams.get('COLUMNS', run_name+'.columns')
    flux_comparison = bpzparams.get('FLUX_COMPARISON', run_name+'.flux_comparison')
    zs=get_2Darray(cat) #Read the whole file

    all=get_2Darray(flux_comparison) #Read the whole file
    ncols=len(all[0,:])
    ''' need to get the number of filters '''
    nf=(ncols-5)/3
    filters=get_str(columns,0,nf)

    #print ' bpzparams["FLUX_COMPARISON"]=',bpzparams["FLUX_COMPARISON"]
    print ' zs=',zs
    print ' filters=',filters
    print ' len(all[:,0])=',len(all[:,0])
    print ' len(all[0,:])=',len(all[0,:])
    ''' need to retrieve the flux predicted, flux observed, and flux_error '''
    import numpy,scipy
    ID=scipy.array(all[:,0])  # FLUX (from spectrum for that TYPE)
    ft=scipy.array(all[:,5:5+nf])  # FLUX (from spectrum for that TYPE)
    fo=scipy.array(all[:,5+nf:5+2*nf])  # FLUX (OBSERVED)
    efo=scipy.array(all[:,5+2*nf:5+3*nf])  # FLUX_ERROR (OBSERVED)
    print ' len(ft)=',len(ft)
    print ' -2.5*scipy.log10(ft)=',-2.5*scipy.log10(ft)

    i = 0
    cols = []

    ''' if column not already there, then add it '''
    cols.append(pyfits.Column(name='SeqNr', format = 'J', array = ID))
    cols.append(pyfits.Column(name='NFILT', format = 'J', array = mag.data.field('NFILT')))
    ft_non0_spots=ft>0

    #adam-plots# in order to mkek the comparison plots (place notes below into func right here, or do ns_dmp.update(locals()) and paste into terminal)
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
        	f.savefig("/u/ki/awright/bonnpipeline/plots/plt_do_multiple_photoz-"+k1)
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
	    print 'adam-look-Error: hit "if not added" portion of "convert_to_mags" function in "adam_do_multiple_photoz.py"\nadam-look-Error: sextractor measured MAG_APER1-'+filters[i]+' has NO good detections, so HYBRID_MAG_APER1-'+filters[i]+' will be ENTIRELY based on bpz output magnitudes!'
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
    #ns_dmp.update(locals()) #adam-tmp#

def add_dummy_ifilter(catalog, outputfile):

    import numpy
    i = 0
    cols = []
    tables = pyfits.open(catalog)['OBJECTS']

    for col in ['SeqNr']:
        cols.append(pyfits.Column(name=col, format = 'J', array = tables.data.field(col)))

    already_there = False
    for column in tables.columns:
        cols.append(column)
        if column.name == 'FLUX_APER1-SUBARU-10_2-1-W-S-I+':
            already_there = True

    ''' if column not already there, then add it STILL NEED TO IMPLEMENT !!! '''
    rows = len(pyfits.open(catalog)['OBJECTS'].data)
    if not already_there:
        cols.append(pyfits.Column(name='FLUX_APER0-SUBARU-10_2-1-W-S-I+', format = '1E', array = numpy.zeros(rows)))
        cols.append(pyfits.Column(name='FLUXERR_APER0-SUBARU-10_2-1-W-S-I+', format = '1E', array = numpy.zeros(rows)))
        cols.append(pyfits.Column(name='FLUX_APER1-SUBARU-10_2-1-W-S-I+', format = '1E', array = numpy.zeros(rows)))
        cols.append(pyfits.Column(name='FLUXERR_APER1-SUBARU-10_2-1-W-S-I+', format = '1E', array = numpy.zeros(rows)))
        cols.append(pyfits.Column(name='MAG_APER0-SUBARU-10_2-1-W-S-I+', format = '1E', array = numpy.zeros(rows)))
        cols.append(pyfits.Column(name='MAGERR_APER0-SUBARU-10_2-1-W-S-I+', format = '1E', array = numpy.zeros(rows)))
        cols.append(pyfits.Column(name='MAG_APER1-SUBARU-10_2-1-W-S-I+', format = '1E', array = numpy.zeros(rows)))
        cols.append(pyfits.Column(name='MAGERR_APER1-SUBARU-10_2-1-W-S-I+', format = '1E', array = numpy.zeros(rows)))
	#adam-SHNT# Ok, so this just puts the cols in there as zeros and leaves it up to "convert_to_mags" to calculate the "HYBRID" versions, how does that work??







    #print ' cols=',cols
    print ' len(cols)=',len(cols)
    hdu = pyfits.PrimaryHDU()
    hduSTDTAB = pyfits.BinTableHDU.from_columns(cols)
    hdulist = pyfits.HDUList([hdu])
    hdulist.append(hduSTDTAB)
    hdulist[1].header['EXTNAME']='OBJECTS'
    import os
    os.system('rm ' + outputfile)
    print ' outputfile=',outputfile
    hdulist.writeto(outputfile)

def add_dummy_filters(catalog, outputfile):

    add_filters =['MEGAPRIME-0-1-g','MEGAPRIME-0-1-r','MEGAPRIME-0-1-i','MEGAPRIME-0-1-z','SUBARU-10_2-1-W-S-G+','SUBARU-10_2-1-W-C-RC','SUBARU-10_2-1-W-C-IC']

    use_filters = ['MEGAPRIME-0-1-u','SUBARU-10_2-1-W-J-B','SUBARU-10_2-1-W-J-V','SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-S-I+','SUBARU-10_2-1-W-S-Z+']

    import numpy
    i = 0
    cols = []
    tables = pyfits.open(catalog)['OBJECTS']

    for col in ['SeqNr','B_mask','V_mask','i_mask','z_mask']:
        cols.append(pyfits.Column(name=col, format = 'J', array = tables.data.field(col)))

    for filt in use_filters: # tables[str(i)]['OBJECTS'].columns:
        cols.append(pyfits.Column(name='MAG_APER-'+filt, format = '1E', array = tables.data.field('MAG_APER-'+filt)))
        cols.append(pyfits.Column(name='MAGERR_APER-'+filt, format = '1E', array = tables.data.field('MAGERR_APER-'+filt)))

    ''' if column not already there, then add it STILL NEED TO IMPLEMENT !!! '''
    rows = len(pyfits.open(catalog)['OBJECTS'].data)
    for filt in add_filters:
        cols.append(pyfits.Column(name='MAG_APER-'+filt, format = '1E', array = -99.*numpy.ones(rows)))
        cols.append(pyfits.Column(name='MAGERR_APER-'+filt, format = '1E', array = 99.*numpy.ones(rows)))

    print ' len(cols)=',len(cols)
    hdu = pyfits.PrimaryHDU()
    hduSTDTAB = pyfits.BinTableHDU.from_columns(cols)
    hdulist = pyfits.HDUList([hdu])
    hdulist.append(hduSTDTAB)
    hdulist[1].header['EXTNAME']='OBJECTS'
    import os
    os.system('rm ' + outputfile)
    print ' outputfile=',outputfile
    hdulist.writeto(outputfile)

def mkplot(file,name):
    import MySQLdb
    import os, sys, anydbm, time
    import lib, scipy, pylab
    from scipy import arange

    file = open(file,'r').readlines()
    results = []
    for line in file:
        if line[0] != '#':
            import re
            res = re.split('\s+',line)
            #for i in range(len(res)):
            #    print res[i],i
            results.append([float(res[2]),float(res[23]),res[1]])

    diff = []
    z = []
    z_spec = []
    zbs = {'0,0.2':[],'0.2,0.4':[],'0.4,0.6':[],'0.6,0.8':[]}
    for line in results:
        diff_val = (line[0] - line[1])/(1 + line[1])
        diff.append(diff_val)
        z.append(line[0])
        z_spec.append(line[1])
        for zb in zbs.keys():
            import re
            min,max = re.split('\,',zb)
            if float(min) <= float(line[1]) < float(max):
                zbs[zb].append(diff_val)


    for zb in zbs.keys():
        import scipy
        print ' zb=',zb , ' scipy.median(scipy.array(zbs[zb]))=',scipy.median(scipy.array(zbs[zb]))
        ys = []
        for y in zbs[zb]:
            if abs(y) < 0.1:
                ys.append(y)
        print ' scipy.mean(scipy.array(ys))=',scipy.mean(scipy.array(ys))



    list = diff[:]
    import pylab
    varps = []
    a, b, varp = pylab.hist(diff,bins=arange(-0.2,0.2,0.016))
    #print a,b,varp
    varps.append(varp[0])

    diff_cut = []
    for d in range(len(diff)):

        if abs(d) < 0.25:
            diff_cut.append(diff[d])

    list = scipy.array(diff_cut)
    mu = list.mean()
    median = scipy.median(diff_cut)
    sigma = list.std()

    print 'mu', mu
    print 'sigma', sigma

    sigma = 0.06

    print ' len(z)=',len(z) , ' len(diff)=',len(diff)

    reject = []
    for line in results:
        diff_val = (line[0] - line[1] - median)/(1 + line[1])
        if abs(diff_val)>3*sigma: reject.append(line[2])

    print reject

    from scipy import stats
    fit_a, fit_b, fit_varp = pylab.hist(diff_cut,bins=arange(-0.2,0.2,0.016))
    pdf = scipy.stats.norm.pdf(fit_b, mu, sigma)
    print 'pdf', pdf

    height = scipy.array(a).max()

    print pdf
    pylab.plot(fit_b,len(diff_cut)*pdf/pdf.sum(),'r')

    pylab.xlabel("(PhotZ - SpecZ)/(1 + SpecZ)")
    pylab.ylabel("Number of Galaxies")
    pylab.show()
    pylab.savefig(name + 'RedshiftErrors.ps')
    pylab.clf()


    import scipy, numpy
    from scipy import optimize

    A = numpy.hstack((scipy.array(z)[:,numpy.newaxis],numpy.ones(len(z))[:,numpy.newaxis]))
    #print A
    #print scipy.shape(A)
    #print scipy.shape(scipy.array(diff))
    #(m,b), resids, rank, s = scipy.linalg.basic.lstsq(A,scipy.array(diff))
    #pylab.plot(z,m*z+b,label='best-fit')
    pylab.scatter(z_spec,z)
    pylab.plot(scipy.array([0,1]),scipy.array([0,1]),color='red')
    pylab.xlim(0,1)
    pylab.ylim(0,1)
    #pylab.ylabel("(PhotZ - SpecZ)/(1 + SpecZ)")
    pylab.xlabel("PhotZ")
    pylab.show()
    pylab.savefig(name + 'RedshiftScatter.ps')
    pylab.clf()

    return reject

def get_cluster_z(file):

    import ldac, numpy

    f = ldac.openObjectFile(file)

    arr = numpy.zeros(151)
    for iz in f['Z']:
        #print iz
        n=int(iz*100.)
        if n>150:
            n=150
        if n < 0:
            n=0
        #print "filling ",n
        arr[n]= arr[n]+1

    max = 0
    maxind=0
    for i in range(151):
        #print max , maxind,arr[i]
        if arr[i]>max:
            max=arr[i]
            maxind=i
    Z = float(maxind)/100.
    print Z

    return Z

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
    hdulist[1].header['EXTNAME']='STDTAB'
    import os
    os.system('rm ' + outputfile)
    print outputfile
    hdulist.writeto(outputfile)

def parse(file,filters,constantFilter, columns,cluster):
    import re
    #filters = re.split('\,',filters[:-1])

    filter_off = {}
    filter_off_wild = {}

    if True:
        print file
        f = open(file).readlines()
        import string
        for line in f:
            if string.find(line,'SHIFTS') != -1:
                shifts = line
                res = re.split('\s+',shifts.replace(',',''))[2:-1]
                shifts_v = res

                break

    print res

    for i in range(len(filters)):
        filter_off[filters[i]] = res[i]
        filter_off_wild[filters[i].replace('-1-','%').replace('-2-','%').replace('-3-','%')] = res[i]

    res_fix = []
    ''' now apply same offsets to chips from the same filter '''
    for i in range(len(filters)):
        zo = float(res[i])
        if zo == 0:
            zo = filter_off_wild[filters[i].replace('-1-','%').replace('-2-','%').replace('-3-','%')]
            print zo
        res_fix.append(str(zo))
    print res_fix



    print filter_off

    import photometry_db
    photometry_db.initConnection()
    ''' save to database '''
    for filt in filters:
        ''' now loop over apertures '''
        print cluster, filt, float(filter_off[filter])
        slrZP = photometry_db.registerLePhareZP(cluster, filt, constantFilter, float(filter_off[filter]))

    #print shifts, res
    print columns
    raw = open(columns,'r').readlines()
    i = -1
    filen = columns.replace('.replace','')
    out = open(filen,'w')
    for line in raw:
        if string.find(line,'AB')!=-1:
            i += 1
            if i < len(res):
                ''' sign on shifts is opposite !!! '''
                #line = line.replace('REPLACE',str(-1.*float(res[i])))

                line = line.replace('REPLACE',str(0))

        line = line.replace('\n','')
        if len(line) > 0:
            out.write(line + '\n')
    out.close()

    return res_fix

    #shifts_v = res = ['0.66','0','0','-0.095','0.228','0.23','0','0','0.36','-0.15','0.002','0.244373']

def apply_shifts(file, filters, columns ):

    shifts_v = res = ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'][0:len(filters)]

    import string
    #print shifts, res
    print columns
    raw = open(columns,'r').readlines()
    i = -1
    filen = columns.replace('.replace','')
    out = open(filen,'w')
    for line in raw:
        if string.find(line,'AB')!=-1:
            i += 1
            if i < len(res):
                line = line.replace('REPLACE',res[i])

        line = line.replace('\n','')

        if len(line) > 0:
            out.write(line + '\n')
    out.close()

    return shifts_v

def parseeazy(catalog,n):
    from utilities import run
    import os
    f = open(catalog,'r').readlines()
    sntmp = open('sntmp','w')
    keys = []
    for line in f:
        if line[0:2] == '# ':
            import re
            res2 = re.split('\s+',line[:-1])
            print res2
            for k in res2[1:]:
                keys.append('EAZY_' + k)
            break
        if line[0] != '#':
            break
    print keys

    tempconf = '/tmp/' + os.environ['USER'] + 'photoz.conf'
    conflist = open(tempconf,'w')
    for key in keys:
        if key == 'EAZY_id' :
            conflist.write('COL_NAME = SeqNr\nCOL_TTYPE = LONG\nCOL_HTYPE = INT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n')
        else:
            conflist.write('COL_NAME = ' + key + '\nCOL_TTYPE = DOUBLE\nCOL_HTYPE = FLOAT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n')
    conflist.close()


    import os
    tempcat = '/tmp/' + os.environ['USER'] + 'zs.cat'
    run('asctoldac -i ' + catalog + ' -o ' + catalog + '.temp.tab' + ' -c ' + tempconf + ' -t STDTAB',[tempcat] )

    command = 'ldacaddkey -i ' + catalog + '.temp.tab -o ' + catalog + '.tab -t STDTAB -k EAZY_NUMBER ' + str(n) + ' FLOAT "" '
    print command
    os.system(command)

    print catalog + '.tab'

def parsebpz(catalog,n):
    '''this adds BPZ_NUMBER on the end, but it's always =0 currently (see /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpzAPER1CWWSB_capak.list1_0.bpz.tab.txt)'''
    import os,re
    from utilities import run
    f = open(catalog,'r').readlines()
    sntmp = open(os.environ['USER'] + 'sntmp','w')
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
    run('asctoldac -i ' + catalog + ' -o ' + catalog + '.temp.tab' + ' -c ' + tempconf + ' -t STDTAB',[tempcat] )

    command = 'ldacaddkey -i ' + catalog + '.temp.tab -o ' + catalog + '.tab -t STDTAB -k BPZ_NUMBER ' + str(n) + ' FLOAT "" '
    print ' command=',command
    os.system(command)

    print catalog + '.tab'
    print 'here'

def get_filters(cat,tab='STDTAB',SPECTRA=None):
    import string
    dict = {}
    p = pyfits.open(cat)
    #print p[tab].columns
    for column in p[tab].columns:

        import re
        res = re.split('-',column.name)
        #if len(res) > 1 and (string.find(column.name,'SUBARU') != -1 or string.find(column.name,'MEGA')!=-1 or string.find(column.name,'WIR')!=-1) and string.find(column.name,'1-u') == -1 and string.find(column.name,'SUBARU-9') == -1:
        ''' 1423 u-band image is bad '''
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

            #if string.find(cat,'HDFN') != -1 and (string.find(column.name,'W-S-Z+') != -1):
            #    use = False


            if string.find(cat,'A383') != -1 and (string.find(column.name,'u') != -1): # or string.find(column.name,'W-J-V') != -1):
                use = False


            #string.find(column.name,'SUBARU-9') != -1 or
            ''' remove WHT data, and u-band data '''
            if string.find(column.name,'WH') != -1 or string.find(column.name,'u') != -1 or string.find(column.name,'-U') != -1: # or string.find(column.name,'B') != -1: # or (string.find(column.name,'B') != -1 and string.find(column.name,'9') != -1): # is False:
                use = False

            #if string.find(column.name,'W-S-I+') != -1: # or string.find(column.name,'B') != -1: # or (string.find(column.name,'B') != -1 and string.find(column.name,'9') != -1): # is False:
            #    use = False


            if False: #string.find(cat,'HDFN') != -1 and (string.find(column.name,'W-J-B') != -1 and string.find(column.name,'9') != -1):
                use = False

            #if string.find(cat,'HDFN') != -1 and string.find(column.name,'W-S-Z') != -1:
            #    use = False


            ''' throw out early data '''
            #if string.find(column.name,'SUBARU') != -1 and (string.find(column.name,'9') != -1 or string.find(column.name,'8')!=-1):
            #    use = False

	# and string.find(column.name,'1-u') == -1: # and string.find(column.name,'W-J-B') == -1  : #or string.find(column.name,'MEGA')!=-1 or string.find(column.name,'WIR')!=-1): #  and string.find(column.name,'1-u') == -1: # and string.find(column.name,'SUBARU-9') == -1: # and string.find(column.name,'10_1') == -1: #
        # and string.find(column.name,'1-u') == -1


        if use:
            try:
                dummy = int(res[-1])
            except:
                filt = reduce(lambda x,y: x+'-'+y,res[1:])
                dict[filt] = 'yes'

                if False: #string.find(filt,'WHT') != -1:
                    print column.name, res, filt
                #print res, filter, column

    filters = dict.keys()
    print filters
    return filters

def figure_out_slr_chip(filters,catalog,tab='STDTAB',magtype='APER1'):


    #magtype='APER1'

    print magtype, 'magtype'
    import string
    print catalog
    table = pyfits.open(catalog)[tab].data

    stdfilts = {}

    good_star_nums = {}

    for filt in filters:

        a = table.field('MAG_' + magtype + '-' + filt)
        b = a[a!=-99]
        print filt, len(a), len(b)

        import utilities
        stdfilt = utilities.parseFilter(filt)[-1]

        ''' USE LATE 10_1 or 10_2 data if possible '''
        if string.find(filt,'-2-') == -1 and (string.find(filt,'10_2') != -1 or string.find(filt,'10_1') != -1):
            stat = 9999999999
        else:
            stat = len(b)


        if not stdfilt in stdfilts:
            stdfilts[stdfilt] = [[stat, filt]]
        else:
            stdfilts[stdfilt] += [[stat, filt]]

        good_star_nums[filt] = len(b)

    print stdfilts

    moststarfilts = {}
    for key in stdfilts:
        usefilt =  sorted(stdfilts[key],reverse=True)[0][1]
        moststarfilts[key] = usefilt

    print moststarfilts

    return moststarfilts, good_star_nums

def do_bpz(CLUSTER,DETECT_FILTER,AP_TYPE,filters,inputcat_alter_ascii,inputcat_alter_ldac, calib_type,spec,SPECTRA,picks=None,magtype='ISO',randsample=False,short=False,randpercent=0.03,magflux='FLUX',ID='SeqNr',only_type=False,inputcolumns=False):
    import os
    SUBARUDIR=os.environ['SUBARUDIR']
    iaper = '1'
    dict = { 'SUBARUDIR':SUBARUDIR,
        'PHOTOMETRYDIR': 'PHOTOMETRY_' + DETECT_FILTER + AP_TYPE,
        'AP_TYPE': AP_TYPE,
        'CLUSTER':CLUSTER,
        'BPZPATH':os.environ['BPZPATH'],
        'iaper':iaper,
        'calib_type':calib_type,
        'magtype':magtype,
        }

    if len(filters) > 4: dict['INTERP'] = '8'
    else: dict['INTERP'] = '0'

    dict['SPECTRA'] = SPECTRA #'CWWSB_capak.list' # use Peter Capak's SEDs #dict['SPECTRA'] = 'CWWSB4.list' #dict['SPECTRA'] = 'CFHTLS_MOD.list'

    ## adam-note: I removed the loop over type that was here
    dict['type'] = 'bpz'

    from glob import glob
    for z in filters:
        f = '' + z + '.res'
        #print ' os.environ["BPZPATH"]+"/FILTER/"+f=',os.environ["BPZPATH"]+"/FILTER/"+f
        print ' glob(os.environ["BPZPATH"]+"/FILTER/"+f)=',glob(os.environ["BPZPATH"]+"/FILTER/"+f)
        if len(glob(os.environ['BPZPATH'] + '/FILTER/' + f)) == 0:
            print 'couldnt find filter!!!'
	    raise Exception("no file of the name: os.environ['BPZPATH']+'/FILTER/'+f="+os.environ['BPZPATH'] + '/FILTER/' + f+" found!")

    ''' assume no zeropoint shifts '''

    #dict.update({'SHIFTS':reduce(lambda x,y:x+','+y,shifts)})
    if short or randsample:
        nsplit = 1
    elif not picks:
        nsplit = 4
    else: nsplit = 1
    print ' nsplit=',nsplit , ' randsample=',randsample , ' picks=',picks #currently: nsplit= 4  randsample= False  picks= None

    #adam-del#tmpdir = '/tmp/' + os.environ['USER'] + '/'
    #adam-del#ooo=os.system('mkdir -p ' + tmpdir)
    #adam-del#if ooo!=0: raise Exception("os.system failed!!!")
    #adam-del#os.chdir(tmpdir)

    print ' dict=',dict

    children = [] ; catalogs = [] ; probs = [] ; fluxes = []

    dict['columns'] = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/spec.%(magtype)s.%(AP_TYPE)s.%(SPECTRA)s.cat.columns' % dict
    if inputcolumns:
	    command_cp_columns=' '.join(["cp",inputcolumns,dict['columns']])
	    print "command_cp_columns=",command_cp_columns
	    ooo=os.system(command_cp_columns)
	    if ooo!=0: raise Exception("os.system failed!!!")
    for n in range(nsplit):
        child = False
        dict.update({'n':n})
        catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all_%(type)s%(magtype)s%(SPECTRA)s%(iaper)s_%(n)s.bpz' % dict
        prob = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all_%(type)s%(magtype)s%(SPECTRA)s%(iaper)s_%(n)s.probs' % dict
        flux = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all_%(type)s%(magtype)s%(SPECTRA)s%(iaper)s_%(n)s.flux_comparison ' % dict

        if nsplit == 1:
            children.append(child)
            catalogs.append(catalog+'.tab')
            probs.append(prob)
            fluxes.append(flux)

        dict['catalog'] = catalog
        dict['prob'] = prob

        #adam-comment# command_cp_cat= cp /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.bpz_input.txt /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/all.APER1CWWSB_capak.list.cat.bpz1.tab
        #adam-comment# Hit error on: counter=  obs_file= /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpzAPER1CWWSB_capak.list1_0.cat  flux_cols= (1, 3, 5, 7, 9)
        cat_in_command= '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all_bpz%(magtype)s%(SPECTRA)s%(iaper)s_%(n)s.cat' % dict
	command_cp_cat=' '.join(["cp",inputcat_alter_ascii,cat_in_command])
        print "command_cp_cat=",command_cp_cat
        ooo=os.system(command_cp_cat)
        if ooo!=0: raise Exception("os.system failed!!!")

        if magflux == 'FLUX': dict['magvar'] = 'no'
        else: dict['magvar'] = 'yes'

        if dict['type'] == 'bpz':

            #-NEW_AB yes \
            #''' FIX PRIOR AND INTERPOLATION!!! '''
            #adam#print 'python %(BPZPATH)s/bpz.py %(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all_bpz%(magtype)s%(SPECTRA)s%(iaper)s_%(n)s.cat \n -COLUMNS %(columns)s \n -MAG %(magvar)s \n -SPECTRA %(SPECTRA)s \n -PRIOR hdfn_SB \n -CHECK yes \n -PLOTS yes  \n -VERBOSE no \n -ZMAX 4.0 \n -PLOTS yes \n -INTERP %(INTERP)s \n -PROBS_LITE %(prob)s \n -OUTPUT %(catalog)s' % dict

	    #adam-SHNT# now how to handle specz input (should have input `spec=True` if I fixed adam_do_photometry.py right)
	    #if pars.d['ONLY_TYPE']=='yes': #Use only the redshift information, no priors
	    # probably have to run it with pars.d['ONLY_TYPE']=='yes' and 'no' to see impact
	    # does this just make it have an extra plot or does it actually change the p(z) results? (does BPZ learn from zspecs?)
	    # either way, for plotting purposes, I'll have to fix some stuff in bpz.py
	    # what about where I don't have a Z_S, what do I put there in the catalog? (I think Z_S=99 should work fine)

            command = 'python %(BPZPATH)s/bpz.py %(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all_bpz%(magtype)s%(SPECTRA)s%(iaper)s_%(n)s.cat \
            -COLUMNS %(columns)s \
            -MAG %(magvar)s \
            -SPECTRA %(SPECTRA)s \
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
		    ns_dmp.update(locals()) #adam-tmp#
		    raise Exception("os.system failed!!!")
            #adam-old# parsebpz(catalog,str(n))
	    print "adam-look: running parsebpz(catalog=",catalog,"str(n)=",str(n),")"
	    parsebpz(catalog,str(n))
	    #adam-comment# parsebpz takes catalog and makes catalog+".tab", which is exactly like catalog, but with BPZ_NUMBER=n column
	    #adam-comment# the list `catalogs` has catalog+".tab" in it, so this is needed!

    if randsample:
        base = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(iaper)s.%(SPECTRA)s.rand' % dict
        output_catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(iaper)s.rand.%(SPECTRA)s.%(calib_type)s.tab' % dict
    elif picks is None: #this is what runs
        base = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(iaper)s.%(SPECTRA)s.all' % dict
        output_catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(iaper)s.photoz.%(SPECTRA)s.%(calib_type)s.tab' % dict
    else:
        base = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(iaper)s.%(SPECTRA)s.picks' % dict
        output_catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(iaper)s.picks.%(SPECTRA)s.%(calib_type)s.tab' % dict


    ''' join the tables '''
    temp = base + '.bpz.temp.tab'
    command = 'ldacpaste -i ' + reduce(lambda x,y: x + ' ' + y, catalogs) + ' -o ' + temp + ' -t STDTAB'
    print ' command=',command
    print ' catalogs=',catalogs , ' base=',base
    ooo=os.system(command)
    if ooo!=0: raise Exception("os.system failed!!!")


    output = base + '.bpz.tab'
    join_cats([temp,(inputcat_alter_ldac,"OBJECTS")],output)
    #adam-comment# now output = base + '.bpz.tab' has combination of all cats in "STDTAB" table and inputcat in "OBJECTS" table

    #adam-old# if nsplit>1:
    #adam-old#     print temp, dict['incat_'+dict['type']]
    #adam-old#     join_cats([temp,dict['incat_' + dict['type']]],output)
    #adam-old# else:
    #adam-old#     command_cp="cp %s %s" % (temp,output)


    print ' output=',output
    #priorcat = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(iaper)s.photoz.%(SPECTRA)s.%(calib_type)s.tab' % dict
    #join_cats([base+'.bpz.tab',dict['incat_prior']],output_catalog)

    ''' join the catalogs '''
    command = 'cat ' + reduce(lambda x,y: x + ' ' + y, [z.replace('.tab','') for z in catalogs]) + ' > ' + base + '.bpz'
    print ' command=',command
    ooo=os.system(command)
    if ooo!=0: raise Exception("os.system failed!!!")

    command = 'cat ' + reduce(lambda x,y: x + ' ' + y, probs) + ' > ' + base + '.probs'
    print ' command=',command
    ooo=os.system(command)
    if ooo!=0: raise Exception("os.system failed!!!")

    command = 'cat ' + reduce(lambda x,y: x + ' ' + y, fluxes) + ' > ' + base + '.flux_comparison'
    print ' command=',command
    ooo=os.system(command)
    if ooo!=0: raise Exception("os.system failed!!!")

    #adam-old# convert_to_mags(base,dict['incat_' + dict['type']],base+'.EVERY.cat')
    convert_to_mags(base,inputcat_alter_ldac,base+'.EVERY.cat')
    #adam-expanded# convert_to_mags("/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.APER1.1.CWWSB_capak.list.all" , "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.alter.cat" , "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.APER1.1.CWWSB_capak.list.all.EVERY.cat")

    #adam-Warning# Other codes might use different final cats/output besides *EVERY.cat
    #for example they might look for:
    #	output_catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(iaper)s.photoz.%(SPECTRA)s.%(calib_type)s.tab' % dict
    #cutout_bpz.make_thecorrections actually uses these:
    #	outputcat = '%(path)s/PHOTOMETRY_%(DETECT_FILTER)s%(AP_TYPE)s/%(cluster)s.%(magtype)s.1.%(SPECTRA)s.%(type)s.bpz.tab' % params 
    #	catalog = '%(path)s/PHOTOMETRY_%(DETECT_FILTER)s%(AP_TYPE)s/%(cluster)s.slr.cat' %params           
    #	starcatalog = '%(path)s/PHOTOMETRY_%(DETECT_FILTER)s%(AP_TYPE)s/%(cluster)s.stars.calibrated.cat' %params           

    #global ns_dmp
    #ns_dmp.update(locals()) #adam-tmp#


if __name__ == '__main__':
    import sys, os
    maindir = sys.argv[1]
    CLUSTER = sys.argv[2]
    PHOTOMETRYDIR = sys.argv[3]
    LEPHARE_CONFIGFILE = sys.argv[4]
    naper = sys.argv[5]
    makelibs = sys.argv[6]
    do_bpz(maindir, CLUSTER, PHOTOMETRYDIR, LEPHARE_CONFIGFILE, naper, makelibs)
