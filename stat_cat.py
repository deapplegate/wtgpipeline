def plot_res(file_name,outbase,SPECTRA,type='bpz'):
    import os, sys, anydbm, time
    import lib, scipy, pylab 
    from scipy import arange
   
    print file_name 
    
    file = open(file_name,'r').readlines()
    results = []
    anjaplot = open('anjaplot','w')
    anjaplot.write('# Z_PHOT Z_MIN Z_MAX ODDS Z_SPEC\n')
    
    
    diff = []
    z = []
    z_spec = []
    for line in file:
        if line[0] != '#':
            import re                                     
            res = re.split('\s+',line)
            if res[0] == '': res = res[1:]
            if type is 'bpz':
                anjaplot.write(res[1] + ' ' + res[2] + ' ' + res[3] + ' ' + res[5] + ' ' + res[9] + '\n') 
                if float(res[5]) > 0.95:
                    #for i in range(len(res)):
                    #    print res[i],i
                    #print res
                    if True: #float(res[9]) > 0:
                        results.append([float(res[1]),float(res[9])])
            elif type is 'eazy': 
                results.append([float(res[2]),float(res[1])])

    
    for line in results:                             
        #print line
        diff_val = (line[0] - line[1])/(1 + line[1])
        diff.append(diff_val)
        z.append(line[0])
        z_spec.append(line[1])

    print results    
    anjaplot.close()

    print diff, file_name
    
    list = diff[:]  
    import pylab   
    varps = [] 
    #print diff        
    a, b, varp = pylab.hist(diff,bins=arange(-0.2,0.2,0.016),color='blue',edgecolor='black')
    #print a,b,varp
    varps.append(varp[0])
    
    diffB = []
    for d in diff:
        if abs(d) < 0.1:
            diffB.append(d)
    diff = diffB
    list = scipy.array(diff)
    mu = list.mean()
    sigma = list.std()
    
    #print 'mu', mu
    #print 'sigma', sigma
    
    from scipy import stats
    pdf = scipy.stats.norm.pdf(b, mu, sigma)
    #print 'pdf', pdf
    
    height = scipy.array(a).max()
    
    pylab.plot(b,len(diff)*pdf/pdf.sum(),color='red')

    print b,len(diff)*pdf/pdf.sum()
    
    pylab.xlabel("(PhotZ - SpecZ)/(1 + SpecZ)")
    pylab.ylabel("Number of Galaxies")
    pylab.title(['mu ' + str(mu),'sigma ' + str(sigma)])
    print outbase
    os.system('mkdir -p ' + outbase)
    pylab.savefig(outbase + '/' + SPECTRA + 'RedshiftErrors.png')
    #pylab.show()

    #save_db(cluster,{'mu':mu,'sigma':sigma})

    pylab.clf()


    
    pylab.scatter(z_spec,z)
    pylab.plot(scipy.array([0,4]),scipy.array([0,4]),color='red')
    pylab.xlim(0,4)
    pylab.ylim(0,4)
    pylab.ylabel("PhotZ")
    pylab.xlabel("SpecZ")
    pylab.savefig(outbase + '/' + SPECTRA + 'RedshiftScatter04.png')

    pylab.clf()

    pylab.scatter(z_spec,z)
    pylab.plot(scipy.array([0,1]),scipy.array([0,1]),color='red')
    pylab.xlim(0,1)
    pylab.ylim(0,1)
    pylab.ylabel("PhotZ")
    pylab.xlabel("SpecZ")
    pylab.savefig(outbase + '/' + SPECTRA + 'RedshiftScatter01.png')

    #pylab.show()
    pylab.clf()
    print outbase + '/RedshiftScatter01.png'

def run():

    import os, pyfits, pylab, scipy
    cluster = 'MACS0717+37'
    
    base = os.environ['sne'] + '/photoz/compare/'
    
    os.system('mkdir -p ' + base)
    file = open(base + '/index.html','w')
    file.write('<table><tr><td colspan=2 style="border:solid 2px red" align=center valign=center><h1>' + cluster + ' Photo-Z Filter Test: uBVRIz</h1></td></tr>\n')
    
    list = [['all',''],['no U','_u'],['no U no Z','_uz'],['no U no B','_ub']]
    for cut, suffix in list:
    
        specfile= os.environ['subdir'] + '/' + cluster + '/PHOTOMETRY_W-J-V/' + cluster + '.APER1.CWWSB_capak' + suffix + '.list.1.spec.bpz'
    
        print specfile
        plot_res(specfile,base,suffix)
    
    
    for cut, suffix in list:
    
        catfile= os.environ['subdir'] + '/' + cluster + '/PHOTOMETRY_W-J-V/' + cluster + '.APER1.1.CWWSB_capak' + suffix + '.list.all.bpz.tab'
        print catfile
    
    
    
        print pyfits.open(catfile)[1].columns
        p = pyfits.open(catfile)[1].data
        original = len(p)# ,'original'
        mask = p.field('BPZ_ODDS') > 0.95
        filt = p[mask]
        print len(filt), suffix
    
        _, _, varp = pylab.hist(filt.field('BPZ_Z_B'),bins=scipy.arange(0.0,3,0.1))
        pylab.title( cut + '     BPZ_ODDS>0.95=' + str(len(filt)) + '    FULL CATALOG=' + str(original))
        pylab.xlabel('z',fontsize='x-large')
        pylab.ylabel('Galaxies',fontsize='x-large')
    
        plot = 'run' + suffix + '.png'
        pylab.savefig(base + '/' + plot)
    
        file.write('<tr><td ><img width=400px src=' + plot + '></td>\n')
        file.write('<td ><img width=400px src=' + suffix + 'RedshiftScatter01.png></td></tr>\n')
        file.write('<tr><td ><img width=400px src=' + suffix + 'RedshiftScatter04.png></td></tr>\n')
    
        #pylab.show()

def comp():
    
    import os, pyfits, sys, pylab

    list = [[['no U','_u'],['no U no B','_ub']]]
    for [cut1, suffix1],[cut2,suffix2] in list:

        catfile1= os.environ['subdir'] + '/' + cluster + '/PHOTOMETRY_W-J-V/' + cluster + '.APER1.1.CWWSB_capak' + suffix1 + '.list.all.bpz.tab'
    
        p1 = pyfits.open(catfile1)[1].data
        original = len(p1)# ,'original'
        mask = p1.field('BPZ_ODDS') > 0.5
        filt1 = p1[mask]

        catfile2= os.environ['subdir'] + '/' + cluster + '/PHOTOMETRY_W-J-V/' + cluster + '.APER1.1.CWWSB_capak' + suffix2 + '.list.all.bpz.tab'
    
    
        
        p2 = pyfits.open(catfile2)[1].data
        original = len(p2)# ,'original'
        mask = p1.field('BPZ_ODDS') > 0.5
        filt2 = p2[mask]
    
    
        import pylab

        pylab.clf()
        pylab.scatter(filt1.field('BPZ_Z_B'),filt2.field('BPZ_Z_B'))
        pylab.ylabel(cut2)
        pylab.xlabel(cut1)
        pylab.xlim([0,2])
        pylab.ylim([0,2])
    
   
        pylab.savefig('comp50.pdf')
        pylab.show()
