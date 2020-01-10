################################################################################
#### My GWAS wrapper for the cuticular evaporation phenotypes from the maize
#### leaf cuticle project.
################################################################################

################################################################################
#### WORKSTATION CONFIGURATION
################################################################################

#### Laptop
workstation.topLevel <- "/home/james/GoreLab"

#### Server
#workstation.topLevel <- "/home/jamesc"

################################################################################
#### Dependencies
################################################################################
library('MASS') # required for ginv
library(multtest)
library(gplots)
library(LDheatmap)
library(genetics)
library(EMMREML)
library("scatterplot3d")
library("compiler")
source("http://zzlab.net/GAPIT/gapit_functions.txt")
source("http://www.zzlab.net/GAPIT/emma.txt")

################################################################################
#### Configuration
################################################################################

project.topLevel <- paste(workstation.topLevel,"/MaizeLeafCuticle/",sep="")

#### Parameters specifying the phenotype
scaleByLeafSize <- TRUE
blupsNotBlues <- TRUE # If true, the script will look for BLUPs; if false, for BLUEs
transformed <- TRUE
checkFixed <- FALSE
checkRandom <- FALSE
#envs <- "AZ16"
#envs <- "SD16"
envs <- "AllEnvs"

#### Base genotype filename for this project
base.genotype.filename <- "MLC_taxa_imputed_408K_filtered_phenoSpecific.hmp.txt"

#### GWA Model Parameters
pcs.to.include <- 0
#kinship.subsetSize <- 0.3 # haven't calculated any others yet
#kinship.model <- NA # other options include "VanRaden" and "Zhang"
kinship.model <- "VanRaden"
#kinship.model <- "Zhang"

################################################################################
#### Setup
################################################################################

#### Return phenotype designation provided parameters
getPhenotypeDesignation <- function(scaleByLeafSize,blupsNotBlues,transformed,checkFixed,checkRandom,envs) {
  pheno.designation = paste("MLC_",envs,"_CE_Rate",sep="")
  if (scaleByLeafSize) {
    pheno.designation = paste(pheno.designation,"_scaled",sep="")
  } else {
    pheno.designation = paste(pheno.designation,"_unscaled",sep="")
  }
  if (blupsNotBlues) {
    pheno.designation = paste(pheno.designation,"_BLUP",sep="")
  } else {
    pheno.designation = paste(pheno.designation,"_BLUE",sep="")
  }
  if (transformed) {
    pheno.designation = paste(pheno.designation,"_transformed",sep="")
  } else {
    pheno.designation = paste(pheno.designation,"_untransformed",sep="")
  }
  if (checkFixed) {
    pheno.designation = paste(pheno.designation,"_checkFixed",sep="")
  }
  if (checkRandom) {
    pheno.designation = paste(pheno.designation,"_checkRandom",sep="")
  }
  return(pheno.designation)
  #blux.filename = paste(blux.filename,".csv",sep="")
}

#### Return input kinship filepath provided parameters
getKinshipFilepath <- function(GWAS.topLevel, kinship.model) {
  kinship.filepath <- paste(GWAS.topLevel,"/KinshipMatrices/",sep="")
  kinship.filepath <- paste(kinship.filepath,"GenomeWide_",kinship.model,"/",sep="")
  kinship.filepath <- paste(kinship.filepath,"GAPIT.Kin.",kinship.model,".csv",sep="")
  return(kinship.filepath)
}

#### Determine top-level directory for the GWAS
GWAS.topLevel <- paste(project.topLevel,"GWAS/",sep="")
if (scaleByLeafSize) {
  GWAS.topLevel <- paste(GWAS.topLevel,"RelativeCuticularEvaporation",sep="")
} else {
  GWAS.topLevel <- paste(GWAS.topLevel,"AbsoluteCuticularEvaporation",sep="")
}
GWAS.topLevel <- paste(GWAS.topLevel,"/",envs,sep="")

#### Determine the input phenotype filepath and load
pheno.designation <- getPhenotypeDesignation(scaleByLeafSize,blupsNotBlues,transformed,checkFixed,checkRandom,envs)
pheno.filepath <- paste(project.topLevel,"phenotypes/BLUPs/BLUXTables/",sep="")
pheno.filepath <- paste(pheno.filepath,pheno.designation,".csv",sep="")
pheno <- read.table(pheno.filepath, header=T, sep="\t", colClasses=c('factor','numeric'), as.is=T)

