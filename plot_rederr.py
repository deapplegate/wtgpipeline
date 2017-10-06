def twodhist(xs,ys,fname):        

    import scipy

    xbins = scipy.arange(0,1.5,0.0225)
    ybins = scipy.arange(0,1.5,0.0225)
    
    prob_matrix,X,Y = scipy.histogram2d(ys,xs,bins=[xbins,ybins])
    
    prob_matrix = prob_matrix / prob_matrix.max()
    
    import pylab
    #X, Y = pylab.meshgrid(zs_copy,zs_copy)
                                                                                              
    print prob_matrix.shape, X.shape, Y.shape
                                                                                              
                                                                                              
    
    
    import pylab
    
    pylab.rcdefaults()
    params = {'backend' : 'ps',
         'text.usetex' : True,
          'ps.usedistiller' : 'xpdf',
          'ps.distiller.res' : 6000}
    pylab.rcParams.update(params)
                                           
    
    fig_size = [8,8]
                                           
    
    params = {'axes.labelsize' : 20,
              'text.fontsize' : 22,
              'legend.fontsize' : 22,
              'xtick.labelsize' : 20,
              'ytick.labelsize' : 20,
              'scatter.s' : 0.1,
                'scatter.marker': 'o',
              'figure.figsize' : fig_size}
    pylab.rcParams.update(params)
    
    
    pylab.clf()
    
    
    print prob_matrix.max()
                                                                                              
    prob_matrix[prob_matrix>1] =1. 
    
    
    #pylab.axes([0.125,0.125,0.95-0.125,0.95-0.125])
    #pylab.axes([0.125,0.25,0.95-0.125,0.95-0.25])
    
    
    
    pylab.axes([0.125,0.15,0.95-0.125,0.95-0.15])
    #pylab.axes([0.225,0.15,0.95-0.225,0.95-0.15])
    pylab.axis([0,1.5,0,1.5])
    
    pylab.pcolor(X, Y,-1.*prob_matrix,cmap='gray',alpha=0.9,shading='flat',edgecolors='None')
    
    pylab.axhline(y=1.2,color='black')                                                                                          
    pylab.plot(scipy.array([0,2]),scipy.array([0,2]),color='black')

    pylab.figtext(0.16,0.89,'HDFN',fontsize=20)
    
    pylab.xlabel('Spectroscopic z')
    pylab.ylabel('Photometric z')
    #pylab.plot([0,1],[0,1],color='red')
    #pylab.xlabel('SpecZ')
    #pylab.ylabel('PhotZ')
    
    
    pylab.savefig(fname) #,figsize=fig_size)


