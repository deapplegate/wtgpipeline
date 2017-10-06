#from scamp import entryExit
import utilities

global itr
itr = 0

def load_spectra():
    import pickle
    f = open('picklespectra','r')
    m = pickle.Unpickler(f)
    spectra = m.load()
    
    return spectra



''' get SDSS zeropoint if exists '''
def get_sdss_zp(run,night,snpath):
    import MySQLdb
    db2 = MySQLdb.connect(db='calib')
    c = db2.cursor()

    zps={'JCAT':0}
    OK = True
    for filt in ['u','g','r','i','z']:
        command = "SELECT SDSSZP from CALIB where SN='" + snpath + "' and FILT='" + filt + "' and NAME='reg' and RUN='" + run + "'" 
        print command
        c.execute(command)                                                                                                       
        zp = c.fetchall()[0][0]
        if str(zp) != 'None':
            print zp
            zps[filt] = float(zp)
        else: OK = False

    if OK:
        return zps #['u'], zps['g'], zps['r'], zps['i'], zps['z']
    else:
        return None


def assign_zp(filt,pars,zps):
    if filt in zps:
        out = pars[zps[filt]]
    else: 
    #    raise Exception            
        out = 0
    return out

def get_kit(): 
    import pickle, os
    f = open(os.environ['kpno'] + '/process_kpno/locuskit','r')
    m = pickle.Unpickler(f)
    locus = m.load()
    return locus

#def get_locus(): 
#    import pickle
#    f = open('/Volumes/mosquitocoast/patrick/kpno/process_kpno/kpnolocus','r')
#    m = pickle.Unpickler(f)
#    locus = m.load()
#    return locus


def get_locus(): 
    import pickle
    f = open('synthlocus','r')
    m = pickle.Unpickler(f)
    locus = m.load()
    return locus



def locus():
    import os, re
    f = open('locus.txt','r').readlines()
    id = -1
    rows = {}
    bands = {}
    for i in range(len(f)):
        l = f[i]
        if l[0] != ' ':
            rows[i] = l[:-1]
        else: 
            id += 1 
            bands[rows[id]] = [float(x) for x in re.split('\s+',l[:-1])[1:]]
    print bands.keys() 
    #pylab.scatter(bands['GSDSS_ZSDSS'],bands['RSDSS_ISDSS'])       
    #pylab.show()

    return bands

#@entryExit
#def all(catalog_dir,cluster,magtype='APER1',location=None): 

