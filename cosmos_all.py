if 0:
    import astropy.io.fits as pyfits, os
    #catalog = '/u/ki/dapple/nfs12/cosmos/cosmos30.slr.matched.cat'

    catalog = '/u/ki/dapple/nfs12/cosmos/cosmos30.slr.cat'
    p = pyfits.open(catalog)['OBJECTS']
    print p.columns
    #print p.data.field('z_spec')[4000:5000]
    
    filters = ['MEGAPRIME-0-1-u','SUBARU-10_2-1-W-J-B','SUBARU-10_2-1-W-J-V','SUBARU-10_2-1-W-S-G+','SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-S-I+','SUBARU-10_2-1-W-S-Z+']
    
    col_names = 'ID MAG_APER-SUBARU-10_2-1-W-S-R+ ' + reduce(lambda x,y: x + ' ' + y,['MAG_APER-' + z + ' MAGERR_APER-' + z for z in filters])


    col= ['ID','MAG_APER-SUBARU-10_2-1-W-S-R+'] + reduce(lambda x,y: x + y,[['MAG_APER-' + z , 'MAGERR_APER-' + z] for z in filters])

    print col

    f = '' 
    for i in range(len(p.data)):
        line = reduce(lambda x,y: x + ' ' + y, [str(p.data.field(c)[i]) for c in col]) 
        #print line
        import string            
        #if string.find(line,'-99') == -1:
        f += line + '\n'


    o = open('COSMOS.input','w')
    o.write(f)
    o.close()

    command = 'ldactoasc -b -i ' + catalog + ' -t OBJECTS -k ' + col_names + ' > COSMOS.input' 
    print command
    #os.system(command)
    
    columns = open('COSMOS.columns','w')
    
    for name,num in [['ID','1'],['Z_S','2'],['M_0','3']]:
        columns.write(name + ' ' + num + '\n')

    for name,num in [['MEGAPRIME-0-1-u','4,5'],['SUBARU-10_2-1-W-J-B','6,7'],['SUBARU-10_2-1-W-J-V','8,9'],['SUBARU-10_2-1-W-S-G+','10,11'],['SUBARU-10_2-1-W-S-R+','12,13'],['SUBARU-10_2-1-W-S-I+','14,15'],['SUBARU-10_2-1-W-S-Z+','16,17']]:
        columns.write(name + ' ' + num + ' AB 0.0 0.0\n')
    
    columns.close()

if 1:
    import os, cutout_bpz
    command = 'python $BPZPATH/bpz.py COSMOS.input -OUTPUT COSMOS.bpz -COLUMNS COSMOS.columns -PROBS_LITE COSMOS.probs -MAG yes -PRIOR hdfn_SB -ZMAX 4.0 -MIN_RMS 0.05 -INTERP 8 -SPECTRA CWWSB_capak.list'
    print command
    os.system(command)
if 0:
    import cutout_bpz, os
    cutout_bpz.plot_res('COSMOS.bpz',os.environ['sne'] + '/photoz/COSMOS/','CWWSB_capak.list')
