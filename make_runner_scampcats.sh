#!/bin/bash

#adam-does# basically this is do_Subaru_register_4batch.sh "astrom" mode
export cluster=A2204
export INSTRUMENT=DECam

for filter in u g r i z
do
	echo "export cluster=A2204 ; export INSTRUMENT=DECam"
	echo "./parallel_manager.sh make_scamp_cats.sh ${filter} 2>&1 | tee -a OUT-make_scamp_cats_${filter}.log"
done