def all(subarudir,cluster,DETECT_FILTER,aptype,magtype,location=None):

    catalog_dir = subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + aptype + '/'
    catalog_dir_iso = subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + '_iso/'

    import astropy.io.fits as pyfits, os, string, random
    min_err = 0.02

    #catalog_dir = '/'.join(catalog.split('/')[:-1])
    catalog = catalog_dir + '/' + cluster + '.stars.calibrated.cat'
    all_phot_cat = catalog_dir + '/' + cluster + '.unstacked.cat'
    all_phot_cat_iso = catalog_dir_iso + '/' + cluster + '.unstacked.cat'
    slr_out = catalog_dir + '/' + cluster + '.slr.cat'
    slr_out_iso = catalog_dir_iso + '/' + cluster + '.slr.cat'
    offset_list = catalog_dir + '/multislr.offsets.list'

    slr_high = catalog_dir + '/slr.offsets.list'
    from glob import glob
    startingzps = {}
    if glob(slr_high):
        f = open(slr_high,'r').readlines()
        for l in f:
            res = l.split(' ')
            filt = res[1]
            zp = float(res[2])
            startingzps[filt.replace('10_2','').replace('10_1','').replace('10_3','')] = zp
    
    offset_list_file = open(offset_list,'w')
    print catalog_dir, offset_list

    #zps_dict = {'full':{'SUBARU-10_2-1-W-J-B': 0.16128103741856098, 'SUBARU-10_2-1-W-C-RC': 0.0, 'SUBARU-10_2-1-W-S-Z+': 0.011793588122789772, 'MEGAPRIME-10_2-1-u': 0.060291451932493148, 'SUBARU-10_2-1-W-C-IC': 0.0012269407091880637, 'SUBARU-10_2-1-W-J-V': 0.013435398732369786}}


    ''' get catalog filters '''
    import do_multiple_photoz
    filterlist = do_multiple_photoz.get_filters(catalog,'OBJECTS')
    filterlist.sort()        
    import pylab
    print catalog
    table = pyfits.open(catalog)[1].data[:]

    print catalog, 'catalog'

    alpha = [table.field('ALPHA_J2000')[0]]
    delta = [table.field('DELTA_J2000')[0]]

    import utilities
    gallong, gallat = utilities.convert_to_galactic(alpha, delta)
    ebv = utilities.getDust(alpha,delta)
    extinct = {}
    for filt in filterlist:
        extinct[filt] = utilities.getExtinction(filt) * ebv[0]
    print extinct
    print ebv, 'ebv', alpha, delta, gallong, gallat

    #location = os.environ['sne'] + '/photoz/' + cluster + '/SLRplots/'
    if location is None:
        location = os.environ['sne'] + '/photoz/' + cluster + '/SLRplots/'
        print 'deleting old plots'
        os.system('rm ' + location + '/*')
        os.system('mkdir -p ' + location)        
        print 'finished deleting old plots'

    import pickle
    f = open('maglocus_SYNTH','r')
    m = pickle.Unpickler(f)
    locus_mags = m.load()

    #import pickle
    #f = open('maglocus_SYNTH','r')
    #m = pickle.Unpickler(f)
    locus_pairs = get_locus() #m.load()






    
    if True:
        ''' assign locus color to each instrument band '''                                                                                                           

        instrument_to_locus = {}

        for filt in filterlist:
            a_short = filt.replace('+','').replace('C','')[-1]  
            print filt, a_short
            ok = True                                           
            if string.find(filt,'MEGAPRIME') != -1:
                a_short = 'MP' + a_short.upper() + 'SUBARU'
            elif string.find(filt,'SUBARU') != -1:
                if string.find(filt,"W-S-") != -1:
                    a_short = 'WS' + a_short.upper() + 'SUBARU'
                else:
                    a_short = a_short.upper() + 'JOHN'
            if string.find(filt,'-2-')==-1 and not (string.find(filt,'MEGAPRIME') != -1 and filt[-1] == 'u'):                                                       
                instrument_to_locus[filt] = a_short

        print instrument_to_locus
        #instrument_to_locus = {'u':'U'+DET,'g':'G'+DET,'r':'R'+DET,'i':'I'+DET,'z':'Z'+DET,'JCAT':'JTMASS'}

        ''' figure out the filter to hold '''
        list = ['SUBARU-10_2-1-W-C-RC','SUBARU-10_2-1-W-C-RC','MEGAPRIME-0-1-r','SUBARU-10_2-1-W-S-R+']
        for filt in list:
            if filt in filterlist:
                hold_all = filt
                break

        def f(x): return x!=hold_all and string.find(x,'-2-') == -1 and not (string.find(x,'MEGAPRIME') != -1 and x[-1] == 'u') #and string.find(x,'10_3') == -1
        vary_list = filter(f, filterlist)
        print vary_list

        #vary_list = ['SUBARU-10_3-1-W-J-V','SUBARU-10_2-1-W-S-Z+','SUBARU-10_2-1-W-C-IC','SUBARU-10_3-1-W-C-IC','MEGAPRIME-10_2-1-i','MEGAPRIME-10_2-1-z']
        print filterlist            

        #vary_list = ['SUBARU-10_3-1-W-J-V','SUBARU-10_2-1-W-S-Z+','SUBARU-10_2-1-W-C-IC','MEGAPRIME-10_2-1-i']
        print vary_list
        hold_all


        #while 


        ''' designate which filter zeropoint to be held constant when matching bands '''
        combos = [{'hold':hold_all,'vary':vary_list}]
        zps_dict_all = {} 
                                                                                                                  
        def update_zps(zps_dict_all,results):
            if not combo['hold'] in zps_dict_all:
                zps_dict_all[combo['hold']] = 0.
            for key in combo['vary']:
                zps_dict_all[key] = zps_dict_all[combo['hold']] + results['full'][key]
            return zps_dict_all
                                                                                                                  
        ''' first fit combinations of three bands'''
        for combo in combos:
            results = fit(table, combo, instrument_to_locus, magtype, locus_mags, locus_pairs, min_err, bootstrap=False, startingzps=startingzps, plotdir=location, pre_zps=None, gallat=gallat, extinct=extinct)
            print results
            zps_dict_all = update_zps(zps_dict_all,results)

        ''' finally fit all bands at once '''                                                                                  
        #combo = {'hold':'JCAT','vary':['u','g','r','i','z']}
        #results = fit(table, combo, instrument_to_locus, magtype, locus_mags, min_err, startingzps=zps_dict_all, bootstrap=True, plotdir=location, pre_zps=None,gallat=gallat)
        #zps_dict_all = update_zps(zps_dict_all,results)
        #print zps_dict_all


    if False:                                                                                                                                                                
        ''' assign locus color to each instrument band '''                                                                                                           
        DET = 'SDSS'
        magtype='APER'
    
        instrument_to_locus = {'SDSS_u':'U'+DET,'SDSS_g':'G'+DET,'SDSS_r':'R'+DET,'SDSS_i':'I'+DET,'SDSS_z':'Z'+DET,'JCAT':'JTMASS'}
                                                                                                                                                                     
        ''' designate which filter zeropoint to be held constant when matching bands '''
        combos = [{'hold':'SDSS_z','vary':['SDSS_r','SDSS_i']},{'hold':'SDSS_r','vary':['SDSS_u','SDSS_g']}]
                                                                                                                                                                     
        zps_dict_all = {} 
                                                                                                                  
        def update_zps(zps_dict_all,results):
            if not combo['hold'] in zps_dict_all:
                zps_dict_all[combo['hold']] = 0.
            for key in combo['vary']:
                zps_dict_all[key] = zps_dict_all[combo['hold']] + results['full'][key]
            return zps_dict_all
                                                                                                                  
        if True: 
            ''' first fit combinations of three bands'''
            for combo in combos:
                results = fit(table, combo, instrument_to_locus, magtype, locus_mags, locus_pairs, min_err, bootstrap=False,plotdir=location, pre_zps=False)
                print results
                zps_dict_all = update_zps(zps_dict_all,results)
                                                                                                                                                                      
            ''' finally fit all bands at once '''                                                                                  
            combo = {'hold':'SDSS_z','vary':['SDSS_u','SDSS_g','SDSS_r','SDSS_i']}
            results = fit(table, combo, instrument_to_locus, magtype, locus_mags, locus_pairs, min_err, startingzps=zps_dict_all, bootstrap=True, plotdir=location, pre_zps=False, extinct=extinct)
            zps_dict_all = update_zps(zps_dict_all,results)
            print zps_dict_all


    #zps_dict_all = {'SUBARU-10_2-1-W-J-B': 0.16128103741856098, 'SUBARU-10_2-1-W-C-RC': 0.0, 'SUBARU-10_2-1-W-S-Z+': 0.011793588122789772, 'MEGAPRIME-10_2-1-u': 0.060291451932493148, 'SUBARU-10_2-1-W-C-IC': 0.0012269407091880637, 'SUBARU-10_2-1-W-J-V': 0.013435398732369786}

    #zps_dict_all['SUBARU-10_2-1-W-C-RC'] = -99
    print zps_dict_all
    for key in zps_dict_all.keys():    
        offset_list_file.write('DUMMY ' + key + ' ' + str(zps_dict_all[key]) + ' 0\n')              
        #offset_list_file.write('DUMMY ' + key + ' ' + str(-99) + ' 0\n')              
    offset_list_file.close()
    if magtype == 'APER1': aptype='aper'
    elif magtype == 'ISO': aptype='iso'
    save_slr_flag = photocalibrate_cat_flag = '--spec mode=' + magtype
    print 'running save_slr'
    command = './save_slr.py -c %(cluster)s -i %(catalog)s -o %(offset_list)s %(save_slr_flag)s' % {'cluster':cluster, 'catalog':catalog, 'offset_list':offset_list, 'save_slr_flag':save_slr_flag}
    os.system(command)

    print 'running photocalibrate_cat'
    command = './photocalibrate_cat.py -i %(all_phot_cat_iso)s -c %(cluster)s -o %(slr_out_iso)s -t slr %(photocalibrate_cat_flag)s' % {'cluster':cluster, 'all_phot_cat_iso':all_phot_cat, 'slr_out_iso':slr_out_iso, 'photocalibrate_cat_flag':photocalibrate_cat_flag}
    os.system(command)

    command = './photocalibrate_cat.py -i %(all_phot_cat)s -c %(cluster)s -o %(slr_out)s -t slr %(photocalibrate_cat_flag)s' % {'cluster':cluster, 'all_phot_cat':all_phot_cat, 'slr_out':slr_out, 'photocalibrate_cat_flag':photocalibrate_cat_flag}
    os.system(command)
    print 'finished' 




    #for band in [['r','i','u','g'],['g','r','i','z'],['g','r','u','g'],['r','i','i','z'],['i','JCAT','i','z']]:
    #    plot(table,zps_dict_all,instrument_to_locus,magtype,locus_c, min_err,band,location)

    #return results

    


