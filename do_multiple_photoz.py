#!/usr/bin/env python



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
    print command

    import commands

    for i in range(1):
        import os
        os.system('cat ' + dictionary['columns'])
        print 'running'                                                     
        f = commands.getoutput(command).split('\n')
        
                                                                                      
        print f 
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
                                                                                      
                                                                                      
        print offsets
                                                                                      
        print dictionary['columns']
        parse_column_file(dictionary['columns'],offsets=offsets)


    #raw_input('finished fit_zps')
        



    





























def convert_to_mags(run_name,mag_cat,outputfile):

    import astropy.io.fits as pyfits

    mag = pyfits.open(mag_cat)[1]

    cat = run_name + '.bpz'

    from useful import *
    from coeio import loaddata, loadfile, params_cl, str2num, loaddict, findmatch1, pause  #, prange, plotconfig

    bpzstr = loadfile(cat)
    bpzparams = {}
    i = 0
    import string                
    while bpzstr[i][:2] == '##':
        line = bpzstr[i][2:]
        if '=' in line:
            [key, value] = string.split(line, '=')
            bpzparams[key] = value
        i = i + 1

    print bpzparams['FLUX_COMPARISON']

    columns = bpzparams.get('COLUMNS', run_name+'.columns')
    flux_comparison = run_name + '.flux_comparison' #bpzparams.get('FLUX_COMPARISON', run_name+'.flux_comparison')

    zs=get_2Darray(cat) #Read the whole file

    print zs


    all=get_2Darray(flux_comparison) #Read the whole file
    ncols=len(all[0,:])
    nf=(ncols-5)/3
    filters=get_str(columns,0,nf)

    print filters


    import numpy
    #t = numpy.loadtxt(inputcat)

    #all=get_2Darray(inputcat) #Read the whole file                        
    print len(all[:,0])
    ncols=len(all[0,:])
    print len(all[0,:]        )
    nf=(ncols-5)/3
    
    ''' need to get the number of filters '''                                          
    
    ''' need to retrieve the flux predicted, flux observed, and flux_error '''    
    import scipy
    ID=scipy.array(all[:,0])  # FLUX (from spectrum for that TYPE)
    ft=scipy.array(all[:,5:5+nf])  # FLUX (from spectrum for that TYPE)
    fo=scipy.array(all[:,5+nf:5+2*nf])  # FLUX (OBSERVED)
    efo=scipy.array(all[:,5+2*nf:5+3*nf])  # FLUX_ERROR (OBSERVED)
                                                                               
    all_num = len(ft) 
    print all_num
    import math as m
    
    print -2.5*scipy.log10(ft)

    import astropy.io.fits as pyfits, numpy
    tables = {}
    i = 0
    cols = []


    ''' if column not already there, then add it '''        
    cols.append(pyfits.Column(name='SeqNr', format = 'J', array = ID))
    cols.append(pyfits.Column(name='NFILT', format = 'J', array = mag.data.field('NFILT')))
    for i in range(len(filters)):
        print filters[i], i, ft[:,i]
        added = False
        for column in mag.columns:
            if 'MAG_APER-' + filters[i] == column.name:
                measured = mag.data.field('MAG_APER-'+filters[i])
                if len(measured[measured!=-99]) > 0:
                    ''' subsitute where there are -99 values '''
                    measured[measured==-99] =  -2.5*scipy.log10(ft[:,i])
                    cols.append(pyfits.Column(name='HYBRID_MAG_APER-' + filters[i], format = '1E', array = measured))
                    added = True
                    print 'measured', filters[i]                        
                    break

        if not added:
            cols.append(pyfits.Column(name='HYBRID_MAG_APER-'+filters[i], format = '1E', array = -2.5*scipy.log10(ft[:,i])))
        #cols.append(pyfits.Column(name='MAGERR_APER-'+filters[i], format = '1E', array = 99.*numpy.ones(2)))

    import scipy
    for column in mag.columns:

        if string.find(column.name,'MAG') == -1:
            a = -2.5*scipy.log10(mag.data.field(column.name))
            a[mag.data.field(column.name) == 0] = -99 
            cols.append(pyfits.Column(name='DATA_' + column.name.replace('FLUX','MAG'), format = column.format, array = a))
        else:
            a = mag.data.field(column.name)
            cols.append(pyfits.Column(name='DATA_' + column.name, format = column.format, array = a))

                                                                    
    print cols
    print len(cols)
    hdu = pyfits.PrimaryHDU()
    hduSTDTAB = pyfits.BinTableHDU.from_columns(cols) 
    hdulist = pyfits.HDUList([hdu])
    hdulist.append(hduSTDTAB)
    hdulist[1].header['EXTNAME']='OBJECTS'
    import os
    os.system('rm ' + outputfile)
    print outputfile
    hdulist.writeto(outputfile)


