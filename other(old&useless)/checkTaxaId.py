import re

class TaxaName:
    def __init__(self, id, name):
        self.id = id
        self.name = name

def search_taxa_id(taxa_el, id):
    return next((taxa for taxa in taxa_el if taxa.id == id), None)

def search_taxa_name(taxa_el, name):
    return next((taxa for taxa in taxa_el if taxa.name == name), None)

def normalize_name(name):
    return re.sub(r'\s+', '', name.strip().lower())

def search_corrispondance(taxa_el,name, fused_name):
    return next((taxa.id for taxa in taxa_el if normalize_name(taxa.name) == normalize_name(name) or normalize_name(taxa.name) == normalize_name(fused_name)), -1)
    

def check_taxa_id(kraken_file_path, taxa_file_path):
    with open(kraken_file_path, 'r') as kraken_file, open(taxa_file_path, 'r') as taxa_file:
        taxa_el = []
        for line in taxa_file:
            line = line.strip().split('\t')
            taxa_el.append(TaxaName(line[0], line[1]))
        next(kraken_file)
        for line in kraken_file:
            line = line.strip().split('\t')
            i = 7
            while i >= 0 and line[i] == 'NA':
                i -= 1

            if i < 0:
                continue

            taxa = search_taxa_id(taxa_el, line[0])
            
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
                            print(f"{normalized_fused_name} | {normalized_taxa_name} | {normalized_species_name}")
            else:
            
                fused_name = line[i-1].strip() + ' ' + line[i].strip()
                normalized_fused_name = normalize_name(fused_name)
                normalized_species_name = normalize_name(line[i])

                with open('unmatched_taxa.txt', 'a') as unmatched_file:
                    unmatched_file.write('\t'.join(line) + '\n')
                    print(f"{normalized_fused_name} | Not Found")

krakenFile = "Kraken_agglom_otu_with_taxa.tsv"
taxaFile = "formatted__names.tsv"

check_taxa_id(krakenFile, taxaFile)
