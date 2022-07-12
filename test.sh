#!/bin/bash

#$ -N infer_loadings_initial_WGS_PCAWG.96.ready.Lung-AdenoCA
#$ -j y
#$ -o /cga/scarter/cathyxue/bayes-power-sig/WGS_PCAWG.96.ready.Lung-AdenoCA/logs

#$ -l h_vmem=32G
#$ -l h_rt=00:02:00
#$ -l os=RedHat7

. /broad/tools/scripts/useuse

reuse .python-3.6.0
reuse GCC-5.2
source /cga/scarter/cathyxue/mutsig-venv/bin/activate

echo "test"