def plot_residuals(cluster, detect_band, base='/nfs/slac/g/ki/ki04/pkelly/photoz/',SPECTRA='CWWSB_capak.list',photoz_code='BPZ'): #,outbase,SPECTRA,type='bpz'):

    outbase = base + cluster + '/'

    import os
    subarudir = os.environ['subdir'] + '/'

    photdir = subarudir + cluster + '/PHOTOMETRY_' + detect_band + '_aper/'

    mergecat = photdir + cluster + '.matched.tab'

    papbase = base + 'papfigs/' 

    os.system('mkdir -p ' + papbase)

    import os, sys, anydbm, time
    import lib, scipy, pylab , pyfits
    from scipy import arange
   
    print mergecat 

    t = pyfits.open(mergecat)['STDTAB'].data
    
    zspec = t['z_spec']

    if photoz_code=='BPZ':
        zphot = t['BPZ_Z_B_data'] 
        odds = t['BPZ_ODDS_data']
        NFILT = t['NFILT_data']
        mag = t['BPZ_M_0_data']

    elif photoz_code=='EAZY':
        zphot = t['EAZY_z_p_data']
        odds = t['EAZY_odds_data']
        NFILT = t['EAZY_nfilt_data']

    diff = [] 
    z = []
    z_spec = []
    
    for i in range(len(zspec)):                             
        #print line
        if NFILT[i]>=4 and odds[i] > 0.9: # and mag[i] > 23:
            diff_val = (zphot[i] - zspec[i])/(1 + zspec[i])
            diff.append(diff_val)
            z.append(zphot[i])
            z_spec.append(zspec[i])


    if False:
        z_phot_array = scipy.array(z)                                                     
        z_spec_array = scipy.array(z_spec)
                                                                                          
        upper_lim = 1.0
        lower_lim = 0.8 
        out_zs = (z_phot < upper_lim) * (z_phot > lower_lim) 
                                                                                          
        phots = z_phot_array[out_zs]
        specs = z_spec_array[out_zs]
                                                                                          
        bins = scipy.arange(0,2.,0.01*multiple)
        n, bins, patches = pylab.hist(cosmos_zs, bins=bins, histtype='bar')
                                                                                          
        pylab.bar(x,y_cosmos,width=x[1]-x[0],facecolor='red',linewidth=0, label='COSMOS')
        pylab.bar(x,y,width=x[1]-x[0],facecolor='none',edgecolor='black', label='BPZ')


    #print results    

    
    list = diff[:]  
    import pylab   

    params = {'backend' : 'ps',
         'text.usetex' : True,
          'ps.usedistiller' : 'xpdf',
          'ps.distiller.res' : 6000}
    pylab.rcParams.update(params)

    if cluster == 'HDFN':
        fig_size = [8.5,8.5]
    else:
        fig_size = [8.5,3]

    params = {'axes.labelsize' : 20,
              'text.fontsize' : 22,
              'legend.fontsize' : 22,
              'xtick.labelsize' : 20,
              'ytick.labelsize' : 20,
              'scatter.s' : 0.1,
                'scatter.marker': 'o',
              'figure.figsize' : fig_size}
    pylab.rcParams.update(params)

    varps = [] 
    #print diff        

    
    if cluster == 'HDFN':
        pylab.axes([0.125,0.15,0.95-0.125,0.95-0.15])
    else:
        pylab.axes([0.125,0.25,0.95-0.125,0.95-0.25])



    #pylab.axis([0,1,0,1])

    print diff

    a, b, varp = pylab.hist(diff,bins=arange(-0.2,0.2,0.015),color='blue',edgecolor='black')
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
    pdf_x = arange(-0.2,0.2,0.005)
    pdf = scipy.stats.norm.pdf(pdf_x, mu, sigma)
    #print 'pdf', pdf
    
    height = scipy.array(a).max()
    
    pylab.plot(pdf_x,3*len(diff)*pdf/pdf.sum(),color='red')

    print b,len(diff)*pdf/pdf.sum()
    
    pylab.xlabel(r"(z$_{phot}$ - z$_{spec}$)/(1 + z$_{spec}$)")
    pylab.ylabel("Galaxies")

    if cluster == 'HDFN':
        pylab.figtext(0.76,0.89,'$\mu_{\Delta z}$=%.3f' % mu, fontsize=20)
        pylab.figtext(0.76,0.85,'$\sigma_{\Delta z}$=%.3f' % sigma, fontsize=20)
    else:
        pylab.figtext(0.76,0.82,'$\mu_{\Delta z}$=%.3f' % mu, fontsize=20)
        pylab.figtext(0.76,0.73,'$\sigma_{\Delta z}$=%.3f' % sigma, fontsize=20)
    #pylab.title(['mu ' + str(mu),'sigma ' + str(sigma)])
    
    os.system('mkdir -p ' + outbase + '/' + SPECTRA)


    file = open(outbase + '/' + SPECTRA + '/redshifterrors.html','w')

    file.write('<h1>Spectroscopic vs. Photometric Redshifts</h1><br>')    

    from datetime import datetime
    t2 = datetime.now()

    file.write('<br><h3>' + t2.strftime("%Y-%m-%d %H:%M:%S") + '</h3><br><br><img src="RedshiftErrors.png"></img>') 


    
    file.write('<br><img src="RedshiftScatter01.png"></img>\n')
    file.write('<br><img src="RedshiftScatter02.png"></img>\n')

    file.close()

    if cluster == 'HDFN':
        pylab.figtext(0.16,0.89,cluster,fontsize=20)
    else:
        pylab.figtext(0.16,0.79,cluster,fontsize=20)
    pylab.savefig(outbase + '/' + SPECTRA + '/RedshiftErrors.png')
    pylab.savefig(papbase + '/' + cluster + 'RedshiftErrors.ps')
    pylab.savefig(papbase + '/' + cluster + 'RedshiftErrors.pdf')

    print papbase + '/' + cluster + 'RedshiftErrors.pdf'

    #save_db(cluster,{'mu':mu,'sigma':sigma})

    pylab.clf()
    
    if cluster == 'HDFN':
        pylab.axes([0.125,0.15,0.95-0.125,0.95-0.15])
    else:
        pylab.axes([0.125,0.25,0.95-0.125,0.95-0.25])

    pylab.axis([0,2,0,2])
    pylab.scatter(z_spec,z,linewidth=0,s=3, marker='o',c='black')
    pylab.plot(scipy.array([0,2]),scipy.array([0,2]),color='black')
    pylab.ylabel("Photometric z")
    pylab.xlabel("Spectroscopic z")
    if cluster == 'HDFN':
        pylab.figtext(0.16,0.89,cluster,fontsize=20)
    else:
        pylab.figtext(0.16,0.79,cluster,fontsize=20)

    pylab.savefig(outbase + '/' + SPECTRA + '/RedshiftScatter02.png')
    pylab.savefig(papbase + '/' + cluster + 'RedshiftScatter02.ps')
    pylab.savefig(papbase + '/' + cluster + 'RedshiftScatter02.pdf')

    pylab.clf()

    if cluster == 'HDFN':
        pylab.axes([0.125,0.15,0.95-0.125,0.95-0.15])
    else:
        pylab.axes([0.125,0.25,0.95-0.125,0.95-0.25])

    pylab.axis([0,1.5,0,1.5])

    pylab.scatter(z_spec,z,linewidth=0,s=3, marker='o',c='black')
    pylab.plot(scipy.array([0,3]),scipy.array([0,3]),color='black')


    pylab.ylabel("Photometric z")
    pylab.xlabel("Spectroscopic z")
    if cluster == 'HDFN':
        pylab.figtext(0.16,0.89,cluster,fontsize=20)
    else:
        pylab.figtext(0.16,0.79,cluster,fontsize=20)

    pylab.savefig(outbase + '/' + SPECTRA + '/RedshiftScatter01.png')
    pylab.savefig(papbase + '/' + cluster + 'RedshiftScatter01.ps')
    pylab.savefig(papbase + '/' + cluster + 'RedshiftScatter01.pdf')


    print papbase + '/' + cluster 

    fname = papbase + '/' + cluster + '2dhist.pdf'
    twodhist(z_spec,z,fname )


    p = open(papbase + '/' + cluster + '_galaxies','w')
    p.write('galaxies ' + str(len(z_spec)) )
    p.close()

    import MySQLdb

    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-sr01')
    c = db2.cursor()
    
    commandst = 'update clusters_db set specmatches=' + str(len(z_spec)) + ' where objname="' + cluster + '"' 
    c.execute(commandst)                                             

    #pylab.show()
    pylab.clf()

