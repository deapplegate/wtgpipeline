#!/bin/bash
set -xv
#adam-does# put the necessary links in place
# first argument = path to your local `quick` github repo
# the second argument = path to local `gravitas` repo

quickpath=$1/pythons/
gravitaspath=$2/maxlikelensing/

## links to quick directory (probably ~/quick/pythons/)
for fl in `cat ${quickpath}/pythons_to_link.list`
do
	ln -s ${quickpath}/${fl} .
	Ignored=`grep ${fl} .gitignore | wc -l`
	if [ ${Ignored} -eq 0 ]; then
		echo ${fl} >> .gitignore
	fi
done

## links to gravitas directory (probably ~/gravitas/maxlikelensing/)
ln -s ${gravitaspath}/adam_cosmos_options.py .
ln -s ${gravitaspath}/adam_make_cosmos_sims_finalplots.py .
ln -s ${gravitaspath}/banff_tools.c .
ln -s ${gravitaspath}/banff_tools.pyx .
ln -s ${gravitaspath}/banff_tools.so .
ln -s ${gravitaspath}/bootstrap_masses.py .
ln -s ${gravitaspath}/compare_masses.py .
ln -s ${gravitaspath}/cosmos_mass_bias_calc_driver.sh .
ln -s ${gravitaspath}/cosmos_sim.py .
ln -s ${gravitaspath}/datamanager.py .
ln -s ${gravitaspath}/intrinsicscatter_grid.py .
ln -s ${gravitaspath}/intrinsicscatter_grid_plots.py .
ln -s ${gravitaspath}/make_pyx_setup.sh .
ln -s ${gravitaspath}/matching.py .
ln -s ${gravitaspath}/maxlike_bootstrap.py .
ln -s ${gravitaspath}/maxlike_controller.py .
ln -s ${gravitaspath}/maxlike_floatvoigt_shapedistro.py .
ln -s ${gravitaspath}/maxlike_floatvoigt_simdriver.py .
ln -s ${gravitaspath}/maxlike_general_filehandler.py .
ln -s ${gravitaspath}/maxlike_masses.py .
ln -s ${gravitaspath}/maxlike_mymc_driver.py .
ln -s ${gravitaspath}/maxlike_nfw2param.py .
ln -s ${gravitaspath}/maxlike_plots.py .
ln -s ${gravitaspath}/maxlike_secure_driver.py .
ln -s ${gravitaspath}/maxlike_secure_floatvoigt_driver.py .
ln -s ${gravitaspath}/maxlike_sim_filehandler.py .
ln -s ${gravitaspath}/maxlike_simdriver.py .
ln -s ${gravitaspath}/maxlike_subaru_driver.py .
ln -s ${gravitaspath}/maxlike_subaru_filehandler.py .
ln -s ${gravitaspath}/maxlike_subaru_secure_filehandler.py .
ln -s ${gravitaspath}/maxlike_voigt_simdriver.py .
ln -s ${gravitaspath}/newmanstyle_batchrunner.py .
ln -s ${gravitaspath}/nfwmodel2param.c .
ln -s ${gravitaspath}/nfwmodel2param.pyx .
ln -s ${gravitaspath}/nfwmodel2param.so .
ln -s ${gravitaspath}/nfwmodel_normshapedistro.py .
ln -s ${gravitaspath}/nfwmodel_sim.py .
ln -s ${gravitaspath}/nfwmodeltools.c .
ln -s ${gravitaspath}/nfwmodeltools.pyx .
ln -s ${gravitaspath}/nfwmodeltools.so .
ln -s ${gravitaspath}/nfwutils.py .
ln -s ${gravitaspath}/pdzfile_utils.py .
ln -s ${gravitaspath}/pdzperturbtools.c .
ln -s ${gravitaspath}/pdzperturbtools.pyx .
ln -s ${gravitaspath}/pdzperturbtools.so .
ln -s ${gravitaspath}/photorunner.sh .
ln -s ${gravitaspath}/prep_cosmos_run.py .
ln -s ${gravitaspath}/preprocess_cosmos_sims.py .
ln -s ${gravitaspath}/process_cosmos_sims.py .
ln -s ${gravitaspath}/process_cosmos_sims_plots.py .
ln -s ${gravitaspath}/readtxtfile.py .
ln -s ${gravitaspath}/run_ml_sim_bias.py .
ln -s ${gravitaspath}/scatter_sims.py .
ln -s ${gravitaspath}/scatter_sims_plots.py .
ln -s ${gravitaspath}/shearprofile.py .
ln -s ${gravitaspath}/simcl_scatter_sim_driver.py .
ln -s ${gravitaspath}/stats.c .
ln -s ${gravitaspath}/stats.pyx .
ln -s ${gravitaspath}/stats.so .
ln -s ${gravitaspath}/submit_mlmasses.sh .
ln -s ${gravitaspath}/submit_mlsims.sh .
ln -s ${gravitaspath}/varcontainer.py .
ln -s ${gravitaspath}/voigt.c .
ln -s ${gravitaspath}/voigt.h .
ln -s ${gravitaspath}/voigt_tools.c .
ln -s ${gravitaspath}/voigt_tools.pyx .
ln -s ${gravitaspath}/voigt_tools.so .
ln -s ${gravitaspath}/voigtcall.pyx .
