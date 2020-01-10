################################################################################
#### This script processes the genotype file GAPIT.RNAseq.hmp_438K_imputed2.csv,
#### taken from Hirsch et al. (2014), into a GAPIT-style HapMap subselected for
#### just those taxa in the MLC panel (Wisconsin Diversity panel). It also
#### implements MLC-standard taxa names in the header, and corrects the NA
#### entries to "NN" to avoid confusing TASSEL in subsequent operations.
####
#### Last updated 12/13/2016
################################################################################

################################################################################
#### DEPENDENCIES
################################################################################
pythonStichScript <- "~/GoreLab/MaizeLeafCuticle/genotypes/pipeline/BuildBaseHapMap.py"

################################################################################
#### CONFIGURATION
################################################################################
setwd("~/GoreLab/MaizeLeafCuticle/genotypes/")
#raw.SNPs.input <- read.csv("maize_503genotypes_485179SNPs_working_SNP_set.txt", sep="\t", header=FALSE)
imputed.SNPs.input <- read.csv("GAPIT.RNAseq.hmp_438K_imputed2.csv", sep=",", header=FALSE)
taxa.name.conversion.table <- read.csv("../design/taxa/taxa_&_accession_name_mappings.csv",sep=",")

################################################################################
#### Build a new table with imputed SNPs for just our taxa
################################################################################
ourTaxaCols <- numeric()
header <- as.matrix(imputed.SNPs.input[1,])
newHeader <- header[c(1,2,3,4,5,6,7,8,9,10,11)]
taxaAdded <- 0
found <- FALSE # used to select just the first occurrence of the "CM174" genotype
for (i in 12:length(header)) {
  x <- header[i]
  if (!is.na(taxa.name.conversion.table[which(taxa.name.conversion.table$HIRSCH_IMPUTEDSNPTABLE == x),1])) {
    #### vvv #### this block is just to catch the double genotype
    if (taxa.name.conversion.table[which(taxa.name.conversion.table[,8] == x),1] == "CM174") {
      if (found) {
        next
      } else {
        found <- TRUE
      }
    }
    #### ^^^
    ourTaxaCols <- c(ourTaxaCols,i)
    taxaAdded <- taxaAdded + 1
    #newHeader <- c(newHeader, toString(taxa.name.conversion.table[which(taxa.name.conversion.table$HIRSCH_IMPUTEDSNPTABLE == x),1]))
    newHeader[11+taxaAdded] <- toString(taxa.name.conversion.table[which(taxa.name.conversion.table$HIRSCH_IMPUTEDSNPTABLE == x),1])
  }
}
## Select the subset of genotypes for just our taxa
SNP.matrix.as.df <- data.frame(imputed.SNPs.input[-c(1),ourTaxaCols])
## Convert all NA entries to "NN", the preferred HapMap naming conventions
SNP.matrix <- as.matrix(SNP.matrix.as.df)
SNP.matrix[is.na(SNP.matrix)] <- "NN"
SNP.matrix.as.df <- as.data.frame(SNP.matrix)

## Build a dataframe of the new HapMap table to write to file
imputed.HapMap.table <- data.frame(imputed.SNPs.input[-c(1),c(1,2,3,4,5,6,7,8,9,10,11)], SNP.matrix.as.df)
imputed.HapMap.table[,6] <- rep("AGPv2", 438222)

## Now have the header and the header-less table for the new HapMap. There is
## probably a way to add the header as a standard row (not as an R header), but
## I couldn't for the life of me figure out how, so I wrote a python script to
## do it instead.
write.table(imputed.HapMap.table, file="MLC_taxa_imputed_438K_genotypes_noHeader.csv", sep='\t', quote=FALSE, col.names=FALSE, row.names=FALSE)
write(newHeader, file="MLC_taxa_imputed_438K_genotypes_header.csv", sep='\t', ncolumns = length(newHeader))
system(paste("python",pythonStichScript,sep=" "))

## remove intermediate files
system(paste("rm","MLC_taxa_imputed_438K_genotypes_noHeader.csv","MLC_taxa_imputed_438K_genotypes_header.csv",sep=" "))

## The new HapMap file can then be read in as follows:
#imputed.SNPs <- read.table("MLC_taxa_imputed_438K_genotypes.hmp.txt", sep="\t", header=FALSE)
