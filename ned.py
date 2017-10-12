
def make_catalog(catalog,image,Ra,Dec): #,Ra_Err,Dec_Err):
    print 'importing pyfits and scipy '''
    import astropy.io.fits as pyfits, scipy, os
    print 'done importing'


    command = 'sex ' + image + " -DETECT_THRESH 100000 -FLAG_IMAGE '' -CATALOG_TYPE FITS_LDAC -CATALOG_NAME sex.cat "
    os.system(command)

    ''' copy in catalog hdus '''
    p = pyfits.open('sex.cat')
    primary = p[0]
    IMHEAD = p['LDAC_IMHEAD']


    #p = pyfits.open('fpC-004204-g5-0113.fits.cat')
    # OBJECTS = p['LDAC_OBJECTS']

    print image
   
    inputfile = open('inputfile','w') 
    for i in range(len(Ra)):
        inputfile.write(str(Ra[i]) + ' ' + str(Dec[i]) + '\n')
    inputfile.close()
    
    command = 'sky2xy_wcstools ' + image + ' @inputfile > output'  
    print command

    utilities.run(command)

    xs = []
    ys = []
    for line in open('output','r').readlines():
        import re
        res = re.split('\s+',line)
        xs.append(float(res[4]))
        ys.append(float(res[5]))

    #raw_input('finished converting')

    import os
    #zcat = open(os.environ['bonn'] + '/' + cluster + '.zcat','w')
    #for i in range(len(SeqNr_col)):
    #    zcat.write(str(SeqNr_col[i]) + ' ' + str(ra_col[i]) + ' ' + str(dec_col[i]) + ' ' + str(z_col[i]) + '\n')
    #zcat.close()


    cols = []

    cols.append(pyfits.Column(name='NUMBER', format='J', array=range(len(xs))))
    cols.append(pyfits.Column(name='XWIN_IMAGE', format='D', array=scipy.array(xs)))
    cols.append(pyfits.Column(name='YWIN_IMAGE', format='D', array=scipy.array(ys)))

    cols.append(pyfits.Column(name='ERRAWIN_IMAGE', format='E', array=0.04*scipy.ones(len(Dec))))
    cols.append(pyfits.Column(name='ERRBWIN_IMAGE', format='E', array=0.04*scipy.ones(len(Dec))))
    cols.append(pyfits.Column(name='ERRTHETAWIN_IMAGE', format='E', array=10.*scipy.ones(len(Dec))))

    cols.append(pyfits.Column(name='X_WORLD', format='D', array=scipy.array(Ra)))
    cols.append(pyfits.Column(name='Y_WORLD', format='D', array=scipy.array(Dec)))

    cols.append(pyfits.Column(name='FLUX_RADIUS', format='E', array=1.5*scipy.ones(len(Dec))))
    cols.append(pyfits.Column(name='FLUX_AUTO', format='E', array=2000.*scipy.ones(len(Dec))))
    cols.append(pyfits.Column(name='FLUXERR_AUTO', format='E', array=60.*scipy.ones(len(Dec))))
    cols.append(pyfits.Column(name='FLUX_MAX', format='E', array=1000.*scipy.ones(len(Dec))))
    #cols.append(pyfits.Column(name='ELONGATION', format='D', array=1.*scipy.ones(len(Dec))))
    cols.append(pyfits.Column(name='FLAGS', format='I', array=0.*scipy.ones(len(Dec))))
    cols.append(pyfits.Column(name='MAG_AUTO', format='E', array=20.*scipy.ones(len(Dec))))

    #cols.append(pyfits.Column(name='AWIN_IMAGE', format='D', array=4.*scipy.ones(len(Dec))))
    #cols.append(pyfits.Column(name='BWIN_IMAGE', format='D', array=4.*scipy.ones(len(Dec))))

    #cols.append(pyfits.Column(name='Ra', format='D', array=scipy.array(Ra)))
    #cols.append(pyfits.Column(name='Dec', format='D', array=scipy.array(Dec)))

    coldefs = pyfits.ColDefs(cols)
    OBJECTS = pyfits.BinTableHDU.from_columns(coldefs)
    OBJECTS.header['extname']='LDAC_OBJECTS'
    
    print 'writing out fits file '
    import os
    thdulist = pyfits.HDUList([primary,IMHEAD,OBJECTS])
    os.system('rm ' + 'test.tab')
    thdulist.writeto('test.tab')
   

    command = 'scamp test.tab -c nedastrom -ASTREFCAT_NAME catalog.cat'
 
    #reg = open(file + '.reg' ,'w')
    #reg.write('global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source\nfk5\n')
    #print ra_col
    #for i in range(len(ra_col)):
    #    reg.write('circle('+str(ra_col[i]) + ',' + str(dec_col[i]) + ',4.000") # color=red width=2 \n')
    #reg.close()


