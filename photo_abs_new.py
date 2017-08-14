#!/usr/bin/env python

# Python module for photometric calibration.
# It needs the Python modules ppgplot and
# mpfit to be installed.

# 03.03.2005 Fixed a serious bug in the rejection loop. Instead
#            of using the remaining points we always used all points
#            and rejected points until the original fit matched the data
# 15.02.2005 Fixed the range of the y-axes in the plots to more
#            sensible values
# 14.02.2005 Fixed a bug when more paramters were fitted than
#            data points were present
#            We now rescale points to the airmass/color at which
#            they are plotted (zero)
#            Check that label is set
# 10.12.2004 Now takes a new argument "label" to be
#            used as axis label in the color plot

import copy
import getopt
import string
import sys

import mpfit
import Numeric

from ppgplot   import *

import BonnLogger


def run_through(cluster,infile=None,output=None,extcoeff=None,sigmareject=None,step=None,bandcomp=None,color1which=None,color2which=None):

    return run_main(cluster,infile,output,extcoeff,sigmareject,step,bandcomp,color1which,color2which)
    
def run_main(cluster,infile,output,extcoeff,sigmareject,step,bandcomp,color1which,color2which,label=None):

    print infile
    data, airmass, color1, color2, magErr, X, Y, stdMag = readInput(infile)  

    print color1

    pdict = {'zp':0,'extcoeff':extcoeff,'color1':0,'color2':0}
 
    #write input quantities to dictionary 
    var_names = {'bandcomp':bandcomp, 'color1which':color1which , 'color2which':color2which, 'sigmareject':sigmareject, 'cluster':cluster, 'label':label}
 
    #define the fits you want to make
    #fits = [{'model':[{'name':'zp','term':['zp'],'value':pdict['zp']},{'name':'color1','term':['color1'],'value':pdict['color1']},{'name':'color2','term':['color2'],'value':pdict['color2']},{'name':'X','term':['X'],'value':0},{'name':'YTY','term':['Y','Y'],'value':0},{'name':'XTX','term':['X','X'],'value':0},{'name':'Y','term':['Y'],'value':0},{'name':'XTY','term':['X','Y'],'value':0}], \
    #            'fixed':[], \
    #            'apply' : ['zp','color1','color2','X','Y','XTY','XTX','YTY'], \
    #            'plots':[{'xaxis_var':'color1','term_names':['color1']}]},]
 
               # 'apply' : ['zp','color1','color2'],\
            #{'model':[{'name':'zp','term':['zp'],'value':pdict['zp']},{'name':'color1','term':['color1'],'value':pdict['color1']},{'name':'color2','term':['color2'],'value':pdict['color2']}], \
            #    'fixed':[], \
            #    'apply':[], \
            #    'plots':[{'xaxis_var':'color1','term_names':['color1']},{'xaxis_var':'color2','term_names':['color2']}]}, \
    fits = [{'model':[{'name':'zp','term':['zp'],'value':pdict['zp']},{'name':'color1','term':['color1'],'value':pdict['color1']}], \
                'fixed':[], \
                'apply': ['zp','color1'], \
                'plots':[{'xaxis_var':'color1','term_names':['color1','zp']}]}]
        #, \
        #{'model':[{'name':'zp','term':['zp'],'value':pdict['zp']},{'name':'color1','term':['color1'],'value':pdict['color1']},{'name':'color1sq','term':['color1','color1'],'value':pdict['color1']}], \
        #    'fixed':[], \
        #'plots':[{'xaxis_var':'color1','term_names':['color1']}]} \
        
    
    #fits = [{'model':[['zp'],['color1','color1']], \
    #        'fixed':[{'term':['airmass'],'value':pdict['extcoeff']}], \
 #      'plotpars':['color1','airmass'], \
 #           'parinfo':[{'value':pdict['zp'],'fixed':0},{'value':pdict['color1'],'fixed':0}],\
 #       }]
 
    #generate a class for the fit model
    for i in range(len(fits)):
        print fits[i]['apply']
        j = phot_funct(fits[i]['model'],fits[i]['fixed'],fits[i]['apply'])
        fits[i]['class'] = j
        print i
        print fits[i]

    print data, color1
    fits, data_good, airmass_good, color1_good, color2_good, magErr_good, X_good, Y_good, stdMag_good = photCalib(data, airmass, color1, color2, magErr, X, Y, stdMag, fits, sigmareject)
 
    #make a label for the fitting model                                             
    for i in range(len(fits)):
        jj = [] 
        for term in fits[i]['model']:   
            print term                                               
            jj.append(reduce(lambda x,y: x  + 'T' + y,term['term']))
        model =  reduce(lambda z,w: z + 'P' + w, jj)
        fits[i]['class'].fitvars['model_name'] = model
    jj = [] 
    for term in fits[i]['fixed']:   
        print term
        jj.append(reduce(lambda x,y: x  + 'T' + y,term['term']))
    if len(jj): 
        model =  reduce(lambda z,w: z + 'P' + w, jj)
    else: model = ''
    fits[i]['class'].fitvars['fixed_name'] = model
 
    corr_data = fits[0]['class'].apply_fit(data_good,airmass_good,color1_good,color2_good,magErr_good,X_good,Y_good)    
    corr_stdMag = fits[0]['class'].apply_fit(stdMag_good,airmass_good,color1_good,color2_good,magErr_good,X_good,Y_good)    
 
    saveResults('/tmp/tmp', fits, var_names, step)
    outfile = 'tmp'
    makePlotsNew(data, airmass, color1, color2, X, Y, outfile, fits, var_names)
    print data[0:20]
    print airmass[0:20]
    print color1[0:20]
    print color2[0:20]

    return {'fits':fits,'corr_data':corr_data,'airmass_good':airmass_good, 'color1_good':color1_good, 'color2_good': color2_good, 'magErr_good':magErr_good, 'X_good':X_good, 'Y_good':Y_good, 'corr_stdMag':corr_stdMag}


