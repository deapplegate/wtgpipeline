##! /usr/bin/env python

def fit_mass(z,shear,shearerr,cluster_z,w):
    import shear_ratio

    fitfunc = lambda p, x: p[0]*advanced_calc.dist_ratio(x,cluster_z,w)
    errfunc = lambda p, x, y, err: (y - fitfunc(p, x)) / err
    pinit = [1.]
    print z,shear,shearerr
    out = scipy.optimize.leastsq(errfunc, pinit, args=(scipy.array(z), scipy.array(shear), scipy.array(shearerr)), full_output=1)

    print out

    return out



def fit_exp(o_xdata,o_ydata,o_yerr):    

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
    for z in range(15): 

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
            print pfinal
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

if len(sys.argv) != 5:
    sys.stderr.write("wrong number of arguments!\n")
    sys.exit(1)

'python fit_PAT2.py MACS0018+16 0.5 "5000,5000" 0.2'

cluster = sys.argv[1]

import calc_test_save
filts, lensexts = reload(calc_test_save).get_lensing_filts(os.environ['subdir'],cluster,True)

filt = filts[0]
lensext = lensexts[0]

catdir = os.environ['subdir'] + '/' + cluster + '/LENSING_' + filt + '_' + filt + '_aper/' + lensext + '/' #+ cluster + '_fbg.cat'
catfile = catdir + 'cut_lensing.cat_step'

photdir = os.environ['subdir'] + '/' + cluster + '/PHOTOMETRY_' + filt + '_aper/' #+ cluster + '_fbg.cat'
photcat = photdir + cluster + '.APER1.1.CWWSB_capak.list.all.bpz.tab' 

print catfile, photcat

photldac = ldac.openObjectFile(photcat,'STDTAB')
lens = ldac.openObjectFile(catfile,'OBJECTS')

phot = photldac.matchById(lens)

print phot['SeqNr'], lens['SeqNr']

#matchedCat.saveas(os.environ['bonn'] + 'test.cat')

#command1 = 'ldacaddtab -i %(inputcat) -o /tmp/tmp1000.cat -p 


cluster_z=float(sys.argv[2])
center=  map(float,sys.argv[3].split(','))
pixscale=float(sys.argv[4]) # arcsec / pix

#catalog= ldac.openObjectFile(catfile)

r, E, B , phi = sp.calcTangentialShear(lens, center, pixscale)

beta=sp.beta(phot["BPZ_Z_B"],cluster_z) #, calcAverage = False)

import scipy
kappacut = scipy.array([False]*len(beta),dtype=bool) #sp.calcWLViolationCut(r, beta, sigma_v = 1300)


for i in range(len(r)):
    if 0 < r[i] < 1000:
        kappacut[i] = True 

print kappacut

#kappacut = sp.calcWLViolationCut(r, beta, sigma_v = 1300)

r = r[kappacut]
E = E[kappacut]

Eerr = (lens['sigma_gscorr'][kappacut])
beta = beta[kappacut]
Zs = phot['BPZ_Z_B'][kappacut]

import pylab, scipy
shears = {}
radii = {}
zs_rec = {}
shears_err = {}
ran = [[0.1,0.3],[0.3,0.5],[0.65,0.8],[0.8,0.95],[0.95,1.1],[1.1,1.3],[1.3,1.5]] #,[0.8,1.2],[1.2,1.8],[1.8,3.0]]

ran = [[0.1,0.3],[0.3,0.5],[0.65,0.8],[0.8,1.2],[1.3,3.]]#,[2,4]] #,[0.8,1.2],[1.2,1.8],[1.8,3.0]]

ran = [[0.1,0.3],[0.3,0.5],[0.6,1.3],[1.3,4]] #,[0.8,1.2],[1.2,1.8],[1.8,3.0]]

#ran = [[0,4]] #,[0.8,1.2],[1.2,1.8],[1.8,3.0]]
for i in range(len(ran)):
    shears[i] = []    
    shears_err[i] = []    
    radii[i] = []
    zs_rec[i] = []
for i in range(len(r)):
    for key in shears.keys():        
        if ran[key][0] < Zs[i] < ran[key][1]: 

        #if 1: #0  < Zs[i] < 0.4 or 1.5 < Zs[i] < 4: 
            shears[key].append(E[i])
            shears_err[key].append(Eerr[i])
            radii[key].append(r[i])
            zs_rec[key].append(Zs[i])

print shears.keys()
print shears[3]

mean = []
std = []
shearratio = []
zs = []
amps = []
ampErrs =[]

for i in range(len(ran)):
    print len(scipy.array(shears[i])), ran[i]
    #raw_input()
    mean.append(scipy.mean(scipy.array(shears[i])))
    std.append(scipy.std(scipy.array(shears[i])))
    #print shears[i], radii[i]
    if len(shears[i]) > 0:
        zs.append(scipy.mean(scipy.array(zs_rec[i])))
        amp, ampErr = fit_exp(scipy.array(radii[i]),scipy.array(shears[i]),scipy.array(shears_err[i])) 
        print amp, ampErr
        amps.append(amp)
        ampErrs.append(ampErr)
        print i

print amps, ampErrs , zs 
print mean 

