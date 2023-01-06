#!/usr/bin/env Rscript

# Convert the multi-sample kraken report to phyloseq object

library(optparse, verbose = FALSE, warn.conflicts = FALSE)
library(phyloseq, verbose = FALSE, warn.conflicts = FALSE)
library(stringr, verbose = FALSE, warn.conflicts = FALSE)
library(dplyr, verbose = FALSE, warn.conflicts = FALSE)

#setwd("/Users/tiwari/Desktop/Project/git/KBKen")

option_list = list(
  make_option(c("-i", "--input"), default = NULL, type = "character", help = "Combined Kraken report file"),
  make_option(c("-m", "--metadata"), default = NULL, type = "character", help = "Sample metadata *.csv file"),
  make_option(c("-r", "--rank"), type="character", default = "G", help = "Available options: S --> Species, G --> Genus, [default=%default]"),
  make_option(c("-o", "--output"), default = NULL, type = "character", help = "Output file name prefix")
)
opt = parse_args(OptionParser(option_list=option_list))

# Check if argumnets are provided or file exist
if (is.null(opt$input)) {
  stop(sprintf("Missing (-i) input file"))
} else if (file.access(opt$input) == -1) {
  stop(sprintf("Specified Combine Kraken report ( %s ) does not exist", opt$input))
} else {
  kreports=read.table(opt$input, sep="\t", header = TRUE)  
}

# Sample metadata
if (is.null(opt$metadata)) {
  stop(sprintf("Missing metadata ( -m ) file"))
} else if (file.access(opt$metadata) == -1) {
  stop(sprintf("Specified metadata ( %s ) file does not exist", opt$metadata))
} else {
  metadata=read.csv(opt$metadata, header = TRUE, row.names = 1)
  meta=sample_data(metadata)
}

# Output file name
if (is.null(opt$output)) {
  stop(sprintf("Specify the output (-o) file name prefix"))
}
# Replacing the _all from sample names.
s_names=str_replace_all(colnames(kreports),"_all","")

# Replacing the colnames with a new one.
colnames(kreports)=s_names

# Get Genus
if (toupper(opt$rank) == "S"){
  taxa_df=kreports %>% filter(lvl_type == "S")
} else {
  taxa_df=kreports %>% filter(lvl_type == "G")
}
row.names(taxa_df)=taxa_df$name
taxa_df=select(taxa_df, -c("lvl_type","name")) # Removing column lvl_type
taxa_phyloseq=otu_table(taxa_df, taxa_are_rows = TRUE)

# Phyloseq object
taxaObj=phyloseq(taxa_phyloseq, meta)

# Write phyloseq object
saveRDS(taxaObj, file = file.path(paste0(basename(opt$output),c(".rds"))))
