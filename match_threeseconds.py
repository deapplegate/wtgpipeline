ldacrenkey -i /tmp/compare.cat -o /tmp/compare2.cat -k ALPHA_J2000_W-C-RC Ra DELTA_J2000_W-C-RC Dec SeqNr_W-C-RC SeqNr  -t STDTAB
match_simple.sh $subdir/MACS0417-11/PHOTOMETRY/all.cat /tmp/compare2.cat /tmp/matched.cat
