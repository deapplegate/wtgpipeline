#!/bin/bash
set -xv
#adam-does# This code will call ds9 with individual chip exposures assembled into a mosaic with consistent scale limits based on the zscale of one of the chips.
#adam-example# ./adam_quicktools_ds9_chips2mosaic.sh /u/ki/awright/data/Zw2089/W-J-V_2010-03-12/SCIENCE/SUPA0119554 "OCF" "zscale"
#adam-example# ./adam_quicktools_ds9_chips2mosaic.sh /u/ki/awright/data/Zw2089/W-J-V_2010-03-12/SCIENCE/SUPA0119555 "OCF" "zscale"
#adam-example# ./adam_quicktools_ds9_chips2mosaic.sh /u/ki/awright/data/Zw2089/W-J-V_2010-03-12/SCIENCE/SUPA0119556 "OCF" "zscale"
supa=$1
end=$2
## if you want something very simple, then 3rd input=zscale
if [ "${3}" == "zscale" ];then
	ds9 -view layout vertical -zoom to fit -geometry 1200x2000 -cmap bb -zscale -frame lock scale -tile grid layout 5 2 -frame lock image \
		${supa}_6${end}.fits ${supa}_7${end}.fits ${supa}_8${end}.fits ${supa}_9${end}.fits ${supa}_10${end}.fits \
		${supa}_1${end}.fits ${supa}_2${end}.fits ${supa}_3${end}.fits ${supa}_4${end}.fits ${supa}_5${end}.fits -zoom to fit -frame lock image -frame lock scale &
fi
## if 3 inputs, then calcuate zscale nums for ccd#3 and apply those to whole mosaic
## if 4 inputs, then 3rd/4th inputs are taken to be the scale limits
if [ -z ${4} ];then
	## if 3 inputs, then calcuate zscale nums for ccd#3 and apply those to whole mosaic
	zminmax=( `~/InstallingSoftware/pythons/zscale_calc.py ${supa}_8${end}.fits`)
	zmin=${zminmax[0]}
	zmax=${zminmax[1]}
else
	## if 4 inputs, then 3rd/4th inputs are taken to be the scale limits
	zmin=$3
	zmax=$4
fi
ds9 -view layout vertical -zoom to fit -geometry 1200x2000 -cmap bb -scale limits ${zmin} ${zmax} -frame lock scale -tile grid layout 5 2 -frame lock image \
	${supa}_6${end}.fits ${supa}_7${end}.fits ${supa}_8${end}.fits ${supa}_9${end}.fits ${supa}_10${end}.fits \
	${supa}_1${end}.fits ${supa}_2${end}.fits ${supa}_3${end}.fits ${supa}_4${end}.fits ${supa}_5${end}.fits -zoom to fit -frame lock image -frame lock scale &
