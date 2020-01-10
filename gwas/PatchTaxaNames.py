"""Apply patch to restore proper genotype names in kinship matrix files created
by the script 'BuildKinshipMatricesWithKChr.r' for the K-chromosome GWAS
approach. 

In the aforementioned script, the genotype file used to calculate the kinship
matrices is read in with header=TRUE at first. R is picky about permissible
header field names, and will automatically modify the field name strings if it
doesn't like them. This is a problem, because this modifies the genotype names
in the input file, such that they don't match up with phenotypes later on. This
script applies a custom patch to the kinship matrix files for a particular
configuration to restore proper genotype names.  

Corrections:
1) If a header name begins with a numeric character, R prepends "X" to the field
name; remove the "X" prefix.
2) Some characters are swapped: e.g., "." for ":" and "(" or ")"

This script is intended to be called from within the R script.

Some of the genotype corrections are hard-coded; do not apply this script to a
novel dataset without proofing the genotype names.

Author:         James Chamness
Last Modified:  11/07/2016
"""

"""Dependencies"""
import sys

"""Apply patch to given input file, writing correction to given output file.    

    Arguments:
    inputFilename -- 
    outputFilename -- 
"""
def patchFile(inputFilename, outputFilename):
    inputFile = open(inputFilename)
    out = open(outputFilename, 'w')
    lineNum = 0
    for line in inputFile:
        lineNum += 1
        genoString = line.split("\t")[0]
        
        if genoString[0] == "X":
            #print(genoString)
            try:
                float(genoString[1:1]) # if the next character is numeric, it's almost certainly because R changed it
            except ValueError:
                genoString = genoString[1:] # eliminate the X prepended by R to header strings starting with a number
        else:
            newLine = line
        
        if genoString == "LH143_.MAINTAINER.":
            genoString = "LH143_(MAINTAINER)"
        if genoString == "NY_159_.NEVEH_YAAR.":
            genoString = "NY_159_(NEVEH_YAAR)"
        newLine = genoString + line[line.find("\t"):]
        newLine = newLine.strip()
        
        #print(newLine)
        out.write(newLine+"\n")  
    out.close()

"""Executable"""
if __name__ == "__main__":
    
    inputFilename = sys.argv[1]
    outputFilename = sys.argv[2]
    
    #inputFilename = "/home/james/GoreLab/MaizeLeafCuticle/GWAS/RelativeCuticularEvaporation/AllEnvs/KinshipMatrices/K_Chromosome_VanRaden_AllSNPs/GAPIT.Kin.VanRaden.csv"
    #outputFilename = "/home/james/GoreLab/MaizeLeafCuticle/GWAS/RelativeCuticularEvaporation/AllEnvs/KinshipMatrices/K_Chromosome_VanRaden_AllSNPs/GAPIT.Kin.VanRaden2.csv"
    
    patchFile(inputFilename, outputFilename)
    
    
#     inputFilenames = ["Zhang/Zhang_Kinship_chr1.csv",
#                  "Zhang/Zhang_Kinship_chr2.csv",
#                  "Zhang/Zhang_Kinship_chr3.csv",
#                  "Zhang/Zhang_Kinship_chr4.csv",
#                  "Zhang/Zhang_Kinship_chr5.csv",
#                  "Zhang/Zhang_Kinship_chr6.csv",
#                  "Zhang/Zhang_Kinship_chr7.csv",
#                  "Zhang/Zhang_Kinship_chr8.csv",
#                  "Zhang/Zhang_Kinship_chr9.csv",
#                  "Zhang/Zhang_Kinship_chr10.csv",
#                  
#                  ]
#     
#     outputFilenames = ["MatricesForGWAS/Zhang/Zhang_Kinship_chr1.txt",
#                  "MatricesForGWAS/Zhang/Zhang_Kinship_chr2.txt",
#                  "MatricesForGWAS/Zhang/Zhang_Kinship_chr3.txt",
#                  "MatricesForGWAS/Zhang/Zhang_Kinship_chr4.txt",
#                  "MatricesForGWAS/Zhang/Zhang_Kinship_chr5.txt",
#                  "MatricesForGWAS/Zhang/Zhang_Kinship_chr6.txt",
#                  "MatricesForGWAS/Zhang/Zhang_Kinship_chr7.txt",
#                  "MatricesForGWAS/Zhang/Zhang_Kinship_chr8.txt",
#                  "MatricesForGWAS/Zhang/Zhang_Kinship_chr9.txt",
#                  "MatricesForGWAS/Zhang/Zhang_Kinship_chr10.txt",
#                  
#                  ]
#     
#     
#     for i in range(0,10):
#         inputFilename = inputFilenames[i]
#         outputFilename = outputFilenames[i]
#         patchFile(inputFilename, outputFilename)
#         
#         inputFilename = inputFilename.replace("Zhang","VanRaden")
#         outputFilename = outputFilename.replace("Zhang","VanRaden")
#         patchFile(inputFilename, outputFilename)
#         
#        
#    print("Done!")