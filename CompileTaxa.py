"""Script to compile a taxa name conversion table, used as a reference for
subsequent conversion request calls.

Author:         James Chamness
Last Modified:  11/02/2016
"""

"""Dependencies"""
import importlib.util
import os
spec = importlib.util.spec_from_file_location("Common", "../../pipeline/Common.py")
Common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Common)

"""Return list of experimental taxa and accessions from the fieldbook.

    Sourced from one of the genotype-barcode keyfile. If no accession is listed,
    supply "NA".
    
    Arguments:
    summarize -- if True, print information about the set
    enumerate -- if True, print the whole list of taxa in lexicographical order
"""
def getTaxaFromFieldbook(genotypeBarcodeKeyFilename, env, summarize=False, enumerate=False):
    taxa = []
    barcodeKeyfile = open(genotypeBarcodeKeyFilename)
    for line in barcodeKeyfile:
        vals = line.split(",")
        if not vals[0] == "name" and not vals[0] == "B73" and not vals[0] == "Mo17":
            taxon = (vals[0],vals[1])
            taxa.append(taxon)
    
    if summarize:
        print("Taxa according to the " + env + " fieldbook:")
        print("    " + str(len(taxa)) + " unique experimental taxa")
    if enumerate:
        for taxon in sorted(taxa):
            print(taxon[0])
            #print(taxon[1]) # accession
            #print(taxon[0] + "\t" + taxon[1]) # both
    return sorted(taxa)

"""Apply transformations to fieldbook names to establish new taxa name standard.

    Returns the set of taxa names in the same order as the input set.
    Transformations applied:
    1) all leading/trailing whitespace chars removed
    2) all chars to uppercase
    3) all spaces, dashes, periods and colons to underscores
    
    I have verified that these transformations do not lead to any non-unique
    taxa names.
    
    Arguments:
    fieldbookNames -- a list of the taxa names according to the MLC fieldbooks
"""
def buildStandardFromFieldbookNames(fieldbookNames):
    standard = []
    for taxon in fieldbookNames:
        standardName = taxon.strip()
        standardName = standardName.upper()
        standardName = standardName.replace(" ","_")
        standardName = standardName.replace("-","_")
        standardName = standardName.replace(".","_")
        standardName = standardName.replace(":","_")
        standard.append(standardName)
    return standard

"""Return list of (taxa, accession) from Hirsch et al., 2014, supp. table 1.

    Returns a list of tuples. If no accession is listed, supply "NA".
    
    Arguments:
    summarize -- if True, print information about the set
    enumerate -- if True, print the whole list of taxa in lexicographical order
"""
def getHirsch_et_al_2014_Taxa_Supp1Table(suppTable1Filename, summarize=False,enumerate=False):
    taxa = []
    suppTableFile = open(suppTable1Filename)
    lineNum = 0
    for line in suppTableFile:
        lineNum += 1
        if lineNum <= 3:
            continue
        vals = line.split("\t")
        genotype = vals[0].strip()
        accessionNumber = vals[1].strip()
        taxon = (genotype,accessionNumber)
        taxa.append(taxon)
        
    if summarize:
        print("Taxa in Hirsch et al., 2014, Supplementary Table 1:")
        print("    " + str(len(taxa)) + " taxa")
        print("    " + str(len(set(list(map(lambda x: x[0], taxa))))) + " unique taxa") # consider unique genotype names
    if enumerate:
        for taxon in sorted(taxa):
            print(taxon[0])
            #print(taxon[1]) # accession
            #print(taxon[0] + "\t" + taxon[1]) # both
    
    return sorted(taxa)

"""Return list of taxa from Hirsch et al., 2014 table of raw SNPs.

    Sourced from the genotype file with raw SNPs for the 485K set
    (maize_503genotypes_485179SNPs_working_SNP_set.txt)
    
    Arguments:
    summarize -- if True, print information about the set
    enumerate -- if True, print the whole list of taxa in lexicographical order
"""
def getHirsch_et_al_2014_Taxa_RawSNPTable(rawInputFilename, summarize=False,enumerate=False):
    inputFile = open(rawInputFilename)
    lineNum = 0
    for line in inputFile:
        lineNum += 1
        vals = line.split("\t")
        if lineNum == 1:
            taxa = vals[5:]
            taxa = list(map(lambda x: x.strip(), taxa))
        else:
            break
    if summarize:
        print("Taxa in Hirsch et al., 2014, raw SNP table:")
        print("    " + str(len(taxa)) + " taxa")
        print("    " + str(len(set(taxa))) + " unique taxa") # consider unique genotype names
    if enumerate:
        for taxon in sorted(taxa):
            print(taxon)
    
    return sorted(taxa)

