#!/bin/bash
##################
# Utilities to execute logging in bash scripts as part of BonnLogger.py
#
# Source at beginning of scripts to enable status logging
##################
#$Id: BonnLogger.sh,v 1.2 2008-07-09 01:22:15 dapple Exp $

function log_status {
    # $1 status code
    # $2 any comments
    ./BonnLogger.py update $bonn_logger_id $@
}


##############################
