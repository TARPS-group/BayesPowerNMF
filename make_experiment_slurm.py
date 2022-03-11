#!/usr/bin/python3

import configparser 
import argparse
import os
import sys

INFER_LOADINGS_TEMPLATE = """#!/bin/bash

#SBATCH -c 4
#SBATCH --job-name {jobname} 
#SBATCH -t 0-02:00 
#SBATCH -p {queue}
#SBATCH --mem=64G 
#SBATCH -o {log_dir}/output_%j_{jobname}.out 
#SBATCH -e {log_dir}/error_%j_{jobname}.err 

module load gcc/8.2.0-fasrc01 python/3.8.5-fasrc01

eval "$(conda shell.bash hook)"
conda activate {conda_env}

DATA={data}
FILTER="{filter}"
SIGS_FILE="{sigs_file}"
SIGS_PREFIX="{sigs_prefix}"
SIGNATURES="{signatures}"
SAVE_DIR={save_dir}
SUB_TYPE={subst_type}
N={num_samples}
OPTS="{opts}"

cd {BPS_dir}
echo "python scripts/infer-loadings-nnls.py $DATA $FILTER $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR --subst-type $SUB_TYPE -n $N $OPTS"
python scripts/infer-loadings-nnls.py $DATA $FILTER $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR --subst-type $SUB_TYPE -n $N $OPTS
"""

GENERATE_SYNTHETIC_TEMPLATE = """#!/bin/bash

#SBATCH --job-name {jobname} 
#SBATCH -t 0-01:00 
#SBATCH -p {queue}
#SBATCH --mem=16G 
#SBATCH -o {log_dir}/output_%j_{jobname}.out 
#SBATCH -e {log_dir}/error_%j_{jobname}.err 

module load gcc/8.2.0-fasrc01 python/3.8.5-fasrc01

eval "$(conda shell.bash hook)"
conda activate {conda_env}

NEW_PREFIX={new_prefix}
SIGS_FILE="{sigs_file}"
SIGS_PREFIX="{sigs_prefix}"
SIGNATURES="{signatures}"
SAVE_DIR={save_dir}
S={seed}
N={num_samples}
PERTURBED="{perturbed}"
OVERDISPERSED="{overdispersed}"
CONTAMINATION="{contamination}"
OPTS="{trim}"

cd {BPS_dir}
echo "python scripts/generate-synthetic-data.py $NEW_PREFIX $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR -s $S -n $N $PERTURBED $OVERDISPERSED $CONTAMINATION $OPTS"
python scripts/generate-synthetic-data.py $NEW_PREFIX $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR -s $S -n $N $PERTURBED $OVERDISPERSED $CONTAMINATION $OPTS
"""

INFER_LOADINGS_AND_SIGS_TEMPLATE = """#!/bin/bash

#SBATCH --job-name {jobname} 
#SBATCH -t 7-00:00 
#SBATCH -p {queue}
#SBATCH --mem=64G 
#SBATCH -o {log_dir}/output_%j_{jobname}.out 
#SBATCH -e {log_dir}/error_%j_{jobname}.err  

module load gcc/8.2.0-fasrc01 python/3.8.5-fasrc01

eval "$(conda shell.bash hook)"
conda activate {conda_env}

zeta=$1
J=$2
data=$3
I=$4
K=$5
S=$6
B=$7
thin=$8
results_dir=$9
seed=$SGE_TASK_ID


cd {BPS_dir}/scripts
echo "python infer-mutsigs.py $data ${{results_dir}} -m normalized_v2 -s $S -b $B -I $I -K $K --thin $thin -e 1e-3 --zeta $zeta --max-J $J --seed $seed ${{10}}"
python infer-mutsigs.py $data ${{results_dir}} -m normalized_v2 -s $S -b $B -I $I -K $K --thin $thin -e 1e-3 --zeta $zeta --max-J $J --seed $seed ${{10}}
"""

