#!/bin/bash
set -xv
## this is a driver script which carries out the four steps needed to run the cosmos mass bias calculation

### /u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.cat ###w
#['gp', 'dIB484', 'F814W', 'i_max', 'dIB527', 'dH1', 'K_uv', 'NB816', 'z_s', 'IB738', 'ID_2006', 'i_auto', 'dH_uv', 'i_star', 'H', 'du_s', 'F814W_star', 'J_uv', 'dch3', 'dIB738', 'du', 'dIB827', 'IB427', 'dJ', 'dH', 'dB', 'H_uv', 'IB505', 'J3', 'dch2', 'dV', 'x', 'dip', 'IB624', 'FUV', 'dIB505', 'dJ3', 'dJ2', 'dKs', 'di_s', 'Eb-v', 'J2', 'g_s', 'J1', 'dIB624', 'dK_uv', 'dKc', 'di_c', 'zp', 'rp', 'dKnf', 'dH2', 'appflag', 'ra', 'photflag', 'dF814W', 'dNUV', 'auto_offset', 'ID_2008', 'acs_mask', 'dNB816', 'di_auto', 'H2', 'drp', 'H1', 'dIB427', 'dzp', 'dFUV', 'deep_mask', 'V_mask', 'dJ1', 'dIB767', 'z_mask', 'dg_s', 'i_mask', 'IB574', 'dzpp', 'NUV', 'zpp', 'blendflag', 'mask_NUV', 'IB679', 'Kc', 'B', 'J', 'F814W_fwhm', 'Ks', 'dIB574', 'det_fwhm', 'dIB679', 'V', 'i_fwhm', 'IB709', 'ch1', 'ch2', 'ch3', 'ch4', 'IB767', 'mask_FUV', 'dec', 'IRAC2_mask', 'ip', 'i_c', 'i_s', 'dIB709', 'dz_s', 'dJ_uv', 'r_s', 'dY_uv', 'u_s', 'Kc_mask', 'B_mask', 'auto_flag', 'tile', 'flags', 'dch1', 'IRAC1_mask', 'dch4', 'acsdata_mask', 'dNB711', 'Knf', 'y', 'dgp', 'IB827', 'ID', 'NB711', 'IB464', 'Y_uv', 'IB527', 'u', 'objID', 'dr_s', 'IB484', 'dIB464']
### /u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat ###
#['zchi', 'M_j', 'M_i', 'M_k', 'BCmass', 'BCsfr', 'zerr_chi_min', 'chipdf', 'M_g', 'M_FUV', 'M_z', 'chisq', 'L_k', 'BCsfr_min', 'M_r', 'M_u', 'zqso', 'BCmodel', 'zerr_chi_max', 'ACSstar', 'M_B', 'star_model', 'BCssfr_min', 'galaxy_model', 'ra', 'qso_model', 'DCnuv-r', 'type', 'chistar', 'BCssfr_max', 'L_nu', 'zqsochi', 'L_r', 'BCext', 'zpdf', 'zphot', 'ID', 'zerr_pdf_min', 'BCmass_min', 'dec', 'BCsfr_max', 'M_NUV', 'BCage', 'zphot2', 'BCmass_max', 'BCssfr', 'zerr_pdf_max', 'M_V', 'Ebv', 'Nbands', 'objID', 'chisq2', 'Mass_2006', 'Ext_law']`

################################

#fl="/nfs/slac/g/ki/ki06/anja/SUBARU/cosmos_cats/simulations/clusters_2012-05-17/MACS0025-12/bpz.cat"
#cosmos="/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.cat"
#cosmos="/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat"

## RUNNING COSMOS MASS BIAS
## step 1 of 4
#adam-done# datadir='/nfs/slac/g/ki/ki18/anja/SUBARU/cosmossims2017_COSMOS2008-zp_best/'
#adam-done# 	both UGRIZ and BVRIZ are done
#adam-done# datadir='/nfs/slac/g/ki/ki18/anja/SUBARU/cosmossims2017_COSMOSnewmatch-zp_dist/'
#adam-done# 	both UGRIZ and BVRIZ are done

## datadir/filterset now set by this:
./adam_cosmos_options.py
. cosmos_mass_bias.ini

#older example: datadir='/u/ki/dapple/nfs22/cosmossims2017/'
#older example: filterset='BVRIZ'
## toggle between the old catalog and the new one by changing `cat_switch` in prep_cosmos_run.py
## toggle from using single point zp_best to drawing a random sample from the p(z) dist'n by changing `zchoice` to `dist ` or `point` in cosmos_sim.py
./prep_cosmos_run_driver.py ${datadir} ${filterset}
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi


## step 2
./submit_mlsims.sh  ${datadir} ${filterset} 5
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi
./photorunner.sh ./simqueue/ ./simqueue/log short 256
exit 0;
#NOTE: this has to be repeated a few times, but the scripts are set-up that way, so it's fairly painless
#./submit_mlsims.sh  ${datadir} ${filterset} 5 && ./photorunner.sh ./simqueue/ ./simqueue/log short 256

## step 3
python preprocess_cosmos_sims.py ${datadir}/${filterset}/nocontam/maxlike/
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi

## step 4
./adam_make_cosmos_sims_finalplots.py ${datadir} ${filterset}
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi
