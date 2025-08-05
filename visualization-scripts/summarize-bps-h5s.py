import os
import numpy as np
from mutsigtools import analysis

CUTOFF = 1



def main():

    bps_dir = "/n/miller_lab/csxue/bayes-power-sig"
    comparisons_dir = "/n/miller_lab/csxue/mutsig-nmf/figures-all/comparisons"
    output_file_template = "{exp}_BPS_results.npz"

    h5_list = open("h5_list.csv")

    for line in h5_list:
        exp_name, h5_file_name = line.replace("\n", "").split(",")

        print(exp_name + "\n")

        h5_file_path = os.path.join(bps_dir, exp_name, "results", h5_file_name)
        output_file = os.path.join(comparisons_dir, exp_name, output_file_template.format(exp = exp_name))

        ## open h5 file
        msi = analysis.load_samples_h5_file(h5_file_path, verbose = False,
                name_prefix = "Signature", cutoff = CUTOFF, sample_start = 0)[0]
        loadings = np.transpose(msi.mean_loadings)
        sigs = np.transpose(msi.mean_mutsigs)

        ## save output
        np.savez(output_file, loadings = loadings, sigs = sigs)

    h5_list.close()


if __name__ == '__main__':
    main()