def plot(table,zplist,instrument_to_locus,magtype,locus_c, min_err,bands,location, alt_locus_c=None):

    b1,b2,b3,b4 = bands

    import pylab

    pylab.clf()

    if alt_locus_c:
        if instrument_to_locus[b1]+'_'+instrument_to_locus[b2] in alt_locus_c and instrument_to_locus[b3]+'_'+instrument_to_locus[b4] in alt_locus_c:                      
            print [instrument_to_locus[a] for a in [b1,b2,b3,b4]]
            pylab.scatter(alt_locus_c[instrument_to_locus[b1]+'_'+instrument_to_locus[b2]],alt_locus_c[instrument_to_locus[b3]+'_'+instrument_to_locus[b4]],color='green')


    if instrument_to_locus[b1]+'_'+instrument_to_locus[b2] in locus_c and instrument_to_locus[b3]+'_'+instrument_to_locus[b4] in locus_c:
        print [instrument_to_locus[a] for a in [b1,b2,b3,b4]]
        pylab.scatter(locus_c[instrument_to_locus[b1]+'_'+instrument_to_locus[b2]],locus_c[instrument_to_locus[b3]+'_'+instrument_to_locus[b4]],color='red')
    else:
        print '\n\n\n********************'
        print b1 +'-'+b2 + ' and ' + b3 + '-' + b4 + ' not both locus color'
        print 'possible locus bands:' 
        print    locus_c.keys()
        return

    x1 = table.field('MAG_' + magtype + '_reg_' + b1)
    x2 = table.field('MAG_' + magtype + '_reg_' + b2)
    x1_err = table.field('MAGERR_' + magtype + '_reg_' + b1)
    x2_err = table.field('MAGERR_' + magtype + '_reg_' + b2)
    x = x1 -zplist[b1] - (x2 - zplist[b2])
    x1_err[x1_err<min_err] = min_err
    x2_err[x2_err<min_err] = min_err
    x_err = (x1_err**2.+x2_err**2.)**0.5

    y1 = table.field('MAG_' + magtype + '_reg_' + b3)
    y2 = table.field('MAG_' + magtype + '_reg_' + b4)
    y1_err = table.field('MAGERR_' + magtype + '_reg_' + b3)
    y2_err = table.field('MAGERR_' + magtype + '_reg_' + b4)
    y1_err[y1_err<min_err] = min_err
    y2_err[y2_err<min_err] = min_err
    y = y1 -zplist[b3] - (y2 - zplist[b4])
    y_err = (y1_err**2.+y2_err**2.)**0.5

    import scipy

    good = scipy.array(abs(x1)<90) * scipy.array(abs(x2)<90) * scipy.array(abs(y1)<90) * scipy.array(abs(y2)<90) 

    pylab.scatter(x[good],y[good])
    pylab.errorbar(x[good],y[good],xerr=x_err[good],yerr=y_err[good],fmt=None)
    pylab.xlabel(b1 + '-' + b2,fontsize='x-large')
    pylab.ylabel(b3 + '-' + b4,fontsize='x-large')

    file = location + '/SLR'+b1+b2+b3+b4 +'.png'
    print file
    pylab.savefig(file)
    #pylab.show()
    #pylab.savefig('/Users/pkelly/Dropbox/plot.pdf')

    
