#! /usr/bin/env python
#adam-does# this replaces "#TEMPLATE-run-filter-FLAT" in some file with other stuff and saves it to new output!
import sys,os,re,string

#temp_starter="#TEMPLATE-run-filter-FLAT"
temp_starter="#TEMPLATE"
temp_file="adam_CTcorr_allOCF-TEMPLATE.sh"
temp_fo=open(temp_file,'rb')
#os.system("grep '%s' %s" % (temp_starter,temp_file))
#f=open(fl,'wb')
for l in temp_fo.xreadlines():
        l=l.strip()
        if not l: continue
	if l.startswith(temp_starter):
		temp_line=l
		break

include=temp_line.split("-")[1:]


## fgas only
#fgas={"2015":{"ppruns":{},"filters":{},"clusters":{}}, "preH":{"ppruns":{},"filters":{},"clusters":{}}, "smoka":{"ppruns":{},"filters":{},"clusters":{}}}
ppruns={}
ppruns["2015-12-15_W-J-B"]={'run':"2015-12-15",'filter':"W-J-B","FLAT":"DOMEFLAT","clusters":[ "MACSJ0159.8-0849", "MACSJ0429.6-0253", "Z2089", "Z2701"]}
ppruns["2015-12-15_W-C-RC"]={'run':"2015-12-15",'filter':"W-C-RC","FLAT":"SKYFLAT","clusters":["Z2089", "Z2701"]}
ppruns["2015-12-15_W-S-Z+"]={'run':"2015-12-15",'filter':"W-S-Z+","FLAT":"DOMEFLAT","clusters":[ "MACSJ0159.8-0849", "MACSJ0429.6-0253", "Z2089" ]}
for pp_key in ppruns.keys():
	final_keys=[]
	for include_key in include:
		ppruns[pp_key][include_key]
		final_keys.append(include_key+"="+ppruns[pp_key][include_key])
	#final_string=final_keys.join(";")
	#print final_string
	final_file=temp_file.replace("TEMPLATE",pp_key)
	final_string=string.join(final_keys,";")
	os.system("sed 's/%s/%s/g' %s > %s" % (temp_line,final_string,temp_file,final_file))
	os.system("chmod u+x %s" % (final_file))

	logout=temp_file.replace("TEMPLATE",pp_key).rsplit('.')[0]
	#print logout
        print "bsub -W 7000 -R rhel60 -o /nfs/slac/g/ki/ki18/anja/SUBARU/batch_files/OUT-%s.out -e /nfs/slac/g/ki/ki18/anja/SUBARU/batch_files/OUT-%s.err ./%s" % (logout,logout,final_file)

#m=re.match("(SUPA[0-9][0-9][0-9][0-9][0-9][0-9][0-9])(.*)",l)