INFER_LOADINGS_AND_SIGS_LOOP_TEMPLATE = """#!/bin/bash

cd {BPS_dir}/{exp_name}

for zeta in {powers}
do
    while read type
    do
        sbatch -l h_rt={max_time} --job-name stan-{synthetic_prefix}-zeta-$zeta-J-{n}-Kmax-{K}-S-{samps}-B-{burnin} -t {seed_start}-{seed_end} -l h_vmem=16g -j y -o {log_dir} helper/run-seeded-stan.sh $zeta {n} ../{exp_name}/synthetic_data/{synthetic_prefix}-seed-$type.tsv {I} {K} {samps} {burnin} {thin} ../{exp_name}/results "{opts}"
    done < ../{exp_name}/synthetic_data/exp_list.txt
done
"""

MAKE_PLOTS_TEMPLATE = """#!/bin/bash

#SBATCH --job-name {jobname} 
#SBATCH -t 0-06:00 
#SBATCH -p {queue}
#SBATCH --mem=64G 
#SBATCH -o {log_dir}/output_%j_{jobname}.out 
#SBATCH -e {log_dir}/error_%j_{jobname}.err 

module load gcc/8.2.0-fasrc01 python/3.8.5-fasrc01

eval "$(conda shell.bash hook)"
conda activate {conda_env}

cd {BPS_dir}
python scripts/generate-multi-zeta-results-figs.py {experiment_name}-burnin-{B}-samps-{S}-K-{K} a-{a:.2f}-J0-{J0:.1f} {base_dir} {rho_cond}{signatures_cond}--seeds {seeds} --zetas {zetas} --skip {skip} --save-dir {save_dir} --results-dir {results_dir} --counts-file {data} --subst-type {subst_type} --prob-zero {p0} --quantile1 {l1} --quantile99 {l99} {opts}
"""

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', default = "bps.ini")
    parser.add_argument('--section', default = "EXPERIMENT")
    return parser.parse_args()

def read_config(config_file, section):
    if not os.path.isfile(config_file):
        sys.exit("missing config file {}".format(config_file))
    
    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    config.read(config_file)

    if section not in config:
        sys.exit("config file {} missing section {}".format(config_file, section))
    return config

