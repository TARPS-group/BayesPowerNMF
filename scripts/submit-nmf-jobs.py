#!/usr/bin/python3

import argparse
import os
import sys

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('template')
    parser.add_argument('experiment_dir')
    parser.add_argument('--seeds', metavar='seed', nargs='*')
    parser.add_argument('--zetas', type=float, metavar='zeta', nargs='*')
    parser.add_argument('--scripts-dir', default = "experiment_scripts")
    parser.add_argument('--results-dir', default = "results")
    return parser.parse_args()


def main():
    args = parse_args()
    
    any_submit = False
    sbatch_template = "sbatch --array={seeds} " + os.path.join(args.experiment_dir, args.scripts_dir, "stage_")

    for zeta in zetas:
        for exp in experiment_list:
            run_seeds = []
            for s in seeds:
                if not os.path.exists(os.path.join(args.experiment_dir, args.results_dir, template.format(s, zeta) + ".h5")):
                    run_seeds.append(s)
                    any_submit = True

            if len(run_seeds) > 0:
                os.system()

    if not any_submit:
        print("All sampling completed. Proceed to next step.")



if __name__ == '__main__':
    main()
