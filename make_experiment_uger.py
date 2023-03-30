#!/usr/bin/python3

import configparser 
import argparse
import os
import sys

INFER_LOADINGS_TEMPLATE = """#!/bin/bash

#$ -N {jobname}
#$ -j y
#$ -o {log_dir}

#$ -l h_vmem=32G
#$ -l h_rt=01:00:00
#$ -l os=RedHat7

source /broad/software/scripts/useuse

reuse .python-3.6.0
reuse GCC-5.2
source {virtual_env}/bin/activate

DATA={data}
FILTER="{filter}"
SIGS_FILE="{sigs_file}"
SIGS_PREFIX="{sigs_prefix}"
SIGNATURES="{signatures}"
SAVE_DIR={save_dir}
SUB_TYPE={subst_type}
N={num_samples}
OPTS="{plain}{cosmic}"

cd {BPS_dir}
echo "python scripts/infer-loadings-nnls.py $DATA $FILTER $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR --subst-type $SUB_TYPE -n $N $OPTS"
python scripts/infer-loadings-nnls.py $DATA $FILTER $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR --subst-type $SUB_TYPE -n $N $OPTS
"""

GENERATE_SYNTHETIC_TEMPLATE = """#!/bin/bash

#$ -N {jobname}
#$ -j y
#$ -o {log_dir}

#$ -l h_vmem=32G
#$ -l h_rt=00:15:00
#$ -l os=RedHat7

source /broad/software/scripts/useuse

reuse .python-3.6.0
source {virtual_env}/bin/activate

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
OPTS="{trim}{cosmic}"

cd {BPS_dir}
echo "python scripts/generate-synthetic-data.py $NEW_PREFIX $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR -s $S -n $N $PERTURBED $OVERDISPERSED $CONTAMINATION $OPTS"
python scripts/generate-synthetic-data.py $NEW_PREFIX $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES --save-dir $SAVE_DIR -s $S -n $N $PERTURBED $OVERDISPERSED $CONTAMINATION $OPTS
"""

INFER_LOADINGS_AND_SIGS_TEMPLATE = """#!/bin/bash

#$ -N {jobname}
#$ -j y
#$ -o {log_dir}

#$ -l h_vmem=64G
#$ -l h_rt={max_time}
#$ -l os=RedHat7

source /broad/software/scripts/useuse

reuse .python-3.6.0
reuse GCC-5.2
source {virtual_env}/bin/activate

ZETA=$1
DATA="{exp_name}/synthetic_data/${{2}}"
MODEL={model}
I={I}
J={n}
K={K}
SAMPLES={samps}
BURNIN={burnin}
THIN={thin}
RESULTS_DIR={exp_name}/results
SEED=$SGE_TASK_ID
OPTS="{opts}"


cd {BPS_dir}
echo "python scripts/infer-mutsigs.py $DATA $RESULTS_DIR -m $MODEL -s $SAMPLES -b $BURNIN -I $I -K $K --thin $THIN -e 1e-3 --zeta $ZETA --max-J $J --seed $SEED $OPTS"
python scripts/infer-mutsigs.py $DATA $RESULTS_DIR -m $MODEL -s $SAMPLES -b $BURNIN -I $I -K $K --thin $THIN -e 1e-3 --zeta $ZETA --max-J $J --seed $SEED $OPTS
""" 

