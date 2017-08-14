#!/usr/bin/env python

import sys, glob,pyfits, os.path
import scipy
import scipy.interpolate.interpolate as interp

c = 299792458e10 #Angstroms/s

''' search SDSS online database from spectra with similar colors to locus point '''
def get_sdss_spectra(umg, imz, gmr,rmi,number=4,tol=0.01,S_N=5):   
    import sqlcl

    dict_names = ['plate', 'MJD', 'fiberID', 'ra', 'dec', 'mag_0', 'mag_1', 'mag_2']
    query = 'select top ' + str(number) + ' ' + reduce(lambda x,y: x + ',' + y, ['s.' + x for x in dict_names]) + ' from specobjall as s join specphotoall as p on s.specobjid = p.specobjid where abs(s.mag_0 - s.mag_1 - ' + str(gmr) + ') < ' + str(tol) + ' and abs(s.mag_1 - s.mag_2 - ' + str(rmi) + ') < ' + str(tol) + ' and abs(s.mag_0 - s.mag_2 - ' + str(gmr + rmi) + ') < ' + str(tol) + ' and s.sn_0 > ' + str(S_N) + ' and s.sn_1 > ' + str(S_N) + ' and s.sn_2 > ' + str(S_N) + ' and abs(s.mag_0 - s.mag_1 - (p.fibermag_g - p.fibermag_r)) < 0.1 and abs(s.mag_1 - s.mag_2 - (p.fibermag_r - p.fibermag_i)) < 0.1  order by -1.*s.sn_1'

    if rmi < 0.7: pattern = 'zbelodiesptype like "%v%" and zbelodiesptype not like "%var%"'
    #elif 0.7 < rmi < 1.0: pattern = '(zbelodiesptype like "%G%v%" or zbelodiesptype like "%K%v%" or zbelodiesptype like "%M%v%")'
    else: pattern = 'zbelodiesptype like "%M%v%"'

    query = 'select top ' + str(number) + ' ' + reduce(lambda x,y: x + ',' + y, ['s.' + x for x in dict_names]) + ' from specobjall as s join specphoto as p on s.specobjid = p.specobjid join sppParams sp on sp.specobjid = s.specobjid where zbclass="STAR" and ' + pattern +  ' and abs(s.mag_0 - s.mag_1 - ' + str(gmr) + ') < ' + str(tol) + ' and abs(s.mag_1 - s.mag_2 - ' + str(rmi) + ') < ' + str(tol) + ' and abs(s.mag_0 - s.mag_2 - ' + str(gmr + rmi) + ') < ' + str(tol) + ' and s.sn_0 > ' + str(S_N) + ' and s.sn_1 > ' + str(S_N) + ' and s.sn_2 > ' + str(S_N) + ' and abs(s.mag_0 - s.mag_1 - (p.fibermag_g - p.fibermag_r)) < 0.1 and abs(s.mag_1 - s.mag_2 - (p.fibermag_r - p.fibermag_i)) < 0.1  and abs(' + str(umg) + ' - (p.psfMag_u - p.psfMag_g)) < 0.05 and abs(' + str(imz) + ' - (p.psfMag_i - p.psfMag_z)) < 0.05 \
order by -1.*s.sn_1'


    query = 'select top ' + str(number) + ' ' + reduce(lambda x,y: x + ',' + y, ['s.' + x for x in dict_names]) + ' from specobjall as s join specphoto as p on s.specobjid = p.specobjid join sppParams sp on sp.specobjid = s.specobjid where zbclass="STAR" and ' + pattern +  ' and abs(s.mag_0 - s.mag_1 - ' + str(gmr) + ') < ' + str(tol) + ' and abs(s.mag_1 - s.mag_2 - ' + str(rmi) + ') < ' + str(tol) + ' and abs(s.mag_0 - s.mag_2 - ' + str(gmr + rmi) + ') < ' + str(tol) + ' and s.sn_0 > ' + str(S_N) + ' and s.sn_1 > ' + str(S_N) + ' and s.sn_2 > ' + str(S_N) + ' and abs(s.mag_0 - s.mag_1 - (p.fibermag_g - p.fibermag_r)) < 0.1 and abs(s.mag_1 - s.mag_2 - (p.fibermag_r - p.fibermag_i)) < 0.1  and abs(' + str(umg) + ' - (p.psfMag_u - p.psfMag_g)) < 0.05 and abs(' + str(imz) + ' - (p.psfMag_i - p.psfMag_z)) < 0.05 \
order by -1.*s.sn_1'







    import time
    time.sleep(1.5)

    print query
    lines = sqlcl.query(query).readlines()
    print lines

    dicts = []                                                                                   

    if lines[0] != 'N':

        for line in lines[1:]:
            dict = {}
            line = line.replace('\n','')
            import re
            res = re.split(',',line)
            print res
            for i in range(len(res)): 
                if dict_names[i] == 'fiberID' or dict_names[i] == 'plate' or dict_names[i] == 'MJD':
                    dict[dict_names[i]] = int(res[i])
                else:
                    dict[dict_names[i]] = (res[i])
            print dict
            dicts.append(dict)
                                                                                                     
        print dicts

    return dicts