raw_input()

max = 1.*scipy.array(amps)[0]

#cluster_z = 0.55

zs = scipy.array(zs)
amps_t = scipy.array(amps)[zs>0]/max
ampErrs_t = scipy.array(ampErrs)[zs>0]/max
zs_f = zs[zs>0]

calc_z = zs_f[0]

print amps_t, ampErrs_t

amps_f = [] 
ampErrs_f = []

import advanced_calc
d_cluster = advanced_calc.compute(cluster_z,-1.)
base = (advanced_calc.compute(calc_z,-1.) - d_cluster)/advanced_calc.compute(calc_z,-1.)

#for i in range(len(amps_t)):
i = 0
corr = (advanced_calc.compute(zs_f[i],-1.) - d_cluster)/advanced_calc.compute(zs_f[i],-1.)/base
amps_f.append(amps_t[i]/corr)
ampErrs_f.append(ampErrs_t[i]/corr)
i = 1
corr = (advanced_calc.compute(zs_f[i],-1.) - d_cluster)/advanced_calc.compute(zs_f[i],-1.)/base
ampErrs_f.append(((ampErrs_t[0]*corr)**2. + (ampErrs_t[i])**2.)**0.5/amps[i] )
amps_f.append(amps_t[i]/corr)



if False:
    amps_f = scipy.concatenate((amps_f,[0.9]))
    ampErrs_f = scipy.concatenate((ampErrs_f,[0.1]))
    zs_f = scipy.concatenate((zs_f,[3.]))

print amps_f, ampErrs_f, zs_f

print len(zs_f)
import shear_ratio, advanced_calc
for w,color in []: #[[-1.,'orange'],[-0.5,'red'],[-1.5,'blue'],[0,'black']]:
    p = fit_mass(zs_f[:],scipy.array(amps_f)[:],scipy.array(ampErrs_f)[:],cluster_z,w)
    d_cluster = advanced_calc.compute(cluster_z,w)
                                                           
    import scipy
    ratios = []
    zsrat = []
    for z in scipy.arange(cluster_z,3,0.2):
      zsrat.append(z)
      ratios.append(p[0] * (advanced_calc.compute(z,w) - d_cluster)/advanced_calc.compute(z,w))
    
    print p[0]
    print ratios, zsrat
                                                           
    pylab.plot(scipy.array(zsrat), scipy.array(ratios), color=color,label=str(w))
pylab.legend()    


#pylab.scatter(arange(0,1.6,0.2),scipy.array(mean))
print zs_f, amps_f, ampErrs_f
pylab.errorbar(scipy.array(zs_f),scipy.array(amps_f),scipy.array(ampErrs_f), fmt='k.')
pylab.xlabel('z')
pylab.ylabel('shear')
pylab.ylim(-0.5,1.5)
pylab.xlim(0,3)


for w in [-1.]: #.5,-1,-0.5,]:                                   
    
  d_cluster = advanced_calc.compute(cluster_z,w)
  refer = (advanced_calc.compute(calc_z,w) - d_cluster)/advanced_calc.compute(calc_z,w)    
                                                                                                                             
  import scipy                                             
  ratios_save = []
  zs = []
  for z in scipy.arange(cluster_z,3.,0.1):
    zs.append(z)
    s = advanced_calc.compute(z,w) 
    #ratio = (d_cluster_high/(1+cluster_z_high))/(d_cluster_low/(1+cluster_z_low))*(s - d_cluster_high)/(s - d_cluster_low)
    #print ratio, s, d_cluster, z
    #ratios.append(ratio)
    ratios_save.append((advanced_calc.compute(z,w) - d_cluster)/advanced_calc.compute(z,w)/refer)
                                                                                                                             
for w in [-1.5,-1,-0.5]:                                   
    
  d_cluster = advanced_calc.compute(cluster_z,w)
  refer = (advanced_calc.compute(calc_z,w) - d_cluster)/advanced_calc.compute(calc_z,w)    
                                                                                                                            
  import scipy                                             
  ratios = []
  zs = []
  i = 0
  for z in scipy.arange(cluster_z,3.,0.1):
    zs.append(z)
    s = advanced_calc.compute(z,w) 
    #ratio = (d_cluster_high/(1+cluster_z_high))/(d_cluster_low/(1+cluster_z_low))*(s - d_cluster_high)/(s - d_cluster_low)
    #print ratio, s, d_cluster, z
    #ratios.append(ratio)
    ratios.append((advanced_calc.compute(z,w) - d_cluster)/advanced_calc.compute(z,w)/refer/ratios_save[i])
    i += 1
                                                                                                                             
                                                           
  pylab.plot(scipy.array(zs), scipy.array(ratios))















pylab.savefig(cluster + 'shearratio.pdf')
pylab.show()

pylab.errorbar(scipy.array(zs_f),scipy.array(amps_t),scipy.array(ampErrs_t), fmt='k.')
pylab.xlabel('z')
pylab.ylabel('shear')
pylab.ylim(-0.5,2.*sorted(amps_t)[-1])
pylab.xlim(0,3)
pylab.savefig(cluster + 'shearratioval.pdf')
pylab.show()

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


