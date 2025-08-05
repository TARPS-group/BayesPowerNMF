import os
import argparse

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
if 'DISPLAY' not in os.environ:
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import seaborn as sns



MAX_CUTOFF = 0.2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("figs_dir")
    return parser.parse_args()


def plot_matched_loadings(matched, unmatched, output_dir, method, method_abbrev):
    matched = np.log10(matched)
    unmatched = np.log10(unmatched)
    min_val = min(matched.min(), unmatched.min())
    max_val = max(matched.max(), unmatched.max())
    bins = np.linspace(min_val, max_val, 9)
    plt.hist([matched, unmatched], bins, label = ["Discovered", "Missing"], color = ["C3", "C4"])
    xticks = np.arange(int(min_val), int(max_val) + 1, dtype = int)
    xticklabels = [r'$10^{{{}}}$'.format(v) for v in xticks]
    plt.xticks(ticks = xticks, labels = xticklabels)
    plt.ylabel("number")
    plt.xlabel("loading")
    plt.title(method)
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, method_abbrev + "-matched-loadings.pdf"), bbox_inches = "tight")
    plt.legend()
    plt.savefig(os.path.join(output_dir, method_abbrev + "-matched-loadings_with_legend.pdf"), bbox_inches = "tight")
    plt.close()
    return None