def download_sdss_spectrum(dict,plot=False): 
    dict['gmr'] = float(dict['mag_0']) - float(dict['mag_1'])
    dict['rmi'] = float(dict['mag_1']) - float(dict['mag_2'])
    print dict
    file = "http://das.sdss.org/spectro/1d_26/%(plate)04d/1d/spSpec-%(MJD)d-%(plate)04d-%(fiberID)03d.fit" % dict      
    print file
    import pyfits, scipy
    import scipy
    p = pyfits.open(file)
    mask = p[0].data[3]
    flux = p[0].data[0]            
    indices = scipy.array(range(len(flux)))
    
    print mask
    COEFF0 = p[0].header['COEFF0']            
    COEFF1 = p[0].header['COEFF1']            
    import scipy
    wavelength = 10.**(COEFF0 + COEFF1*indices)
    spectrum = []
    for i in range(len(indices)):
        spectrum.append([wavelength[i],flux[i]])
    import scipy
    spectrum = scipy.array(spectrum)
    if plot:
        import pylab                    
        pylab.plot(spectrum[:,0], spectrum[:,1])
        pylab.xlabel('angstroms')
        pylab.ylabel('flux')
        pylab.show()
    return spectrum 

def make_new_spectrum(locus_index,plot=False):
    filters = get_filters()
    import pickle
    f = open('picklelocus_MACS','r')
    m = pickle.Unpickler(f)
    stars = m.load()

    import string 
    spectra_complete = load_spectra() 
    locus_list = locus()
    comp_list =  filter(lambda x: string.find(x.replace('SDSS_',''),'SDSS')!=-1 and string.find(x,'SDSS_')!=-1, locus_list.keys())
    print comp_list

    import pylab
    
    gmr_all = locus_list['GSDSS_RSDSS'][:]
    rmi_all = locus_list['RSDSS_ISDSS'][:]
    umg_all = locus_list['USDSS_GSDSS'][:]
    imz_all = locus_list['ISDSS_ZSDSS'][:]

    #locus_index = 13
    print 'locus_index', locus_index
    gmr = locus_list['GSDSS_RSDSS'][locus_index]
    rmi = locus_list['RSDSS_ISDSS'][locus_index]
    umg = locus_list['USDSS_GSDSS'][locus_index]
    imz = locus_list['ISDSS_ZSDSS'][locus_index]

    print gmr, rmi  

    if plot:
        pylab.clf()                         
        pylab.scatter(gmr_all,rmi_all,color='blue')
        pylab.scatter(gmr,rmi,color='red')
        pylab.show()

    if False:
        closest = closest_pickles(stars, locus_list, locus_index, comp_list)
        closest_index = closest[1][1]
        import pylab
        print 'plotting'                                                                            
        print spectra_complete[closest_index][0][:,0]
        print spectra_complete[closest_index][0][:,1]
        pylab.plot(spectra_complete[closest_index][0][:,0],spectra_complete[closest_index][0][:,1])
        pylab.xlim(3000,11000)
        pylab.show()

    print 'plotted'

    import pickle
    f = open('picklelocus_MACS','r')
    m = pickle.Unpickler(f)
    stars = m.load()
    locus_list = locus()

    good = False
    gmr_off = 0
    rmi_off = 0
    trys = 0
    tol = 0.01
    while not good:
        trys += 1
        print gmr, rmi                                            
        dicts = get_sdss_spectra(umg,imz,gmr-gmr_off,rmi-rmi_off,tol=tol)

        if len(dicts):
            print dicts                                                
            gmr_diffs = []
            rmi_diffs = []
            for dict in dicts:
                spectrum = download_sdss_spectrum(dict,plot=False)
                mags = synth([1.],[[spectrum]],filters,show=False)
                print mags
                gmr_diffs.append(mags['GSDSS'] - mags['RSDSS'] - gmr)
                rmi_diffs.append(mags['RSDSS'] - mags['ISDSS'] - rmi)
                print mags['GSDSS'] - mags['RSDSS'], gmr
                print float(dict['mag_0']) - float(dict['mag_1'])
                print mags['RSDSS'] - mags['ISDSS'], rmi
                print float(dict['mag_1']) - float(dict['mag_2'])

                                                                       
            gmr_diffs.sort()
            rmi_diffs.sort()
                                                                      
            median_gmr = gmr_diffs[int(len(gmr_diffs)/2)]
            median_rmi = rmi_diffs[int(len(rmi_diffs)/2)]
                                                                       
            if abs(median_gmr) > tol or abs(median_rmi) > tol:
                gmr_off += median_gmr
                rmi_off += median_rmi
            else: good = True            
                                                                       
            print gmr_diffs, rmi_diffs
            print median_gmr, median_rmi
            print gmr, rmi
        else: tol += 0.01
   
    print spectrum 
    print comp_list

    if plot:
        max = spectrum[:,1].max()               
        pylab.plot(spectrum[:,0],spectrum[:,1]/max)
        #pylab.plot(spectra_complete[closest_index][0][:,0],spectra_complete[closest_index][0][:,1])
        pylab.xlim(3000,11000)
        pylab.show()

    sdssSpec, pickleSpec, pickleName = similar(spectrum)

    info = pickleName +  ' pickleName ' +  str(gmr) + ' gmr ' +  str(rmi) +  ' rmi'
    stitchSpec = optimize(sdssSpec,pickleSpec, locus_index,info=info, plot=plot)
    print stitchSpec

    return stitchSpec, pickleSpec, info


