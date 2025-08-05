require(dplyr)
require(ggplot2)
require(ggnewscale)

sig.names <- paste("Signature", 1:30) 
eps <- 1e-2

exps <- c("synthetic-38-lung-adenoca", "synthetic-113-ovary-adenoca", "synthetic-326-liver-hcc")
shortname <- c("lung", "ovary", "liver")
ind <- 1

long.prefix <- exps[ind] 
short.prefix <- shortname[ind]

suffix <- c("WS", "contamination-2", "overdispersed-2.0", "perturbed-0.0025")
short.suffix <- c("WS", "C", "OD", "P")

synthetic.dirs <- paste(short.prefix, suffix, sep = "-")


## read in ground truth signatures and loadings
GT <- paste0(long.prefix, "-all-seed-1-GT-loadings.csv") %>% read.csv(header = FALSE)
GT <- cbind(rep("Ground Truth", nrow(GT)), GT, rep(0L, nrow(GT)), rep("GT", nrow(GT)))
colnames(GT) <- c("Experiment", "Mean.Loading", "COSMIC.SBS.Signature", "Cosine.Error", "Method")
GT
sig.order <- GT %>% arrange(desc(Mean.Loading)) %>% select(COSMIC.SBS.Signature) %>% c(sig.names) %>% unlist() %>% unique()


## read in experiment results
plot.info <- GT

for (exp in synthetic.dirs)  {
    syn.dir <- file.path("..", exp)

    ## BayesPowerNMF
    sim.exp <- paste0("BPNMF_", exp)
    summary.file <- file.path(syn.dir, 
        list.files(syn.dir, pattern = "best-seed.*csv")[1])
    sprintf("Reading summary file: %s", summary.file)
    df <- read.csv(summary.file) 
    df <- sim.exp %>% rep(nrow(df)) %>% cbind(df, rep("BayesPowerNMF", nrow(df)))
    colnames(df) <- colnames(GT)
    df$Mean.Loading <- strsplit(df$Mean.Loading, " ") %>% 
        lapply(function (x) {x[4]}) %>% 
        unlist() %>% 
        sapply(function (x) {substr(x, 1, nchar(x) - 1)}) %>% 
        as.numeric()
    plot.info <- rbind(plot.info, df)

    ## SigProfilerExtractor
    sim.exp <- paste0("SPE_", exp)
    summary.file <- file.path(syn.dir, 
        list.files(syn.dir, pattern = "comparison_.*csv") %>% tail(n = 1))
    sprintf("Reading summary file: %s", summary.file)
    df <- read.csv(summary.file) 
    df <- sim.exp %>% rep(nrow(df)) %>% cbind(df, rep("SigProfilerExtractor", nrow(df)))
    colnames(df) <- colnames(GT)
    df$Mean.Loading <- strsplit(df$Mean.Loading, " ") %>% 
        lapply(function (x) {x[4]}) %>% 
        unlist() %>% 
        sapply(function (x) {substr(x, 1, nchar(x) - 1)}) %>% 
        as.numeric()
    plot.info <- rbind(plot.info, df)

    ## SignatureAnalyzer
    sim.exp <- paste0("SA_", exp)
    summary.file <- file.path(syn.dir, "SA_best-mutsigs-comparison-list.csv")
    sprintf("Reading summary file: %s", summary.file)
    df <- read.csv(summary.file) 
    df <- sim.exp %>% rep(nrow(df)) %>% cbind(df, rep("SignatureAnalyzer", nrow(df)))
    colnames(df) <- colnames(GT)
    df$Mean.Loading <- strsplit(df$Mean.Loading, " ") %>% 
        lapply(function (x) {x[4]}) %>% 
        unlist() %>% 
        sapply(function (x) {substr(x, 1, nchar(x) - 1)}) %>% 
        as.numeric()
    plot.info <- rbind(plot.info, df)
}

## Plot
plot.info$COSMIC.SBS.Signature <- factor(plot.info$COSMIC.SBS.Signature, levels = sig.order)
plot.info$Experiment <- factor(plot.info$Experiment, levels = unique(plot.info$Experiment))
plot.info$Method <- factor(plot.info$Method, levels = unique(plot.info$Method))

p <- plot.info %>% ggplot(aes(x = Experiment, y = COSMIC.SBS.Signature, fill = Cosine.Error)) + 
    geom_point(aes(size = Mean.Loading), shape = 21) 
