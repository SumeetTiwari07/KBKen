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
  make_option(c("-r", "--rank"), type="character", default = "S", help = "Available options: S --> Species, G --> Genus, [default=%default]"),
  make_option(c("-o", "--output"), default = NULL, type = "character", help = "Output file name prefix")
)
opt = parse_args(OptionParser(option_list=option_list))

# Check if argumnets are provided or file exist
if (is.null(opt$input)) {
  stop(sprintf("Missing (-i) input file"))
} else if (file.access(opt$input) == -1) {
  stop(sprintf("Specified Combine Kraken report ( %s ) does not exist", opt$input))
} else {
  kreports=read.table(opt$input, sep="\t", header = TRUE, comment.char = "", quote = "", check.names = FALSE)
}

# Sample metadata
if (is.null(opt$metadata)) {
  stop(sprintf("Missing metadata ( -m ) file"))
} else if (file.access(opt$metadata) == -1) {
  stop(sprintf("Specified metadata ( %s ) file does not exist", opt$metadata))
} else {
  metadata=read.csv(opt$metadata, header = TRUE, row.names = 1, comment.char = "", quote = "", check.names = FALSE)
}

# Output file name
if (is.null(opt$output)) {
  stop(sprintf("Specify the output (-o) file name prefix"))
}

# Get Genus or species
if (toupper(opt$rank) == "G"){
  taxa_df=kreports %>% filter(lvl_type == "g" | lvl_type == "u")
} else {
  taxa_df=kreports %>% filter(lvl_type == "s" | lvl_type == "u")
}

# Species/genus names as index
row.names(taxa_df)=taxa_df$name

# otu/species/genus abundance
abundance=select(taxa_df, -c("lvl_type","name","taxonomy")) # Removing columns

# Taxonomy
taxonomy_df=select(taxa_df, c("taxonomy"))

taxonomy_df[c('Domain','Phylum','Class','Order','Family','Genus','Species')] <- str_split_fixed(taxonomy_df$taxonomy,';',7)
taxonomy_df = select(taxonomy_df, -c("taxonomy"))
taxonomy_df$Domain=str_replace(taxonomy_df$Domain, c("d__"), "")
taxonomy_df$Phylum=str_replace(taxonomy_df$Phylum, c("p__"), "")
taxonomy_df$Class=str_replace(taxonomy_df$Class, c("c__"), "")
taxonomy_df$Order=str_replace(taxonomy_df$Order, c("o__"), "")
taxonomy_df$Family=str_replace(taxonomy_df$Family, c("f__"), "")
taxonomy_df$Genus=str_replace(taxonomy_df$Genus, c("g__"), "")
taxonomy_df$Species=str_replace(taxonomy_df$Species, c("s__"), "")

# if rank = G remove the unclassified species
# the taxonomy_df consist of Genus by default but since there is s__unclassified
# Thats why discard species

if (toupper(opt$rank) == "G") {
  taxonomy_df = select(taxonomy_df, -c("Species")) 
}

# Create phyloseq objects

## Abundance
taxa_abundance=otu_table(abundance, taxa_are_rows = TRUE)

## Sample Metadata
sample_names_in_abundance = colnames(abundance)
metadata = metadata %>% filter(row.names(metadata) %in% sample_names_in_abundance)
meta=sample_data(metadata) # Metadata

## taxonomy
taxa_mat = as.matrix(taxonomy_df)
taxa_taxonomy = tax_table(taxa_mat)

## Phyloseq object
taxaObj=phyloseq(taxa_abundance, meta, taxa_taxonomy)

print(taxaObj)

# Write phyloseq object
saveRDS(taxaObj, file = file.path(paste0(basename(opt$output),c(".rds"))))
data = readRDS(file.path(paste0(basename(opt$output),c(".rds"))))
print(data)
