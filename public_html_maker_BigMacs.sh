#!/bin/bash
set -v
#adam-example# ./public_html_maker_BigMacs.sh Zw2089
bigmacsrun="${cluster}_BigMacs"

[[ -d ~/public_html/${bigmacsrun} ]] && rm -r ~/public_html/${bigmacsrun} || echo "no directory yet"

mkdir ~/public_html/${bigmacsrun}
chmod g+r ~/public_html/${bigmacsrun}
cd ~/public_html/${bigmacsrun}

chmod g+r ${PHOTDIR}/BIGMACS_output_PureStarCalib/PLOTS/
chmod g+r ${PHOTDIR}/BIGMACS_output_PureStarCalib/PLOTS/*.html
chmod g+r ${PHOTDIR}/BIGMACS_output_PureStarCalib/PLOTS/*.png
ln -s ${PHOTDIR}/BIGMACS_output_PureStarCalib/PLOTS/ .

cd -
echo "" >> ${PHOTDIR}/BIGMACS_output_PureStarCalib/PLOTS/README
echo "http://www.slac.stanford.edu/~awright/${bigmacsrun}/PLOTS/all.html" >> ${PHOTDIR}/BIGMACS_output_PureStarCalib/PLOTS/README
cat ${PHOTDIR}/BIGMACS_output_PureStarCalib/PLOTS/README
