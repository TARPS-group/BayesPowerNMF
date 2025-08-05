import os
import subprocess

import numpy as np
import pandas as pd

from mutsigtools import mutsig


def main():

    exp_list = open("experiment_list.txt")
    
    exp_dir_template = "/n/miller_lab/csxue/bayes-power-sig/{experiment_name}/"
    figs_dir_template = "figures/"
    summary_file_template = "summary.npz"
    solution_dir_template = "results/"
    
    h5_list = open("/n/miller_lab/csxue/mutsig-nmf/figures-all/comparisons/scripts/h5_list.csv", mode = "w")

    for exp in exp_list:
        print("\n" + exp)
        exp_name = exp.replace("\n", "")
        exp_dir = exp_dir_template.format(experiment_name = exp_name)
        figs_dir = os.path.join(exp_dir, figs_dir_template)

        ## Find specific experiment directory
        subfolders = [ f.path for f in os.scandir(figs_dir) if f.is_dir() ]
        if "subsample" in exp_name:
            final_figs_dir = subfolders[0]
        else: 
            original = [ "original_counts" in sf for sf in subfolders ]
            if sum(original) == 1:
                final_figs_dir = subfolders[np.where(original)[0][0]]
            elif sum(original) == 0:
                print("No original_counts figures found for " + exp_name)
                continue
            else:
                print("Multiple original_counts figures directories found for " + exp_name)
                for i in np.where(original)[0]:
                    print(subfolders[i])
                final_figs_dir = input("Which directory to use?\n")

        summary_file = os.path.join(final_figs_dir, summary_file_template)
        # print(summary_file)
        if not os.path.isfile(summary_file):
            print("Summary file for " + summary_file + " could not be found.")
            continue 
        # print(summary_file)

        ## Extract best seed from log file
        summary = np.load(summary_file) 
        if len(summary["best_seeds"]) == 1:
            seed = summary["best_seeds"][0]
        elif len(summary["best_seeds"]) == 0: 
            print("Summary file empty for " + exp_name)
            continue
        else: 
            print("Multiple powers processed for " + exp_name)
            i = input("Which power (index) to use? ")
            seed = summary["best_seeds"][int(i)]

        ## Copy other relevant files
        sig_comp_plot = subprocess.run(['ls {dir} | grep best-seed-comparison-zeta-[0123456789.]*.pdf'.format(dir = final_figs_dir)],
            shell = True, capture_output = True, text = True).stdout.split("\n")[:-1]
        sig_comp_list = subprocess.run(['ls {dir} | grep best-seed-comparison-zeta-[0123456789.]*-list.csv'.format(dir = final_figs_dir)],
            shell = True, capture_output = True, text = True).stdout.split("\n")[:-1]
        if len(sig_comp_list) == 1:
            sig_comp_plot = sig_comp_plot[0]
            sig_comp_list = sig_comp_list[0]
        else: 
            zeta = input("Figures for multiple powers found. Which power to use? ")
            zeta = float(zeta)
            sig_comp_plot = "best-seed-comparison-zeta-{:.3f}.pdf".format(zeta)
            sig_comp_list = "best-seed-comparison-zeta-{:.3f}-list.csv".format(zeta)
            print("\n")
        subprocess.run(['cp {exp}/{file} {out}/{file}'.format(exp = final_figs_dir,
            out = os.path.join("/n/miller_lab/csxue/comparisons/", exp_name), 
            file = sig_comp_plot)], 
            shell = True)
        subprocess.run(['cp {exp}/{file} {out}/{file}'.format(exp = final_figs_dir,
            out = os.path.join("/n/miller_lab/csxue/comparisons/", exp_name), 
            file = sig_comp_list)], 
            shell = True)
        str_zeta = sig_comp_list.split("zeta-")[1].split("-")[0]

        ## Convert to results file name
        results_file_root = final_figs_dir.split("/")[-1].split("-a-")[0] + "-seed-" + str(seed) + "-"
        grep_out = subprocess.run(['ls {dir} | grep "{root}" '.format(dir = os.path.join(exp_dir, solution_dir_template),
            root = results_file_root)],
            shell = True, capture_output = True, text = True).stdout.split("\n")[:-1]
        if len(grep_out) == 1:
            h5_file = grep_out[0]
        elif len(grep_out) == 0: 
            print("No results file starting with '" + results_file_root + "' found.")
            continue
        else: 
            results_match_zeta = [f for f in grep_out if str_zeta in f]
            if len(results_match_zeta) == 1:
                h5_file = results_match_zeta[0]
            else:
                print("Multiple results file options found for " + results_file_root)
                for filename in grep_out:
                    print(filename)
                h5_file = input("Which h5 file to use?\n")

        ## Save to file
        h5_list.write(exp_name + "," + h5_file + "\n")


    exp_list.close()
    h5_list.close()



if __name__ == '__main__':
    main()
