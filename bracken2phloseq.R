#!/usr/bin/env Rscript

library(optparse, verbose = FALSE, warn.conflicts = FALSE)
library(phyloseq, verbose = FALSE, warn.conflicts = FALSE)
library(stringr, verbose = FALSE, warn.conflicts = FALSE)
library(dplyr, verbose = FALSE, warn.conflicts = FALSE)

# Bracken output into phyloseq object.

option_list = list(
  make_option(c("-i", "--input"), default = NULL, type = "character", help = "Combined bracken report file"),
  make_option(c("-m", "--metadata"), default = NULL, type = "character", help = "Sample metadata *.csv file"),
  make_option(c('-t', '--taxonomy'), default = NULL, type = "character", help = "taxonomy file in tsv format"),
  make_option(c("-o", "--output"), default = "brackenSpecies", type = "character", help = "Output file name prefix [default=%default]")
)
opt = parse_args(OptionParser(option_list=option_list))

# Parsing input files
if (is.null(opt$input)) {
  stop(sprintf("Specify the (-i) input file"))
} else if (file.access(opt$input) == -1) {
  stop(sprintf("Specified Combine bracken report ( %s ) does not exist", opt$input))
} else {
  bracken_estimates=read.table(opt$input, sep="\t", header = TRUE, row.names = 'name', comment.char = "", quote="", check.names = FALSE) # Bracken report
}

# Checking metadata file
if (is.null(opt$metadata)) {
  stop(sprintf("Specify the (-m) metadata file"))
} else if (file.access(opt$metadata) == -1) {
  stop(sprintf("Specified metadata file ( %s ) does not exist", opt$metadata))
} else {
  metadata=read.csv(opt$metadata, header = TRUE, row.names = 1, comment.char = "", quote="", check.names = FALSE) # Sample metadata
}

# Check taxonomy file
if (is.null(opt$taxonomy)) {
  stop(sprintf("Specify the (-t) taxonomy file"))
} else if (file.access(opt$input) == -1) {
  stop(sprintf("Specified taxonomy file ( %s ) does not exist", opt$taxonomy))
} else {
  taxonomy=read.table(opt$taxonomy, sep="\t", header = TRUE, comment.char = "", quote="", check.names = FALSE) # Taxonomy file
}

# Phyloseq objects

## Species abundance
### Filtering fractions
bracken_estimates <- bracken_estimates %>% select(-ends_with("_frac"))
### Filtering taxa and levels
bracken_estimates=select(bracken_estimates, -c("taxonomy_id","taxonomy_lvl"))
### Replacing the _all from sample names.
s_names=str_replace_all(colnames(bracken_estimates),".bracken.report_num","")
### Replacing the colnames with a new one.
colnames(bracken_estimates)=s_names
### otu/species abundance table
species_abundance=otu_table(bracken_estimates, taxa_are_rows = TRUE)

## Sample metadata
sample_names_in_abundance = colnames(bracken_estimates)
metadata = metadata %>% filter(row.names(metadata) %in% sample_names_in_abundance)
meta=sample_data(metadata)

## Species taxonomy
taxonomy=taxonomy %>% filter(lvl_type == "s")
rownames(taxonomy) = taxonomy$name
taxonomy=select(taxonomy, -c("lvl_type","name"))
taxonomy[c('Domain','Phylum','Class','Order','Family','Genus','Species')] <- str_split_fixed(taxonomy$taxonomy,';',7)
taxonomy_df = select(taxonomy, -c("taxonomy"))
taxonomy_df$Domain=str_replace(taxonomy_df$Domain, c("d__"), "")
taxonomy_df$Phylum=str_replace(taxonomy_df$Phylum, c("p__"), "")
taxonomy_df$Class=str_replace(taxonomy_df$Class, c("c__"), "")
taxonomy_df$Order=str_replace(taxonomy_df$Order, c("o__"), "")
taxonomy_df$Family=str_replace(taxonomy_df$Family, c("f__"), "")
taxonomy_df$Genus=str_replace(taxonomy_df$Genus, c("g__"), "")
taxonomy_df$Species=str_replace(taxonomy_df$Species, c("s__"), "")
taxa_mat = as.matrix(taxonomy_df)
taxa_taxonomy = tax_table(taxa_mat)

# Create Phyloseq object
speciesObj=phyloseq(species_abundance, meta, taxa_taxonomy)

print(speciesObj)

# Write phyloseq object
saveRDS(speciesObj, file = file.path(paste0(basename(opt$output),c(".rds"))))
