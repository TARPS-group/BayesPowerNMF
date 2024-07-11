#!/usr/bin/python3

import argparse
import os
import sys

SUBSAMPLE_SIZES = [20, 30, 50, 80, 120, 170, 230]
SUBSAMPLE_REPLICATES = [32, 20, 12, 10, 10, 10, 10]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('orig_zeta', type = float)
    parser.add_argument('max_n', type = int)
    parser.add_argument('substage')
    return parser.parse_args()


args = parse_args()
    
orig_zeta = args.orig_zeta
max_n = args.max_n 

alpha = orig_zeta * max_n / (1 - orig_zeta)

batch_template = "sbatch subsample-liver-{size}-replicate-{rep}/experiment_scripts/stage_5_{substage}.sh {zeta:.3f}"

for n, max_r in zip(SUBSAMPLE_SIZES, SUBSAMPLE_REPLICATES):
    zeta = alpha / (alpha + n)
    for r in range(max_r):
        cmd = batch_template.format(size = n, rep = r + 1, substage = args.substage, zeta = zeta)
        print(cmd)
        os.system(cmd)


