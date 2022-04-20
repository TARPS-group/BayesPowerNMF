import os
import sys
import argparse

import numpy.random as npr
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('counts_file')
    parser.add_argument('subsample_size', type=int)
    parser.add_argument('replicates', type=int)
    return parser.parse_args()


def main():
    args = parse_args()

    subsample_size = args.subsample_size
    output_base = os.path.splitext(args.counts_file)[0]
    output_file_template = output_base + '-subsample-{}-replicate-{{}}.tsv'.format(subsample_size)

    counts_df = pd.read_csv(args.counts_file, sep='\t', index_col=0)
    counts = counts_df.values

    for i in range(1, args.replicates+1):
        npr.seed(i)
        inds = npr.choice(counts.shape[1], size=subsample_size, replace=False)
        pd.DataFrame(counts[:,inds]).to_csv(output_file_template.format(i), sep='\t')


if __name__ == '__main__':
    main()
