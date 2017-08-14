ii = open('ii','r').readlines()
nherve = open('nherve','w')
list = []
for line in ii:
	import re
	spl = re.split('\s+',line)	
	list.append(spl)

finallist = []
for obj in list:
	no = 0
	for entry in finallist:	
		dist = ((float(entry[0])-float(obj[0]))**2. + (float(entry[1]) - float(obj[1]))**2.)**0.5
		if dist < 0.1:
			no = 1
	
	if no == 0:
		finallist.append(obj)
finallist.sort()
for obj in finallist:
	nherve.write(reduce(lambda x,y: x + ' ' + y, obj) + '\n')