import sys

version = '3'

cluster = sys.argv[1]
filt = sys.argv[2]
submit = sys.argv[3]

if submit == 'True': submit = True
else: submit = False

SUBARUDIR='/nfs/slac/g/ki/ki18/anja/SUBARU'

output_dir = SUBARUDIR + '/' + cluster + '/PHOTOMETRY_' + filt + '_aper/'

lookupfile='/nfs/slac/g/ki/ki18/anja/SUBARU/SUBARU.list'

output_filename = "pat3_" + cluster + "_ned_ver" + version + ".dat"

#submit = False 

if submit:
    #ra=`grep ${cluster} ${lookupfile} | awk '{print $3}'`
    #dec=`grep ${cluster} ${lookupfile} | awk '{print $4}'`
    
    #short=`awk 'BEGIN{printf "%.8s", "'${cluster}'"}'`
    #shortnr=`awk 'BEGIN{printf "%.8s", "'${cluster}'"}' | sed 's/MACS//g'`

    f = open(lookupfile,'r').readlines()
    for l in f:
        import re
        res = re.split('\s+',l)
        if res[0] == cluster:        
            ra = float(res[2])
            dec = float(res[3])
    
    position = "%(ra).12fd; %(dec).10f; 45" % {'ra': ra, 'dec': dec}
    
    input = "OUTPUT_FILENAME          " + output_filename + "    \n\
OUTPUT_OPTION              standard \n\
INPUT_COORDINATE_SYSTEM    equatorial              \n\
OUTPUT_COORDINATE_SYSTEM   equatorial              \n\
INPUT_EQUINOX              J2000.0                 \n\
OUTPUT_EQUINOX             J2000.0                 \n\
EXTENDED_NAME_SEARCH       yes                     \n\
OUTPUT_SORTED_BY           RA_or_Longitude         \n\
REDSHIFT_VELOCITY          0.0                     \n\
SEARCH_RADIUS              45.0                    \n\
BEGIN_YEAR                 1900                    \n\
END_YEAR                   2010                    \n\
IAU_STYLE                  S                       \n\
FIND_OBJECTS_NEAR_POSITION   \n\
" + position + "\n\
REDSHIFT                   Available              \n\
UNIT                       z                       \n\
INCLUDE ALL                                        \n\
 Galaxies X                                        \n\
 GClusters _                                       \n\
 Supernovae _                                      \n\
 QSO _                                             \n\
 AbsLineSys _                                      \n\
 GravLens _                                        \n\
 Radio _                                           \n\
 Infrared _                                        \n\
 EmissnLine _                                      \n\
 UVExcess _                                        \n\
 Xray _                                            \n\
 GammaRay _                                        \n\
 GPairs _                                          \n\
 GTriples _                                        \n\
 GGroups _                                         \n\
END_INCLUDE                                        \n\
EXCLUDE                                            \n\
 Galaxies _                                        \n\
 GClusters _                                       \n\
 Supernovae _                                      \n\
 QSO _                                             \n\
 AbsLineSys _                                      \n\
 GravLens _                                        \n\
 Radio _                                           \n\
 Infrared _                                        \n\
 EmissnLine _                                      \n\
 UVExcess _                                        \n\
 Xray _                                            \n\
 GammaRay _                                        \n\
 GPairs _                                          \n\
 GTriples _                                        \n\
 GGroups _                                         \n\
END_EXCLUDE                                        \n\
END_OF_DATA                                        \n\
END_OF_REQUESTS                                    \n"

    print input

    fout = open('input.ned','w')
    fout.write(input)
    fout.close()
    
    import os
    command = 'mail -s " " nedbatch@ipac.caltech.edu < input.ned'
    print command
    os.system(command)