#### Determine the input genotype filepath and load
geno.filepath <- paste(GWAS.topLevel,"/",base.genotype.filename,sep="")
geno <- read.table(geno.filepath, sep="\t", header = FALSE)

################################################################################
#### Configurable GWA model function
################################################################################
myGAPITWrapper <- function(GWAS.topLevel, pheno.designation, pheno, geno, kinship.model=NA, myPCA.total=0) {
  
  #### Determine the results directory for the GWAS and set as working directory
  res.path = paste(GWAS.topLevel,"/Results/",pheno.designation,"/",sep="")
  if (is.na(kinship.model)) {
    if (pcs.to.include == 0) {
      res.path = paste(res.path,"Naive",sep="")
    } else {
      res.path = paste(res.path,as.character(pcs.to.include),"PCs",sep="")
    }
  } else {
    res.path = paste(res.path,"GenomeWide_",kinship.model,sep="")
    res.path = paste(res.path,"_",as.character(pcs.to.include),"PCs", sep="")
  }
  try(system(paste("mkdir","-p",res.path,sep=" ")))
  setwd(res.path)
  
  #### Determine appropriate kinship matrix
  if (is.na(kinship.model)) {
    kinship.filepath = getKinshipFilepath(GWAS.topLevel, "VanRaden") # a default to get appropriately sized identity matrix
  } else {
    kinship.filepath = getKinshipFilepath(GWAS.topLevel, kinship.model)
  }
  myKI = read.csv(kinship.filepath, head = FALSE)
  if (is.na(kinship.model)) {
    myKI[1:dim(myKI)[1],2:dim(myKI)[2]]=diag(dim(myKI)[1]) # Use identity matrix so no effect on model
  }
  
  #### Call GAPIT to run GWAS
  myGAPIT <- GAPIT(
    Y=pheno,
    G=geno,
    KI=myKI,
    PCA.total=myPCA.total,
  )
}

################################################################################
#### Configurable K-Chromosome GWA model function
################################################################################
kChrGWAS <- function(GWAS.topLevel, pheno.designation, pheno, geno, kinship.model=NA, kinship.subsetSize=0.3, myPCA.total=0, chr.count=10) {
  
  #### Determine the results directory for the GWAS and set as working directory
  res.path = paste(GWAS.topLevel,"/Results/",pheno.designation,"/K_Chromosome_",kinship.model,"_",as.character(pcs.to.include),"PCs",sep="")
  try(system(paste("mkdir","-p",res.path,sep=" ")))
  setwd(res.path)
  
  #### Determine the directory containing the kinship matrices
  kin.dir = paste(GWAS.topLevel,"/KinshipMatrices/K_Chromosome_",kinship.model,sep="")
  
  for (j in c(1:chr.count) ) {
  #for (j in c(2,4,7) ) {
    
    cat("################################################################################")
    cat(paste("#### Running association study for chromosome #",j,sep=""))
    cat("####")
    
    genohd = geno[1,]
    genotmp = geno[which(geno[,3] == as.character(j)),]
    genotmp[,3] = rep('1', length(genotmp[,3])) # GAPIT wants the first (or only) chromosome to be called "1"
    genotmp = rbind(genohd, genotmp) ## only one chromosome at a time
    
    #### Determine path to chr-specific kinship matrix and load
    chr.kin.file = paste(kin.dir,"/",kinship.model,"_Kinship_chr",j,".txt",sep="")
    myKI = read.table(chr.kin.file, header=FALSE, sep='\t')
    
    #### Create directory for chromosome-wide GWAS and run with GAPIT
    chr.res.dir = paste(res.path,"/chr",j,sep="")
    system(paste('mkdir -p ',chr.res.dir,sep=''))
    setwd(chr.res.dir)
    res <- GAPIT( Y = pheno, G = genotmp, KI=myKI, plot.style="Ocean" )
    
    cat(paste("#### Association study for chromosome #",j," complete.",sep=""))
  }
  
}

################################################################################
#### Call functions to run GWAS
################################################################################
#myGAPITWrapper(GWAS.topLevel, pheno.designation, pheno, geno, kinship.model, pcs.to.include)

kChrGWAS(GWAS.topLevel, pheno.designation, pheno, geno, kinship.model, pcs.to.include)