def add_dummy_ifilter(catalog, outputfile): 

    import astropy.io.fits as pyfits, numpy
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






                                                                    
    print cols
    print len(cols)
    hdu = pyfits.PrimaryHDU()
    hduSTDTAB = pyfits.BinTableHDU.from_columns(cols) 
    hdulist = pyfits.HDUList([hdu])
    hdulist.append(hduSTDTAB)
    hdulist[1].header['EXTNAME']='OBJECTS'
    import os
    os.system('rm ' + outputfile)
    print outputfile
    hdulist.writeto(outputfile)




def add_dummy_filters(catalog, outputfile): 

    add_filters =['MEGAPRIME-0-1-g','MEGAPRIME-0-1-r','MEGAPRIME-0-1-i','MEGAPRIME-0-1-z','SUBARU-10_2-1-W-S-G+','SUBARU-10_2-1-W-C-RC','SUBARU-10_2-1-W-C-IC']

    use_filters = ['MEGAPRIME-0-1-u','SUBARU-10_2-1-W-J-B','SUBARU-10_2-1-W-J-V','SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-S-I+','SUBARU-10_2-1-W-S-Z+']

    import astropy.io.fits as pyfits, numpy
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
                                                                    
    print cols
    print len(cols)
    hdu = pyfits.PrimaryHDU()
    hduSTDTAB = pyfits.BinTableHDU.from_columns(cols) 
    hdulist = pyfits.HDUList([hdu])
    hdulist.append(hduSTDTAB)
    hdulist[1].header['EXTNAME']='OBJECTS'
    import os
    os.system('rm ' + outputfile)
    print outputfile
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
        print zb, scipy.median(scipy.array(zbs[zb]))
        ys = []
        for y in zbs[zb]:
            if abs(y) < 0.1:
                ys.append(y)
        print scipy.mean(scipy.array(ys))

    
    
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

    print sigma
    sigma = 0.06

    print len(z), len(diff)
    
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
    import astropy.io.fits as pyfits
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

    print cols
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
    key_start = False
    keys = [] 
    for line in f:
        import string
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
    import os
    from utilities import run
    f = open(catalog,'r').readlines()
    sntmp = open(os.environ['USER'] + 'sntmp','w')
    key_start = False
    keys = [] 
    for line in f:
        import string
        if line[0:2] == '# ':
            import re
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
   
 
    import os
    tempcat = '/tmp/' + os.environ['USER'] + 'zs.cat'
    run('asctoldac -i ' + catalog + ' -o ' + catalog + '.temp.tab' + ' -c ' + tempconf + ' -t STDTAB',[tempcat] )

    command = 'ldacaddkey -i ' + catalog + '.temp.tab -o ' + catalog + '.tab -t STDTAB -k BPZ_NUMBER ' + str(n) + ' FLOAT "" '  
    print command
    os.system(command)

    print catalog + '.tab'
    print 'here'