def break_slr():
    locus_list = locus()
    keys = locus_list.keys()
    #keys += ['WSRSUBARU_WSGSUBARU','WSRSUBARU_WSISUBARU','WSRSUBARU_WSZSUBARU','MPUSUBARU_WSRSUBARU','BJOHN_WSRSUBARU','WSGSUBARU_WSISUBARU']
    keys += ['WSRSUBARU_WSGSUBARU','WSRSUBARU_WSISUBARU','WSRSUBARU_WSZSUBARU','MPUSUBARU_WSRSUBARU','BJOHN_WSRSUBARU','WSGSUBARU_WSISUBARU','WHTB_VJOHN','WHTU_VJOHN','B_VJOHN','I_VJOHN']
    print keys

    locus_list_new = dict([[x,[]] for x in keys])
    filters = get_filters(sdss=False)
    print filters

    locus_list_mag = []

    spectra = []        
    for i in 2* scipy.array(range(len(locus_list[keys[0]])/2)):
        if i > len(locus_list_mag):
            stitchSpec, pickleSpec, info = make_new_spectrum(i,plot=False)                                  

            spectra.append(stitchSpec)
            mags = synth([1.,0,0,0],[[stitchSpec]],filters) 
            print filters
            locus_list_mag.append(mags)
                                                                             
            for key in keys:
                if key != 'NUM':
                    import re                                               
                    res = re.split('\_',key)
                    locus_list_new[key].append(mags[res[0]] - mags[res[1]])
                else: locus_list_new['NUM'] = i
            print locus_list_new
                                                                             
            import pickle 
            f = open('newlocus_broken_SYNTH','w')
            m = pickle.Pickler(f)
            pickle.dump(locus_list_new,m)
            f.close()
                                                                             
            import pickle 
            f = open('maglocus_broken_SYNTH','w')
            m = pickle.Pickler(f)
            pickle.dump(locus_list_mag,m)
            f.close()

            f = open('spectra_broken_SYNTH','w')
            m = pickle.Pickler(f)
            pickle.dump(spectra,m)
            f.close()


''' assemble a new locus '''
def make_new_locus():
    
    locus_list = locus()

    keys = locus_list.keys()

    #keys += ['WSRSUBARU_WSGSUBARU','WSRSUBARU_WSISUBARU','WSRSUBARU_WSZSUBARU','MPUSUBARU_WSRSUBARU','BJOHN_WSRSUBARU','WSGSUBARU_WSISUBARU']

    keys += ['WSRSUBARU_WSGSUBARU','WSRSUBARU_WSISUBARU','WSRSUBARU_WSZSUBARU','MPUSUBARU_WSRSUBARU','BJOHN_WSRSUBARU','WSGSUBARU_WSISUBARU','WHTB_VJOHN','WHTU_VJOHN','B_VJOHN','I_VJOHN']
    print keys

    locus_list_new = dict([[x,[]] for x in keys])
    filters = get_filters(sdss=False)
    print filters

    locus_list_mag = []
   
    if False:
        import pickle 
        f = open('newlocus','r')
        m = pickle.Unpickler(f)
        locus_list_new = m.load()
                                      
        import pickle 
        f = open('maglocus','r')
        m = pickle.Unpickler(f)
        locus_list_mag = m.load()




    spectra = []        


    for i in 2* scipy.array(range(len(locus_list[keys[0]])/2)):
        if i > len(locus_list_mag):
            stitchSpec, pickleSpec, info = make_new_spectrum(i,plot=False)                                  

            spectra.append(stitchSpec)
                                                                             
            mags = synth([1.,0,0,0],[[stitchSpec]],filters) 
            print filters
            print mags['GSDSS'] - mags['RSDSS']
                                                                             
            print mags
            locus_list_mag.append(mags)
                                                                             
            for key in keys:
                if key != 'NUM':
                    import re                                               
                    res = re.split('\_',key)
                    locus_list_new[key].append(mags[res[0]] - mags[res[1]])
                else: locus_list_new['NUM'] = i
                
                
            print locus_list_new

                                                                             
            import pickle 
            f = open('newlocus_SYNTH','w')
            m = pickle.Pickler(f)
            pickle.dump(locus_list_new,m)
            f.close()
                                                                             
            import pickle 
            f = open('maglocus_SYNTH','w')
            m = pickle.Pickler(f)
            pickle.dump(locus_list_mag,m)
            f.close()


            import pickle 
            f = open('spectra_SYNTH','w')
            m = pickle.Pickler(f)
            pickle.dump(spectra,m)
            f.close()


