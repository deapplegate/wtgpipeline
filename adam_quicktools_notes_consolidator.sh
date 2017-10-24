#!/bin/bash
#adam-does# this code takes a list of files, and puts all of their contents into a new file (1st one of inputs) so as to consolidate the notes I've taken
#adam-example# ./adam_quicktools_notes_consolidator.sh adam_notes-photom_notes_all.log adam_notes-do_photometry_issues.log adam_notes-quick-do_photometry_notes.sh do_photometry-new_ending.sh adam_notes-prob_with_keys.log adam_notes-doug_and_pat_code_descriptions.log )

flout=$1
fls=$@
rm_fls_str="mv "
for fl in ${fls}
do 
	if [ "${fl}" != "${flout}" ]; then
		echo "############################################################" >> ${flout}
		echo "##########  ${fl}  ##########" >> ${flout}
		echo "############################################################" >> ${flout}
		cat ${fl} >> ${flout}
		echo "" >> ${flout}
		echo "" >> ${flout}
		rm_fls_str="${rm_fls_str} ${fl}"
	fi
done

rm_fls_str="${rm_fls_str} /u/ki/awright/wtgpipeline/scratch/"
echo "ALL NOTES CONSOLIDATED IN: ${flout}, check the results and remove the old notes"
echo "vim ${flout}"
echo ${rm_fls_str}
