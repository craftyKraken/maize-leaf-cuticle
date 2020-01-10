"""Dependencies"""
import importlib.util
import os
from matplotlib.testing.jpl_units import day
spec = importlib.util.spec_from_file_location("Common", "../../pipeline/Common.py")
Common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Common)


""" Read in table with pop structure features: S1 Table from Hansey et al. """
rawFeatureTable = []
sourceFilename = "../../design/taxa/Hansey_et_al_2010_Supplemental_Table_1.csv"
for line in open(sourceFilename):
    vals = line.strip().split("\t")
    genotype = vals[1]
    #print(genotype)
    popGroup = vals[4]
    group = vals[13]
    rawFeatureTable.append([genotype,popGroup,group])

""" Make a list of the MLC standard genotype names ordered as they need to be
to correspond with the values output by pcaMethods. This order is determined by
the .012 files.

Write a copy of this list to file that is easy for R to read."""
genos = []
outFile = open("../popStructure/order.txt",'w')

for line in open("../MLC_taxa_imputed_408K_filtered_viaVCF.ind"):
    geno = line.strip()[:line.strip().find(" U")].strip()
    #print(geno)
    genos.append(geno)
    outFile.write(geno + "\n")
outFile.close()

""" Match genotypes of interest to features """
features = {}
duplicated = []
for entry in rawFeatureTable[1:]:
    #print(entry)
    fgeno = entry[0]
    #print(fgeno)
    try:
        geno = Common.translateNameToStandard(fgeno,6)
        if not geno in list(features.keys()):
            # replace empty entries with NA
            #if entry[0].strip == ".":
            #    entry[0] = "NA"
            #if entry[1].strip == ".":
            #    entry[1] = "NA"
            features[geno] = entry[1:]
        #### Determined all duplicates have identical features
        else:
            #features[geno] = (features[geno],entry[1:])
            if not geno in duplicated:
                duplicated.append(geno)
    except ValueError:
        #print(entry)
        continue

""" Write a table matching known features to genotype names """
featureTableFilename = "../popStructure/Pedigree_&_Structure_Table.csv"
featureTableFile = open(featureTableFilename,'w')
header="Genotype\tPopulation_Group\tSubpopulation\n"
featureTableFile.write(header)
for genotype in sorted(list(features.keys())):
    popGroup = features[genotype][0]
    subPop = features[genotype][1]
    if popGroup == ".": popGroup = "NA"
    if subPop == ".": subPop = "NA"
    featureTableFile.write(genotype + "\t" + popGroup + "\t" + subPop + "\n")
 
missing = set(genos).difference(set(list(features.keys())))
for genotype in missing:
    featureTableFile.write(genotype + "\tNA\tNA\n")
 
featureTableFile.close()

print("Done!")