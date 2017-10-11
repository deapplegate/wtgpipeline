
def convert_to_pogson(p):

    import astropy, astropy.io.fits as pyfits, scipy

    cols = []
    for col in p.columns:
        if col.name[0:7] == 'psfFlux':  
            array = -2.5*scipy.log10(p.data.field(col.name)) + 22.5
            cols.append(pyfits.Column(name=col.name.replace('psfFlux','psfPog'), format=col.format, array=array)) 
        cols.append(col)

    hdu = pyfits.PrimaryHDU()                                                  
    hdulist = pyfits.HDUList([hdu])
    print cols
    tbhu = pyfits.BinTableHDU.from_columns(cols)
    #hdulist.append(tbhu)
    #hdulist[1].header['EXTNAME']='STDTAB'
    #outcat = '/tmp/test' #path + 'PHOTOMETRY/' + type + '.cat'                
    #os.system('rm ' + f + '.tab')
    #hdulist.writeto(f + '.tab')

    return tbhu
        



import astropy, astropy.io.fits as pyfits, pylab, scipy

p = pyfits.open('extflux_pkelly50.fit')[1]#[0:20000]

p = convert_to_pogson(p).data

p = p[p.field('extinction_u') < 0.3]

p = p[:200000]

#p2 = pyfits.open('locus_pkelly50.fit')[1]

pylab.close()
pylab.clf()

#for c1,c2,c1_lim,c2_lim in [[['g','i'],['g','r'],[-0.5,3.0],[-0.5,2.0]]]:

#for c1,c2,c1_lim,c2_lim in [[['g','r'],['u','g'],[-0.5,2.0],[-1,5]]]:

loci = {}

for c1,c2,c1_lim,c2_lim in [[['g','i'],['g','z'],[-0.5,4.0],[-0.5,5]],[['g','i'],['r','i'],[-0.5,4.0],[-0.5,4]]]:
    pylab.scatter(p.field('psfPog_' + c1[0])-p.field('psfPog_' + c1[1]),p.field('psfPog_' + c2[0])- p.field('psfPog_' + c2[1]),s=0.001)

    points = []
    incre = 0.1
    for x in scipy.arange(c1_lim[0],c1_lim[1],incre):        
        mask = (x < p.field('psfPog_'+c1[0]) - p.field('psfPog_' + c1[1])) * (x + incre > p.field('psfPog_'+c1[0]) - p.field('psfPog_'+c1[1])) * (19 > p.field('psfPog_r')) # - p.field('psfPog_r')) * (-99 < p.field('psfPog_g') - p.field('psfPog_r'))

        filt = p[mask]
        colors = filt.field('psfPog_' + c2[0]) - filt.field('psfPog_' + c2[1])
        print colors
        points.append([x+incre/2., scipy.median(colors)] )                    
        
    points = scipy.array(points)
    print points

    loci[c2[0] + '_' + c2[1]] = points

    if False: #record:
        import pickle           
        f = open('lociCAS','w')
        m = pickle.Pickler(f)
        pickle.dump(loci,m) 
        f.close()

    else:
        import pickle 
        f = open('lociCAS','r')
        m = pickle.Unpickler(f)
        locus_list_mag = m.load()
        print locus_list_mag.keys()

        pylab.scatter(locus_list_mag['g_r'][:,1],locus_list_mag['r_i'][:,1],color='green')

    




    pylab.scatter(points[:,0], points[:,1],color='red')

    points = []
    incre = 0.02
    for x in scipy.arange(c1_lim[0],c1_lim[1],incre):        
        mask = (x < p.field('psfPog_'+c1[0]) - p.field('psfPog_' + c1[1])) * (x + incre > p.field('psfPog_'+c1[0]) - p.field('psfPog_'+c1[1])) * (19 < p.field('psfPog_r')) # - p.field('psfPog_r')) * (-99 < p.field('psfPog_g') - p.field('psfPog_r'))
                                                                                                                                                                                                                                                                           
        filt = p[mask]
        colors = filt.field('psfPog_' + c2[0]) - filt.field('psfPog_' + c2[1])
        print colors
        points.append([x+incre/2., scipy.median(colors)] )                    
        
    points = scipy.array(points)
    print points
    pylab.scatter(points[:,0], points[:,1],color='blue')







    #pylab.scatter(p2.field('psfPog_' + c1[0])-p2.field('psfPog_' + c1[1]),p2.field('psfPog_' + c2[0])- p2.field('psfPog_' + c2[1]),s=0.001, color='red')
    pylab.xlim(c1_lim)
    pylab.ylim(c2_lim)
    pylab.xlabel(c1[0] + '-' + c1[1])
    pylab.ylabel(c2[0] + '-' + c2[1])


    
    #p = pyfits.open('locusext2_pkelly100.fit')[1]
    #pylab.scatter(p.field('Column2')-p.field('Column3'),p.field('Column1')- p.field('Column2'),s=0.05,color='red')
    
    pylab.show()