def main():
    sns.set_style('white')
    sns.set_context('notebook', font_scale = 1.5, rc = {'lines.linewidth': 2})
    matplotlib.rcParams['legend.frameon'] = False

    args = parse_args()

    base_dir = "/n/miller_lab/csxue/comparisons"
    exp_list = open(os.path.join(base_dir, args.figs_dir, "experiment_list.txt"))

    spe = pd.DataFrame()
    bps = pd.DataFrame()
    sa = pd.DataFrame()

    ## compile the results
    for exp in exp_list:
        print("\n" + exp)
        exp_name = exp.replace("\n", "")
        
        ## compile overall matched error list
        if spe.empty:
            spe = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_SPE_matched_errors.csv"), index_col = 0)
            spe["experiment"] = exp_name
        else:
            df = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_SPE_matched_errors.csv"), index_col = 0)
            df["experiment"] = exp_name
            spe = pd.concat([spe, df]) 
        
        if bps.empty:
            bps = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_BPS_matched_errors.csv"), index_col = 0)
            bps["experiment"] = exp_name
        else:
            df = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_BPS_matched_errors.csv"), index_col = 0)
            df["experiment"] = exp_name
            bps = pd.concat([bps, df])

        if "subsample" not in args.figs_dir:
            if sa.empty:
                sa = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_SA_matched_errors.csv"), index_col = 0)
                sa["experiment"] = exp_name
            else:
                df = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_SA_matched_errors.csv"), index_col = 0)
                df["experiment"] = exp_name
                sa = pd.concat([sa, df])

    exp_list.close()


    ## Loadings histogram
    spe_matched = spe[spe["matched"] == True]["mean_loadings"]
    spe_unmatched = spe[spe["matched"] == False]["mean_loadings"]
    bps_matched = bps[bps["matched"] == True]["mean_loadings"]
    bps_unmatched = bps[bps["matched"] == False]["mean_loadings"]
    sa_matched = sa[sa["matched"] == True]["mean_loadings"]
    sa_unmatched = sa[sa["matched"] == False]["mean_loadings"]

    summary = open(os.path.join(base_dir, args.figs_dir, "matched_loadings_summary.txt"), 
        mode = "w")
    summary.write("SigProfilerExtractor:\n")
    summary.write("U = {:.1f}\n".format(stats.mannwhitneyu(spe_matched, spe_unmatched)[0]))
    summary.write("p = {:.5f}\n".format(stats.mannwhitneyu(spe_matched, spe_unmatched)[1]))
    summary.write("\nBayesPowerNMF:\n")
    summary.write("U = {:.1f}\n".format(stats.mannwhitneyu(bps_matched, bps_unmatched)[0]))
    summary.write("p = {:.5f}\n".format(stats.mannwhitneyu(bps_matched, bps_unmatched)[1]))
    summary.close()

    plot_matched_loadings(spe_matched, spe_unmatched, os.path.join(base_dir, args.figs_dir), "SigProfilerExtractor", "spe")
    plot_matched_loadings(bps_matched, bps_unmatched, os.path.join(base_dir, args.figs_dir), "BayesPowerNMF", "bps")
    if "subsample" not in args.figs_dir:
        plot_matched_loadings(sa_matched, sa_unmatched, os.path.join(base_dir, args.figs_dir), "SignatureAnalyzer", "sa")

    # spe_matched = np.log10(spe_matched)
    # spe_unmatched = np.log10(spe_unmatched)
    # min_val = min(spe_matched.min(), spe_unmatched.min())
    # max_val = max(spe_matched.max(), spe_unmatched.max())
    # bins = np.linspace(min_val, max_val, 9)
    # plt.hist([spe_matched, spe_unmatched], bins, label = ["Discovered", "Missing"], color = ["C3", "C4"])
    # xticks = np.arange(int(min_val), int(max_val) + 1, dtype = int)
    # xticklabels = [r'$10^{{{}}}$'.format(v) for v in xticks]
    # plt.xticks(ticks = xticks, labels = xticklabels)
    # plt.ylabel("number")
    # plt.xlabel("loading")
    # plt.title("SigProfilerExtractor")
    # sns.despine()
    # plt.tight_layout()
    # plt.savefig(os.path.join(base_dir, args.figs_dir, "spe-matched-loadings.pdf"), bbox_inches = "tight")
    # plt.legend()
    # plt.savefig(os.path.join(base_dir, args.figs_dir, "spe-matched-loadings_with_legend.pdf"), bbox_inches = "tight")
    # plt.close()

    # bps_matched = np.log10(bps_matched)
    # bps_unmatched = np.log10(bps_unmatched)
    # min_val = min(bps_matched.min(), bps_unmatched.min())
    # max_val = max(bps_matched.max(), bps_unmatched.max())
    # bins = np.linspace(min_val, max_val, 9)
    # plt.hist([bps_matched, bps_unmatched], bins, label = ["Discovered", "Missing"], color = ["C3", "C4"])
    # xticks = np.arange(int(min_val), int(max_val) + 1, dtype = int)
    # xticklabels = [r'$10^{{{}}}$'.format(v) for v in xticks]
    # plt.xticks(ticks = xticks, labels = xticklabels)
    # plt.ylabel("number")
    # plt.xlabel("loading")
    # plt.title("BayesPowerNMF")
    # sns.despine()
    # plt.tight_layout()
    # plt.savefig(os.path.join(base_dir, args.figs_dir, "bps-matched-loadings.pdf"), bbox_inches = "tight")
    # plt.legend()
    # plt.savefig(os.path.join(base_dir, args.figs_dir, "bps-matched-loadings_with_legend.pdf"), bbox_inches = "tight")
    # plt.close()

    # if "subsample" not in args.figs_dir:
    #     sa_matched = sa[sa["matched"] == True]["mean_loadings"]
    #     sa_unmatched = sa[sa["matched"] == False]["mean_loadings"]
    #     sa_matched = np.log10(sa_matched)
    #     sa_unmatched = np.log10(sa_unmatched)
    #     min_val = min(sa_matched.min(), sa_unmatched.min())
    #     max_val = max(sa_matched.max(), sa_unmatched.max())
    #     bins = np.linspace(min_val, max_val, 9)
    #     plt.hist([sa_matched, sa_unmatched], bins, label = ["Discovered", "Missing"], color = ["C3", "C4"])
    #     xticks = np.arange(int(min_val), int(max_val) + 1, dtype = int)
    #     xticklabels = [r'$10^{{{}}}$'.format(v) for v in xticks]
    #     plt.xticks(ticks = xticks, labels = xticklabels)
    #     plt.ylabel("number")
    #     plt.xlabel("loading")
    #     plt.title("SignatureAnalyzer")
    #     sns.despine()
    #     plt.tight_layout()
    #     plt.savefig(os.path.join(base_dir, args.figs_dir, "sa-matched-loadings.pdf"), bbox_inches = "tight")
    #     plt.legend()
    #     plt.savefig(os.path.join(base_dir, args.figs_dir, "sa-matched-loadings_with_legend.pdf"), bbox_inches = "tight")
    #     plt.close()    
    



if __name__ == '__main__':
    main()
