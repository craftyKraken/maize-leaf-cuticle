################################################################################
#### This script parses GAPIT GWAS results for custom FDR adjustments and
#### Manhattan plotting.
################################################################################
library('qqman')
################################################################################
#### Configuration
################################################################################
parent.dir <- "/home/james/GoreLab/MaizeLeafCuticle/GWAS/" # laptop

#### Path to a single GAPIT results folder. Eventually will want to generate
#### this dynamically from parameters, but hardcoding for now.
results.dir <- paste(parent.dir,"AbsoluteCuticularEvaporation/AllEnvs/Results/MLC_AllEnvs_CE_Rate_unscaled_BLUP_transformed/GenomeWide_VanRaden_0PCs/",sep="")
#results.dir <- paste(parent.dir,"RelativeCuticularEvaporation/AllEnvs/Results/MLC_AllEnvs_CE_Rate_scaled_BLUP_transformed/GenomeWide_VanRaden_0PCs/",sep="")

################################################################################
#### Script
################################################################################

results.filename <- paste(results.dir,"GAPIT..PHENOTYPE.GWAS.Results.csv",sep="")
GWAS.results <- read.table(results.filename,sep=",",header=T)


for (i in 1:408597) {
  if (4085970 * GWAS.results$P.value[i] < i) {
    cat(i)
    cat("\n")
  }
}





manhattan(GWAS.results, chr="Chromosome", bp="Position",p="P.value",#"FDR_Adjusted_P.values",
          col=c("blue4","orange3"), ymax=12,
          #suggestiveline=-log10(0.10/408597),
          #genomewideline=-log10(0.05/408597),
          suggestiveline=F,
          genomewideline=F,
          ylim=c(0,7)
          )

colnames(GWAS.results)[2] <- "CHR"
colnames(GWAS.results)[3] <- "BP"
colnames(GWAS.results)[4] <- "P"

manhattan(GWAS.results)

#GWAS.results <- cbind(GWAS.results,p.adjust(GWAS.results$P.value, method="BH"))manhattan(GWAS.results)

masterResultTable$P.value.adj.gnmwide <- p.adjust(masterResultTable$P.value, method="BH")

################################################################################
#### Compile p-values from chromosome-wide association tests from K-Chr approach
################################################################################

#### Parameters determining which association study (and filepath) to do
kin.alg <- "VanRaden"
trait.name <- "aT"

### the directory containing a folder for each chromosome
resultFolder <- paste(parent.dir,"K_Chromosome_approach/Results/",kin.alg,'/',trait.name, '/',sep='') 
setwd(resultFolder) 

### build a table with all of the values
masterResultTable <- data.frame(matrix(NA,ncol=6))
colnames(masterResultTable) <- c("SNP_name","Chromosome","Position","P.value","P.value.adj.chrwide","P.value.adj.gnmwide")
for (i in c(1,2,3,4,5,6,7,8,9,10)) {
  chrResultFolder <- paste(resultFolder,"chr",i,'/',sep='')
  chrResultTable <- read.table(paste(chrResultFolder,"GAPIT..",trait.name,".GWAS.Results.csv",sep=''), sep=",", header = TRUE)
  chrResultTable <- chrResultTable[,c(1,2,3,4,9)]
  chrResultTable <- cbind(chrResultTable,rep(NA,dim(chrResultTable)[1]))
  colnames(chrResultTable) <- c("SNP_name","Chromosome","Position","P.value","P.value.adj.chrwide","P.value.adj.gnmwide")
  masterResultTable <- rbind(masterResultTable,chrResultTable)
}
### remove empty row at beginning
masterResultTable <- masterResultTable[-c(1),]

### the chromosome numbers are wrong (all=1) because of how the K-chr script feeds data to GAPIT
### correct this by parsing the true chromosome number from the SNP name
masterResultTable$Chromosome <- substr(masterResultTable$SNP_name,2,regexpr('_',masterResultTable$SNP_name)-1)

### Calculate genome-wide adjusted p-values
masterResultTable$P.value.adj.gnmwide <- p.adjust(masterResultTable$P.value, method="BH")
write.table(masterResultTable,file=paste(resultFolder,trait.name,"_",kin.alg,"pValuesFDR_corrections.csv",sep=''),quote=F,row.names=F,col.names=T,sep='\t')
