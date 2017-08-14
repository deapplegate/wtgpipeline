import matplotlib
import pylab, sys, re
file = sys.argv[1]

lines = open(file,'r').readlines()
x = []
y = []
z = []
err = []

for line in lines:
	spt = re.split('\s+',line)
	aptmag = float(spt[1])
	catmag = float(spt[2])
	radius = float(spt[3])
	star_class = float(spt[4])
	sdss_error = float(spt[5])
	color = float(spt[6])
	print color
	if aptmag != 0 and catmag < 40 and catmag > 10 and color > 0.5: # and radius < 3.3 and aptmag>-1.5:
		
		print spt
		x.append(aptmag)

		y.append(aptmag - catmag)

		z.append(radius)

		err.append(sdss_error)
		
#pylab.scatter(z,x)
pylab.errorbar(x,y,err,fmt='o',markersize=0.01)
pylab.show()	