def join_cats(cs,outputfile):
    import astropy.io.fits as pyfits
    tables = {}
    i = 0
    cols = []
    seqnr = 0 
    for c in cs:
        print c
        if len(c) > 1:
            TAB = c[1]
            c = c[0]
        else: TAB = 'STDTAB'
        i += 1
        print c
        tables[str(i)] = pyfits.open(c)
        for column in  tables[str(i)][TAB].columns:           
            if column.name == 'SeqNr':
                if not seqnr:
                    seqnr += 1
                else:                                            
                    column.name = column.name + '_' + str(seqnr)
                    seqnr += 1

            cols.append(column)

    print cols
    print len(cols)
    hdu = pyfits.PrimaryHDU()
    hduSTDTAB = pyfits.BinTableHDU.from_columns(cols) 
    hdulist = pyfits.HDUList([hdu])
    hduFIELDS = pyfits.open(cs[1][0])['FIELDS']
    hdulist.append(hduFIELDS)
    hdulist.append(hduSTDTAB)
    hdulist[1].header['EXTNAME']='FIELDS'
    hdulist[2].header['EXTNAME']='STDTAB'
    import os
    os.system('rm ' + outputfile)
    print outputfile
    hdulist.writeto(outputfile)







class file_iter:
    def __init__(self,name):
        self.name = name
        self.suffix = 1
        self.file = self.name + str(self.suffix) 
    def next(self):
        self.suffix += 1    
        self.file = self.name + str(self.suffix) 
        return self.file
    def __iter__(self):
        self.file = self.name + str(self.suffix) 