def fit(table, combo_dict, instrument_to_locus, magtype, locus_mags, locus_pairs, 
        min_err=0.02, 
        min_bands_per_star=3, 
        startingzps=None, 
        plot_iteration_increment=50, 
        max_err=0.1, 
        bootstrap=False, 
        bootstrap_num=0, 
        plotdir='.', 
        save_bootstrap_plots=False, 
        live_plot=True,
        pre_zps=None,
        gallat=None,
        extinct=None):

    import string, re, pyfits, random, scipy, pylab
    from copy import copy

    if live_plot: 
        pylab.ion()

    zps ={} 
    for i in range(len(combo_dict['vary'])):
        zps[combo_dict['vary'][i]] = i
    
    number_locus_points = len(locus_mags) 
    number_all_stars = len(table.field('MAG_' + magtype + '-' + instrument_to_locus.keys()[0]))

    ''' for each point in locus, make a list of the locus in each color (locus has same number of points in each color) '''
    ''' just a rearrangement '''
    locus_list = []
    for j in range(number_locus_points):
        o = []
        for c in instrument_to_locus.values():
            o.append(locus_mags[j][c])
        locus_list.append(o)

    
    results = {} 

    if bootstrap:
        cycles = ['full'] + ['bootstrap' + str(i) for i in range(bootstrap_num)] 
    else:        
        cycles = ['full']

    for iteration in cycles:       
        ''' make matrix with a full set of locus points for each star '''    
        locus_matrix = scipy.array(number_all_stars*[locus_list])
        print locus_matrix.shape

        ''' assemble matricies to make instrumental measured bands '''
        print instrument_to_locus.keys()
        A_band = scipy.swapaxes(scipy.swapaxes(scipy.array(number_locus_points*[[table.field('MAG_' + magtype + '-' + a) for a in instrument_to_locus.keys()]]),0,2),1,2)

        n = len(table.field('MAG_' + magtype + '-' + instrument_to_locus.keys()[0]))

        def isitJ(name):
            import string
            if string.find(name,'JCAT') != -1:
                return scipy.ones(n)
            else: 
                return scipy.zeros(n)                

        A_err = scipy.swapaxes(scipy.swapaxes(scipy.array(number_locus_points*[[table.field('MAGERR_' + magtype + '-' + a) for a in instrument_to_locus.keys()]]),0,2),1,2)
    
        print A_err.shape

        ''' only use stars with errors less than max_err '''            

        if True:
            mask = A_err > max_err  
            #mask[A_band_J == 1] = 0
            mask[A_err > 1.5] = 1  
            A_band[mask] = 99

        ''' make matrix specifying good values '''
        good = scipy.ones(A_band.shape)

        #A_band[abs(A_FLAG) != 0] = 99 
        #A_band[abs(A_IMAFLAG) != 0] = 99 
        good[abs(A_band) == 99] = 0
        good[abs(A_band) == 0] = 0


        good = good[:,0,:]
        good_bands_per_star = good.sum(axis=1) # sum all of the good bands for any given star
        
        print good_bands_per_star 

        ''' figure out the cut-off '''
        A_band = A_band[good_bands_per_star>=min_bands_per_star]
        A_err = A_err[good_bands_per_star>=min_bands_per_star]

        A_err[A_err<min_err] = min_err 

        locus_matrix = locus_matrix[good_bands_per_star>=min_bands_per_star]

        ''' if a bootstrap iteration, bootstrap with replacement '''
        if string.find(iteration,'bootstrap') != -1:
            length = len(A_band)

            random_indices = []
            unique_indices = {}
            for e in range(length): 
                index = int(random.random()*length - 1)
                unique_indices[index] = 'yes'
                random_indices.append(index)

            print random_indices, len(unique_indices.keys())

            A_band = scipy.array([A_band[i] for i in random_indices])             
            A_err = scipy.array([A_err[i] for i in random_indices])
            locus_matrix = scipy.array([locus_matrix[i] for i in random_indices])
        
        bands = A_band 
        bands_err = A_err

        ''' set errors on bad measurements (value=+-99) equal to 100000. and bands equal to 0 '''
        bands_err[abs(A_band) == 99] = 1000.   
        bands[abs(A_band) == 99] = 0.   

        print bands.shape, locus_matrix.shape
        number_good_stars = len(locus_matrix)

        ''' update good matrix after masking '''
        good = scipy.ones(A_band.shape) 
        good[abs(A_band) == 99] = 0
        good[abs(A_band) == 0] = 0

        global itr
        itr = 0

        keep_fitting = True
        outliers = 'no outlier rejection'

        while keep_fitting:
        
            def errfunc(pars,residuals=False,savefig=None):                                                                                                                                           
                global itr 
                                                                                                                                                                                                      
                stat_tot = 0
                                                                                                                                                                                                      
                zp_bands = scipy.zeros((number_good_stars,number_locus_points,len(instrument_to_locus.keys()))) 
                for i in range(len(instrument_to_locus.keys())):
                    a = instrument_to_locus.keys()[i]
                    zp_bands[:,:,i] = assign_zp(a,pars,zps)
                                                                                                                                                                                                      
                print zp_bands.shape, bands.shape, locus_matrix.shape, good.shape, number_good_stars, number_locus_points
                num_prelim = (bands - locus_matrix + zp_bands) / bands_err**2. 
                num_prelim[good == 0] = 0.
                num = (num_prelim.sum(axis=2))
                                                                                                                                                                                                      
                denom_prelim = 1. / bands_err**2. 
                denom_prelim[good == 0] = 0.
                denom = (denom_prelim.sum(axis=2))
                                                                                                                                                                                                      
                mean = num / denom
                                                                                                                                                                                                      
                mean_array = scipy.dstack(len(instrument_to_locus.keys())*[mean])
                                                                                                                                                                                                      
                ds_prelim = (bands - locus_matrix + zp_bands - mean_array)**2. #/ ds_err**2. 
                ds_prelim[good == 0] = 0
                ''' calculate reduced chi squared '''
                ds = ds_prelim.sum(axis=2)**0.5 
                                                                                                                                                                                                      
                resid_prelim = (bands - locus_matrix + zp_bands - mean_array )**2. / bands_err**2. 
                                                                                                                                                                                                      
                plot = (bands -locus_matrix + zp_bands - mean_array ) 
                                                                                                                                                                                                      
                                                                                                                                                                                                      
                resid_prelim[good == 0] = 0
                ''' calculate reduced chi squared '''
                resid = resid_prelim.sum(axis=2) / good.sum(axis=2) 
                                                                                                                                                                                                      
                                                                                                                                                                                                      
                if False: #live_plot and iteration is 'full' and (itr % plot_iteration_increment == 0 or savefig is not None):
                                                                                                                                                                                                
                    id = 100
                                                                                                                                                                                                      
                    for id in [10,20,30,40,100,150]:
                                                                                                                                                                                                
                        best = 99999999999999999999999999999999999999999999999999999999                                                                                                              
                        for i in range(len(resid[id])):
                            if resid[id][i] < best:
                                star = i
                                best = resid[id][i]
                                                                                                                                                                                                    
                                                                                                                                                                                                    
                        pylab.clf()                                                                                                                                                                 
                        pylab.scatter(range(len(plot[id][star])),plot[id][star])                
                        #pylab.scatter(range(len(plot[id][0])),locus_matrix[id][0])                
                        pylab.errorbar(range(len(plot[id][star])),plot[id][star],yerr=bands_err[id][star])                
                        pylab.ylim([-0.4,0.4])
                                                                                                                                                                                                      
                        pylab.draw()
                                                                                                                                                                                                      
                        pylab.draw()
                        print combo_dict['vary'], resid_prelim[id][star], (bands - locus_matrix + zp_bands - mean_array)[id][star], bands_err[id][star], good[id][star], resid[id], resid[id][star]
                                                                                                                                                                                                      
                #print (bands - locus_matrix + zp_bands - mean_array )[10], bands_err[10]
                #raw_input()
                                                                                                                                                                                                      
                ''' these two are not necessarily the same star '''
                dist = ds.min(axis=1)
                select_diff = resid.min(axis=1)
                                                                                                                                                                                                      
                #for i in range(len(ds.min(axis=0))):
                #    print i
                #    print len(ds[0]), len(ds.min(axis=0))
                #    print ds[0][i]
                #    print ds.min(axis=1)[i]
                #print 'end of locus', end_of_locus, ds.min(axis=1), ds[0]
                                                                                                                                                                                                      
                stat_tot = select_diff.sum()
                print 'ZPs', dict(zip([combo_dict['hold']]+combo_dict['vary'],([0.] + ['%.6f' % a for a in pars.tolist()])))
                print len(bands), 'stars'
                redchi = stat_tot / float(len(bands) - 1)
                print 'chi^2', '%.5f' % stat_tot, 
                print 'red chi^2', '%.5f' % redchi
                print 'iteration', itr
                if live_plot and iteration is 'full' and (itr % plot_iteration_increment == 0 or savefig is not None):
                    #savefig = None 
                    plot_progress(pars,stat_tot,savefig)
                itr += 1
                                                                                                                                                                                                      
                if residuals:
                    end_of_locus = scipy.array([reduce(lambda x,y: x*y, [resid.min(axis=1)[i] != resid[i][x] for x in range(5)]) for i in range(len(ds.min(axis=1)))]) 
                    print end_of_locus
                    return select_diff, dist, redchi, end_of_locus, len(bands)
                else: return stat_tot
                                                                                                                                                                                                      
            def plot_progress(pars,stat_tot=None,savefig=None):
                                                                                                                                                                                                      
                import pylab, scipy                                                           
                                                                                                                                                                                                      
                zp_bands = scipy.zeros((number_good_stars,number_locus_points,len(instrument_to_locus.keys()))) 
                for i in range(len(instrument_to_locus.keys())):
                    a = instrument_to_locus.keys()[i]
                    zp_bands[:,:,i] = assign_zp(a,pars,zps)
                                                                                                                                                                                                      
                                                                                                                                                                                                      
                                                                                                                                                                                                      
                                                                                                                                                                                                      
                if pre_zps:
                    #pre_zp_A = scipy.swapaxes(scipy.swapaxes(scipy.array(number_locus_points*[number_good_stars*[[pre_zps[a[0][0]] for a in complist]]]),0,1),0,0) 
                    #pre_zp_B = scipy.swapaxes(scipy.swapaxes(scipy.array(number_locus_points*[number_good_stars*[[pre_zps[a[1][0]] for a in complist]]]),0,1),0,0)
                    #pre_zp_bands = pre_zp_A - pre_zp_B
                    pre_zp_bands = scipy.swapaxes(scipy.swapaxes(scipy.array(number_locus_points*[number_good_stars*[[assign_zp(a[0],pars,pre_zps) for a in instrument_to_locus.keys()]]]),0,1),0,0)
                                                                                                                                                                                                      
                    pre_zp_bands = scipy.zeros((number_good_stars,number_locus_points,len(pre_zpz))) 
                    for i in range(len(pre_zps)):
                        a = pre_zps[i]
                        zp_bands[:,:,i] = assign_zp(a[0][0],pars,zps)-assign_zp(a[1][0],pars,zps)
                                                                                                                                                                                                      
                oa = instrument_to_locus.keys()
                if savefig is not None:
                    #index_list = zip([int(x) for x in 2*scipy.arange(len(complist)/2)],[int(x) for x in 2*scipy.arange(len(complist)/2)+scipy.ones(len(complist)/2)])
                    #if len(complist) > 2*(len(complist)/2):
                    #    index_list.append([len(complist)-2,len(complist)-1])
                    #print index_list
                    index_list = []
                    print instrument_to_locus.keys()        
                    rng = range(len(instrument_to_locus.keys()))
                    for a in rng: #range(len(complist)):
                        for b in rng: #range(len(complist)):
                            if a < b:
                                for c in rng: #range(len(complist)):
                                    if b < c:
                                        for d in rng: #range(len(complist)):
                                            if c < d:
                            #if c < d and c > b:
                                                index_list.append([[oa[a],oa[b]],[oa[c],oa[d]]])
                                                                                                                                                                                                      
                    print index_list #, range(len(complist)), complist
                                                                                                                                                                                                      
                    index_list += [[['SUBARU-10_3-1-W-J-V','SUBARU-10_2-1-W-S-Z+'],['SUBARU-10_2-1-W-C-IC','MEGAPRIME-10_2-1-i']]]

                    index_list = index_list[:]
                                                                                                                                                                                                      
                    #index_list = [[['SUBARU-10_2-1-W-C-RC''SUBARU-10_2-1-W-S-Z+'],['SUBARU-10_2-1-W-S-Z+','SUBARU-10_3-1-W-J-V']]]
                                                                                                                                                                                                      
                                                                                                                                                                                                      
                else: 
                    #index_list = [[[complist[1][0],complist[2][0]],[complist[3][0],complist[4][0]]]]
                    index_list = [[['MEGAPRIME-10_2-1-g','SUBARU-10_2-1-W-C-RC'],['SUBARU-10_2-1-W-C-RC','MEGAPRIME-10_2-1-z']]]
                                                                                                                                                                                                      
                    index_list = [[['SUBARU-10_2-1-W-C-RC','SUBARU-10_2-1-W-S-Z+'],['SUBARU-10_2-1-W-S-Z+','SUBARU-10_3-1-W-J-V']]]
                                                                                                                                                                                                      
                    index_list = [[['SUBARU-10_3-1-W-J-V','SUBARU-10_2-1-W-S-Z+'],['SUBARU-10_2-1-W-C-IC','MEGAPRIME-10_2-1-i']]]
                                                                                                                                                                                                      
                    index_list = [[[oa[0],oa[1]],[oa[1],oa[2]]]]
                                                                                                                                                                                                      
                                                                                                                                                                                                      
                print index_list
                                                                                                                                                                                                      
                print instrument_to_locus 
                                                                                                                                                                                                      
                def ind(filt):
                    for j in range(len(instrument_to_locus.keys())):
                        if instrument_to_locus.keys()[j] == filt:
                            return j
                                                                                                                                                                                                      
                for [c1_band1, c1_band2], [c2_band1,c2_band2] in index_list: 
                                                                                                                                                                                                      
                    print instrument_to_locus.values()
                    
                    print ind(c1_band1), ind(c1_band2)
                                                                                                                                                                                                      
                    print ind(c2_band1), ind(c2_band2)
                                                                                                                                                                                                      
                    print c2_band1, c2_band2
                                                                                                                                                                                                      
                                                                                                                                                                                                      
                                                                                                                                                                                                      
                    if ind(c1_band1) is not None and ind(c1_band2) is not None and ind(c2_band1) is not None and ind(c2_band2) is not None:
                        x_color = scipy.array(bands + zp_bands)[:,0,ind(c1_band1)] - scipy.array(bands + zp_bands)[:,0,ind(c1_band2)]
                        print ind(c2_band1), ind(c2_band2)
                                                                                                                                                                                                      
                        y_color = (bands + zp_bands)[:,0,ind(c2_band1)] - (bands + zp_bands)[:,0,ind(c2_band2)]
                                                                                                                                                                         
                        if pre_zps:
                            pre_x_color = scipy.array((bands + pre_zp_bands)[:,0,color1_index].tolist())
                            pre_y_color = (bands + pre_zp_bands)[:,0,color2_index]
                                                                                                                                                                         
                        x_err_1 = (bands_err)[:,0,ind(c1_band1)]
                        x_err_2 = (bands_err)[:,0,ind(c1_band2)]
                                                                                                                                                                         
                        y_err_1 = (bands_err)[:,0,ind(c2_band1)]
                        y_err_2 = (bands_err)[:,0,ind(c2_band2)]
                                                                                                                                                                         
                        mask = (x_err_1<100)*(x_err_2<100)*(y_err_1<100)*(y_err_2<100)
                        x_color = x_color[mask]
                        y_color = y_color[mask]
                                                                                                                                                                         
                        x_err = (x_err_1**2. + x_err_2**2.)**0.5
                        y_err = (y_err_1**2. + y_err_2**2.)**0.5
                                                                                                                                                                         
                        y_err = y_err[mask]
                        x_err = x_err[mask]
                        
                        if pre_zps:
                            pre_x_color = pre_x_color[mask]
                            pre_y_color = pre_y_color[mask]
                                                                                                                                           
                        print len(x_color), len(x_color) 
                                                                                                                                           
                        pylab.clf()                                                                             
                                                                                                                                                                         
                        x_a = c1_band1 #complist[color1_index][0][0]
                        x_b = c1_band2 #complist[color1_index][1][0]
                                                                                                                                                                      
                        y_a = c2_band1 #complist[color2_index][0][0]
                        y_b = c2_band2 #complist[color2_index][1][0]
                                                                                                                                                                         
                        print extinct, x_a
                        
                        x_extinct = extinct[x_a] - extinct[x_b]
                        y_extinct = extinct[y_a] - extinct[y_b]
                                                                                                                                                                         
                        x_color_name = x_a + '-' + x_b 
                        y_color_name = y_a + '-' + y_b 
                        pylab.xlabel(x_color_name,fontsize='x-large')
                        pylab.ylabel(y_color_name,fontsize='x-large')
                                                                                                                                           
                        pylab.errorbar(x_color,y_color,xerr=x_err,yerr=y_err,fmt=None,ecolor='gray')
                        pylab.errorbar(x_color,y_color,xerr=0,yerr=0,fmt=None,marker='s',
             mfc='re    d', mec='green', ms=1, mew=1)
                                                                                                                                                                         
                        #pylab.scatter(x_color,y_color,s=0.1)
                        c1_locus = locus_matrix[0,:,ind(c1_band1)] - locus_matrix[0,:,ind(c1_band2)]
                        c2_locus = locus_matrix[0,:,ind(c2_band1)] - locus_matrix[0,:,ind(c2_band2)]
                        pylab.errorbar(c1_locus,c2_locus,xerr=0,yerr=0,color='red')
                                                                                                                                                                         
                        if pre_zps:
                            pylab.errorbar(pre_x_color,pre_y_color,xerr=x_err,yerr=y_err,fmt=None,c='green')
                            pylab.scatter(pre_x_color,pre_y_color,c='green')
                                                                                                                                                                         
                        #print locus_matrix[0,:,color1_index][0]
                        pylab.arrow(c1_locus[0],c2_locus[-1],x_extinct,y_extinct,width=0.01,color='black')
                                                                                                                                                                         
                                                                                                                                                                         
                        if stat_tot is not None:
                            pylab.title('N=' + str(len(x_color)) + ' chi$^{2}$=' + ('%.1f' % stat_tot) + ' ' + iteration + ' ' + outliers + ' LAT=' + ('%.1f' % gallat))
                                                                                                                                                                         
                        if live_plot:
                            pylab.draw()
                                                                                                                                                                         
                        fit_band_zps = reduce(lambda x,y: x + y, [z[-2:].replace('C','').replace('-','') for z in [combo_dict['hold']] + combo_dict['vary']])
                                                                                                                                                                         
                        ''' only save figure if savefig is not None '''
                        if savefig is not None: 
                            if (string.find(iteration,'bootstrap')==-1 or save_bootstrap_plots):
                                pylab.savefig(plotdir + '/' + fit_band_zps + '_' + x_color_name + '_' + y_color_name + '_' + savefig.replace(' ','_'))
                        #pylab.show()
                                                                                                                                                                                                      
            #def median_starting_zp():
                #for key in combo_dict['vary']:            
                #    median = instrument_to_locus[key]
                                                                                                                                                                                                      
                    
                    
            ''' starting guess for zeropoint : median hold instrumental magnitude - median hold locus magnitude ''' 
            print A_band.shape
            pinit = []
            for i in range(1,len(instrument_to_locus.keys())):
                key = instrument_to_locus.keys()[i]
                key_hold = instrument_to_locus.keys()[0]
                diff = A_band[:,0,i] - A_band[:,0,0]
                good_diff = good[:,0,i] + good[:,0,0]
                diff = diff[good_diff == 2]
            
                median_instrumental = scipy.median(diff)
                locus_here = [locus_mags[x][instrument_to_locus[key]] - locus_mags[x][instrument_to_locus[key_hold]] for x in range(len(locus_mags))]
                median_locus = scipy.median(locus_here)
                                                                                                                                                                                                      
                pinit.append(median_locus - median_instrumental)
                
            print pinit 
                                                                                                                                                                                                      
                                                                                                                                                                                                      
            if True:            
                if iteration == 'full':                                                                                  
                    print startingzps.keys()
                    if startingzps is None:
                        pinit = scipy.zeros(len(combo_dict['vary']))
                    else:
                        pinit = []
                        for key in combo_dict['vary']:
                            try1 = key.replace('10_2','').replace('10_1','').replace('10_3','').replace('9-4','')
                            try2 = key.replace('10_2','').replace('10_1','').replace('10_3','').replace('9-4','') + '-1'
                            if startingzps.has_key(key):
                                val = startingzps[key]
                            elif startingzps.has_key(try1):
                                val = startingzps[try1]
                            elif startingzps.has_key(try2):
                                val = startingzps[try2]
                            pinit.append(val)
                                                                                                                         
                                                                                                                         
                                                                                                                         
                else:
                    import random
                    ''' add random offset of 1.0 mag '''
                    pinit = [results['full'][key] + random.random()*1.0 for key in combo_dict['vary']]
                                                                                                                                                                                                      
                                                                                                                                                                                                      
            from scipy import optimize
            out = scipy.optimize.fmin(errfunc,pinit,maxiter=100000,args=()) #,gtol=0.001) 
            if iteration is 'full':
                errfunc(out,savefig=iteration+'_'+outliers+'.png')
            print out
                                                                                                                                                                                                      
            import scipy                                                              
            print 'starting'        
            residuals,dist,redchi,end_of_locus, num  = errfunc(pars=[0.] + out,residuals=True)
                                                                                                                                                                                                      
            print dist
                                                                                                                                                                                                      
                                                                                                                                                                                                      
            print 'finished'
            print 'bands' , len(bands)
                                                                                                                                                                                                      
                                                                                      
            ''' first filter on distance '''
            bands = bands[dist < 1.5]
            bands_err = bands_err[dist < 1.5]
            locus_matrix = locus_matrix[dist < 1.5]
            good = good[dist < 1.5]
            residuals = residuals[dist < 1.5]
            end_of_locus = end_of_locus[dist < 1.5]

            print end_of_locus
                                                                                                                                                                                                      
            print bands.shape
            print dist.shape, residuals.shape
                                                                                                                                                                                                      
            if True:                                                                          
                ''' filter on residuals '''                
                print bands.shape, residuals.shape
                bands = bands[residuals < 6]
                bands_err = bands_err[residuals < 6]
                locus_matrix = locus_matrix[residuals < 6]
                good = good[residuals < 6]
                end_of_locus = end_of_locus[residuals < 6]
                                                                                                                                                                                                      
                                                                                                                                                                                                      
            if True:
                ''' filter on end of locus '''            
                bands = bands[end_of_locus]
                bands_err = bands_err[end_of_locus]
                locus_matrix = locus_matrix[end_of_locus]
                good = good[end_of_locus]
                                                                                                                                                                                                      
                                                                                                                                                                                                      
            print number_good_stars, len(locus_matrix)
                                                                                      
            if number_good_stars > len(locus_matrix) or len(filter(lambda x: x is False,end_of_locus.tolist())) > 0:
                
                print 'REFITTING AFTER REMOVING ' + str(number_good_stars - len(locus_matrix) ) + ' OUTLIERS AND STARS MATCHING BLUE END OF LOCUS'


                number_good_stars = len(locus_matrix)

                print 'bands' , len(bands)                                     

                print bands.shape, locus_matrix.shape
                
                pinit = out #scipy.zeros(len(zps_list))                         

                outliers = 'outliers removed'

                if False:                                                                 
                    pinit = scipy.array(out) + scipy.array([random.random()*1.0 for p in pinit])                                 
                    pinit = out #scipy.zeros(len(zps_list))                         
                    from scipy import optimize
                    out = scipy.optimize.fmin(errfunc,pinit,args=()) 
                    residuals,dist,redchi,end_of_locus, num  = errfunc(out,savefig=iteration+'_'+outliers+'.png',residuals=True)
                    print out
            else:
                print 'NO OUTLYING STARS OR STARS MATCHING BLUE END OF LOCUS, PROCEEDING'
                keep_fitting = False

        results[iteration] = dict(zip([combo_dict['hold']]+combo_dict['vary'],([0.] + out.tolist())))

        mask = bands_err < 100

    results['redchi'] = redchi
    results['num'] = num        

    print results    
    errors = {}
    bootstraps = {}
    import scipy
    print 'BOOTSTRAPPING ERRORS:'
    for key in [combo_dict['hold']] + combo_dict['vary']:
        l = []
        for r in results.keys():
            if r != 'full' and r != 'redchi' and r != 'num':
                l.append(results[r][key])
        print key+':', scipy.std(l), 'mag'
        
        errors[key] = scipy.std(l)

        if bootstrap_num > 0 and len(l) > 0:
            bootstraps[key] = reduce(lambda x,y: x + ',' + y, [str(z) for z in l])
        else: bootstraps[key] = 'None'

    results['bootstraps'] = bootstraps
    results['errors'] = errors
    results['bootstrapnum'] = bootstrap_num 
    

    if False:
        def save_results(save_file,results,errors):                                               
            f = open(save_file,'w')
            for key in results['full'].keys():
                f.write(key + ' ' + str(results['full'][key]) + ' +- ' + str(errors[key]) + '\n')
            f.close()
                                                                                                  
            import pickle 
            f = open(save_file + '.pickle','w')
            m = pickle.Pickler(f)
            pickle.dump({'results':results,'errors':errors},m)
            f.close()

        if results.has_key('full') and save_results is not None: save_results(save_file,results, errors)
                                                              
    return results

