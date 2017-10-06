
itr = 0

global itr
def assign_zp(filt,pars,zps):
    #print filt, zps
    if filt in zps:
        out = pars[zps[filt]]
    else: 
        out = 0
    return out

def get_locus(): 
    import pickle
    f = open('newlocus','r')
    m = pickle.Unpickler(f)
    locus = m.load()
    return locus


def all(): #filt,catalog,starcatalog,cluster,magtype,save_file=None):

    magtype='APER'
    import os

    ''' assign locus color to each instrument band '''
    mapping = {'u':'USDSS','g':'GSDSS','r':'RSDSS','i':'ISDSS','z':'ZSDSS','J':'JTMASS'}
    ''' first filter held constant '''
    combos = [['J','r','i'],['r','i','z'],['r','i','z'],['r','u','g']]
    zps_dict_all = {} #dict([mapping

    for combo in []: #combos:
        results = fit(combo, mapping, magtype)
        for key in combo[1:]:
            if zps_dict_all.has_key(combo[0]):
                zps_dict_all[key] = zps_dict_all[combo[0]] + results['full'][key]
            else:
                zps_dict_all[key] = results['full'][key]
        print zps_dict_all            
        raw_input()

    zps_dict_all = {'r': -24.033997449921568, 'z': -22.482056495878631, 'i': -23.6515342423546, 'g': -23.870150872353541, 'u': -21.791655326076722} 

    combo = ['J','u','g','r','i','z']

    fit(combo, mapping, magtype, startingzps=zps_dict_all)

def plot_simple(table,zplist,mapping,b1,b2,b3,b4):

    x = (table.field('MAG_' + magtype + '_' + b1) + zplist[mapping[b1]]) - (table.field('MAG_' + magtype + '_' + b2) + zplist[mapping[b2]])
    x_err = (table.field('MAGERR_' + magtype + '_' + b1)**2.-table.field('MAGERR_' + magtype + '_' + b2)**2.)**0.5

    y = (table.field('MAG_' + magtype + '_' + b3) + zplist[mapping[b3]]) - (table.field('MAG_' + magtype + '_' + b4) + zplist[mapping[b4]])
    y_err = (table.field('MAGERR_' + magtype + '_' + b3)**2.-table.field('MAGERR_' + magtype + '_' + b4)**2.)**0.5

    pylab.scatter(x,y)
    pylab.errobar(x,y,x_err,y_err)

    

        
