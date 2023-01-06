#!/usr/bin/env Rscript

library(optparse, verbose = FALSE, warn.conflicts = FALSE)
library(phyloseq, verbose = FALSE, warn.conflicts = FALSE)
library(stringr, verbose = FALSE, warn.conflicts = FALSE)
library(dplyr, verbose = FALSE, warn.conflicts = FALSE)

# Bracken output into phyloseq object.

option_list = list(
  make_option(c("-i", "--input"), default = NULL, type = "character", help = "Combined bracken report file"),
  make_option(c("-m", "--metadata"), default = NULL, type = "character", help = "Sample metadata *.csv file"),
  make_option(c("-o", "--output"), default = "brackenSpecies", type = "character", help = "Output file name prefix [default=%default]")
)
opt = parse_args(OptionParser(option_list=option_list))

# Parsing input files
if (is.null(opt$input)) {
  stop(sprintf("Specify the (-i) input file"))
} else if (file.access(opt$input) == -1) {
  stop(sprintf("Specified Combine bracken report ( %s ) does not exist", opt$input))
} else {
  bestimates=read.table(opt$input, sep="\t", header = TRUE, row.names = 'name') # Bracken report
}

# Checking metadafile
if (is.null(opt$metadata)) {
  stop(sprintf("Specify the (-m) metadata file"))
} else if (file.access(opt$metadata) == -1) {
  stop(sprintf("Specified metadata file ( %s ) does not exist", opt$metadata))
} else {
  metadata=read.csv(opt$metadata, header = TRUE, row.names = 1) # Sample metadata
  meta=sample_data(metadata)
}
# Filtering fractions
bestimates <- bestimates %>% select(-ends_with("_frac"))

# Filtering taxa and levels
bestimates=select(bestimates, -c("taxonomy_id","taxonomy_lvl"))

# Replacing the _all from sample names.
s_names=str_replace_all(colnames(bestimates),".bracken.report_num","")

# Replacing the colnames with a new one.
colnames(bestimates)=s_names

# Get Species
species_phyloseq=otu_table(bestimates, taxa_are_rows = TRUE)

# Create Phyloseq object
species=phyloseq(species_phyloseq, meta)

# Write phyloseq object
saveRDS(species, file = file.path(paste0(basename(opt$output),c(".rds"))))
