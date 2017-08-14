yy = open('ee','r').readlines()
import re
for filterlist in [['b','B'],['i','IC'],['z','Z+']]:
	filter = filterlist[1]	
	lowerfilter = filterlist[0]
	uu = open('list_' + filter,'w')
	qq = []

	file = lowerfilter + '_dates'
        ww = open(file,'r').readlines()
	for line in ww:
        	date = ((re.split('\s+',line)[1]))
		qq.append(date)
	for line in yy:
		import string
		if string.find(line,filter) != -1:
			qq.append(line[:-1])
	qq.sort()			
	oo = []
	for ele in qq:
		tt = 0
		for ue in oo: 
			if ue == ele: tt = 1
		if tt == 0:	
			oo.append(ele)
			uu.write(ele + '\n')
