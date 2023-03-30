#!/usr/bin/python3

import numpy as np 

DEFAULTS = """[DEFAULT]
experiment_name = temp_experiment
base_dir = /cga/scarter/cathyxue/bayes-power-sig
virtual_env = /cga/scarter/cathyxue/mutsig-venv


### STAGE I ###
signatures_file = 
signatures_prefix = Signature
cosmic_version = v2
subst_type = SBS
putative_sigs = 
plain = False

### STAGE II ###
trim_sigs = True
synthetic_data_seed = 1
perturbed = 0.0025
contamination = 2
overdispersed = 2

### STAGE III-V ###
inferring_signatures = True
model = normalized
testing_powers = 0.1 0.2 0.3 0.4 0.6 0.8 1
no_chains = 4
thin = 4
I = 96
K = 45
samples = 10000
burnin = 10000
max_time = 96:00:00
a = 0.5
J0 = 10.
eps = 0.001
skip = 25



"""


REPLICATE_TEMPLATE = """[SUBSAMPLE-{size}-{rep}]
experiment_name = subsample-liver-{size}-replicate-{rep}
data = data/synthetic-liver-subsamples/synthetic-326-liver-hcc-all-seed-1-subsample-{size}-replicate-{rep}.tsv
sample_prefixes = liver-hcc-subsample-{size}-replicate-{rep}
num_samples = {size}
plain = True


"""


SUBSAMPLE_SIZES = [20, 30, 50, 80, 120, 170, 230]
SUBSAMPLE_REPLICATES = [32, 20, 12, 10, 10, 10, 10]


ini_content = DEFAULTS
print(ini_content)
for s, max_r in zip(SUBSAMPLE_SIZES, SUBSAMPLE_REPLICATES):
	print(s, max_r)
	for i in np.arange(max_r):
		ini_content = ini_content + REPLICATE_TEMPLATE.format(size = s, rep = i + 1)

print(ini_content)
with open("liver_subsample.ini", "w+") as f:
	f.writelines(ini_content)



