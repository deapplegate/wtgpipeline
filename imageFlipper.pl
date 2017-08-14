#!/usr/bin/perl -w
###################
# @file imageFlipper.pl
# @author Douglas Applegate
# @date 5/30/2008
#
# @brief Flips through a series of images
###################

#$CVSID = "$Id: imageFlipper.pl,v 1.5 2009-01-22 22:54:59 dapple Exp $"

##################

use ds9xpautils;
use imagelistutils;

$usage = "

imageFlipper.pl 

variations:
   imageFlipper.pl -h
       display this message
  
   imageFlipper.pl -l <file>
       file is a txt file containing a list of files to process
              file defaults to toDisplay.list

   imageFlipper.pl -d dir prefix
       process all files in maindir/dir/prefix

   Individual files may be also listed on the command line.

   Other options: 
    
    -o reject.list  File to dump rejected image names to

    -z do not zscale images automatically

   
   Make sure the xpa commands {i.e. xpaset, xpaget} are on your path!
";

use File::Basename;
use Getopt::Std;
use Cwd 'abs_path';

$listName = 'toDisplay.list';
$rejectName = 'reject.list';
my %Options;
getopts('dlho:z', \%Options);

defined($Options{'h'}) and die $usage;

$doCloseDS9 = 0;

if (defined($Options{'o'})){

    $rejectName = $Options{'o'};

}

$zscale = 1;
if (defined($Options{'z'})){
    $zscale = 0;
}

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



@rejectedImages = doList(\@imageList);


saveList($listName, 'w',  @imageList);
saveList($rejectName, 'a', @rejectedImages);

&closeDS9;

#############################################################################

sub doList {

    my ($images) = @_;

    @toReject = ();
    while ($image = pop @$images){

	my $keep = doFile($image);
	if (! $keep){
	    push(@toReject, $image);
	}
	my $doContinue = &promptUser('Next Image?', 'Y');
	last unless ($doContinue eq 'Y');
    }

    return @toReject;

}

#############################################################################

sub saveList {

    my ($name, $mode, @list) = @_;

    $outputName = &promptUser('Save Remaining Images as', $name);
    
    if ($mode eq 'w'){
	open(OUTPUT, "> $outputName");
    } else {
	open(OUTPUT, ">> $outputName");
    }
    
    print OUTPUT join("\n", @list), "\n";

    close(OUTPUT)

    
}

#############################################################################

sub doFile  {

    local($imagename) = @_;

    my ($base,$path,$type) = fileparse($imagename, '\.fits');
    if ($base =~ /(SUPA\d+_\d+)/){
	my $image = $1;
    } else {
	my $image = $base;
    }

    print "Processing $image...\n";

    while (1) {

	&openDS9;
	
	&openDS9Image($imagename, $zscale);
	
	my $response = &promptUser("(n)ext or (r)eject", "n");

	return 1 if ($response eq 'n');

	return 0 if ($response eq 'r');

    }


}

#############################################################################
