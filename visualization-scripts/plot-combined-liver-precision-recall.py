import os

import numpy as np
import pandas as pd

import matplotlib
if 'DISPLAY' not in os.environ:
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import seaborn as sns



MAX_CUTOFF = 0.2



def main():
    sns.set_style('white')
    sns.set_context('notebook', font_scale = 1.5, rc = {'lines.linewidth': 2})
    matplotlib.rcParams['legend.frameon'] = False

    base_dir = "/n/miller_lab/csxue/comparisons"
    figs_dir = "liver-subsampling-overall"

    # exp_dirs = ["subsample-liver-30", "subsample-liver-80", "subsample-liver-170", "liver-WS"]
    exp_dirs = ["subsample-liver-30", "subsample-liver-80", "subsample-liver-170"]

    x = np.linspace(0, MAX_CUTOFF, 100)
    recall_spe_all = []
    recall_bps_all = []
    precision_spe_all = []
    precision_bps_all = []

    ## compile the results
    for exp_dir in exp_dirs:
        exp_list = open(os.path.join(base_dir, exp_dir, "experiment_list.txt"))

        recall_spe = []
        recall_bps = []
        precision_spe = []
        precision_bps = []

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

        recall_spe = np.array(recall_spe)
        recall_bps = np.array(recall_bps)
        precision_spe = np.array(precision_spe)
        precision_bps = np.array(precision_bps)

        recall_spe_all.append(recall_spe)
        recall_bps_all.append(recall_bps)
        precision_spe_all.append(precision_spe)
        precision_bps_all.append(precision_bps)

        exp_list.close()


    ## Plot precision and recall
    plt.figure() 
    plt.plot(x, np.mean(precision_bps_all[0], axis = 0), label = "BayesPowerNMF, n = 30")
    plt.plot(x, np.mean(precision_bps_all[1], axis = 0), label = "BayesPowerNMF, n = 80", color = "C0", linestyle = "dashed")
    plt.plot(x, np.mean(precision_bps_all[2], axis = 0), label = "BayesPowerNMF, n = 170", color = "C0", linestyle = "dotted")
    # plt.plot(x, np.mean(precision_bps_all[3], axis = 0), label = "BayesPowerNMF, n = 326", color = "C0", linestyle = "dashdot")
    plt.plot(x, np.mean(precision_spe_all[0], axis = 0), label = "SigProfilerExtractor, n = 30", color = "C3")
    plt.plot(x, np.mean(precision_spe_all[1], axis = 0), label = "SigProfilerExtractor, n = 80", color = "C3", linestyle = "dashed")
    plt.plot(x, np.mean(precision_spe_all[2], axis = 0), label = "SigProfilerExtractor, n = 170", color = "C3", linestyle = "dotted")
    # plt.plot(x, np.mean(precision_spe_all[3], axis = 0), label = "SigProfilerExtractor, n = 326", color = "C3", linestyle = "dashdot")
    plt.xlabel("cosine error cutoff")
    plt.ylabel("precision")
    plt.ylim([0, 1])
    # plt.title(title, fontsize = 25)
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(base_dir, figs_dir, "precision.pdf"), bbox_inches = "tight")
    plt.legend(loc = "center left", bbox_to_anchor = (1, 0.5))
    # plt.legend()
    plt.savefig(os.path.join(base_dir, figs_dir, "precision_with_legend.pdf"), bbox_inches = "tight")
    plt.close()

    plt.figure() 
    plt.plot(x, np.mean(recall_bps_all[0], axis = 0), label = "BayesPowerNMF, n = 30")
    plt.plot(x, np.mean(recall_bps_all[1], axis = 0), label = "BayesPowerNMF, n = 80", color = "C0", linestyle = "dashed")
    plt.plot(x, np.mean(recall_bps_all[2], axis = 0), label = "BayesPowerNMF, n = 170", color = "C0", linestyle = "dotted")
    # plt.plot(x, np.mean(recall_bps_all[3], axis = 0), label = "BayesPowerNMF, n = 326", color = "C0", linestyle = "dashdot")
    plt.plot(x, np.mean(recall_spe_all[0], axis = 0), label = "SigProfilerExtractor, n = 30", color = "C3")
    plt.plot(x, np.mean(recall_spe_all[1], axis = 0), label = "SigProfilerExtractor, n = 80", color = "C3", linestyle = "dashed")
    plt.plot(x, np.mean(recall_spe_all[2], axis = 0), label = "SigProfilerExtractor, n = 170", color = "C3", linestyle = "dotted")
    # plt.plot(x, np.mean(recall_spe_all[3], axis = 0), label = "SigProfilerExtractor, n = 326", color = "C3", linestyle = "dashdot")
    plt.xlabel("cosine error cutoff")
    plt.ylabel("recall")
    plt.ylim([0, 0.8]) # for subsampling
    # plt.ylim([0, 1]) # for regular
    # plt.title(title, fontsize = 25)
    # plt.title(" ", fontsize = 25)
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(base_dir, figs_dir, "recall.pdf"), bbox_inches = "tight") #_WS_xi1
    plt.legend(loc = "center left", bbox_to_anchor = (1, 0.5))
    # plt.legend()
    plt.savefig(os.path.join(base_dir, figs_dir, "recall_with_legend.pdf"), bbox_inches = "tight")
    plt.close()



if __name__ == '__main__':
    main()
