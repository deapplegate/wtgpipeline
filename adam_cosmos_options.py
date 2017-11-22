#! /usr/bin/env python
#adam-old# cat_switch='oldcat'
#adam-old# cat_switch='newcat_matched'
cat_switch='4cccat'

#adam: toggle from using single point zp_best to drawing a random sample from the p(z) dist'n by changing `zchoice_switch` to `dist ` or `point` in cosmos_sim.py
#adam-old# zchoice_switch='dist'
zchoice_switch='point'

## place this line in other scripts:
#from adam_cosmos_options import zchoice_switch, cat_switch
#from adam_cosmos_options import zchoice_switch, cat_switch, cosmos_idcol
if cat_switch=='oldcat':
	cosmos_idcol='id'
elif cat_switch=='newcat_matched':
	cosmos_idcol='id'
elif cat_switch=='4cccat':
	cosmos_idcol='SeqNr'

## make this useful for .sh files too:
filterset='BVRIZ'
dirtag='CAT%s-Z%s' % (cat_switch, zchoice_switch)
datadir='/nfs/slac/g/ki/ki18/anja/SUBARU/cosmossims2017_'+dirtag
if __name__=='__main__':
	flini=open('cosmos_mass_bias.ini','w')
	flini.write('export dirtag='+dirtag+'\n')
	flini.write('export datadir='+datadir+'\n')
	flini.write('export filterset='+filterset+'\n')
	flini.write('export zchoice_switch='+zchoice_switch+'\n')
	flini.write('export cat_switch='+cat_switch+'\n')
	flini.write('export cosmos_idcol='+cosmos_idcol+'\n')
	flini.close()

