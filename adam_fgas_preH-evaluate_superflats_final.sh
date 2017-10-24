#!/bin/bash -xv
cd /nfs/slac/g/ki/ki18/anja/SUBARU/

# ds9 -tile grid layout 5 2 -geometry 2000x2000 -frame lock image -cmap bb -scale limits .99 1.01 SUPA012604*.fits -zoom to fit -saveimage png -saveimage png plt10ims_SUPA012604.png -quit

#for pprun in 2010-12-05_W-J-V 2010-03-12_W-J-V 2010-03-12_W-S-I+ 2007-02-13_W-S-I+ 2009-03-28_W-S-I+
#for pprun in 2010-03-12_W-J-V 2010-03-12_W-S-I+ 2007-02-13_W-S-I+ 2009-03-28_W-S-I+
for pprun in 2009-03-28_W-S-I+
do
	echo ${pprun} >> ~/wtgpipeline/adam_preH_superflat_progress-${pprun}.txt
	#dfits -x 1 ${pprun}/SCIENCE/ORIGINALS/SUP*.fits | fitsort OBJECT DOTHIS TOTHIS > ${pprun}/superflat_stats.txt
	#dfits -x 1 ${pprun}/SCIENCE/ORIGINALS/SUP*.fits | fitsort OBJECT DOTHIS TOTHIS >> superflat_stats_preH.txt
	awk '{print $1}' ${pprun}/superflat_stats.txt | cut -c -11 > ${pprun}/proto_superflat_exclusion 
	sed -i.old 's/FILE/#=keep x=remove S=shadow \*=would keep some/g' ${pprun}/proto_superflat_exclusion
	rm ${pprun}/proto_superflat_exclusion.old
	echo "${pprun}: KEY  #=keep   x=remove   S=shadow   *=would keep some"
	objnum=`awk '{print $2}' ${pprun}/superflat_stats.txt | sort | uniq | sed '/OBJECT/d' | wc -l`
	objnames=`awk '{print $2}' ${pprun}/superflat_stats.txt | uniq | sed '/OBJECT/d' `
	echo "${objnum} objects : ${objnames}" >>  ~/wtgpipeline/adam_preH_superflat_progress-${pprun}.txt
	echo "Superflat status (everything fine, need S excluder, need * excluder, need more data):" >>  ~/wtgpipeline/adam_preH_superflat_progress-${pprun}.txt
	echo "" >>  ~/wtgpipeline/adam_preH_superflat_progress-${pprun}.txt
	for objname in $objnames
	do
		objnameplus=${objname%.[0-9]+[0-9][0-9][0-9][0-9]}
		objnameminus=${objname%.[0-9]-[0-9][0-9][0-9][0-9]}
		if [ ${#objnameplus} -lt ${#objname} ]; then objnameuse=${objnameplus}; elif [ ${#objnameminus} -lt ${#objname} ]; then objnameuse=${objnameminus}; else objnameuse=${objname} ;fi
		echo "ds9 -frame lock image -geometry 2000x2000 -cmap bb -scale limits .94 1.01 ${pprun}/SCIENCE_norm/BINNED/${objname}*/SUPA*mosOCFN.fits -zoom to fit -frame lock scale &"
		xv ${pprun}/SCIENCE_norm/BINNED/${objnameuse}_scale9[4-6].png
	done
	wait 15
	vim -o ${pprun}/proto_superflat_exclusion ${pprun}/superflat_stats.txt 
done
