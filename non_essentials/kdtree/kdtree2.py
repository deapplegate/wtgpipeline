''' http://www.biopython.org/DIST/docs/api/Bio.KDTree.KDTree%27-module.html '''


def photoz(list):
    import sys, pyfits, os
    file = os.environ['sne'] + '/cosmos/cosmos_zphot_mag25.nums.fits'
    hdulist = pyfits.open(file)
    table = hdulist["OBJECTS"].data

    r = []
    for i in list[0]:    
        r.append(table.field('zp_best')[i])
    print r

    import pylab, scipy                                    
    
    a = scipy.array(r) 
    a, b, varp = pylab.hist(a,bins=scipy.arange(0,4,0.05))
    pylab.xlabel("Z")
    pylab.ylabel("Number of Galaxies")
    pylab.show()
    raw_input()

    return 

def tree(length):    
    import sys, pyfits, os
    #caltable = '/tmp/' + cluster + 'output.cat' #sys.argv[1]
    #print cluster, caltable
    #hdulist = pyfits.open(caltable)
    #table = hdulist["OBJECTS"].data
    
    from scipy.spatial import KDTree
    
    file = os.environ['sne'] + '/cosmos/cosmos_zphot_mag25.nums.fits'
    hdulist = pyfits.open(file)
    table = hdulist["OBJECTS"].data
    array = []
    cols = []
    for filter in ['umag','bmag','vmag','gmag','rmag','imag','zmag']: #,'icmag','jmag','kmag']:
        print hdulist['OBJECTS'].columns
        for column in hdulist['OBJECTS'].columns:
            if filter == column.name:
                print column.format
                cols.append(pyfits.Column(name=filter,format=column.format,array=hdulist['OBJECTS'].data.field(filter)[0:length]))

    print cols
    tbhdu=pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))

    import scipy

    p = scipy.array([[tbhdu.data[2200][i] for i in range(7)]])
    print p
    
    #return KDTree(p) 

    hdu = pyfits.PrimaryHDU()
    thdulist = pyfits.HDUList([hdu,tbhdu])
    #os.system('rm temp.fits')
    #thdulist.writeto('temp.fits')

    import numpy 
    sarray = numpy.asarray(tbhdu.data.tolist())
    print numpy.shape(sarray)        
    
    a = KDTree(sarray)
    
    return a
