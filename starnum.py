
def star_num(filt,catalog,starcatalog,cluster,magtype,name_suffix=''):
    import random, pyfits
    print catalog, starcatalog
    p = pyfits.open(catalog)['OBJECTS'].data
    s = pyfits.open(starcatalog)
    indices = s['OBJECTS'].data.field('SeqNr')
    ddict = {}
    for index in indices:
        p.field('CLASS_STAR')[index-1] = -999 
    mask = p.field('CLASS_STAR') == -999 
    table = p[mask]
   
    for filt in filters: 
        at = table.field('MAG_' + magtype + '-' + filt)[:] 
        aterr = table.field('MAGERR_' + magtype + '-' + filt)[:] 

        good = scipy.ones(len(at))
        good[at==-99]  = 0
        good[aterr>0.4]  = 0
        print len(at[good==1]), filt
