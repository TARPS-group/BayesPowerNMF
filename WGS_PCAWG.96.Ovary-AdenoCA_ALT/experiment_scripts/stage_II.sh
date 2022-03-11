#!/bin/bash

#SBATCH --job-name generate_synthetic_data_WGS_PCAWG.96.Ovary-AdenoCA_ALT 
#SBATCH -t 0-01:00 
#SBATCH -p shared
#SBATCH --mem=16G 
#SBATCH -o /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Ovary-AdenoCA_ALT/logs/output_%j_generate_synthetic_data_WGS_PCAWG.96.Ovary-AdenoCA_ALT.out 
#SBATCH -e /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Ovary-AdenoCA_ALT/logs/error_%j_generate_synthetic_data_WGS_PCAWG.96.Ovary-AdenoCA_ALT.err 

module load gcc/8.2.0-fasrc01 python/3.8.5-fasrc01

eval "$(conda shell.bash hook)"
conda activate mutsig-venv

NEW_PREFIX=synthetic-113-ovary-adenoca-1-2-3-5-8-13-18-26-35-39-40-41
SIGS_FILE=""
SIGS_PREFIX="Signature"
SIGNATURES="1 2 3 5 8 13 18 26 35 39 40 41"
SAVE_DIR=WGS_PCAWG.96.Ovary-AdenoCA_ALT/synthetic_data
S=1
N=113
PERTURBED="--perturbed 0.01 0.02"
OVERDISPERSED="--overdispersed 2"
CONTAMINATION="--contamination 1 5"
OPTS="--trim"

cd /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig
echo "python scripts/generate-synthetic-data.py $NEW_PREFIX $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR -s $S -n $N $PERTURBED $OVERDISPERSED $CONTAMINATION $OPTS"
python scripts/generate-synthetic-data.py $NEW_PREFIX $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR -s $S -n $N $PERTURBED $OVERDISPERSED $CONTAMINATION $OPTS
