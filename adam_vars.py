SUBARUDIR="/nfs/slac/g/ki/ki18/anja/SUBARU"
INSTRUMENT="SUBARU"
cluster="MACS1226+21"
ending="OCF"
filt_runs=["W-C-RC_2010-02-12","W-C-RC_2006-03-04","W-C-IC_2010-02-12","W-C-IC_2011-01-06","W-J-B_2010-02-12","W-J-V_2010-02-12","W-S-G+_2010-04-15","W-S-I+_2010-04-15","W-S-Z+_2011-01-06"]
filters=["W-C-IC","W-C-RC","W-J-B","W-J-V","W-S-G+","W-S-I+","W-S-Z+"]

cluster="MACS0416-24"
filt_runs=["W-C-RC_2010-11-04","W-J-B_2010-11-04","W-S-Z+_2010-11-04"]
#ending="OCFR" when filter=W-C-RC and cluster="MACS0416-24"

#s=`copy in command`
#s.replace('$','')

s="./parallel_manager.sh add_regionmasks.sh {SUBARUDIR}/{cluster}/{filter}_{run} SCIENCE {ending} WEIGHTS {filter} 2>&1 | tee -a scratch/OUT-add_regionmasks_{cluster}_{filter}_{run}.final.log"
for fr in filt_runs:
	filter,run=fr.split('_')
	print s.format(**locals())
