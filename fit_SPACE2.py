##! /usr/bin/env python



def fit_mass(zs,shear,shearerr,cluster_z,w,WM,WV,dict_DCMR):
    import shear_ratio

    import scipy
    print zs, shear

    dist_vec = []
    for z in zs: 
      print w, str(float(w)), '%.2f' % z + '_' + '%.2f' % w + '_' + '%.2f' % WM

      d_cluster = dict_DCMR['%.2f' % cluster_z + '_' + '%.2f' % w + '_' + '%.2f' % WM] #advanced_calc.compute(clusterz,w)
      DS = dict_DCMR['%.2f' % z + '_' + '%.2f' % w + '_' + '%.2f' % WM]
      #print d_cluster, DS
      dist_vec.append(( DS - d_cluster)/DS )

    dist_vec = scipy.array(dist_vec)

    fitfunc = lambda p, x: p[0]*dist_vec
    errfunc = lambda p, x, y, err: scipy.sum((y - fitfunc(p, x)) / err)
    pinit = [1.]
    print z,shear,shearerr
    out = scipy.optimize.leastsq(errfunc, pinit, args=(scipy.array(z), scipy.array(shear), scipy.array(shearerr)), full_output=1)

    chi = abs(out[0] * dist_vec - shear)/shearerr

    print dist_vec, out
    if False:
      pylab.clf()                    
      pylab.plot(zs,out[0]*dist_vec)
      pylab.scatter(zs, shear)
      pylab.show()
    

    chisq = scipy.sum(chi**2.)

    p = len(shear)
    redchi = chisq / (p - 2)
    
    print chi, chisq
    

    print out

    return out, redchi, chisq



def fit_exp(o_xdata,o_ydata,o_yerr,o_weight):    

    import scipy, pylab

    a = scipy.array(o_ydata) 
    a, b, varp = pylab.hist(a,bins=scipy.arange(-2,2,0.05))
    pylab.xlabel("shear")
    pylab.ylabel("Number of Galaxies")
    #pylab.show()

    o_xdata = scipy.array(o_xdata)
    o_ydata = scipy.array(o_ydata)
    o_yerr = scipy.array(o_yerr)
    print o_yerr

    #o_xdata = o_xdata[abs(o_ydata) > 0.05]
    #o_yerr = o_yerr[abs(o_ydata) > 0.05]
    #o_ydata = o_ydata[abs(o_ydata) > 0.05]

    both = 0 
    As = []
    for z in range(100): 

        xdata = []
        ydata = []
        yerr = []
        for i in range(len(o_xdata)):
            rand = int(random.random()*len(o_xdata)) - 1
            #print rand, len(o_xdata)
            xdata.append(o_xdata[rand])
            ydata.append(o_ydata[rand]) 
            yerr.append(o_yerr[rand])
        xdata = scipy.array(xdata)
        ydata = scipy.array(ydata)
                
        ##########                                                                                                                        
        # Fitting the data -- Least Squares Method
        ##########
        
        # Power-law fitting is best done by first converting
        # to a linear equation and then fitting to a straight line.
        #
        #  y = a * x^b
        #  log(y) = log(a) + b*log(x)
        #
                                                                                                                                          
        powerlaw = lambda x, amp, index: amp * (x**index)
                                                                                                                                          
        #print xdata
        #print ydata 
                                                                                                                                          
        ydata = ydata / (scipy.ones(len(ydata)) + abs(ydata))
        
        # define our (line) fitting function
        #fitfunc = lambda p, x: p[0]*x**p[1] 
                                                                                                                                          
        if both: 
            fitfunc = lambda p, x: p[0]*x**p[1] 
            errfunc = lambda p, x, y, err: (y - fitfunc(p, x)) / err
            pinit = [1.,-1.]
        else:
            fitfunc = lambda p, x: p[0]*x**-1.
            errfunc = lambda p, x, y, err: (y - fitfunc(p, x)) / err
            pinit = [1.] #, -1.0]
                                                                                                                                          
        #ydataerr = scipy.ones(len(ydata))  * 0.3
                                                                                                                                          
        out = scipy.optimize.leastsq(errfunc, pinit, args=(scipy.array(xdata), scipy.array(ydata), scipy.array(yerr)), full_output=1)
                                                                                                                                          
        if both:
            pfinal = out[0]          
            covar = out[1]
            print pfinal
            print covar
            
            index = pfinal[1]
            amp = pfinal[0]
            ampErr = covar[0][0]
            indexErr = covar[1][1]
                                                                                                                                          
        else: 
            pfinal = out[0]          
            covar = out[1]
            #print pfinal
            print covar
            
            index = -1. #pfinal[1]
            amp = pfinal #[0]
            ampErr = covar[0][0]**0.5
            indexErr = 0 #covar
        
        #indexErr = scipy.sqrt( covar[0][0] )
        #ampErr = scipy.sqrt( covar[1][1] ) * amp
        
        ##########
        # Plotting data
        ##########
        if False:                                                                                                                                  
          import pylab                                                      
          pylab.clf()
          #pylab.subplot(2, 1, 1)
          pylab.errorbar(xdata, ydata, yerr=yerr, fmt='k.')  # Data
          from copy import copy
          xdataline = copy(xdata)
          xdataline.sort()
          pylab.plot(xdataline, powerlaw(xdataline, amp, index))     # Fit
          pylab.text(5, 6.5, 'Ampli = %5.2f +/- %5.2f' % (amp, ampErr))
          pylab.text(5, 5.5, 'Index = %5.2f +/- %5.2f' % (index, indexErr))
          pylab.title('Best Fit Power Law')
          pylab.xlabel('X')
          pylab.ylabel('Y')
          
          #pylab.subplot(2, 1, 2)
          #pylab.loglog(xdataline, powerlaw(xdataline, amp, index))
          #pylab.errorbar(xdata, ydata, yerr=ydataerr, fmt='k.')  # Data
          #pylab.xlabel('X (log scale)')
          #pylab.ylabel('Y (log scale)')
          #pylab.xlim(1.0, 11)
                                                                                                                                          
        print z 
        if both:
            pylab.show() 
                                                                                                                                          
                                                                                                                                          
        #pylab.show() 
                                                                                                                                          
        pylab.clf()

        As.append(amp)            

    As = scipy.array(As)

    return As.mean(), As.std()

    #savefig('power_law_fit.png')


