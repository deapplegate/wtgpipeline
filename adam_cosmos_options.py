#! /usr/bin/env python
#adam-options# cat_switch='oldcat'
#adam-options# cat_switch='newcat_matched'
#adam-options# cat_switch='4cccat'

#adam-options# filterset='UGRIZ'
#adam-options# filterset='BVRIZ'

# toggle from using single point zp_best to drawing a random sample from the p(z) dist'n by changing `zchoice_switch` to `dist ` or `point`
#adam-options# zchoice_switch='dist'
#adam-options# zchoice_switch='point'

#done: cat_switch='4cccat';filterset='UGRIZ';zchoice_switch='point'
#done: cat_switch='newcat_matched';filterset='UGRIZ';zchoice_switch='point'
#done: cat_switch='newcat_matched';filterset='UGRIZ';zchoice_switch='dist'
cat_switch='4cccat';filterset='BVRIZ';zchoice_switch='point'
#togo: cat_switch='newcat_matched';filterset='BVRIZ';zchoice_switch='point'
#togo: cat_switch='newcat_matched';filterset='BVRIZ';zchoice_switch='dist'


## place this line in other scripts:
#from adam_cosmos_options import zchoice_switch, cat_switch, cosmos_idcol
if cat_switch=='oldcat':
	cosmos_idcol='id'
elif cat_switch=='newcat_matched':
	cosmos_idcol='id'
elif cat_switch=='4cccat':
	cosmos_idcol='SeqNr'

## make this useful for .sh files too:
dirtag='simcl_CAT%s-Z%s' % (cat_switch, zchoice_switch)
datadir='/nfs/slac/g/ki/ki18/anja/SUBARU/simcl/'+dirtag
if __name__=='__main__':
	flini=open('cosmos_mass_bias.ini','w')
	flini.write('export dirtag='+dirtag+'\n')
	flini.write('export datadir='+datadir+'\n')
	flini.write('export filterset='+filterset+'\n')
	flini.write('export zchoice_switch='+zchoice_switch+'\n')
	flini.write('export cat_switch='+cat_switch+'\n')
	flini.write('export cosmos_idcol='+cosmos_idcol+'\n')
	flini.close()

