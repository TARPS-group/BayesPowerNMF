import os
import sys
import itertools
import argparse
import decimal

import matplotlib
if 'DISPLAY' not in os.environ:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import numpy as np
import scipy as sp
import pandas
import h5py

import seaborn as sns

from mutsigtools import analysis, mutsig, plotting, util

CUTOFF = 1


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('start_info')
    parser.add_argument('end_info')
    parser.add_argument('base_dir')
    parser.add_argument('--samp-info', default='')
    parser.add_argument('--seeds', type=int, metavar='seed', nargs='*')
    parser.add_argument('--zetas', type=float, metavar='zeta', nargs='*')
    parser.add_argument('--save-dir', default='figures')
    parser.add_argument('--results-dir', default='results')
    parser.add_argument('--counts-file', default='data/Alexandrov2018/WGS_all.96.ready.tsv')
    parser.add_argument('--subst-type', default='SBS', choices=['SBS', 'DBS', 'INDEL'])
    parser.add_argument('--skip', type=int, default=25)
    # parser.add_argument('--best', action='store_true')
    parser.add_argument('--signatures-file', default="")
    parser.add_argument('--signatures-prefix', default="Signature")
    parser.add_argument('--signatures', metavar='K', nargs='*')
    parser.add_argument('--ignore-summary', action='store_true')
    parser.add_argument('--cosmic-version', default='v3')
    return parser.parse_args()


def expected_K(msi, start_sample=0):
    # return np.mean(msi.expected_loadings_samples[:,:,start_sample:] > CUTOFF)*msi.expected_loadings_samples.shape[1]
    return np.sum(np.median(msi.expected_loadings_samples, axis = (0, 2)) > CUTOFF)


def format_template(template, seed, zeta):
    zeta_str = 'zeta-{:.3f}-'.format(zeta) 
    return template.format(seed, zeta_str)