import ldac
from numpy import *
import shearprofile as sp
import sys
import os

#os.system('do_lensing_pat.sh ' + cluster + ' W-J-V ' + 

list = [['MACS1347-11',0.451]] #['MACS0911+17',0.505]] #,['MACS2214-13',0.502]] #['MACS1149+22',0.544]] #['MACS1347-11',0.451]] #,['A383',0.188]] #['MACS1149+22',0.544],['MACS0018+16',0.547],['MACS0717+37',0.545],['MACS0911+17',0.505],['MACS2214-13',0.502]]

list = [['MACS1423+24',0.543],['MACS1347-11',0.451],['MACS0025-12',0.584],['MACS1720+35',0.387],['MACS1347-11',0.451],['MACS0911+17',0.505],['MACS2214-13',0.502],['MACS0717+37',0.545],['MACS1149+22',0.544]]


list = [['MACS1423+24',0.543],['MACS1347-11',0.451],['MACS1720+35',0.387],['MACS1347-11',0.451],['MACS2214-13',0.502],['MACS1149+22',0.544]]
#list = [['MACS0717+37',0.545],['MACS1720+35',0.387],['MACS1347-11',0.451]]

#list = [['A383',0.188],['MACS1149+22',0.544],['MACS0018+16',0.547]]

list = [['MACS0911+17',0.505,'W-J-V'],['MACS0744+39',0.6977,'W-C-RC'],['MACS1347-11',0.451,'W-C-RC'],['MACS0025-12',0.584,'W-J-V'],['MACS1108+09',0.4663,'W-J-V'],['MACS0257-23',0.505,'W-J-V'],['MACS2214-13',0.502,'W-C-RC'],['MACS0329-02',0.4502,'W-J-V'],['MACS2214-13',0.502,'W-C-RC']]

#list = [['MACS1108+09',0.4663,'W-J-V']] #['MACS0257-23',0.505,'W-J-V'],['MACS2214-13',0.502,'W-C-RC']]


#list = [['MACS0329-02',0.4502,'W-J-V'],['MACS2214-13',0.502,'W-C-RC']]

