match.sh /tmp/MACS2243-09matchspec STDTAB /tmp/MACS2243-09spec4 spec /tmp/MACS2243-09final.cat data
ldacfilter -i /tmp/MACS2243-09matchspec -c '((z_spec != 0) AND (SeqNr_data != 0));' -t STDTAB -o /tmp/MACS2243-09matchspec.filt
ldactoasc -i /tmp/MACS2243-09matchspec.filt -t STDTAB -k Z_BEST_data
