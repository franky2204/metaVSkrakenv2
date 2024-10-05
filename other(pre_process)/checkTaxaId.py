import re

class TaxaName:
    def __init__(self, id, name):
        self.id = id
        self.name = name
#search for taxid
def search_taxa_id(taxa_el, id):
    return next((taxa for taxa in taxa_el if taxa.id == id), None)
#search for taxaname
def search_taxa_name(taxa_el, name):
    return next((taxa for taxa in taxa_el if taxa.name == name), None)
#it eliminates all the spaces and makes the string lowercase its usefull for better comparison
def normalize_name(name):
    return re.sub(r'\s+', '', name.strip().lower())
#this is needed becase sometime the name dispayed in the taxa file is the fusion between the two deepest level
def search_corrispondance(taxa_el,name, fused_name):
    return next((taxa.id for taxa in taxa_el if normalize_name(taxa.name) == normalize_name(name) or normalize_name(taxa.name) == normalize_name(fused_name)), -1)
    

def check_taxa_id(pylo_file_path, taxa_file_path):
    count=0
    #read all the row from the kraken file and the taxa file 
    with open(pylo_file_path, 'r') as pylo_file, open(taxa_file_path, 'r') as taxa_file:
        taxa_el = []
    #the taxa part is the easiest simpli save each row as a TaxaName object in a list
        for line in taxa_file:
            line = line.strip().split('\t')
            taxa_el.append(TaxaName(line[0], line[1]))
        next(pylo_file)
    #for each row in the kraken file we will try to find the corresponding taxa in the taxa file
    #the cicle is used to find the last non NA value in the row that will correspond 
    # to the deepest three level(to witch the taxa is referring)
        for line in pylo_file:
            count =+ 1
            line = line.strip().split('\t')
            i = 7
            while i >= 0 and line[i] == 'NA':
                i -= 1

            if i < 0:
                continue

            taxa = search_taxa_id(taxa_el, line[0])
        #now it searches for the taxa in the taxa file(from the kraken one)
        #if it finds it (with the correspoding name)it will write the row in the matched_taxa file
        #otherwwise search for a corresponding name in the taxa file
        #if it finds it it will write the row in the matched_taxa file with the taxaid changed
            if taxa is not None:
                
                fused_name = line[i-1].strip() + ' ' + line[i].strip()
                normalized_fused_name = normalize_name(fused_name)
                normalized_species_name = normalize_name(line[i])
                normalized_taxa_name = normalize_name(taxa.name)

                if normalized_fused_name == normalized_taxa_name or normalized_species_name == normalized_taxa_name:
                    with open('matched_taxa.txt', 'a') as matched_file:
                        matched_file.write('\t'.join(line) + '\n')
                else:
                    n = search_corrispondance(taxa_el,line[i],fused_name)
                    if n != -1 :
                        with open('matched_taxa.txt', 'a') as matched_file:
                            line[0] = n
                            matched_file.write('\t'.join(line) + '\n')
                    else :    
                        with open('unmatched_taxa.txt', 'a') as unmatched_file:
                            unmatched_file.write('\t'.join(line) + '\n')
                            
            else:
            
                fused_name = line[i-1].strip() + ' ' + line[i].strip()
                normalized_fused_name = normalize_name(fused_name)
                normalized_species_name = normalize_name(line[i])

                with open('unmatched_taxa.txt', 'a') as unmatched_file:
                    unmatched_file.write('\t'.join(line) + '\n')
                    print(f"{count} both={normalized_fused_name} species={normalized_species_name}")
#this is used to validate the clades number present in the kraken file
#taxa file is a tsv file with taxaid and name of the taxa for each row
pyloFile = "input/Prova_phyloseq_daMetaph.tsv"
taxaFile = "input/formatted__names.tsv"

check_taxa_id(pyloFile, taxaFile)
