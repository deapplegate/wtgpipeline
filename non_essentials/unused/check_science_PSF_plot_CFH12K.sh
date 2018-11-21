#!/bin/bash -xv

# the script creates check plots of the PSF
# anisotropy for the CFH12K geometry.

# $1: main directory
# $2: science dir.
# $3: image extension (ext) on ..._iext.fits (i is the chip number)

. CFH12K.ini 

if [ ! -d "/$1/$2/cat/PSFcheck" ]; then
  mkdir /$1/$2/cat/PSFcheck
fi

ls -1 /$1/$2/*_1$3.fits > psfimages_plot_$$

cat psfimages_plot_$$ |\
{
  while read file
  do
    BASE=`basename ${file} _1$3.fits`

    i=1
    while [ "${i}" -le ${NCHIPS} ]
    do
      ${P_LDACTOASC} -i /$1/$2/cat/${BASE}_${i}$3_ksb.cat2 -b -t OBJECTS\
                     -k Xpos Ypos e1 e2 > tmp_${i}.asc_plot_$$
      i=$(( $i + 1 ))
    done

    {
      echo 'macro read "'${SMMACROS}'/shearfield.sm"'
      echo 'device "postportfile /'$1'/'$2'/cat/PSFcheck/'${BASE}''$3'.ps"'
      echo "relocate (17600 32500)"
      echo "putlabel 5 '${BASE}$3'"
      echo "limits 0 1990 0 4000"
      echo "expand 0.8"
      echo "window -6 -2 1 2"
      echo "box 0 2"
      echo "shearfield tmp_7.asc_plot_$$ 2000"
      echo "stats e1 m1 s1 k1"
      echo "stats e2 m2 s2 k2"
      echo "expand 0.4"
      echo "relocate 0 4050"
      echo "define s (sprintf('e1: %.2f', \$m1))"
      echo 'label $s'
      echo "relocate 1000 4050"
      echo "define s (sprintf('e2: %.2f', \$m2))"
      echo 'label $s'
      echo "expand 0.8"
      echo "window -6 -2 2 2"
      echo "box 0 0"
      echo "shearfield tmp_8.asc_plot_$$ 2000"
      echo "stats e1 m1 s1 k1"
      echo "stats e2 m2 s2 k2"
      echo "expand 0.4"
      echo "relocate 0 4050"
      echo "define s (sprintf('e1: %.2f', \$m1))"
      echo 'label $s'
      echo "relocate 1000 4050"
      echo "define s (sprintf('e2: %.2f', \$m2))"
      echo 'label $s'
      echo "expand 0.8"
      echo "window -6 -2 3 2"
      echo "box 0 0"
      echo "shearfield tmp_9.asc_plot_$$ 2000"
      echo "stats e1 m1 s1 k1"
      echo "stats e2 m2 s2 k2"
      echo "expand 0.4"
      echo "relocate 0 4050"
      echo "define s (sprintf('e1: %.2f', \$m1))"
      echo 'label $s'
      echo "relocate 1000 4050"
      echo "define s (sprintf('e2: %.2f', \$m2))"
      echo 'label $s'
      echo "expand 0.8"
      echo "window -6 -2 4 2"
      echo "box 0 0"
      echo "shearfield tmp_10.asc_plot_$$ 2000"
      echo "stats e1 m1 s1 k1"
      echo "stats e2 m2 s2 k2"
      echo "expand 0.4"
      echo "relocate 0 4050"
      echo "define s (sprintf('e1: %.2f', \$m1))"
      echo 'label $s'
      echo "relocate 1000 4050"
      echo "define s (sprintf('e2: %.2f', \$m2))"
      echo 'label $s'
      echo "expand 0.8"
      echo "window -6 -2 5 2"
      echo "box 0 0"
      echo "shearfield tmp_11.asc_plot_$$ 2000"
      echo "stats e1 m1 s1 k1"
      echo "stats e2 m2 s2 k2"
      echo "expand 0.4"
      echo "relocate 0 4050"
      echo "define s (sprintf('e1: %.2f', \$m1))"
      echo 'label $s'
      echo "relocate 1000 4050"
      echo "define s (sprintf('e2: %.2f', \$m2))"
      echo 'label $s'
      echo "expand 0.8"
      echo "window -6 -2 6 2"
      echo "box 0 0"
      echo "shearfield tmp_12.asc_plot_$$ 2000"
      echo "stats e1 m1 s1 k1"
      echo "stats e2 m2 s2 k2"
      echo "expand 0.4"
      echo "relocate 0 4050"
      echo "define s (sprintf('e1: %.2f', \$m1))"
      echo 'label $s'
      echo "relocate 1000 4050"
      echo "define s (sprintf('e2: %.2f', \$m2))"
      echo 'label $s'
      echo "expand 0.8"
      echo "window -6 -2 6 1"
      echo "box 1 0"
      echo "shearfield tmp_6.asc_plot_$$ 2000"
      echo "stats e1 m1 s1 k1"
      echo "stats e2 m2 s2 k2"
      echo "expand 0.4"
      echo "relocate 0 -700"
      echo "define s (sprintf('e1: %.2f', \$m1))"
      echo 'label $s'
      echo "relocate 1000 -700"
      echo "define s (sprintf('e2: %.2f', \$m2))"
      echo 'label $s'
      echo "expand 0.8"
      echo "window -6 -2 5 1"
      echo "box 1 0"
      echo "shearfield tmp_5.asc_plot_$$ 2000"
      echo "stats e1 m1 s1 k1"
      echo "stats e2 m2 s2 k2"
      echo "expand 0.4"
      echo "relocate 0 -700"
      echo "define s (sprintf('e1: %.2f', \$m1))"
      echo 'label $s'
      echo "relocate 1000 -700"
      echo "define s (sprintf('e2: %.2f', \$m2))"
      echo 'label $s'
      echo "expand 0.8"
      echo "window -6 -2 4 1"
      echo "box 1 0"
      echo "shearfield tmp_4.asc_plot_$$ 2000"
      echo "stats e1 m1 s1 k1"
      echo "stats e2 m2 s2 k2"
      echo "expand 0.4"
      echo "relocate 0 -700"
      echo "define s (sprintf('e1: %.2f', \$m1))"
      echo 'label $s'
      echo "relocate 1000 -700"
      echo "define s (sprintf('e2: %.2f', \$m2))"
      echo 'label $s'
      echo "expand 0.8"
      echo "window -6 -2 3 1"
      echo "box 1 0"
      echo "shearfield tmp_3.asc_plot_$$ 2000"
      echo "stats e1 m1 s1 k1"
      echo "stats e2 m2 s2 k2"
      echo "expand 0.4"
      echo "relocate 0 -700"
      echo "define s (sprintf('e1: %.2f', \$m1))"
      echo 'label $s'
      echo "relocate 1000 -700"
      echo "define s (sprintf('e2: %.2f', \$m2))"
      echo 'label $s'
      echo "expand 0.8"
      echo "window -6 -2 2 1"
      echo "box 1 0"
      echo "shearfield tmp_2.asc_plot_$$ 2000"
      echo "stats e1 m1 s1 k1"
      echo "stats e2 m2 s2 k2"
      echo "expand 0.4"
      echo "relocate 0 -700"
      echo "define s (sprintf('e1: %.2f', \$m1))"
      echo 'label $s'
      echo "relocate 1000 -700"
      echo "define s (sprintf('e2: %.2f', \$m2))"
      echo 'label $s'
      echo "expand 0.8"
      echo "window -6 -2 1 1"
      echo "box"
      echo "shearfield tmp_1.asc_plot_$$ 2000"
      echo "stats e1 m1 s1 k1"
      echo "stats e2 m2 s2 k2"
      echo "expand 0.4"
      echo "relocate 0 -700"
      echo "define s (sprintf('e1: %.2f', \$m1))"
      echo 'label $s'
      echo "relocate 1000 -700"
      echo "define s (sprintf('e2: %.2f', \$m2))"
      echo 'label $s'
      echo "expand 0.8"
      echo "hardcopy"
    } | ${P_SM}
  done
}


