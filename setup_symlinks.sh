#!/bin/bash
set -xv
#adam-does# put the necessary links in place
# first argument = path to your local `quick` github repo
# the second argument = path to local `gravitas` repo

quickpath=$1/pythons/
gravitaspath=$2/
maxlikepath=$2/maxlikelensing/
ldaclensingpath=$2/ldaclensing/

## links to quick directory (probably ~/quick/pythons/)
for fl in `cat ${quickpath}/pythons_to_link.list`
do
	ln -s ${quickpath}/${fl} .
	Ignored=`grep ${fl} .gitignore | wc -l`
	if [ ${Ignored} -eq 0 ]; then
		echo ${fl} >> .gitignore
	fi
done

## links to gravitas/ldaclensing directory
fl="RXJ2129.ini"
ln -s ${ldaclensingpath}/${fl} .
Ignored=`grep ${fl} .gitignore | wc -l`
if [ ${Ignored} -eq 0 ]; then
	echo ${fl} >> .gitignore
fi

## links to gravitas/maxlikelensing/ directory
ln -s ${maxlikepath}/adam_cosmos_options.py .
ln -s ${maxlikepath}/adam_make_cosmos_sims_finalplots.py .
ln -s ${maxlikepath}/banff_tools.c .
ln -s ${maxlikepath}/banff_tools.pyx .
ln -s ${maxlikepath}/banff_tools.so .
ln -s ${maxlikepath}/bootstrap_masses.py .
ln -s ${maxlikepath}/compare_masses.py .
ln -s ${maxlikepath}/cosmos_mass_bias_calc_driver.sh .
ln -s ${maxlikepath}/cosmos_sim.py .
ln -s ${maxlikepath}/datamanager.py .
ln -s ${maxlikepath}/intrinsicscatter_grid.py .
ln -s ${maxlikepath}/intrinsicscatter_grid_plots.py .
ln -s ${maxlikepath}/make_pyx_setup.sh .
ln -s ${maxlikepath}/matching.py .
ln -s ${maxlikepath}/maxlike_bootstrap.py .
ln -s ${maxlikepath}/maxlike_controller.py .
ln -s ${maxlikepath}/maxlike_floatvoigt_shapedistro.py .
ln -s ${maxlikepath}/maxlike_floatvoigt_simdriver.py .
ln -s ${maxlikepath}/maxlike_general_filehandler.py .
ln -s ${maxlikepath}/maxlike_masses.py .
ln -s ${maxlikepath}/maxlike_mymc_driver.py .
ln -s ${maxlikepath}/maxlike_nfw2param.py .
ln -s ${maxlikepath}/maxlike_plots.py .
ln -s ${maxlikepath}/maxlike_secure_driver.py .
ln -s ${maxlikepath}/maxlike_secure_floatvoigt_driver.py .
ln -s ${maxlikepath}/maxlike_sim_filehandler.py .
ln -s ${maxlikepath}/maxlike_simdriver.py .
ln -s ${maxlikepath}/maxlike_subaru_driver.py .
ln -s ${maxlikepath}/maxlike_subaru_filehandler.py .
ln -s ${maxlikepath}/maxlike_subaru_secure_filehandler.py .
ln -s ${maxlikepath}/maxlike_voigt_simdriver.py .
ln -s ${maxlikepath}/newmanstyle_batchrunner.py .
ln -s ${maxlikepath}/nfwmodel2param.c .
ln -s ${maxlikepath}/nfwmodel2param.pyx .
ln -s ${maxlikepath}/nfwmodel2param.so .
ln -s ${maxlikepath}/nfwmodel_normshapedistro.py .
ln -s ${maxlikepath}/nfwmodel_sim.py .
ln -s ${maxlikepath}/nfwmodeltools.c .
ln -s ${maxlikepath}/nfwmodeltools.pyx .
ln -s ${maxlikepath}/nfwmodeltools.so .
ln -s ${maxlikepath}/nfwutils.py .
ln -s ${maxlikepath}/pdzfile_utils.py .
ln -s ${maxlikepath}/pdzperturbtools.c .
ln -s ${maxlikepath}/pdzperturbtools.pyx .
ln -s ${maxlikepath}/pdzperturbtools.so .
ln -s ${maxlikepath}/photorunner.sh .
ln -s ${maxlikepath}/prep_cosmos_run.py .
ln -s ${maxlikepath}/preprocess_cosmos_sims.py .
ln -s ${maxlikepath}/process_cosmos_sims.py .
ln -s ${maxlikepath}/process_cosmos_sims_plots.py .
ln -s ${maxlikepath}/readtxtfile.py .
ln -s ${maxlikepath}/run_ml_sim_bias.py .
ln -s ${maxlikepath}/scatter_sims.py .
ln -s ${maxlikepath}/scatter_sims_plots.py .
ln -s ${maxlikepath}/shearprofile.py .
ln -s ${maxlikepath}/simcl_scatter_sim_driver.py .
ln -s ${maxlikepath}/stats.c .
ln -s ${maxlikepath}/stats.pyx .
ln -s ${maxlikepath}/stats.so .
ln -s ${maxlikepath}/submit_mlmasses.sh .
ln -s ${maxlikepath}/submit_mlsims.sh .
ln -s ${maxlikepath}/varcontainer.py .
ln -s ${maxlikepath}/voigt.c .
ln -s ${maxlikepath}/voigt.h .
ln -s ${maxlikepath}/voigt_tools.c .
ln -s ${maxlikepath}/voigt_tools.pyx .
ln -s ${maxlikepath}/voigt_tools.so .
ln -s ${maxlikepath}/voigtcall.pyx .
