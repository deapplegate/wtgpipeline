
def make_ssc_config_colors(list):

    ofile = tmpdir + '/tmp.cat'
    out = open(tmpdir + '/tmp.ssc','w')
    import os, string, re

    keys = []
    i = -1 
    for file_name,prefix in list:
        i += 1
        print file_name
        os.system('ldacdesc -t OBJECTS -i ' + file_name + ' > ' + ofile)
        file = open(ofile,'r').readlines()
        for line in file:
            if string.find(line,"Key name") != -1:
                red = re.split('\.+',line)
                key = red[1].replace(' ','').replace('\n','')
                out_key = key + '_' + prefix
                out.write("COL_NAME = " + out_key + '\nCOL_INPUT = ' + key + '\nCOL_MERGE = AVE_REG\nCOL_CHAN = ' + str(i) + "\n#\n")
                #print key
                keys.append(key)

    out.close()

def match_many(list,color=False):

    import os 
    os.system('rm -rf ' + tmpdir + '/assoc/')
    os.system('mkdir -p ' + tmpdir + '/assoc/')

    import os
    files = []
    i=0
    for file,prefix in list:
        print file
        import re
        res = re.split('\/',file)
        #os.system('ldactoasc -i ' + file + ' -t OBJECTS -k ALPHA_J2000 DELTA_J2000 > ' +  os.environ['bonn'] +  res[-1] )
        #os.system('mkreg.pl -c -rad 3 -xcol 0 -ycol 1 -wcs ' +  os.environ['bonn'] + res[-1])

        i += 1                                                                                                                  
        colour = 'blue'
        if i%2 ==0: colour = 'red'
        if i%3 ==0: colour = 'green'
        import re
        res = re.split('\/',file)
        #os.system('ldactoasc -i ' + file + ' -t OBJECTS -k ALPHA_J2000 DELTA_J2000 > ' +  os.environ['bonn'] +  res[-1] )
        #os.system('mkreg.pl -c -rad ' + str(i) + ' -xcol 0 -ycol 1 -colour ' + colour + ' -wcs ' +  os.environ['bonn'] + res[-1])

        fileout1 = tmpdir + '/assoc/' + prefix + re.split('\/',file)[-1] + '.assoc1'
        fileout2 = tmpdir + '/assoc/' + prefix + re.split('\/',file)[-1] + '.assoc2'
        command = 'ldacaddkey -i %(inputcat)s -t OBJECTS -o %(outputcat)s -k A_WCS_assoc 0.0003 FLOAT "" \
                                        B_WCS_assoc 0.0003 FLOAT "" \
                                        Theta_assoc 0.0 FLOAT "" \
                                        Flag_assoc 0 SHORT "" ' % {'inputcat':file,'outputcat':fileout1}
        os.system(command)
    
        command = 'ldacrenkey -i %(inputcat)s -o %(outputcat)s -k Nr SeqNr' % {'inputcat':fileout1,'outputcat':fileout2} 
        os.system(command)
        files.append([fileout2,prefix])
    
    if 1:
        make_ssc_config_colors(files) 
        print color




    import re
    print files
    files_input = reduce(lambda x,y:x + ' ' + y,[z[0] for z in files])

    files_output = reduce(lambda x,y:x + ' ' + y,[tmpdir + '/assoc/'+re.split('\/',z[0])[-1] +'.assd' for z in files])

    print files
    print files_input, files_output
    
    command = 'associate -i %(inputcats)s -o %(outputcats)s -t OBJECTS -c %(bonn)s/photconf/fullphotom.radec.associate' % {'inputcats':files_input,'outputcats':files_output, 'bonn':os.environ['bonn']}
    print command
    os.system(command)
    print 'associated'

    outputcat = tmpdir + '/final.cat'
    command = 'make_ssc -i %(inputcats)s \
            -o %(outputcat)s\
            -t OBJECTS -c %(tmpdir)s/tmp.ssc ' % {'tmpdir': tmpdir, 'inputcats':files_output,'outputcat':outputcat}
    os.system(command)

import os

tmpdir = '/usr/work/pkelly/'
os.system('mkdir -p ' + tmpdir)
l = ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']
cluster = 'MACS0911+17'
list = [[os.environ['subdir'] + '/' + cluster + '/' + filter +'/SCIENCE/coadd_' + cluster + '_all/coadd_stars.cat',filter] for filter in l] 
print list
match_many(list)
