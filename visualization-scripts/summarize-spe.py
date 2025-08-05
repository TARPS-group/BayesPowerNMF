import os
import subprocess

import numpy as np
import pandas as pd

from mutsigtools import mutsig


def main():

    exp_list = open("experiment_list.txt")
    # exp_list = open("experiment_list_main.txt")
    # exp_list = open("experiment_list_liver_subsampling.txt")
    
    exp_dir_template = "/n/miller_lab/csxue/sigprofiler_outputs/{experiment_name}_output/"
    log_file_template = "figures/K_comparison.txt"
    solution_dir_template = "SBS96/All_Solutions/SBS96_{K}_Signatures/"
    sigs_file_template = "Signatures/SBS96_S{K}_Signatures.txt"
    loadings_file_template = "Activities/SBS96_S{K}_NMF_Activities.txt"
    sigs_comparison_file_template = "comparison_{K}.pdf"
    sigs_list_file_template = "comparison_{K}-list.csv"
    
    output_directory_template = "/n/miller_lab/csxue/mutsig-nmf/figures-all/comparisons/{experiment_name}/"
    output_file_template = "{experiment_name}_SPE_results.npz"

    error_list = open("/n/miller_lab/csxue/mutsig-nmf/figures-all/comparisons/scripts/sigprofiler_no_valid_solutions_list.txt", 
        mode = "w")

    for exp in exp_list:
        print(exp)
        
        ## Reconcile experiment names
        bps_exp_name = exp.replace("\n", "")
        spe_exp_name = ""
        if "WGS" in bps_exp_name:
            spe_exp_name = bps_exp_name
        elif "subsample" in bps_exp_name:
            size = bps_exp_name.split("-")[2]
            rep = bps_exp_name.split("-")[4]
            spe_exp_name = "synthetic-326-liver-hcc-all-seed-1-subsample-{size}-replicate-{rep}".format(size = size, rep = rep)
        else:
            name = bps_exp_name.split("-", 1)
            if name[0] == "lung": 
                spe_exp_name = "synthetic-38-lung-adenoca-all-seed-1"
            elif name[0] == "stomach":
                spe_exp_name = "synthetic-75-stomach-adenoca-all-seed-1"
            elif name[0] == "skin":
                spe_exp_name = "synthetic-107-skin-melanoma-all-seed-1"
            elif name[0] == "ovary":
                spe_exp_name = "synthetic-113-ovary-adenoca-all-seed-1"
            elif name[0] == "breast":
                spe_exp_name = "synthetic-214-breast-all-seed-1"
            elif name[0] == "liver":
                spe_exp_name = "synthetic-326-liver-hcc-all-seed-1"
            if name[1] != "WS":
                spe_exp_name = spe_exp_name + "-" + name[1]

        exp_dir = exp_dir_template.format(experiment_name = spe_exp_name)
        if not os.path.exists(exp_dir):
            print(spe_exp_name + "is not a valid SPE experiment name.")
            continue 

        log_file = os.path.join(exp_dir, log_file_template)
        # print(log_file)
        if not os.path.isfile(log_file):
            print("Log file for " + spe_exp_name + " could not be found.")
            continue 

        ## Extract K from log file
        grep_out = subprocess.run(['grep "Optimal K under SigProfilerExtractor heuristic with paired test: " ' + log_file], 
            shell = True, capture_output = True, text = True).stdout
        if grep_out == "":  # no valid solution under SigProfiler heuristic
            grep_out = subprocess.run(['grep "Optimal K under our heuristic: " ' + log_file], 
                shell = True, capture_output = True, text = True).stdout
            error_list.write(exp)  # write to error file, with newline
        K = grep_out.replace("\n", "").split(" ")[-1] 

        ## Open loadings
        loadings_file = os.path.join(exp_dir, solution_dir_template.format(K = K), loadings_file_template.format(K = K))
        loadings = pd.read_csv(loadings_file, delimiter = "\t", header = 0, index_col = 0)

        ## Open signatures
        sigs_file = os.path.join(exp_dir, solution_dir_template.format(K = K), sigs_file_template.format(K = K))
        sigs = pd.read_csv(sigs_file, delimiter = "\t", header = 0, index_col = 0).reindex(mutsig.substitution_names())

        ## Save to file
        output_dir = output_directory_template.format(experiment_name = bps_exp_name)
        output_file = os.path.join(output_dir, output_file_template.format(experiment_name = bps_exp_name))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        np.savez(output_file, loadings = loadings.values, sigs = sigs.values)

        ## Copy other relevant files
        subprocess.run(['cp {exp}/figures/{file} {out}/{file}'.format(exp = exp_dir,
            out = output_dir, 
            file = sigs_comparison_file_template.format(K = K))], 
            shell = True)
        subprocess.run(['cp {exp}/figures/{file} {out}/{file}'.format(exp = exp_dir,
            out = output_dir, 
            file = sigs_list_file_template.format(K = K))], 
            shell = True)



    exp_list.close()
    error_list.close()



if __name__ == '__main__':
    main()
