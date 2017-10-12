#best superflat data in /nfs/slac/g/ki/ki18/anja/SUBARU/2010-03-12_W-S-I+
./spikefinder_para.sh ${SUBARUDIR}/2010-03-12_W-S-I+ SCIENCE SUPA OCF W-S-I+ ' 1 2 3 4 5 6 7 8 9 10' 2>&1 | tee -a OUT-SF_spikefinder_para-2010-03-12_W-S-I+.log
./adam_SF_2010-03-12_W-S-I+-do_Subaru_preprocess_superflat_SET2.sh 2>&1 | tee -a OUT-adam_SF_2010-03-12_W-S-I+-do_Subaru_preprocess_superflat_SET2.log
#next run
./get_error_log.sh OUT-SF_spikefinder_para-2010-03-12_W-S-I+.log
./get_error_log.sh OUT-adam_SF_2010-03-12_W-S-I+-do_Subaru_preprocess_superflat_SET2.log
# use data in /nfs/slac/g/ki/ki18/anja/SUBARU/2010-03-12_W-S-I+/SCIENCE/diffmask (esp *.sh.fits) to incorporate guider shadow into superflat
#see #adam-SHNT# in:
vim process_sub_images_para.sh



#2010-03-12_W-S-I+
#11 objects : ABELL0773
#ABELL0781
#ZwCl0949.6+5207
#RXCJ1212.3-1816
#ZwCl1231.4+1007
#ZwCl1309.1+2216
#ABELL0901
#ABELL0907
#ZwCl1021.0+0426
#ABELL1451
#ABELL1682
#Superflat status (everything fine, need S excluder, need * excluder, need more data):
#ZwCl1021.0+0426 (#2 and #7 removed)
#ZwCl1309.1+2216 (ALL REMOVED)

#see
#adam_fgas_preH-do_Subaru_preprocess.sh (lines ~450-550)
#vim process_superflat_para.sh
