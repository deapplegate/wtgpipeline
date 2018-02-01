#!/bin/bash
set -xv

## you have to compile .pyx scripts before they can be imported in python
cython nfwmodeltools.pyx 
cython banff_tools.pyx
cython nfwmodel2param.pyx
cython pdzperturbtools.pyx
cython stats.pyx
cython voigt_tools.pyx
export NPY_NO_DEPRECATED_API="NPY_1_7_API_VERSION"
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I /u/lt/rherbonn/anaconda2/envs/astroconda/include/python2.7/ -I /gpfs/slac/kipac/fs1/u/anja/adam_needs_more_space/Anaconda2/envs/astroconda/lib/python2.7/site-packages/numpy/core/include/ -I./ -o banff_tools.so banff_tools.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I /u/lt/rherbonn/anaconda2/envs/astroconda/include/python2.7/ -I /u/lt/rherbonn/anaconda2/envs/astroconda/lib/python2.7/site-packages/numpy/core/include/ -I./ -o nfwmodel2param.so nfwmodel2param.c voigt.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I /u/lt/rherbonn/anaconda2/envs/astroconda/include/python2.7/ -I /u/lt/rherbonn/anaconda2/envs/astroconda/lib/python2.7/site-packages/numpy/core/include/ -I./ -o nfwmodeltools.so nfwmodeltools.c voigt.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I /u/lt/rherbonn/anaconda2/envs/astroconda/include/python2.7/ -I /u/lt/rherbonn/anaconda2/envs/astroconda/lib/python2.7/site-packages/numpy/core/include/ -I./ -o pdzperturbtools.so pdzperturbtools.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I /u/lt/rherbonn/anaconda2/envs/astroconda/include/python2.7/ -I /u/lt/rherbonn/anaconda2/envs/astroconda/lib/python2.7/site-packages/numpy/core/include/ -I./ -o stats.so stats.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I /u/lt/rherbonn/anaconda2/envs/astroconda/include/python2.7/ -I /u/lt/rherbonn/anaconda2/envs/astroconda/lib/python2.7/site-packages/numpy/core/include/ -I./ -o voigt_tools.so voigt_tools.c voigt.c
