#!/bin/bash

FILENAMES="/n/miller_lab/csxue/bayes-power-sig/data/synthetic-liver-subsamples/*.tsv"
for f in $FILENAMES
do
	trimmed=$(basename $f .tsv)
	trimmed=${trimmed#"synthetic-326-liver-hcc-all-seed-1-subsample-"}
	echo -n -e "$trimmed\t\t"
	ls subsample-liver-${trimmed}/results/ | wc -l 
done