def calcDataIllum(file, LENGTH1, LENGTH2, bin,data, airmass, color1, color2, magErr, X, Y, rot=0):
    import numpy, math, pyfits, os                                                                              
    x = []
    y = []
    z = []
    zerr = []

    from copy import copy
    X_sort = copy(X)
    Y_sort = copy(Y)
    X_sort = numpy.sort(X_sort)
    Y_sort = numpy.sort(Y_sort)

    X_min = X_sort[0]
    Y_min = Y_sort[0]

    X_max = X_sort[-1]
    Y_max = Y_sort[-1]

    X_width = abs(X_max - X_min)
    Y_width = abs(Y_max - Y_min)

    nbin1 =10 
    nbin2 =10 

    LENGTH1 = LENGTH1
    LENGTH2 = LENGTH2

    print LENGTH1, LENGTH2
    bin1 = int(LENGTH1/nbin1)
    bin2 = int(LENGTH2/nbin2)
    diff_weightsum = -9999*numpy.ones([nbin1,nbin2])
    diff_invvar = -9999*numpy.ones([nbin1,nbin2])

    X_cen = []
    Y_cen = []
    data_cen = []
    zerr_cen = []

    chisq = 0
    for i in range(len(data)):
        if 1: # LENGTH1*0.3 < X[i] < LENGTH1*0.6:
            X_cen.append(X[i])
            Y_cen.append(Y[i])
            data_cen.append(data[i])
            zerr_cen.append(magErr[i])

        x.append(X[i])    
        y.append(Y[i])
        z.append(data[i])
        zerr.append(magErr[i])
        chisq += data[i]**2./magErr[i]**2.

        x_val = int((X[i])/float(bin1))  # + size_x/(2*bin)
        y_val = int((Y[i])/float(bin2))  #+ size_y/(2*bin)
        #print LENGTH1, LENGTH2, x_val, y_val, X[i], Y[i]
        #raw_input()
        #print size_x/bin+1,size_y/bin+1, x_val, y_val, X[i], Y[i]
        err = magErr[i]
        ''' lower limit on error '''
        if err < 0.04: err = 0.04
        weightsum = data[i]/err**2.
        invvar = 1/err**2.
        

        #if 1: #0 <= x_val and x_val < int(nbin1) and y_val >= 0 and y_val < int(nbin2):  #0 < x_val < size_x/bin and 0 < y_val < size_y/bin:
        #print x_val, y_val
        try:
            if diff_weightsum[x_val][y_val] == -9999:      
                diff_weightsum[x_val][y_val] = weightsum
                diff_invvar[x_val][y_val] = invvar 
            else:                 
                diff_weightsum[x_val][y_val] += weightsum 
                diff_invvar[x_val][y_val] += invvar 
        except: print 'fail'

    redchisq = chisq**0.5 / len(data)
    print 'redchisq', redchisq
    #raw_input()

    import Numeric
    x_p = Numeric.array(X_cen)
    y_p = Numeric.array(Y_cen)
    z_p = Numeric.array(data_cen)
    zerr_p = Numeric.array(zerr_cen)
    x.sort()
    y.sort()
    z.sort()



    mean = diff_weightsum/diff_invvar
    print 'mean'
    #print mean
    err = 1/diff_invvar**0.5

    print 'err'
    #print err 

    print 'writing'
    hdu = pyfits.PrimaryHDU(mean)
    pth = '/nfs/slac/g/ki/ki04/pkelly/plots/'
    f = pth + file 
    os.system('rm ' + f +   'diffmap.fits')
    hdu.writeto( f + 'diffmap.fits')      

    hdu = pyfits.PrimaryHDU(err)
    os.system('rm ' + f + 'diffinvar.fits')
    hdu.writeto( f + 'diffinvar.fits')      


    pgbeg(f + 'pos.ps'+"/cps",1,1)
    pgiden()

    #print x_p
    #print z_p 
    #print zerr_p

    #pgswin(x[0],x[-1],z[0],z[-1])

    ### plot positions
    pgpanl(1,1)
    pgswin(x[0],x[-1],y[0],y[-1])
    pgbox()
    pglab('X','Y',file)     # label the plot
    #pgsci(3)
    #pgerrb(6,x_p,z_p,zerr_p)
    pgpt(x_p,y_p,3)

    pgend()

    ### plot residuals
    pgbeg(f + 'diff.ps'+"/cps",1,2)
    pgiden()

    #print x_p
    #print z_p 
    #print zerr_p

    #pgswin(x[0],x[-1],z[0],z[-1])

    pgpanl(1,1)
    pgswin(x[0],x[-1],-0.5,0.5)
    pgbox()
    pglab('X axis','SDSS-SUBARU',file)     # label the plot
    #pgsci(3)
    #pgerrb(6,x_p,z_p,zerr_p)
    pgpt(x_p,z_p,3)

    #pgswin(y[0],y[-1],z[0],z[-1])
    pgpanl(1,2)
    pgswin(y[0],y[-1],-0.5,0.5)

    pgsci(1)
    pgbox()
    pglab('Y axis','SDSS-SUBARU',file)     # label the plot
    #pgsci(3)
    #pgerrb(6,y_p,z_p,zerr_p)
    pgpt(y_p,z_p,3)
    pgsci(1)
  


    #print x_p
    #print z_p 
    #print zerr_p

    pgend()

    return

