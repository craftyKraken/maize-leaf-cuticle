################################################################################
#### Script to perform PCA for MLC genotypes
#### 
#### Hansey et al. (2010) did some popgen analyis using STRUCTURE, and listed
#### pedigrees for most of lines in the MLC panel. I parsed the ones I could and
#### made a table matching these to the taxa names as they appear in the
#### genotype files, which I then use to color points on the PC plots.
#### 
#### The first section uses the R library pcaMethods and the kinship subset of
#### 46K SNPs. pcaMethods is not fast enough to use the entire set.
####
#### The second section reads in the output of eigenstrat (performed prior) and
#### similar plotting.
####
#### Last updated 01/05/2016
################################################################################

################################################################################
#### DEPENDENCIES
################################################################################
#source("https://bioconductor.org/biocLite.R")
#biocLite("pcaMethods")
library(pcaMethods)
library(ggplot2)
library(RColorBrewer)

################################################################################
#### WORKSTATION CONFIGURATION
################################################################################
#### Laptop
workstation.topLevel <- "/home/james/GoreLab"

#### Server
#workstation.topLevel <- "/home/jamesc"

################################################################################
#### Read in a priori features, taken from Hansey et al., 2010, and matched to
#### the taxa used here. There are two features: population group, numbered 1-9,
#### and subpopulation, including: UK, Popcorn, NSS, SSS, Sweet Corn, Midland,
#### Semi Flint, Tropical, Flint, Iodent, Tropical/NSS, Iodent/Midland, and
#### Amargo. Some taxa in our panel may have NA listed for either feature.
################################################################################
setwd(paste(workstation.topLevel,"/MaizeLeafCuticle/genotypes/popStructure",sep=""))
Hansey.features.table <- read.csv("Pedigree_&_Structure_Table.csv",header=T,sep="\t")

# order the table w.r.t. the first genotype table
order <- read.csv("order.txt",header=F,col.names=c("Genotype"))
features.table.ordered.for.012 <- data.frame(order, popGroup=rep(NA,465), subPop=rep(NA,465))
for (i in 1:465) {
  index <- which(Hansey.features.table[,1] == features.table.ordered.for.012[i,1])
  features.table.ordered.for.012[i,2] <- Hansey.features.table[i,2]
  features.table.ordered.for.012[i,3] <- as.character(Hansey.features.table[i,3])
}
################################################################################
#### Analysis using pcaMethods
################################################################################
setwd(paste(workstation.topLevel,"/MaizeLeafCuticle/genotypes",sep=""))

#### The input to pcaMethods should be a .012 file, with individuals in rows,
#### and with no column headers or row names/indices.
geno <-read.delim("MLC_taxa_imputed_46K_filtered_LDPruned.012", header=FALSE)

a <- pca(geno[,-c(1)], methods='robustPca', center=TRUE, nPcs = 10)
(R2cum(a)[1] )*100 -> percentvarexplPC1
round(percentvarexplPC1,2)-> percentvarexplPC1
(R2cum(a)[2]- R2cum(a)[1] )*100 -> percentvarexplPC2
round(percentvarexplPC2,2)-> percentvarexplPC2
(R2cum(a)[3]- R2cum(a)[2] )*100 -> percentvarexplPC3
round(percentvarexplPC3,2)-> percentvarexplPC3
(R2cum(a)[4]- R2cum(a)[3] )*100 -> percentvarexplPC4
round(percentvarexplPC4,2)-> percentvarexplPC4
(R2cum(a)[5]- R2cum(a)[4] )*100 -> percentvarexplPC5
round(percentvarexplPC5,2)-> percentvarexplPC5
(R2cum(a)[6]- R2cum(a)[5] )*100 -> percentvarexplPC6
round(percentvarexplPC6,2)-> percentvarexplPC6
(R2cum(a)[7]- R2cum(a)[6] )*100 -> percentvarexplPC7
round(percentvarexplPC7,2)-> percentvarexplPC7
(R2cum(a)[8]- R2cum(a)[7] )*100 -> percentvarexplPC8
round(percentvarexplPC8,2)-> percentvarexplPC8
(R2cum(a)[9]- R2cum(a)[8] )*100 -> percentvarexplPC9
round(percentvarexplPC9,2)-> percentvarexplPC9
(R2cum(a)[10]- R2cum(a)[9] )*100 -> percentvarexplPC10
round(percentvarexplPC10,2)-> percentvarexplPC10
scores(a)-> myind_scores

#### Build a table matching the PC values to individuals with a priori features
pca.methods.table <- data.frame(features.table.ordered.for.012,myind_scores)

