#########################
# @file ds9xpautils.pm
# 
# @brief Provides some convinient utils for operating DS9 through XPA
#########################

#$CVSID = "$Id: ds9xpautils.pm,v 1.3 2009-01-22 22:54:58 dapple Exp $";

use Exporter 'import';
@EXPORT = qw(isDS9Running openDS9 openDS9Image closeDS9 saveDS9PNG);

$doCloseDS9 = 0;

#########################################################################

sub isDS9Running {

    my $isDS9Running = `xpaaccess ds9`;
    chomp($isDS9Running);

    return ($isDS9Running eq 'yes')

}

#############################################################################

sub openDS9 {

    
    if ( ! &isDS9Running ){
	
	system('ds9 &');
	$doCloseDS9= 1;
	while (`xpaget xpans | grep '$ENV{'USER'}'` !~ /^DS9/){
	    sleep 1;
	}
    }
    
}

#############################################################################

sub openDS9Image{

    my $imagename = shift;
    my $zscale = shift;

    if ( ! defined($zscale)){
	$zscale = 1;
    }

    system("xpaset -p ds9 file $imagename");
    system("xpaset -p ds9 cmap BB");
    if ( $zscale == 1 ) {
	system("xpaset -p ds9 scale mode zscale");
    }
    system("xpaset -p ds9 zoom to fit");

}

#############################################################################

sub closeDS9 {

    if ($doCloseDS9 and &isDS9Running){
	system("xpaset -p ds9 exit");
    }

}

#############################################################################

sub saveDS9PNG {
    $imagename = shift;
    system("xpaset -p ds9 saveimage png $imagename");
}

#############################################################################
1;
