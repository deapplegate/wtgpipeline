#! /usr/bin/env python
#adam-does# this script shows how to get info from lensing_coadd_type_filter.list into python
#adam-others# see the info retrieval used in adam_plot_bpz_output.py
import os
cluster=os.environ['cluster']

fo_lens_filter=open('lensing_coadd_type_filter.list','r')
lines_lens_filter=fo_lens_filter.readlines()
for line in lines_lens_filter:
    clean_line=line.strip()
    if line.startswith(cluster):
        line_data=[dat for dat in clean_line.split(' ') if not dat is '']
        cluster_lens,type_lens,filt_lens,mag_lens=line_data
        print ' cluster_lens=',cluster_lens , ' type_lens=',type_lens , ' filt_lens=',filt_lens , ' mag_lens=',mag_lens
