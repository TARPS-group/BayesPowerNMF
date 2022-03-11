#!/bin/bash

#SBATCH -c 4
#SBATCH --job-name infer_loadings_initial_WGS_PCAWG.96.Skin-Melanoma_ALT 
#SBATCH -t 3-00:00 
#SBATCH -p shared
#SBATCH --mem=64G 
#SBATCH -o /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Skin-Melanoma_ALT/logs/output_%j_infer_loadings_initial_WGS_PCAWG.96.Skin-Melanoma_ALT.out 
#SBATCH -e /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Skin-Melanoma_ALT/logs/error_%j_infer_loadings_initial_WGS_PCAWG.96.Skin-Melanoma_ALT.err 

module load gcc/8.2.0-fasrc01 python/3.8.5-fasrc01

eval "$(conda shell.bash hook)"
conda activate mutsig-venv

DATA=data/WGS_PCAWG.96.ready.tsv
FILTER="Skin-Melanoma"
SIGS_FILE=""
SIGS_PREFIX="Signature"
SIGNATURES="1 2 5 7a 7b 7c 7d 13 17a 17b 38 40"
SAVE_DIR=WGS_PCAWG.96.Skin-Melanoma_ALT/synthetic_data
SUB_TYPE=SBS
N=107
A=0.00
ZETA=1
P0=""
Q1=""
Q99=""
OPTS=""

cd /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig
echo "python scripts/infer-loadings-only-2.py $DATA $FILTER $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR --subst-type $SUB_TYPE -n $N -a $A --zeta $ZETA $P0 $Q1 $Q99 $OPTS"
python scripts/infer-loadings-only-2.py $DATA $FILTER $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR --subst-type $SUB_TYPE -n $N -a $A --zeta $ZETA $P0 $Q1 $Q99 $OPTS
