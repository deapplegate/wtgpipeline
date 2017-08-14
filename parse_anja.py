import re, sys 

file = open(sys.argv[1]).readlines()


spltdict = re.split('\s+',file[0])


stars = []
for line in file[1:]:
	splt = re.split('\s+',line)
	for ele
	

