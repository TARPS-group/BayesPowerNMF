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
    parser.add_argument('--save-dir', default='.')
    parser.add_argument('-n', '--num-samples', type=int, default=0)
    parser.add_argument('-a', type=float, default=0)
    parser.add_argument('--zeta', type=float, default=1)
    parser.add_argument('--rho', type=int, default=None, nargs='*')
    parser.add_argument('--iters', type=int, default=None)
    parser.add_argument('--median', action='store_true')
    parser.add_argument('--MAP', action='store_true')
    parser.add_argument('--subst-type', default='SBS', choices=['SBS', 'DBS', 'INDEL'])
    parser.add_argument('--signatures', metavar='K', type=int, nargs='*', default=0)
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
    full_df = load_sbs_data(args.data)
    filtered_df = full_df[full_df.columns[full_df.columns.str.startswith(args.filter)]]
    filtered_data = filtered_df.values
    sample_names = filtered_df.columns
    max_samples = args.num_samples if args.num_samples > 0 else np.inf
    num_samples = min(max_samples, len(sample_names))
    print('Using', num_samples, 'samples')
    Xs = { sample_names[i] : filtered_data[:,i] for i in range(num_samples) }
    
    # construct filenames and descriptions
    base_description = 'synthetic-{}-{}-{}'.format(
        num_samples, args.filter, '-'.join(map(str, args.signatures))).lower()
    if args.a != 0:
        base_description += '-a-{:.2f}'.format(args.a)
    if args.median:
        base_description += '-median'
    loadings_file_base = os.path.join(args.save_dir, base_description + '-loadings')
    loadings_file = loadings_file_base + '.npy'
    loadings_figures_file = loadings_file_base + '.pdf'
    
    # load signatures
    if args.signatures_file == "":
        ref_sigs, ref_sig_names = mutsig.cosmic_signatures()
    else:
        ref_sigs, ref_sig_names = read_new_sigs(args.signatures_file, args.signatures_prefix)
    ref_sigs[ref_sigs <= 0] = 1e-10
    use_sig_inds = np.array(args.signatures) - 1
    num_sigs = use_sig_inds.size
    sigs = ref_sigs[use_sig_inds]
    sig_names = ref_sig_names[use_sig_inds]
    print('Using', ', '.join(sig_names))
    
    # infer loadings
    kwargs = dict(iters=1500)
    if args.a != 0:
        kwargs['a'] = args.a
    if args.zeta != 1:
        kwargs['lik_power'] = args.zeta
    if args.rho is not None:
        kwargs['rho'] = args.rho
    if args.iters is not None:
        kwargs['iters'] = args.iters
    if args.MAP is True:
        kwargs['use_map'] = True
    fits, loadings = models.infer_loadings(sigs, sig_names, Xs, **kwargs)
    point_est = np.median if args.median else np.mean
    loadings_array = np.array([point_est(fit['theta'], 0)
                               for fit in fits.values()]).T
    np.save(loadings_file, loadings_array)
    
    plotting.plot_loadings_matrix(loadings_array, sig_names,
                                  sample_names[:num_samples],
                                  save_path=loadings_figures_file)

    normalized_loadings = loadings_array / np.sum(loadings_array, axis=0,
                                                  keepdims=True)
    max_loadings = np.max(normalized_loadings, axis=1)
    low_loadings = max_loadings < .1
    if np.sum(low_loadings) > 0:
        print('Warning: some signatures do not have substantial loadings'
              ' attributed to them:', ', '.join(sig_names[low_loadings]))
    print('max loadings:', np.round(100*max_loadings))


def load_sbs_data(path, df = None):
    print(path)

    data = pd.read_csv(path, sep = "\t").T
    data.columns = data.loc['Substitution']
    data = data.drop('Substitution')
    data.columns.names = ['']
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
