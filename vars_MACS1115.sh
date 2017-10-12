#!/bin/bash

echo "export cluster='MACS1115+01'"
echo "export filter='W-C-RC'"
echo "export run='2010-03-12'"
echo 'export pprun=${filter}_${run}'
echo "export ending='OCFSI'"

echo 'export filter_run_pairs=" W-S-Z+_2009-04-29 W-J-B_2009-04-29 W-J-B_2010-03-12 W-S-Z+_2010-03-12 W-C-RC_2010-03-12"'
echo "export filter='W-C-IC'; export ending='OCFSI' ; export run='2009-01-23'"
echo "export filter='W-J-V'; export ending='OCFSI' ; export run='2009-01-23'"