if not submit:

    ned_loc = 'http://nedbatch.ipac.caltech.edu/batch/'

    import os

    os.system('rm ' + output_filename)

    os.system('wget ' + ned_loc + output_filename) 

    file = output_filename 
    f = open(file,'r').readlines()

    index = False
    object_dict = {}
    i_num = 1
    import string
    for line in f:

        if len(line) < 2: index = False

        if index: 
            ra = line[:-1].split(',')[0].replace(' ','')
            dec = line[:-1].split(',')[1].replace(' ','')
            object_dict[i_num] = {'ra':ra,'dec':dec}
            i_num += 1


        match = '********  Positions for all the objects found in this request *********' 
        if string.find(line,match) != -1:
            index = True


        
    match = "#           Extinct    --------column1------- column2 column3 column4 -----------------column5----------------" 

    i = 0            
    index = False
    for line in f:
        i += 1

        if index and i % 17 == 0 and len(line) < 2:
            index = True 

        if index and (string.find(line,'+/-')!=-1): # or (string.find(line,'...')!=-1 and string.find(line,'Ref') == -1)): #i % 17 == 0:

            try: 
                q = int(line[:5])
                go = True
            except:
                go = False
            if go:                
                i_num = int(line[:5])                                      
                z = line[71:79]
                z_err = line[84:92]
                ref = line[92:-1].replace(' ','')
                                                                           
                object_dict[i_num].update({'z':z,'z_err':z_err,'ref':ref})

            

        if string.find(line,'Extinct') != -1 and string.find(line,'column1') != -1:
            index = True
            i= -1 




    sets = {}

    for key in object_dict.keys():
        if object_dict[key].has_key('ref'):
            ref = object_dict[key]['ref']     
            if not ref in sets: sets[ref] = [key] 
            else: sets[ref].append(key) 
   
    array = zip([len(y) for y in sets.values()],sets.keys())
    array.sort(reverse=True)
    print reduce(lambda x,y:x + '\n' + y, [str(a[0]) + ': ' + str(a[1]) for a in array]    )

    subarudir = '/nfs/slac/g/ki/ki18/anja/SUBARU/'

    import astropy.io.fits as pyfits, os                                                                                                                                                                                                                                                                         
    photdir = subarudir + cluster + '/PHOTOMETRY_' + filt + '_aper/'
    phot_cat = photdir + cluster + '.slr.cat' # '.APER1.1.CWWSB_capak.list.all.bpz.tab'
    photoz_cat = photdir + cluster + '.APER1.1.CWWSB_capak.list.all.bpz.tab'
    image = subarudir + cluster + '/' + filt + '/SCIENCE/coadd_' + cluster + '_good/coadd.fits'

    import utilities
    #utilities.run("ldacfilter -i " + phot_cat + " -t OBJECTS -c '(MAG_APER1-SUBARU-COADD-1-" + filt + " < 22);' -o catalog.cat" ) # + phot_cat+'.SCAMP',[phot_cat+'.SCAMP'])

    #command = 'ldacaddkey -i catalog.cat -t OBJECTS -o catalog2.cat -k ERRA_WORLD 0.000277 FLOAT "" ERRB_WORLD 0.000277 FLOAT "" ERRTHETA_WORLD 0 FLOAT "" '
    #os.system(command)

    zcat = open(os.environ['bonn'] + '/' + cluster + '.zcat','w')

    zcat_index = 0

    for num, key in array[:]:
        print key
        if len(sets[key]) > 20:

            def raconvdeg(ra):    
                radeg = (float(ra[0:2]) + float(ra[3:5])/60. + float(ra[6:10])/3600.)*15
                return radeg

            def decconvdeg(dec):
                if dec[0] != '+' and dec[0] != '-':
                    dec = '+' + dec

                if dec[0] == '-': mult = -1.
                else: mult = 1.                
                decdeg = mult * (float(dec[1:3]) + float(dec[4:6])/60. + float(dec[7:9])/3600.)
                return decdeg    


            Ra = [raconvdeg(object_dict[ind]['ra']) for ind in sets[key]]
            Dec = [decconvdeg(object_dict[ind]['dec']) for ind in sets[key]]
            z = [(object_dict[ind]['z']) for ind in sets[key]]

            reg = open(file + '.reg' ,'w')        
            reg.write('global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source\nfk5\n')
            for i in range(len(Ra)):
                reg.write('circle('+str(Ra[i]) + ',' + str(Dec[i]) + ',4.000") # color=red width=2 \n')
            reg.close()

            
            for i in range(len(Ra)):
                zcat_index += 1
                zcat.write(str(zcat_index) + ' ' + str(Ra[i]) + ' ' + str(Dec[i]) + ' ' + str(z[i]) + '\n')




            #make_catalog(phot_cat,image,Ra,Dec)

            #raw_input('finished')
            


    zcat.close()

