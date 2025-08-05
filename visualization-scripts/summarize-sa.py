import os
import subprocess

import numpy as np

from rpy2.robjects import r


def extract_result(rep, results_dir):
    filename = 'L1W.L2H.96.{}.RData'.format(rep)
    filepath = os.path.join(results_dir, filename)
    r['load'](filepath)
    res = r['res']
    mutsigs = np.array(res[0]).T  ## 96 x K
    loadings = np.array(res[1])  ## K x N
    mass = np.sum(mutsigs, axis = 1) * np.sum(loadings, axis = 1) / loadings.shape[1]
    sorted_inds = np.argsort(mass)[::-1]
    n_significant_components = np.sum(mass > 1)
    significant_inds = sorted_inds[:n_significant_components]
    mutsigs = mutsigs[significant_inds]
    loadings = (loadings[significant_inds].T * np.sum(mutsigs, axis = 1)).T
    mutsigs /= np.sum(mutsigs, axis=0, keepdims=True)
    return (rep, -np.array(res[3])[0], np.transpose(mutsigs), mass[significant_inds], np.transpose(loadings))


def main():

    # exp_list = open("experiment_list.txt")
    exp_list = open("experiment_list_main.txt")
    # exp_list = open("experiment_list_liver_subsampling.txt")
    
    results_dir_template = "/n/miller_lab/csxue/SignatureAnalyzer/OUTPUT_{experiment_name}/"
    n_reps = 10
    
    output_directory_template = "/n/miller_lab/csxue/mutsig-nmf/figures-all/comparisons/{experiment_name}/"
    output_file_template = "{experiment_name}_SA_results.npz"

    for exp in exp_list:
        print(exp)
        
        ## Reconcile experiment names
        bps_exp_name = exp.replace("\n", "")
        sa_exp_name = ""
        if "WGS" in bps_exp_name:
            if "lung" in bps_exp_name:
                sa_exp_name = "Lung-AdenoCA"
            elif "stomach" in bps_exp_name:
                sa_exp_name = "Stomach-AdenoCA"
            elif "skin" in bps_exp_name:
                sa_exp_name = "Skin-Melanoma"
            elif "ovary" in bps_exp_name:
                sa_exp_name = "Ovary-AdenoCA"
            elif "breast" in bps_exp_name:
                sa_exp_name = "Breast"
            else:
                sa_exp_name = "Liver-HCC"
            sa_exp_name = sa_exp_name + "_original_counts"
        elif "subsample" in bps_exp_name:
            size = bps_exp_name.split("-")[2]
            rep = bps_exp_name.split("-")[4]
            sa_exp_name = "synthetic-326-liver-hcc-all-seed-1-subsample-{size}-replicate-{rep}".format(size = size, rep = rep)
        else:
            name = bps_exp_name.split("-", 1)
            if name[0] == "lung": 
                sa_exp_name = "synthetic-38-lung-adenoca-all-seed-1"
            elif name[0] == "stomach":
                sa_exp_name = "synthetic-75-stomach-adenoca-all-seed-1"
            elif name[0] == "skin":
                sa_exp_name = "synthetic-107-skin-melanoma-all-seed-1"
            elif name[0] == "ovary":
                sa_exp_name = "synthetic-113-ovary-adenoca-all-seed-1"
            elif name[0] == "breast":
                sa_exp_name = "synthetic-214-breast-all-seed-1"
            elif name[0] == "liver":
                sa_exp_name = "synthetic-326-liver-hcc-all-seed-1"
            if name[1] != "WS":
                sa_exp_name = sa_exp_name + "-" + name[1]

        results_dir = results_dir_template.format(experiment_name = sa_exp_name)
        if not os.path.exists(results_dir):
            print(sa_exp_name + "is not a valid SignatureAnalyzer experiment name.")
            continue 


        ## Identify best replicate
        best_res = (0, -np.inf,)
        for rep in range(n_reps):
            res = extract_result(rep + 1, results_dir)
            # print(res[1])
            if res[1] > best_res[1]:
                best_res = res
        best_rep, best_ll, best_sigs, best_mass, best_loadings = best_res


        ## Save to file
        output_dir = output_directory_template.format(experiment_name = bps_exp_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, output_file_template.format(experiment_name = bps_exp_name))
        np.savez(output_file, loadings = best_loadings, sigs = best_sigs)

        ## Copy other relevant files
        subprocess.run(['cp {exp}/best-mutsigs-comparison.pdf {out}/SA_best-mutsigs-comparison.pdf'.format(exp = results_dir,
            out = output_dir)], 
            shell = True)
        subprocess.run(['cp {exp}/best-mutsigs-comparison-list.csv {out}/SA_best-mutsigs-comparison-list.csv'.format(exp = results_dir,
            out = output_dir)], 
            shell = True)



    exp_list.close()




if __name__ == '__main__':
    main()
