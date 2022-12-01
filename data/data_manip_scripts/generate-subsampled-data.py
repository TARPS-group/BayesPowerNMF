import os
import sys
import argparse

import numpy as np
import numpy.random as npr
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('counts_file')
    parser.add_argument('subsample_size', type=int)
    # parser.add_argument('replicates', type=int)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--min-permutations', type=int, default=2)
    parser.add_argument('--min-samples', type=int, default=10)
    parser.add_argument('--track-samples', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()

    subsample_size = args.subsample_size
    output_base = os.path.splitext(args.counts_file)[0]
    output_file_template = output_base + '-subsample-{}-replicate-{{}}.tsv'.format(subsample_size)

    counts_df = pd.read_csv(args.counts_file, sep='\t', index_col=0)
    counts = counts_df.values
    J = counts.shape[1]

    sample_inds = []
    p = 0
    i = 0

    while (i < args.min_samples or p < args.min_permutations):
        npr.seed(args.seed + p)
        perm = npr.choice(J, size=J, replace=False)
        for k in range(int(J / subsample_size)):
            inds = perm[np.arange(subsample_size) + k * subsample_size]
            pd.DataFrame(counts[:,inds]).to_csv(output_file_template.format(i + 1), sep='\t')
            sample_inds.append(inds)
            i += 1
            if (i >= args.min_samples and p >= args.min_permutations):
                break
        p += 1

    # for i in range(1, args.replicates+1):
    #     npr.seed(args.seed + i)
    #     inds = npr.choice(counts.shape[1], size=subsample_size, replace=False)
    #     pd.DataFrame(counts[:,inds]).to_csv(output_file_template.format(i), sep='\t')
    #     sample_inds.append(inds)
    
    if args.track_samples:
        output_sample_track = output_base + '-subsample-{}-samples.csv'.format(subsample_size)
        pd.DataFrame(sample_inds).to_csv(output_sample_track)



if __name__ == '__main__':
    main()
