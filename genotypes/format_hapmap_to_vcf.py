import os, sys

# The input file format is

#rs#	alleles	chrom	pos	strand	assembly#	center	protLSID	assayLSID	panelLSID	QCcode	sample1 sample 2 etc (1 column per sample)
# e.g. S01_23664	C/T	01	23664	+	NA	NA	NA	NA	NA	NA	C	N	C

# Note that chr are coded 01, 02 etc up to 10
# Genotypes code:
# A,C,T,G: hmz
# N: missing
# other letters: htz
# - hmz deletion
# + hmz insertion
# 0 htz indel

# read the second column and get the nucleotide(s) from there
# if there is only one letter, it means the SNP is fixed
# otherwise, split by slash character
# the first one if the ref, the other one it the alt
# recode the first as 0, the second as 2, other letter as 1, except for N that are -1
# add a vcf header
##fileformat=VCFv4.2
##filedate=20160818
##source="beagle.27Jun16.b16.jar (version 4.1)"
##INFO=<ID=AF,Number=A,Type=Float,Description="Estimated ALT Allele Frequencies">
##INFO=<ID=AR2,Number=1,Type=Float,Description="Allelic R-Squared: estimated squared correlation between most probable REF dose and true REF dose">
##INFO=<ID=DR2,Number=1,Type=Float,Description="Dosage R-Squared: estimated squared correlation between estimated REF dose [P(RA) + 2*P(RR)] and true REF dose">
##INFO=<ID=IMP,Number=0,Type=Flag,Description="Imputed marker">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=DS,Number=A,Type=Float,Description="estimated ALT dose [P(RA) + P(AA)]">
##FORMAT=<ID=GP,Number=G,Type=Float,Description="Estimated Genotype Probability">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	sample1 sample 2 etc

# The output format is a vcf, so it should have the following info:

# 01	23664	S01_23664	C	T	.	PASS	AR2=0.99;DR2=0.99;AF=0.10	GT:DS:GP	0/0:0:1,0,0   0/0:0:1,0,0


filename = sys.argv[1] # input vcf, here sorghum_first72WGS.hmp.txt
outname = sys.argv[2] # name of the output, here sorghum_first72WGS_noImput.vcf

output = open(outname,'w')
output.write('##fileformat=VCFv4.2\n')
output.write('##filedate=20161220\n')
output.write('##source="beagle.27Jun16.b16.jar (version 4.1)"\n')
output.write('##INFO=<ID=AF,Number=A,Type=Float,Description="Estimated ALT Allele Frequencies">\n')
output.write('##INFO=<ID=AR2,Number=1,Type=Float,Description="Allelic R-Squared: estimated squared correlation between most probable REF dose and true REF dose">\n')
output.write('##INFO=<ID=DR2,Number=1,Type=Float,Description="Dosage R-Squared: estimated squared correlation between estimated REF dose [P(RA) + 2*P(RR)] and true REF dose">\n')
output.write('##INFO=<ID=IMP,Number=0,Type=Flag,Description="Imputed marker">\n')
output.write('##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n')
output.write('##FORMAT=<ID=DS,Number=A,Type=Float,Description="estimated ALT dose [P(RA) + P(AA)]">\n')
output.write('##FORMAT=<ID=GP,Number=G,Type=Float,Description="Estimated Genotype Probability">\n')

headerlast = '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t' # and add sample names to that

for line in open(filename):
    if len(line) <= 1:
        continue
    if line.startswith('rs#'):
        a = line.strip().split('\t')
        indvlist = a[11:]
        indvstr = '\t'.join(map(str,indvlist))+'\n'
        headerlast = headerlast + indvstr
        output.write(headerlast)
        continue

    a = line.strip().split('\t')
    alleles = a[1]
    if len(alleles) == 3: # exclude fixed, 'NA', triallelic
        if '-' in alleles or '0' in alleles:
            continue
        ## There are also cases like that:
        ## S10_58283280	A/-	10	58283280	+	NA	NA	NA	NA	NA	NA	A	-	N	A	A
        ## filter out lines with 0 or -, we are going to exclude indels for now
        all1 = alleles.split('/')[0]
        all2 = alleles.split('/')[1]
        new_line_beginning = 'Chr'+ str(a[2]) +'\t'+ str(a[3]) + '\t.\t' + all1 + '\t' + all2 + '\t.\tPASS\tAR2=0;DR2=0;AF=0\tGT:DS:GP\t'

        for g in a[11:]:
            if g == all1:
                new_line_beginning = new_line_beginning + '0/0:1:1,0,0'+ '\t'
            elif g == all2:
                new_line_beginning = new_line_beginning + '1/1:1:0,0,1' + '\t'
            elif g == 'N':
                new_line_beginning = new_line_beginning + './.' + '\t'
            else:
                new_line_beginning = new_line_beginning + '0/1:1:0,1,0' + '\t'
        new_line_beginning = new_line_beginning + '\n'
        output.write(new_line_beginning)
output.close()