def optimize(specSDSS,pickleSpec,locus_index,info=None,plot=False):
    filters = get_filters()
    locus_list = locus()
    import string

    comp_list =  filter(lambda x: string.find(x.replace('SDSS_',''),'SDSS')!=-1 and string.find(x,'SDSS_')!=-1, locus_list.keys())
    print comp_list
    grdiff = (locus_list['GSDSS_RSDSS'][locus_index])
    
    sdssSpline = interp.interp1d(specSDSS[:,0], specSDSS[:,1], 
                    bounds_error = False, 
                    fill_value = 0.)

    sdssLimits = [specSDSS[0,0],8500] #specSDSS[-1,0]]
    sdssLimits = [4200,8500] #specSDSS[-1,0]]
    zOverLap = [8000,9000]
    uOverLap = [4100,4600]

    print sdssLimits
    specSDSS_new = []
    for l in specSDSS:
        if sdssLimits[0] < l[0] < sdssLimits[1]:
            specSDSS_new.append(l)

    import scipy
    specSDSS = scipy.array(specSDSS_new)
    
    uSpec = []
    zSpec = []
    zOverLapData = []
    uOverLapData = []
    for l in pickleSpec:
        if l[0] < sdssLimits[0]:
            uSpec.append(l)
        if l[0] > sdssLimits[1]:
            zSpec.append(l)
        if zOverLap[0] < l[0] < zOverLap[1]:
            zOverLapData.append(l)
        if uOverLap[0] < l[0] < uOverLap[1]:
            uOverLapData.append(l)

    uOverLapData = scipy.array(uOverLapData)        
    zOverLapData = scipy.array(zOverLapData)        

    uSpec = scipy.array(uSpec)        
    zSpec = scipy.array(zSpec)        

    zRescale = scipy.median(sdssSpline(zOverLapData[:,0])/ zOverLapData[:,1])
    uRescale = scipy.median(sdssSpline(uOverLapData[:,0])/ uOverLapData[:,1])

    import scipy
    uSpec = scipy.array(zip(uSpec[:,0],uRescale*uSpec[:,1]))
    zSpec = scipy.array(zip(zSpec[:,0],zRescale*zSpec[:,1]))

    import pylab
    if False:
        pylab.clf()                              
        pylab.plot(uSpec[:,0],uSpec[:,1])
        pylab.plot(zSpec[:,0],zSpec[:,1])
        pylab.plot(specSDSS[:,0],specSDSS[:,1])
        pylab.show()

    def plot(specStitch,pickleSpecMod):
        pylab.clf()                              
        pylab.plot(specStitch[:,0],specStitch[:,1])
        print pickleSpecMod
        #pylab.plot(pickleSpecMod[:,0],pickleSpecMod[:,1])
        pylab.xlim([3000,10000])
        pylab.show()

    fit_list = ['USDSS_GSDSS','GSDSS_ZSDSS','ISDSS_Z_SDSS']        

    def errfunc(p,plot_it=False, getSpec=False):

        
        uWarp = interp.interp1d([2500]+uOverLap, [abs(p[0]),1.,1.], 
                    bounds_error = False, 
                    fill_value = 1.)

        zWarp = interp.interp1d(zOverLap + [11000], [1.,1.,abs(p[1])], 
                    bounds_error = False, 
                    fill_value = 1.)

        specStitch_0 = (uSpec[:,0].tolist() + specSDSS[:,0].tolist() + zSpec[:,0].tolist())
        specStitch_1 = (uSpec[:,1].tolist() + specSDSS[:,1].tolist() + zSpec[:,1].tolist())

        

        specStitch = scipy.array(zip(specStitch_0,specStitch_1*uWarp(specStitch_0)*zWarp(specStitch_0)))
        mags = synth([1.,0,0,0],[[specStitch]],filters) 
        #print mags
        #raw_input()

        if False: #getSpec: #plot_it:
            import pylab
            pylab.plot(pickleSpec[:,0],uWarp(pickleSpec[:,0])*zWarp(pickleSpec[:,0]),color='red')
            pylab.xlim([3000,10000])
            pylab.show()

            #plot(specStitch,scipy.array(zip(pickleSpec[:,0].tolist(),(uWarp(pickleSpec[:,0])*zWarp(pickleSpec[:,0])*pickleSpec[:,1]).tolist())))

            #plot(specStitch,scipy.array(zip(specStitch[:,0].tolist(),(uWarp(specStitch[:,0])*zWarp(specStitch[:,0])*specStitch[:,1]).tolist())))

            plot(specStitch,specStitch[:,1])

            pylab.show()

        #print mags
        ugdiff = (mags['USDSS'] - mags['GSDSS'] - locus_list['USDSS_GSDSS'][locus_index])

        #urdiff = (mags['USDSS'] - mags['RSDSS'] - locus_list['USDSS_RSDSS'][locus_index])
        gzdiff = (mags['GSDSS'] - mags['ZSDSS'] - locus_list['GSDSS_ZSDSS'][locus_index])
        izdiff = (mags['ISDSS'] - mags['ZSDSS'] - locus_list['ISDSS_ZSDSS'][locus_index])
        ridiff = (mags['RSDSS'] - mags['ISDSS'] - locus_list['RSDSS_ISDSS'][locus_index])
        stat = ( ugdiff**2. + gzdiff**2.  + izdiff**2. + ridiff**2.)


        
        print (locus_list['GSDSS_RSDSS'][locus_index]), mags['GSDSS'] - mags['RSDSS']

        print ugdiff, gzdiff, izdiff, stat

        
        if getSpec: return specStitch
        else:
            return stat

    from scipy import optimize
    pinit = [1.,1.]
    out = scipy.optimize.fmin(errfunc,pinit,args=()) 
    print out
    stitchSpec = errfunc(out,plot_it=plot,getSpec=True)

    if True: #getSpec: #plot_it:
        import pylab
        #pylab.plot(pickleSpec[:,0],uWarp(pickleSpec[:,0])*zWarp(pickleSpec[:,0]),color='red')
        #pylab.xlim([3000,10000])
        #pylab.show()
                                                                                                                                              
        #plot(specStitch,scipy.array(zip(pickleSpec[:,0].tolist(),(uWarp(pickleSpec[:,0])*zWarp(pickleSpec[:,0])*pickleSpec[:,1]).tolist())))
                                                                                                                                              
        #plot(specStitch,scipy.array(zip(specStitch[:,0].tolist(),(uWarp(specStitch[:,0])*zWarp(specStitch[:,0])*specStitch[:,1]).tolist())))
                                                                                                                                              
        #plot(specSDSS,specSDSS[:,1])
        #plot(stitchSpec,stitchSpec[:,1])

        pylab.clf()                              

        params = {'backend' : 'ps',                                 
             'text.usetex' : True,
              'ps.usedistiller' : 'xpdf',
              'ps.distiller.res' : 6000}
        pylab.rcParams.update(params)
        
        fig_width = 6
        fig_height = 6                                       
        
        fig_size = [fig_width,fig_height]
        params = {'axes.labelsize' : 16,
                  'text.fontsize' : 16,
                  'legend.fontsize' : 15,
                  'xtick.labelsize' : 16,
                  'ytick.labelsize' : 16,
                  'figure.figsize' : fig_size}
        pylab.rcParams.update(params)

        pylab.plot(stitchSpec[:,0], stitchSpec[:,1],label='Pickles')
        pylab.plot(specSDSS[:,0],specSDSS[:,1],c='red',label='SDSS')
        #pylab.plot(pickleSpec[:,0],specSDSS[:,1],c='yellow',label='SDSS')
        pylab.xlim([3000,10000])
        pylab.legend(frameon=False)
        pylab.xlabel('Wavelength (Angstroms)')
        pylab.ylabel('Flux')

        pylab.savefig(os.environ['sne'] + '/photoz/slrs/' + info.replace('/','').replace(' ','_') + '.pdf')

        #pylab.show()



    mags = synth([1.,0,0,0],[[stitchSpec]],filters) 

    print (locus_list['GSDSS_RSDSS'][locus_index]), mags['GSDSS'] - mags['RSDSS']

    return stitchSpec

    



