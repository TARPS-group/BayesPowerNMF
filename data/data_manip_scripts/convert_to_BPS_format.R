
file_base = "in_vitro_exposures_SBS96_mutation_counts"

X = read.csv(paste0(file_base, ".csv"))

pyrs = c("C", "T")
nucs = c("A", "C", "G", "T")

channel.order = c()

for (i in pyrs) {
	for (j in nucs) {
		if (i != j) {
			for (k in nucs) {
				for (l in nucs) {
					channel.order = c(channel.order, paste0(k, "[", i, ">", j, "]", l))
				}
			}
		}
	}
}

## check channel order; reorder if needed

X = X[,2:ncol(X)]
rownames(X) = channel.order
write.table(X, file = paste0(file_base, ".tsv"), quote = FALSE, sep = "\t")

