#!/bin/bash

FILENAMES="*/figures/*/best*.csv"
# for f in $FILENAMES
# do
# 	trimmed=$(basename $f .tsv)
# 	echo "get $f "
# done

for f in $FILENAMES
do
	trimmed=${f%%/*}
	K=$(wc -l $f | cut -d ' ' -f1)
	let "K--"
	echo -e "$trimmed\t\t$K"
done

