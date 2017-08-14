from glob import glob
import os

gs = glob(os.environ['sne'] + '/spec/Id000*')

for g in gs:
    os.system('python plot_spec2.py ' + g)
