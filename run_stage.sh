#!/bin/bash

STAGE=$1

# for c in WGS_PCAWG.96.Liver-HCC #WGS_PCAWG.96.Ovary-AdenoCA WGS_PCAWG.96.ready.Lung-AdenoCA WGS_PCAWG.96.Stomach-AdenoCA WGS_PCAWG.96.Skin-Melanoma WGS_PCAWG.96.Breast  
# do
#     echo "${c}/experiment_scripts/stage_${STAGE}.sh"
#     qsub ${c}/experiment_scripts/stage_${STAGE}.sh
# done

# for c in WGS_PCAWG.96.ready.Lung-AdenoCA WGS_PCAWG.96.Stomach-AdenoCA WGS_PCAWG.96.Skin-Melanoma WGS_PCAWG.96.Ovary-AdenoCA WGS_PCAWG.96.Breast WGS_PCAWG.96.Liver-HCC
# do
#     echo "${c}_NO40/experiment_scripts/stage_${STAGE}.sh"
#     qsub ${c}_NO40/experiment_scripts/stage_${STAGE}.sh
# done

# for c in ovary lung stomach skin breast liver
# do
#     for exp in WS contamination-2 overdispersed-2.0 perturbed-0.0025
#     do
#         echo "${c}-${exp}/experiment_scripts/stage_${STAGE}.sh"
#         qsub ${c}-${exp}/experiment_scripts/stage_${STAGE}.sh
#     done
# done

echo "liver-WS/experiment_scripts/stage_${STAGE}.sh"
qsub liver-WS/experiment_scripts/stage_${STAGE}.sh

for size in 20 #30 50 80 120 170 230 
do
    N=$(ls data/synthetic-liver-subsamples/*.tsv | grep -- -${size}- | wc -l)
    echo "subsample size $size with $N replicates"
    # for (( replicate = 1 ; replicate <= $N ; replicate ++ ))
    for (( replicate = 1 ; replicate <= 5 ; replicate ++ ))
    do
        echo "subsample-liver-${size}-replicate-${replicate}/experiment_scripts/stage_${STAGE}.sh"
        qsub subsample-liver-${size}-replicate-${replicate}/experiment_scripts/stage_${STAGE}.sh
    done
done

