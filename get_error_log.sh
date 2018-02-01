#!/bin/bash
fls=$@
for fl in $fls
do
	base=`basename ${fl}`
	#grep -i "adam-look\|error\|exception\|^+.*exit [1-9]\|No such file or directory" ${fl} | sed '/^\s*#[^a][^d]/d;/^\s*echo/d' > err.${base}
	#old# grep -i "adam-look\|error\|exception\|^+.*exit [1-9]\|Permission denied" ${fl} | sed '/^\s*#[^a][^d]/d;/^\s*echo/d' > err.${base}
	grep -i "adam-Error\|adam-look\|error\|exception\|^+.*exit [1-9]\|Permission denied\|cannot" ${fl} | sed '/^\s*#[^a][^d]/d;/^\s*echo/d;/VerifyWarning/d;/trap/d' > err.${base}
	Nechos=`grep -i "adam-look" err.${base} | grep "^+ echo" | wc -l`
	if [ "${Nechos}" -gt "0" ]; then
		grep -v "^+ echo .*adam-look" err.${base} > err2well
		mv err2well err.${base}
	fi
	cat err.${base}
	echo ""
	Nlines=`wc -l err.${base} | sed 's/\ .*$//g'`
	if [ "${Nlines}" == "0" ]; then
		rm err.${base}
		echo "No Errors Found!"
	else
		echo "error log is named: err.${base}"
	fi
done

