import sys

version = '3'

cluster = sys.argv[1]
filt = sys.argv[2]
submit = sys.argv[3]

if submit == 'True': submit = True
else: submit = False

SUBARUDIR='/nfs/slac/g/ki/ki05/anja/SUBARU'

output_dir = SUBARUDIR + '/' + cluster + '/PHOTOMETRY_' + filt + '_aper/'

lookupfile='/nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list'

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

    os.system('pwd')
    file = output_filename 
    f = open(file,'r').readlines()
    
    import string
    ra_col = []
    dec_col = []
    z_col = []
    SeqNr_col = []
    SeqNr = 0
    for l in f:
        if len(l) > 82:
            if l[4] == '(' and l[9] == ')':                                                     
                
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
    import pyfits, scipy
    print 'done importing'
    
    hdu = pyfits.PrimaryHDU()

    zcat = open(os.environ['bonn'] + '/' + cluster + '.zcat','w')
    for i in range(len(SeqNr_col)):
        zcat.write(str(SeqNr_col[i]) + ' ' + str(ra_col[i]) + ' ' + str(dec_col[i]) + ' ' + str(z_col[i]) + '\n')
    zcat.close()
    
    cols = []
    cols.append(pyfits.Column(name='Nr', format='J', array=scipy.array(SeqNr_col)))
    cols.append(pyfits.Column(name='Ra', format='D', array=scipy.array(ra_col)))
    cols.append(pyfits.Column(name='Dec', format='D', array=scipy.array(dec_col)))
    cols.append(pyfits.Column(name='Z', format='D', array=scipy.array(z_col)))
    cols.append(pyfits.Column(name='FIELD_POS', format='J', array=scipy.ones(len(z_col))))
    coldefs = pyfits.ColDefs(cols)
    OBJECTS = pyfits.new_table(coldefs)
    OBJECTS.header.update('extname','OBJECTS')
    
    cols = []
    cols.append(pyfits.Column(name='OBJECT_POS', format='J', array=[1.]))
    cols.append(pyfits.Column(name='OBJECT_COUNT', format='D', array=[len(z_col)]))
    cols.append(pyfits.Column(name='CHANNEL_NR', format='J', array=[0]))
    coldefs = pyfits.ColDefs(cols)
    FIELDS = pyfits.new_table(coldefs)
    FIELDS.header.update('extname','FIELDS')
    
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
        