#@entryExit
def sdss(run,night,snpath,name=None): 
    
    import pylab, pyfits, commands

    input_cat = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/stars.fits'
    p = pyfits.open(input_cat)[1].data

    
    #pylab.scatter(p.field('psfMag_g') - p.field('psfMag_r'),p.field('MAG_APER_u') - p.field('psfMag_u'))
    #pylab.errorbar(x[good],y[good],xerr=x_err[good],yerr=y_err[good],fmt=None)
    #pylab.show()

    import transform_filts, scipy

    kit = get_kit()

    det = 'T2KB'

    print kit.keys()

    aptype = 'psfMag_' #'MAG_APERCORR-SDSS_'
    aptype_err = 'psfMagErr_' #'MAGERR_APERCORR-SDSS_'



    for mag in ['APERCORR','APERDUST']:

        cat_aptype = 'MAG_' + mag + '-' #'psfMag_'
        cat_aptype_err = 'MAGERR_' + mag + '-' #'psfMagErr_'

        for filt in ['u','g','r','i','z']:
        
            running = p.field(aptype + 'g') - p.field(aptype + 'i')
            x = p.field('ra')[running==0.47440300000000235]
            y = p.field('dec')[running==0.47440300000000235]
            #print x,y
            variation=transform_filts.apply_kit(running,kit[filt.upper() + det])

            print variation
    
            calibrated = p.field(aptype + filt) + variation 
            uncalibrated = p.field(cat_aptype + filt) 
    
            error = (p.field(aptype_err + filt)**2. + p.field(cat_aptype_err + filt)**2.)**0.5
    
            mask= (error < 0.1) * (p.field('FLAGS-' + filt) == 0) * (p.field('IMAFLAGS_ISO-' + filt) == 0.)
    
            #mask *= (error < 0.1) * (p.field('FLAGS-SDSS_' + filt) == 0) * (p.field('IMAFLAGS_ISO-SDSS_' + filt) == 0.)
    
            mask *= (p.field('FLAGS-g') == 0) * (p.field('IMAFLAGS_ISO-g') == 0.)
    
            mask *= (p.field('FLAGS-i') == 0) * (p.field('IMAFLAGS_ISO-i') == 0.)
    
            #mask *= p.field('FLAGS_SDSS') == 0
    
            print mask
    
            running = running[mask]           
            calibrated = calibrated[mask]
            uncalibrated = uncalibrated[mask]
            error = error[mask]
    
            #print running, p.field('psfMag_g'), p.field('psfMag_i')
            #print sorted(running)
    
            #print p.field('SDSS_NEIGHBORS'), p.field('psfMag_g')
    
            error[error < 0.02] = 0.02
            print calibrated
    
            def compute(cal_sample, uncal_sample, error_sample):
                zp = scipy.average(cal_sample - uncal_sample,weights=1./error_sample**2.) 
                zp = scipy.median(cal_sample - uncal_sample)
                mask = abs(cal_sample- uncal_sample-zp)/error_sample < 6.
                cal_sample= cal_sample[mask]     
                uncal_sample= uncal_sample[mask]
                error_sample = error_sample[mask]
                zp = scipy.average(cal_sample - uncal_sample,weights=1./error_sample**2.)
                zp_med = scipy.median(cal_sample - uncal_sample)
                                                                                                  
                return zp, zp_med
    
    
            zps = []
            for i in range(100):
                import random
                random_indices = []
                unique_indices = {}
    
                length = len(calibrated)
                for e in range(length): 
                    index = int(random.random()*length - 1)
                    unique_indices[index] = 'yes'
                    random_indices.append(index)
    
    
                cal = scipy.array([calibrated[i] for i in random_indices])             
                uncal = scipy.array([uncalibrated[i] for i in random_indices])             
                err = scipy.array([error[i] for i in random_indices])             
    
                zp, zp_med = compute(cal,uncal,err)
    
                zps.append(zp)
    
    
            zp = scipy.mean(zps)
            zp_err = scipy.std(zps)
            
            pylab.clf()
            pylab.title(str(zp) + ' +- ' + str(zp_err))
            pylab.axhline(zp,c='red')
            pylab.axhline(zp+zp_err,c='red')
            pylab.axhline(zp-zp_err,c='red')
            pylab.scatter(running,calibrated-uncalibrated)
            pylab.errorbar(running,calibrated-uncalibrated,yerr=error,fmt=None)
            tab = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/sdss_stars' + filt + '.png'
            print tab
            pylab.savefig(tab)
            pylab.savefig('/Users/pkelly/Dropbox/sdss' + filt + '.png')
    
            pylab.clf()
            pylab.title(str(zp) + ' +- ' + str(zp_err))
            pylab.scatter(calibrated,uncalibrated-calibrated)
            pylab.errorbar(calibrated,uncalibrated-calibrated,yerr=error,fmt=None)
            tab = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/bias_stars' + filt + '.png'
            print tab
            pylab.savefig(tab) 
            pylab.savefig('/Users/pkelly/Dropbox/bias_sdss' + filt + '.png')
    
    
    
    
    
    
    
    
    
    
    
    
            #pylab.show()
    
    
            image = '/Volumes/mosquitocoast/patrick/kpno/' + run +'/' + night + '/' + snpath + '/' + filt + '/reg.fits'
            import scamp
            name = 'reg'
            print image, snpath, filt, name, run
            reload(scamp).add_image(image,snpath,filt,name,run)
            import MySQLdb
            db2 = MySQLdb.connect(db='calib')
            c = db2.cursor()
            if mag=='APERCORR':
                command = "UPDATE CALIB set SDSSZP=" + str(zp) + " WHERE SN='" + snpath + "' and FILT='" + filt + "' and NAME='" + name + "' and RUN='" + run + "'"                
                c.execute(command)
                command = "UPDATE CALIB set SDSSZPERR=" + str(zp_err) + " WHERE SN='" + snpath + "' and FILT='" + filt + "' and NAME='" + name + "' and RUN='" + run + "'" 
                c.execute(command)
                command = "UPDATE CALIB set SDSSNUM=" + str(len(calibrated)) + " WHERE SN='" + snpath + "' and FILT='" + filt + "' and NAME='" + name + "' and RUN='" + run + "'" 
                c.execute(command)                                                                                                                       
            elif mag=='APERDUST':
                command = "UPDATE CALIB set SDSSDUSTZP=" + str(zp) + " WHERE SN='" + snpath + "' and FILT='" + filt + "' and NAME='" + name + "' and RUN='" + run + "'"                
                print command
                c.execute(command)
                command = "UPDATE CALIB set SDSSDUSTZPERR=" + str(zp_err) + " WHERE SN='" + snpath + "' and FILT='" + filt + "' and NAME='" + name + "' and RUN='" + run + "'" 
                c.execute(command)
                command = "UPDATE CALIB set SDSSDUSTNUM=" + str(len(calibrated)) + " WHERE SN='" + snpath + "' and FILT='" + filt + "' and NAME='" + name + "' and RUN='" + run + "'" 
                c.execute(command)                                                                                                                       









        
    
            print filt, zp, zp_med