#list = [['MACS0025-12',0.584,'W-J-V']]#['MACS0257-23',0.505,'W-J-V'],['MACS2214-13',0.502,'W-C-RC']]

fit_val = {}
import pickle
clusters = {}

import pickle
f = open('DA.pickle','r')
m = pickle.Unpickler(f)
dict_DCMR = m.load()




for cluster,clusterz,filter in list:
    if 1: #try:
        #if len(sys.argv) != 5:                                                                                             
        #    sys.stderr.write("wrong number of arguments!\n")
        #    sys.exit(1)
        
        'python fit_PAT2.py MACS0018+16 0.5 "5000,5000" 0.2'

        
        #cluster = sys.argv[1]
        catfile= os.environ['subdir'] + '/' + cluster + '/LENSING/' + cluster + '_fbg.cat'

        catfile= os.environ['subdir'] + '/' + cluster + '/LENSING_' + filter + '_' + filter + '_aper/good/' + cluster + '_weighted_photz.cat'
        print catfile
        #catfile= os.environ['subdir'] + '/' + cluster + '/ACS/merged_photz.cat'
        center=  map(float,"5000,5000".split(','))
        pixscale=float(0.2) # arcsec / pix


        import pyfits, scipy, pylab
        pylab.clf()
        p = pyfits.open(catfile)
        a = scipy.array(p['OBJECTS'].data.field('BPZ_ODDS')) 
        a, b, varp = pylab.hist(a,bins=scipy.arange(0,1,0.05))
        pylab.xlabel("BPZ_ODDS")
        pylab.ylabel("Number of Galaxies")
        pylab.title(cluster)
        pylab.savefig(cluster + 'BPZODDS_new.png')


        command = 'ldacfilter -i ' + catfile + " -c '(BPZ_ODDS > 0.3);' -t OBJECTS -o " + catfile+'.tmp'
        os.system('rm ' + catfile + '.tmp')
        print command
        os.system(command)

        command = 'ldacfilter -i ' + catfile + " -c '(e1_acs > 0.0);' -t OBJECTS -o " + catfile+'.tmp'
        #os.system('rm ' + catfile + '.tmp')
        print command
        #os.system(command)
       
        print catfile 
        catalog= ldac.openObjectFile(catfile+'.tmp',table='OBJECTS')
        
        r, E, B = sp.calcTangentialShear(catalog, center, pixscale) #,g1col='e1_acs',g2col='e2_acs')
        beta=sp.beta(catalog["Z_BEST"],clusterz)
        import scipy
        kappacut = scipy.array([False]*len(beta),dtype=bool) #sp.calcWLViolationCut(r, beta, sigma_v = 1300)
        
        for i in range(len(r)):
            if 100 < r[i] :
                kappacut[i] = True 
        
        #print kappacut
        
        kappacut = sp.calcWLViolationCut(r, beta, sigma_v = 1300)
        
        r = r[kappacut]
        E = E[kappacut]
        
        Eerr = scipy.ones(len(r))/10. #sqrt(catalog['sigma2_gs'][kappacut])
        beta = beta[kappacut]
        Zs = catalog['Z_BEST'][kappacut]
        
        import pylab, scipy
        shears = {}
        radii = {}
        zs_rec = {}
        shears_err = {}
        ran = [[0.1,0.3],[0.3,0.5],[0.65,0.8],[0.8,0.95],[0.95,1.1],[1.1,1.3],[1.3,1.5]] #,[0.8,1.2],[1.2,1.8],[1.8,3.0]]
        
        ran = [[0.1,0.3],[0.45,0.55],[0.55,0.65],[0.65,0.8],[0.8,0.95],[0.95,1.1]]#,[1,2.]]#,[2,4]] #,[0.8,1.2],[1.2,1.8],[1.8,3.0]]
        
        #ran = [[0.1,0.3],[0.3,0.5],[0.65,1.],[1.,4]] #,[0.8,1.2],[1.2,1.8],[1.8,3.0]]
        ran = [[0.5,0.65],[0.65,0.9],[0.9,1.8],[1.8,3.0]]

        ran = [[clusterz+0.1,clusterz+0.25],[clusterz+0.25,clusterz+0.4],[clusterz+0.4,clusterz+0.55],[clusterz+0.55,clusterz+0.7]]                

        ran = [[0.1,0.3],[0.3,0.5],[0.5,0.6],[0.6,0.7],[0.7,0.8],[0.8,0.9],[0.9,1.1],[1.1,1.3]] #,[1.3,1.5],[1.5,2.0]] #,[1.3,1.5]] 

        #,[0.95,1.1]]#,[1,2.]]#,[2,4]] #,[0.8,1.2],[1.2,1.8],[1.8,3.0]]
        
        #ran = [[0.6,1.1],[1.1,1.8],[1.8,3.0]]
        for i in range(len(ran)):
            shears[i] = []    
            shears_err[i] = []    
            radii[i] = []
            zs_rec[i] = []
        add = 0
        for i in range(len(r)):
            for key in shears.keys():        
                #if Zs[i] > clusterz + 0.05 and ran[key][0] < Zs[i] < ran[key][1]: 

                if ran[key][0] < Zs[i] < ran[key][1]: 
                #if 1: #0  < Zs[i] < 0.4 or 1.5 < Zs[i] < 4: 
                    add += 1
                    shears[key].append(E[i])
                    shears_err[key].append(Eerr[i])
                    radii[key].append(r[i])
                    zs_rec[key].append(Zs[i])
        print add
        
        print shears.keys()
        #print shears[3]
        
        mean = []
        std = []
        shearratio = []
        zs = []
        amps = []
        ampErrs =[]
        
        ''' find the shear in each bin and append to array '''
        for i in range(len(ran)):
            print len(scipy.array(shears[i])), ran[i]
            #raw_input()
            mean.append(scipy.mean(scipy.array(shears[i])))
            std.append(scipy.std(scipy.array(shears[i])))
            #print shears[i], radii[i]
            if len(shears[i]) > 0:
                weights = []
                zs.append(scipy.mean(scipy.array(zs_rec[i])))
                amp, ampErr = fit_exp(scipy.array(radii[i]),scipy.array(shears[i]),scipy.array(shears_err[i]),scipy.array(weights)) 
                print amp, ampErr
                amps.append(amp)
                ampErrs.append(ampErr)
                print i
        
        
        print amps, ampErrs , zs 
        print mean 
        
        ''' find the maximum shear '''
        max = 1.*sorted(scipy.array(amps))[-1]
        print max, scipy.array(amps)
        
        
        zs = scipy.array(zs)
        amps_f = scipy.array(amps)[zs>clusterz]#/max
        ampErrs_f = scipy.array(ampErrs)[zs>clusterz]#/max
        zs_f = zs[zs>clusterz]
        
        if False:
            amps_f = scipy.concatenate((amps_f,[0.9]))
            ampErrs_f = scipy.concatenate((ampErrs_f,[0.1]))
            zs_f = scipy.concatenate((zs_f,[3.]))
        
        print amps_f, ampErrs_f, zs_f
        
        print len(zs_f)
        import shear_ratio, advanced_calc
        
        ''' fit for each cosmology '''
        #for w,color in [[-1.,'orange'],[-0.5,'red'],[-1.5,'blue'],[0,'black']]:


        omega_m = 0.3
        omega_lambda = 0.7

        x = []
        y = []

        for w in scipy.arange(-2,2,0.1):
          p, redchi, chisq = fit_mass(zs_f[:],scipy.array(amps_f)[:],scipy.array(ampErrs_f)[:],clusterz,w,omega_m,omega_lambda,dict_DCMR)
          x.append(w)
          y.append(chisq)

        if not 'chi_all' in locals(): 
          chi_all = scipy.array(y)
          meas_all = len(zs_f)            
        else:
          chi_all += scipy.array(y)
          meas_all += len(zs_f)            
        print 'end'

        pylab.clf()
        pylab.scatter(x,y)

         
        bigfile = '/a/wain023/g.ki.ki05/anja/SUBARU/' + cluster + '/' + filter + '/SCIENCE/coadd_' + cluster + '_all/coadd.fits'            
        import commands
        seeing = commands.getoutput('gethead ' + bigfile + ' SEEING')
        print 'seeing', seeing 

        pylab.title(cluster) # + ' seeing ' + str(seeing) + ' redchi ' + str(redchi))
        pylab.savefig(cluster + 'chiratio.png')
        #pylab.show()

        
        pylab.clf()
        WM = 0.3         
        
        import scipy
        for w,color in [[-1,'black']]: #[-0.5,'black'],[-1,'blue'],[-1.5,'yellow']]: #scipy.arange(-10,10,2):
            print 'fitting'
            omega_m = 0.3
            omega_lambda = 0.7
            import scipy
            #for w in scipy.arange(-2,0,0.5):
            p, redchi, chisq = fit_mass(zs_f[:],scipy.array(amps_f)[:],scipy.array(ampErrs_f)[:],clusterz,w,omega_m,omega_lambda,dict_DCMR)
            #x.append(w)
            #y.append(redchi)
            print 'finished fitting'


            print redchi
        
            fit_val[str(w)] = redchi
        
            d_cluster = advanced_calc.compute(clusterz,w)
            import scipy
            ratios = []
            zsrat = []
            infinite = p[0] * (advanced_calc.compute(10000,w) - d_cluster)/advanced_calc.compute(10000,w)

            for z in scipy.arange(clusterz,2.4,0.02):
              zsrat.append(z)
              #ratios.append((p[0] * (advanced_calc.compute(z,w) - d_cluster)/advanced_calc.compute(z,w)) / infinite)
              DS = dict_DCMR['%.2f' % z + '_' + '%.2f' % w + '_' + '%.2f' % WM] #str(float('%.2f' % z)) + '_' + str(w) + '_' + str(WM)]
              ratios.append((p[0] * ( DS - d_cluster)/DS) / infinite)
            
            print p[0], w
            print ratios, zsrat

            
            f=open(cluster + 'curve.txt','w')
            for i in range(len(zsrat)):                                                                      
                f.write(str(zsrat[i]) + ' ' + str(ratios[i]) + '\n')
            f.close()



                                                                   
            pylab.plot(scipy.array(zsrat), scipy.array(ratios),color=color ) #,label=str(w))
        pylab.legend()    
        
        
        #pylab.scatter(arange(0,1.6,0.2),scipy.array(mean))
       
         
        ''' now plot measurements '''
        pylab.errorbar(scipy.array(zs),scipy.array(amps)/infinite,scipy.array(ampErrs)/infinite, fmt='k.', markersize=20)
        pylab.xlabel('z',fontsize=25)
        pylab.ylabel('$\gamma$(z)/$\gamma$($\infty$)',fontsize=25)
        #pylab.ylim(-0.5,1.5)
        pylab.xlim(0,2.5)
        pylab.ylim(-1,2.0)
        pylab.axhline(y=0,linestyle='--',c='black')


        pylab.title(cluster + ' seeing ' + str(seeing) + ' redchi ' + str(redchi))

        pylab.savefig(cluster + 'ACSratio.png')

        f=open(cluster + 'ratio.txt','w')
        for i in range(len(zs)):
            f.write(str(zs[i]) + ' ' + str(amps[i]/infinite) + ' ' + str(ampErrs[i]/infinite) + '\n')
        f.close()
        
        print cluster
        #pylab.show()
       
        if False: 
            sigma, sigmaerr, chisq, isCon = sp.runSIS_ML(r, E, Eerr, beta, stepcor = 1.082, guess=1) 
            filebase,ext=os.path.splitext(catfile)
            
            
            #output = open(filebase+"_profile.dat", 'w')
            #for i in xrange(len(r_as)):
            #    output.write("%f  %f  %f  %f  %f\n" % (r_as[i], E[i], Err[i], B[i], Berr[i]))
            #output.close()
            #
            
            
            
            #output = open(filebase+"_sisfit.ml.dat", 'w')
            print "sigma: %f  %f\n" % (sigma, sigmaerr)
            #output.write("sigma: %f  %f\n" % (sigma, sigmaerr))
            #output.close()
        
        print 'fit_val', fit_val
        from copy import copy
                                                                                                                            
        clusters[cluster] = copy(fit_val)

        store = open('store','w')
        pickle.dump(clusters,store)
        store.close()

import pylab
pylab.clf()  
pylab.scatter(scipy.arange(-2,2,0.1)  ,chi_all)
print chi_all
pylab.title('total measurements ' + str(meas_all))
pylab.xlabel('w')
pylab.ylabel('Chi^2')
pylab.savefig('allchi.pdf')
pylab.show()

#    except: print 'fail'

    
    
