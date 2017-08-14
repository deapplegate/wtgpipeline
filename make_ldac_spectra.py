#!/usr/bin/env python


import MySQLdb
import os, sys, anydbm, time, re, string, BonnLogger, getopt
#from config import datb, dataloc
#from config_bonn import cluster

# cluster = sys.argv[1]
#print datb + cluster

import lib 


def doit(cluster,specfile,outputfile):

	#	os.system("mkdir " + cluster)
	
	zcat = open(specfile,'r').readlines()
	op = open('op','w')

	SeqNr = 0
	for line in zcat:
		ll = re.split('\s+',line)	
		if ll[0] == '': ll = ll[1:]	
		temp = ['','temp']

		if string.find(ll[1],':') != -1:
			for ele in ll[1:]:
				temp.append(ele) 
			ll = temp


		id = ll[1] #line[0:6]

		agalra     = ll[2] #line[8:20]
		agaldec    = ll[3] #line[22:34]
		z = ll[4] #line[37:43]
		# print id, agalra, agaldec, z
		rlist = ['','',''] 
		dlist = ['','',''] 
		rlist[0] = agalra[0:2] 
		rlist[1] = agalra[3:5] 
		rlist[2] = agalra[6:] 
		dsign = agaldec[0]
		dmul = float(dsign + '1')
		dlist[0] = agaldec[1:3] 
		dlist[1] = agaldec[4:6] 
		dlist[2] = agaldec[7:] 


		radeg = (360/24.0)*string.atof(rlist[0]) + (360.0/(24.0*60))*string.atof(rlist[1]) + (360.0/(24.0*60.0*60.0))*string.atof(rlist[2])
		spectrara = radeg
		decdeg = dmul * (string.atof(dlist[0]) + (1/60.0)*string.atof(dlist[1]) + string.atof(dlist[2])*(1/(60.0*60.0))                           )
		spectradec = decdeg
		spectraz = z
		label = id

		p = re.compile('\S')
		m = p.findall(label)
		if len(m) == 0: label = 'nolab'
		SeqNr += 1
		if string.find(spectraz,'?') == -1 and \
		   spectraz != '' and spectraz != '-1' and \
		   0 < float(spectraz) < 1.5:
			print radeg, decdeg, spectraz

			op.write(str(SeqNr) + ' ' + \
				 str(radeg) + " " + \
				 str(decdeg)+ " " + str(spectraz) + "\n")
	op.close()
	os.system('asctoldac -i op -o '+ outputfile +' -c ./photconf/zspec.conf')
	



if __name__ == "__main__":

	
	__bonn_logger_id__ = BonnLogger.addCommand('do_calibration.py', 
						   sys.argv[1:])

	usage = '''
	make_ldac_spectra.py -c, --cluster=[cluster name] # cluster
	                     -s, --specfile=[spectra file] # File with the spectra
			     -o, --outputfile=[output file] # output cat name


	'''
	
	try:
		opts, args = getopt.getopt(sys.argv[1:],
					   "c:s:o:",
					   ["cluster=",
					    "specfile=","outputfile="])
	except getopt.GetoptError:
		print usage
		sys.exit(2)


	cluster = "MACS1423+24"
	specfile = "1423.spec"
	outputfile = "/tmp/"+cluster+".cat"

	# opts
	for o, a in opts:
		if o in ("-c", "--cluster"):
			cluster = a
		elif o in ("-s","--specfile"):
			specfile = a
		elif o in ("-o","--outputfile"):
			outputfile = a
	        else:
			print "option:", o, " unknown"
			usage()
			sys.exit(2)
	
			
	doit(cluster,specfile,outputfile)
