#!/bin/bash

#SBATCH --job-name generate_synthetic_data_sparse.WGS_PCAWG.96.Skin-Melanoma 
#SBATCH -t 0-01:00 
#SBATCH -p shared
#SBATCH --mem=32G 
#SBATCH -o /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/sparse.WGS_PCAWG.96.Skin-Melanoma/logs/output_%j_generate_synthetic_data_sparse.WGS_PCAWG.96.Skin-Melanoma.out 
#SBATCH -e /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/sparse.WGS_PCAWG.96.Skin-Melanoma/logs/error_%j_generate_synthetic_data_sparse.WGS_PCAWG.96.Skin-Melanoma.err 

module load gcc/8.2.0-fasrc01 python/3.8.5-fasrc01

eval "$(conda shell.bash hook)"
conda activate mutsig-venv

NEW_PREFIX=synthetic-107-skin-melanoma-
SIGS_FILE=""
SIGS_PREFIX="Signature"
SIGNATURES=""
SAVE_DIR=sparse.WGS_PCAWG.96.Skin-Melanoma/synthetic_data
S=1
N=107
OVERDISPERSED="--overdispersed 500 1000"
NEGBIN="--negbin 2"
ERRORSIG="--errorsig 1 5"
OPTS=""

cd /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig
echo "python scripts/generate-synthetic-data.py $NEW_PREFIX $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR -s $S -n $N $OVERDISPERSED $NEGBIN $ERRORSIG $OPTS"
python scripts/generate-synthetic-data.py $NEW_PREFIX $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR -s $S -n $N $OVERDISPERSED $NEGBIN $ERRORSIG $OPTS
