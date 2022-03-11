import os
import argparse

import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('ctype', nargs='+')
    parser.add_argument('--overwrite', action='store_true')
    return parser.parse_args()


def load_2018_sbs_data(path, df=None):
    # print(path)
    data = pd.read_csv(path)
    tri = data.pop('Trinucleotide')
    mt = data.pop('Mutation type')
    data['Substitution'] = tri.str[0] + '[' + mt + ']' + tri.str[2]
    cols = data.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    data = data[cols]
    data = data.set_index('Substitution')
    if df is None:
        df = data
    else: 
        try:
            df = pd.concat([df, data], axis=1)
        except ValueError:
            print(df)
            print(data)
            raise
    return df


def reformat_sbs(input_file, ctype, overwrite):
    df = load_2018_sbs_data(input_file)
    output_file = os.path.splitext(input_file)[0] + '.ready'
    if len(ctype) > 0:
        df = df.loc[:,df.columns.str.startswith(ctype)]
        output_file += '.' + ctype
    output_file += '.tsv'
    if not overwrite and os.path.exists(output_file):
        print('not saving since output file already exists')
    else:
        print('saving', df.shape[1], 'samples to', output_file)
        df.to_csv(output_file, sep='\t')


def main():
    args = parse_args()
    for ct in args.ctype:
        print(ct)
        reformat_sbs(args.input_file, ct, args.overwrite)


if __name__ == '__main__':
    main()