def make_name(name): 
    if len(name) > 1:                               
        name = reduce(lambda x,y: x + 'T' + y,name)
    else: 
        name = name[0]
    return name

class phot_funct:
    def __init__(self, sinputmodel, sfixed, sapply=[]):
        self.sinputmodel = sinputmodel
        #generate objects to make functions and to input into fitting program     
        self.smodel = [x['term'] for x in self.sinputmodel]
        self.smodeldict = {}
        for x in self.sinputmodel:
            self.smodeldict[x['name']] = x['term']
        self.parinfo = [{'value':x['value'],'fixed':0} for x in self.sinputmodel]
        self.sfixed = sfixed    
        self.sapply = sapply
        self.fitvars = {}
    #   self.smodel = [['zp'],['color1'],['color2']]
    def prep_fit(self, data, airmass=None, color1=None, color2=None, y=None, X=None, Y=None):
        self.dict = {'zp':1., 'color1':color1, 'color2':color2, 'airmass':airmass, 'X':X, 'Y':Y}
        # remove dependence on fixed variables
        for i in range(len(self.sfixed)):    
            term = self.sfixed[i]['term']
            data -= self.sfixed[i]['value'] * reduce(lambda x,y: x * y,[self.dict[z] for z in term]) 
        return data 

        ''' after fit, apply some terms to the data vector '''
    def apply_fit(self, data, airmass=None, color1=None, color2=None, y=None, X=None, Y=None):
        self.dict = {'zp':1., 'color1':color1, 'color2':color2, 'airmass':airmass, 'X':X, 'Y':Y}
        # remove dependence on fixed variables
        #print self.fitvars.keys()
        for i in range(len(self.sapply)):    
            term_name = self.sapply[i]
            value = self.fitvars[term_name]
            term = self.smodeldict[term_name]
            #print term_name, value, term, self.fitvars[term_name], self.dict[term[0]]
            data -= self.fitvars[term_name] * reduce(lambda x,y: x * y,[self.dict[z] for z in term]) 
        return data 

    def calc_model(self, p, fjac=None, airmass=None, color1=None, color2=None, y=None, X=None, Y=None, err=None):
        # function you can pass to mpfit
        self.dict = {'zp':1., 'color1':color1, 'color2':color2, 'airmass':airmass, 'X':X, 'Y':Y}
        model = 0       
        for i in range(len(self.smodel)):    
            term = self.smodel[i]
            model += p[i] * reduce(lambda x,y: x * y,[self.dict[z] for z in term]) 
        status = 0
        return([status, (model-y)/err])

    def calc_sigma(self, p, airmass=None, color1=None, color2=None, y=None, err=None, X=None, Y=None):
        # function you can pass to mpfit
        self.dict = {'zp':1., 'color1':color1, 'color2':color2, 'airmass':airmass, 'X':X, 'Y':Y}
        model = 0       
        for i in range(len(self.smodel)):   
            term = self.smodel[i]
            #print term
            model += p[i] * reduce(lambda x,y: x * y,[self.dict[z] for z in term]) 
        status = 0
        return([model, (model-y)/err])

    def generate_plot_input(self, xaxis_var, term_names,Min,Max,airmass=None, color1=None, color2=None, data=None, X=None, Y=None, err=None,  ):
        self.dict = {'zp':1., 'color1':color1, 'color2':color2, 'airmass':airmass, 'X':X, 'Y':Y}
        params = (self.sinputmodel + self.sfixed)
        for ele in params:   
            if reduce(lambda x,y: x * y, [(ele['name'] != z) for z in term_names]):  
                term = ele['term']                                                             
                if self.fitvars.has_key(make_name(ele['term'])):
                    coeff = self.fitvars[make_name(ele['term'])] #fitted
                else: 
                    coeff = ele['value'] # not fitted
                data -= coeff * reduce(lambda x,y: x * y,[self.dict[z] for z in term]) 


        data_plot_x = self.dict[xaxis_var]    
        data_plot_y = data 
               
        from numpy import arange 

        model = 0       
        model_plot_x = []
        model_plot_y = []
        
        smerge = self.sinputmodel + self.sfixed
        model_plot = []

        for name in term_names: 
            ele = -999
            for sterm in smerge: 
                if name == sterm['name']:
                    ele= sterm 
                    if self.fitvars.has_key(make_name(ele['term'])):
                        coeff = self.fitvars[make_name(ele['term'])] #fitted
                    else: coeff = ele['value'] # not fitted
                                                                             
                    model_plot.append({'term':ele['term'],'value':coeff})

        for x_value in arange(Min,Max,0.05):
            y_value = 0       

            for i in range(len(model_plot)):                                           
                term = model_plot[i]['term']
                if term[0] == 'zp':
                    y_value += model_plot[i]['value']  # in this case there is no x dependence
                else:
                    y_value += model_plot[i]['value'] * reduce(lambda x,y: x * y,[x_value for z in term]) 
            
            model_plot_x.append(x_value) 
            model_plot_y.append(y_value) 
        return (Numeric.array(model_plot_x), Numeric.array(model_plot_y), data_plot_x, data_plot_y)