if False: 
    raw_input('filtered')

    command = 'scamp '

    import os
    #os.system('python mk_ldac_spec.py ' + cluster + ' ' + filt)

    import string
    ra_col = []
    dec_col = []
    z_col = []
    SeqNr_col = []
    SeqNr = 0
    for l in f:
        print len(l), l
        if len(l) > 82:
            if l[4] == '(' and l[9] == ')' and l[79] == '+':                                                     
                
                Type = l[10:18]            
                z = float(l[73:82])
                ra = l[49:60]
                #name = l[]
                
                radeg = (float(ra[0:2]) + float(ra[3:5])/60. + float(ra[6:10])/3600.)*15
                dec = l[61:72]
                print dec
                if dec[0] == '+': mult = 1.
                else: mult = -1.                
                decdeg = mult * (float(dec[1:3]) + float(dec[4:6])/60. + float(dec[7:9])/3600.)
                
                if (string.find(Type,'G') != -1 and string.find(Type,'QSO')== -1) and z > 0.01: 
                    print ra,dec,z, decdeg, radeg
                    ra_col.append(radeg)
                    dec_col.append(decdeg)
                    z_col.append(z)
                    SeqNr += 1                    
                    SeqNr_col.append(SeqNr)
    
    print 'importing pyfits and scipy '''
    import astropy.io.fits as pyfits, scipy
    print 'done importing'
    
    hdu = pyfits.PrimaryHDU()

    #zcat = open(os.environ['bonn'] + '/' + cluster + '.zcat','w')
    #for i in range(len(SeqNr_col)):
    #    zcat.write(str(SeqNr_col[i]) + ' ' + str(ra_col[i]) + ' ' + str(dec_col[i]) + ' ' + str(z_col[i]) + '\n')
    #zcat.close()
    
    cols = []
    cols.append(pyfits.Column(name='Nr', format='J', array=scipy.array(SeqNr_col)))
    cols.append(pyfits.Column(name='Ra', format='D', array=scipy.array(ra_col)))
    cols.append(pyfits.Column(name='Dec', format='D', array=scipy.array(dec_col)))
    cols.append(pyfits.Column(name='Z', format='D', array=scipy.array(z_col)))
    cols.append(pyfits.Column(name='FIELD_POS', format='J', array=scipy.ones(len(z_col))))
    coldefs = pyfits.ColDefs(cols)
    OBJECTS = pyfits.BinTableHDU.from_columns(coldefs)
    OBJECTS.header['extname']='OBJECTS'
    
    cols = []
    cols.append(pyfits.Column(name='OBJECT_POS', format='J', array=[1.]))
    cols.append(pyfits.Column(name='OBJECT_COUNT', format='D', array=[len(z_col)]))
    cols.append(pyfits.Column(name='CHANNEL_NR', format='J', array=[0]))
    coldefs = pyfits.ColDefs(cols)
    FIELDS = pyfits.BinTableHDU.from_columns(coldefs)
    FIELDS.header['extname']='FIELDS'
    
    print 'writing out fits file '
    import os
    thdulist = pyfits.HDUList([hdu,OBJECTS,FIELDS])
    os.system('rm ' + output_dir + file + '.tab')
    thdulist.writeto(output_dir + file + '.tab')
    
    reg = open(file + '.reg' ,'w')
    reg.write('global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source\nfk5\n')
    print ra_col
    for i in range(len(ra_col)):
        reg.write('circle('+str(ra_col[i]) + ',' + str(dec_col[i]) + ',4.000") # color=red width=2 \n')
    reg.close()
        