def similar(input):

    #sdssSpectrum = sdssSpectrum[0]

    from copy import copy
    sdssSpectrum = copy(input)

    import scipy, pylab
    print scipy.median(sdssSpectrum[:,1])
    sdssSpectrum[:,1] = sdssSpectrum[:,1] / (scipy.ones(len(sdssSpectrum[:,1]))*scipy.median(sdssSpectrum[:,1]))
    print sdssSpectrum


    spectra_complete = load_spectra() 

    diffs = []

    for i in range(len(spectra_complete)):
        sp = spectra_complete[i] 
        spectrum = sp[0]
        picklesSpline = interp.interp1d(spectrum[:,0], spectrum[:,1], 
                                   bounds_error = False, 
                                   fill_value = 0.)


        specInterp = picklesSpline(sdssSpectrum[:,0])
        
        specInterp = specInterp / (scipy.ones(len(sdssSpectrum[:,1]))*scipy.median(specInterp))

        diff = specInterp - sdssSpectrum[:,1]
        diff = diff - scipy.ones(len(diff))*scipy.median(diff)
        stat = abs(diff).sum()
        print stat, i
        diffs.append([stat,i])

    diffs.sort()

    
    sp = spectra_complete[diffs[0][1]] 
    spectrum = sp[0]
    picklesSpline = interp.interp1d(spectrum[:,0], spectrum[:,1], 
                               bounds_error = False, 
                               fill_value = 0.)
                                                                                          
                                                                                          
    specInterp = picklesSpline(sdssSpectrum[:,0])
    
    specInterp = specInterp / (scipy.ones(len(sdssSpectrum[:,1]))*scipy.median(specInterp))
                                                                                          
    diff = specInterp - sdssSpectrum[:,1]
    diff = diff - scipy.ones(len(diff))*scipy.median(diff)

    import scipy
    specAll = scipy.array(zip(spectrum[:,0], spectrum[:,1] / (scipy.ones(len(spectrum[:,1]))*scipy.median(specInterp))))
    if False: 
        pylab.clf()                                     
        pylab.plot(specAll[:,0],specAll[:,1])
        pylab.plot(sdssSpectrum[:,0],sdssSpectrum[:,1])
        pylab.plot(sdssSpectrum[:,0],diff)
                                                        
        pylab.xlim(3000,11000)
        pylab.show()

    ''' need to fit spectral ends to reproduce locus color '''        

    return sdssSpectrum, specAll, spectra_complete[diffs[0][1]][1]

    



