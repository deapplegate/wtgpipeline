#!/usr/bin/perl -w
###################
# @file makeImageList.pl
# @author Douglas Applegate
# @date 7/9/2008
#
# @brief Creates an image list for imageFlipper.pl or maskImages.pl
###################

#$CVSID = "$Id: makeImageList.pl,v 1.2 2008-07-14 21:34:27 dapple Exp $"

##################

use ds9xpautils;
use BonnLogger;

log_force_start;

$usage = "

makeImageList.pl [-n num / -a ] [-r dir] [-o file] [-b] [-i] dir prefix suffix

   Creates an image list from a directory

   -h          display this message


   -n num      randomly select num images for list [default: all]

   -r dir      designate region file directory

   -o file     save image list to file [default: images.list]

   -b          just use mosaics images
   -i          just use individual chip images (both default)


   
   Make sure the xpa commands {i.e. xpaset, xpaget} are on your path!
";

use File::Basename;
use Getopt::Std;
use Cwd 'abs_path';

my %Options;
getopts('hn:r:o:bi', \%Options);

defined($Options{'h'}) and die $usage;

$numImages = -1;
defined($Options{'n'}) and $numImages = $Options{'n'};

$regionDir = "";
defined($Options{'r'}) and $regionDir = $Options{'r'};

$outFile = "images.list";
defined($Options{'o'}) and $outFile = $Options{'o'};

$doBinned = 1;
$doChips = 1;
defined($Options{'b'}) and $doChips = 0;
defined($Options{'i'}) and $doBinned = 0;

if (scalar(@ARGV) != 3){
    log_status(1,"Invalid Command Line");
    die $usage;
}

$dir = abs_path($ARGV[0]);
$prefix = $ARGV[1];
$suffix = $ARGV[2];



open(OUTPUT, "> $outFile");

if ($regionDir ne ""){
    print OUTPUT "#regiondir:$regionDir\n";
}

@rawFiles = glob "$dir/${prefix}*_1$suffix.fits";
if ($numImages == -1){
    @selectedFiles = @rawFiles;
} else {
    fisher_yates_shuffle(\@rawFiles);
    @selectedFiles = @rawFiles[0..($numImages-1)];
}

@sortedFiles = sort { $a cmp $b } @selectedFiles;

foreach $file (@sortedFiles){

    $file =~ /($prefix.+)_1$suffix/;
    $base = $1;

    if ($doChips){
	for ($i = 1; $i <=10; $i += 1){
	    print OUTPUT "$dir/${base}_${i}$suffix.fits\n";
	}
    }
    if ($doBinned){
	print OUTPUT "$dir/BINNED/${base}_mos$suffix.fits\n";
    }
}



close(OUTPUT);

log_status_and_exit(0);

###################################

# fisher_yates_shuffle( \@array ) : generate a random permutation
# of @array in place
# from http://www.unix.com.ua/orelly/perl/cookbook/ch04_18.htm
sub fisher_yates_shuffle {
    my $array = shift;
    my $i;
    for ($i = @$array; --$i; ) {
        my $j = int rand ($i+1);
        next if $i == $j;
        @$array[$i,$j] = @$array[$j,$i];
    }
}
