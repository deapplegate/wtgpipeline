import os, re

file = os.environ['sne'] + '/cosmos/cosmos_zphot_mag25.tbl'
f = open(file,'r').readlines()[0:30]

i = 0
cols = {}
for line in f:
    if line[0] == '|' and i==0:
        names = re.split('\|',line)[1:-1]
        i += 1 
    elif line[0] == '|' and i==1:
        format = re.split('\|',line)[1:-1]
        break

ds = ''
for i in range(len(names)):       
    ds += 'COL_NAME = ' + names[i].replace(' ','') + '\nCOL_TTYPE = DOUBLE\nCOL_HTYPE = FLOAT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n'

print ds
fw = open('temp.conf','w')
fw.write(ds)
fw.close()

file = os.environ['sne'] + '/cosmos/cosmos_zphot_mag25.nums'
command = 'asctoldac -a ' + file + ' -o ' + file + '.fits -c temp.conf'
os.system(command)



