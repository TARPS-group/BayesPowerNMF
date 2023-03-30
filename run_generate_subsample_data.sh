#!/bin/bash

for size in 20 30 50 80 120 170 230
do
	python data/data_manip_scripts/generate-subsampled-data.py data/synthetic-liver-subsamples/synthetic-326-liver-hcc-all-seed-1.tsv $size --track-samples
done

# python data/data_manip_scripts/generate-subsampled-data.py data/synthetic-liver-subsamples/synthetic-326-liver-hcc.tsv 300 --track-samples --min-samples 5


