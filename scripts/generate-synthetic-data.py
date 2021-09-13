import os
import sys
import argparse
from collections import OrderedDict

import numpy as np
import scipy as sp
from scipy.stats import nbinom
import pandas

from mutsigtools import  mutsig, models, analysis, plotting


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('prefix')
    parser.add_argument('--signatures-file', default="")
    parser.add_argument('--signatures-prefix', default="Signature")
    parser.add_argument('--save-dir', default='.')
    parser.add_argument('-s', '--seed', type=int, default=1)
    parser.add_argument('-n', '--num-samples', type=int, default=0)
    parser.add_argument('--overdispersed', type=int, nargs = "*")
    parser.add_argument('--errorsig', type=int, nargs = "*")
    parser.add_argument('--negbin', type=float, nargs = "*")
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
    
    # construct filenames and descriptions
    base_description = args.prefix
    loadings_file_base = os.path.join(args.save_dir, base_description + '-loadings')
    loadings_file = loadings_file_base + '.npy'
    output_file_template = os.path.join(args.save_dir,
                                        '{}-seed-{}{{}}.tsv'.format(base_description, args.seed))

    # checkpoint
    if os.path.exists(loadings_file):
        loadings_array = np.load(loadings_file)
    else:
        sys.exit("Stage I incomplete. Please try again later.")

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

    # generate synthetic data
    configs = [('correct', None)] + [('overdispersed', p) for p in args.overdispersed] + [('errorsig', p) for p in args.errorsig] + [('negbin', p) for p in args.negbin]

    for synth_type, param in configs:
        if synth_type == 'correct':
            counts = generate_overdispersed_counts(loadings_array, sigs,
                                                   concentration=np.inf,
                                                   seed=args.seed)    
        elif synth_type == 'overdispersed':
            counts = generate_overdispersed_counts(loadings_array, sigs,
                                                   concentration=param,
                                                   seed=args.seed)
        elif synth_type == 'errorsig':
            counts = generate_counts_with_error_loading(
                loadings_array, sigs, error_proportion=param/100.,
                seed=args.seed)
        elif synth_type == 'negbin':
            counts = generate_negbin_counts(loadings_array, sigs,
                                            overdispersion=param,
                                            seed=args.seed)
        else:
            sys.exit('Invalid type')
        print(synth_type, param, np.mean(counts))
        output_file = output_file_template.format(
            '' if synth_type == 'correct' else '-{}-{}'.format(synth_type, param))
        pandas.DataFrame(counts).to_csv(output_file, sep = "\t")


def generate_overdispersed_counts(loadings, sigs, concentration=1e5,
                                  seed=30192):
    np.random.seed(seed)
    if concentration == np.inf:
        counts = np.random.poisson(loadings.T.dot(sigs))
    else:
        K, J = loadings.shape
        K, I = sigs.shape
        counts = np.zeros((J, I), dtype=int)
        for j, loading in enumerate(loadings.T):
            rand_sigs = np.zeros_like(sigs)
            for k, sig in enumerate(sigs):
                rand_sigs[k] = np.random.dirichlet(concentration*sig)
            counts[j]  = np.random.poisson(loading.dot(rand_sigs))
    return counts.T


def generate_negbin_counts(loadings, sigs, overdispersion=2,
                             seed=30192):
    np.random.seed(seed)
    if overdispersion < 1:
        raise ValueError('overdispersion must be at least 1')
    if overdispersion == 1:
        counts = np.random.poisson(loadings.T.dot(sigs))
    else:
        means = loadings.T.dot(sigs)
        r = means / (overdispersion - 1.)
        p = r / (r + means)
        counts = sp.stats.nbinom.rvs(r, p)
    return counts.T


def generate_counts_with_error_loading(loadings, sigs, concentration=1,
                                       error_proportion=.01, seed=30192):
    np.random.seed(seed)
    K, J = loadings.shape
    K, I = sigs.shape
    counts = np.zeros((J, I), dtype=int)
    for j, loading in enumerate(loadings.T):
        error_sig = np.random.dirichlet(concentration*np.ones(I))[np.newaxis,:]
        error_loading = error_proportion * np.sum(loading)
        sigs_with_error = np.concatenate([sigs, error_sig], axis=0)
        loading_with_error = np.concatenate([(1-error_proportion)*loading, [error_loading]])
        counts[j]  = np.random.poisson(loading_with_error.dot(sigs_with_error))
    return counts.T


if __name__ == '__main__':
    main()