def readInput(file):
    f = open(file, "r")

    instMagList = []
    stdMagList = []
    magErrList = []
    colList1 = []
    colList2 = []
    airmassList = []
    X = [] 
    Y = []

    for line in f.readlines():
        instMag, stdMag, col1, col2, airmass, instMagErr, stdMagErr, chipX, chipY = string.split(line)
        #print instMag, stdMag, col1, col2, airmass, instMagErr, stdMagErr 
        magErr = (float(instMagErr)**2. + float(stdMagErr)**2.)**0.5
        if magErr < 0.1: magErr = 0.1
        magErrList.append(magErr)
        instMagList.append(float(instMag))
        stdMagList.append(float(stdMag))
        colList1.append(float(col1))
        colList2.append(float(col2))
        airmassList.append(float(airmass))
        X.append(float(chipX))
        Y.append(float(chipY))

    f.close()

    instMag = Numeric.array(instMagList)
    stdMag = Numeric.array(stdMagList)
    data = stdMag - instMag
    airmass = Numeric.array(airmassList)
    color1 = Numeric.array(colList1)
    color2 = Numeric.array(colList2)
    magErr = Numeric.array(magErrList)
    X = Numeric.array(X)
    Y = Numeric.array(Y)

    return data, airmass, color1, color2, magErr, X, Y, stdMag

