import os
import sys
import argparse
from collections import OrderedDict

import numpy as np
import scipy as sp
import pandas as pd
import pystan

import seaborn as sns
# make figures pretty
sns.set_style('white')
sns.set_context('notebook', font_scale=2, rc={'lines.linewidth': 3})

from mutsigtools import mutsig, models, analysis, plotting


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('data')
    parser.add_argument('filter')
    parser.add_argument('--signatures-file', default="")
    parser.add_argument('--signatures-prefix', default="Signature")
    parser.add_argument('--signatures', metavar='K', nargs='*', default=0)
    parser.add_argument('--save-dir', default='.')
    parser.add_argument('--subst-type', default='SBS', choices=['SBS', 'DBS', 'INDEL'])
    parser.add_argument('-n', '--num-samples', type=int, default=0)
    parser.add_argument('--plain', action='store_true')
    return parser.parse_args()


def read_new_sigs(filename, sig_prefix):
    sigs = pd.read_csv(filename, sep = "\t")
    sigs = sigs.drop(columns = ["Substitution Type", "Trinucleotide"])
    sigs = sigs.set_index("Somatic Mutation Type")
    
    channel_order = np.array(mutsig.substitution_names())
    inds = sigs.index.values.tolist()
    order = [inds.index(ch) for ch in channel_order]

    sig_cols = sigs.columns.str.startswith(sig_prefix)
    r = sigs.iloc[order, sig_cols].values.T
    sig_names = sigs.columns.values[sig_cols]
    return r, sig_names


def main():
    args = parse_args()
    
    # load count data and filter
    full_df = load_sbs_data(args.data, args.plain)
    if not args.plain:
        filtered_df = full_df[full_df.columns[full_df.columns.str.startswith(args.filter)]]
        sample_names = filtered_df.columns
    else:
        filtered_df = full_df
        sample_names = args.filter + "_" + filtered_df.columns
    filtered_data = filtered_df.values

    max_samples = args.num_samples if args.num_samples > 0 else np.inf
    num_samples = min(max_samples, len(sample_names))
    print('Using', num_samples, 'samples')
    Xs = { sample_names[i] : filtered_data[:,i] for i in range(num_samples) }

    # save copy of original counts
    counts_file = os.path.join(args.save_dir, args.filter + "_original_counts.tsv")
    filtered_df.to_csv(counts_file, sep = "\t")
    
    # construct filenames and descriptions
    if args.signatures == 0:
        base_description = 'synthetic-{}-{}-{}'.format(
            num_samples, args.filter, "all").lower()
    else:
        base_description = 'synthetic-{}-{}-{}'.format(
            num_samples, args.filter, '-'.join(map(str, args.signatures))).lower()
    
    loadings_file_base = os.path.join(args.save_dir, base_description + '-loadings')
    loadings_file = loadings_file_base + '.npy'
    loadings_figures_file = loadings_file_base + '.pdf'
    
    # load signatures
    if args.signatures_file == "":
        ref_sigs, ref_sig_names = mutsig.cosmic_signatures(subst_type = args.subst_type, validated = True)
    else:
        ref_sigs, ref_sig_names = read_new_sigs(args.signatures_file, args.signatures_prefix)
    ref_sigs[ref_sigs <= 0] = 1e-10

    if args.signatures == 0:
        use_sig_inds = np.arange(len(ref_sig_names))
    elif args.signatures_file == "":
        use_sig_inds = np.array(mutsig.cosmic_v3_SBS_to_index(args.signatures)) - 1
    else:
        use_sig_inds = np.array(args.signatures) - 1
    
    num_sigs = use_sig_inds.size
    sigs = ref_sigs[use_sig_inds]
    sig_names = ref_sig_names[use_sig_inds]
    print('Using', ', '.join(sig_names))
    
    # infer loadings
    sigs = sigs.T
    nnls = []
    for i in range(num_samples):
        nnls.append(sp.optimize.nnls(sigs, filtered_data[:,i]))
    nnls_loadings_array = np.array([l[0] for l in nnls]).T

    np.save(loadings_file, nnls_loadings_array)
    
    plotting.plot_loadings_matrix(nnls_loadings_array, sig_names,
                                  sample_names[:num_samples],
                                  save_path=loadings_figures_file)

    normalized_loadings = nnls_loadings_array / np.sum(nnls_loadings_array, axis=0,
                                                  keepdims=True)
    max_loadings = np.max(normalized_loadings, axis=1)
    low_loadings = max_loadings < .1
    if np.sum(low_loadings) > 0:
        print('Warning: some signatures do not have substantial loadings'
              ' attributed to them:', ', '.join(sig_names[low_loadings]))
    print('max loadings:', np.round(100*max_loadings))


def load_sbs_data(path, plain = False, df = None):
    print(path)

    data = pd.read_csv(path, sep = "\t").T
    if not plain:
        data.columns = data.loc['Substitution']
        data = data.drop('Substitution')
        data.columns.names = ['']
    else:
        data = data.iloc[1:, :]
    
    if df is None:
        df = data
    else:
        try:
            df = pd.concat([df, data], axis=1)
        except ValueError:
            print(df)
            print(data)
            raise
    return df.T


## STILL NEED TO WORK ON!!
def load_indel_data(path, df = None):
    print(path)
    data = pd.read_csv(path)
    typ = data.pop('Type')
    subtyp = data.pop('Subtype')
    indel_size = data.pop('Indel_size')
    rep_mh_size = data.pop('Repeat_MH_size')
    data['Indel Type'] = typ + '-' + subtyp + '-'  + indel_size.astype(str) + '-' + rep_mh_size.astype(str)
    cols = data.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    data = data[cols]
    #data.columns = data.columns.astype(str)
    data = data.set_index('Indel Type')
    #data = data.T
    #data.columns = data.loc['Substitution']
    #data = data.drop('Substitution')
    #data.columns.names = ['']
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


def load_dbs_data(path, df=None):
    print(path)
    data = pd.read_csv(path)
    ref = data.pop('Ref')
    var = data.pop('Var')
    data['Substitution'] = ref + '>' + var
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

if __name__ == '__main__':
    main()
