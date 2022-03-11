#!/bin/bash

#SBATCH -c 4
#SBATCH --job-name infer_loadings_initial_WGS_PCAWG.96.Liver-HCC 
#SBATCH -t 0-02:00 
#SBATCH -p shared
#SBATCH --mem=64G 
#SBATCH -o /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Liver-HCC/logs/output_%j_infer_loadings_initial_WGS_PCAWG.96.Liver-HCC.out 
#SBATCH -e /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Liver-HCC/logs/error_%j_infer_loadings_initial_WGS_PCAWG.96.Liver-HCC.err 

module load gcc/8.2.0-fasrc01 python/3.8.5-fasrc01

eval "$(conda shell.bash hook)"
conda activate mutsig-venv

DATA=data/WGS_PCAWG.96.ready.tsv
FILTER="Liver-HCC"
SIGS_FILE=""
SIGS_PREFIX="Signature"
SIGNATURES="1 4 5 6 9 12 14 16 17a 17b 18 19 22 24 26 28 29 30 31 35 40"
SAVE_DIR=WGS_PCAWG.96.Liver-HCC/synthetic_data
SUB_TYPE=SBS
N=326
OPTS=""

cd /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig
echo "python scripts/infer-loadings-nnls.py $DATA $FILTER $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR --subst-type $SUB_TYPE -n $N $OPTS"
python scripts/infer-loadings-nnls.py $DATA $FILTER $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR --subst-type $SUB_TYPE -n $N $OPTS
