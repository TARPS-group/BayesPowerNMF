import os
import numpy as np
import pandas as pd

import matplotlib
if 'DISPLAY' not in os.environ:
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FormatStrFormatter
import matplotlib.lines as mlines

import seaborn as sns



def main():
    sns.set_style('white')
    sns.set_context('notebook', font_scale = 1.5, rc = {'lines.linewidth': 2})
    matplotlib.rcParams['legend.frameon'] = False

    base_dir = "/n/miller_lab/csxue/comparisons/liver-subsampling-overall/"

    bps = pd.read_csv(os.path.join(base_dir, "BPS-liver-subsample-K.tsv"), sep = "\t", header = None)
    bps[1] = [int(s.split("-")[4]) for s in bps[0]]
    bps[0] = [int(s.split("-")[2]) for s in bps[0]]
    bps.rename(columns = {0: "size", 1: "replicate", 2: "K"}, inplace = True)
    bps["method"] = "BayesPowerNMF"

    spe = pd.read_csv(os.path.join(base_dir, "SPE-liver-subsample-K-paired.tsv"), sep = ":", header = None)
    spe[1] = [int(s.split("-")[-1]) for s in spe[0]]
    lst = [int(s.split("-")[-3]) for s in spe[0][:-1]]
    lst.append(326)
    spe[0] = lst
    spe.rename(columns = {0: "size", 1: "replicate", 2: "K"}, inplace = True)
    spe["method"] = "SigProfilerExtractor"
    
    ## Plot Ks
    df = pd.concat([bps, spe], ignore_index = True)
    df.sort_values("size")
    df["size"] = [str(s) for s in df["size"]]

    ymin = 0
    ymax = 15.5
    ticks = np.arange(ymin, ymax, step = 3)
    ticklabs = [str(int(x)) for x in ticks]
    bps_leg = mlines.Line2D([], [], color = "C0", label = "BayesPowerNMF")
    spe_leg = mlines.Line2D([], [], color = "C3", label = "SigProfilerExtractor")

    plt.figure()
    sns.pointplot(data = bps, x = "size", y = "K", color = "C0", ci = 95, label = "BayesPowerNMF")
    ax = sns.pointplot(data = spe, x = "size", y = "K", color = "C3", ci = 95, label = "SigProfilerExtractor")    
    plt.setp(ax.lines, alpha = 0.5)  
    plt.xlabel("subsample size")
    plt.ylabel("# signatures inferred")
    plt.ylim([ymin, ymax])
    plt.yticks(ticks = ticks, labels = ticklabs)
    plt.grid(axis = "y")
    plt.title("Inferred signature count in liver subsamples")
    plt.legend(handles = [bps_leg, spe_leg])
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(base_dir, "synthetic-liver-subsampling-inferred-signatures-total.pdf"), bbox_inches = "tight")
    plt.close()

    # plt.figure()
    # sns.pointplot(data = bps, x = "size", y = "K", color = "C0", ci = 95)
    # ax = sns.pointplot(data = spe, x = "size", y = "K", color = "C3", ci = 95)
    # plt.setp(ax.collections, alpha = 0.5) 
    # plt.setp(ax.lines, alpha = 0.5)  
    # sns.swarmplot(data = df, x = "size", y = "K", hue = "method", palette = ["C0", "C3"], hue_order = ["BayesPowerNMF", "SigProfilerExtractor"])
    # plt.xlabel("subsample size")
    # plt.ylabel("# signatures inferred")
    # plt.ylim([0, ymax])
    # plt.yticks(ticks = ticks, labels = ticklabs)
    # plt.title("Inferred signature count in liver subsamples")
    # sns.despine()
    # plt.tight_layout()
    # plt.savefig(os.path.join(base_dir, "synthetic-liver-subsampling-inferred-signatures-total-swarm.pdf"), bbox_inches = "tight")
    # plt.close()


    ## plot difference
    diff = bps.copy()
    diff["method"] = "difference"
    for i in range(diff.shape[0]):
        diff.loc[i, "K"] = bps.loc[i, "K"] - spe[(spe["size"] == bps.loc[i, "size"]) & (spe["replicate"] == bps.loc[i, "replicate"])].iloc[0, 2]

    diff.sort_values("size", inplace = True)
    diff["size"] = [str(s) for s in diff["size"]]

    ymin = 2
    ymax = 8.5
    ticks = np.arange(ymin, ymax, step = 1)
    ticklabs = [str(int(x)) for x in ticks]

    plt.figure(figsize = (12, 4.8))
    # sns.pointplot(data = diff, x = "size", y = "K", color = "C2", ci = 95)    
    sns.swarmplot(data = diff, x = "size", y = "K", hue = "size", size = 5, 
        palette = ["C2", "yellowgreen", "C2", "yellowgreen", "C2", "yellowgreen", "C2", "yellowgreen"])    
    plt.xlabel("subsample size")
    plt.ylabel("Difference in\n# signatures inferred")
    plt.title("Difference in # signatures inferred by subsample size")
    sns.despine()
    plt.tight_layout()
    plt.legend([], [], frameon = False)
    plt.savefig(os.path.join(base_dir, "synthetic-liver-subsampling-inferred-signatures-difference.pdf"), bbox_inches = "tight")
    plt.close()

    # plt.figure()
    # ax = sns.pointplot(data = diff, x = "size", y = "K", color = "C2", ci = 95)
    # plt.setp(ax.collections, alpha = 0.5) 
    # plt.setp(ax.lines, alpha = 0.5)  
    # sns.swarmplot(data = diff, x = "size", y = "K", color = "C2")
    # plt.xlabel("subsample size")
    # plt.ylabel("Difference in # signatures inferred")
    # plt.ylim([ymin - 0.5, ymax])
    # plt.yticks(ticks = ticks, labels = ticklabs)
    # sns.despine()
    # plt.tight_layout()
    # plt.savefig(os.path.join(base_dir, "synthetic-liver-subsampling-inferred-signatures-difference-swarm.pdf"), bbox_inches = "tight")
    # plt.close()



if __name__ == '__main__':
    main()
