
set = 'CWWSB_capak'

def load_probs():
	import scipy
	P = scipy.loadtxt('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_aper/COSMOS_PHOTOZ.APER.1.' + set + '.list.all.probs')

	return P


def run(P):

	import astropy.io.fits as pyfits, os, scipy, pylab
        
        web = os.environ['sne'] + '/photoz/COSMOS_' + set + '/'

	comp = open(web + '/comp.html','w')
        os.system('mkdir -p ' + web)
        
        print 'loading cosmos'
        C = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_aper/cosmos_lephare.cat')['OBJECTS'].data
        print 'loading BPZ'
        U = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_aper/COSMOS_PHOTOZ.APER.1.' + set + '.list.all.bpz.tab')['STDTAB'].data
        print 'loading PDZ'
        print 'done'
        
        
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


	for low,high in [[0.2,0.3],[0.3,0.4],[0.4,0.5],[0.5,0.6],[0.6,0.7],[0.7,0.8],[0.8,0.9],[0.9,1.0]]:

			
        
       		pylab.clf()                                                                                                               
                out_zs = (U.field('BPZ_Z_B') < high) * (U.field('BPZ_Z_B') > low) * (U.field('BPZ_ODDS') > 0.5) * (C.field('zp_best') > 0)
                cosmos_zs = C.field('zp_best')[out_zs]
                
                multiple=4
                bins = scipy.arange(0,2.,0.01*multiple)
                
                n, bins, patches = pylab.hist(cosmos_zs, bins=bins, histtype='bar')
                
                pylab.clf()
                mask = out_zs[:]
                pdz_zs_raw = P[mask].sum(axis=0)/mask.sum()
                pdz_zs = []
                sum = 0
                for i in range(len(pdz_zs_raw)):		
                	if (i+1) % multiple == 0:
                		pdz_zs.append(sum)
                		sum = 0
                	sum += pdz_zs_raw[i]
                
                print pdz_zs
                
                x = bins[:-1] 
                y = pdz_zs[:len(bins[:-1])]
                y[0] = 0
                print x, y
                y_cosmos = n/float(len(cosmos_zs))
                
                print (y_cosmos)
                
                pylab.bar(x,y_cosmos,width=x[1]-x[0],facecolor='red',linewidth=0, label='COSMOS')
                pylab.bar(x,y,width=x[1]-x[0],facecolor='none',edgecolor='black', label='BPZ')
                
                import scipy, pylab
                zs = scipy.arange(0.01000,4.0100,0.0100)
                
                #pylab.plot([0,1],[0,1],c='red')
                #pylab.xlim([0,1])
                #pylab.ylim([0,1])
                #pylab.title('ALL')
		pylab.legend(frameon=False)			
		pylab.figtext(0.62,0.73,'$' +  str(low) + '< z_B < ' + str(high) + '$',size=15) 
		pylab.figtext(0.62,0.68,str(len(cosmos_zs)) + ' Galaxies',size=15)
                pylab.ylabel('Probability Density')
                pylab.xlabel('Redshift')
		file = str(low) + '_' + str(high) + 'interval.png'
		print web + file
		comp.write('<img src=' + file + '></img>\n')
		
                pylab.savefig(web + file)
                pylab.savefig(web + file.replace('.png','.pdf'))
                pylab.savefig(web + file.replace('.png','.ps'))
                #pdz.write('<img width=600px src=all.png></img><br>\n')
	comp.close()                
