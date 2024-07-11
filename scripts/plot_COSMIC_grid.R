require(dplyr)
require(ggplot2)
require(gridExtra)

# sig.names <- c('SBS1', 'SBS2', 'SBS3', 'SBS4', 'SBS5', 'SBS6', 'SBS7a', 'SBS7b', 
#                'SBS7c', 'SBS7d', 'SBS8', 'SBS9', 'SBS10a', 'SBS10b', 'SBS11', 
#                'SBS12', 'SBS13', 'SBS14', 'SBS15', 'SBS16', 'SBS17a', 'SBS17b', 
#                'SBS18', 'SBS19', 'SBS20', 'SBS21', 'SBS22', 'SBS23', 'SBS24', 
#                'SBS25', 'SBS26', 'SBS27', 'SBS28', 'SBS29', 'SBS30', 'SBS31', 
#                'SBS32', 'SBS33', 'SBS34', 'SBS35', 'SBS36', 'SBS37', 'SBS38', 
#                'SBS39', 'SBS40', 'SBS41', 'SBS42', 'SBS43', 'SBS44', 'SBS45') 

sig.names <- paste("Signature", 1:30) 


######

args <- commandArgs(trailingOnly=TRUE)
exp.dir <- args[1]
synthetic.prefix <- args[2]
synthetic.suffix <- args[3]
zetas <- strsplit(args[4], " ")[[1]] %>% as.numeric()


setwd(exp.dir)
exp.names <- read.csv("synthetic_data/exp_list.txt", header = FALSE)$V1
n.exp <- length(exp.names)
synthetic.dirs <- paste0(synthetic.prefix, exp.names, synthetic.suffix)

seed <- exp.names[1]
exp.names[1] <- "well-specified"
exp.names <- sub(paste0(seed, "-"), "", exp.names)

## read in ground truth signatures and loadings
GT <- file.path("synthetic_data", paste0(synthetic.prefix, seed, "-GT-loadings.csv")) %>% read.csv(header = FALSE)
GT <- cbind(rep("Ground Truth", nrow(GT)), GT, rep(0L, nrow(GT)))
colnames(GT) <- c("Experiment", "Mean.Loading", "COSMIC.SBS.Signature", "Cosine.Error")
GT
sig.order <- GT %>% arrange(desc(Mean.Loading)) %>% select(COSMIC.SBS.Signature) %>% c(sig.names) %>% unlist() %>% unique()


## read in experiment results
plot.info <- list()
p <- list()
for (i in 1:n.exp)  {
    plot.info[[i]] <- GT
    sim.list <- c("Ground Truth")
    for (zeta in zetas)  {
        sim.exp <- sprintf(paste0("%s_%.", - floor(log10(min(zetas))), "f"), exp.names[i], zeta)
        summary.file <- sprintf("best-seed-comparison-zeta-%.3f-list.csv", zeta) %>%
            file.path("figures", synthetic.dirs[i], .)
        if (file.exists(summary.file))  {
            sprintf("Reading summary file: %s", summary.file)
            df <- read.csv(summary.file) 
            df <- sim.exp %>% rep(nrow(df)) %>% cbind(df)
            colnames(df) <- colnames(GT)
            df$Mean.Loading <- strsplit(df$Mean.Loading, " ") %>% 
                lapply(function (x) {x[4]}) %>% 
                unlist() %>% 
                sapply(function (x) {substr(x, 1, nchar(x) - 1)}) %>% 
                as.numeric()
            plot.info[[i]] <- rbind(plot.info[[i]], df)
        }
        else  {
            df <- data.frame(sim.exp, NA, GT$COSMIC.SBS.Signature[1], 0)
            colnames(df) <- colnames(GT)
            plot.info[[i]] <- rbind(plot.info[[i]], df)
        }
        sim.list <- c(sim.list, sim.exp)
    }
    plot.info[[i]]$COSMIC.SBS.Signature <- factor(plot.info[[i]]$COSMIC.SBS.Signature, levels = sig.order)
    plot.info[[i]]$Experiment <- factor(plot.info[[i]]$Experiment, levels = sim.list)
    p[[i]] <- plot.info[[i]] %>% 
        ggplot(aes(Experiment, COSMIC.SBS.Signature, fill = Cosine.Error)) +
        geom_point(aes(size = Mean.Loading), shape = 21) +
        # scale_fill_distiller(limits = c(0, 0.3), na.value = "black", direction = 1) + 
        scale_fill_gradient(low = "white", high = "dodgerblue4", limits = c(0, 0.3), na.value = "black") +
        ggtitle(exp.names[i]) + labs(x = "", y = "") + theme_bw() +
        theme(axis.text.x = element_text(angle = 30, hjust = 1, vjust = 0.9)) + 
        geom_hline(yintercept = nrow(GT) + 0.5, color = "red") + 
        geom_vline(xintercept = 1.5)
}


## plot
pdf(file.path("figures", "zeta-comparison.pdf"), width = 5, height = 4 * n.exp)
do.call(grid.arrange, append(p, list(ncol = 1)))
dev.off()

