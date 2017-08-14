
def calc_comp(cluster,DETECT_FILTER,AP_TYPE,spectra,magtype='APER1',verbose=True,type='rand',plot=False):
    from useful import *
    from coeio import loaddata, loadfile, params_cl, str2num, loaddict, findmatch1, pause  #, prange, plotconfig
    
    if type == 'rand': suffix = 'rand'
    elif type == 'spec': suffix = 'spec'
    else: suffix = 'all'
    
    import os
    run_name =  os.environ['subdir'] + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + '' + AP_TYPE + '/' + cluster + '.' + magtype + '.1.' + spectra + '.' + suffix
    print run_name, 'run_name'
    
    cat = None
    if cat == None: cat=run_name+'.bpz'
    else: cat = bpz
                                                                                              
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
    bpzcols = []
    while bpzstr[i][:2] == '# ':
        line = bpzstr[i][2:]
        [col, key] = string.split(line)
        bpzcols.append(key)       
        i = i + 1

    bpzparams['FLUX_COMPARISON'] = run_name + '.flux_comparison'
    bpzparams['OUTPUT'] = run_name + '.bpz'
    bpzparams['INPUT'] = run_name + '.cat'
    bpzparams['PROBS_LITE'] = run_name + '.probs'
    print bpzparams

    print run_name, 'run_name'
    
    spectra = bpzparams.get('SPECTRA', 'CWWSB_fuv_f_f.list')
    columns = bpzparams.get('COLUMNS', run_name+'.columns')
    flux_comparison = bpzparams.get('FLUX_COMPARISON', run_name+'.flux_comparison')
    interp = str2num(bpzparams.get('INTERP', '2'))
    output = bpzparams.get('OUTPUT')
    
    output_f =get_2Darray(output) #Read the whole file
    all=get_2Darray(flux_comparison) #Read the whole file
    print len(all[:,0])
    ncols=len(all[0,:])
    nf=(ncols-5)/3
    
    ''' need to get the number of filters '''
    
    ''' need to retrieve the flux predicted, flux observed, and flux_error '''
    import scipy
    ft=scipy.array(all[:,5:5+nf])  # FLUX (from spectrum for that TYPE)
    fo=scipy.array(all[:,5+nf:5+2*nf])  # FLUX (OBSERVED)
    efo=scipy.array(all[:,5+2*nf:5+3*nf])  # FLUX_ERROR (OBSERVED)
  
    all_num = len(ft) 
    ''' only use predictions with good ODDS ''' 
    if 1: #good_odds:
        odds=scipy.array(output_f[:,5])

        redshift=scipy.array(output_f[:,1])
    if 1:
        mask = (odds == 1) * (redshift > 0.4)
        ft = ft[mask]
        fo = fo[mask]
        efo = efo[mask]


    odds_num = len(ft) 

        
    print odds
    
    #print ft/fo[0]
    #print flux_comparison
    #print columns
    
    ''' read in BPZ ODDS parameters and filter catalog '''
    
    print 'Reading filter information from %s' % columns
    filters=get_str(columns,0,nrows=nf,)
    print filters

    print filters, nf
    
    corrections = [] 
    
    for i in range((nf)):
        import scipy
        print filters[i]
        ''' get rid of zero flux objects in the training band '''
        mask1 = (fo[:,i]!=0) 
        ft_temp_1 = ft[mask1]
        fo_temp_1 = fo[mask1]
        efo_temp_1 = efo[mask1]

        if len(ft_temp_1):
            ''' get rid of poorly constrained objects in training band '''                                                        
            mask2 = (efo_temp_1[:,i]/fo_temp_1[:,i] < 0.2) 
            ft_temp = ft_temp_1#[mask2]
            fo_temp = fo_temp_1#[mask2]

            zero_num = len(ft) 
                                                                                                                                  
            print ft_temp[:100,i], fo_temp[:100,i]
            vec = (ft_temp/fo_temp)[:,i]
            #print vec
            #print ft[:,i], fo[:,i]
                                                                                                                                  
            #print ft_temp,fo_temp
            median = scipy.median(vec)
                                                                                                                                  
            print median
            title = filters[i] + ' all=' + str(all_num) + ' odds_num=' + str(odds_num) + ' zero_num=' + str(zero_num)
            #print median, filters[i]
            if 0:
                import pylab                                 
                o = pylab.hist((ft_temp/fo_temp)[:,i],bins=40,range=[0,3])
                print o
                pylab.suptitle(filters[i] + ' all=' + str(all_num) + ' odds_num=' + str(odds_num) + ' zero_num=' + str(zero_num))
                if  verbose:
                    pylab.show()
            #print (ft/fo)[:,0]
            corrections.append([median,filters[i],len(vec),vec,title])
            print filters[i]
    corrections.sort()
    correction_dict = {}
    plot_dict = {}
    title_dict = {}
    for c in corrections: 
        print c
        correction_dict[c[1]] = -2.5*math.log10(float(c[0]))
        plot_dict[c[1]] = c[3]
        title_dict[c[1]] = c[4]

    print correction_dict

    if not plot:
        return correction_dict
    else:
        return correction_dict, plot_dict, title_dict
    
if __name__ == '__main__':
    import sys
    cluster = sys.argv[1]
    magtype = sys.argv[2]
    calc_comp(cluster,magtype=magtype, verbose=True)



