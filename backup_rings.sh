#!/bin/bash

subaru=/nfs/slac/g/ki/ki05/anja/SUBARU

clusters=`ls ${subaru}`

curdate=`date +%y-%m-%d_%H-%M`

backupdir=${subaru}/rings_backup_${curdate}
if [ -d ${backupdir} ]; then
    echo "Backup Dir Exists!?"
    exit 1
fi
mkdir ${backupdir}

for cluster in $clusters; do

    filters=`ls ${subaru}/${cluster}`
    for filter in $filters; do

	if [ -d ${subaru}/${cluster}/${filter}/SCIENCE/ ]; then

	    suppressiondirs=`ls ${subaru}/${cluster}/${filter}/SCIENCE/ | grep suppression`
	    for suppressiondir in ${suppressiondirs}; do

		if [ -d ${subaru}/${cluster}/${filter}/SCIENCE/${suppressiondir} ]; then
		    
		    mkdir -p ${backupdir}/${cluster}/${filter}
		    cp -r ${subaru}/${cluster}/${filter}/SCIENCE/${suppressiondir} ${backupdir}/${cluster}/${filter}/${suppressiondir}

		fi

	    done

	fi

    done

done


tar -zcvf ${subaru}/rings_backup_${curdate}.tar.gz ${backupdir}
chmod 444 ${subaru}/rings_backup_${curdate}.tar.gz