#!/bin/bash

#SBATCH -c 4
#SBATCH --job-name infer_loadings_initial_WGS_PCAWG.96.Ovary-AdenoCA 
#SBATCH -t 0-02:00 
#SBATCH -p shared
#SBATCH --mem=64G 
#SBATCH -o /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Ovary-AdenoCA/logs/output_%j_infer_loadings_initial_WGS_PCAWG.96.Ovary-AdenoCA.out 
#SBATCH -e /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Ovary-AdenoCA/logs/error_%j_infer_loadings_initial_WGS_PCAWG.96.Ovary-AdenoCA.err 

module load gcc/8.2.0-fasrc01 python/3.8.5-fasrc01

eval "$(conda shell.bash hook)"
conda activate mutsig-venv

DATA=data/WGS_PCAWG.96.ready.tsv
FILTER="Ovary-AdenoCA"
SIGS_FILE=""
SIGS_PREFIX="Signature"
SIGNATURES="1 2 3 5 8 13 18 26 35 39 40 41"
SAVE_DIR=WGS_PCAWG.96.Ovary-AdenoCA/synthetic_data
SUB_TYPE=SBS
N=113
OPTS=""

cd /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig
echo "python scripts/infer-loadings-nnls.py $DATA $FILTER $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR --subst-type $SUB_TYPE -n $N $OPTS"
python scripts/infer-loadings-nnls.py $DATA $FILTER $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR --subst-type $SUB_TYPE -n $N $OPTS
