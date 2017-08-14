
''' input ra limits and get back a list of dictionaries with parameters '''

import sqlcl

ramin = 15.0 
ramax = 15.1 
decmin = 15.0 
decmax = 15.1 

query = "select ra, dec, psfMag_g, psfMagErr_g, psfMag_r, psfMagErr_r, flags, clean from star where ra between " + str(ramin) + " and  " + str(ramax) + " and  dec between " + str(decmin) + " and " +str(decmax)  + " AND flags & dbo.fPhotoFlags('BLENDED') = 0 "

lines = sqlcl.query(query).readlines()

columns = lines[0][:-1].split(',')
print columns
data = []

for line in range(1,len(lines[1:])+1): 
	dt0 = {}
	for j in range(len(lines[line][:-1].split(','))): 
                dt0[columns[j]] = lines[line][:-1].split(',')[j]
	import string
	if string.find(lines[line][:-1],'font') == -1: 
		data.append(dt0)
        print dt0

print len(data)
print len(data[0])
