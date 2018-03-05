# python retrieve_test.py $subdir/MACS2243-09/W-C-RC/SCIENCE/coadd_MACS2243-09/coadd.fits $subdir/MACS2243-09/PHOTOMETRY/panstarrs.cat

# python retrieve_test.py $subdir/MACS0911+17/W-C-RC/SCIENCE/coadd_MACS0911+17/coadd.fits $subdir/MACS0911+17/PHOTOMETRY/panstarrsstar.cat
from math import *
import os, sys, anydbm, time, string, commands, re
import astropy
import pickle
import math


def convert_to_pogson(magnitude,filter):
	''' converts from luptitudes to magnitudes in the traditional (i.e. pogson), sense'''
	b_values = {'u':1.4E-10,'g':0.9E-10,'r':1.2E-10,'i':1.8E-10,'z':7.4E-10}
	b = b_values[filter]
	try:
		flux_ratio = sinh(-1.*log(10)*magnitude/2.5 - log(b))*2*b	
	except: flux_ratio = -99
	#print flux_ratio

	if flux_ratio > 0:
	        pogson_magnitude = -2.5 * log10(flux_ratio)
	else: pogson_magnitude = -999

	#print pogson_magnitude, magnitude
	return pogson_magnitude


''' make sure we have a clean sample of panstarrs stars '''
def inspect_flags(flags1,flags2):

	flcodes = {'PEAKCENTER':[1,5],'NOTCHECKED':[1,19],'DEBLEND_NOPEAK':[2,14],'PSF_FLUX_INTERP':[2,15],'BAD_COUNTS_ERROR':[2,8],'INTERP_CENTER':[2,12],'CR':[1,12],'BINNED1':[1,28],'BRIGHT':[1,1],'SATURATED':[1,18],'EDGE':[1,2],'BLENDED':[1,3],'NODEBLEND':[1,6],'NOPROFILE':[1,7]}

	good = 1

	for i in range(5):
        	
		dict = {}	

		if (int(flag) & 2**n): flag_up_2.append(n)	
                                                           
	        for fl in flcodes.keys():
	        	flag_num = flcodes[fl][0]
	        	bit_num = flcodes[fl][0]
			flags = [flags1[i],flags2[i]]
			dict[fl] = flags[flag_num] & 2**int(bit_num)
				
		
		print dict	

	        good = 1
	return good

