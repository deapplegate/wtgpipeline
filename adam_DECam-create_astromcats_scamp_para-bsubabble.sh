#!/bin/bash
set -xv
#adam-does# basically this is do_Subaru_register_4batch.sh "astrom" mode
export cluster=A2204
export INSTRUMENT=DECam

lookupfile=/nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
ra=`grep ${cluster} ${lookupfile} | awk '{print $3}'`
dec=`grep ${cluster} ${lookupfile} | awk '{print $4}'`
outdir="/nfs/slac/kipac/fs1/u/awright/batch_files/"                                                     

#ALLCATS=`\ls /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/{u,g,r,i,z,Y}_DECam/single_V0.0.2A/dec*_*OXCLFSF.sub.fits`
LINE=""
#for filter in u g r i z Y
for filter in g r i z Y
do
        ###./adam_DECam-create_astromcats_scamp_para.sh /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/${filter}_DECam/ single_V0.0.2A/
	for chipsnum in 1 2 3 4 5 6
	do
		#sed "s/filter=u/filter=${filter}/g" adam_DECam-create_astromcats_scamp_para-bsub_u_chipsnum${chipsnum}.sh > adam_DECam-create_astromcats_scamp_para-bsub_${filter}_chipsnum${chipsnum}.sh
		#chmod u+x adam_DECam-create_astromcats_scamp_para-bsub_${filter}_chipsnum${chipsnum}.sh
		#adam_DECam-create_astromcats_scamp_para-bsub_${filter}_chipsnum${chipsnum}.sh
		bsub -W 6500 -R rhel60 -o ${outdir}/OUT-adam_DECam-create_astromcats_scamp_para-bsub_${filter}_chipsnum${chipsnum}.out -e ${outdir}/OUT-adam_DECam-create_astromcats_scamp_para-bsub_${filter}_chipsnum${chipsnum}.err ./adam_DECam-create_astromcats_scamp_para-bsub_${filter}_chipsnum${chipsnum}.sh
		#./adam_DECam-create_astromcats_scamp_para-bsub${filter}chipsnum${chipsnum}.sh 2>&${chipsnum} | tee -a scratch/OUT-create_astromcats_scamp_para-bsub${filter}chipsnum${chipsnum}.log
	done
	# ./adam_DECam-create_astromcats_scamp_para-bsub_u_chipsnum1.sh 2>&1 | tee -a scratch/OUT-create_astromcats_scamp_para-bsub_u_chipsnum1.log
        # ./adam_DECam-create_astromcats_scamp_para-bsub_u_chipsnum2.sh 2>&1 | tee -a scratch/OUT-create_astromcats_scamp_para-bsub_u_chipsnum2.log
        # ./adam_DECam-create_astromcats_scamp_para-bsub_u_chipsnum3.sh 2>&1 | tee -a scratch/OUT-create_astromcats_scamp_para-bsub_u_chipsnum3.log
        # ./adam_DECam-create_astromcats_scamp_para-bsub_u_chipsnum4.sh 2>&1 | tee -a scratch/OUT-create_astromcats_scamp_para-bsub_u_chipsnum4.log
        # ./adam_DECam-create_astromcats_scamp_para-bsub_u_chipsnum5.sh 2>&1 | tee -a scratch/OUT-create_astromcats_scamp_para-bsub_u_chipsnum5.log
        # ./adam_DECam-create_astromcats_scamp_para-bsub_u_chipsnum6.sh 2>&1 | tee -a scratch/OUT-create_astromcats_scamp_para-bsub_u_chipsnum6.log

done
