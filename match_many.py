
def make_ssc_config(list):
    for i,prefix,file_name in [[0,'',phot_file],[1,'SDSS_',SDSS_file]]:

	os.system('ldacdesc -t STDTAB -i ' + file_name + ' > ' + ofile)
        
        file = open(ofile,'r').readlines()
        
        for line in file:
        	if string.find(line,"Key name") != -1:
        		red = re.split('\.+',line)
        		key = red[1].replace(' ','').replace('\n','')
			out_key = prefix + key
        		out.write("COL_NAME = " + out_key + '\nCOL_INPUT = ' + key + '\nCOL_MERGE = AVE_REG\nCOL_CHAN = ' + str(i) + "\n#\n")
        		#print key
			keys.append(key)



import os
command = 'ldacaddkey -i %(inputcat)s -t OBJECTS -o %(outputcat) -k A_WCS_assoc 0.0003 FLOAT "" \
                                B_WCS_assoc 0.0003 FLOAT "" \
                                Theta_assoc 0.0 FLOAT "" \
                                Flag_assoc 0 SHORT "" ' % {'inputcat':,'outputcat':}
os.system(command)

command = 'ldacrenkey -i %(inputcat)s -o %(outputcat)s -k ALPHA_J2000 Ra DELTA_J2000 Dec' % {'inputcat':,'outputcat':} 
os.system(command)

command = 'associate -i %(inputcats)s -o %(outputcats)s -t STDTAB -c ./photconf/fullphotom.conf.associate' % {'inputcats':,'outputcats':}
os.system(command)

command = 'makessc -i %(inputcats)s \
		-o %(outputcat)s\
		-t STDTAB -c ${TEMPDIR}/tmp.conf ' % {'inputcats':,'outputcat':}
os.system(command)