def select_best_seed(sample_file_template, output_file_template, zeta, seeds, skip, all_counts):
    lmls = []
    stdvs = []
    ells = []
    Ks = []
    runtimes = []
    print(zeta, seeds)
    for seed in seeds:
        file_path = format_template(sample_file_template, seed, zeta)
        print(file_path)
        if os.path.isfile(file_path):
            msi, counts, _ = analysis.load_samples_h5_file(
                file_path, verbose=False, cutoff=0, sample_start=0)
            counts = counts or all_counts
            for pname in ['zeta', 'eps', 'J0']:
                msi.parameters.pop(pname, None)
            model = mutsig.MutSigModel(counts, **msi.parameters)
            start = 0
            lml = model.log_marginal_likelihood_approx(msi.loadings_samples[:,:,start::skip],
                msi.mutsigs_samples[:,:,start::skip],
                msi.expected_loadings_samples[:,:,start::skip])
            ll_n = model.log_likelihood(msi.loadings_samples[:,:,start::skip],
                msi.mutsigs_samples[:,:,start::skip],
                msi.expected_loadings_samples[:,:,start::skip], over = "n")
            stdv = np.std(ll_n) / np.sqrt(len(ll_n))
            print(seed, lml, stdv)
            lmls.append(lml) 
            stdvs.append(stdv)
            ell = np.mean(model.log_likelihood(msi.loadings_samples[:,:,start::skip],
                msi.mutsigs_samples[:,:,start::skip],
                msi.expected_loadings_samples[:,:,start::skip]))
            ells.append(ell)
            Ks.append(expected_K(msi))
            runtimes.append(msi.runtime)
        else:
            lmls.append(-np.inf)
            stdvs.append(0)
            ells.append(-np.inf)
            Ks.append(np.nan)
            runtimes.append(np.nan)
    best_ind = np.argmax(lmls)

    plt.figure()
    sns.scatterplot(Ks, lmls, seeds, palette = sns.color_palette("hls", len(seeds)))
    plt.xlabel("K")
    plt.ylabel("LMLE")
    sns.despine()
    plt.savefig(output_file_template.format("K-vs-lmle-zeta-{:.3f}.pdf".format(zeta)), bbox_inches="tight")
    plt.show()

    plt.figure()
    sns.scatterplot(Ks, lmls, seeds, palette = sns.color_palette("hls", len(seeds)))
    plt.errorbar(Ks, lmls, yerr = stdvs, fmt = "none")
    plt.xlabel("K")
    plt.ylabel("LMLE")
    sns.despine()
    plt.savefig(output_file_template.format("K-vs-lmle-zeta-{:.3f}-errorbar.pdf".format(zeta)), bbox_inches="tight")
    plt.show()

    plt.figure()
    plt.plot(Ks, ells, "*")
    plt.xlabel("K")
    plt.ylabel("E [log-likelihood]")
    sns.despine()
    plt.savefig(output_file_template.format("K-vs-log-lik-zeta-{:.3f}.pdf".format(zeta)), bbox_inches="tight")
    plt.close()

    plt.figure()
    sns.scatterplot(lmls, ells, seeds, palette = sns.color_palette("hls", len(seeds)))
    plt.errorbar(lmls, ells, xerr = stdvs, fmt = "none")
    plt.xlabel("LMLE")
    plt.ylabel("E [log-likelihood]")
    sns.despine()
    plt.savefig(output_file_template.format("lmle-vs-log-lik-zeta-{:.3f}.pdf".format(zeta)), bbox_inches="tight")
    plt.close()

    return seeds[best_ind], lmls[best_ind], Ks[best_ind], np.nanmean(runtimes)


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
    print("start")
    # make figures pretty
    sns.set_style('white')
    sns.set_context('notebook', font_scale=1.5, rc={'lines.linewidth': 2})
    matplotlib.rcParams['legend.frameon'] = False

    args = parse_args()
    start_info = args.start_info
    end_info = args.end_info
    save_path = os.path.join(args.base_dir, args.save_dir,
                             '{}-{}-{}multi-zeta'.format(start_info, end_info,
                                                          args.samp_info))
    os.makedirs(save_path, exist_ok=True)
    data = pandas.read_csv(os.path.join(args.base_dir, args.counts_file),
                           sep='\t')
    all_counts = data.iloc[:,1:].values
    sample_names = data.columns[1:].values

    sample_file_template = os.path.join(
        args.base_dir, args.results_dir,
        '{}-seed-{{}}-{}-{{}}{}samples.h5').format(start_info, end_info, args.samp_info)
    output_file_template = os.path.join(save_path, '{}')
    # if args.best:
    #output_file_template = output_file_template.format('best-{}')
    subst_type = args.subst_type
    seeds = args.seeds
    zetas = np.asarray(args.zetas)
    skip = args.skip

    # if args.best:
    summary_file = output_file_template.format('summary.npz')
    print(summary_file)
    if (os.path.exists(summary_file) and not args.ignore_summary):
        print("summary file exists")
        summary = np.load(summary_file)
        best_seeds = summary['best_seeds']
        lmls = summary['lmls']
        Ks = summary['Ks']
        if 'runtimes' in summary:
            runtimes = summary['runtimes']
        else:
            runtimes = None
    else:
        if args.ignore_summary:
            print("ignoring summary file")
        else:
            print("no summary file")
        best_seeds, lmls, Ks, runtimes = zip(*[select_best_seed(sample_file_template, output_file_template,
                                                      zeta, seeds, skip, all_counts)
                                     for zeta in zetas])
        np.savez(summary_file, best_seeds=best_seeds, lmls=lmls, Ks=Ks, runtimes=runtimes)
    valid_inds = np.logical_not(np.isnan(Ks))
    if not np.all(valid_inds):
        print('some zeta values did not have any valid results:',
              ', '.join(map(str, zetas[np.logical_not(valid_inds)])))
    zetas = zetas[valid_inds]
    best_seeds = np.asarray(best_seeds)[valid_inds]
    lmls = np.asarray(lmls)[valid_inds]
    Ks = np.asarray(Ks)[valid_inds]
    if runtimes is not None:
        runtimes = np.asarray(runtimes)[valid_inds] / 3600
        plt.figure()
        plt.plot(zetas, runtimes, '-*')
        plt.xlabel('$\zeta$')
        plt.ylabel('runtime (h)')
        # plt.yscale('log')
        sns.despine()
        plt.tight_layout()
        plt.savefig(output_file_template.format('runtimes.pdf'), bbox_inches='tight')
        plt.close()

    ### analysis of each seed
    # msis = []
    # for zeta, seed in zip(zetas, best_seeds):
    #    name_prefix = 'zeta-{:.3f}-{}'.format(zeta, subst_type)
    #    msis.append(analysis.load_samples_h5_file(
    #        format_template(sample_file_template, seed, zeta), verbose=False,
    #        name_prefix=name_prefix, cutoff=CUTOFF, sample_start=0)[0])
        # XXX temporarily omit
        #sigs, sigs_names, matches, errors = analysis.basic_mugsig_inference_analysis(
        #    msis[-1], subst_type=subst_type, save_path=save_path,
        #    loadings_analysis=False, pages=False)
    # else:
    #     msis = []
    #     Ks = []
    #     cutoff = .1
    #     lmls = np.zeros(len(zetas))
        # for i, zeta in enumerate(zetas):
        #     name_prefix = 'zeta-{:.3f}-{}'.format(zeta, subst_type)
        #     Ksum = 0
        #     for seed in seeds:
        #         msi, counts, _ = analysis.load_samples_h5_file(
        #             format_template(sample_file_template, seed, zeta),
        #             verbose=False, name_prefix=name_prefix, cutoff=cutoff,
        #             sample_start=0)
        #         Ksum += expected_K(msi)
        #         counts = counts or all_counts
        #         for pname in ['zeta', 'eps', 'J0']:
        #             msi.parameters.pop(pname, None)
        #         model = mutsig.MutSigModel(counts, **msi.parameters)
        #         lml = model.log_marginal_likelihood(
        #             msi.loadings_samples[:,:,::skip],
        #             msi.mutsigs_samples[:,:,::skip],
        #             msi.expected_loadings_samples[:,:,::skip])
        #         lmls[i] += lml
        #     Ks.append(Ksum / len(seeds))
        # lmls /= len(seeds)

    def plot_diagnostics(ys, yname, ynameshort, xs, xname, xnameshort):
        d_xs = np.diff(xs)
        d_ys = np.diff(ys) / d_xs
        dd_ys = np.abs(2 * np.diff(d_ys) / (d_xs[:-1] + d_xs[1:]))

        plt.figure()
        plt.plot(xs, ys, '-*')
        plt.xlabel(xname)
        plt.ylabel(yname)
        sns.despine()
        plt.savefig(output_file_template.format(xnameshort + '-vs-' + ynameshort + '.pdf'), bbox_inches='tight')
        plt.close()

        plt.figure()
        plt.plot(xs[:-1], d_ys, '-*')
        plt.xlabel(xname)
        plt.ylabel('D' + yname)
        sns.despine()
        plt.savefig(output_file_template.format(xnameshort + '-vs-d-' + ynameshort + '.pdf'), bbox_inches='tight')
        plt.close()

        plt.figure()
        plt.plot(xs[1:-1], dd_ys, '-*', label='unnormalized')
        plt.plot(xs[1:-1], dd_ys / (d_ys[1:] + d_ys[:-1]), '-*', label='normalized')
        plt.plot(xs[1:-1], dd_ys / np.square(d_ys[1:] + d_ys[:-1]), '-*', label='normalized (square)')
        plt.xlabel(xname)
        plt.ylabel('DD' + yname)
        plt.yscale('log')
        plt.legend()
        sns.despine()
        plt.savefig(output_file_template.format(xnameshort + '-vs-dd-' + ynameshort + '.pdf'), bbox_inches='tight')
        plt.close()

    plot_diagnostics(lmls, 'approx log marginal likelihood', 'log-lik', zetas, '$\zeta$', 'zeta')

    Kzetas = np.array(Ks) + np.array(zetas)
    plot_diagnostics(lmls, 'approx log marginal likelihood', 'log-lik', Kzetas, '$K + \zeta$', 'K+zeta')


    plot_Ks = []
    plot_lmls = []
    for K, lml in zip(Ks, lmls):
        if K not in plot_Ks:
            plot_Ks.append(K)
            plot_lmls.append(lml)

    plot_diagnostics(plot_lmls, 'approx log marginal likelihood', 'log-lik', plot_Ks, '$K$', 'K')

    # plt.figure()
    # plt.plot(Ks, lmls, '-*')
    # plt.gca().annotate('$\zeta$ = {:.3f}'.format(zetas[0]), (Ks[0], lmls[0]))
    # plt.gca().annotate('$\zeta$ = {:.3f}'.format(zetas[-1]), (Ks[-1], lmls[-1]))
    # plt.xlabel('K')
    # plt.ylabel('E[loglik | data]')
    # sns.despine()
    # plt.savefig(output_file_template.format('K-vs-log-lik.pdf'), bbox_inches='tight')
    # plt.close()

    plt.figure()
    plt.plot(zetas, Ks, '-*')
    plt.xlabel('$\zeta$')
    plt.ylabel('K')
    sns.despine()
    plt.savefig(output_file_template.format('zeta-vs-K.pdf'),
                bbox_inches='tight')
    plt.close()

    plt.figure()
    plt.plot(zetas, Ks, '-*')
    plt.xlabel('$\zeta$')
    plt.ylabel('K')
    plt.xscale('log')
    sns.despine()
    plt.savefig(output_file_template.format('log-zeta-vs-K.pdf'),
                bbox_inches='tight')
    plt.close()

    ### analysis of each seed
    msis = []
    for zeta, seed in zip(zetas, best_seeds):
        name_prefix = 'zeta-{:.3f}-{}'.format(zeta, subst_type)
        msis.append(analysis.load_samples_h5_file(
            format_template(sample_file_template, seed, zeta), verbose=False,
            name_prefix=name_prefix, cutoff=CUTOFF, sample_start=0)[0])

    if args.signatures_file == "":
        comp_sigs, comp_sig_names = mutsig.cosmic_signatures(subst_type = subst_type, validated = True, version = args.cosmic_version)
    else:
        comp_sigs, comp_sig_names = read_new_sigs(args.signatures_file, args.signatures_prefix)
    comp_sigs[comp_sigs <= 0] = 1e-10

    if args.signatures == []:
        use_sig_inds = np.arange(len(comp_sig_names))
    elif args.signatures_file == "" and args.cosmic_version == "v3":
        use_sig_inds = np.array(mutsig.cosmic_v3_SBS_to_index(args.signatures)) - 1
    else:
        use_sig_inds = np.array(args.signatures) - 1
    num_sigs = use_sig_inds.size
    comp_sigs = comp_sigs[use_sig_inds]
    comp_sig_names = comp_sig_names[use_sig_inds]

    def sig_names_with_mu(msi):
        return [r'{} ($\mu$ = {})'.format(sn, int(mu)) for sn, mu in zip(msi.sig_names, msi.mean_expected_loadings)]

    ## Compare best signatures to existing ones
    for zeta, msi in zip(zetas, msis):
        plotting.plot_loadings_matrix(msi.mean_loadings, msi.sig_names, sample_names, title=None,
                                      save_path=output_file_template.format('best-seed-loadings-zeta-{:.3f}.pdf'.format(zeta)))
        analysis.compare_signatures(
            msi.mutsigs_samples.squeeze(), sig_names_with_mu(msi), comp_sigs, comp_sig_names, top=2, bipartite = True, save_path_base=output_file_template.format(
                'best-seed-comparison-zeta-{:.3f}'.format(zeta)))
        plt.close('all')
        np.savetxt(output_file_template.format('best-seed-loadings-zeta-{:.3f}.tsv'.format(zeta)), msi.mean_loadings[0:expected_K(msi),:], delimiter = "\t")
        np.savetxt(output_file_template.format('best-seed-sigs-zeta-{:.3f}.tsv'.format(zeta)), msi.mean_mutsigs[0:expected_K(msi),:], delimiter = "\t")

    ### Compare all signatures to existing ones
    for zeta in zetas:
        name_prefix = 'zeta-{:.3f}-{}'.format(zeta, subst_type)
        for seed in seeds:
            file_path = format_template(sample_file_template, seed, zeta)
            if os.path.isfile(file_path):
                msi = analysis.load_samples_h5_file(
                        file_path, verbose=False, name_prefix=name_prefix,
                        cutoff=CUTOFF, sample_start=0)[0]
                plotting.plot_loadings_matrix(msi.mean_loadings, msi.sig_names, sample_names, title=None,
                                      save_path=output_file_template.format('comparison-zeta-{:.3f}-seed-{}-loadings.pdf'.format(zeta, seed)))
                analysis.compare_signatures(
                    msi.mutsigs_samples.squeeze(), sig_names_with_mu(msi), comp_sigs, comp_sig_names, top=2, bipartite = True, save_path_base=output_file_template.format(
                        'comparison-zeta-{:.3f}-seed-{}'.format(zeta, seed)))
                plt.close('all')

    ## Visualize signatures and data using PCA
    # if len(args.signatures) > 0:
    #     cosmic_sigs, _ = mutsig.cosmic_signatures()
    #     use_sig_inds = np.array(args.signatures) - 1
    #     num_sigs = len(use_sig_inds)
    #     sigs = cosmic_sigs[use_sig_inds]
    #     sig_names = ['Sig {}'.format(i+1) for i in use_sig_inds]
    # elif args.signatures_file is not None:
    #     sigs = comp_sigs
    #     sig_names = comp_sig_names
    # else:
    #     sigs = None
    # if sigs is not None:
    #     kernel = 'cosine'
    #     pca_fig_file = output_file_template.format('mutsig-pcs')
    #     if kernel is not None:
    #         pca_fig_file += '-' + kernel + '-kernel'

    #     # plt.figure()
    #     # colors = sns.color_palette('Purples_d', n_colors=len(zetas))
    #     # colors.reverse()
    #     # inferred_mutsigs = [(msi.mean_mutsigs, None, '$\zeta =$ {:.3f} (K = {:.1f}'.format(zeta, K),
    #     #                      dict(color=color, marker='*', markersize=10))
    #     #                         for msi, zeta, K, color in zip(msis, zetas, Ks, colors)]
    #     # plotting.plot_mutsigs_pca(*inferred_mutsigs
    #     #                           + [(all_counts.T, None, 'Data', dict(color='k', markersize=3)),
    #     #                              (sigs, sig_names, 'True', dict(marker='o', markersize=6, color='b'))],
    #     #                           #(np.eye(96), None, 'Extreme points', dict(marker='*', markersize=4, color='m')),
    #     #                           #(msis[seed].mean_mutsigs, None, 'MCMC'),
    #     #                           kernel=kernel, pcs_from=all_counts.T,
    #     #                           show=False)
    #     # plt.savefig(pca_fig_file + '.pdf', bbox_inches='tight')
    #     # plt.close()
    #     n_pcs = min(5, len(sig_names)) - 1
    #     n_cols = n_pcs - 1
    #     thin_samples = max(1, int(msis[0].mutsigs_samples.shape[-1] / 2000))
    #     with PdfPages(pca_fig_file + '-detailed.pdf') as pdf:
    #         for zeta, msi, K in zip(zetas, msis, Ks):
    #             # plt.figure(figsize=(9, 5))
    #             fig, axes = plt.subplots(1, n_cols,
    #                                      figsize=(4*(n_cols+1), 7),
    #                                      sharey=True, sharex=True, squeeze=True)
    #             plotting.plot_mutsigs_pca(*[(all_counts.T, None, 'Data', dict(color='k', markersize=3)),
    #                                         (sigs, sig_names, 'True', dict(marker='o', markersize=6, color='b'))]
    #                                       +[(mutsigs[:,::thin_samples].T, None, '{} ($\mu =$ {:.1f})'.format(msi.sig_names[i],
    #                                                                                                       msi.mean_expected_loadings[i]),
    #                                                                                                       dict(marker='.', markersize=10))
    #                                                 for i, mutsigs in enumerate(msi.mutsigs_samples)],
    #                                       kernel=kernel, pcs_from=sigs, #all_counts.T,
    #                                       ax=axes, show=False)
    #             plt.title('$\zeta = {:.3f}$ (K = {})'.format(zeta, K))
    #             plt.tight_layout()
    #             pdf.savefig(box_inches='tight')
    #             plt.close()


if __name__ == '__main__':
    main()
