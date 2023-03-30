import os
import sys
import argparse
from collections import OrderedDict

import numpy as np
import scipy as sp
from scipy.stats import nbinom
import pandas

from mutsigtools import mutsig


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('prefix')
    parser.add_argument('--signatures-file', default="")
    parser.add_argument('--signatures-prefix', default="Signature")
    parser.add_argument('--signatures', metavar='K', nargs='*')
    parser.add_argument('--save-dir', default='.')
    parser.add_argument('-s', '--seed', type=int, default=1)
    parser.add_argument('-n', '--num-samples', type=int, default=0)
    parser.add_argument('--perturbed', type=float, nargs = "*")
    parser.add_argument('--contamination', type=int, nargs = "*")
    parser.add_argument('--overdispersed', type=float, nargs = "*")
    parser.add_argument('--cosmic-version', default='v3')
    parser.add_argument('--trim', action='store_true')
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
    output_reference_loadings = os.path.join(args.save_dir,
                                        '{}-seed-{}-GT-loadings.csv'.format(base_description, args.seed))
    # trimmed_output_reference_loadings = os.path.join(args.save_dir,
    #                                     '{}-seed-{}-GT-loadings-trimmed.csv'.format(base_description, args.seed))
    output_file_template = os.path.join(args.save_dir,
                                        '{}-seed-{}{{}}.tsv'.format(base_description, args.seed))

    # checkpoint
    if os.path.exists(loadings_file):
        loadings_array = np.load(loadings_file)
    else:
        sys.exit("Stage I incomplete. Missing file " + loadings_file + ". Please try again later.")

    # load signatures
    if args.signatures_file == "":
        ref_sigs, ref_sig_names = mutsig.cosmic_signatures(version = args.cosmic_version)
    else:
        ref_sigs, ref_sig_names = read_new_sigs(args.signatures_file, args.signatures_prefix)
    ref_sigs[ref_sigs <= 0] = 1e-10

    if args.signatures == []:
        use_sig_inds = np.arange(len(ref_sig_names))
    elif args.signatures_file == "" and args.cosmic_version == "v3":
        use_sig_inds = np.array(mutsig.cosmic_v3_SBS_to_index(args.signatures)) - 1
    else:
        use_sig_inds = np.array(args.signatures) - 1

    # trim minimal signatures
    new_use_sig_inds = []
    new_k = []
    normalized_loadings = loadings_array / np.sum(loadings_array, axis=0, keepdims=True)
    for (k, sig) in zip(range(use_sig_inds.size), use_sig_inds):
        if np.sum(normalized_loadings[k] > 0.1) > 0 or np.sum(loadings_array[k]) > 0.02 * np.sum(loadings_array):
            new_use_sig_inds.append(sig)
            new_k.append(k)
    if args.trim:
        use_sig_inds = np.array(new_use_sig_inds)
        loadings_array = loadings_array[new_k]
    # else:
    #     print(pandas.DataFrame(np.vstack((np.mean(loadings_array[new_k], axis = 1), ref_sig_names[np.array(new_use_sig_inds)])).T))
    #     pandas.DataFrame(np.vstack((np.mean(loadings_array[new_k], axis = 1), ref_sig_names[np.array(new_use_sig_inds)])).T).to_csv(trimmed_output_reference_loadings, header = False, index = False)

    num_sigs = use_sig_inds.size
    sigs = ref_sigs[use_sig_inds]
    sig_names = ref_sig_names[use_sig_inds]

    print('Using', ', '.join(sig_names))

    # save "ground truth" loadings
    lds = np.mean(loadings_array, axis = 1)
    pandas.DataFrame(np.vstack((lds, sig_names)).T).to_csv(output_reference_loadings, header = False, index = False)

    # generate synthetic data
    configs = [('correct', None)] 
    if args.perturbed is not None:
        configs = configs + [('perturbed', p) for p in args.perturbed] 
    if args.contamination is not None:
        configs = configs + [('contamination', p) for p in args.contamination]
    if args.overdispersed is not None:
        configs = configs + [('overdispersed', p) for p in args.overdispersed]

    exp_list = ""

    for synth_type, param in configs:
        if synth_type == 'correct':
            counts = generate_perturbed_counts(loadings_array, sigs,
                                               mean_error=np.inf,
                                               seed=args.seed)    
            exp_list = exp_list + str(args.seed) + "\n"
        elif synth_type == 'perturbed':
            counts = generate_perturbed_counts(loadings_array, sigs,
                                               mean_error=param,
                                               seed=args.seed)
            exp_list = exp_list + str(args.seed) + "-perturbed-" + str(param) + "\n"
        elif synth_type == 'contamination':
            counts = generate_counts_with_error_loading(
                loadings_array, sigs, error_proportion=param/100.,
                seed=args.seed)
            exp_list = exp_list + str(args.seed) + "-contamination-" + str(param) + "\n"
        elif synth_type == 'overdispersed':
            counts = generate_overdispersed_counts(loadings_array, sigs,
                                                   overdispersion=param,
                                                   seed=args.seed)
            exp_list = exp_list + str(args.seed) + "-overdispersed-" + "{:.1f}\n".format(param)
        else:
            sys.exit('Invalid type')
        print(synth_type, param, np.mean(counts))
        output_file = output_file_template.format(
            '' if synth_type == 'correct' else '-{}-{}'.format(synth_type, param))
        pandas.DataFrame(counts).to_csv(output_file, sep = "\t")

    exp_file = open(os.path.join(args.save_dir, "exp_list.txt"), "wt")
    exp_file.write(exp_list)
    exp_file.close()


def generate_perturbed_counts(loadings, sigs, mean_error=0.005,
                              seed=30192):
    np.random.seed(seed)
    if mean_error == np.inf:
        counts = np.random.poisson(loadings.T.dot(sigs))
    else:
        # log (mean error / sparsity) = 3.6641 - 0.9820 log (concentration)
        # sparsity = 1 / (I * ||sig||^2)
        K, J = loadings.shape
        K, I = sigs.shape
        sparsity = 1 / (I * np.linalg.norm(sigs, axis = 1) ** 2)
        concentration = np.exp( (3.6641 - np.log (mean_error / sparsity)) / 0.9820 )
        # print(sparsity)
        # print(concentration)
        counts = np.zeros((J, I), dtype=int)
        for j, loading in enumerate(loadings.T):
            rand_sigs = np.zeros_like(sigs)
            for k, sig in enumerate(sigs):
                rand_sigs[k] = np.random.dirichlet(concentration[k]*sig)
            counts[j]  = np.random.poisson(loading.dot(rand_sigs))
    return counts.T


def generate_overdispersed_counts(loadings, sigs, overdispersion=2,
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
