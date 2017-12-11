#!/bin/bash
set -xv
## this is a driver script which carries out the steps needed to run the cosmos mass bias calculation

### step 1 of 5 (i.e. the preliminary stuff)
# this step simply involves openning up `adam_cosmos_options.py` and setting which options you're going to use. There are four things to consider:
#	1.) cat_switch: which catalog you're going to pull from for the true redshifts.
#	2.) filterset: which filter combination (`UGRIZ` or `BVRIZ`) you're going to run on.
#	3.) datadir: where you want to send the output you're going to generate
#	4.) zchoice_switch: this will determine if single point zp_best (`zchoice_switch="point"`) or drawing a random sample from the p(z) dist'n (`zchoice_switch="dist"`). The `dist` choice is only an option for `newcat_matched` at this point.
### so, just to restate this one more time for clarity's sake:
# open up `adam_cosmos_options.py` and set the parameters first, you can:
# 	toggle between filter-combinations by changing `filterset` in adam_cosmos_options.py. Should be `UGRIZ` or `BVRIZ`
# 	toggle between the old catalog and the new one by changing `cat_switch` in adam_cosmos_options.py
# 		...this changes the catalogs that prep_cosmos_run.prepSourceFiles points to when making bpz.cat
# 	toggle from using single point zp_best to drawing a random sample from the p(z) dist'n by changing `zchoice_switch` to `dist ` or `point` in cosmos_sim.py

## datadir/filterset now set by running this:
./adam_cosmos_options.py
. cosmos_mass_bias.ini

### step 2 of 5
## simcl (i.e. real-observed-cluster-specific) cosmos sims, as opposed to ideal ones well spaced out in M and z
## simcl_scatter_sim_driver.py runs prep_cosmos_run_driver.prepSourceFiles, then runs scatter_sims.createPrecutSimFiles to make cosmos bootstrap fields and assign shears to them
./simcl_scatter_sim_driver.py ${datadir} ${filterset}

##adam-old# previously prep_cosmos_run_driver.py ran 4 functions in prep_cosmos_run.py, then simcl_scatter_sim_driver.py came along for simcl (i.e. cluster-specific) stuff
##adam-old#./prep_cosmos_run_driver.py ${datadir} ${filterset}
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi


### step 3 of 5
## run maxlike_simdriver.py to do p(z) quality cuts, and run nfwfit on all generated sim files
./submit_mlsims.sh  ${datadir} ${filterset} 5
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi
./photorunner.sh ./simqueue/ ./simqueue/log short 256
#NOTE: this may have to be repeated a few times, but the scripts are set-up that way, so it's fairly painless

### step 4 of 5
python preprocess_cosmos_sims.py ${datadir}/${filterset}/ /nocontam/maxlike/
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi

## step 5 of 5
./adam_make_cosmos_sims_finalplots.py ${datadir} ${filterset}
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi

## some information on catalogs:
### /u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.cat ###w
#['gp', 'dIB484', 'F814W', 'i_max', 'dIB527', 'dH1', 'K_uv', 'NB816', 'z_s', 'IB738', 'ID_2006', 'i_auto', 'dH_uv', 'i_star', 'H', 'du_s', 'F814W_star', 'J_uv', 'dch3', 'dIB738', 'du', 'dIB827', 'IB427', 'dJ', 'dH', 'dB', 'H_uv', 'IB505', 'J3', 'dch2', 'dV', 'x', 'dip', 'IB624', 'FUV', 'dIB505', 'dJ3', 'dJ2', 'dKs', 'di_s', 'Eb-v', 'J2', 'g_s', 'J1', 'dIB624', 'dK_uv', 'dKc', 'di_c', 'zp', 'rp', 'dKnf', 'dH2', 'appflag', 'ra', 'photflag', 'dF814W', 'dNUV', 'auto_offset', 'ID_2008', 'acs_mask', 'dNB816', 'di_auto', 'H2', 'drp', 'H1', 'dIB427', 'dzp', 'dFUV', 'deep_mask', 'V_mask', 'dJ1', 'dIB767', 'z_mask', 'dg_s', 'i_mask', 'IB574', 'dzpp', 'NUV', 'zpp', 'blendflag', 'mask_NUV', 'IB679', 'Kc', 'B', 'J', 'F814W_fwhm', 'Ks', 'dIB574', 'det_fwhm', 'dIB679', 'V', 'i_fwhm', 'IB709', 'ch1', 'ch2', 'ch3', 'ch4', 'IB767', 'mask_FUV', 'dec', 'IRAC2_mask', 'ip', 'i_c', 'i_s', 'dIB709', 'dz_s', 'dJ_uv', 'r_s', 'dY_uv', 'u_s', 'Kc_mask', 'B_mask', 'auto_flag', 'tile', 'flags', 'dch1', 'IRAC1_mask', 'dch4', 'acsdata_mask', 'dNB711', 'Knf', 'y', 'dgp', 'IB827', 'ID', 'NB711', 'IB464', 'Y_uv', 'IB527', 'u', 'objID', 'dr_s', 'IB484', 'dIB464']
### /u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat ###
#['zchi', 'M_j', 'M_i', 'M_k', 'BCmass', 'BCsfr', 'zerr_chi_min', 'chipdf', 'M_g', 'M_FUV', 'M_z', 'chisq', 'L_k', 'BCsfr_min', 'M_r', 'M_u', 'zqso', 'BCmodel', 'zerr_chi_max', 'ACSstar', 'M_B', 'star_model', 'BCssfr_min', 'galaxy_model', 'ra', 'qso_model', 'DCnuv-r', 'type', 'chistar', 'BCssfr_max', 'L_nu', 'zqsochi', 'L_r', 'BCext', 'zpdf', 'zphot', 'ID', 'zerr_pdf_min', 'BCmass_min', 'dec', 'BCsfr_max', 'M_NUV', 'BCage', 'zphot2', 'BCmass_max', 'BCssfr', 'zerr_pdf_max', 'M_V', 'Ebv', 'Nbands', 'objID', 'chisq2', 'Mass_2006', 'Ext_law']`
################################
#fl="/nfs/slac/g/ki/ki06/anja/SUBARU/cosmos_cats/simulations/clusters_2012-05-17/MACS0025-12/bpz.cat"
#cosmos="/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.cat"
#cosmos="/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat"
