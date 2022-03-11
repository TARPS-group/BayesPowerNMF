#!/bin/bash

#SBATCH --job-name generate_synthetic_data_WGS_PCAWG.96.Stomach-AdenoCA_NO40 
#SBATCH -t 0-01:00 
#SBATCH -p shared
#SBATCH --mem=16G 
#SBATCH -o /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Stomach-AdenoCA_NO40/logs/output_%j_generate_synthetic_data_WGS_PCAWG.96.Stomach-AdenoCA_NO40.out 
#SBATCH -e /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Stomach-AdenoCA_NO40/logs/error_%j_generate_synthetic_data_WGS_PCAWG.96.Stomach-AdenoCA_NO40.err 

module load gcc/8.2.0-fasrc01 python/3.8.5-fasrc01

eval "$(conda shell.bash hook)"
conda activate mutsig-venv

NEW_PREFIX=synthetic-75-stomach-adenoca-1-2-3-5-9-13-15-17a-17b-18-20-21-26-28-41-44
SIGS_FILE=""
SIGS_PREFIX="Signature"
SIGNATURES="1 2 3 5 9 13 15 17a 17b 18 20 21 26 28 41 44"
SAVE_DIR=WGS_PCAWG.96.Stomach-AdenoCA_NO40/synthetic_data
S=1
N=75
PERTURBED="--perturbed 0.01 0.02"
OVERDISPERSED="--overdispersed 2"
CONTAMINATION="--contamination 1 5"
OPTS="--trim"

cd /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig
echo "python scripts/generate-synthetic-data.py $NEW_PREFIX $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR -s $S -n $N $PERTURBED $OVERDISPERSED $CONTAMINATION $OPTS"
python scripts/generate-synthetic-data.py $NEW_PREFIX $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR -s $S -n $N $PERTURBED $OVERDISPERSED $CONTAMINATION $OPTS
