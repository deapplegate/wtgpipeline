f = open('hdfn_spectroscopic_zs.txt').readlines()
hdfn = open('hdfn.reg','w')
hdfn.write('global color=green dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\nfk5\n')
index = 0
hdfn_cat = open('op','w')
for l in f:
    if l[0] == '1':
        import re
        res = re.split('\s+',l)
        hdfn.write('circle(' + res[0] + ',' + res[1] + ',2")\n')
        index += 1

        hdfn_cat.write(str(index) + ' ' + res[0] + ' ' + res[1] + ' ' + res[8] + '\n')

hdfn.close()
hdfn_cat.close()

import os
cluster = 'HDFN'
SUBARUDIR = '/nfs/slac/g/ki/ki05/anja/SUBARU/'
output = SUBARUDIR + cluster + '/PHOTOMETRY/'  + cluster + 'spec.cat'
os.system('asctoldac -i op -o ' + output + ' -c ./photconf/zspec.conf')
print output