INFER_LOADINGS_AND_SIGS_LOOP_TEMPLATE = """#!/bin/bash

#$ -N {jobname}
#$ -j y
#$ -o {log_dir}

#$ -l h_vmem=8G
#$ -l h_rt=00:20:00
#$ -l os=RedHat7

source /broad/software/scripts/useuse

reuse .python-3.6.0
reuse UGER
source {virtual_env}/bin/activate

ZETAS="{zetas}"
PREFIX={synthetic_prefix}
TEMPLATE="{prefix}{{exp}}-{model}-burnin-{burnin}-samps-{samps}-K-{K}-seed-{{seed}}-a-{a:.2f}-J0-{J0:.1f}-zeta-{{zeta:.3f}}-{opts}samples.h5"
EXPS="{exp_list}"
EXP_DIR="{exp_name}"
SEEDS="{seeds}"


cd {BPS_dir}
echo "python scripts/submit-nmf-jobs.py $PREFIX $EXP_DIR $TEMPLATE --seeds $SEEDS --zetas $ZETAS --exp-list $EXPS"
python scripts/submit-nmf-jobs.py $PREFIX $EXP_DIR $TEMPLATE --seeds $SEEDS --zetas $ZETAS --exp-list $EXPS
"""

MAKE_PLOTS_LOOP_TEMPLATE = """#!/bin/bash

#$ -N {jobname}
#$ -j y
#$ -o {log_dir}

#$ -l h_vmem=8G
#$ -l h_rt=00:05:00
#$ -l os=RedHat7

source /broad/software/scripts/useuse

reuse .python-3.6.0
reuse UGER
source {virtual_env}/bin/activate

ZETA={final_zeta}

cd {BPS_dir}
for EXP in {exp_list}
do
    echo "qsub -N generate_plots_{exp_name}_${{EXP}} {exp_name}/experiment_scripts/run_viz_{stage}.sh $EXP $ZETA"
    qsub -N generate_plots_{exp_name}_${{EXP}} {exp_name}/experiment_scripts/run_viz_{stage}.sh $EXP $ZETA
done
"""


MAKE_PLOTS_TEMPLATE = """#!/bin/bash

#$ -j y
#$ -o {log_dir}

#$ -l h_vmem=32G
#$ -l h_rt=06:00:00
#$ -l os=RedHat7


source /broad/software/scripts/useuse

reuse .python-3.6.0
source {virtual_env}/bin/activate

EXP=$1
SYNTHETIC_PREFIX="{synthetic_prefix}"
PREFIX={model}-burnin-{B}-samps-{S}-K-{K}
MID=a-{a:.2f}-J0-{J0:.1f}
EXP_DIR={exp_dir}
SEEDS="{seeds}"
ZETAS="{zetas}"
SKIP={skip}
SAVE_DIR=figures/
RESULTS_DIR=results/
DATA=synthetic_data/${{SYNTHETIC_PREFIX}}${{EXP}}.tsv
SUBST_TYPE="{subst_type}"
SIGS_FILE="{sigs_file}"
SIGS_PREFIX="{sigs_prefix}"
SIGNATURES="{signatures}"
OPTS="{opts}{cosmic}"


cd {BPS_dir}

echo "python scripts/generate-multi-zeta-results-figs.py ${{SYNTHETIC_PREFIX}}${{EXP}}-$PREFIX $MID $EXP_DIR --seeds $SEEDS --zetas $ZETAS --skip $SKIP --save-dir $SAVE_DIR --results-dir $RESULTS_DIR --counts-file $DATA --subst-type $SUBST_TYPE $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES $OPTS"
python scripts/generate-multi-zeta-results-figs.py ${{SYNTHETIC_PREFIX}}${{EXP}}-$PREFIX $MID $EXP_DIR --seeds $SEEDS --zetas $ZETAS --skip $SKIP --save-dir $SAVE_DIR --results-dir $RESULTS_DIR --counts-file $DATA --subst-type $SUBST_TYPE $SIGS_FILE --signatures-prefix $SIGS_PREFIX --signatures $SIGNATURES $OPTS
"""


