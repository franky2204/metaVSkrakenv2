class taxaName(id, name):
    self.id = id
    self.name = name

def checkTaxaId():
    # Open the files
    krakenFile = open(krakenFile, 'r')
    taxaFile = open(taxaFile, 'r')
    taxaEl=[]
    kraken
    # Create a dictionary to store the taxa ids
    taxaDict = {}
    for line in taxaFile:
        line = line.strip().split('\t')
        taxaEl.append(taxaName(line[0],line[1]))

    # Check if the taxa ids in the kraken file are in the taxa file
    # Skip the first line
    next(krakenFile)
    for line in krakenFile:
        line = line.strip().split('\t')
        i=7
        for line[i]= "NA":
            i=i-1
        if line[0] in taxaDict:
        


    # Close the files
    krakenFile.close()
    taxaFile.close()








krakenFile="Kraken_agglom_otu_with_taxa.tsv"
taxaFile="formatted__names.tsv"

checkTaxaId(krakenFile,taxaFile)