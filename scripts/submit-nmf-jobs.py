#!/usr/bin/python3

import argparse
import os
import sys

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('prefix')
    parser.add_argument('experiment_dir')
    parser.add_argument('output_template')
    parser.add_argument('--seeds', metavar='seed', nargs='*')
    parser.add_argument('--zetas', type=float, metavar='zeta', nargs='*')
    parser.add_argument('--exp-list', nargs='*')
    parser.add_argument('--slurm', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    
    any_submit = False
    if args.slurm:
        batch_template = "sbatch --array={seeds} --job-name={exp}_{prefix}_NMF_{zeta} " + os.path.join(args.experiment_dir, "experiment_scripts", "run_nmf.sh") + " {zeta} {data_file}"
    else:
        batch_template = "qsub -t {seeds} -N {exp}_{prefix}_NMF_{zeta} " + os.path.join(args.experiment_dir, "experiment_scripts", "run_nmf.sh") + " {zeta} {data_file}"

    for zeta in args.zetas:
        # Stage III
        for exp in args.exp_list:
            run_seeds = []
            for s in args.seeds:
                if not os.path.exists(os.path.join(args.experiment_dir, "results", args.output_template.format(exp = exp, seed = s, zeta = zeta))):
                    run_seeds.append(s)
                    # print("Missing " + os.path.join(args.experiment_dir, "results", args.output_template.format(exp = exp, seed = s, zeta = zeta)))
                    any_submit = True

            if len(run_seeds) > 0:
                experiment = args.prefix + "-seed-" + exp
                cmd = batch_template.format(seeds = ",".join(map(str, run_seeds)), exp = args.experiment_dir, prefix = experiment, zeta = zeta, data_file = experiment + ".tsv")
                print(cmd)
                os.system(cmd)

        # Stage V
        if len(args.exp_list) == 0:
            run_seeds = []
            for s in args.seeds:
                if not os.path.exists(os.path.join(args.experiment_dir, "results", args.output_template.format(exp = "", seed = s, zeta = zeta))):
                    run_seeds.append(s)
                    any_submit = True

            if len(run_seeds) > 0:
                cmd = batch_template.format(seeds = ",".join(map(str, run_seeds)), exp = args.experiment_dir, prefix = args.prefix, zeta = zeta, data_file = args.prefix + "_original_counts.tsv")
                print(cmd)
                os.system(cmd)

    if not any_submit:
        print("All sampling completed. Proceed to next step.")



if __name__ == '__main__':
    main()
