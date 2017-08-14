#!/usr/bin/env python

# $Id: distribute_standards_subaru.py,v 1.1 2009-04-23 19:10:25 dapple Exp $

#Distribute standard images to their proper places.
# Closely based on distribute_sets_subaru.sh



#$1: main directory
#$2: run/science directory
#$3: image extension (ext) on ..._iext.fits (i is the chip number)
#$4: minimum overlap for counting exposures to the same set
#$5: lookup file: nick full_name ra dec nicknames
#$6: weights directory

import sys, os, re

main_dir = sys.argv[1]
runscience_dir = sys.argv[2]
ext = sys.argv[3]
minOverlap = sys.argv[4]
lookup_file = sys.argv[5]
weights_dir = "WEIGHTS";
if len(sys.argv) > 6:
    weights_dir = sys.argv[6]


match = re.match('^([\w-]+)_([\w-]+)', runscience_dir)
if not match:
    sys.stderr.write('Cannot parse run directory: %s' % runscience_dir)
    sys.exit(1)
night = match.group(1)
filter = match.group(2)
run_dir = '%s_%s' % (night, filter)

print "RUNDIR: $run_dir"


FILTERKEY="FILTER"
OBJECTKEY="OBJECT"
RAKEY="CRVAL1"
DECKEY="CRVAL2"

sets = {}

while ($file = <$main_dir/$runscience_dir/*${ext}.fits>){
    $name = basename($file);
    $RA=`dfits $file | fitsort ${RAKEY} | awk '($1!="FILE") {print $2}'`;
    $DEC=`dfits $file | fitsort ${DECKEY} | awk '($1!="FILE") {print $2}'`;
    $OBJECT=`dfits $file | fitsort ${OBJECTKEY} | awk '($1!="FILE") {print $2}'`;

    $OBJECT =~ /^([A-Za-z]+\d+)/;
    die "Can't parse Object: $name $OBJECT" unless $nickname = $1;
    @objInfo = [$name, $RA, $DEC, $OBJECT];
    
    if ( ! defined $sets{$nickname} ){
	$sets{$nickname} = [];
    }

    push @{$sets{$nickname}}, @objInfo;
}

foreach $nickname ( keys %sets){
    print "$nickname:\n";
    for $file_ref ($sets{$nickname}) {
	print "\t [ @$file_ref ]\n";
    }
}
