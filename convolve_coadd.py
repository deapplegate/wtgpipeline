import os, sys, anydbm, time, re
import bashreader, commands

cluster = sys.argv[1]
whichpass = sys.argv[2]
if whichpass == '#': whichpass = '' 
filters = sys.argv[3:]
print filters

#dict = bashreader.parseFile('progs.ini')
#SUBARUDIR = dict['SUBARUDIR']
IMAGE='coadd'
SUBARUDIR='/nfs/slac/g/ki/ki02/xoc/anja/SUBARU/'

WORKDIR=SUBARUDIR+'/'+cluster+'/PHOTOMETRY'

seeing_array=[]
for filter in filters:
	from glob import *
        IMAGEDIR=SUBARUDIR+ '/' + cluster + '/' + filter + '/SCIENCE/coadd_' + cluster + whichpass
	if len(glob(IMAGEDIR) ) == 0: 
        	IMAGEDIR=SUBARUDIR+ '/' + cluster + '/' + filter + '/SCIENCE/coadd_' + cluster 
        OUTPUT_WORKDIR=SUBARUDIR + '/' +cluster + '/' + filter + '/PHOTOMETRY/'
	print IMAGEDIR
	command = 'dfits ' + IMAGEDIR + '/' + IMAGE + '.fits | fitsort -d SEEING'
	print command
	print commands.getoutput(command)
        SEEING=re.split('\s+',commands.getoutput(command))[1]
	print SEEING 
	seeing_array.append([SEEING,filter])

seeing_array.sort()
print seeing_array	
worst_filter = seeing_array[-1][1]
print 'Worst Seeing is in the ' + worst_filter + ' filter'



stellar_positions = open(WORKDIR +'/' + IMAGE + '.positions','r').readlines()
position_list = []
import random
for i in range(15):
	rr = int(random.random()*len(stellar_positions))
	position_list.append(re.split('\s+',stellar_positions[rr])[1:3])
	
input = open('input','w')
output = open('output','w')
kernels = open('kernels','w')

pp = open('pp.cl','w')

for filter in filters:
        IMAGEDIR=SUBARUDIR+ '/' + cluster + '/' + filter + '/SCIENCE/coadd_' + cluster + whichpass
	if len(glob(IMAGEDIR) ) == 0: 
        	IMAGEDIR=SUBARUDIR+ '/' + cluster + '/' + filter + '/SCIENCE/coadd_' + cluster 

        OUTPUT_WORKDIR=SUBARUDIR + '/' +cluster + '/' + filter + '/PHOTOMETRY/'

        positions = open("positions",'w')
        for ele in position_list:
        	positions.write(str(ele[0]) + " " + str(ele[1]) + "\n")
	positions.close()
	img =   filter + '.fits'
	img = img.replace("//","/")
	if worst_filter != filter:
		tempim = "/tmp/" + filter + ".fits"
		os.system('cp ' + IMAGEDIR + '/' + IMAGE + ".fits " + tempim)
		input.write(tempim + "\n")
		img = OUTPUT_WORKDIR + '/' + IMAGE + '.smooth.fits'
		img = img.replace("//","/")
		pp.write("del " + img + '\n')
		output.write(img + "\n")
		kernelimg = filter + "kernel.fits"
		os.system("rm " + kernelimg)
		kernels.write(kernelimg + "\n")

#copy over the image from the worst seeing band
IMAGEDIR=SUBARUDIR+ '/' + cluster + '/' + worst_filter + '/SCIENCE/coadd_' + cluster + whichpass
OUTPUT_WORKDIR=SUBARUDIR + '/' +cluster + '/' + filter + '/PHOTOMETRY/'
if len(glob(IMAGEDIR) ) == 0: 
	IMAGEDIR=SUBARUDIR+ '/' + cluster + '/' + worst_filter + '/SCIENCE/coadd_' + cluster 



#IMAGEDIR=SUBARUDIR + '/' +cluster + '/' + worst_filter + '/PHOTOMETRY/'
img1 = IMAGEDIR + '/' + IMAGE + '.fits'
img2 = OUTPUT_WORKDIR + '/' + IMAGE + '.smooth.fits'
os.system("cp " + img1 + " " + img2)
input.close()

reference = open('reference','w')
img = IMAGEDIR + '/' + IMAGE + '.fits'
img = img.replace("//","/")
reference.write(img)
reference.close()
uu = "psfmatch @input " + img + " positions @kernels output=@output dnx=31 dny=31 pnx=15 pny=15\nlogout\n" 
#uu = "psfmatch B.fits " + img + " positions kernel output=test.fits" 
pp.write(uu)
pp.close()
