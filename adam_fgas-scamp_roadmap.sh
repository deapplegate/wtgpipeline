5 steps to doing this:
1.) make catalogs from images
	~/wtgpipeline/adam_DECam-create_astromcats_scamp_para.sh
	on batch with: adam_DECam-create_astromcats_scamp_para-make_parallelable.sh and make_scamp_cats.sh and make_runner_scampcats.sh
2.) make PANSTARRS reference catalog (stars are best, since so many detections)
	get catalogs from panstarrs_query: /nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/get_cats_and_combine/get_newcats.py
	combine those catalogs: /nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/get_cats_and_combine/A2204_combine_cats_properly.py
	fix output format and units of raMeanErr/decMeanErr: /nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/cat_fix/fix_cats.py
		asctoldac.config is needed
		final:
		/nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/run_scamp/astrefcat-stars_only.cat
		others:
		/nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/run_scamp/astrefcat-unfiltered.cat
		/nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/run_scamp/astrefcat.cat
		/nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/run_scamp/astrefcat-ng_cat.cat
3.) catalog filtering to make .ldac cats and combine them to make _scamp.cat catalogs
	might be worth doing this to chose which parts you want to include: vimdiff ~/wtgpipeline/adam_DECam-create_scamp_astrom_photom.sh /nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/run_scamp/adam_DECam-create_scamp_astrom_photom.sh
	(needs: DECam.ini DECam.ahead )
	/nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/run_scamp/adam_A2204_scamp_subaru_and_megaprime.sh
	some fixes to consider here: /gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/astrom_photom_scamp_PANSTARRS/adam_DECam-create_scamp_cats_no_ccd62.sh
4.) 1st pass scamp run
	/gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/astrom_photom_scamp_PANSTARRS/adam_A2204-scamp_pass1_final.sh
	tips for managing output here: bsub_scamp_examples.sh scamp_making_notes.sh (same dir)
5.) 2nd pass scamp run (kinda involves redoing some stuff from #3)
	/gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/astrom_photom_scamp_PANSTARRS/adam_A2204-scamp_pass2_final.sh
	necessary fixes here: /nfs/slac/kipac/fs1/u/awright/A2204_panstarrs_cats/run_scamp/adam_DECam-create_scamp_photom.sh

other notes on this stuff: /u/ki/awright/wtgpipeline/adam_A2204_scamp.sh