def load_spectra():
    import pickle
    f = open('picklespectra','r')
    m = pickle.Unpickler(f)
    spectra = m.load()
    
    return spectra

def locus():
    import os, re
    f = open(os.environ['bonn'] + '/locus.txt','r').readlines()
    id = -1
    rows = {}
    colors = {}
    for i in range(len(f)):
        l = f[i]
        if l[0] != ' ':
            rows[i] = l[:-1]
        else: 
            id += 1 
            colors[rows[id]] = [float(x) for x in re.split('\s+',l[:-1])[1:]]
    import pylab
    #pylab.scatter(colors['GSDSS_ZSDSS'],colors['RSDSS_ISDSS'])       
    #pylab.show()

    return colors




def readtxtfile(file):
    import re
    f = open(file,'r').readlines()
    file_out = []
    for l in f:
        import re
        res = re.split('\s+',l)
        if l[0] != '#':
            if res[0] == '': res = res[1:]           
            if res[-1] == '': res = res[:-1]
            file_out.append([float(x) for x in res])
    filt_out = scipy.array(file_out)
    #print file, 'file'
    return filt_out


def get_filters(sdss=True):

    #filter = readtxtfile(filterfile)[:,:2]                                                                                                        
    if sdss:
        #flist = [['USDSS','u_SDSS.res'],['GSDSS','g_SDSS.res'],['RSDSS','r_SDSS.res'],['ISDSS','i_SDSS.res'],['ZSDSS','z_SDSS.res']]

        flist = [['USDSS','SDSS-u.res'],['GSDSS','SDSS-g.res'],['RSDSS','SDSS-r.res'],['ISDSS','SDSS-i.res'],['ZSDSS','SDSS-z.res']]
    else:
        flist = [['BJOHN','SUBARU-10_1-1-W-J-B.res'],['VJOHN','SUBARU-10_1-1-W-J-V.res'],['RJOHN','SUBARU-10_1-1-W-C-RC.res'],['IJOHN','SUBARU-10_1-1-W-C-IC.res'],['MPUSUBARU','MEGAPRIME-0-1-u.res'],['MPGSUBARU','MEGAPRIME-0-1-g.res'],['MPRSUBARU','MEGAPRIME-0-1-r.res'],['MPISUBARU','MEGAPRIME-0-1-i.res'],['MPZSUBARU','MEGAPRIME-0-1-z.res'],['USDSS','SDSS-u.res'],['GSDSS','SDSS-g.res'],['RSDSS','SDSS-r.res'],['ISDSS','SDSS-i.res'],['ZSDSS','SDSS-z.res'],['JTMASS','J2MASS.res'],['HTMASS','H2MASS.res'],['KTMASS','K2MASS.res'],['WSZSUBARU','SUBARU-10_1-1-W-S-Z+.res'],['CAPAKIS','i_subaru.res'],['WSISUBARU','SUBARU-10_1-1-W-S-I+.res'],['WKSUBARU','SPECIAL-0-1-K.res'],['WSGSUBARU','SUBARU-10_1-1-W-S-G+.res'],['WSRSUBARU','SUBARU-10_1-1-W-S-R+.res'],['WHTB','WHT-0-1-B.res'],['WHTU','WHT-0-1-U.res'],['B','B_12k.res'],['I','MEGAPRIME-0-1-i.res']]

    
    filters = []
    for name, filt_name in flist:
        file = '/a/wain010/g.ki.ki04/pkelly/bpz-1.99.2/FILTER/' + filt_name
        #filt = readtxtfile(file)

        import numpy
        filt = numpy.loadtxt(file)
        #filt = filt[filt[:,1]>0] 
        import pylab
        print filt_name
        #pylab.plot(filt[:,0],filt[:,1])
        #pylab.show()
        step = filt[1,0] - filt[0,0]
        if filt[0,0] > filt[-1,0]:
            filt_list = filt.tolist()
            filt_list.reverse()
            import scipy
            filt = scipy.array(filt_list)

            print filt
            import string
            #if string.find(filt_name,'SDSS') != -1:


        from copy import copy
        filterSpline = interp.interp1d(filt[:,0], filt[:,1], 
                                       bounds_error = False, 
                                       fill_value = 0.)
        filters.append([copy(filterSpline),copy(step),copy(name)])

    return filters

