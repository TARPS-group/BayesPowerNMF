import os
import sys
import argparse

import numpy as np
import scipy as sp
import pandas

from mutsigtools import models


MODEL_DEFAULT = 'normalized'
A_DEFAULT = 1.0
ALPHA_DEFAULT = 0.5
EPS_DEFAULT = 1e-3
TOL_DEFAULT = 5e-1
J0_DEFAULT = 1.0  # i.e. J0 = J
ZETA_DEFAULT = 1.0

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('data')
    parser.add_argument('output', default='.')
    parser.add_argument('-m', '--model', default=MODEL_DEFAULT,
                        choices=['normalized',
                                 'normalized_hypers',
                                 'normalized_no_ard',
                                 'normalized_gamma_ard',
                                 'normalized_v2'],
                        help='model to use')
    parser.add_argument('-I', type=int, default=96,
                        help='number of substitution types')
    parser.add_argument('-K', type=int, default=20,
                        help='maximum number of mutational signatures')
    parser.add_argument('--samples', '-s', type=int, default=1000,
                        help='total number of samples to draw after burnin')
    parser.add_argument('--burnin', '-b', type=int, default=1000,
                        help='total number of burnin samples')
    parser.add_argument('--thin', type=int, default=1,
                        help='thin the samples')
    parser.add_argument('--max-J', type=int, default=0,
                        help='maximum number of samples to analyze')
    parser.add_argument('-a', type=float, default=A_DEFAULT,
                        help='loadings prior hyperparameter')
    parser.add_argument('--alpha', type=float, default=ALPHA_DEFAULT,
                        help='mutational signatures prior hyperparameter')
    parser.add_argument('--epsilon', '-e', type=float, default=EPS_DEFAULT,
                        help='ARD tolerance parameter')
    parser.add_argument('--no-rho', action='store_true',
                        help='do not rescale rates by counts')
    parser.add_argument('--J0', type=float, default=J0_DEFAULT,
                        help='minimum sample support (for ARD prior). Intepreted as J * J0 if J0 <= 1.')
    parser.add_argument('--zeta', type=float, default=ZETA_DEFAULT,
                        help='power likelihood factor')
    parser.add_argument('--seed', type=int, default=1,
                        help='random seed')
    parser.add_argument('--prob-zero', type=float, default=None)
    parser.add_argument('--q1', type=float, default=None)
    parser.add_argument('--q99', type=float, default=None)
    parser.add_argument('--sparse', action='store_true')
    return parser.parse_args()



def main():
    args = parse_args()

    os.makedirs(args.output, exist_ok=True)
    data = pandas.read_csv(args.data, sep='\t')
    counts = data.iloc[:,1:].values

    if args.I != counts.shape[0]:
        raise ValueError('incorrect number of substitution types')

    J = counts.shape[1]
    if args.max_J > 0 and J > args.max_J:
        J = args.max_J
        counts = counts[:,:J]

    J0 = args.J0
    if J0 <= 1:
        J0 *= J

    # where to save results
    base_filename = os.path.splitext(os.path.basename(args.data))[0]
    description = '' if args.model == MODEL_DEFAULT else args.model + '-'
    description += 'burnin-{}-samps-{}-K-{}-seed-{}'.format(
        args.burnin, args.samples, args.K, args.seed)
    if args.a != A_DEFAULT:
        description += '-a-{:.2f}'.format(args.a)
    if args.alpha != ALPHA_DEFAULT:
       description += '-alpha-{:.2f}'.format(args.alpha)
    if args.epsilon != EPS_DEFAULT:
       description += '-eps-{:f}'.format(args.epsilon)
    if args.J0 != J0_DEFAULT:
       description += '-J0-{:.1f}'.format(J0)
    description += '-zeta-{:.3f}'.format(args.zeta)
    if args.no_rho:
       description += '-no-rho'
    samples_path = os.path.join(args.output,
                                '{}-{}-samples.h5'.format(base_filename,
                                                          description))

    if args.sparse is True:
        p = args.prob_zero or 0.75
        l99 = args.q99 or np.mean(counts.astype("int").sum(axis = 0)) / 2
        a0, b0 = models.set_prior_hyperparameters(p, l99)
    else:
        lst = np.sort(counts.astype("int").sum(axis = 0))
        l1 = args.q1 or lst[0] / len(sigs)
        l99 = args.q99 or np.mean(pd.DataFrame.from_dict(Xs).values.astype("int").sum(axis = 0)) / 2
        a0, b0 = models.set_prior_hyperparameters(l1, l99, False)
    print("a0: {} b0: {}".format(a0, b0))

    # sample from posterior and save results
    total_iters = args.burnin + args.samples
    models.fit_model_and_save_results(
        args.model + '_nmf', counts, args.K, samples_path, J0=J0, eps=args.epsilon,
        alpha=args.alpha, a=args.a, 
        no_rho=args.no_rho, 
        seed=args.seed, a0 = a0, b0 = b0,
        lik_power=args.zeta, iters=total_iters, warmup=args.burnin,
        control=dict(adapt_delta=.98, max_treedepth=15))


if __name__ == '__main__':
    main()
