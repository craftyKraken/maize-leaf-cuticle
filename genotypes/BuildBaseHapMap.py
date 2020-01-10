"""Stitch together the HapMap table and header created by script BuildHapMaps.r.

Author:         James Chamness
Last Modified:  12/06/2016
"""

"""Dependencies"""
import os

"""Executable"""
if __name__ == "__main__":
    
    os.chdir("/home/james/GoreLab/MaizeLeafCuticle/genotypes")
    
    """Stitch together the header and data table into a single file for the imputed genotypes"""
    imputedInputTableNoHeaderFilename = "MLC_taxa_imputed_438K_genotypes_noHeader.csv"
    imputedInputTableHeaderFilename = "MLC_taxa_imputed_438K_genotypes_header.csv"
    imputedInputTableHeader = []
    for line in open(imputedInputTableHeaderFilename):
        imputedInputTableHeader = line.strip().split("\t")
        #print(line)
        #imputedInputTableHeader.append(line.strip())
    imputedOutputTableFilename = "MLC_taxa_imputed_438K_genotypes.hmp.txt"
    out = open(imputedOutputTableFilename, 'w')
    for i in range(0, len(imputedInputTableHeader)-1):
        colHeader = imputedInputTableHeader[i]
        #out.write(colHeader.replace(" ","_") + "\t")
        out.write(colHeader + "\t")
    out.write(imputedInputTableHeader[-1] + "\n")
    input = open(imputedInputTableNoHeaderFilename)
    for line in input:
        out.write(line)
        
    out.close()
    
#     """Stitch together the header and data table into a single file for the raw genotypes"""
#     rawInputTableNoHeaderFilename = "MLC_taxa_raw_485K_genotypes_noHeader.csv"
#     rawInputTableHeaderFilename = "MLC_taxa_raw_485K_genotypes_header.csv"
#     rawInputTableHeader = []
#     for line in open(rawInputTableHeaderFilename):
#         rawInputTableHeader = line.strip().split("\t")
#         #print(line)
#         #rawInputTableHeader.append(line.strip())
#     rawOutputTableFilename = "MLC_taxa_raw_485K_genotypes.hmp.txt"
#     out = open(rawOutputTableFilename, 'w')
#     for i in range(0, len(rawInputTableHeader)-1):
#         colHeader = rawInputTableHeader[i]
#         #out.write(colHeader.replace(" ","_") + "\t")
#         out.write(colHeader + "\t")
#     out.write(rawInputTableHeader[-1] + "\n")
#     input = open(rawInputTableNoHeaderFilename)
#     for line in input:
#         out.write(line)
#     out.close()
    
    print("Done!")