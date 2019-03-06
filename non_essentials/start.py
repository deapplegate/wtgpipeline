
dtop = {'OBJNAME':'MACS1149+22','PPRUN':'2000-12-27_W-C-IC'}
''' retrieve all random fits '''
db_keys_f = describe_db(c,['fit_db'])
command="SELECT * from fit_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and sample_size like 'rand%'"           
print command                                                  
c.execute(command)                                             
results=c.fetchall()                                           
random_dict = {}
for line in results:
    drand = {}  
    for i in range(len(db_keys_f)):
        drand[db_keys_f[i]] = str(line[i])
    import string
    if string.find(drand['sample_size'],'corr') != -1 and string.find(drand['sample_size'],'uncorr') == -1:
        if not drand['sample_size'].replace('corr','') in random_dict: random_dict[drand['sample_size'].replace('corr','')] = {}
        random_dict[drand['sample_size'].replace('corr','')]['corr'] = drand['reducedchi']
    if string.find(drand['sample_size'],'uncorr') == -1:
        if not drand['sample_size'].replace('uncorr','') in random_dict: random_dict[drand['sample_size'].replace('uncorr','')] = {}
        random_dict[drand['sample_size'].replace('uncorr','')]['uncorr'] = drand['reducedchi']

chi_diffs = []
for key in random_dict.keys():    
    random_dict['chi_diff'] = random_dict[key]['uncorr']/random_dict[key]['corr']
    chi_diffs.append(random_dict['chi_diff'])

import scipy
print 'mean', scipy.mean(chi_diffs)
print 'std', scipy.std(chi_diffs)
    
''' calculate the mean and std of the reduced chi sq improvement '''



''' calculate the variance in the best fit '''

''' retrieve all sdss tests '''

''' decide if good '''


???
???
