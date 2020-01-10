################################################################################
#### This script filters SNPs.
################################################################################

################################################################################
#### DEPENDENCIES
################################################################################


################################################################################
#### CONFIGURATION
################################################################################
setwd("~/GoreLab/MaizeLeafCuticle/genotypes/")
siteSummaryTable <- read.csv("MLC_taxa_imputed_438K_genotypes_SiteSummary.txt", sep="\t", header=TRUE)
taxaSummaryTable <- read.csv("MLC_taxa_imputed_438K_genotypes_TaxaSummary.txt", sep="\t", header=TRUE)
markerCount.original <- as.numeric(dim(siteSummaryTable)[1])
sampleCount.original <- as.numeric(dim(taxaSummaryTable)[1])

##################################
##### Filter taxa ################
##################################

##### Filter by Sample Call Rate
sampleCallRates <- 1-taxaSummaryTable[,5]
hist(sampleCallRates, main="Sample Call Rate", xlab="% of total SNPs called", ylab="# of Samples",col="blue",breaks=50)
# can see all have extremely high call rates, minimum is still >98%
# this is because these SNPs are coming from transcriptome sequencing

##################################
##### Filter sites ###############
##################################

#### Each criteria here is applied independently to see how many sites are filtered from the original set
#### I make a list of names of SNPs passing each filter, and at the end I take the intersection to produce the filtered set

#### Select only biallelic SNPs (this was already done, so none should be filtered - just a sanity check)
SNPs.biallelic <- siteSummaryTable[which(is.na(siteSummaryTable[,14])),2]
markerCount.biallelic <- length(SNPs.biallelic)
filteredProportion <- markerCount.biallelic/markerCount.original
cat(filteredProportion)

#### Filter on SNP Call Rate
#### Using different criteria for SNP sets used for kinship and for GWAS
snpCallRates <- 1-siteSummaryTable[,31]
minSNPCallRate <- 0.95
hist(snpCallRates, main="SNP Call Rate", xlab="% of total Samples with each SNP", ylab="# of SNPs",col="blue", breaks=50)
abline(v=minSNPCallRate,col="red", lty=2,lwd=2)
SNPs.minCallRate <- siteSummaryTable[which(snpCallRates > minSNPCallRate),2]
markerCount.minCallRate <- length(SNPs.minCallRate)
filteredProportion <- markerCount.minCallRate/markerCount.original
cat(filteredProportion)

#### MAF
minMAF <- 0.05
MAFs <- siteSummaryTable[,13]
hist(MAFs, main="Loci by MAF", xlab="MAF", ylab="# of Loci", col="blue")
abline(v=minMAF,col="red", lty = 2, lwd=2)
SNPs.minMaf <- siteSummaryTable[which(MAFs >= minMAF),2]
markerCount.maf <- length(SNPs.minMaf)
filteredProportion <- markerCount.maf/markerCount.original
cat(filteredProportion)

#### Inbreeding coefficient: F = 1 - Hobs/Hexp = 1 - proportion heterozygous/(2pq)
#### Again - original set was prefiltered for homozygous calls. Another sanity check,
#### everything should pass.
minF <- 0.95
Hobs <- siteSummaryTable[,33]
Hexp <- 2*MAFs*(1-MAFs)
F <- 1 - Hobs/Hexp
F <- replace(F,which(is.nan(F)),1)
hist(F, main="Inbreeding Coefficient by SNP", xlab="F", ylab="# of SNPs", col="blue",breaks=50)
hist(F, main="Inbreeding Coefficient by SNP", xlab="F", ylab="# of SNPs", col="blue",breaks=500, xlim=c(0.5,1))
abline(v=minF,col="red", lty = 2, lwd=2)
SNPs.minInbreeding <- siteSummaryTable[which(F > minF),2]
markerCount.minInbreeding <- length(SNPs.minInbreeding)
filteredProportion <- markerCount.minInbreeding/markerCount.original
cat(filteredProportion)

### Write the list of site and taxa names passing filtering criteria
SNPs <- siteSummaryTable[which(siteSummaryTable[,2] %in% intersect(SNPs.biallelic,intersect(SNPs.minCallRate,intersect(SNPs.minMaf,SNPs.minInbreeding)))),c(2,3,4)]
total.filteredProportion <- dim(SNPs)[1] / markerCount.original
cat(total.filteredProportion)
write.table(SNPs[,1], file="filtered_SNPs.csv",quote=FALSE,sep="\t", col.names=FALSE, row.names=FALSE)
