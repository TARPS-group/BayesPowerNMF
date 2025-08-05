require(dplyr)
require(ggplot2)
require(ggnewscale)

setwd("../PCAWG-bubble")

## pull SPE global sigs 
SPE.global <- read.csv("PCAWG_sigProfiler_SBS_signatures_in_samples.csv")
sig.names <- colnames(SPE.global)[4:53] 

exps <- c("Lung-AdenoCA", "Stomach-AdenoCA", "Skin-Melanoma", "Ovary-AdenoCA", "Breast", "Liver-HCC")

plot.info <- data.frame(Experiment = character(), 
                        Mean.Loading = numeric(),
                        COSMIC.SBS.Signature = character(), 
                        Cosine.Error = numeric(), 
                        Method = character())

for (i in 1:length(exps))  {
    exp <- exps[i]
    
    ## COSMIC+NNLS
    loadings <- SPE.global[grepl(exp, SPE.global$Cancer.Types, fixed = TRUE), 4:48]
    mean.loadings <- colMeans(loadings)
    
    df <- data.frame(paste0("COSMIC+NNLS_", exp),
                     mean.loadings[mean.loadings > 0],
                     names(loadings)[mean.loadings > 0],
                     0,
                     "COSMIC+NNLS")
    colnames(df) <- colnames(plot.info)
    rownames(df) <- NULL
    plot.info <- rbind(plot.info, df)
    
    ## SPE-Local
    spe <- read.csv(paste0(exp, "_SPE.csv"))
    mean.loadings <- spe$Loadings %>% 
        strsplit(" ") %>% 
        lapply(function (x) {x[4]}) %>% 
        unlist() %>% 
        sapply(function (x) {substr(x, 1, nchar(x) - 1)}) %>% 
        as.numeric()
    df <- data.frame(paste0("SPE_", exp),
                     mean.loadings,
                     spe$COSMIC,
                     spe$Cosine.Error,
                     "SigProfilerExtractor")
    colnames(df) <- colnames(plot.info)
    plot.info <- rbind(plot.info, df)
    
    ## BPS
    bps <- read.csv(paste0(exp, "_BPS.csv"))
    mean.loadings <- bps$Loadings %>% 
        strsplit(" ") %>% 
        lapply(function (x) {x[4]}) %>% 
        unlist() %>% 
        sapply(function (x) {substr(x, 1, nchar(x) - 1)}) %>% 
        as.numeric()
    df <- data.frame(paste0("BPNMF_", exp),
                     mean.loadings,
                     bps$COSMIC,
                     bps$Cosine.Error,
                     "BayesPowerNMF")
    colnames(df) <- colnames(plot.info)
    plot.info <- rbind(plot.info, df)
}



## Plot
plot.info$COSMIC.SBS.Signature <- factor(plot.info$COSMIC.SBS.Signature, levels = sig.names)
plot.info$Experiment <- factor(plot.info$Experiment, levels = unique(plot.info$Experiment))
plot.info$Method <- factor(plot.info$Method, levels = unique(plot.info$Method))

eps <- 1e-2

p <- plot.info %>% ggplot(aes(x = Experiment, y = COSMIC.SBS.Signature, fill = Cosine.Error)) + 
    geom_point(aes(size = Mean.Loading), shape = 21) 
for (j in 1:length(exps)) {
    p <- p + 
        annotate("text", x = 3 * j - 1, y = length(unique(plot.info$COSMIC.SBS.Signature)) + 1.6, 
                 size = 5, label = exps[j]) + 
        # geom_rect(data = plot.info[1,], xmin = 3 * j - 2.5, xmax = 3 * j - 1.5 + eps, 
        #           ymin = -1, ymax = length(unique(plot.info$COSMIC.SBS.Signature)) + 0.5, 
        #           alpha = 0.5, fill = "cornflowerblue") +
        geom_rect(data = plot.info[1,], xmin = 3 * j - 1.5 - eps, xmax = 3 * j - 0.5 + eps, 
                  ymin = -1, ymax = length(unique(plot.info$COSMIC.SBS.Signature)) + 0.5, 
                  alpha = 0.4, fill = "lightcoral") + 
        geom_rect(data = plot.info[1,], xmin = 3 * j - 0.5 - eps, xmax = 3 * j + 0.5, 
                  ymin = -1, ymax = length(unique(plot.info$COSMIC.SBS.Signature)) + 0.5, 
                  alpha = 0.4, fill = "cornflowerblue") + 
        geom_vline(xintercept = 3 * j + 0.5)
}
p <- p + geom_point(aes(size = Mean.Loading), shape = 21) + 
    scale_fill_gradient(low = "white", high = "gray25", limits = c(0, 0.2), na.value = "black") +
    geom_hline(yintercept = length(unique(plot.info$COSMIC.SBS.Signature)) + 0.5, color = "black") +
    scale_y_discrete(expand = expansion(add = c(0.75, 3))) + 
    scale_x_discrete(breaks = NULL, expand = expansion(add = c(0.5, 0.5))) + 
    ggtitle("Signature recovery on PCAWG project data") +
    theme_bw() +
    theme(axis.title.x = element_blank(),
          axis.title.y = element_blank(), 
          axis.text.x = element_blank(),
          axis.text.y = element_text(size = 14), 
          panel.grid.major.y = element_blank(),
          plot.title = element_text(size = 22),
          legend.text = element_text(size = 16),
          legend.title = element_text(size = 20)) + 
    labs(size = "Mean Loading", fill = "Recovery Error \n (cosine)") + 
    new_scale_color() +
    geom_point(aes(1, 1, color = Method), size = -1) +
    guides(color = guide_legend(override.aes = list(size = 5, shape = 15, alpha = 0.6))) +
    scale_color_manual(values = c("COSMIC+NNLS" = "white",
                                  "SigProfilerExtractor" = "lightcoral",
                                  "BayesPowerNMF" = "cornflowerblue"))

## plot
pdf(paste0("bubble-plot_PCAWG.pdf"), width = 15, height = 10)
    plot(p)
dev.off()


wilcox.test(plot.info$Cosine.Error[plot.info$Method == "BayesPowerNMF"], plot.info$Cosine.Error[plot.info$Method == "SigProfilerExtractor"])
mean(plot.info$Cosine.Error[plot.info$Method == "BayesPowerNMF"])
mean(plot.info$Cosine.Error[plot.info$Method == "SigProfilerExtractor"])





