import os
p = open(os.environ['subdir'] + '/lensing.bands','r').readlines()
i = 0
for l in p:
    import re
    res = re.split('\s+',l)
    f_in = os.environ['subdir'] + '/' + res[0] + '/' + res[1] + '/SCIENCE/coadd_' + res[0] + '_good/coadd.reg'
    from glob import glob
    command = 'cp ' + f_in +  ' ' +  os.environ['subdir'] + '/' + res[0] + '/' + res[1] + '/SCIENCE/handmasking.reg'
    print command
    os.system(command)

    if glob(f_in):
        i += 1
print i