def parselph(catalog):
    from utilities import run
    f = open(catalog,'r').readlines()
    sntmp = open(os.environ['USER'] + 'sntmp','w')
    key_start = False
    keys = [] 
    for line in f:
        import string
        if key_start:
            import re
            res = re.split(',',line[1:])
            for r in res:
                res2 = re.split('\s+',r)
                if len(res2) > 2:
                    keys.append('LPH_' + res2[1])
        if string.find(line,'Output format') != -1:
            key_start = True
        if string.find(line,'########') != -1 and key_start == True:
            key_start = False 
            break

    tempconf = '/tmp/' + os.environ['USER'] + 'photoz.conf'
    conflist = open(tempconf,'w')
    for key in keys:
        if key == 'ID' :
            conflist.write('COL_NAME = SeqNr\nCOL_TTYPE = LONG\nCOL_HTYPE = INT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n')
        else:
            conflist.write('COL_NAME = ' + key + '\nCOL_TTYPE = DOUBLE\nCOL_HTYPE = FLOAT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n')
    conflist.close()
    
    import os
    tempcat = '/tmp/' + os.environ['USER'] + 'zs.cat'
    run('asctoldac -i ' + catalog + ' -o ' + catalog + '.tab' + ' -c ' + tempconf + ' -t STDTAB',[tempcat] )

    print catalog + '.tab'
    
    #input = reduce(lambda x,y: x + ' ' + y, keys)
    #run('ldacjoinkey -t OBJECTS -i /tmp/' + cluster + 'output.cat -p ' + tempcat + ' -o /tmp/' + cluster + 'final.cat -t STDTAB  -k ' + input)

def get_filters(cat,tab='STDTAB',SPECTRA=None):
    import astropy.io.fits as pyfits, string
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
    import astropy.io.fits as pyfits, string
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
    

    
        





