def photCalib(data_save, airmass_save, color1_save, color2_save, err_save, X_save, Y_save, stdMag_save, fits, sigmareject, maxSigIter=50):
   
    save_len = len(data_save)

    #parinfos = [[{"value": p[0], "fixed": 0},{"value": p[1], "fixed": 0, "limited": [0,1], "limits": [-99, 0]},{"value": p[2], "fixed": 0}],[{"value": p[0], "fixed": 0},{"value": p[1], "fixed": 0}],[{"value": p[0], "fixed": 0}]]


    solutions = [] 
    for fit in fits:
        airmass = copy.copy(airmass_save)
        color1 = copy.copy(color1_save)
        color2 = copy.copy(color2_save)
        data_tmp = copy.copy(data_save)
        err = copy.copy(err_save)                                               
        X = copy.copy(X_save)
        Y = copy.copy(Y_save)
        stdMag = copy.copy(stdMag_save)
                                                                                
        #first apply coefficients we are holding fixed  
        data = copy.copy(data_tmp)
                                                                                
        # holding parameters fixed doesn't seem to work, so just substract them

        #print 'data', data[0:10]
        data = fit['class'].prep_fit(data,airmass,color1,color2,data_tmp)    
        #print 'data', data[0:10]
                                                                                
        data_rec = copy.copy(data)

        for i in range(maxSigIter):
            old_len = len(data)
            fa = {"airmass": airmass,"color1": color1, "color2": color2,"y": data, "err": err, 'X':X, 'Y':Y}
            func = fit['class'].calc_model 
        
            #print fit['class'].parinfo                                                                                                                                                                                           
            #print func
            print 'airmass', airmass[0:10]
            print 'color1', color1[0:10]
            print 'color2', color2[0:10]
            print 'data', data[0:10]
            print 'err', err[0:10]
                                               
            print 'X', X[0:10] 
            print 'Y', Y[0:10]                                                                                                                                                                    
            #functkw takes input data arrays
            #parinfo takes initial guess and constraints on parameters 
            #import optimize
            #params, covar, info, mesg, ier = optimize.leastsq(func,guess,args = (points,vals,errs), full_output=True)


            m =  mpfit.mpfit(func, functkw=fa,
                             parinfo=fit['class'].parinfo,
                             maxiter=1000, quiet=1)
            print m.params, m.perror 
            if (m.status <= 0):
                print 'error message = ', m.errmsg
                condition = Numeric.zeros(len(data))
                break
                                                                                                                                                                                                                   
            print m.params,m.perror
                                                                                                                                                                                                                   
            #fits = [{'vars':['zp','color1coeff','color1coeff2'],'parinfo':[{'value':p[0],'fixed':0},{'value':p[1],'fixed':0},{'value':p[2],'fixed':0},'function':phot_funct_secondorder,'fit_type':'no_airmass'}]
                                                                                                                                                                                                                   
            fit['class'].fitvars = {}
            for ele in range(len(fit['class'].smodel)):                              
                print ele, fit['class'].smodel
                name = make_name(fit['class'].smodel[ele])
                print ele, fit['class'].fitvars, name, m.params[ele] 
                fit['class'].fitvars[name] = m.params[ele]          
                fit['class'].fitvars[name + '_err'] = m.perror[ele]
            perror = copy.copy(m.perror)
                                                                                                                                                                                                                   
            # Compute a 3 sigma rejection criterion
            print m.params, data_rec[0], data[0]
            #condition, redchisq = SigmaCond(params, data_save, data,
            #                           airmass_save, airmass,
            #                           color1_save, color1, color2_save, color2, err_save, err, sigmareject)
                                                                                                                                                                                                                   
            if len(data_save) > 1:                                                                     
                (mo_save, reddm) = fit['class'].calc_sigma(m.params, airmass_save, color1_save, color2_save, data_save, err_save, X_save, Y_save)
                #reddm = (data-mo)/err
                redchisq = Numeric.sqrt(Numeric.sum(Numeric.power(reddm, 2)) / (len(reddm) - 1))
                dm = data_save-mo_save
                #dm_save = data_save - mo_save
                print len(data_save), len(mo_save)
                dm_save = data_save - mo_save
                mean =  Numeric.sum(dm)/len(dm)
                sigma = Numeric.sqrt(Numeric.sum(Numeric.power(mean-dm, 2)) / (len(dm) - 1))
                # you can pick either 
                #condition = Numeric.less(Numeric.fabs(dm_save), float(sigmareject) * sigma)
                condition = Numeric.less(Numeric.fabs(dm_save), float(sigmareject) * err_save)
            else:
                condition = Numeric.zeros(len(data_save))
              
            print redchisq 
            # Keep everything (from the full data set!) that is within
            # the 3 sigma criterion
            #data_sig = Numeric.compress(condition, data_save)
            data = Numeric.compress(condition, data_rec)
            airmass = Numeric.compress(condition, airmass_save)
            color1 = Numeric.compress(condition, color1_save)
            color2 = Numeric.compress(condition, color2_save)
            err = Numeric.compress(condition, err_save)
            X = Numeric.compress(condition, X_save)
            Y = Numeric.compress(condition, Y_save)
            stdMag = Numeric.compress(condition, stdMag_save)
            new_len = len(data)
            
            if float(new_len)/float(save_len) < 0.5:
                print "Rejected more than 50% of all measurements."
                print "Aborting this fit."
                break
            
            # No change
            if new_len == old_len:
                print "Converged! (%d iterations)" % (i+1, )
                print "Kept %d/%d stars." % (new_len, save_len)
                break
        #print params, perror, condition
        meanerr = Numeric.sum(err_save)/len(err_save)
        fit['class'].fitvars['good_stars'] = new_len 
        fit['class'].fitvars['start_stars'] = save_len 
        fit['class'].fitvars['redchisq'] = redchisq
        fit['class'].fitvars['meanerr'] = meanerr
        fit['class'].fitvars['condition'] = condition
        
    return fits, data, airmass, color1, color2, err, X, Y, stdMag 

