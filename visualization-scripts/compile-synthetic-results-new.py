import os
import numpy as np
import pandas as pd

from mutsigtools import analysis, mutsig


MAX_CUTOFF = 0.5


def get_matches_and_errors(inferred_sigs, inferred_mean_loadings, comp_sigs, cutoff, 
                           gt_mean_loadings, gt_sig_inds):
    sig_inds, comp_matches, error = analysis.match_signatures(
        inferred_sigs, comp_sigs, bipartite = True, oldstyle = False)
    valid_matches = np.unique(comp_matches[error < cutoff])
    df = pd.DataFrame(dict(mean_loadings = gt_mean_loadings,
                           error = 1,
                           matched = False,
                           inferred_mean_loadings = 0))
    for i in range(len(gt_sig_inds)):
        if gt_sig_inds[i] in valid_matches:
            df.loc[i, "matched"] = True 
            df.loc[i, "error"] = error[(comp_matches.flatten() == gt_sig_inds[i]).nonzero()[0][0]][0]
            df.loc[i, "inferred_mean_loadings"] = inferred_mean_loadings[(comp_matches.flatten() == gt_sig_inds[i]).nonzero()[0][0]]
    return df


def get_matches_and_errors(inferred_sigs, inferred_mean_loadings, comp_sigs, cutoff, 
                           gt_mean_loadings, gt_sig_inds):
    sig_inds, comp_matches, error = analysis.match_signatures(
        inferred_sigs, comp_sigs, bipartite = True, oldstyle = False)
    valid_matches = np.unique(comp_matches[error < cutoff])
    df = pd.DataFrame(dict(mean_loadings = gt_mean_loadings,
                           error = float(1),
                           matched = False,
                           inferred_mean_loadings = float(0)))
    for i in range(len(gt_sig_inds)):
        if gt_sig_inds[i] in valid_matches:
            df.loc[i, "matched"] = True 
            df.loc[i, "error"] = error[(comp_matches.flatten() == gt_sig_inds[i]).nonzero()[0][0]][0]
            df.loc[i, "inferred_mean_loadings"] = inferred_mean_loadings[(comp_matches.flatten() == gt_sig_inds[i]).nonzero()[0][0]]
    return df


def save_matches_and_errors(prefix, method, comp_sigs, gt, gt_sig_inds):
    result = np.load(prefix + "_" + method + "_results.npz")
    df = get_matches_and_errors(inferred_sigs = np.transpose(result["sigs"]),
                                inferred_mean_loadings = np.mean(result["loadings"], axis = 0),
                                comp_sigs = comp_sigs, cutoff = MAX_CUTOFF,
                                gt_mean_loadings = gt["loadings"], 
                                gt_sig_inds = gt_sig_inds)
    df.to_csv(prefix + "_" + method + "_matched_errors.csv")
    return None


def save_matches_and_errors_from_csv(prefix, gt):
    result = pd.read_csv("best-seed-comparison-zeta-1.000-list.csv")
    found_sigs = result["COSMIC"].to_list()
    df = pd.DataFrame(dict(mean_loadings = gt["loadings"],
                           error = 1,
                           matched = False,
                           inferred_mean_loadings = 0))
    for i in range(len(df)):
        if gt.loc[i, "sig"] in found_sigs: 
            j = found_sigs.index(gt.loc[i, "sig"])
            if result.loc[j, "Cosine Error"] < MAX_CUTOFF:
                df.loc[i, "matched"] = True 
                df.loc[i, "error"] = result.loc[j, "Cosine Error"] 
                df.loc[i, "inferred_mean_loadings"] = int(result.loc[j, "Loadings"].split(" ")[-1].split(")")[0])
    df.to_csv(prefix + "_BPS-power-1_matched_errors.csv")
    return None


def main():

    exp_list = open("experiment_list.txt")
    base_dir = "/n/miller_lab/csxue/comparisons"

    for exp in exp_list:
        if "WGS" in exp:
            continue
            
        print("\n" + exp)
        prefix = exp.replace("\n", "")

        os.chdir(os.path.join(base_dir, prefix))

        gt = pd.read_csv(prefix + "_GT-loadings.csv", 
                         header = None, names = ["loadings", "sig"])
        gt_sig_inds = [int(s.split(" ")[1]) - 1 for s in list(gt["sig"])]
        comp_sigs, comp_sig_names = mutsig.cosmic_signatures(version = "v2")

        save_matches_and_errors(prefix, "BPS", comp_sigs, gt, gt_sig_inds)
        save_matches_and_errors(prefix, "SPE", comp_sigs, gt, gt_sig_inds)
        # if "subsample" not in prefix:
        #     save_matches_and_errors(prefix, "SA", comp_sigs, gt, gt_sig_inds)
        # if "WS" in prefix:
        #     save_matches_and_errors_from_csv(prefix, gt)

    exp_list.close()



if __name__ == '__main__':
    main()
