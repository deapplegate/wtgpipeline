import matplotlib
import pylab, sys, re, os
file = sys.argv[1]

#now need to read 
command = "ldactoasc -b  -i  ldactoasc -i /nfs/slac/g/ki/ki02/xoc/anja/Stetson/Stetson_std_2.0.cat -t STDTAB -k BmV VmR > ./ldac_tmp2" 
os.system(command)
command = "ldactoasc -b  -i  ldactoasc -i coadd.smooth.cat -t STDTAB -k BmV VmR > ./ldac_tmp" 
print command + '\n\n\n'
os.system(command)

lines = open('./ldac_tmp2','r').readlines()
x = []
y = []
z = []
err = []

for line in lines:
	spt = re.split('\s+',line)
	b_v = float(spt[0])
	v_r = float(spt[1])
	if -10 < b_v < 10 and -10 < v_r < 10:		
		print spt
		x.append(b_v)

		y.append(v_r)

		#err.append(sdss_error)

x2 = x[0:300]
y2 = y[0:300]

#pylab.scatter(x2,y2)
		
#pylab.errorbar(x,y,err,fmt='o',markersize=0.01)


#file = 'ldac_tmp'
lines = open(file,'r').readlines()
x = []
x_sdss = []
y = []
z = []
err = []

for line in lines:
	spt = re.split('\s+',line)
	b_v = float(spt[0])
	v_r = float(spt[1])
	b_v_sdss = float(spt[2])
	v_r_sdss = float(spt[3])

	b_sdss = float(spt[4])
	v_sdss = float(spt[5])
	r_sdss = float(spt[6])

	b = float(spt[7])
	v = float(spt[8])
        r = float(spt[9])


	#if 1 == 1:		

	if -10 < b_v < 10 and -10 < v_r < 10 and -10 < b_v_sdss < 10 and -10 < v_r_sdss < 10 and b_v_sdss!=0 and v_r_sdss!=0:		
		print spt
		x.append(b_v)

		y.append(v_r)
		x_sdss.append(r-r_sdss)

		z.append(r_sdss)
		#err.append(sdss_error)
print len(x)
		
pylab.scatter(z,x_sdss,color='red')
#pylab.ylim(-0.3,0.3)
#pylab.errorbar(x,y,err,fmt='o',markersize=0.01)
pylab.show()	


