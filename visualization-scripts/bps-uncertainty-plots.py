import os
import subprocess

import numpy as np
import pandas as pd
import statsmodels.api as sm

import matplotlib
if 'DISPLAY' not in os.environ:
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import seaborn as sns

from mutsigtools import analysis, mutsig


MAX_CUTOFF = 1 ## cosine error
CUTOFF = 1 ## filtering inferred sigs


def compile_bps_uncertainty_and_errors():
    base_dir = "/n/miller_lab/csxue/comparisons"
    bps_dir = "/n/miller_lab/csxue/bayes-power-sig"
    out_dir = os.path.join(base_dir, "synthetic-all") 
    exp_list = open(os.path.join(base_dir, "scripts/experiment_list_main.txt"))

    comp_sigs, comp_sig_names = mutsig.cosmic_signatures(version = "v2")
    comp_sig_flatness = np.array([ 1 / (96 * np.linalg.norm(sig) ** 2) for sig in comp_sigs ])

    flatness = []
    recovery_error = []
    quantile = []
    uncertainty = []

    skip = 25

    for exp in exp_list:
        if "WGS" in exp:
            continue
            
        print("\n" + exp)
        prefix = exp.replace("\n", "")

        os.chdir(os.path.join(base_dir, prefix))

        ## Read best-seed-comparison-zeta-[]-list.csv 
        matches_list = subprocess.run(['ls | grep best-seed-comparison-zeta-0.[0123456789]*-list.csv'],
            shell = True, capture_output = True, text = True).stdout.split("\n")[0]
        matches = pd.read_csv(matches_list)

        ## Open h5 file
        h5_file_name = subprocess.run(['cat ../scripts/h5_list.csv | grep {}'.format(prefix)],
            shell = True, capture_output = True, text = True).stdout.split("\n")[0].split(",")[1]
        h5_file_name = os.path.join(bps_dir, prefix, "results", h5_file_name)
        msi = analysis.load_samples_h5_file(h5_file_name, verbose = False,
                name_prefix = "Signature", cutoff = CUTOFF, sample_start = 0)[0]
        samples = msi.mutsigs_samples
        mean_sigs = msi.mean_mutsigs

        uncertainty.extend([ np.mean([ analysis.cosine_dissimilarity(samples[i,:,k], mean_sigs[i,:]) for k in range(0, samples.shape[2], skip) ]) for i in range(samples.shape[0]) ])
        quantile.extend([ ([ analysis.cosine_dissimilarity(samples[i,:,k], mean_sigs[i,:]) for k in range(0, samples.shape[2], skip) ] < matches["Cosine Error"][i]).mean() for i in range(samples.shape[0]) ])
        recovery_error.extend(list(matches["Cosine Error"]))

        flatness.extend([ comp_sig_flatness[np.where(comp_sig_names == sig)[0][0]] for sig in matches["COSMIC"]])

    exp_list.close()

    dct = {"Uncertainty": uncertainty, "Recovery Error": recovery_error, "Quantile": quantile, "Flatness": flatness}
    df = pd.DataFrame(dct)
    df.to_csv(os.path.join(out_dir, "bps_uncertainty_error_main.csv"))
    return None


def compile_errors():
    base_dir = "/n/miller_lab/csxue/comparisons"
    out_dir = os.path.join(base_dir, "synthetic-all") 
    exp_list = open(os.path.join(base_dir, "scripts/experiment_list_main.txt"))

    spe = pd.DataFrame()
    bps = pd.DataFrame()

    for exp in exp_list:
        if "WGS" in exp:
            continue
            
        print("\n" + exp)
        exp_name = exp.replace("\n", "")

        if spe.empty:
            spe = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_SPE_matched_errors-1.csv"), index_col = 0)
            spe["experiment"] = exp_name
        else:
            df = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_SPE_matched_errors-1.csv"), index_col = 0)
            df["experiment"] = exp_name
            spe = pd.concat([spe, df]) 
        
        if bps.empty:
            bps = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_BPS_matched_errors-1.csv"), index_col = 0)
            bps["experiment"] = exp_name
        else:
            df = pd.read_csv(os.path.join(base_dir, exp_name, exp_name + "_BPS_matched_errors-1.csv"), index_col = 0)
            df["experiment"] = exp_name
            bps = pd.concat([bps, df])

    exp_list.close()

    return bps, spe


def main():
    sns.set_style('white')
    sns.set_context('notebook', font_scale = 1.5, rc = {'lines.linewidth': 2})
    matplotlib.rcParams['legend.frameon'] = False

    base_dir = "/n/miller_lab/csxue/comparisons"
    out_dir = os.path.join(base_dir, "synthetic-all") 


    ## uncertainty vs recovery error in BayesPowerNMF
    if not os.path.isfile(os.path.join(out_dir, "bps_uncertainty_error_main.csv")): 
        compile_bps_uncertainty_and_errors()

    df = pd.read_csv(os.path.join(out_dir, "bps_uncertainty_error_main.csv"), index_col = 0)
    # model = sm.OLS(df["Recovery Error"], df["Uncertainty"])
    # results = model.fit()
    # m = results.params
    # b = 0

    model = sm.OLS(df["Recovery Error"], sm.add_constant(df["Uncertainty"]))
    results = model.fit()
    b, m = results.params

    plt.figure()
    plt.scatter(x = df["Uncertainty"], y = df["Recovery Error"], alpha = 0.3)
    plt.axline(xy1 = (0, b), slope = m, color = "C1", linestyle = "--")
    plt.text(0.08, 0, f"$R^2 = {results.rsquared:.3f}$", fontsize = 20)
    plt.xlabel("Mean Uncertainty in Posterior Samples (cosine)")
    plt.ylabel("Recovery Error (cosine)")
    plt.title("Uncertainty vs Recovery Error in BayesPowerNMF")
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "bps-uncertainty-error.pdf"), bbox_inches = "tight")
    plt.close()


    ## uncertainty in BayesPowerNMF vs SigProfilerExtractor
    bps, spe = compile_errors()
    plt.figure()
    plt.scatter(x = bps["error"], y = spe["error"], alpha = 0.4)
    plt.axline(xy1 = (0, 0), slope = 1, color = "0.75", linestyle = "--")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("BayesPowerNMF recovery error (cosine)")
    plt.ylabel("SigProfilerExtractor\nrecovery error (cosine)")
    plt.title("Recovery Error in BayesPowerNMF\nvs SigProfilerExtractor")
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "spe-bps-error-scatter.pdf"), bbox_inches = "tight")
    plt.close()    


if __name__ == '__main__':
    main()
