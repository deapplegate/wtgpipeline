def run(command):
	print command
	system(command)



cluster = 'A2219'

from os import *

i = iter(['/tmp/tmpf' + str(j) for j in range(300)]

base = '/nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/PHOTOMETRY/'
file = base + 'all.cat'
sdss = base + 'sdss.cat '

run('preastrom -i ' + temp[i.next()] + ' -o ' + temp[i.next()] + ' -p  ')

run('ldacconv -b 1 -c R -i ' + file + ' -o /tmp/all.conv')

run('ldacrentab -i /tmp/all.conv -o /tmp/all.stdtab.conv -t OBJECTS STDTAB ')

run('ldacfilter -i /tmp/all.stdtab.conv -o /tmp/all.filt -c "(CLASS_STAR>0.98) AND (Flag=0);" -t STDTAB')

run('associate -i /tmp/all.filt ' + sdss + ' -o /tmp/subaru.asc /tmp/sdss.asc -t STDTAB -c ./photconf/fullphotom.conf.associate')

run('ldacfilter -i /tmp/subaru.asc -o /tmp/subaru.asc.filt -c "(Pair_1>0);" -t STDTAB')

run('ldacfilter -i /tmp/sdss.asc -o /tmp/sdss.asc.filt -c "(Pair_0>0);" -t STDTAB')

