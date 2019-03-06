#!/bin/bash
set -xv
cluster=$1

rm junk.tmp ${cluster}.inventory.log 
for dir in `\ls -d /nfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}/W-*[A-Z+]/` 
do
	dirfilt=`basename ${dir}`
	echo "${dirfilt} weight files : " > junk.tmp
	for i in 1 2 3 4 5 6 7 8 9 10 
	do
		num=`\ls ${dir}/WEIGHTS/SUPA*_${i}OCF*.weight.fits | wc -l` 
		echo "${num}" >> junk.tmp
	done
	paste -s -d\  junk.tmp >> ${cluster}.inventory.log 
	echo "${dirfilt}  flag  files : " > junk.tmp
	for i in 1 2 3 4 5 6 7 8 9 10 
	do
		num=`\ls ${dir}/WEIGHTS/SUPA*_${i}OCF*.flag.fits | wc -l` 
		echo "${num}" >> junk.tmp
	done
	paste -s -d\  junk.tmp >> ${cluster}.inventory.log 
	echo "${dirfilt} science files: " > junk.tmp
	for i in 1 2 3 4 5 6 7 8 9 10 
	do
		num=`\ls ${dir}/SCIENCE/SUPA*_${i}OCF*.fits | wc -l` 
		echo "${num}" >> junk.tmp
	done 
	paste -s -d\  junk.tmp >> ${cluster}.inventory.log 
done
rm junk.tmp

