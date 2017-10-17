#!/bin/bash
set -xv

#for filter in u g r i z Y
for filter in i
do                                                                                                                           
        #num=`\ls /nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/${cluster}/${filter}_DECam/single_V0.0.2A/dec*_*OXC*.flag.fits | wc -l`
        #\/nfs\/slac\/g\/ki\/ki18\/anja\/DECAM\/CLUSTERSCOLLAB_V0.0.2\/${cluster}\/${filter}_DECam\/
        #\ls /nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/${filter}_DECam/single_V0.0.2A/dec*_*OXCL*.sub.fits > subims.log 
        #\ls /nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/${filter}_DECam/single_V0.0.2A/dec*_*OXCL*.weight.fits > weightims.log
        #\ls /nfs/slac/g/ki/ki18/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/${filter}_DECam/single_V0.0.2A/dec*_*OXCL*.flag.fits > flagims.log
        #sub_wt_flag=`wc -l subims.log weightims.log flagims.log`
        #echo $filter , $sub_wt_flag >> decam_data.log
        #./parallel_manager.sh ./create_astromcats_scamp_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE WEIGHTS
        for chip in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62
        do
                num_fls=`\ls ~/A2204_data/${filter}_DECam/single_V0.0.2A/cat_scamp/dec[0-9]*_${chip}OXC*.cat | wc -l`
		#echo $filter $chip $num_fls >> countit_a2204.log
		echo $filter $chip $num_fls >> i.tmp
	done
done
