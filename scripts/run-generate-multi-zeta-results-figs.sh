#!/bin/bash
#SBATCH --job-name generate_figs_WGS_PCAWG.96.ready.Lung-AdenoCA 
#SBATCH -t 0-06:00 
#SBATCH -p shared
#SBATCH --mem=32G 
#SBATCH -o /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.ready.Lung-AdenoCA/logs/output_%j_generate_figs_WGS_PCAWG.96.ready.Lung-AdenoCA.out 
#SBATCH -e /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.ready.Lung-AdenoCA/logs/error_%j_generate_figs_WGS_PCAWG.96.ready.Lung-AdenoCA.err 


module load gcc/8.2.0-fasrc01 python/3.8.5-fasrc01

eval "$(conda shell.bash hook)"
conda activate mutsig-venv

cd /net/rcstorenfs02/ifs/rc_labs/miller_lab/csxue/bayes-power-sig
python scripts/generate-multi-zeta-results-figs.py $1