def fit(combo, mapping, magtype, startingzps=None):

    filt_combo = [[mapping[c],c] for c in combo]
    good_fs = dict(filt_combo) 
    filt_combo = [[mapping[c],'yes'] for c in combo]
    l_fs = dict(filt_combo)
    filt_combo = [[mapping[c],[c]] for c in combo]
    locus_dict_obj = dict(filt_combo) 








    #good_fs = {'USDSS':'u','GSDSS':'g','RSDSS':'r','ISDSS':'i','ZSDSS':'z','JTMASS':'J'}
    #l_fs = {'USDSS':'yes','GSDSS':'yes','RSDSS':'yes','ISDSS':'yes','ZSDSS':'yes','JTMASS':'yes'}
    #locus_dict_obj = {'USDSS':['u'],'GSDSS':['g'],'RSDSS':['r'],'ISDSS':['i'],'ZSDSS':['z'],'JTMASS':['J']}

    #zp_dict = {'USDSS':0.,'GSDSS':0.,'RSDSS':0.,'ISDSS':0.,'ZSDSS':0.,'JTMASS':0.}

    #good_fs = {'JTMASS':'J','RSDSS':'r','ISDSS':'i',}
    #l_fs = {'JTMASS':'yes','RSDSS':'yes','ISDSS':'yes'}
    #locus_dict_obj = {'JTMASS':['J'],'RSDSS':['r'],'ISDSS':['i'],}

    import cutout_bpz, string
    locus_c = cutout_bpz.locus()

    print filter(lambda x:string.find(x.split('_')[0],'SDSS')!=-1 and string.find(x.split('_')[1],'SDSS')!=-1,locus_c.keys())
    print filter(lambda x:string.find(x,'MASS')!=-1 and string.find(x,'SDSS')!=-1 ,locus_c.keys())


    import re                                                    
    good_fs = []
    for k1 in locus_c.keys():
        res = re.split('_',k1)
        print l_fs
        print res
        if l_fs.has_key(res[0]) and l_fs.has_key(res[1]):
            good_fs.append([res[0],res[1]])

    print l_fs

    print locus_dict_obj, good_fs

    print good_fs

    zps_dict_obj = {} 

    list = ['MPUSUBARU','VJOHN','RJOHN'] #,'RJOHN','IJOHN','WSZSUBARU','WSISUBARU'] 

    print good_fs

    complist = []
    for f1A,f1B in good_fs:         
        if f1A != 'MPUSUBARU' and f1B != 'MPUSUBARU': # True: #filter(lambda x: x==f1A, list) and filter(lambda x: x==f1B, list): 
            zps_dict_obj[f1A] = 0                          
            zps_dict_obj[f1B] = 0
            import random
            for a in locus_dict_obj[f1A]:
                for b in locus_dict_obj[f1B]:
                    complist.append([[a,f1A],[b,f1B]])

    print complist
    print good_fs
    print zps_dict_obj

    print complist, 'complist'

    zps_list_full = combo #zps_dict_obj.keys()
    #if 'JTMASS' in zps_list_full:        
    #    zps_list_full = ['JTMASS'] + filter(lambda x: x!='JTMASS',zps_list_full)
        
    zps_list = zps_list_full[1:]
    zps ={} 
    zps_rev ={} 
    for i in range(len(zps_list)):
        zps[zps_list[i]] = i
        zps_rev[i] = zps_list[i] 

    import astropy.io.fits as pyfits
    p = pyfits.open('stars.fits')[1].data
   
    table = p                                                                            
    loci = len(locus_c['GSDSS_RSDSS'])

    print loci

    stars = len(table.field('MAG_' + magtype + '_' + complist[0][0][0]))

    locus_list = []
    for j in range(len(locus_c['GSDSS_RSDSS'])):
        o = []
        for c in complist:
            #print c, len(locus_c[c[0][1] + '_' +  c[1][1]]), j
            o.append(locus_c[c[0][1] + '_' +  c[1][1]][j])
        locus_list.append(o)

    import scipy

    results = {} 
    for iteration in ['full','bootstrap1','bootstrap2','bootstrap3','bootstrap4']:       

        ''' make matrix with a locus for each star '''                                                                                           
        locus_matrix = scipy.array(stars*[locus_list])
        print locus_matrix.shape

        ''' assemble matricies to make colors '''
        A_band = scipy.swapaxes(scipy.swapaxes(scipy.array(loci*[[table.field('MAG_' + magtype + '_' + a[0][0]) for a in complist]]),0,2),1,2)
        B_band = scipy.swapaxes(scipy.swapaxes(scipy.array(loci*[[table.field('MAG_' + magtype + '_' + a[1][0]) for a in complist]]),0,2),1,2)
        A_err = scipy.swapaxes(scipy.swapaxes(scipy.array(loci*[[table.field('MAGERR_' + magtype + '_' + a[0][0]) for a in complist]]),0,2),1,2)
        B_err = scipy.swapaxes(scipy.swapaxes(scipy.array(loci*[[table.field('MAGERR_' + magtype + '_' + a[1][0]) for a in complist]]),0,2),1,2)
                                                                                                                                                 
        print A_err.shape
        A_band[A_err > 1.] = -99
        B_band[B_err > 1.] = -99

        ''' make matrix specifying good values '''
        good = scipy.ones(A_band.shape)
        good[A_band == -99] = 0
        good[B_band == -99] = 0
        good = good[:,0,:]
        good_test = good.sum(axis=1) # sum all of the good measurements for any given star
        
        print sorted(good_test)
        print good_test
                                                                                                                                                 
        ''' figure out the cut-off '''
        cut_off = 2 #sorted(good_test)[-20] -1 
        print cut_off
        
                                                                                                                                                 
        A_band = A_band[good_test>cut_off]
        B_band = B_band[good_test>cut_off]
        A_err = A_err[good_test>cut_off]
        B_err = B_err[good_test>cut_off]

        A_err[A_err<0.05] = 0.05
        B_err[B_err<0.05] = 0.05


        locus_matrix = locus_matrix[good_test>cut_off]

        if string.find(iteration,'bootstrap') != -1:

            length = len(A_band)
            randvec = scipy.array([random.random() for ww in range(length)])
            fraction = 0.5
            mask = randvec < (fraction) 

            A_band = A_band[mask]             
            B_band = B_band[mask]
            A_err = A_err[mask]
            B_err = B_err[mask]
            locus_matrix = locus_matrix[mask]
        
        colors = A_band - B_band
        colors_err = (A_err**2. + B_err**2.)**0.5
                                                                                                                                                 
        colors_err[A_band == -99] = 1000000.   
        colors_err[B_band == -99] = 1000000.   
        colors_err[A_band == 99] = 1000000.   
        colors_err[B_band == 99] = 1000000.   
        colors[A_band == -99] = 0.   
        colors[B_band == -99] = 0.   
        colors[A_band == 99] = 0.   
        colors[B_band == 99] = 0.   
                                                                                                                                                 
        print colors.shape, locus_matrix.shape
                                                                                                                                                 
        from copy import copy
                                                                                                                                                 
        print good_test
                                                                                                                                                 
        #colors = colors[good_test > 1]
        #colors_err = colors_err[good_test > 1]
        #locus_matrix = locus_matrix[good_test > 1]
        stars_good = len(locus_matrix)
        good = scipy.ones(A_band.shape) 
        good[A_band == -99] = 0
        good[B_band == -99] = 0
        print good.sum(axis=2).sum(axis=1).sum(axis=0)
        #good = good[:,0,:]
        good_test = good[:,0,:].sum(axis=1)
        good = good[good_test > 1]
        star_mag_num = good[:,0,:].sum(axis=1)

        itr = 0

        
        def errfunc(pars,residuals=False):
            stat_tot = 0
            #for i in range(len(table.field('MAG_' + magtype + '-' + complist[0][0][0])[:100])):    
                #print i
                #print 'MAG_' + magtype + '-' + a                                 
                #print a,b                                           
                #print table.field('MAG_ISO-' + a)                    
                #print magtype, 'MAG_' + magtype + '-' + a
                                                                                                                                                 
            if 1:                
                A_zp = scipy.swapaxes(scipy.swapaxes(scipy.array(loci*[stars_good*[[assign_zp(a[0][1],pars,zps) for a in complist]]]),0,1),0,0)
                B_zp = scipy.swapaxes(scipy.swapaxes(scipy.array(loci*[stars_good*[[assign_zp(a[1][1],pars,zps) for a in complist]]]),0,1),0,0)
                colors_zp = A_zp- B_zp
                #print colors_zp.shape
                #print locus_matrix.shape
                #print colors.shape
                #print colors_zp[0][:][0]
                                                                                                                                                 
                #print colors[2][0], colors.shape
                #print locus_matrix[2][0], locus_matrix.shape
                print colors_zp.shape, colors.shape, locus_matrix.shape
                                                                                                                                                 
                ds_prelim = ((colors - locus_matrix - colors_zp)**2.)
                ds_prelim[good == 0] = 0.
                #print ds_prelim[2][0], 'ds_prelim'
                ds = (ds_prelim.sum(axis=2))**0.5
                #print ds[2][0]
                                                                                                                                                 
                ''' formula from High 2009 '''
                dotprod = abs((colors - locus_matrix - colors_zp) * colors_err)
                dotprod[good == 0] = 0. # set error to zero for poor measurements not in fit
                dotprod_sum = dotprod.sum(axis=2)
                                                                                                                                                 
                sum_diff = ds**2./dotprod_sum 
                #sum_diff = ds / colors_err
                #print sum_diff[2], 'sum_diff'
                #print c_diff[2][0], 'c_diff'
                dist = ds.min(axis=1)
                select_diff = sum_diff.min(axis=1)
                #print select_diff, 'select_diff'
                #select_diff_norm = select_diff #/star_mag_num         
                #print select_diff_norm, 'select_diff_norm'
                stat_tot = select_diff.sum()
                #print stat_tot, 'stat_tot'

            print pars, stat_tot#, zps
            print zps_list_full
            if residuals: return select_diff, dist
            else: return stat_tot
                                                                                                                                                 
        import pylab
        #pylab.ion()


        def plot(pars):

            A_zp = scipy.swapaxes(scipy.swapaxes(scipy.array(loci*[stars_good*[[assign_zp(a[0][1],pars,zps) for a in complist]]]),0,1),0,0)
            B_zp = scipy.swapaxes(scipy.swapaxes(scipy.array(loci*[stars_good*[[assign_zp(a[1][1],pars,zps) for a in complist]]]),0,1),0,0)
            colors_zp = A_zp- B_zp
            import pylab                                                           
            pylab.clf()
            for i in range(len(complist)):
                print complist[i], i


            x_color = scipy.array((colors - colors_zp)[:,0,2].tolist())
            y_color = (colors - colors_zp)[:,0,0]
            x_err = (colors_err)[:,0,2]
            y_err = (colors_err)[:,0,0]
                                                                                    
            x_color = x_color[x_err<100]
            y_color = y_color[x_err<100]
            y_err = y_err[x_err<100]
            x_err = x_err[x_err<100]
                                                                                    
            x_color = x_color[y_err<100]
            y_color = y_color[y_err<100]
            x_err = x_err[y_err<100]
            y_err = y_err[y_err<100]
                                                                                    
            print len(x_color), len(x_color) 
            #raw_input()
                                                                                    
                                                                                    
            pylab.scatter(x_color,y_color)
            pylab.errorbar(x_color,y_color,xerr=x_err,yerr=y_err,fmt=None)
            pylab.scatter(locus_matrix[0,:,2],locus_matrix[0,:,0],color='red')
                                                                                    
            pylab.show()

        ''' now rerun after cutting outliers '''        
        if True:
            
            if iteration == 'full':
                if startingzps is None:
                    pinit = scipy.zeros(len(zps_list))
                else:
                    pinit = [startingzps[key] for key in zps_list]
            else:
                import random
                ''' add random offset of 1.0 mag '''
                pinit = [results['full'][key] + random.random()*1.0 for key in zps_list]

            #plot(pinit)
            from scipy import optimize
            out = scipy.optimize.fmin(errfunc,pinit,maxiter=100000,args=()) 
            print out

            #plot(out)
                                                                                                                                                 
            import scipy                                                              
            print zps_list        
            print 'starting'        
            print out
            residuals,dist  = errfunc(pars=[0.] + out,residuals=True)


            print dist.shape, residuals.shape
            raw_input()
                                                                                                                                                 
            print dist 
            print 'finished'
            print 'colors' , len(colors)
                                                                                      
            ''' first filter on distance '''
            colors = colors[dist < 1]
            colors_err = colors_err[dist < 1]
            locus_matrix = locus_matrix[dist < 1]
            good = good[dist < 1]
            residuals = residuals[dist < 1]
                                                                                      
            ''' filter on residuals '''
            colors = colors[residuals < 6]
            colors_err = colors_err[residuals < 6]
            locus_matrix = locus_matrix[residuals < 6]
            good = good[residuals < 6]
                                                                                      
            stars_good = len(locus_matrix)
            star_mag_num = good[:,0,:].sum(axis=1)
                                                                                                                                                 
            print 'colors' , len(colors)

        pinit = out #scipy.zeros(len(zps_list))                         
        from scipy import optimize
        out = scipy.optimize.fmin(errfunc,pinit,args=()) 
        print out

        #plot(out)
        results[iteration] = dict(zip(zps_list_full,([0.] + out.tolist())))

                                                                  
                                                                  
    print results    

    errors = {}
                                                              
    import scipy
    print 'BOOTSTRAPPING ERRORS:'
    for key in zps_list_full:
        l = []
        for r in results.keys():
            if r != 'full':
                l.append(results[r][key])
        print key+':', scipy.std(l), 'mag'
        errors[key] = scipy.std(l)

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


    #pylab.show()


    


