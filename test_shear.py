import astropy, astropy.io.fits as pyfits, os

web = os.environ['sne'] + '/photoz/COSMOS/'

#C = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_APER/cosmos_lephare.cat')['OBJECTS'].data
#U = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_APER/COSMOS_PHOTOZ.APER.1.CWWSB_capak.list.all.bpz.tab')['STDTAB'].data
#P = open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_APER/COSMOS_PHOTOZ.APER.1.CWWSB_capak.list.all.probs').readlines()

def run(C,U,P):
    import pickle
    f = open('DA.pickle','r')
    m = pickle.Unpickler(f)
    dict_DCMR = m.load()
    
    import scipy, pylab, math
    r = scipy.arange(0.8,1.2,0.02)
    masses = dict(zip(r,scipy.zeros(len(r)))) 
    masses_onepoint = dict(zip(r,scipy.zeros(len(r)))) 
    zs = scipy.arange(0.01000,4.0100,0.0100)


    def parse(i,Z, Z_onepoint):

        import scipy 
        from scipy import stats
        an = scipy.stats.norm.rvs() * 0.3
        true_shear = (angdist_ratio(Z) + an) 

        y = scipy.array([float(x) for x in P[i+1][:-1].split(' ')[1:-1]])
        vec = zip(zs,y)
        for m in masses.keys():
            prob= 0
            for v in vec:           
                if v[1] > 0:
                    

                    prob+= v[1] * math.exp(-1.*(m*angdist_ratio(v[0]) - true_shear)**2./0.3**2.)/(2.*math.pi)**0.5 
                    #print true_shear, angdist_ratio(v[0]), v[1], prob, m
                    #raw_input()

            #print prob, m
            masses[m] += math.log(prob)

            masses_onepoint[m] += math.exp(-1.*(m*angdist_ratio(Z_onepoint) - true_shear)**2./0.3**2.)/(2.*math.pi)**0.5
        
    
    import advanced_calc
    cluster_z = 0.5
    WM = 0.27
    w = -1
    d_cluster = advanced_calc.compute(cluster_z,w)
    DS = advanced_calc.compute(0.75,w,WM=WM) #dict_DCMR[]
    norm = (DS - d_cluster)/DS 

    
    def angdist_ratio(z): 
        #d_cluster = dict_DCMR['%.2f' % cluster_z + '_' + '%.2f' % w + '_' + '%.2f' % WM] #advanced_calc.compute(clusterz,w) 
        key = '%.2f' % z + '_' + '%.2f' % w + '_' + '%.2f' % WM 
        if key in dict_DCMR:
            DS = dict_DCMR[key]
        else:
            DS = advanced_calc.compute(z,w,WM=WM) #dict_DCMR[]
            dict_DCMR[key] = DS
        ratio = (DS - d_cluster)/DS 
        if ratio < 0: ratio = 0

        

        return ratio / norm * 0.1

    
    
    CZ = []
    UZ = []
    fracs = []
    vals = []
    num = 0 
    for i in range(40000,60000):
        if i%10: print i
        cosmos_z = C.field('zp_best')[i]
        our_z = U.field('BPZ_Z_B')[i]
        mag = U.field('BPZ_M_0')[i]
        if mag < 25 and U.field('BPZ_ODDS')[i] > 0.5 and our_z > cluster_z + 0.1 and our_z < 1. and cosmos_z > 0 and cosmos_z < 1.5: # and not (0.18 < cosmos_z < 0.025): # and our_z > 0.5:
            num += 1
            CZ.append(cosmos_z)
            UZ.append(our_z)
            frac = parse(i,cosmos_z,our_z)
            fracs.append(frac)
    
            vals.append(angdist_ratio(our_z)/angdist_ratio(cosmos_z))
            #print w, str(float(w)), '%.2f' % z + '_' + '%.2f' % w + '_' + '%.2f' % WM
    
    import pylab
    #pylab.hist(vals,bins=40)
    pylab.scatter(masses_onepoint.keys(),masses.values())
    pylab.title(str(num))
    pylab.show()

    pylab.scatter(masses.keys(),masses.values())
    pylab.title(str(num))
    pylab.show()
