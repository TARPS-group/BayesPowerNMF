#!/bin/bash

# for c in LUNG OVARY STOMACH SKIN BREAST LIVER
# do
#     echo $c
#     python make_experiment_uger.py --section ${c}
    
#     for exp in WS CONT-2 OVERDISPERSED PERTURBED-25 
#     do
#         echo "${c}-${exp}"
#         python make_experiment_uger.py --section ${c}-${exp}
#     done
# done

# python make_experiment_uger.py --section LIVER-WS
# python make_experiment_uger.py --section LIVER

for size in 20 30 50 80 120 170 230 
do
    N=$(ls data/synthetic-liver-subsamples/*.tsv | grep -- -${size}- | wc -l)
    echo "subsample size $size with $N replicates"
    for (( replicate = 1 ; replicate <= $N ; replicate ++ ))
    do
        python make_experiment_uger.py --config-file liver_subsample.ini --section SUBSAMPLE-${size}-${replicate}
    done
done




