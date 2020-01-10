"""Load list of SNP names to keep""" 
snpNameFile = "/home/james/GoreLab/MaizeLeafCuticle/genotypes/popStructure/plink.prune.in"
snpNames = []
for line in open(snpNameFile):
    if not line.strip() == "":
        snpNames.append(line.strip())

"""Open a file to write the pruned output to"""
outputHapMapFile = "/home/james/GoreLab/MaizeLeafCuticle/genotypes/MLC_taxa_imputed_46K_filtered_LDPruned.hmp.txt"
out = open(outputHapMapFile,'w')

"""Load unpruned HapMap file"""
inputHapMapFile = "/home/james/GoreLab/MaizeLeafCuticle/genotypes/MLC_taxa_imputed_408K_filtered.hmp.txt"
lineNum = 1

for line in open(inputHapMapFile):
    if line.strip() == "":
        continue
    if lineNum == 1:
        #pass
        out.write(line)
    else:
        snp = line[:line.find("\t")]
        if not snp in snpNames:
            continue
        else:
            out.write(line)
            snpNames.remove(snp) # for speed
    lineNum += 1
    
print("Done!")