def temp():
    if 1:
        if 1:
            if 1: 
                if 1:
                    if 1:   
                        if 1:        


                #a = locus_dict_obj[f1A] 
                #b = locus_dict_obj[f1B]
                #c = locus_dict_obj[f2A]
                #d = locus_dict_obj[f2B]

                                print a,b,c,d                                                                                                                       
                                
                                
                                
                                
                                import string                                                                                                   
                                def fix(q): 
                                    if string.find(q,'MEGA') != -1:         
                                        import re                           
                                        res = re.split('-',q)               
                                        q = 'MEGAPRIME-0-1-' + res[-1]      
                                    print q                                 
                                    return q                                
                                                                                                                                                                
                                                                                                                                                                
                                #print catalog , starcatalog                            
                                #px = pickles.field(fix(a)) - pickles.field(fix(b))    
                                #py = pickles.field(fix(b)) - pickles.field(fix(c))    
                                #print px,py                                           
                                                                                       
                                import pylab                                           
                                                                                       
                                pylab.clf()                                            
                                                                                                                                                                    
                                
                                if 0: #a==b or ==f2B:                                
                                    print a,b,c,d
                                    print f1A,f1B,f2A,f2B
                                                                                       
                                                                                       
                                #pylab.savefig(outbase + '/RedshiftErrors.png')        
                                                                                       
                                                                                      
                                                                                      
                                table = p                                             
                                                                                      
                                print 'MAG_' + magtype + '-' + a                                 
                                print a,b,c                                           
                                #print table.field('MAG_ISO-' + a)                    
                                print magtype, 'MAG_' + magtype + '-' + a

                                at = table.field('MAG_' + magtype + '-' + a)[:]                
                                bt = table.field('MAG_' + magtype + '-' + b)[:]                
                                ct = table.field('MAG_' + magtype + '-' + c)[:]                
                                dt = table.field('MAG_' + magtype + '-' + d)[:]                

                                bt = bt[at!=-99]                                      
                                ct = ct[at!=-99]                                      
                                dt = dt[at!=-99]                                      
                                at = at[at!=-99]                                      
                                                                                      
                                at = at[bt!=-99]                                      
                                ct = ct[bt!=-99]                                      
                                dt = dt[bt!=-99]                                      
                                bt = bt[bt!=-99]                                      
                                                                                      
                                at = at[ct!=-99]                                      
                                bt = bt[ct!=-99]                                      
                                dt = dt[ct!=-99]                                      
                                ct = ct[ct!=-99]                                      
                                                                                                                                                                    
                                at = at[dt!=-99]                                      
                                bt = bt[dt!=-99]                                      
                                ct = ct[dt!=-99]                                      
                                dt = dt[dt!=-99]                                      
                                                                                      
                                if len(at) and len(bt) and len(ct) and len(dt) and len(locus_c[f1A + '_' + f1B])==len(locus_c[f2A + '_' + f2B]):                   
                                    x = at - bt                                       
                                    y = ct -dt                                        
                                                                                      
                                    x = x[:]                                      
                                    y = y[:]                                      


                                
                                                                                      
                                    print x[0:100], y[0:100]                                        


                                    pylab.clf()
                                    
                                    pylab.xlabel(a + ' - ' + b)                            
                                    pylab.ylabel(c + ' - ' + d)                            

                                    pylab.scatter(x,y,s=1)                            
                                                                                      
                                    pylab.scatter(locus_c[f1A + '_' + f1B],locus_c[f2A + '_' + f2B],color='red',s=1.)                  
                                    print len(x), 'x'
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                      
                                    #pylab.axis([sorted(x)[5],sorted(x)[-5],sorted(y)[5
                                    file = a+ b+ c+ d + '.png'    
                                    print 
                                    pylab.savefig(base + file)                        
                                    #pylab.show()
                                    pylab.clf()                                       
                                                                                      
                                    f.write('<img src=' + file + '>\n')               
                                plot = False                                          
                                print len(at), len(bt), len(ct), len(dt), len(locus_c[f1A + '_' + f1B])==len(locus_c[f2A + '_' + f2B]), f1A, f2A, f1B, f2B

