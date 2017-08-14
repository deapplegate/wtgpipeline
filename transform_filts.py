import re, scipy 
import scipy.interpolate.interpolate as interp
c = 299792458e10 #Angstroms/s

def load_spectra():
    import pickle
    f = open('picklespectra','r')
    m = pickle.Unpickler(f)
    spectra = m.load()
    
    return spectra

def readtxtfile(file):
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


def locus():
    import os, re
    f = open('locus.txt','r').readlines()
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
    print colors.keys() 
    import pylab
    #pylab.scatter(colors['ISDSS_ZSDSS'],colors['ZSDSS_JTMASS'])       
    #pylab.show()

    import pickle 
    f = open('newlocus','w')
    m = pickle.Pickler(f)
    locus = colors
    pickle.dump(locus,m)
    f.close() 

    return colors


def get_spectra():
    spectrafiles = glob.glob('dwarf-pickles/*.dat')[:]
    spectra = [[readtxtfile(s)[:,:2],s] for s in spectrafiles]
    import pickle
    f = open('picklespectra','w')
    m = pickle.Pickler(f)
    pickle.dump(spectra,m)
    f.close()

def get_filters(sdss=False):

    flist = [['USDSS','SDSS-u.res'],['GSDSS','SDSS-g.res'],['RSDSS','SDSS-r.res'],['ISDSS','SDSS-i.res'],['ZSDSS','SDSS-z.res']]
    flist += [['UT2KA','t2ka-kpno-u.res'],['GT2KA','t2ka-kpno-g.res'],['RT2KA','t2ka-kpno-r.res'],['IT2KA','t2ka-kpno-i.res'],['ZT2KA','t2ka-kpno-z.res']]
    flist += [['UT2KB','t2kb-kpno-u.res'],['GT2KB','t2kb-kpno-g.res'],['RT2KB','t2kb-kpno-r.res'],['IT2KB','t2kb-kpno-i.res'],['ZT2KB','t2kb-kpno-z.res']]
    flist += [['JTMASS','JTMASS.res']]

    filters = []
    for name, filt_name in flist:
        file = './kpno/' + filt_name #'/a/wain010/g.ki.ki04/pkelly/bpz-1.99.2/FILTER/' + filt_name
        filt = readtxtfile(file)
        import pylab
        #pylab.plot(filt[:,0],filt[:,1])
        #pylab.show()
        step = filt[1,0] - filt[0,0]
        from copy import copy
        filterSpline = interp.interp1d(filt[:,0], filt[:,1], 
                                       bounds_error = False, 
                                       fill_value = 0.)
        filters.append([copy(filterSpline),copy(step),copy(name)])
    return filters

def applyFilter():
    filters = get_filters()
    spectra = load_spectra()
    nspectra = len(spectra)
    ''' interpolate only on the filter '''
    spec_mags = []
    import scipy
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
    f = open('picklelocus','w')
    m = pickle.Pickler(f)
    pickle.dump(spec_mags,m)
    f.close()
    return spec_mags

def part_fit(x,y):
    polycoeffs = scipy.polyfit(x,y,1)   
    print polycoeffs
    yfit = scipy.polyval(polycoeffs, x)
    return yfit.tolist(), polycoeffs

def apply_kit(x,kit):
    x = scipy.array(x)
    y_out = []
    for i in x:
        for k in kit:                       
            if k[0](i):
                func = k[1]                    
                y_out.append(func([i])[0])
                break
    return scipy.array(y_out)
        
                

def fit(x_all, y_all, breaks, plot=0):
    import scipy, pylab
    kit = [] 
    if len(breaks) == 1:
        y1 = y_all[x_all<breaks[0]]
        x1 = x_all[x_all<breaks[0]]
        yfit1, polycoeffs1 = part_fit(x1,y1)
        kit.append([lambda x: x < breaks[0],lambda x: scipy.polyval(polycoeffs1,x)])
        y2 = y_all[x_all>breaks[0]]
        x2 = x_all[x_all>breaks[0]]
        yfit2, polycoeffs2 = part_fit(x2,y2)
        print x1, x2
        x = x1.tolist() + x2.tolist()
        yfit = yfit1 + yfit2
        kit.append([lambda x: x > breaks[0],lambda x: scipy.polyval(polycoeffs2,x)])
        print len(yfit1), len(yfit2), len(yfit)
        if plot:
            pylab.clf()
            pylab.plot(x1,yfit1)              
            pylab.plot(x2,yfit2)
            y = apply_kit(x_all,kit)
            pylab.scatter(x_all,y,c='yellow')
            pylab.show()

    elif len(breaks) == 2:
        y1 = y_all[x_all<breaks[0]]
        x1 = x_all[x_all<breaks[0]]
        yfit1, polycoeffs1 = part_fit(x1,y1)
        kit.append([lambda x: x < breaks[0], lambda x: scipy.polyval(polycoeffs1,x)])
        y2 = y_all[x_all>breaks[0]]
        x2 = x_all[x_all>breaks[0]]
        y2 = y2[x2<breaks[1]]
        x2 = x2[x2<breaks[1]]
        yfit2, polycoeffs2 = part_fit(x2,y2)
        kit.append([lambda x: (breaks[0] < x) *  (x < breaks[1]), lambda x: scipy.polyval(polycoeffs2,x)])
        y3 = y_all[x_all>breaks[1]]
        x3 = x_all[x_all>breaks[1]]
        yfit3, polycoeffs3 = part_fit(x3,y3)
        kit.append([lambda x: breaks[1] < x, lambda x: scipy.polyval(polycoeffs3,x)])
        yfit = yfit1 + yfit2 + yfit3
        x = x1.tolist() + x2.tolist() + x3.tolist()
        if plot:
            pylab.clf()
            pylab.plot(x1,yfit1)              
            pylab.plot(x2,yfit2)
            pylab.plot(x3,yfit3)
            y = apply_kit(x_all,kit)
            pylab.scatter(x_all,y,c='yellow')
            pylab.show()

    elif len(breaks) == 0:
        yfit, polycoeffs = part_fit(x_all,y_all)
        x = x_all
        kit.append([lambda x: True, lambda x: scipy.polyval(polycoeffs,x)])
        if plot:
            pylab.clf()
            pylab.plot(x,yfit)                
            y = apply_kit(x_all,kit)
            pylab.scatter(x_all,y,c='yellow')
            pylab.title('ONE!!')
            pylab.show()

    return x, yfit, kit

