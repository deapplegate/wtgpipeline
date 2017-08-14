import os
import os
cluster = 'HDFN'
SUBARUDIR = '/nfs/slac/g/ki/ki05/anja/SUBARU/'
output = SUBARUDIR + cluster + '/PHOTOMETRY/'  + cluster + 'spec.cat'
command = 'ldactoasc -i tkrs_by_ra.fits -t tkrs_by_ra.tab -k id ra dec z > op'
os.system('rm op2')
os.system('rm op')
os.system(command)
os.system('asctoldac -i op -o op2 -c ./photconf/zspec.conf')
command = '''ldacfilter -i op2 -t OBJECTS -c '(Z > 0);' -o ''' + output
os.system(command)