def get_spectra():
    spectrafiles = glob.glob('dwarf-pickles/*.dat')[:]
    spectra = [[readtxtfile(s)[:,:2],s] for s in spectrafiles]

    
    import pickle
    f = open('picklespectra','w')
    m = pickle.Pickler(f)
    pickle.dump(spectra,m)
    f.close()




def applyFilter():

    spectrafiles = glob.glob('dwarf-pickles/*.dat')[:]
    spectra = [[readtxtfile(s)[:,:2],s] for s in spectrafiles]


    filters = get_filters()
    
    nspectra = len(spectra)
        
    ''' interpolate only on the filter '''

    spec_mags = []

    for spec,name in spectra:
        star = {'name':name} 
        for filterSpline, step, filt_name in filters:
            specStep = spec[1,0] - spec[0,0] # wavelength increment                   
            resampFilter = filterSpline(spec[:,0]) # define an interpolating function
            val =    sum(specStep * resampFilter * spec[:,1])
            logEff = scipy.log10(val)
            logNorm = scipy.log10(sum(resampFilter*c*specStep/spec[:,0]**2))
            mag = 2.5*(logNorm - logEff) # to calculated an AB magnitude
            star[filt_name] = mag
        spec_mags.append(star)

    import pickle
    f = open('picklelocus_MACS','w')
    m = pickle.Pickler(f)
    pickle.dump(spec_mags,m)
    f.close()
        
    return spec_mags

def synth(p,spectra,filters,show=False):

    #polyfunc = lambda x: abs(1. + p[2]*x + p[3]*x**2.) #+ p[5]*x**3.)

    mags ={} 
    import scipy

    for filterSpline, step, filt_name in filters:
        specall = scipy.zeros(len(spectra[0][0][:,1]))
        val = 0 
        for coeff,specfull  in [[p[0],spectra[0]]]: #,[p[1],spectra[1]],[1.-p[0]-p[1],spectra[2]]]: 
            spec = specfull[0]
            print spec
            specStep = spec[1:,0] - spec[0:-1,0] # wavelength increment                   
            print specStep[400:600], 'specStep'
            resampFilter = filterSpline(spec[:,0]) # define an interpolating function

            print resampFilter
            print filt_name
            import pylab, string

            if False: #string.find(filt_name,'SDSS') != -1:
                pylab.plot(spec[:,0],resampFilter) 
                pylab.show()
            ''' need to multiply by polynomial '''
            #polyterm = polyfunc(spec[:,0]) # define an interpolating function
            #specall = polyterm * spec[:,1]
            val += abs(coeff)*sum(specStep * resampFilter[:-1] * spec[:-1,1])

        logEff = scipy.log10(val)                                        
        logNorm = scipy.log10(sum(resampFilter[:-1]*c*specStep/spec[:-1,0]**2))
        mag = 2.5*(logNorm - logEff) # to calculated an AB magnitude
        import string
        if False: #string.find(filt_name,'SDSS') != -1:
            print mag, val, filt_name, resampFilter, spec[:,1]
    
        mags[filt_name]=mag

    import pylab
    if show:
        pylab.plot(spec[:,0], specall)
        pylab.show()
    return mags

def errfunc(p,spectra,locus_list,locus_index,comp_list,filters):
    star_stats = []

    mags = synth(p,spectra,filters) 
    stat = 0                 
    #print mags, 'mags'
    for combo in comp_list:
        import re
        res = re.split('\_',combo)
        f1 = res[0]
        f2 = res[1]
        #print mags[f1]-mags[f2], locus_list[combo][locus_index], f1, f2
        stat += ((mags[f1]-mags[f2]) - locus_list[combo][locus_index])**2.
    from copy import copy

    stat = stat**0.5

    print 'stat', stat, 'p', p

    return stat

def closest_pickles(stars, locus_list, locus_index, comp_list):
    star_stats = []                                                                                          
    for s in range(len(stars)):
        stat = 0                 
        for combo in comp_list:
            import re
            res = re.split('\_',combo)
            f1 = res[0]
            f2 = res[1]
            stat += ((stars[s][f1]-stars[s][f2]) - locus_list[combo][locus_index])**2.
        from copy import copy
        star_stats.append([stat,copy(s)])
                                                                                                          
    star_stats.sort()
                                                                                                          
    print [x for x  in star_stats[:3]]

    return star_stats