"""Return list of taxa from Hirsch et al., 2014 table of imputed SNPs

    Sourced from the genotype file with imputed SNPs for the 438K set
    (GAPIT.RNAseq.hmp_438K_imputed2.csv)
    
    Arguments:
    summarize -- if True, print information about the set
    enumerate -- if True, print the whole list of taxa in lexicographical order
"""
def getHirsch_et_al_2014_Taxa_ImputedSNPTable(imputedInputFilename, summarize=False,enumerate=False):
    inputFile = open(imputedInputFilename)
    lineNum = 0
    for line in inputFile:
        lineNum += 1
        vals = line.split(",")
        if lineNum == 1:
            taxa = list(map(lambda x: x.strip()[1:-1], vals[11:]))
            taxa = list(map(lambda x: x.strip(), taxa))
        else:
            break
    
    if summarize:
        print("Taxa in Hirsch et al., 2014, imputed SNP table:")
        print("    " + str(len(taxa)) + " taxa")
        print("    " + str(len(set(taxa))) + " unique taxa") # consider unique genotype names
    if enumerate:
        for taxon in sorted(taxa):
            print(taxon)
    
    return sorted(taxa)

"""Executable"""
if __name__ == "__main__":
    
    AZ16_genotypeBarcodeKeyfilename = Common.designPath + os.sep + "MLC_AZ16_Genotypes_to_PlotBarcodes_Key.csv"
    SD16_genotypeBarcodeKeyfilename = Common.designPath + os.sep + "MLC_SD16_Genotypes_to_PlotBarcodes_Key.csv"
    Hirsch_suppTable1Filename = Common.designPath + os.sep + "taxa" + os.sep + "Hirsch_et_al_2014_Supplemental_Table_1.csv"
    Hirsch_rawInputFilename = Common.genotypeTopLevel + os.sep + "maize_503genotypes_485179SNPs_working_SNP_set.txt"
    Hirsch_imputedInputFilename = Common.genotypeTopLevel + os.sep + "GAPIT.RNAseq.hmp_438K_imputed2.csv"
    
    AZ16_fieldbook_taxa = getTaxaFromFieldbook(AZ16_genotypeBarcodeKeyfilename, "AZ16")
    SD16_fieldbook_taxa = getTaxaFromFieldbook(SD16_genotypeBarcodeKeyfilename, "SD16")
    
    """Consider differences between the sets from the two field designs"""
#     missing = set(AZ16_fieldbook_taxa).difference(set(SD16_fieldbook_taxa))
#     for taxon in missing:
#         print(eltaxon)
#     
#     missing = set(SD16_fieldbook_taxa).difference(set(AZ16_fieldbook_taxa))
#     for taxon in missing:
#         print(taxon)
    
    """Create the master set of taxa as the union of the two sets, then apply
    name standardization"""
#     all_MLC_fieldbook_taxa = list(set(AZ16_fieldbook_taxa).union(set(SD16_fieldbook_taxa)))
#     standard_taxa = buildStandardFromFieldbookNames(list(map(lambda x: x[0], all_MLC_fieldbook_taxa)))
#     print(len(standard_taxa))
#     for taxon in sorted(standard_taxa):
#         print(taxon)
    
    """I used the functions below to list all the taxa and accessions from the
    different sources, then built a spreadsheet by hand matching them by hand.
    The spreadsheet is used for all subsequent translation between name schema.
    """
    HirschSuppTable_taxa = getHirsch_et_al_2014_Taxa_Supp1Table(Hirsch_suppTable1Filename,False,False)
    HirschRawSNP_taxa = getHirsch_et_al_2014_Taxa_RawSNPTable(Hirsch_rawInputFilename,False,False)
    HirschImputedSNP_taxa = getHirsch_et_al_2014_Taxa_ImputedSNPTable(Hirsch_imputedInputFilename,False,False)
    
    """The table used for name conversion"""
    masterTableFilename = Common.designPath + os.sep + "taxa" + os.sep + "taxa_&_accession_name_mappings.csv"
    masterTaxaTable = Common.readTableFromFile(masterTableFilename, delimChar=',', header=True)
    
    #for i in range(0, len(masterTaxaTable)):
    #    for j in range(0, len(masterTaxaTable[i])):
    #        if (masterTaxaTable[i][j] != masterTaxaTable[i][j].strip()):
    #            print(masterTaxaTable[i][j])
    
    print("Done!")