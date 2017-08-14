import sys, string, re, os

ssc_conf = sys.argv[1]
phot_file = sys.argv[2]
SDSS_file = sys.argv[3]
ofile = '/tmp/tmpssc'



out = open(ssc_conf,'w')

out_keys = {} 
keys = []
for i,prefix,file_name in [[0,'SEx_',phot_file],[1,'',SDSS_file]]:
	os.system('ldacdesc -t STDTAB -i ' + file_name + ' > ' + ofile)
        file = open(ofile,'r').readlines()
        for line in file:
        	if string.find(line,"Key name") != -1:
        		red = re.split('\.+',line)
        		key = red[1].replace(' ','').replace('\n','')
                        prefix_t = prefix
			if prefix == '' and key == 'SeqNr':
				prefix_t = 'SDSS_'
			if prefix == 'SDSS_' and (key == 'Ra' or key=='Dec'):
				prefix_t = ''
			out_key = prefix_t + key
                        print out_key
                        if not out_keys.has_key(out_key) and out_key[0:2] != 'N_': 
                		out.write("COL_NAME = " + out_key + '\nCOL_INPUT = ' + key + '\nCOL_MERGE = AVE_REG\nCOL_CHAN = ' + str(i) + "\n#\n")
                                out_keys[out_key] = ''
        		#print key
			keys.append(key)

for ele in keys:
	found = 0
	for j in keys:
		if j == ele:
			found += 1

	if found > 1:
		print 'double', ele
        
       
out.close() 
os.system('rm /tmp/tmpssc')