#### Build color palettes for population group and subpopulation, and assign to
#### each indidual.
popGroupPalette <- brewer.pal(9, "Paired")
popGroupColors <- vector(,465)
for (i in 1:465) {
  popGroup <- pca.methods.table$popGroup[i]
  if (is.na(popGroup) || popGroup == 9) {
    popGroupColors[i] <- 'white'
    next
  }
  ## to use assigned groups
  # popGroup <- as.numeric(popGroup)
  
  ## to collapse some groups
  if (popGroup == 1 || popGroup == 4) {
    popGroupColors[i] <- 'blue'
  }
  if (popGroup == 2) {
    popGroupColors[i] <- 'black'
  }
  if (popGroup == 3 || popGroup == 5 || popGroup == 7 || popGroup == 8) {
    popGroupColors[i] <- 'green'
  }
  if (popGroup == 6) {
    popGroupColors[i] <- 'red'
  }
}


subPopPalette <- brewer.pal(12,"Set3")
subPopColors <- vector(,465)
for (i in 1:465) {
  subPop <- pca.methods.table$subPop[i]
  if (is.na(subPop)) {
    subPopColors[i] <- 'black'
    next
  }
  if (subPop == "UK") {
    subPopColors[i] <- subPopPalette[1]
  }
  if (subPop == "Popcorn") {
    subPopColors[i] <- subPopPalette[2]
  }
  if (subPop == "NSS") {
    subPopColors[i] <- subPopPalette[3]
  }
  if (subPop == "SSS") {
    subPopColors[i] <- subPopPalette[4]
  }
  if (subPop == "Sweet Corn") {
    subPopColors[i] <- subPopPalette[5]
  }
  if (subPop == "Midland") {
    subPopColors[i] <- subPopPalette[6]
  }
  if (subPop == "Semi Flint") {
    subPopColors[i] <- subPopPalette[7]
  }
  if (subPop == "Tropical") {
    subPopColors[i] <- subPopPalette[8]
  }
  if (subPop == "Flint") {
    subPopColors[i] <- subPopPalette[7]
  }
  if (subPop == "Iodent") {
    subPopColors[i] <- subPopPalette[9]
  }
  if (subPop == "Tropical/NSS") {
    subPopColors[i] <- subPopPalette[10]
  }
  if (subPop == "Iodent/Midland") {
    subPopColors[i] <- subPopPalette[11]
  }
  if (subPop == "Amargo") {
    subPopColors[i] <- subPopPalette[12]
  }
}

#### Color by population group
plot(pca.methods.table$PC1,pca.methods.table$PC2,
     main="PCA methods", xlab= paste("PC 1 (", percentvarexplPC1, '%)', sep=''),
     ylab=paste("PC 2 (", percentvarexplPC2, '%)', sep=''), cex.lab=1.3,
     pch=19, col=popGroupColors)

plot(pca.methods.table$PC2,pca.methods.table$PC3,
     main="PCA methods", xlab= paste("PC 2 (", percentvarexplPC2, '%)', sep=''),
     ylab=paste("PC 3 (", percentvarexplPC3, '%)', sep=''), cex.lab=1.3,
     pch=19, col=popGroupColors)

#### Color by subpopulation
plot(pca.methods.table$PC1,pca.methods.table$PC2,
     main="PCA methods", xlab= paste("PC 1 (", percentvarexplPC1, '%)', sep=''),
     ylab=paste("PC 2 (", percentvarexplPC2, '%)', sep=''), cex.lab=1.3,
     pch=19, col=subPopColors)

plot(pca.methods.table$PC2,pca.methods.table$PC3,
     main="PCA methods", xlab= paste("PC 2 (", percentvarexplPC2, '%)', sep=''),
     ylab=paste("PC 3 (", percentvarexplPC3, '%)', sep=''), cex.lab=1.3,
     pch=19, col=subPopColors)

# This plots a stair-shaped cross-graph of all PCs against one another
# plotPcs(a)

#### How rapidly does the variation explained by PC diminish?
varsexplained <- c(percentvarexplPC1,percentvarexplPC2,percentvarexplPC3,percentvarexplPC4,percentvarexplPC5,percentvarexplPC6,percentvarexplPC7,percentvarexplPC8,percentvarexplPC9,percentvarexplPC10)
plot(varsexplained,main="% Variance Explained: pcaMethods",xlab="PC#",ylab="% Variance Explained",col="blue",pch=19,ylim=c(1,3.5),xlim=c(1,10))

################################################################################
#### Eigenstrat Analysis
################################################################################

eval <- read.table("~/GoreLab/MaizeLeafCuticle/genotypes/MLC_taxa_imputed_408K_filtered_viaVCF.eval", header=FALSE)
evec1.pc <- round(eval[1,1]/sum(eval)*100,digits=2)
evec2.pc <- round(eval[2,1]/sum(eval)*100,digits=2)
evec3.pc <- round(eval[3,1]/sum(eval)*100,digits=2)
evec4.pc <- round(eval[4,1]/sum(eval)*100,digits=2)
evec <- read.table("~/GoreLab/MaizeLeafCuticle/genotypes/MLC_taxa_imputed_408K_filtered_viaVCF.evec", header=FALSE)