PLOT_COMPARISON_TEMPLATE = """#!/bin/bash

#$ -N {jobname}
#$ -j y
#$ -o {log_dir}

#$ -l h_vmem=16G
#$ -l h_rt=00:05:00
#$ -l os=RedHat7


source /broad/software/scripts/useuse

reuse R-4.1

EXP_DIR={exp_dir}
SYNTHETIC_PREFIX="{synthetic_prefix}"
SYNTHETIC_SUFFIX="-{model}-burnin-{B}-samps-{S}-K-{K}-a-{a:.2f}-J0-{J0:.1f}-multi-zeta"
ZETAS="{zetas}"


cd {BPS_dir}
echo "Rscript scripts/plot_COSMIC_grid.R $EXP_DIR $SYNTHETIC_PREFIX $SYNTHETIC_SUFFIX '$ZETAS'"
Rscript scripts/plot_COSMIC_grid.R $EXP_DIR $SYNTHETIC_PREFIX $SYNTHETIC_SUFFIX "$ZETAS"
"""


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', default = "bps.ini")
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

    wd = exp.get("base_dir")

    oldmask = os.umask(000)
    os.makedirs(exp_name, exist_ok = True)
    os.makedirs(os.path.join(exp_name, "logs"), exist_ok = True)
    os.makedirs(os.path.join(exp_name, "experiment_scripts"), exist_ok = True)
    os.makedirs(os.path.join(exp_name, "synthetic_data"), exist_ok = True)
    os.makedirs(os.path.join(exp_name, "results"), exist_ok = True)
    os.makedirs(os.path.join(exp_name, "figures"), exist_ok = True)
    os.umask(oldmask)

    ## Stage I 
    stage_1_content = INFER_LOADINGS_TEMPLATE.format(
        jobname = "infer_loadings_initial_" + exp_name,
        log_dir = os.path.join(wd, exp_name, "logs"),
        virtual_env = exp.get("virtual_env"),
        BPS_dir = wd,
        data = exp.get("data"),
        filter = exp.get("sample_prefixes"),
        sigs_file = "" if exp.get("signatures_file") == "" else "--signatures-file {}".format(exp.get("signatures_file")),
        sigs_prefix = exp.get("signatures_prefix"),
        signatures = exp.get("putative_sigs"),
        save_dir = os.path.join(exp_name, "synthetic_data"),
        subst_type = exp.get("subst_type"),
        num_samples = exp.get("num_samples"),
        plain = "" if exp.getboolean("plain") is False else "--plain ",
        cosmic = ("" if exp.get("cosmic_version_internal") == "" else "--cosmic-version {}".format(exp.get("cosmic_version_internal")))  
    )

    with open(os.path.join(exp_name, "experiment_scripts", "stage_1.sh"), "w+") as f:
        f.writelines(stage_1_content)

    sigs_index_string = "all" if exp.get("putative_sigs") == "" else "-".join(exp.get("putative_sigs").split())

    synthetic_prefix = "synthetic-{}-{}-{}".format(
        exp.get("num_samples"), 
        exp.get("sample_prefixes"), 
        sigs_index_string
    ).lower()

    ## Stage II
    seed = exp.get("synthetic_data_seed")

    stage_2_content = GENERATE_SYNTHETIC_TEMPLATE.format(
        jobname = "generate_synthetic_data_" + exp_name,
        log_dir = os.path.join(wd, exp_name, "logs"),
        virtual_env = exp.get("virtual_env"),
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
        trim = "--trim " if exp.getboolean("trim_sigs") else "",
        cosmic = "" if exp.get("cosmic_version_internal") == "" else "--cosmic-version {}".format(exp.get("cosmic_version_internal"))
    )

    with open(os.path.join(exp_name, "experiment_scripts", "stage_2.sh"), "w+") as f:
        f.writelines(stage_2_content)

    synthetic_experiments = [seed] + ["{}-overdispersed-{}".format(seed, p) for p in map(float, exp.get("overdispersed").split())] + ["{}-contamination-{}".format(seed, p) for p in exp.get("contamination").split()] + ["{}-perturbed-{}".format(seed, p) for p in exp.get("perturbed").split()]
    synthetic_data_files = ["{}-seed-{}.tsv".format(synthetic_prefix, se) for se in synthetic_experiments]

    ## NMF script
    nmf_content = INFER_LOADINGS_AND_SIGS_TEMPLATE.format(
        jobname = "NMF_" + exp_name,
        log_dir = os.path.join(wd, exp_name, "logs"),
        virtual_env = exp.get("virtual_env"),
        max_time = exp.get("max_time"),
        exp_name = exp_name,
        BPS_dir = wd,
        model = exp.get("model"),
        I = 96 if exp.get("subst_type") == "SBS" else (78 if exp.get("subst_type") == "DBS" else 83),
        n = exp.get("num_samples"),
        K = exp.get("K"),
        samps = exp.get("samples"),
        burnin = exp.get("burnin"),
        thin = exp.get("thin"),
        opts = "-a " + exp.get("a") + " --J0 " + exp.get("J0") 
    )

    with open(os.path.join(exp_name, "experiment_scripts", "run_nmf.sh"), "w+") as f:
        f.writelines(nmf_content)


    ## Stage IIIa
    stage_3_a_content = INFER_LOADINGS_AND_SIGS_LOOP_TEMPLATE.format(
        jobname = "submit_NMF_" + exp_name,
        log_dir = os.path.join(wd, exp_name, "logs"),
        virtual_env = exp.get("virtual_env"),
        exp_name = exp_name,
        BPS_dir = wd,
        zetas = exp.get("testing_powers"),
        synthetic_prefix = synthetic_prefix,
        prefix = synthetic_prefix + "-seed-",
        exp_list = " ".join(synthetic_experiments),
        model = exp.get("model"),
        seeds = " ".join(map(str, list(range(1, int(exp.get("no_chains")) + 1)))),
        K = exp.get("K"),
        samps = exp.get("samples"),
        burnin = exp.get("burnin"),
        a = float(exp.get("a")),
        J0 = float(exp.get("J0")),
        opts = ""
    )

    with open(os.path.join(exp_name, "experiment_scripts", "stage_3_a.sh"), "w+") as f:
        f.writelines(stage_3_a_content)

    ## Stage IIIb
    viz_content_3 = MAKE_PLOTS_TEMPLATE.format(
        log_dir = os.path.join(wd, exp_name, "logs"),
        virtual_env = exp.get("virtual_env"),
        BPS_dir = wd,
        exp_dir = exp_name,
        synthetic_prefix = synthetic_prefix + "-seed-",
        model = exp.get("model"),
        B = exp.get("burnin"),
        S = exp.get("samples"),
        K = exp.get("K"),
        a = float(exp.get("a")),
        J0 = float(exp.get("J0")),
        seeds = " ".join(map(str, list(range(1, int(exp.get("no_chains")) + 1)))),
        zetas = exp.get("testing_powers"),
        skip = exp.get("skip"),
        subst_type = exp.get("subst_type"),
        sigs_file = "" if exp.get("signatures_file") == "" else "--signatures-file {}".format(exp.get("signatures_file")),
        sigs_prefix = exp.get("signatures_prefix"),
        signatures = "", #signatures = exp.get("putative_sigs"),
        opts = "--ignore-summary ",
        cosmic = ("" if exp.get("cosmic_version_internal") == "" else "--cosmic-version {}".format(exp.get("cosmic_version_internal")))
    )

    with open(os.path.join(exp_name, "experiment_scripts", "run_viz_3.sh"), "w+") as f:
        f.writelines(viz_content_3)

    stage_3_b_content = MAKE_PLOTS_LOOP_TEMPLATE.format(
        jobname = "generate_plot_jobs_" + exp_name,
        log_dir = os.path.join(wd, exp_name, "logs"),
        virtual_env = exp.get("virtual_env"),
        BPS_dir = os.path.join(wd),
        exp_name = exp_name,
        exp_list = " ".join(synthetic_experiments),
        final_zeta = "",
        stage = str(3)
    )

    with open(os.path.join(exp_name, "experiment_scripts", "stage_3_b.sh"), "w+") as f:
        f.writelines(stage_3_b_content)

    ## Stage IV
    stage_4_content = PLOT_COMPARISON_TEMPLATE.format(
        jobname = "plot_comparison_" + exp_name,
        log_dir = os.path.join(wd, exp_name, "logs"),
        BPS_dir = wd,
        exp_dir = os.path.join(wd, exp_name),
        synthetic_prefix = synthetic_prefix + "-seed-",
        model = exp.get("model"),
        B = exp.get("burnin"),
        S = exp.get("samples"),
        K = exp.get("K"),
        a = float(exp.get("a")),
        J0 = float(exp.get("J0")),
        zetas = exp.get("testing_powers")
    )

    with open(os.path.join(exp_name, "experiment_scripts", "stage_4.sh"), "w+") as f:
        f.writelines(stage_4_content)

    ## Stage Va
    stage_5_a_content = INFER_LOADINGS_AND_SIGS_LOOP_TEMPLATE.format(
        jobname = "submit_NMF_" + exp_name,
        log_dir = os.path.join(wd, exp_name, "logs"),
        virtual_env = exp.get("virtual_env"),
        exp_name = exp_name,
        BPS_dir = wd,
        # zetas = exp.get("testing_powers"), 
        zetas = "$1",
        synthetic_prefix = exp.get("sample_prefixes"),
        prefix = exp.get("sample_prefixes"),
        exp_list = "",
        model = exp.get("model"),
        seeds = " ".join(map(str, list(range(1, int(exp.get("no_chains")) + 1)))),
        K = exp.get("K"),
        samps = exp.get("samples"),
        burnin = exp.get("burnin"),
        a = float(exp.get("a")),
        J0 = float(exp.get("J0")),
        opts = ""
    )

    with open(os.path.join(exp_name, "experiment_scripts", "stage_5_a.sh"), "w+") as f:
        f.writelines(stage_5_a_content)

    ## Stage Vb
    viz_content_5 = MAKE_PLOTS_TEMPLATE.format(
        log_dir = os.path.join(wd, exp_name, "logs"),
        virtual_env = exp.get("virtual_env"),
        BPS_dir = wd,
        exp_dir = exp_name,
        synthetic_prefix = "",
        model = exp.get("model"),
        B = exp.get("burnin"),
        S = exp.get("samples"),
        K = exp.get("K"),
        a = float(exp.get("a")),
        J0 = float(exp.get("J0")),
        seeds = " ".join(map(str, list(range(1, int(exp.get("no_chains")) + 1)))),
        zetas = "$2",
        # zetas = exp.get("testing_powers"),
        skip = exp.get("skip"),
        subst_type = exp.get("subst_type"),
        sigs_file = "" if exp.get("signatures_file") == "" else "--signatures-file {}".format(exp.get("signatures_file")),
        sigs_prefix = exp.get("signatures_prefix"),
        signatures = "",
        opts = "--ignore-summary ",
        cosmic = ("" if exp.get("cosmic_version_final") == "" else "--cosmic-version {}".format(exp.get("cosmic_version_final")))
    )

    with open(os.path.join(exp_name, "experiment_scripts", "run_viz_5.sh"), "w+") as f:
        f.writelines(viz_content_5)

    stage_5_b_content = MAKE_PLOTS_LOOP_TEMPLATE.format(
        jobname = "generate_plot_jobs_" + exp_name,
        log_dir = os.path.join(wd, exp_name, "logs"),
        virtual_env = exp.get("virtual_env"),
        BPS_dir = os.path.join(wd),
        exp_name = exp_name,
        exp_list = exp.get("sample_prefixes") + "_original_counts",
        final_zeta = "$1",
        stage = str(5)
    )

    with open(os.path.join(exp_name, "experiment_scripts", "stage_5_b.sh"), "w+") as f:
        f.writelines(stage_5_b_content)

if __name__ == '__main__':
    main()