def run(img,outcat,type,limits=None,illum_cat='test.cat'):
	#example: outcat='/gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/PHOTOMETRY/panstarrsstar.cat'
	startdir=os.getcwd()
	outcatdir=os.path.dirname(outcat)
	os.chdir(outcatdir)
       
        print img, outcat, type

        if type == 'star': mag_type = 'psf'
        if type == 'galaxy': mag_type = 'petro'

        print img
	if os.path.isfile("outim_panstarrs"):
		os.system("rm outim_panstarrs")
	if os.path.isfile(outcat):
		os.system('rm ' + outcat)
	if os.path.isfile("panstarrs_out"):
		os.system('rm panstarrs_out')
       
        if limits is not None:
            ramin = limits['ramin']
            ramax = limits['ramax']
            decmin = limits['decmin']
            decmax = limits['decmax']
        else:
            command = 'dfits ' + img + ' | fitsort -d CD2_1'
            print command
            print commands.getoutput(command)
            if string.find(commands.getoutput(command),'KEY') == -1:
            	imcom = "dfits " + img + " | fitsort CRPIX1 CRPIX2 CRVAL1 CRVAL2 CD2_1 CD1_2 CD2_2 CD1_1 > ./outim_panstarrs"
            else:
            	imcom = "dfits " + img + " | fitsort CRPIX1 CRPIX2 CRVAL1 CRVAL2 CDELT1 CDELT2 > ./outim_panstarrs"
            
            print imcom
            os.system(imcom)
            print open('outim_panstarrs','r').readlines()
            com = re.split('\s+',open("outim_panstarrs",'r').readlines()[1][:-1]  )
            print com
            crpix1 = float(com[1])
            crpix2 = float(com[2])
            crval1 = float(com[3])
            crval2 = float(com[4])
            
            if string.find(commands.getoutput(command),'KEY') == -1:
                cdelt1A = float(com[5])
                cdelt2A = float(com[6])
                cdelt1B = float(com[7])
                cdelt2B = float(com[8])
                
                if float(cdelt1A) != 0:
                    cdelt1 = cdelt1A
                    cdelt2 = cdelt2A
                else:
                    cdelt1 = cdelt1B
                    cdelt2 = cdelt2B
            else: 
                cdelt1 = float(com[5])
                cdelt2 = float(com[6])
            
            
            print crpix1, crval1, cdelt1
            #ramin = crval1 - crpix1*cdelt1 
            
            ramin = crval1 - 9000*abs(cdelt1)
            print ramin
            ramax = crval1 + 9000*abs(cdelt1)
            if ramax < ramin: 
            	top = ramin
            	ramin = ramax
            	ramax = top
            
            decmin = crval2 - 9000*abs(cdelt2) 
            decmax = crval2 + 9000*abs(cdelt2)
	
	#adam-SHNT# this is my substitute for the sdss-version of clipping in ra/dec, check to make sure it works
	illum_fo=astropy.io.ascii.read(illum_cat,'csv')
	ra=illum_fo['ra']
	dec=illum_fo['dec']
	ra_lims=(ra<ramax)*(ra>ramin)
	dec_lims=(dec<decmax)*(dec>decmin)
	pos_lims=ra_lims*dec_lims
	illum_fo2=illum_fo[pos_lims]
	illum_fo2.write(illum_cat+'2',format='ascii.csv',overwrite=True)
	#illum_fo.close()

	panstarrs_fo=open(illum_cat+'2','r')
	lines = panstarrs_fo.readlines()
	#adam-sdss-version# query = "select clean, ra,dec,raErr,decErr," + mag_type + "Mag_u," + mag_type + "Mag_g," + mag_type + "Mag_r," + mag_type + "Mag_i," + mag_type + "Mag_z," + mag_type + "MagErr_u," + mag_type + "MagErr_g," + mag_type + "MagErr_r," + mag_type + "MagErr_i," + mag_type + "MagErr_z, flags from " + type + " where   ra between " + str(ramin)[:8] + " and  " + str(ramax)[:8] + " and  dec between " + str(decmin)[:8] + " and " +str(decmax)[:8]  + " AND clean=1 and " + flags 
        
        uu = open('store_panstarrs','w')
        pickle.dump(lines,uu)
        
        columns = lines[0][:-1].split(',')
        data = []
        #print columns 
        #print lines
        if lines[0][0:2] == 'No':
            return False, None
        
        for line in range(1,len(lines[1:])+1): 
                #print lines[line]
        	dt0 = {}
        	for j in range(len(lines[line][:-1].split(','))): 
                        dt0[columns[j]] = lines[line][:-1].split(',')[j]
        
        	if string.find(lines[line][:-1],'font') == -1: 
        		data.append(dt0)
        	#if string.find(lines[line][:-1],'font') != -1: 
        		#print lines[line][:-1]
        
        print ' len(data)=',len(data)
        print ' len(data[0])=',len(data[0])
        
        outwrite = open('panstarrs_out','w')
        
        keys = ['SeqNr',['dec','Dec'],['ra','Ra'],'raErr','decErr','umag','gmag','rmag','imag','Bmag','Vmag','Rmag','Imag','zmag','uerr','gerr','rerr','ierr','Berr','Verr','Rerr','Ierr','zerr','umg','gmr','rmi','imz','BmV','VmR','RmI','Imz','umgerr','gmrerr','rmierr','imzerr','BmVerr','VmRerr','RmIerr','Imzerr','A_WCS','B_WCS','THETAWCS','Flag','Clean',['ra','ALPHA_J2000'],['dec','DELTA_J2000']]

        #keys = ['SeqNr',['dec','Dec'],['ra','Ra'],'raErr','decErr','umag','gmag','rmag','imag','Bmag','Vmag','Rmag','Imag','zmag','uerr','gerr','rerr','ierr','Berr','Verr','Rerr','Ierr','zerr','umg','gmr','rmi','imz','BmV','VmR','RmI','Imz','umgerr','gmrerr','rmierr','imzerr','BmVerr','VmRerr','RmIerr','Imzerr','flags_u','flags_g','flags_r','flags_i','flags_z','A_WCS','B_WCS','THETAWCS','Flag','Clean',['ra','ALPHA_J2000'],['dec','DELTA_J2000']]
	#adam-SHNT# this is the point where I'll have to get the panstarrs catalog to start from!
	#adam-SHNT# on this cat: /nfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/PHOTOMETRY/astrefcat-stars_only.txt

	#adam-ask-anja# are these corrections for sdss applicable for panstarrs?
	#answer: this doesn't really matter that much
	ab_correction = {'u':-0.036,'g':0.012,'r':0.010,'i':0.028,'z':0.040}
        seqnr = 1
        for els in range(len(data)): 
        	clean = data[els]['clean']

		#pogson converts from luptitudes to magnitudes, and is not needed for PANSTARRS
		#u = convert_to_pogson(float(data[els][mag_type + 'Mag_u']),'u') + ab_correction['u']
		#g = convert_to_pogson(float(data[els][mag_type + 'Mag_g']),'g') + ab_correction['g']
		#r = convert_to_pogson(float(data[els][mag_type + 'Mag_r']),'r') + ab_correction['r']
		#i = convert_to_pogson(float(data[els][mag_type + 'Mag_i']),'i') + ab_correction['i']
		#z = convert_to_pogson(float(data[els][mag_type + 'Mag_z']),'z') + ab_correction['z']
        
        	u = float(data[els][mag_type + 'Mag_u'])
                g = float(data[els][mag_type + 'Mag_g'])
                r = float(data[els][mag_type + 'Mag_r'])
                i = float(data[els][mag_type + 'Mag_i'])
                z = float(data[els][mag_type + 'Mag_z'])
        	uerr = float(data[els][mag_type + 'MagErr_u']) ; gerr = float(data[els][mag_type + 'MagErr_g']) ; rerr = float(data[els][mag_type + 'MagErr_r']) ; ierr = float(data[els][mag_type + 'MagErr_i']) ; zerr = float(data[els][mag_type + 'MagErr_z'])
        
		#adam-old: I have to change this, since there is no u band for PANSTARRS
		#	data[els]['Bmag'] = u - 0.8116*(u - g) + 0.1313#  sigma = 0.0095
		#	data[els]['Berr'] = math.sqrt( (uerr*0.19)**2. + (0.8119*gerr)**2.) 
		#adam-new# using Lupton 2005 conversion
                #B = g + 0.3130*(g - r) + 0.2271#  sigma = 0.0107
		if g>0 and r>0:
			data[els]['Bmag'] = g + 0.3130*(g - r) + 0.2271 #  sigma = 0.0107
		else:
			data[els]['Bmag'] = -999.0
        	data[els]['Berr'] = math.sqrt( (gerr*1.3130)**2 + (rerr*0.3130)**2 + 0.0107**2)
                
                #V = g - 0.2906*(u - g) + 0.0885#  sigma = 0.0129
		if g>0 and r>0:
			data[els]['Vmag'] = g - 0.5784*(g - r) - 0.0038#  sigma = 0.0054
		else:
			data[els]['Vmag'] = -999.0
        	data[els]['Verr'] = math.sqrt( (gerr*0.42)**2. + (0.57*rerr)**2.) 
                
                #R = r - 0.1837*(g - r) - 0.0971#  sigma = 0.0106
		if i>0 and r>0:
                	data[els]['Rmag'] = r - 0.2936*(r - i) - 0.1439#  sigma = 0.0072
		else:
			data[els]['Rmag'] = -999.0
        	data[els]['Rerr'] = math.sqrt( (rerr*0.71)**2. + (0.29*ierr)**2.) 
                
		if i>0 and r>0:
			data[els]['Imag'] = r - 1.2444*(r - i) - 0.3820#  sigma = 0.0078
		else:
			data[els]['Imag'] = -999.0
        	data[els]['Ierr'] = math.sqrt( (rerr*0.24)**2. + (1.244*ierr)**2.) 
                #I = i - 0.3780*(i - z)  -0.3974#  sigma = 0.0063  
                
                data[els]['umag'] = u ; data[els]['gmag'] = g ; data[els]['rmag'] = r ; data[els]['imag'] = i ; data[els]['zmag'] = z
        
        	data[els]['umg'] = -999.0
		if data[els]['rmag']>0 and data[els]['gmag']>0:
			 data[els]['gmr'] = data[els]['gmag'] - data[els]['rmag']  
		else:
			 data[els]['gmr'] = -999.0
		if data[els]['rmag']>0 and data[els]['imag']>0:
			 data[els]['rmi'] = data[els]['rmag'] - data[els]['imag']  
		else:
			 data[els]['rmi'] = -999.0
		if data[els]['zmag']>0 and data[els]['imag']>0:
			 data[els]['imz'] = data[els]['imag'] - data[els]['zmag']  
		else:
			 data[els]['imz'] = -999.0
        	data[els]['uerr'] = uerr ; data[els]['gerr'] = gerr ; data[els]['rerr'] = rerr ; data[els]['ierr'] = ierr ; data[els]['zerr'] = zerr
        
        	data[els]['umgerr'] = math.sqrt(data[els]['uerr']**2. + data[els]['gerr']**2.) 
                data[els]['gmrerr'] = math.sqrt(data[els]['gerr']**2. + data[els]['rerr']**2.) 
                data[els]['rmierr'] = math.sqrt(data[els]['rerr']**2. + data[els]['ierr']**2.) 
                data[els]['imzerr'] = math.sqrt(data[els]['ierr']**2. + data[els]['zerr']**2.) 

		if data[els]['Bmag']>0 and data[els]['Vmag'] > 0:
			data[els]['BmV'] = data[els]['Bmag'] - data[els]['Vmag'] 
		else:
			data[els]['BmV'] = -999.0
		if data[els]['Rmag']>0 and data[els]['Vmag'] > 0:
			data[els]['VmR'] = data[els]['Vmag'] - data[els]['Rmag'] 
		else:
			data[els]['VmR'] = -999.0
		if data[els]['Rmag']>0 and data[els]['Imag'] > 0:
			data[els]['RmI'] = data[els]['Rmag'] - data[els]['Imag'] 
		else:
			data[els]['RmI'] = -999.0
		if data[els]['zmag']>0 and data[els]['Imag'] > 0:
			data[els]['Imz'] = data[els]['Imag'] - data[els]['zmag'] 
		else:
			data[els]['Imz'] = -999.0

                data[els]['BmVerr'] = math.sqrt(data[els]['Berr']**2. + data[els]['Verr']**2.) 
                data[els]['VmRerr'] = math.sqrt(data[els]['Verr']**2. + data[els]['Rerr']**2.) 
                data[els]['RmIerr'] = math.sqrt(data[els]['Rerr']**2. + data[els]['Ierr']**2.) 
                data[els]['Imzerr'] = math.sqrt(data[els]['Ierr']**2. + data[els]['zerr']**2.) 
        	#error = (float(data[els]['rowcErr_r'])**2. + float(data[els]['colcErr_r'])**2.)**0.5*0.4/3600.
        	#if error < 0.0004: error=0.0004
        	data[els]['A_WCS'] = 0.0004 #error #data[els]['Err'] #'0.0004'
        	data[els]['B_WCS'] = 0.0004 #error #data[els]['decErr'] #'0.0004'
        	data[els]['THETAWCS'] = '0'
        	data[els]['Clean'] = str(clean) 
        	data[els]['Flag'] = '0' #str(clean) 
        	seqnr += 1 
        	data[els]['SeqNr'] = seqnr
        
        	lineh = ""	
        	for key in keys:                                                                             
        		if len(key) == 2:	
        			key_dict = key[0]
        			key  = key[1]
        		else: 
        			key_dict = key
        		if (key == 'SeqNr' or key_dict=='ra' or key_dict=='dec' or key[0:3] == 'Fla'): 
        			num = '%(s)s' % {'s' : str(data[els][key_dict])}
        		else:
        			num = '%(num).4f' % {'num' : float(data[els][key_dict])}
        			num = '%s' % num
        		num.strip()
        		lineh = lineh + num  + " "
        	outwrite.write(lineh + "\n")
        outwrite.close()
        
        #lineh= "lc -C -B "
        #for key in data[els].keys():
        #	lineh = lineh + " -N '1 1 " + str(key) + "' "
        #lineh = lineh + " < outwrite > outf.cat"
        #print lineh
        #os.system(lineh)
        
        asc = open('asctoldac_panstarrs.conf','w')
        asc.write('VERBOSE = DEBUG\n')
        for column in keys: 
        	if len(column) == 2:	
        		name = column[1]
        	else: name = column 
        	if column == 'objID' or column[0:3] == 'fla': 
        		type = 'STRING'
        		htype = 'STRING'
        		depth = '128'
        	elif column == 'Flag':
        		type = 'SHORT'
        		htype = 'INT'
        		depth = '1'
        	elif column == 'SeqNr':
        		type = 'LONG'
        		htype = 'INT'
        		depth = '1'
        	elif len(column) ==2: #column == 'Ra' or column == 'Dec':
        		type = 'DOUBLE'
        		htype = 'FLOAT'
        		depth = '1'
        	else: 
        		type = 'FLOAT'
        		htype = 'FLOAT'
        		depth = '1'
        	asc.write('#\nCOL_NAME = ' + name + '\nCOL_TTYPE= ' + type + '\nCOL_HTYPE= ' + htype + '\nCOL_COMM= ""\nCOL_UNIT= ""\nCOL_DEPTH= ' + depth + '\n')

        asc.close()

        command = "asctoldac -i panstarrs_out -c asctoldac_panstarrs.conf -t STDTAB -o " + outcat
        ooo=os.system(command)
        print command
	if ooo!=0: raise Exception('asctoldac command failed!')

	os.chdir(startdir)
        if len(data) > 10:
            cov = True
        else: cov = False
        return cov, outcat

if __name__ == '__main__':
        img = sys.argv[1]
        outcat = sys.argv[2]
        mag_type = 'star'

	run(img, outcat, mag_type,None,illum_cat='test.cat')