#### Build a table matching the PC values to individuals with a priori features
eigenstrat.table <- data.frame(Genotype=evec$V1,popGroup=rep(NA,465),subPop=rep(NA,465),PC1=evec$V2,PC2=evec$V3,PC3=evec$V4,PC4=evec$V5)
for (i in 1:465) {
  geno <- eigenstrat.table$Genotype[i]
  eigenstrat.table$popGroup[i] <- features.table.ordered.for.012[which(features.table.ordered.for.012$Genotype == geno),2]
  eigenstrat.table$subPop[i] <- features.table.ordered.for.012[which(features.table.ordered.for.012$Genotype == geno),3]
}

#### Build color palettes for population group and subpopulation, and assign to
#### each indidual.
popGroupPalette <- brewer.pal(9, "Paired")
popGroupColors <- vector(,465)
for (i in 1:465) {
  popGroup <- eigenstrat.table$popGroup[i]
  if (!is.na(popGroup)) {
    popGroup <- as.numeric(popGroup)
  } else {
    popGroupColors[i] <- 'black'
    next
  }
  popGroupColors[i] <- popGroupPalette[popGroup]
}

subPopPalette <- brewer.pal(12,"Paired")
subPopColors <- vector(,465)
for (i in 1:465) {
  subPop <- eigenstrat.table$subPop[i]
  if (is.na(subPop)) {
    subPopColors[i] <- 'black'
    next
  }
  if (subPop == "UK") {
    subPopColors[i] <- subPopPalette[1]
  }
  if (subPop == "Popcorn") {
    subPopColors[i] <- subPopPalette[2]
  }
  if (subPop == "NSS") {
    subPopColors[i] <- subPopPalette[3]
  }
  if (subPop == "SSS") {
    subPopColors[i] <- subPopPalette[4]
  }
  if (subPop == "Sweet Corn") {
    subPopColors[i] <- subPopPalette[5]
  }
  if (subPop == "Midland") {
    subPopColors[i] <- subPopPalette[6]
  }
  if (subPop == "Semi Flint") {
    subPopColors[i] <- subPopPalette[7]
  }
  if (subPop == "Tropical") {
    subPopColors[i] <- subPopPalette[8]
  }
  if (subPop == "Flint") {
    subPopColors[i] <- subPopPalette[7]
  }
  if (subPop == "Iodent") {
    subPopColors[i] <- subPopPalette[9]
  }
  if (subPop == "Tropical/NSS") {
    subPopColors[i] <- subPopPalette[10]
  }
  if (subPop == "Iodent/Midland") {
    subPopColors[i] <- subPopPalette[11]
  }
  if (subPop == "Amargo") {
    subPopColors[i] <- subPopPalette[12]
  }
}

#### Color by population group
plot(eigenstrat.table$PC1, eigenstrat.table$PC2,
     main="eigenstrat: EV1 vs. EV2",
     xlab=paste("eigenvector1\n",evec1.pc, "% of observed genetic variation", sep=""),
     ylab=paste("eigenvector2\n",evec2.pc, "% of observed genetic variation", sep=""),
     pch=19, col=popGroupColors
)

plot(eigenstrat.table$PC2, eigenstrat.table$PC3,
     main="eigenstrat: EV2 vs. EV",
     xlab=paste("eigenvector2\n",evec2.pc, "% of observed genetic variation", sep=""),
     ylab=paste("eigenvector3\n",evec3.pc, "% of observed genetic variation", sep=""),
     pch=19, col=popGroupColors
)

#### Color by subpopulation
plot(eigenstrat.table$PC1, eigenstrat.table$PC2,
     main="eigenstrat: EV1 vs. EV2",
     xlab=paste("eigenvector1\n",evec1.pc, "% of observed genetic variation", sep=""),
     ylab=paste("eigenvector2\n",evec2.pc, "% of observed genetic variation", sep=""),
     pch=19, col=subPopColors
)

plot(eigenstrat.table$PC2, eigenstrat.table$PC3,
     main="eigenstrat: Ev2 vs. EV3",
     xlab=paste("eigenvector2\n",evec2.pc, "% of observed genetic variation", sep=""),
     ylab=paste("eigenvector3\n",evec3.pc, "% of observed genetic variation", sep=""),
     pch=19, col=subPopColors
)

#### How rapidly does the variation explained by PC diminish?
varsexplained.eigenstrat <- c(evec1.pc,evec2.pc,evec3.pc,evec4.pc)
plot(varsexplained.eigenstrat,main="% Variance Explained: eigenstrat",xlab="PC#",ylab="% Variance Explained",col="blue",pch=19,ylim=c(1,3.5),xlim=c(1,10))
