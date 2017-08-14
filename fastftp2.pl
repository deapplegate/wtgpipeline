#!/usr/bin/perl -w
#######################
# @file fastftp2.pl
# @author Douglas Applegate
# @date 9/5/2008
# @brief Queues up a bunch of files to the ncftp queue. You start the daemons manually.
########################

#CVSID="$Id: fastftp2.pl,v 1.4 2008-12-17 02:43:16 dapple Exp $"

########################

use Getopt::Std;
use Cwd;
use Net::FTP;
use List::Util qw(min max shuffle);


$usage = "fastftp.pl -t targetdir <-d todownload>
        
         -t targetdir   directory to download files to
         -d todownload   list of directories on archive to download
                            if not specificed, defaults to \$targetdir/todownload
\n";

getopts("t:d:h");

die $usage unless defined($opt_t);
$targetdir = $opt_t;
die "$targetdir doesn't exit" unless -d $targetdir;

$todownload = "$targetdir/todownload";
defined($opt_d) and $todownload = $opt_d;

$server = "smokaftp.nao.ac.jp";
$user = "smokaftp";
$password = "02YoS04";

@directories = readList($todownload);
print "@directories\n";

@files = readFiles($targetdir, @directories);
$nfiles = @files;
die "No Files to Download" if ($nfiles == 0);

$i = 0;
while ($i < $nfiles){
    $imax = min($i + 1000, $nfiles);
    $filelist = join(" ", @files[$i..$imax]);
    print "ncftpget -bb -u $user -p $password $server $targetdir $filelist";
    system("ncftpget -bb -u $user -p $password $server $targetdir $filelist");
    $i = $imax;
}


exit();

################################

sub readList {
    my ($toRead) = @_;
    my (@list) = ();
    open(INPUT, $toRead);
    while ($line = <INPUT>){
	$line =~ s/^\s+//;
	$line =~ s/\s+$//;
	push(@list, $line);
    }
    return @list;
};

################################

sub readFiles{

    my($targetdir, @directories) = @_;

    my @files = ();

    my $ftp = Net::FTP->new($server, Debug=>0) || die "Cannot connect to $server\n";
    $ftp->login($user, $password) || die "Cannot login\n";
    
    for my $dir (@directories){

	$filelist = "$dir/request$dir";
	$targetlist = "$targetdir/request$dir";
	print "Getting:$filelist $targetlist\n";
	if (! -e $targetlist){
	    $ftp->ascii;
	    $ftp->get($filelist, $targetlist) || die "Cannot download $filelist\n";
	}
	open(FILELIST, $targetlist) || die "Cannot open $targetlist\n";
	while (my $line = <FILELIST>){
	    chomp($line);
	    if ($line =~ /(SUPA\d+)/){
		my $file = "$dir/$1.fits";
		$targetfile = "$targetdir/$1.fits";
		if (-e $targetfile){
		    $ftp->binary;
		    $remotesize = $ftp->size($file);
		    $localsize = -s $targetfile;
		    if ($remotesize == $localsize){
			next;
		    } else {
			print "$targetfile incomplete: removing\n";
			unlink $targetfile;
		    }
		}
		print "Queuing $targetfile...\n";
		push(@files, $file);
		
	    }
	}
	close(FILELIST);
    }
    $ftp->quit;
    return @files;
};

#################################