def plot():
    to_fit = [['I','Z',[]],['G','R',[]],['G','Z',[]],['G','I',[1.75]],['R','I',[]],['U','G',[0.9,2.3]],['R','Z',[0.4]]]
    TMASS_fit = [['I','JTMASS',[0.3]],['G','JTMASS',[]],['Z','JTMASS',[0.3]],['R','JTMASS',[1.2]]]

    spec_mags = applyFilter()
    import pylab
    stars = len(spec_mags[:])

    locus = get_locus()

    kpno_locus = {}

    for det in ['T2KA','T2KB']:
        for c in to_fit: 
            color1 = scipy.array([spec_mags[x][c[0] + 'SDSS'] for x in range(stars)])-scipy.array([spec_mags[x][c[1] + 'SDSS'] for x in range(stars)]) 
            color2 = scipy.array([spec_mags[x][c[0] + det] for x in range(stars)])-scipy.array([spec_mags[x][c[1] + det] for x in range(stars)])
            pylab.scatter(color1,color2 - color1)
            x, yfit, kit = fit(color1,color2 - color1,c[2])
            kpno_locus[c[0] + det + '_' + c[1] + det] = locus[c[0] + 'SDSS_' + c[1] + 'SDSS'] + apply_kit(locus[c[0] + 'SDSS_' + c[1] + 'SDSS'],kit)
        for c in TMASS_fit: 
            color1 = scipy.array([spec_mags[x][c[0] + 'SDSS'] for x in range(stars)])-scipy.array([spec_mags[x]['JTMASS'] for x in range(stars)]) 
            color2 = scipy.array([spec_mags[x][c[0] + det] for x in range(stars)])-scipy.array([spec_mags[x]['JTMASS'] for x in range(stars)])
            pylab.scatter(color1,color2 - color1)
            x, yfit, kit = fit(color1,color2-color1,c[2])
            kpno_locus[c[0] + det + '_JTMASS' ] = locus[c[0] + 'SDSS_JTMASS'] + apply_kit(locus[c[0] + 'SDSS_JTMASS'],kit)

    import pickle
    f = open('kpnolocus','w')
    m = pickle.Pickler(f)
    pickle.dump(kpno_locus,m)
    f.close()

def get_locus(): 
    import pickle, string
    f = open('newlocus','r')
    m = pickle.Unpickler(f)
    locus = m.load()
    comp_list =  filter(lambda x: string.find(x.replace('SDSS_',''),'SDSS')!=-1 and string.find(x,'SDSS_')!=-1, locus.keys())
    comp_list +=  filter(lambda x: string.find(x,'SDSS')!=-1 and string.find(x,'JTMASS')!=-1, locus.keys())
    print comp_list
    return locus

def get_kpno_locus(): 
    import pickle, string
    f = open('kpnolocus','r')
    m = pickle.Unpickler(f)
    locus = m.load()
    return locus

def plot_locus():
    to_fit = [['G','R',[]],['G','Z',[]],['G','I',[1.75]],['R','I',[]],['U','G',[0.9,2.3]],['R','Z',[0.4]]]
    TMASS_fit = [['I','JTMASS',[0.3]],['G','JTMASS',[]],['Z','JTMASS',[0.3]],['R','JTMASS',[1.2]]]

    spec_mags = applyFilter()
    import pylab
    stars = len(spec_mags[:])

    locus = get_locus()
    kpno_locus = get_kpno_locus()
    print kpno_locus.keys()

    print kpno_locus['GT2KA_RT2KA'] - kpno_locus['GT2KB_RT2KB']


    cs = [['U','G','G','R'],['G','R','R','I'],['G','R','I','Z'],['R','I','I','Z']]
    for c in cs: 
        pylab.clf()
        print c[0] + 'SDSS_' + c[1] + 'SDSS'
        pylab.scatter(locus[c[0] + 'SDSS_' + c[1] + 'SDSS'], locus[c[2] + 'SDSS_' + c[3] + 'SDSS'],c='red')
        for det in ['T2KA','T2KB']:
            pylab.scatter(kpno_locus[c[0] + det + '_' + c[1] + det], kpno_locus[c[2] + det + '_' + c[3] + det],c='blue')
        pylab.xlabel(c[0] + '-' + c[1])
        pylab.ylabel(c[2] + '-' + c[3])
        pylab.title('Stellar Locus ' + det)
        pylab.show()

    c = ['I','Z','Z']
    pylab.clf()
    print c[0] + 'SDSS_JTMASS'
    pylab.scatter(locus[c[0] + 'SDSS_' + c[1] + 'SDSS'], locus[c[2] + 'SDSS_JTMASS'],c='red')
    for det in ['T2KA','T2KB']:
        pylab.scatter(kpno_locus[c[0] + det + '_' + c[1] + det], kpno_locus[c[2] + det + '_JTMASS'],c='blue')
    pylab.xlabel(c[0] + '-' + c[1])
    pylab.ylabel(c[2] + '_JTMASS')
    pylab.title('Stellar Locus ' + det)
    pylab.show()