def run():
    from optparse import OptionParser
    usage = "usage: python redsequence [options] \n\nIdentifies and fits the red sequence using apparent magnitude and one color.\nOption of identifying star column and only using objects larger.\n"
    parser = OptionParser(usage)
    parser.add_option("-c", "--cluster", 
                      help="name of cluster (i.e. MACS0717+37)")
    parser.add_option("-d", "--detectband", 
                      help="detection band (i.e. W-J-V)",default='W-J-V')
    parser.add_option("-p", "--photozcode", 
                      help="photoz code",default='BPZ')
    parser.add_option("-s", "--short", 
                      help="short output",action='store_false')

    (options, args) = parser.parse_args()

    photoz_code = options.photozcode        

    short = options.short

    import os

    #os.system('python mk_ldac_spec.py ' + options.cluster + ' ' + options.detectband)

    import mk_ldac_spec
    found = reload(mk_ldac_spec).run(options.cluster, options.detectband)

    print 'found', str(found)

    if found:

        subarudir = '/nfs/slac/g/ki/ki05/anja/SUBARU/'                                                                                                                                                                                                                                             
        import astropy.io.fits as pyfits, os                                                                                                                                                                                                                                                                         
        SPECTRA = 'CWWSB_capak.list'

        #SPECTRA = 'CWWSB4.list'

        photdir = subarudir + options.cluster + '/PHOTOMETRY_' + options.detectband + '_aper/'
        phot_cat = photdir + options.cluster + '.slr.cat' # '.APER1.1.CWWSB_capak.list.all.bpz.tab'

        if short and not photoz_code == 'noz':
            phot_cat = photdir + options.cluster + '.short.cat' # '.APER1.1.CWWSB_capak.list.all.bpz.tab'

        if photoz_code == 'BPZ':
            photoz_cat = photdir + options.cluster + '.APER1.1.' + SPECTRA + '.all.bpz.tab'

        elif photoz_code == 'EAZY':
            photoz_cat = '/tmp/pkelly/OUTPUT/photz.zout.tab'
	elif photoz_code == 'noz': photoz_cat = None
                                                                                                                                                                                                                                                                                                   
        print photoz_cat, phot_cat

                                                                                                                                                                                                                                                                                                   
        cat = photdir + options.cluster + '.merge.cat'
                                                                                                                                                                                                                                                                                                   
        import utilities
        utilities.run("ldacrentab -i " + phot_cat + " -t OBJECTS STDTAB  -o " + phot_cat+'.STDTAB',\
            [phot_cat+'.STDTAB'])
                                                                                                                                                                                                                                                                                                   
        print phot_cat
        #join_cats([[photoz_cat,'STDTAB'],[phot_cat + '.STDTAB','STDTAB']],cat) 
        

	if photoz_code == 'noz':
	    command = 'cp ' + phot_cat + '.STDTAB ' + cat
        elif photoz_code == 'BPZ':
            command = 'ldacjoinkey -i ' + phot_cat + '.STDTAB -o ' + cat + ' -p ' + photoz_cat + ' -k BPZ_Z_B BPZ_ODDS BPZ_M_0 NFILT -t STDTAB'

        elif photoz_code == 'EAZY':
            command = 'ldacjoinkey -i ' + phot_cat + '.STDTAB -o ' + cat + ' -p ' + photoz_cat + ' -k EAZY_z_p EAZY_odds EAZY_nfilt -t STDTAB'
        print command
                                                                                                                                                                                                                                                                                                   
        os.system(command)
                                                                                                                                                                                                                                                                                                   
        matchedcat = photdir + options.cluster + '.matched.tab'
                                                                                                                                                                                                                                                                                                   
        p = pyfits.open(cat)
        photoz = p['STDTAB'].data
        zero_IDs = len(photoz[photoz.field('SeqNr')==0])
        if zero_IDs > 0:
            print 'Wrong photoz catalog?', cat
            print str(zero_IDs) + ' many SeqNr=0' 
            raise Exception
                                                                                                                                                                                                                                                                                                   
        import utilities
                                                                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                                   
        speccat = photdir + options.cluster + 'spec.cat'
        from glob import glob
        if not glob(speccat):
            os.system('cp ' +  subarudir + '/' + options.cluster + '/PHOTOMETRY_' + options.detectband + '/' + options.cluster + 'spec.cat ' + speccat)
                                                                                                                                                                                                                                                                                                   
        print speccat
        specfile = file_iter(speccat+'spec')                                                                                       
        from glob import glob
        if not glob(speccat): 
            print 'NO SPECTRA FILE'
            raise Exception
                                                                                                                                                                                                                                                                                         
        os.system('rm ' + specfile.file[:-1] + '*')
        os.system('cp '+ speccat +' '+specfile.file)
        
        utilities.run("ldacrentab -i " + specfile.file + " -t OBJECTS STDTAB FIELDS NULL -o " + specfile.next(),[specfile.file])
        utilities.run("ldacrenkey -i " + specfile.file  + " -t STDTAB -k Ra ALPHA_J2000 Dec DELTA_J2000 Z z -o " + specfile.next(),[specfile.file])
        utilities.run("ldaccalc -i " + specfile.file + " -t STDTAB -c '(Nr);'  -k LONG -n SeqNr '' -o " + specfile.next(),[specfile.file] )

                                                                                                                                                                                                                                                                                                   
                                                                                                                                   
        print specfile.file
                                                                                                                                   
        #    inputtable = ldac.openObjectFile(cat)

                                                                                                                                   
        if os.environ['USER'] == 'dapple':            
            os.chdir('/a/wain001/g.ki.ki02/dapple/pipeline/bonnpipeline/')
            print os.environ['USER'], os.system('pwd')
            command = "./match_neighbor.sh " + matchedcat + " STDTAB " + specfile.file + " spec " + cat  + " data "                                                                                                                       
        else: 
            os.chdir('/u/ki/pkelly/pipeline/bonnpipeline/')
            print os.environ['USER'], os.system('pwd')


            os.system('rm /tmp/' + os.environ['USER'] + 'combined.cat')                 

            os.system('rm ' + matchedcat)
                                                                                                                                                                                                                                                                                         
            command = "/u/ki/pkelly/pipeline/bonnpipeline//match_neighbor.sh " + matchedcat + " STDTAB " + specfile.file + " spec " + cat +  " data "                                                                                                                       
        print command
        os.system('pwd')
        utilities.run(command, [matchedcat])

                                                                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                                   
        ''' save IDs of matched spectra '''
        matched_seqnr = photdir + 'spec_match_id.list'
        command = 'ldactoasc -i ' + matchedcat + ' -b -t STDTAB -k SeqNr_data z_spec BPZ_ODDS_data >  ' + matched_seqnr 
        utilities.run(command,[matched_seqnr])
                                                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                         
        print matchedcat, specfile.file            
                                                                                                                                   
        import astropy.io.fits as pyfits
                                                                                                                                   
        spectable = pyfits.open(matchedcat)['STDTAB']
        #print "looking at "+varname+'-'+filterlist[0]+'_data'
        print spectable
        print matchedcat
        	
	if photoz_code != 'noz':                                                                                                                                                                                                                                                                                          
	        plot_residuals(options.cluster, options.detectband,photoz_code=photoz_code)

                                                                                                                                                                                                                                                                                                   
        
                                                                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                                   
if __name__ == '__main__':
        run()
