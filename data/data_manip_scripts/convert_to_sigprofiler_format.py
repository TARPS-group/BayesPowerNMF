import os
import argparse

import pandas

from mutsigtools import mutsig

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('ctype', nargs='?', default='Cancer')
    return parser.parse_args()


def convert_file(input_file, ctype, trinucs, subs):
    output_file = os.path.splitext(input_file)[0] + '.csv'
    df = pandas.read_csv(input_file, sep='\t', index_col=0)
    df.columns = ['{}::Sample-{}'.format(ctype, i+1) for i in range(df.shape[1])]
    df.insert(0, 'Trinucleotide', trinucs)
    df.insert(0, 'Mutation type', subs)
    df.to_csv(output_file, index=False)


def main():
    subst_types = mutsig.construct_substitution_types()
    trinucs, subs = zip(*[(t[0]+t[4]+t[2], t[4]+'>'+t[8]) for t in subst_types])

    args = parse_args()
    convert_file(args.input_file, args.ctype, trinucs, subs)


if __name__ == '__main__':
    main()
