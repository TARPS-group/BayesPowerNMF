import os
import argparse

import numpy as np
import pandas as pd

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
    parser.add_argument("title")
    return parser.parse_args()


def main():
    sns.set_style('white')
    sns.set_context('notebook', font_scale = 1.5, rc = {'lines.linewidth': 2})
    matplotlib.rcParams['legend.frameon'] = False

    args = parse_args()

    base_dir = "/n/miller_lab/csxue/comparisons"
    exp_list = open(os.path.join(base_dir, args.figs_dir, "experiment_list.txt"))

    x = np.linspace(0, MAX_CUTOFF, 100)
    recall_spe = []
    recall_bps = []
    recall_bps_1 = []
    recall_sa = []
    precision_spe = []
    precision_bps = []
    precision_bps_1 = []
    precision_sa = []

    ## compile the results
    for exp in exp_list:
        print("\n" + exp)
        exp_name = exp.replace("\n", "")
        
        ## compile precision-recall
        df = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_SPE_matched_errors.csv"), index_col = 0)
        K = np.load(os.path.join(base_dir, exp_name, exp_name + "_SPE_results.npz"))["sigs"].shape[1]
        recall_spe.append(np.array([sum(df["error"] < cutoff) / df.shape[0] for cutoff in x]))
        precision_spe.append(np.array([sum(df["error"] < cutoff) / K for cutoff in x]))

        df = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_BPS_matched_errors.csv"), index_col = 0)
        K = np.load(os.path.join(base_dir, exp_name, exp_name + "_BPS_results.npz"))["sigs"].shape[1]
        recall_bps.append(np.array([sum(df["error"] < cutoff) / df.shape[0] for cutoff in x]))
        precision_bps.append(np.array([sum(df["error"] < cutoff) / K for cutoff in x]))

        if "WS" in args.figs_dir:
            df = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_BPS-power-1_matched_errors.csv"), index_col = 0)
            K = len(pd.read_csv(os.path.join(base_dir, exp_name, "best-seed-comparison-zeta-1.000-list.csv")))
            recall_bps_1.append(np.array([sum(df["error"] < cutoff) / df.shape[0] for cutoff in x]))
            precision_bps_1.append(np.array([sum(df["error"] < cutoff) / K for cutoff in x]))

        if "subsample" not in args.figs_dir:
            df = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_SA_matched_errors.csv"), index_col = 0)
            K = np.load(os.path.join(base_dir, exp_name, exp_name + "_SA_results.npz"))["sigs"].shape[1]
            recall_sa.append(np.array([sum(df["error"] < cutoff) / df.shape[0] for cutoff in x]))
            precision_sa.append(np.array([sum(df["error"] < cutoff) / K for cutoff in x]))

        # ## compile loadings-weighted precision-recall
        # df = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_SPE_matched_errors.csv"), index_col = 0)
        # gt_total_mean_loading = sum(df["mean_loadings"])
        # inferred_total_mean_loading = sum(np.mean(np.load(os.path.join(base_dir, exp_name, exp_name + "_SPE_results.npz"))["loadings"], axis = 0))
        # numerator = np.array([sum([min(il, gl) for il, gl in zip(df[df["error"] < cutoff]["inferred_mean_loadings"], 
        #                                                          df[df["error"] < cutoff]["mean_loadings"])]) for cutoff in x])
        # recall_spe.append(numerator / gt_total_mean_loading)
        # precision_spe.append(numerator / inferred_total_mean_loading)

        # df = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_BPS_matched_errors.csv"), index_col = 0)
        # gt_total_mean_loading = sum(df["mean_loadings"])
        # inferred_total_mean_loading = sum(np.mean(np.load(os.path.join(base_dir, exp_name, exp_name + "_BPS_results.npz"))["loadings"], axis = 0))
        # numerator = np.array([sum([min(il, gl) for il, gl in zip(df[df["error"] < cutoff]["inferred_mean_loadings"], 
        #                                                          df[df["error"] < cutoff]["mean_loadings"])]) for cutoff in x])
        # recall_bps.append(numerator / gt_total_mean_loading)
        # precision_bps.append(numerator / inferred_total_mean_loading)

        # if "subsample" not in args.figs_dir:
        #     df = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_SA_matched_errors.csv"), index_col = 0)
        #     gt_total_mean_loading = sum(df["mean_loadings"])
        #     inferred_total_mean_loading = sum(np.mean(np.load(os.path.join(base_dir, exp_name, exp_name + "_SA_results.npz"))["loadings"], axis = 0))
        #     numerator = np.array([sum([min(il, gl) for il, gl in zip(df[df["error"] < cutoff]["inferred_mean_loadings"], 
        #                                                              df[df["error"] < cutoff]["mean_loadings"])]) for cutoff in x])
        #     recall_sa.append(numerator / gt_total_mean_loading)
        #     precision_sa.append(numerator / inferred_total_mean_loading)


    exp_list.close()

    recall_spe = np.array(recall_spe)
    recall_bps = np.array(recall_bps)
    recall_sa = np.array(recall_sa)
    precision_spe = np.array(precision_spe)
    precision_bps = np.array(precision_bps)
    precision_sa = np.array(precision_sa)

    ## Plot precision and recall
    # plt.figure()
    # plt.plot(x, np.mean(precision_bps, axis = 0), label = "BayesPowerNMF")
    # # plt.plot(x, np.mean(precision_bps_1, axis = 0), label = "BayesPowerNMF, power = 1", color = "C0", linestyle = "dashed")
    # plt.plot(x, np.mean(precision_spe, axis = 0), label = "SigProfilerExtractor", color = "C3")
    # plt.plot(x, np.mean(precision_sa, axis = 0), label = "SignatureAnalyzer", color = "C8")
    # plt.xlabel("cosine error cutoff")
    # plt.ylabel("precision")
    # plt.ylim([0, 1])
    # plt.title(args.title, fontsize = 25)
    # sns.despine()
    # plt.tight_layout()
    # plt.savefig(os.path.join(base_dir, args.figs_dir, "precision.pdf"), bbox_inches = "tight")
    # plt.legend()
    # plt.savefig(os.path.join(base_dir, args.figs_dir, "precision_with_legend.pdf"), bbox_inches = "tight")
    # plt.close()

    plt.figure()
    plt.plot(x, np.mean(recall_bps, axis = 0), label = "BayesPowerNMF")
    # plt.plot(x, np.mean(precision_bps_1, axis = 0), label = "BayesPowerNMF, power = 1", color = "C0", linestyle = "dashed")
    plt.plot(x, np.mean(recall_spe, axis = 0), label = "SigProfilerExtractor", color = "C3")
    # plt.plot(x, np.mean(recall_sa, axis = 0), label = "SignatureAnalyzer", color = "C8")
    plt.xlabel("cosine error cutoff")
    plt.ylabel("recall")
    plt.ylim([0, 0.8]) # for subsampling
    # plt.ylim([0, 1]) # for regular
    # plt.title(args.title, fontsize = 25)
    plt.title(" ", fontsize = 25)
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(base_dir, args.figs_dir, "recall.pdf"), bbox_inches = "tight") #_WS_xi1
    # plt.legend(loc = "center left", bbox_to_anchor = (1, 0.5))
    plt.legend()
    plt.savefig(os.path.join(base_dir, args.figs_dir, "recall_with_legend.pdf"), bbox_inches = "tight")
    plt.close()



if __name__ == '__main__':
    main()
