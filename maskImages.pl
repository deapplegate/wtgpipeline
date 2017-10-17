#!/usr/bin/perl -w
######################
# @file maskImages.pl
# @author Douglas Applegate
# @date 3/12/08
#
# @brief Manages clerical tasks associated with masking lots of chip images in
#            ds9.
# This requires the XPA messaging system to be installed and in your path
######################

#CVSID = "$Id: maskImages.pl,v 1.23 2009-12-11 22:57:04 dapple Exp $"

use ds9xpautils;
use imagelistutils;
#use BonnLogger;

#log_force_start;

$usage = "

maskImages.pl 

variations:
   maskImages.pl -h
       display this message
  
   maskImages.pl -l <file>
       file is a txt file containing a list of files to process
              file defaults to toMask.list

   maskImages.pl -d dir prefix
       process all files in maindir/dir/prefix

   Options:
       -r dir  region files will be saved in a reg directory 
                  under the file image dir, unless -r is specified

       -g      load global region files ../../reg/template_chip.reg

       -s      smooth images on loading
      

   Regiondir is saved in the lists. Command line overrides file.

   Make sure the xpa commands {i.e. xpaset, xpaget} are on your path!
";

use File::Basename;
use Getopt::Std;
use Cwd 'abs_path';

$listName = 'toMask.list';

my %Options;
getopts('dlhr:g:s', \%Options);

defined($Options{'h'}) and die $usage;

$regionDir = "";
defined($Options{'r'}) and $regionDir = abs_path($Options{'r'});

$doSmooth = 0;
if (defined($Options{'s'})) {
    print "SMOOTH!\n";
    $doSmooth = 1;
}

$doGlobal = 0;
if (defined($Options{'g'})){
    $doGlobal = 1;
    $globalPrefix = $Options{'g'};
}

$doCloseDS9 = 0;

if (defined($Options{'l'})){

    $listName = defined($ARGV[0]) ? $ARGV[0] : $listName;

    @imageList = readList($listName);

} elsif (defined($Options{'d'})) {

    die $usage unless scalar(@ARGV) == 2;

    @imageList = readDir($ARGV[0], $ARGV[1]);

} else {

    @imageList = ();
    foreach (@ARGV) {
	push(@imageList, abs_path($_));
    }

}
    
@remainingImages = doList(@imageList);

saveList(@remainingImages);

&closeDS9;

#log_status_and_exit(0);

#############################################################################

sub doList {

    my (@images) = @_;
    my $image;
    while ($image = pop @images){

	my $isComplete = doFile($image);
	if (! $isComplete){
	    push(@images, $image);
	    last;
	}
	my $doContinue = &promptUser('Next Image?', 'Y');
	last unless ($doContinue eq 'Y');
    }

    return @images;

}

#############################################################################

sub saveList {

    my (@list) = @_;

    $outputName = &promptUser('Save Remaining Images as', $listName);
    
    open(OUTPUT, "> $outputName");

    if ($regionDir ne ""){
	print OUTPUT "#regiondir:$regionDir\n";
    }
    
    print OUTPUT join("\n", @list), "\n";

    close(OUTPUT)

    
}

#############################################################################

sub doFile  {

    local($imagename) = @_;

    my ($base,$path,$type) = fileparse($imagename, '(\.weighted)?\.fits');
    if ($base =~ /(.+?_(\d+))/){
	$image = $1;
	$chip = $2;
    } else {
	$image = $base;
	$chip = "";
    }


    print "Processing $image...\n";

    my $regionPath = "";
    if ($regionDir eq ""){
	$regionPath = "$path/reg";
    } else {
	$regionPath = $regionDir;
    }

    my $regionFile = "$regionPath/$image.reg";

    my $globalFile = "";
    if ($doGlobal){
	$globalFile = "$globalPrefix$chip.reg"
    }

    if (! -d "$regionPath"){
	mkdir "$path/reg"
    }

    while (1) {

	&openDS9;
	
	&openDS9Image($imagename);

	if ( $doSmooth == 1 ) {
	    system("xpaset -p ds9 smooth yes")
	}

	print "$regionFile\n";
	
	if (-e $regionFile){
	    system("xpaset -p ds9 regions load $regionFile");
	}

	if ($doGlobal){
	    system("xpaset -p ds9 regions load $globalFile");	    
	}

    
	my $response = &promptUser("(s)ave,(r)etry,(a)bort ", "s");

	last if ($response eq 's');

	return 0 unless ($response eq 'r');

    }

    system("xpaset -p ds9 regions strip no");
    system("xpaset -p ds9 regions system image");
    print "Saving $regionFile\n";
    system("xpaset -p ds9 regions save $regionFile");


    return 1;

}

#############################################################################


