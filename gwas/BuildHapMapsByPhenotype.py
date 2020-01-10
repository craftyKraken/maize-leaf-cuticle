"""Prepare a GAPIT-compatible HapMap file for both the association and kinship
SNP sets, with the subset of taxa appropriate for a specified phenotype
configuration.

Author:         James Chamness
Last Modified:  12/22/2016
"""

"""Dependencies"""
import importlib.util
import subprocess
import os
spec = importlib.util.spec_from_file_location("Common", "../../pipeline/Common.py")
Common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Common)

"""Determine literal phenotype designation from parameters.

    Arguments:
    scaleByLeafSize -- if true, use absolute rate divided by leaf dry mass
    blupsNotBlues -- if true, use BLUPs; if false, then BLUEs
    transformed -- if true, use BLUXs calculated with boxcox transformation
    checkFixed -- if true, use BLUXs calculated using checks as a fixed effect
    checkRandom -- if true, use BLUXs calculated using checks as a random effect
    envs -- the environment(s) from which to select the phenotypes
            argument space: ["AZ16", "SD16", "AllEnvs"]
"""
def getPhenotypeDesignation(scaleByLeafSize,blupsNotBlues, transformed, checkFixed, checkRandom, envs):
    
    phenoDesignation = "MLC_" + envs + "_CE_Rate"
    
    if scaleByLeafSize:
        phenoDesignation += "_scaled"
    else:
        phenoDesignation += "_unscaled"
    if blupsNotBlues:
        phenoDesignation += "_BLUP"
    else:
        phenoDesignation += "_BLUE"
    if transformed:
        phenoDesignation += "_transformed"
    else:
        phenoDesignation += "_untransformed"
    if checkFixed:
        phenoDesignation += "_checkFixed"
    if checkRandom:
        phenoDesignation += "_checkRandom"
    
    return phenoDesignation

if __name__ == "__main__":
    
    """
    ============================================================================
    ============================================================================
    ==== CONFIGURATION
    ============================================================================
    ============================================================================
    """
    scaleByLeafSize = True
    blupsNotBlues = True
    transformed = True
    checkFixed = False
    checkRandom = False
    envs = "AZ16"
    #envs = "SD16"
    #envs = "AllEnvs"
    
    """
    ============================================================================
    ============================================================================
    ==== RUN SCRIPT
    ============================================================================
    ============================================================================
    """
    """
    1) Generate a file listing taxa names based on phenotype specification.
    """
    bluxTableDir = Common.projectTopLevel + os.sep + "phenotypes" + os.sep + "BLUPs" + os.sep + "BLUXTables"
    bluxTableFilename = getPhenotypeDesignation(scaleByLeafSize, blupsNotBlues, transformed, checkFixed, checkRandom, envs) + ".csv"
    bluxTablePath = bluxTableDir + os.sep + bluxTableFilename
    bluxTable = Common.readTableFromFile(bluxTablePath,header=True)
    tempFilename = Common.projectTopLevel + os.sep + "GWAS/pipeline/tempTaxaList"
    Common.writeTableToFile(list(map(lambda x: [x[0]],bluxTable)), tempFilename)
    
    """
    2) Make a system call to TASSEL to filter the base genotype files for
    those taxa.
    """
    baseAssociationGenotypeFilename = Common.genotypeTopLevel + os.sep + "MLC_taxa_imputed_408K_filtered.hmp.txt"
    baseKinshipGenotypeFilename = Common.genotypeTopLevel + os.sep + "MLC_taxa_imputed_46K_filtered_LDPruned.hmp.txt"
    exportDirectory = "/home/james/GoreLab/MaizeLeafCuticle/GWAS/"
    if scaleByLeafSize:
        exportDirectory += "RelativeCuticularEvaporation/"
    else:
        exportDirectory += "AbsoluteCuticularEvaporation/"
    exportDirectory += envs
    exportAssociationFilename = "MLC_taxa_imputed_408K_filtered_phenoSpecific.hmp.txt"
    exportKinshipFilename = "MLC_taxa_imputed_46K_filtered_LDPruned_phenoSpecific.hmp.txt"
    exportAssociationPath = exportDirectory + os.sep + exportAssociationFilename
    exportKinshipPath = exportDirectory + os.sep + exportKinshipFilename
    
    os.chdir("/home/james")
    sysCommandList = ["./TASSEL5/run_pipeline.pl","-h",baseAssociationGenotypeFilename,"-includeTaxaInFile",tempFilename,"-export",exportAssociationPath,"-exportType","HapmapDiploid"]
    subprocess.call(sysCommandList)
    sysCommandList = ["./TASSEL5/run_pipeline.pl","-h",baseKinshipGenotypeFilename,"-includeTaxaInFile",tempFilename,"-export",exportKinshipPath,"-exportType","HapmapDiploid"]
    subprocess.call(sysCommandList)
    
    """
    3) Make another system call to correct the problematic # character in
    the new genotype files.
    """
    sysCommandList = ["sed","-i","-e",'1,1s/#//g',exportAssociationPath]
    subprocess.call(sysCommandList)
    sysCommandList = ["sed","-i","-e",'1,1s/#//g',exportKinshipPath]
    subprocess.call(sysCommandList)
    
    """
    4) Make another system call to delete the file listing taxa names.
    """
    sysCommandList = ["rm",tempFilename]
    
    print("Done!")