def makePlotsNew(data, airmass, color1, color2, X, Y, outfile, fits, label):
    
    file = outfile+".ps"
    #pgbeg(file+"/cps", 2, 3)
    pgbeg("/XWINDOW",1,1)
    #pgbeg("/XTERM",1,1)
                               
    pgiden()

    index = 0
    for i in range(len(fits)):
        for j in range(len(fits[i]['plots'])):
            fitvars = fits[i]['class'].fitvars                                                                                                                                            
            condition = fitvars['condition']
           
            index += 1 
            h = index%2 
            if h ==0: hor = 2
            else: hor = 1
            ver = int(index/2. + 0.6)
            #print index, ver, hor
            pgpanl(ver,hor)
            #raw_input()
                                                                                                                                                                                          
            #calculate limits
                                                                                                                                                                                          
            # separate into good and bad data -- condition is just a string of 1's and 0's 
            goodAirmass = Numeric.compress(condition, airmass)
            goodData = Numeric.compress(condition, data)
            goodColor1 = Numeric.compress(condition, color1)
            goodColor2 = Numeric.compress(condition, color2)
            goodX = Numeric.compress(condition, X)
            goodY = Numeric.compress(condition, Y)
            badX = Numeric.compress(Numeric.logical_not(condition), X)
            badY = Numeric.compress(Numeric.logical_not(condition), Y)
            badAirmass = Numeric.compress(Numeric.logical_not(condition), airmass)
            badData = Numeric.compress(Numeric.logical_not(condition), data)
            badColor1 = Numeric.compress(Numeric.logical_not(condition), color1)
            badColor2 = Numeric.compress(Numeric.logical_not(condition), color2)
                                                                                                                                                                                          
            dataColMin = fitvars['zp']-1.5
            dataColMax =  fitvars['zp']+1.5

            #dataColMin = 0 #Numeric.sort(data)[0]
            #dataColMax = 10 #Numeric.sort(data)[-1]*1.1

            colMinVal = Numeric.sort(goodColor1)[3]
            if colMinVal < 0:
                colMin = colMinVal*1.1
            else:
                colMin = colMinVal*0.95
            colMaxVal = Numeric.sort(goodColor1)[-3]*1.1


            dataColMin = Numeric.sort(goodData)[0] 
            dataColMax = Numeric.sort(goodData)[-1] 

            colMinVal = Numeric.sort(goodColor1)[0]
            colMaxVal = Numeric.sort(goodColor1)[-1]
            #if colMaxVal > 10: colMaxVal = 10
            #if colMinVal < -10: colMinVal = -10

           
            colMinVal = -1
            colMaxVal = 3
            eqStr = 'test'
                                                                                                                                                                                          
            xaxis_var = fits[i]['plots'][j]['xaxis_var']
                                                                                                                                                                                          
            eqStr = fits[i]['class'].fitvars['model_name'].replace('P','+').replace('T','*')
                                                                                                                                                                                          
            # set x,y limits, label axes, draw box 
            fixenv([colMinVal,colMaxVal] ,
                   [dataColMin, dataColMax],
                   eqStr, label=[xaxis_var, "Mag - Mag(Inst)"])
                                                                                                                                                                                          
            #figure out which values to subtract from the data and which to incorporate into model 
            #print fits[i]
            x_fit,y_fit,x_data,y_data = fits[i]['class'].generate_plot_input(xaxis_var,fits[i]['plots'][j]['term_names'],colMinVal, colMaxVal,goodAirmass,goodColor1,goodColor2,goodData,goodX,goodY)


            x_bad_fit,y_bad_fit,x_bad_data,y_bad_data = fits[i]['class'].generate_plot_input(xaxis_var,fits[i]['plots'][j]['term_names'],colMinVal, colMaxVal,badAirmass,badColor1,badColor2,badData,badX,badY)


    #def generate_plot_input(self, xaxis_var, term_names,Min,Max,airmass=None, color1=None, color2=None, data=None, X=None, Y=None, err=None,  ):
            #print x_fit, y_fit

            print x_bad_data, y_bad_data
            print len(data), len(x_bad_data), len(y_bad_data)
            pgsci(1)
            pgpt(x_bad_data, y_bad_data, 5)


            pgsci(3)
            pgpt(x_data, y_data, 5)


            #pgpt(color1, data, 5)
            pgsci(2)
            pgline(x_fit, y_fit)
                                                                                                                                                                                          
            #x_data,y_data = fits['class'].calc_removed_fixed(fixed,badAirmass, badColor1, badColor2, badData)
            #x_fit,y_fit = fits['class'].generate_fit(fixed,colMinVal,colMaxVal)
            #pgsci(3)
            #pgpt(x_data, y_data, 5)
            #pgpt(x_fit, y_fit, 5)
      
    pgend() 
    return 



