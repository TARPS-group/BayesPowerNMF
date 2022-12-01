#!/bin/bash


python data/data_manip_scripts/generate-subsampled-data.py data/synthetic-liver-subsamples/synthetic-326-liver-hcc.tsv 20 --track-samples
python data/data_manip_scripts/generate-subsampled-data.py data/synthetic-liver-subsamples/synthetic-326-liver-hcc.tsv 30 --track-samples
python data/data_manip_scripts/generate-subsampled-data.py data/synthetic-liver-subsamples/synthetic-326-liver-hcc.tsv 50 --track-samples
python data/data_manip_scripts/generate-subsampled-data.py data/synthetic-liver-subsamples/synthetic-326-liver-hcc.tsv 80 --track-samples
python data/data_manip_scripts/generate-subsampled-data.py data/synthetic-liver-subsamples/synthetic-326-liver-hcc.tsv 120 --track-samples
python data/data_manip_scripts/generate-subsampled-data.py data/synthetic-liver-subsamples/synthetic-326-liver-hcc.tsv 170 --track-samples
python data/data_manip_scripts/generate-subsampled-data.py data/synthetic-liver-subsamples/synthetic-326-liver-hcc.tsv 230 --track-samples
# python data/data_manip_scripts/generate-subsampled-data.py data/synthetic-liver-subsamples/synthetic-326-liver-hcc.tsv 300 --track-samples --min-samples 5


