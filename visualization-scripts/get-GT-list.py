import os
import subprocess

import numpy as np
import pandas as pd



def main():
    
    comparisons_dir = "/n/miller_lab/csxue/comparisons"
    

    exp_list = open("experiment_list.txt")

    for exp in exp_list:
        print(exp)
        exp_name = exp.replace("\n", "")
        
        ## Bypass real data
        if "WGS" in exp_name:
            continue
        elif "lung" in exp_name: 
            subprocess.run(["cp {source} {exp_dir}/{prefix}_GT-loadings.csv".format(source = "/n/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.ready.Lung-AdenoCA/synthetic_data/synthetic-38-lung-adenoca-all-seed-1-GT-loadings.csv",
                                                                                    exp_dir = os.path.join(comparisons_dir, exp_name),
                                                                                    prefix = exp_name)],
                           shell = True)
        elif "stomach" in exp_name:
            subprocess.run(["cp {source} {exp_dir}/{prefix}_GT-loadings.csv".format(source = "/n/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Stomach-AdenoCA/synthetic_data/synthetic-75-stomach-adenoca-all-seed-1-GT-loadings.csv",
                                                                                    exp_dir = os.path.join(comparisons_dir, exp_name),
                                                                                    prefix = exp_name)],
                           shell = True)
        elif "skin" in exp_name: 
            subprocess.run(["cp {source} {exp_dir}/{prefix}_GT-loadings.csv".format(source = "/n/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Skin-Melanoma/synthetic_data/synthetic-107-skin-melanoma-all-seed-1-GT-loadings.csv",
                                                                                    exp_dir = os.path.join(comparisons_dir, exp_name),
                                                                                    prefix = exp_name)],
                           shell = True)
        elif "ovary" in exp_name: 
            subprocess.run(["cp {source} {exp_dir}/{prefix}_GT-loadings.csv".format(source = "/n/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Ovary-AdenoCA/synthetic_data/synthetic-113-ovary-adenoca-all-seed-1-GT-loadings.csv",
                                                                                    exp_dir = os.path.join(comparisons_dir, exp_name),
                                                                                    prefix = exp_name)],
                           shell = True)
        elif "breast" in exp_name: 
            subprocess.run(["cp {source} {exp_dir}/{prefix}_GT-loadings.csv".format(source = "/n/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Breast/synthetic_data/synthetic-214-breast-all-seed-1-GT-loadings.csv",
                                                                                    exp_dir = os.path.join(comparisons_dir, exp_name),
                                                                                    prefix = exp_name)],
                           shell = True)
        elif "liver" in exp_name:
            subprocess.run(["cp {source} {exp_dir}/{prefix}_GT-loadings.csv".format(source = "/n/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Liver-HCC/synthetic_data/synthetic-326-liver-hcc-all-seed-1-GT-loadings.csv",
                                                                                    exp_dir = os.path.join(comparisons_dir, exp_name),
                                                                                    prefix = exp_name)],
                           shell = True)

    exp_list.close()


    


    subsample_index_template = "/n/miller_lab/csxue/bayes-power-sig/data/synthetic-liver-subsamples/synthetic-326-liver-hcc-all-seed-1-subsample-{size}-samples.csv"
    subsample_sizes = [20, 30, 50, 80, 120, 170, 230]
    exp_name_template = "subsample-liver-{size}-replicate-{replicate}"
    sig_names = ["Signature " + str(i + 1) for i in range(30)] 

    loadings_array = np.load("/n/miller_lab/csxue/bayes-power-sig/WGS_PCAWG.96.Liver-HCC/synthetic_data/synthetic-326-liver-hcc-all-loadings.npy")
    normalized_loadings = loadings_array / np.sum(loadings_array, axis = 0, keepdims = True)
    keep = []

    for k in range(30):
        if np.sum(normalized_loadings[k] > 0.1) > 0 or np.sum(loadings_array[k]) > 0.02 * np.sum(loadings_array):
            keep.append(k)
    trimmed_loadings_array = loadings_array[keep]
    trimmed_sig_names = [sig_names[k] for k in keep]
        


    for s in subsample_sizes:
        indices = pd.read_csv(subsample_index_template.format(size = s), index_col = 0)
        for rep in range(indices.shape[0]):
            exp_name = exp_name_template.format(size = str(s), replicate = str(rep + 1))
            print(exp_name + "\n")

            samp_inds = indices.iloc[rep,:]
            subsample_loadings = trimmed_loadings_array[:,samp_inds]

            lds = np.mean(subsample_loadings, axis = 1)
            df = np.vstack((lds, trimmed_sig_names)).T
            pd.DataFrame(df).to_csv(os.path.join(comparisons_dir, exp_name, exp_name + "_GT-loadings.csv"), 
                                    header = False, index = False)





if __name__ == '__main__':
    main()
