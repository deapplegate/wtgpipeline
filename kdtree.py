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

def tree(start,end):    
    import sys, pyfits, os
    #caltable = '/tmp/' + cluster + 'output.cat' #sys.argv[1]
    #print cluster, caltable
    #hdulist = pyfits.open(caltable)
    #table = hdulist["OBJECTS"].data
    
    from scipy.spatial import KDTree
    
    file = os.environ['sne'] + '/cosmos/cosmos_zphot_mag25.nums.fits'
    #file = os.environ['subdir'] + '/MACS1423+24/PHOTOMETRY/MACS1423+24.slr.cat'
    hdulist = pyfits.open(file)
    table = hdulist["OBJECTS"].data
    array = []
    cols = []
    lim_mags = {}
    #for filter in ['MAG_APER1-MEGAPRIME-0-1-u']: # ['umag','bmag','vmag','gmag','rmag','imag','zmag']: #,'icmag','jmag','kmag']:

    for filter in  ['umag','bmag','vmag','gmag','rmag','imag','zmag']: #,'icmag','jmag','kmag']:
        print hdulist['OBJECTS'].columns
        for column in hdulist['OBJECTS'].columns:
            if filter == column.name:
                print column.format
                cols.append(pyfits.Column(name=filter,format=column.format,array=hdulist['OBJECTS'].data.field(filter)[start:end]))
                #import pylab, scipy                    
                l = hdulist['OBJECTS'].data.field(filter)[start:end]
                #a,b,varp = pylab.hist(l,bins=scipy.arange(20,30,0.1))
                #print a, b
                #c = zip(a,b)
                #c.sort()
                #lim_mags[filter] = c[-1][1]
                #pylab.xlabel('Mag')
                #pylab.ylabel('Number of Galaxies')
                #pylab.show()

    print cols
    tbhdu=pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))

    from copy import copy
    tbhdu_good=copy(tbhdu)

    #mask = reduce(lambda x,y:x*y,[tbhdu.data.field(filter) < (lim_mags[filter]-1.) for filter in lim_mags.keys()])

    #print len(tbhdu_good.data.field('umag')[mask])

    for filter in  ['umag','bmag','vmag','gmag','rmag','imag','zmag']: #,'icmag','jmag','kmag']:                                     
        print hdulist['OBJECTS'].columns
        for column in hdulist['OBJECTS'].columns:
            if filter == column.name:
                print column.format
                cols.append(pyfits.Column(name=filter,format=column.format,array=hdulist['OBJECTS'].data.field(filter)[start:end]))
                #import pylab, scipy                    
                #l = hdulist['OBJECTS'].data.field(filter)[mask][0:length]
                #pylab.clf()                    
                #a,b,varp = pylab.hist(l,bins=scipy.arange(20,30,0.1))
                #print a, b
                #c = zip(a,b)
                #c.sort()
                #lim_mags[filter] = c[-1][1]
                #pylab.xlabel('Mag')
                #pylab.ylabel('Number of Galaxies')
                #pylab.show()



    tbhdu_bad=copy(tbhdu)

    import scipy

    p = scipy.array([[tbhdu.data[2200][i] for i in range(7)]])
    print p
    
    #return KDTree(p) 

    hdu = pyfits.PrimaryHDU()
    thdulist = pyfits.HDUList([hdu,tbhdu])
    #os.system('rm temp.fits')
    #thdulist.writeto('temp.fits')

    import numpy 
    sarray = (tbhdu.data.tolist())
    print numpy.shape(sarray)        
    
    #a = KDTree(sarray)

    print lim_mags
    
    return sarray
