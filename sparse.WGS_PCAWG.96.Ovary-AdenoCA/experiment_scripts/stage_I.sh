#!/bin/bash

#SBATCH -c 4
#SBATCH --job-name infer_loadings_initial_sparse.WGS_PCAWG.96.Ovary-AdenoCA 
#SBATCH -t 1-00:00 
#SBATCH -p shared
#SBATCH --mem=32G 
#SBATCH -o /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/sparse.WGS_PCAWG.96.Ovary-AdenoCA/logs/output_%j_infer_loadings_initial_sparse.WGS_PCAWG.96.Ovary-AdenoCA.out 
#SBATCH -e /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/sparse.WGS_PCAWG.96.Ovary-AdenoCA/logs/error_%j_infer_loadings_initial_sparse.WGS_PCAWG.96.Ovary-AdenoCA.err 

module load gcc/8.2.0-fasrc01 python/3.8.5-fasrc01

eval "$(conda shell.bash hook)"
conda activate mutsig-venv

DATA=data/WGS_PCAWG.96.ready.tsv
FILTER="Ovary-AdenoCA"
SIGS_FILE=""
SIGS_PREFIX="Signature"
SIGNATURES=""
SAVE_DIR=sparse.WGS_PCAWG.96.Ovary-AdenoCA/synthetic_data
SUB_TYPE=SBS
N=113
A=0.00
ZETA=1
P0=""
Q1=""
Q99=""
OPTS="--sparse "

cd /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig
echo "python scripts/infer-loadings-only.py $DATA $FILTER $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR --subst-type $SUB_TYPE -n $N -a $A --zeta $ZETA $P0 $Q1 $Q99 $OPTS"
python scripts/infer-loadings-only.py $DATA $FILTER $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR --subst-type $SUB_TYPE -n $N -a $A --zeta $ZETA $P0 $Q1 $Q99 $OPTS