def makePlots(data, airmass, color1, color2, outfile, fits, label):

    file = outfile+".ps"
    pgbeg(file+"/cps", 2, 3)

    pgiden()
    for i in range(len(fits)):
        result = fits[i]['fitvars']

        # Airmass plot
        pgpanl(1, i+1)
        airMin = 1
        airMax = Numeric.sort(airmass)[-1]*1.1
        print result
        dataAirMax = result['zp']+result['airmass']+1
        dataAirMin = result['zp']+result['airmass']-1
        dataColMax = result['zp']+1
        dataColMin = result['zp']-1
        colMinVal = Numeric.sort(color)[0]
        if colMinVal < 0:
            colMin = colMinVal*1.1
        else:
            colMin = colMinVal*0.95
        colMax = Numeric.sort(color)[-1]*1.1
        
        
        if result[0] and result[1]:
            eqStr = "%d parameter fit: Mag-Mag(Inst) = %.2f\\(2233)%.2f + (%.2f\\(2233)%.2f) airmass + "\
                    "(%.2f\\(2233)%.2f) color" % \
                    (3-i, result[0]['zp'], result[1][0], result[0]['airmass'], result[1][1], result[0]['color1'], result[1][2])
        else:
            eqStr = "%d parameter fit not possible" % (3-i, )
        
        fixenv([1, airMax] ,
               [dataAirMin, dataAirMax],
               eqStr, label=["Airmass", "Mag - Mag(Inst)"])

        condition = result[4]
        goodAirmass = Numeric.compress(condition, airmass)
        goodData = Numeric.compress(condition, data)
        goodColor = Numeric.compress(condition, color)
        badAirmass = Numeric.compress(Numeric.logical_not(condition), airmass)
        badData = Numeric.compress(Numeric.logical_not(condition), data)
        badColor = Numeric.compress(Numeric.logical_not(condition), color)
      
        #remove the color dependence 
        if len(goodData):
            pgsci(3)
            # Rescale to zero color and filter for data within
            # our plotting range
            plotData = goodData-result[0]['color']*goodColor
            plotCond1 = Numeric.less(plotData, dataAirMax)
            plotCond2 = Numeric.greater(plotData, dataAirMin)
            plotCond = Numeric.logical_and(plotCond1, plotCond2)
            plotAirmass = Numeric.compress(plotCond, goodAirmass)
            plotData = Numeric.compress(plotCond, plotData)
            pgpt(plotAirmass, plotData, 5)
        print type(plotAirmass), type(plotData)

        if len(badData):
            pgsci(2)
            plotData = badData-result[0][2]*badColor
            plotCond1 = Numeric.less(plotData, dataAirMax)
            plotCond2 = Numeric.greater(plotData, dataAirMin)
            plotCond = Numeric.logical_and(plotCond1, plotCond2)
            plotAirmass = Numeric.compress(plotCond, badAirmass)
            plotData = Numeric.compress(plotCond, plotData)
            pgpt(plotAirmass, plotData, 5)
        pgsci(1)

        a = Numeric.arange(1, airMax, 0.01)
        m = result[0][0] + result[0][1] * a
        pgline(a, m)
        
        # Color Plot
        pgpanl(2, i+1)

        fixenv([colMin, colMax] ,
               [dataColMin, dataColMax],
               eqStr, label=[label, "Mag - Mag(Inst)"])

        if len(goodData):
            pgsci(3)
            # Rescale to zero airmass and filter for data within
            # our plotting range
            plotData = goodData-result[0][1]*goodAirmass
            plotCond1 = Numeric.less(plotData, dataColMax)
            plotCond2 = Numeric.greater(plotData, dataColMin)
            plotCond = Numeric.logical_and(plotCond1, plotCond2)
            plotColor = Numeric.compress(plotCond, goodColor)
            plotData = Numeric.compress(plotCond, plotData)
            pgpt(plotColor, plotData, 5)
        if len(badData):
            pgsci(2)
            plotData = badData-result[0][1]*badAirmass
            plotCond1 = Numeric.less(plotData, dataColMax)
            plotCond2 = Numeric.greater(plotData, dataColMin)
            plotCond = Numeric.logical_and(plotCond1, plotCond2)
            plotColor = Numeric.compress(plotCond, badColor)
            plotData = Numeric.compress(plotCond, plotData)
            pgpt(plotColor, plotData, 5)
        pgsci(1)

        a = Numeric.arange(colMin, colMax, 0.01)
        m = result[0][0] + result[0][2] * a
        pgline(a, m)
    return

def fixenv (xrange=[0,1], yrange=[0,1], fname="none", ci = 1, label=["x", "y"]):
                              # set axis ranges.
    pgswin(xrange[0], xrange[1], yrange[0], yrange[1])     
    pgsci(ci)                # set color index.
    pgbox()                  # draw axes. 
    pgsci(1)                 # back to color index 1 (white)
    pglab(label[0], label[1], fname)     # label the plot
    return


#def saveResults(file, solutions, step, sigmareject, cluster, color1, color2):