def plot():
   
    spectra_complete = load_spectra() 

    filters = get_filters(False)
    print filters

    import pickle
    f = open('picklelocus_MACS','r')
    m = pickle.Unpickler(f)
    stars = m.load()
    locus_list = locus()
    import string        
    comp_list =  filter(lambda x: string.find(x.replace('SDSS_',''),'SDSS')!=-1 and string.find(x,'SDSS_')!=-1, locus_list.keys())

    import string

    print locus_list.keys()


    close_locus = []


    if 0:
        fit_mags = []                                                                                             
                                                                                                                  
        for i in 5 * scipy.array(range(len(locus_list[comp_list[0]])/5)): #[0:20]:
            star_stats = []
            for s in range(len(stars)):
                stat = 0                 
                for combo in comp_list:
                    import re
                    res = re.split('\_',combo)
                    f1 = res[0]
                    f2 = res[1]
                    stat += ((stars[s][f1]-stars[s][f2]) - locus_list[combo][i])**2.
                from copy import copy
                star_stats.append([stat,copy(s)])
                                                                                                                  
            star_stats.sort()
                                                                                                                  
            print [x for x  in star_stats[:3]]
                                                                                                                  
            spectra_sub = [spectra_complete[x[1]] for x in star_stats[:4]]
                                                                                                                  
            if True:
                                                                                                                  
                mags = synth([1,0,0,0],spectra_sub,filters)
                for combo in comp_list:                                                                        
                    import re
                    res = re.split('\_',combo)
                    f1 = res[0]
                    f2 = res[1]
                    print mags[f1] - mags[f2], locus_list[combo][star_stats[0][1]], f1, f2
                                                                                                                  
                                                                                                                  
            close_locus.append(star_stats[0][1])
            close_locus.append(star_stats[1][1])
            #close_locus.append(star_stats[2][1])
                                                                                                                  
                                                                                                                  
            print spectra_sub
           
            from scipy import optimize
            pinit = [1,0,0,0] #,1] #,1,1,1,1]
            locus_index = i
            out = scipy.optimize.fmin(errfunc,pinit,xtol=0.005,ftol=0.001,args=(spectra_sub,locus_list,locus_index,comp_list,filters)) 
            #mags = errfunc([1,1,1,1,1,1,1,1],spectra_complete[0:3],filters)  
                                                                                                                  
            print   out  
            mags = synth(out,spectra_sub,filters,show=False) 
            print mags
            from copy import copy            
            fit_mags.append([mags,out,spectra_sub,copy(i)])

   
        #print fit_mags              
                                     
        import pickle
        f = open('maglocus','w')
        m = pickle.Pickler(f)
        pickle.dump(fit_mags,m)

    import pickle
    f = open('maglocus_SYNTH','r')
    m = pickle.Unpickler(f)
    fit_mags = m.load()

    
    import pickle 
    f = open('newlocus_SYNTH','r')
    m = pickle.Unpickler(f)
    locus_list_new = m.load()

    synth_locus = {}

    for key in locus_list_new.keys():
        s = key.split('_')
        if len(s) == 2:
            mag1, mag2 = s                                         
            list = []
            for i in range(len(fit_mags)):
                list.append(fit_mags[i][mag1] - fit_mags[i][mag2])
                                                                   
            synth_locus[key] = list 

    print synth_locus

    
    import pickle
    f = open('synthlocus','w')
    m = pickle.Pickler(f)
    pickle.dump(synth_locus,m)

            








    print comp_list

    import pylab
    pylab.clf()

    c1 = []
    c2 = []
    print close_locus
    for i in range(len(stars)):
        print len(stars)
        c1.append(stars[i]['GSDSS']-stars[i]['RSDSS'])
        c2.append(stars[i]['RSDSS']-stars[i]['ISDSS'])
    print c1, c2
    import string

    pylab.scatter(c1,c2,color='green')
    
    pylab.scatter(locus_list['GSDSS_RSDSS'], locus_list['RSDSS_ISDSS'])

    c1 = []
    c2 = []
    print close_locus
    for i in close_locus:
        print len(stars)
        c1.append(stars[i]['GSDSS']-stars[i]['RSDSS'])
        c2.append(stars[i]['RSDSS']-stars[i]['ISDSS'])
    print c1, c2
    import string

    c1 = []
    c2 = []
    print close_locus
    for i in range(len(fit_mags)):
        print len(stars)
        c1.append(fit_mags[i]['GSDSS']-fit_mags[i]['RSDSS'])
        c2.append(fit_mags[i]['RSDSS']-fit_mags[i]['ISDSS'])

        #c1.append(fit_mags[i]['RSDSS']-fit_mags[i]['CAPAKIS'])
        #c2.append(fit_mags[i]['RSDSS']-fit_mags[i]['WSISUBARU'])


    print c1, c2
    import string


    pylab.scatter(c1,c2,color='red')

    pylab.show()

    

def warp():
    
    mod_func = lambda x: p[0] + p[1]*x + p[2]*x**2. + p[3]*x**3. 


