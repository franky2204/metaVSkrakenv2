class TaxaName:
    def __init__(self, id, name):
        self.id = id
        self.name = name

def search_taxa_id(taxa_el, id):
    return next((taxa for taxa in taxa_el if taxa.id == id), None)

def search_taxa_name(taxa_el, name):
    return next((taxa for taxa in taxa_el if taxa.name == name), None)

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
            while i >= 0 and line[i] == "NA":
                i -= 1

            if i < 0:
                continue
            print(line[i])
            taxa = search_taxa_id(taxa_el, line[0])

            if taxa is not None and (line[i] in taxa.name or taxa.name in line[i]):
                with open('matched_taxa.txt', 'a') as matched_file:
                    matched_file.write('\t'.join(line) + '\n')
            else:
                name_search = search_taxa_name(taxa_el, line[i])
                if name_search is not None:
                    line[0] = name_search.id
                    with open('matched_taxa.txt', 'a') as matched_file:
                        matched_file.write('\t'.join(line) + '\n')
                else:
                    with open('unmatched_taxa.txt', 'a') as unmatched_file:
                        unmatched_file.write('\t'.join(line) + '\n')




krakenFile="Kraken_agglom_otu_with_taxa.tsv"
taxaFile="formatted__names.tsv"

check_taxa_id(krakenFile,taxaFile)