for (j in 1:length(suffix)) {
    p <- p + 
        annotate("text", x = 3 * j, y = length(unique(plot.info$COSMIC.SBS.Signature)) + 1, 
                 size = 4, label = short.suffix[j]) + 
        geom_rect(data = plot.info[1,], xmin = 3 * j - 1.5, xmax = 3 * j - 0.5 + eps, 
                  ymin = -1, ymax = length(unique(plot.info$COSMIC.SBS.Signature)) + 0.5, 
                  alpha = 0.5, fill = "cornflowerblue") +
        geom_rect(data = plot.info[1,], xmin = 3 * j - 0.5 - eps, xmax = 3 * j + 0.5 + eps, 
                  ymin = -1, ymax = length(unique(plot.info$COSMIC.SBS.Signature)) + 0.5, 
                  alpha = 0.6, fill = "lightcoral") + 
        geom_rect(data = plot.info[1,], xmin = 3 * j + 0.5 - eps, xmax = 3 * j + 1.5, 
                  ymin = -1, ymax = length(unique(plot.info$COSMIC.SBS.Signature)) + 0.5, 
                  alpha = 0.6, fill = "lightgoldenrod") + 
        geom_vline(xintercept = 3 * j - 1.5)
}
p <- p + annotate("text", x = 1, y = length(unique(plot.info$COSMIC.SBS.Signature)) + 1, 
                 size = 4, label = "GT") + 
    geom_point(aes(size = Mean.Loading), shape = 21) + 
    scale_fill_gradient(low = "white", high = "gray25", limits = c(0, 0.3), na.value = "black") +
    geom_hline(yintercept = length(unique(plot.info$COSMIC.SBS.Signature)) + 0.5, color = "black") + 
    geom_hline(yintercept = nrow(GT) + 0.5, color = "red") + 
    scale_y_discrete(expand = expansion(add = c(0.75, 1.6))) + 
    scale_x_discrete(breaks = NULL, expand = expansion(add = c(0.5, 0.5))) + 
    ggtitle(paste("Synthetic", short.prefix, "comparison")) + 
    theme_bw() +
    theme(axis.title.x = element_blank(),
          axis.text.x = element_blank(), 
          axis.title.y = element_blank(), 
          axis.text.y = element_text(size = 12),
          panel.grid.major.y = element_blank(),
          legend.title = element_text(size = 12),
          legend.spacing.y = unit(-0.15, "cm")) + 
    labs(size = "Mean Loading", fill = "Recovery Error \n (cosine)") + 
    new_scale_color() + 
    geom_point(aes(1, 1, color = Method), size = -1) +
    guides(color = guide_legend(override.aes = list(size = 5, shape = 15, alpha = 0.6))) +
    scale_color_manual(values = c("BayesPowerNMF" = "cornflowerblue", 
                                  "SigProfilerExtractor" = "lightcoral",
                                  "SignatureAnalyzer" = "lightgoldenrod"))

## plot
pdf(paste0("bubble-plot_", short.prefix, "_with-SA.pdf"), width = 8, height = 4.5)
    plot(p)
dev.off()


## No SignatureAnalyzer
# plot.info.alt <- droplevels(plot.info[!plot.info$Method == "SignatureAnalyzer",])
# p <- plot.info.alt %>% ggplot(aes(x = Experiment, y = COSMIC.SBS.Signature, fill = Cosine.Error)) + 
#     geom_point(aes(size = Mean.Loading), shape = 21) 
# for (j in 1:length(suffix)) {
#     p <- p + 
#         annotate("text", x = 2 * j + 0.5, y = length(unique(plot.info.alt$COSMIC.SBS.Signature)) + 1, 
#                  size = 4, label = short.suffix[j]) + 
#         geom_rect(data = plot.info.alt[1,], xmin = 2 * j - 0.5, xmax = 2 * j + 0.5 + eps, 
#                   ymin = -1, ymax = length(unique(plot.info.alt$COSMIC.SBS.Signature)) + 0.5, 
#                   alpha = 0.5, fill = "cornflowerblue") +
#         geom_rect(data = plot.info.alt[1,], xmin = 2 * j + 0.5 - eps, xmax = 2 * j + 1.5, 
#                   ymin = -1, ymax = length(unique(plot.info.alt$COSMIC.SBS.Signature)) + 0.5, 
#                   alpha = 0.6, fill = "lightcoral") +  
#         geom_vline(xintercept = 2 * j - 0.5)
# }
# p <- p + annotate("text", x = 1, y = length(unique(plot.info.alt$COSMIC.SBS.Signature)) + 1, 
#                  size = 4, label = "GT") + 
#     geom_point(aes(size = Mean.Loading), shape = 21) + 
#     scale_fill_gradient(low = "white", high = "gray25", limits = c(0, 0.3), na.value = "black") +
#     geom_hline(yintercept = length(unique(plot.info.alt$COSMIC.SBS.Signature)) + 0.5, color = "black") + 
#     geom_hline(yintercept = nrow(GT) + 0.5, color = "red") + 
#     scale_y_discrete(expand = expansion(add = c(0.75, 1.6))) + 
#     scale_x_discrete(breaks = NULL, expand = expansion(add = c(0.5, 0.5))) + 
#     ggtitle(paste("Synthetic", short.prefix, "comparison")) + 
#     theme_bw() +
#     theme(axis.title.x = element_blank(),
#           axis.text.x = element_blank(), 
#           axis.title.y = element_blank(), 
#           panel.grid.major.y = element_blank(),
#           legend.title = element_text(size = 8)) + 
#     labs(size = "Mean Loading", fill = "Recovery Error \n (cosine)") + 
#     new_scale_color() + 
#     geom_point(aes(1, 1, color = Method), size = -1) +
#     guides(color = guide_legend(override.aes = list(size = 5, shape = 15, alpha = 0.6))) +
#     scale_color_manual(values = c("BayesPowerNMF" = "cornflowerblue", "SigProfilerExtractor" = "lightcoral"))


# ## plot
# pdf(paste0("bubble-plot_", short.prefix, ".pdf"), width = 6, height = 4.5)
#     plot(p)
# dev.off()