def run(cluster):

    ratio = []
    import astropy.io.fits as pyfits, cutout_bpz
    import os
    import os, sys, bashreader, commands
    from utilities import *
    from config_bonn import appendix, tag, arc, filters, filter_root, appendix_root

    type='all'
    magtype = 'APER'
    if len(sys.argv) > 2:
        for s in sys.argv:
            if s == 'spec':
                type = 'spec' 
            elif s == 'rand': 
                type = 'rand'
            elif s == 'all': 
                type = 'all'
            elif s == 'picks': 
                type = 'picks'
            elif s == 'ISO': 
                magtype = 'ISO'
            elif s == 'APER': 
                magtype = 'APER'

    print cluster
    
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%s/' % cluster
    
    
    filecommand = open('record.analysis','w')
    
    BASE="coadd"
    image = BASE + '.fits'

    from glob import glob
    
    images = []
    filters.reverse()
    print filters
    ims = {}
    ims_seg = {}

    params = {'path':path, 
              'filter_root': filter_root, 
              'cluster':cluster, 
              'appendix':appendix, }


    catalog = '%(path)s/PHOTOMETRY/%(cluster)s.slr.cat' %params           
    starcatalog = '%(path)s/PHOTOMETRY/%(cluster)s.stars.calibrated.cat' %params           
    save_file = '%(path)s/PHOTOMETRY/pat_slr.calib' %params           
    import do_multiple_photoz, os
    reload(do_multiple_photoz)
    filterlist = do_multiple_photoz.get_filters(catalog,'OBJECTS')
    print filterlist

    filters = cutout_bpz.conv_filt(filterlist)
    y = {} 
    for f in filters: 
        y[f] = 'yes'
    filters = y.keys()
    filters.sort(cutout_bpz.sort_filters)

    print filters

    os.system('mkdir -p ' + os.environ['sne'] + '/photoz/' + cluster)           
    mkcolorcolor(filterlist,catalog,starcatalog,cluster,magtype,save_file)

if __name__ == '__main__':
    import sys
    cluster = sys.argv[1]

    run(cluster)
