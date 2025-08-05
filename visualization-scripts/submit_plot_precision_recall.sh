#!/bin/bash

#SBATCH --job-name precision_recall_plots
#SBATCH -t 0-00:05 
#SBATCH -p hsph
#SBATCH --mem=16G 
#SBATCH -o /n/miller_lab/csxue/comparisons/logs/output_%j_%x.out 
#SBATCH -e /n/miller_lab/csxue/comparisons/logs/error_%j_%x.err 

module load python/3.10.9-fasrc01 gcc/10.2.0-fasrc01 

eval "$(conda shell.bash hook)"
conda activate mutsig-venv

cd /n/miller_lab/csxue/comparisons/scripts 
python plot-precision-recall.py synthetic-WS "Well-Specified Data"
python plot-precision-recall.py synthetic-misspec "Misspecified Data"
python plot-errors-histogram.py synthetic-all 

python plot-precision-recall.py subsample-liver-20 "number of samples = 20"
python plot-precision-recall.py subsample-liver-30 "number of samples = 30"
python plot-precision-recall.py subsample-liver-50 "number of samples = 50"
python plot-precision-recall.py subsample-liver-80 "number of samples = 80"
python plot-precision-recall.py subsample-liver-120 "number of samples = 120"
python plot-precision-recall.py subsample-liver-170 "number of samples = 170"
python plot-precision-recall.py subsample-liver-230 "number of samples = 230"
python plot-precision-recall.py liver-WS "number of samples = 326"
