#!/bin/bash
#adam-does# takes IN an output script that includes a sextractor/ldac tool call and gets rid of some of the garbage
fl=$1
mv ${fl} ${fl}.old
sed '/Setting\ up\ background\ map\|sextracted\|>\ Computing\ background\|>\ Looking\ for\ \|>\ Initializing\|Objects selected:/d' ${fl}.old >  ${fl}
rm -f ${fl}.old