def main():
    args = parse_args()
    config = read_config(args.config_file, args.section)

    exp = config[args.section]
    exp_name = exp.get("experiment_name")

    wd = os.getcwd()

    oldmask = os.umask(000)
    os.makedirs(exp_name, exist_ok = True)
    os.makedirs(exp.get("log_dir"), exist_ok = True)
    os.makedirs(os.path.join(exp_name, "experiment_scripts"), exist_ok = True)
    # os.makedirs(os.path.join(exp_name, "experiment_scripts", "helper"), exist_ok = True)
    os.makedirs(os.path.join(exp_name, "synthetic_data"), exist_ok = True)
    os.makedirs(os.path.join(exp_name, "results"), exist_ok = True)
    os.makedirs(os.path.join(exp_name, "figures"), exist_ok = True)
    os.umask(oldmask)

    ## Stage I 
    stage_I_content = INFER_LOADINGS_TEMPLATE.format(
        jobname = "infer_loadings_initial_" + exp_name,
        queue = exp.get("queue"),
        log_dir = os.path.join(wd, exp.get("log_dir")),
        conda_env = exp.get("conda_env"),
        BPS_dir = wd,
        data = exp.get("data"),
        filter = exp.get("sample_prefixes"),
        sigs_file = "" if exp.get("signatures_file") == "" else "--signatures-file {}".format(exp.get("signatures_file")),
        sigs_prefix = exp.get("signatures_prefix"),
        signatures = exp.get("putative_sigs"),
        save_dir = os.path.join(exp_name, "synthetic_data"),
        subst_type = exp.get("subst_type"),
        num_samples = exp.get("num_samples"),
        a = exp.getfloat("a_init"),
        zeta = exp.get("loadings_inference_power"),
        p0 = ("" if exp.get("p_sigs_zero_init") == "" else "--prob-zero {}".format(exp.get("p_sigs_zero_init"))),
        q1 = ("" if exp.get("loadings_quantile_1_init") == "" else "--q1 {}".format(exp.get("loadings_quantile_1_init"))),
        q99 = ("" if exp.get("loadings_quantile_99_init") == "" else "--q99 {}".format(exp.get("loadings_quantile_99_init"))),
        opts = ("" if exp.getboolean("sparse_init") is False else "--sparse ") + ("" if exp.getboolean("median") is False else "--median ") + ("" if exp.getboolean("MAP") is False else "--MAP ") + ("" if exp.get("iters") == "" else "--iters {} ".format(exp.get("iters")))
    )

    with open(os.path.join(exp_name, "experiment_scripts", "stage_I.sh"), "w+") as f:
        f.writelines(stage_I_content)

    synthetic_prefix = "synthetic-{}-{}-{}".format(
        exp.get("num_samples"), 
        exp.get("sample_prefixes"), 
        "-".join(exp.get("putative_sigs").split())
    ).lower()
    if exp.getfloat("a_init") != 0:
        synthetic_prefix += '-a-{:.2f}'.format(float(exp.get("a_init")))
    if exp.getfloat("loadings_inference_power") != 1:
        base_description += '-zeta-{:.1f}'.format(float(exp.get("loadings_inference_power")))
    if exp.getboolean("median") is True:
        synthetic_prefix += '-median'

    ## Stage II
    seed = exp.get("synthetic_data_seed")

    stage_II_content = GENERATE_SYNTHETIC_TEMPLATE.format(
        jobname = "generate_synthetic_data_" + exp_name,
        queue = exp.get("queue"),
        log_dir = os.path.join(wd, exp.get("log_dir")),
        conda_env = exp.get("conda_env"),
        BPS_dir = wd,
        new_prefix = synthetic_prefix,
        sigs_file = "" if exp.get("signatures_file") == "" else "--signatures-file {}".format(exp.get("signatures_file")),
        sigs_prefix = exp.get("signatures_prefix"),
        signatures = exp.get("putative_sigs"),
        save_dir = os.path.join(exp_name, "synthetic_data"),
        seed = seed,
        num_samples = exp.get("num_samples"),
        perturbed = "" if exp.get("perturbed") == "" else "--perturbed {}".format(exp.get("perturbed")),
        overdispersed = "" if exp.get("overdispersed") == "" else "--overdispersed {}".format(exp.get("overdispersed")),
        contamination = "" if exp.get("contamination") == "" else "--contamination {}".format(exp.get("contamination")),
        trim = "" if (exp.getboolean("sparse_init") or exp.getboolean("trim_sigs")) else "--trim" # trim if sparse or if desired
    )

    with open(os.path.join(exp_name, "experiment_scripts", "stage_II.sh"), "w+") as f:
        f.writelines(stage_II_content)

    synthetic_experiments = [seed] + ["{}-overdispersed-{}".format(seed, p) for p in map(float, exp.get("overdispersed").split())] + ["{}-contamination-{}".format(seed, p) for p in exp.get("contamination").split()] + ["{}-perturbed-{}".format(seed, p) for p in exp.get("perturbed").split()]
    synthetic_data_files = ["{}-seed-{}.tsv".format(synthetic_prefix, se) for se in synthetic_experiments]

    ### Stage IIIa
    # infer_sigs = exp.getboolean("inferring_signatures")

    # if infer_sigs is True:
    #     helper = INFER_LOADINGS_AND_SIGS.format(
    #         log_dir = os.path.join(wd, exp.get("log_dir")),
    #         virtual_env = exp.get("virtual_env"),
    #         BPS_dir = wd
    #     )

    #     with open(os.path.join(exp_name, "experiment_scripts", "helper", "run-seeded-stan.sh"), "w+") as f:
    #         f.writelines(helper)

    #     stage_IIIa_content = INFER_LOADINGS_AND_SIGS_LOOP_TEMPLATE.format(
    #         powers = exp.get("testing_powers"),
    #         exp_list = " ".join(synthetic_experiments),
    #         BPS_dir = wd,
    #         log_dir = os.path.join(wd, exp.get("log_dir")),
    #         exp_name = exp_name,
    #         seed_start = exp.get("seed_start"),
    #         seed_end = exp.get("seed_end"),
    #         I = 96 if exp.get("subst_type") == "SBS" else (78 if exp.get("subst_type") == "DBS" else 83),
    #         n = exp.get("num_samples"),
    #         K = exp.get("K"),
    #         synthetic_prefix = synthetic_prefix,
    #         samps = exp.get("samples"),
    #         burnin = exp.get("burnin"),
    #         thin = exp.get("thin"),
    #         max_time = exp.get("max_time"),
    #         opts = ("--no-rho " if exp.get("rho_new") == "" else "") + "-a " + exp.get("a_new") + " --J0 " + exp.get("J0")
    #     )

    #     with open(os.path.join(exp_name, "experiment_scripts", "stage_IIIa.sh"), "w+") as f:
    #         f.writelines(stage_IIIa_content)
    # else:
    #     # fill in infer loadings again
    #     pass

    # # ## Stage IIIb
    # if infer_sigs is True:
    #     ### Checkpoint

    #     ### Scripts
    #     for sexp, sdata_path in zip(synthetic_experiments, synthetic_data_files):
    #         stage_IIIb_content = MAKE_PLOTS_TEMPLATE.format(
    #             jobname = "generate_plots_{}".format(sexp),
    #             log_dir = os.path.join(wd, exp.get("log_dir")),
    #             virtual_env = exp.get("virtual_env"),
    #             BPS_dir = os.path.join(wd),
    #             experiment_name = synthetic_prefix,
    #             B = exp.get("burnin"),
    #             S = exp.get("samples"),
    #             K = exp.get("K"),
    #             a = exp.getfloat("a_new"),
    #             J0 = exp.getint("J0"),
    #             base_dir = wd,
    #             rho_cond = "" if exp.get("rho_new") == "" else "--samp-info no-rho- ",
    #             signatures_cond = "" if exp.get("signatures_file") == "" else "--signatures-file {} ".format(exp.get("signatures_file")),
    #             seeds = " ".join([str(s) for s in range(int(exp.get("seed_start")), int(exp.get("seed_end")) + 1)]),
    #             zetas = exp.get("testing_powers"),
    #             skip = exp.get("skip"),
    #             save_dir = os.path.join(wd, exp_name, "figures"),
    #             results_dir = os.path.join(wd, exp_name, "results"),
    #             data = sdata_path,
    #             subst_type = exp.get("subst_type"),
    #             opts = "--ignore-summary"
    #         )

    #         with open(os.path.join(exp_name, "experiment_scripts", "helper", "stage_IIIb_{}.sh".format(sexp)), "w+") as f:
    #             f.writelines(stage_IIIb_content)

    #     with open(os.path.join(exp_name, "experiment_scripts", "stage_IIIb.sh".format(sexp)), "w+") as f:
    #         f.writelines(["#!/bin/bash\n\n"] + ["qsub helper/stage_IIIb_{}.sh\n".format(sexp) for sexp in synthetic_experiments])

    # ## Stage IIIc

    # ## Stage Va

    # ## Stage Vb
    # ### Script
    # stage_Vb_content = MAKE_PLOTS_TEMPLATE.format(
    #     log_dir = os.path.join(wd, exp.get("log_dir")),
    #     virtual_env = exp.get("virtual_env"),
    #     BPS_dir = os.path.join(wd),
    #     experiment_name = exp_name,
    #     B = exp.get("burnin"),
    #     S = exp.get("samples"),
    #     K = exp.get("K"),
    #     a = float(exp.get("a_new")),
    #     J0 = int(exp.get("J0")),
    #     base_dir = wd,
    #     rho_cond = "" if exp.get("rho_new") is None else "--samp-info no-rho- ",
    #     signatures_cond = "" if exp.get("signatures_file") == "" else "--signatures-file {} ".format(exp.get("signatures_file")),
    #     seeds = " ".join([str(s) for s in range(int(exp.get("seed_start")), int(exp.get("seed_end")) + 1)]),
    #     zetas = "$1",
    #     skip = exp.get("skip"),
    #     save_dir = os.path.join(wd, exp_name, "figures"),
    #     results_dir = os.path.join(wd, exp_name, "results"),
    #     data = os.path.join(wd, exp.get("data")),
    #     subst_type = exp.get("subst_type")
    # )

    # with open(os.path.join(exp_name, "experiment_scripts", "stage_Vb.sh"), "w+") as f:
    #     f.writelines(stage_Vb_content)

if __name__ == '__main__':
    main()