def saveResults(file, fits, var_names, step):
    f = open(file+".asc", "w")
    which_solution = 0
    
    import MySQLdb, sys, os, re                                                                     
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-sr01')
    c = db2.cursor()

    for fit in fits:
        which_solution += 1
        #if Numeric.sometrue(result[2]):
        import os , time
        user_name = os.environ['USER']
        bonn_target = os.environ['BONN_TARGET']
        bonn_filter = os.environ['BONN_FILTER']
        time_now = time.asctime() 
        user = user_name

        stringvars = {'USER':user_name,'BONN_TARGET':bonn_target,'BONN_FILTER':bonn_filter,'TIME':time_now,'CHOICE':'', 'NUMBERVARS':4-which_solution,'USER': user, 'step': step} 
        for ele in var_names.keys():         
            stringvars[ele] = var_names[ele]
        #print stringvars

        from copy import copy
        floatvars = {}  
        #copy array but exclude lists                                                   
        for ele in fit['class'].fitvars.keys():
            if ele != 'condition' and ele != 'model_name' and ele != 'fixed_name': 
                floatvars[ele] = fit['class'].fitvars[ele]
            elif ele == 'model_name' or ele == 'fixed_name':
                stringvars[ele] = fit['class'].fitvars[ele]

        # make database if it doesn't exist
        make_db = reduce(lambda x,y: x + ',' + y,[x  + ' float(30)' for x in floatvars.keys()])
        make_db += ',' + reduce(lambda x,y: x + ',' + y,[x  + ' varchar(80)' for x in stringvars.keys()])
        command = "CREATE TABLE IF NOT EXISTS photometry_db ( id MEDIUMINT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id))"
        #print command
        #c.execute("DROP TABLE IF EXISTS photometry_db")
        #c.execute(command)

        for column in stringvars: 
            try:
                command = 'ALTER TABLE photometry_db ADD ' + column + ' varchar(80)'
                c.execute(command)  
            except: nope = 1 

        for column in floatvars: 
            try:
                command = 'ALTER TABLE photometry_db ADD ' + column + ' float(30)'
                c.execute(command)  
            except: nope = 1 

        # insert new observation 
        names = reduce(lambda x,y: x + ',' + y, [x for x in floatvars.keys()])
        values = reduce(lambda x,y: str(x) + ',' + str(y), [floatvars[x] for x in floatvars.keys()])

        names += ',' + reduce(lambda x,y: x + ',' + y, [x for x in stringvars.keys()])
        values += ',' + reduce(lambda x,y: x + ',' + y, ["'" + str(stringvars[x]) + "'" for x in stringvars.keys()])
        command = "INSERT INTO photometry_db (" + names + ") VALUES (" + values + ")"
        printvals = {}
        for key in floatvars.keys():         
            printvals[key] = floatvars[key]
        for key in stringvars.keys():
            printvals[key] = stringvars[key]
        print "##" + printvals['model_name'] + '##'
        keylist = printvals.keys()
        keylist.sort()
        for key in keylist:
            print key, ": ", printvals[key]
        print "######"
        #print command
        c.execute(command)
 
    #f.write("%s %s %s\n" % (result[0][0], result[0][1], result[0][2]))
    #f.write("%s %s %s\n" % (result[1][0], result[1][1], result[1][2]))
    #f.write("%s#ReducedChiSq\n" % (result[2]))
    #f.write("%s#MeanError\n" % (result[3]))
    #f.write("%s\n" % (id))
    #else:
    #    f.write("-1 -1 -1\n")
    #    f.write("-1 -1 -1\n")
    #    f.write("-1#ReducedChiSq\n")
    #    f.write("-1#MeanError\n")
    #    f.write("%s\n" % (id))
    f.close
    return id
                


def usage():
    print "Usage:"
    print "photo_abs.py -i input -f filter -n GABODSID - e ext. coeff. -c color coeff. -o output -l label"
    print
    print "    -i, --input=STRING        Input file, must have 4 columns: Instrumental Mag, Standard Mag, Color, Airmass"
    print "    -o, --output=STRING       Output file basename"
    print "    -n, --night=INT           GABODSID, unique numerical night identifier"
    print "    -e, --extinction=FLOAT    Default value of extinction coefficient for one/two parameter fit"
    print "    -c, --color=FLOAT         Default value of color term for one parameter fit"
    print "    -l, --label=STRING        Label for color axis (e.g. B-V)"
    print
    print "Author:"
    print "    Joerg Dietrich <dietrich@astro.uni-bonn.de>"
    print
    return
    


if __name__ == "__main__":

    __bonn_logger_id__ = BonnLogger.addCommand('photo_abs_new.py', 
                                                       sys.argv[1:])


    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "i:n:o:e:c:l:s:",
                                   ["input=", "night=", "extinction=",
                                    "color=", "output=", "label=","sigmareject=","step=","cluster=","bandcomp=","color1=","color2="])
    except getopt.GetoptError:
        usage()
        BonnLogger.updateStatus(__bonn_logger_id__, 1)
        sys.exit(2)
    print sys.argv[1:]

    infile = night = extcoeff = colcoeff = outfile = label = sigmareject = step = cluster = color1which = color2which = bandcomp = None
    for o, a in opts:
        if o in ("-i", "--input"):
            infile = a
        elif o in ("-o", "--output"):
            outfile = a
        elif o in ("-n", "--night"):
            night = int(a)
        elif o in ("-e", "--extinction"):
            extcoeff  = float(a)
        elif o in ("-c", "--color"):
            colcoeff = float(a)
        elif o in ("-l", "--label"):
            label = a
        elif o in ("-s", "--sigmareject"): 
                sigmareject = float(a)
        elif o in ("-t", "--step"):
                step = a
        elif o in ("-c", "--cluster"):
                cluster = a
        elif o in ("-b", "--bandcomp"):
                bandcomp = a
        elif o in ("-1", "--color1"):
                color1which = a
        elif o in ("-2", "--color2"):
                color2which = a
        else:
            print "option:", o
            usage()
            BonnLogger.updateStatus(__bonn_logger_id__, 1)
            sys.exit(2)
    print cluster
    #raw_input()

    #### FIX COLOR COEFF
            
    if not infile or night==None or not outfile or \
           extcoeff==None or colcoeff==None or label==None:
        #print infile, night, outfile, coeff, color
        usage()
        BonnLogger.updateStatus(__bonn_logger_id__, 1)
        sys.exit(2)

    print cluster,infile,outfile,extcoeff,sigmareject,step,bandcomp,color1which,color2which
    run_main(cluster,infile,outfile,extcoeff,sigmareject,step,bandcomp,color1which,color2which)
        
    BonnLogger.updateStatus(__bonn_logger_id__, 0)

