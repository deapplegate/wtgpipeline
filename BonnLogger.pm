#########################
# @file BonnLogger.pm
# 
# @brief Provides some convinient utils for operating DS9 through XPA
#########################

#$CVSID = "$Id: BonnLogger.pm,v 1.2 2008-07-10 00:19:11 dapple Exp $";

use Exporter 'import';
@EXPORT = qw(log_start log_force_start log_status);

#############################################################################

$bonn_log_id = '-1';

sub log_start {
    $raw_bonn_log_id = `./BonnLogger.py log maskImages.pl @ARGV`;
    die unless $? == 0;
    $bonn_log_id = $raw_bonn_log_id;
    chomp($bonn_log_id)

}

#############################################################################

sub log_force_start {
    $raw_bonn_log_id = `./BonnLogger.py forceLog maskImages.pl @ARGV`;
    die unless $? == 0;
    $bonn_log_id = $raw_bonn_log_id;
    chomp($bonn_log_id)

}

#############################################################################

sub log_status {

    my($exitCode, @comments) = @_;

    system("./BonnLogger.py update $bonn_log_id $exitCode @comments");


}

#############################################################################


sub log_status_and_exit {

    my($exitCode, @comments) = @_;

    system("./BonnLogger.py update $bonn_log_id $exitCode @comments");
    exit $exitCode;

}

#############################################################################
1;