def do_it(CLUSTER,DETECT_FILTER,AP_TYPE,filters,inputcat, calib_type,spec,use_spec,SPECTRA,picks=None,magtype='ISO',randsample=False,short=False,randpercent=0.03,magflux='FLUX',ID='SeqNr',only_type=False):

    go = True
    
    
    LEPHAREDIR='/nfs/slac/g/ki/ki04/pkelly/lephare_dev/'
    LEPHAREWORK='/nfs/slac/g/ki/ki04/pkelly/lepharework/'
    SUBARUDIR='/nfs/slac/g/ki/ki05/anja/SUBARU'
    
    iaper = '1'
    
    import os
    
    dict = {'LEPHAREDIR':LEPHAREDIR,
        'SUBARUDIR':SUBARUDIR,
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

    final_cats = []   




    dict['SPECTRA'] = SPECTRA #'CWWSB_capak.list' # use Peter Capak's SEDs

    #dict['SPECTRA'] = 'CWWSB4.list'

    #dict['SPECTRA'] = 'CFHTLS_MOD.list'

    for type in ['bpz']: 
        dict['type'] = type                                                                                                                                                                            
        dict['incat_lph'] = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all.%(magtype)s%(SPECTRA)s.cat.lph%(iaper)s.tab' % dict 
        dict['incat_bpz'] = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all.%(magtype)s%(SPECTRA)s.cat.bpz%(iaper)s.tab' % dict 
        #print dict['incat_bpz']
        #print ID
        dict['incat_eazy'] = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all.%(magtype)s%(SPECTRA)s.cat.eazy%(iaper)s' % dict 
        dict['header_eazy'] = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all.%(magtype)s%(SPECTRA)s.cat.eazyheader' % dict 
        dict['incat_prior'] = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all.%(magtype)s%(SPECTRA)s.cat.prior%(iaper)s.tab' % dict 

        #filters = get_filters(dict['incat_' + dict['type']])
        
        ''' make configuration file '''
        dummy_config = '%(LEPHAREDIR)s/config/dummy_config.para' % dict
        t = open(dummy_config).read()
        config = '%(LEPHAREDIR)s/config/%(CLUSTER)sconfig.para' % dict
        dict.update({'config':config})

        import string
        fstring = ''
        quadadd = ''

        i = 1            
        goodl = []
        for z in filters:
            #if string.find(z,'MEGA')!=-1:
            #    f = 'cfht/megacam/' + z + '.pb' 
            #elif string.find(z,'SUBARU')!=-1:
            print z
            if True: #(string.find(z,'10_2-1') != -1 or string.find(z,'10_1-1') != -1) and string.find(z,'SUBARU')!=-1:
                goodl.append(i)                
            i += 1

            print goodl

            if True:
                f = '' + z + '.res' 

            from glob import glob
            print glob(os.environ['BPZPATH'] + '/FILTER/' + f)

            print os.environ['BPZPATH'] + '/FILTER/' + f
            if len(glob(os.environ['BPZPATH'] + '/FILTER/' + f)) > 0: 
                fstring += f + ','
                quadadd += '0.00,'
            else:
                print 'couldnt find filter!!!'
                raise Exception


        if len(goodl) > 1:
            ref = str(goodl[0]) + ',' + str(goodl[1]) + ',' + str(goodl[0])
        else: ref = '1,3,1'
        dict['ref'] = ref

        import re
        constantFilter = reduce(lambda x,y: str(x) + ',' + str(y), [filters[i] for i in [int(z) for z in re.split('\,',ref)]])

        print constantFilter

        dict['mag_ref'] = str(goodl[0])

        fstring = fstring[:-1]
        quadadd = quadadd[:-1]
        print fstring

        dict['quadadd'] = str(quadadd)
        print quadadd
        dict['fstring'] = fstring

        if False:
            c = open(config,'w')                                                             
            c.write('FILTER_LIST ' + fstring + '\n' + t.replace('cluster',dict['CLUSTER']))
            #c.write('FILTER_LIST ' + fstring + '\n' + t.replace('cluster',dict['CLUSTER']))
            c.close()


        print config
        if False: # go:            
            os.system(os.environ['LEPHAREDIR'] + '/source/filter -c ' + config)        

            os.system(os.environ['LEPHAREDIR'] + '/source/sedtolib -t G -c ' + config)

            os.system(os.environ['LEPHAREDIR'] + '/source/sedtolib -t S -c ' + config)
            os.system(os.environ['LEPHAREDIR'] + '/source/mag_star -c ' + config)
            os.system(os.environ['LEPHAREDIR'] + '/source/mag_gal -t G -c ' + config)
            go = False




        ''' retrieve zeropoint shifts '''
        columns = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/spec.cat.columns.replace' % dict
        file = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(iaper)s.spec.zs' % dict


        print spec
        if spec: 
            ''' filter out cluster galaxies '''                                                        
            spec_cat = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)sspec.cat' % dict
            Z = get_cluster_z(spec_cat)
            print Z
                                                                                                      
            training_cat = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/spec.cat.lph%(iaper)s' % dict

            #new_training_cat = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/spec.cat.training' % dict
            #ntc = open(new_training_cat,'w')
            #print training_cat
            #for l in open(training_cat).readlines():
            #    import re
            #    res = re.split('\s+',l)
            #    print float(res[-3])
            #    if not (Z - 0.015 < float(res[-3]) < Z + 0.015):
            #        ntc.write(l)
            #ntc.close()

            #os.system('cp ' + training_cat + ' ' + new_training_cat )

            ''' make zphot.param file '''

            if False:

                eazydir = '/nfs/slac/g/ki/ki04/pkelly/eazy-1.00/'                                              
                                                                                                               
                dummy = open(eazydir + 'zphot.dummy','r').read()
                                                                                                               
                training_cat = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/specsave.cat.eazy%(iaper)s' % dict
                ecat = open(training_cat,'r').read() 
                eheader = open(dict['header_eazy'],'r').read() 
                print training_cat, eheader
                scat = open('/tmp/pat','w')
                scat.write(eheader + ecat)
                scat.close()
                                                                                                               
                filter_res = 'test.RES' % dict
                dummy = "".join([dummy,'FILTERS_RES    ' + filter_res + '\n'])
                dummy = "".join([dummy,'CATALOG_FILE   /tmp/pat \n'])
                dummy = "".join([dummy,'PRIOR_FILTER   ' + str(1) + '\n'])
                                                                                                               
                zphot = open('zphot.param','w')
                zphot.write(dummy)
                zphot.close()

                command = eazydir + 'src/eazy'       
                print command
                os.system(command)
                parseeazy('./OUTPUT/photz.zout','0')
            
            ''' first retrieve LEPHARE zeropoint corrections '''
            command = '%(LEPHAREDIR)s/source/zphota -c %(config)s  \
                -CAT_TYPE     LONG \
                -ADAPT_BAND %(ref)s \
                -MAG_REF %(mag_ref)s \
                -MABS_REF %(mag_ref)s \
                -ADAPT_LIM 18,22 \
                -ZMAX_GAL 1 \
                -SPEC_OUT YES \
                -CAT_IN %(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/spec.cat.training\
                -CAT_OUT  %(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(iaper)s.spec.zs \
                -FILTER_LIST %(fstring)s\
                -ERR_SCALE %(quadadd)s' % dict 
            print command 
                                                                                                      
            #os.system(command)

            
            print command

            outputcat = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(iaper)s.spec.zs' % dict

            print outputcat

            #parselph(outputcat)    
            print outputcat
            #rejects = mkplot(outputcat,'0') 


            #print rejects



            for i in []: #'1']: #: #'2']: #,'3','4']:

                new_training_cat = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/spec.cat.training' % dict  
                reject_training_cat = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/spec.cat.reject' % dict
                ntc = open(reject_training_cat,'w')
                print training_cat
                for l in open(new_training_cat).readlines():
                    import re
                    res = re.split('\s+',l)
                    bad = False
                    for p in rejects:
                        if int(p) == int(res[0]): bad = True
                    if not bad:
                        ntc.write(l)
                ntc.close()
                                                                                                           
                print reject_training_cat


                command = '%(LEPHAREDIR)s/source/zphota -c %(config)s  \
                    -CAT_TYPE     LONG \
                    -ADAPT_BAND %(ref)s \
                    -MAG_REF %(mag_ref)s \
                    -MABS_REF %(mag_ref)s \
                    -ADAPT_LIM 18,22 \
                    -SPEC_OUT YES \
                    -ZMAX_GAL 1 \
                    -CAT_IN %(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/spec.cat.reject\
                    -CAT_OUT  %(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(iaper)s.spec.zs \
                    -FILTER_LIST %(fstring)s\
                    -ERR_SCALE %(quadadd)s' % dict 
                                                                                                           
                ''' first retrieve LEPHARE zeropoint corrections '''
                print command 
                                                                                                          
                os.system(command)

                
                                                                                                           
                rejects += mkplot(outputcat,str(i)) 




            #print new_training_cat
            #print reject_training_cat


            print file 
            #shifts = parse(file,filters,constantFilter,columns,dict['CLUSTER'])

            catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(SPECTRA)s.%(iaper)s.spec.bpz' % dict 
            print catalog
            dict['catalog'] = catalog 
            dict['n'] = '1' 
            dict['probs'] = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(SPECTRA)s.%(iaper)s.spec.probs ' % dict 
            dict['flux'] = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(SPECTRA)s.%(iaper)s.spec.flux_comparison ' % dict 
            dict['input'] = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/spec.%(magtype)s.%(AP_TYPE)s.%(SPECTRA)s.cat.bpz1' % dict 
            dict['columns'] = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/spec.%(magtype)s.%(AP_TYPE)s.%(SPECTRA)s.cat.columns' % dict 

    
            #dict['SPECTRA'] = SPECTRA 

            #dict['SPECTRA'] = 'CWWSB4.list'

            if True: 
                if magflux == 'FLUX': dict['magvar'] = 'no' 
                else: dict['magvar'] = 'yes'

                command = 'python %(BPZPATH)s/bpz.py %(input)s \
                -COLUMNS %(columns)s \
                -MAG %(magvar)s \
                -SPECTRA %(SPECTRA)s \
                -PRIOR hdfn_SB \
                -CHECK yes \
                -PLOTS yes \
                -ONLY_TYPE NO \
                -ZMAX 4.0 \
                -INTERP %(INTERP)s \
                -PROBS_LITE %(probs)s \
                -OUTPUT %(catalog)s' % dict
                print command
                os.system(command)
                print catalog 
            print catalog 
            parsebpz(catalog,'0')    

            ''' NEED TO MAKE CATALOG IN TABLE FORM!!!! '''

            print 'finished'

        else: 
            #shifts = apply_shifts(file,filters,columns)
            print file
            print columns
            print 'zero shifts'

            #dict.update({'SHIFTS':reduce(lambda x,y:x+','+y,shifts)})                                                                                                                                                    
            if short or randsample: 
                nsplit = 1
            elif not picks: 
                nsplit = 4
            else: nsplit = 1



            print nsplit, randsample, picks

            print dict['incat_' + dict['type']].replace('.tab','') 
            import random
            l = open(dict['incat_' + dict['type']].replace('.tab',''),'r').readlines()
                                                                                                                                                                                                                          
            if True:
                subset = 0 #random.sample(range(len(l)-100),1)[0]
            
            flist = []
            #nsplit = 1
            interval = int(len(l)/nsplit)
            for n in range(nsplit):
                dict.update({'n':n})
                print 'n, writing'
                start = 1 + subset + n*interval
                end = 1 + subset + (n+1)*interval
                if n == range(nsplit)[-1]:
                    end =  len(l) + 2 
                #if n == range(nsplit)[-1]:                 
                #    end = 1 + len(l)                
                
                print start, end

                print randsample

                os.system('rm ' + dict['incat_' + dict['type']] + str(n))
               
                if False: #randsample:
                    command = 'ldacfilter -i ' + dict['incat_' + dict['type']] + " -t STDTAB -c '(" + ID + " > 0);' -o " + dict['incat_' + dict['type']] + str(n)
                elif not picks: 
                    command = 'ldacfilter -i ' + dict['incat_' + dict['type']] + " -t STDTAB -c '((" + ID + " >= " + str(start) + ") AND (" + ID + " < " + str(end) + "));' -o " + dict['incat_' + dict['type']] + str(n)
                else:
                    command = 'ldacfilter -i ' + dict['incat_' + dict['type']] + " -t STDTAB -c '((" + ID + " >= " + str(picks[0]) + ") AND (" + ID + " < " + str(picks[0]+1) + "));' -o " + dict['incat_' + dict['type']] + str(n)


                                                                                                                                                                                                                          
                #command = 'ldacfilter -i ' + dict['incat_' + dict['type']] + " -t STDTAB -c '((SeqNr >= 0) AND (SeqNr < 1000000));' -o " + dict['incat_' + dict['type']] + str(n)
                print command
                os.system(command)

                if not glob(dict['incat_' + dict['type']] + str(n)):
                    raise Exception
                
                catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all_%(type)s%(magtype)s%(SPECTRA)s%(iaper)s_%(n)s.cat' % dict 
                command = 'ldactoasc -b -i ' + dict['incat_' + dict['type']] + str(n) + ' -t STDTAB > ' + catalog 
                print command
                os.system(command)
                                                                                                                                                                                                                          

            dir = '/tmp/' + os.environ['USER'] + '/'
            os.system('mkdir -p ' + dir)
            os.chdir(dir)
            print dict
            print randsample
            
            if True:
                children = []
                catalogs = []
                probs = []
                fluxes = []
                                                                                                                                                                                                                          
                for n in range(nsplit):
                    if nsplit > 1:  
                        child = os.fork()
                    else: child = False 
            
                    dict.update({'n':n})                                                                                                            
                    catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all_%(type)s%(magtype)s%(SPECTRA)s%(iaper)s_%(n)s.bpz' % dict 
                    prob = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all_%(type)s%(magtype)s%(SPECTRA)s%(iaper)s_%(n)s.probs' % dict
                    flux = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all_%(type)s%(magtype)s%(SPECTRA)s%(iaper)s_%(n)s.flux_comparison ' % dict 
                                                                                                                                                    
                                                                                                                                                    
                    if nsplit == 1:
                        children.append(child)
                        catalogs.append(catalog+'.tab')
                        probs.append(prob)
                        fluxes.append(flux)
                     
                    if child:
                        children.append(child)
                        catalogs.append(catalog+'.tab')
                        probs.append(prob)
                        fluxes.append(flux)
                                                                                                                                                                                                                          
                    else:
                        dict['catalog'] = catalog 
                        dict['prob'] = prob 
                        dict['columns'] = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/spec.%(magtype)s.%(AP_TYPE)s.%(SPECTRA)s.cat.columns' % dict 

                        if  False:
                                eazydir = '/nfs/slac/g/ki/ki04/pkelly/eazy-1.00/'                                                   
                                dummy = open(eazydir + 'zphot.dummy','r').read()
                                #training_cat = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/specsave.cat.eazy%(iaper)s' % dict
                                training_cat = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all.%(magtype)s%(SPECTRA)s.cat.eazy1' % dict                    
                                ecat = open(training_cat,'r').read() 
                                eheader = open(dict['header_eazy'],'r').read() 
                                print training_cat, eheader
                                scat = open('/tmp/pat','w')
                                scat.write(eheader + ecat)
                                scat.close()
                                os.system('mkdir -p /tmp/pkelly/OUTPUT/')
                                filter_res = 'test.RES' % dict
                                dummy = "".join([dummy,'FILTERS_RES    ' + filter_res + '\n'])
                                dummy = "".join([dummy,'CATALOG_FILE   /tmp/pat \n'])
                                dummy = "".join([dummy,'PRIOR_FILTER   ' + str(1) + '\n'])
                                zphot = open('zphot.param','w')
                                zphot.write(dummy)
                                zphot.close()
                                command = eazydir + 'src/eazy'       
                                print command
                                os.system(command)
                                os.system('pwd')
                                parseeazy('./OUTPUT/photz.zout','0')

                    
                        if dict['type'] == 'lph':
                            command = '%(LEPHAREDIR)s/source/zphota -c %(config)s  \
                                -CAT_TYPE LONG \
                                -AUTO_ADAPT NO \
                                -Z_STEP 0.02,2.5,0.1 \
                                -ZMAX_GAL 2.5 \
                                -APPLY_SHIFTS %(SHIFTS)s \
                                -CAT_IN %(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all.cat.lph%(iaper)s.%(n)s \
                                -CAT_OUT  %(catalog)s' % dict 
                            print command 
                            os.system(command)
                            parselph(catalog)    
           
                        if magflux == 'FLUX': dict['magvar'] = 'no' 
                        else: dict['magvar'] = 'yes'

                        if dict['type'] == 'bpz':

                            #-NEW_AB yes \
                            #''' FIX PRIOR AND INTERPOLATION!!! '''
                            command = 'python %(BPZPATH)s/bpz.py %(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all_bpz%(magtype)s%(SPECTRA)s%(iaper)s_%(n)s.cat \
                            -COLUMNS %(columns)s \
                            -MAG %(magvar)s \
                            -SPECTRA %(SPECTRA)s \
                            -PRIOR hdfn_SB \
                            -CHECK yes \
                            -PLOTS yes  \
                            -VERBOSE no \
                            -ZMAX 4.0 \
                            -PLOTS yes \
                            -INTERP %(INTERP)s \
                            -PROBS_LITE %(prob)s \
                            -OUTPUT %(catalog)s' % dict


                            if only_type:
                                command= 'python %(BPZPATH)s/bpz.py %(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all_bpz%(magtype)s%(SPECTRA)s%(iaper)s_%(n)s.cat \
                            -COLUMNS %(columns)s \
                            -MAG %(magvar)s \
                            -SPECTRA %(SPECTRA)s \
                            -PRIOR hdfn_SB \
                            -CHECK yes \
                            -PLOTS yes  \
                            -VERBOSE no \
                            -ZMAX 4.0 \
                            -PLOTS yes \
                            -INTERP 8 \
                            -PROBS_LITE %(prob)s \
                            -ONLY_TYPE yes \
                            -OUTPUT %(catalog)s' % dict
                            print command

                #fit_zps(dict)              

                            #raw_input('finished') #print catalog 
                            os.system(command)
                
                            parsebpz(catalog,str(n))    
    
                        import sys
                        if nsplit > 1: sys.exit(0)
                
                if nsplit > 1:
                    for child in children: 
                        os.waitpid(child,0)
                                                                                                                                                                                                                          
                                                                                                                                                                                                                          
                                                                                                                                                                                                                          
            if randsample:
                base = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(iaper)s.%(SPECTRA)s.rand' % dict                                              
                output_catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(iaper)s.rand.%(SPECTRA)s.%(calib_type)s.tab' % dict 
            elif picks is None:  
                base = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(iaper)s.%(SPECTRA)s.all' % dict                                              
                output_catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(iaper)s.photoz.%(SPECTRA)s.%(calib_type)s.tab' % dict 
            else:
                base = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(iaper)s.%(SPECTRA)s.picks' % dict                                              
                output_catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(magtype)s.%(iaper)s.picks.%(SPECTRA)s.%(calib_type)s.tab' % dict 
                                                                                                                                                                                                                          
            #columns = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/spec.cat.columns' % dict
                                                                                                                                                                                                                          
            #os.system('cp ' + columns + ' ' + base + '.columns') 
                                                                                                                                                                                                                          
            ''' join the tables ''' 
            temp = base + '.bpz.temp.tab'
            command = 'ldacpaste -i ' + reduce(lambda x,y: x + ' ' + y, catalogs) + ' -o ' + temp + ' -t STDTAB' 
            print command
            print catalogs, base
            os.system(command)
            final_cats.append(catalog + '.tab')


            output = base + '.bpz.tab'
            print temp, dict['incat_' + dict['type']]
            join_cats([temp,dict['incat_' + dict['type']]],output)
            

            print output
            #priorcat = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(iaper)s.photoz.%(SPECTRA)s.%(calib_type)s.tab' % dict 
            #join_cats([base+'.bpz.tab',dict['incat_prior']],output_catalog)    

            if True:
                ''' join the catalogs '''                                                                                             
                command = 'cat ' + reduce(lambda x,y: x + ' ' + y, [z.replace('.tab','') for z in catalogs]) + ' > ' + base + '.bpz' 
                print command
                os.system(command)
                final_cats.append(catalog)
                
                command = 'cat ' + reduce(lambda x,y: x + ' ' + y, probs) + ' > ' + base + '.probs' 
                print command
                os.system(command)
                final_cats.append(catalog)
                                                                                                                                      
                command = 'cat ' + reduce(lambda x,y: x + ' ' + y, fluxes) + ' > ' + base + '.flux_comparison' 
                print command
                os.system(command)
                final_cats.append(catalog)

            convert_to_mags(base,dict['incat_' + dict['type']],base+'.EVERY.cat')
    print final_cats

    #output_catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(iaper)s.photoz.%(SPECTRA)s.%(calib_type)s.tab' % dict 
    #join_cats(final_cats,output_catalog)    
   
if __name__ == '__main__':           

    import sys, os
    maindir = sys.argv[1]
    CLUSTER = sys.argv[2]
    PHOTOMETRYDIR = sys.argv[3]
    LEPHARE_CONFIGFILE = sys.argv[4]
    naper = sys.argv[5]
    makelibs = sys.argv[6]

    do_it(maindir, CLUSTER, PHOTOMETRYDIR, LEPHARE_CONFIGFILE, naper, makelibs)