def plot_zp():

    import MySQLdb, scipy
    db2 = MySQLdb.connect(db='calib')
    c = db2.cursor()

    for filt in ['u','g','r','i','z']:
        command = 'select JD, SLRZP, sn from calib where gallat is not null and  slrzp is not null and filt="'   + filt + '"' # and run="kpno_May2010"' #JD > 2455470'

        #command = 'select JD, SLRZP, sn from calib where gallat is not null and  slrzp is not null and filt="'   + filt + '" and exptime=120'
        c.execute(command)
        results = c.fetchall()

        print results 
                                                                         
        x = [float(a[0]) for a in results]
        y = [float(a[1]) for a in results]
        s = [(a[2][4:]) for a in results]


        import pylab
        pylab.clf() 

        for i in range(len(x)):
            pylab.text(x[i],y[i],s[i],fontsize=8)
                                                                         
                                                                         
        pylab.scatter(x,y)
        pylab.title(filt)
        pylab.savefig('/Users/pkelly/Dropbox/test' + filt + '.pdf')
        #pylab.show()            


def plot_detail(calibrate=False):
    import MySQLdb, scipy
    db2 = MySQLdb.connect(db='calib')
    c = db2.cursor()
    for filt in ['u','g','r','i','z']:

        import pylab
        pylab.clf() 

        def p(command,color):
            
            import MySQLdb, scipy
            db2 = MySQLdb.connect(db='calib')
            c = db2.cursor()



            c.execute(command)                 
            results = c.fetchall()

            print results

            x = scipy.array([float(a[0]) for a in results])                                   
            y = scipy.array([float(a[1]) for a in results])                                   
            y_err = scipy.array([float(a[2]) for a in results])
            s = [(a[3][4:]) for a in results]                                    
            for i in range(len(x)):
                pylab.text(x[i]+0.01,y[i]+0.00,s[i],fontsize=8)

            print x
            if 1:
                                               
                pylab.errorbar(x,y,y_err,fmt='ro',color=color)
                pylab.scatter(x,y,c=color)
                x_new = scipy.arange(1,3)
                print len(x), len(y)
                p = scipy.polyfit(x,y,1)                    
                y_new = scipy.polyval(p, x_new)
                pylab.plot(x_new,y_new, color='black')

                A = scipy.vstack([x/y_err, scipy.ones(len(x))/y_err]).T
                print A
                from scipy import linalg
            
                m,c = scipy.linalg.lstsq(A,y/y_err)[0]
                print m,c
                pylab.plot(x_new,m*x_new + c, color='blue')
                print x_new, m*x_new
            return m,c

        run = 'kpno_Oct2010'
        variable = 'airmass'
        command = 'select b.' + variable + ', c.slrdustzp+b.RELZP, c.slrdustzperr, b.sn from calib as c join calib b on c.sn=b.sn and c.run=b.run and c.filt=b.filt where c.slrzp is not null and c.slrzperr is not null and c.slrnum > 10 and b.relzp is not null and c.filt="' + filt + '" and c.run="' + run + '" and c.slrzperr<8 and c.JD>2455475'
        #p(command,'blue')
        command = 'select b.' + variable + ', c.sdssdustzp+b.RELZP, c.sdssdustzperr, b.sn from calib as c join calib b on c.sn=b.sn and c.run=b.run and c.filt=b.filt where c.sdssdustzp is not null and c.sdsszperr is not null and c.sdssnum > 1 and b.relzp is not null and c.filt="' + filt + '" and c.run="' + run + '" and b.night=4297' #  and c.JD>2455475'
        print command
        m_fit,c_fit = p(command,'red')


        if calibrate:
            #for filt in ['u','g','r','i','z']:                                                                                                       
            #command = 'select sn, airmass, sdssdustzp, run from calib where night=4297 and filt="'   + filt + '" group by sn,filt'

            command = 'select sn, airmass, sdssdustzp, run from calib where night=4353 and sn="sn1997ef" and filt="'   + filt + '" group by sn,filt'
            print command
            c.execute(command)                 
            results = c.fetchall()
            print results
                                                                                                                                                      
            import string  , os          
            for sn, airmass, sdssdustzp, run in results:
                if not sdssdustzp:
                    sdssphotozp = m_fit*float(airmass) + c_fit 
                else: 
                    sdssphotozp = float(sdssdustzp)
                    print sdssphotozp, sdssdustzp, sn
                                                                                                                                                      
                command = 'sethead ' + os.environ['kpno'] + '/' + run+ '/work_night/' + sn + '/' + filt + '/reg.fits SDSSPHOTOZP=' + str(sdssphotozp)
                print command
                os.system(command)

                command = 'sethead ' + os.environ['kpno'] + '/' + run+ '/work_night/' + sn + '/' + filt + '/reg.sdss.fits SDSSPHOTOZP=' + str(sdssphotozp)
                print command
                os.system(command)




                command = 'update calib set sdssphotozp=' + str(sdssphotozp) + ' where sn="' + sn + '" and run="' + run + '" and filt="' + filt + '"'
                c.execute(command)

                import anydbm
                gh = anydbm.open(sn)
                gh['sdssphotozp_' + filt ] = str(sdssphotozp)

                import commands
                gain = commands.getoutput('gethead ' + os.environ['kpno'] + '/' + run+ '/work_night/' + sn + '/' + filt + '/reg.fits GAIN')

                detector = commands.getoutput('gethead ' + os.environ['kpno'] + '/' + run+ '/work_night/' + sn + '/' + filt + '/reg.fits DETECTOR')
                gh['gain_' + filt + '_' + detector ] = gain

             

        
        

        
        
        
                                                                         
                                                                         
        pylab.title(filt)
        pylab.savefig('/Users/pkelly/Dropbox/test' + filt + '.pdf')


if __name__ == '__main__':
    import os , sys, string
    subarudir = os.environ['subdir']
    cluster = sys.argv[1] #'MACS1423+24'
    spec = False 
    train_first = False 
    magtype = 'APER1'
    AP_TYPE = ''
    type = 'all' 
    if len(sys.argv) > 2:                                                                   
        for s in sys.argv:
            if s == 'spec':
                type = 'spec'            
                spec = True
            if s == 'rand':
                type = 'rand'
            if s == 'train':
                train_first = True
            if s == 'ISO':
                magtype = 'ISO'
            if s == 'APER1':
                magtype = 'APER1'
    
            if s == 'APER':
                magtype = 'APER'
    
            if string.find(s,'detect') != -1:
                import re
                rs = re.split('=',s)
                DETECT_FILTER=rs[1]
            if string.find(s,'spectra') != -1:
                import re
                rs = re.split('=',s)
                SPECTRA=rs[1]
            if string.find(s,'aptype') != -1:
                import re
                rs = re.split('=',s)
                AP_TYPE = '_' + rs[1]
    
    #photdir = subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + AP_TYPE + '/'
    all(subarudir,cluster,DETECT_FILTER,AP_TYPE,magtype)
