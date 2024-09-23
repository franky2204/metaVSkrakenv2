import csv
import re
path_to_meta = "metaResult/"
class Categorization:
    def __init__(self, tool, sample, depth,three ,name, clade, quantity, qtyWOU):
        self.tool = tool
        self.sample = sample
        self.depth = depth
        self.three =three
        self.name = name
        self.clade = clade#renaame inn taxaid
        self.quantity = quantity
        self.qtyWOU = qtyWOU

class meta_unknown:
    def __init__(self, sample, quantity):
        self.sample = sample
        self.quantity = quantity

def from_letter_to_taxa(letter):
    match letter:
        case "k":
            return "Kingdom"
        case "p":
            return "Phylum"
        case "c":
            return "Class"
        case "o":
            return "Order"
        case "f":
            return "Family"
        case "g":
            return "Genus"
        case "s":
            return "Species"
        case "t":
            return "Strain"
        case "_":
            return "Unknown"  #muda
def findClade(name_find):
    elements = name_find.split('|')
    last_element = elements[-1]
    if last_element == "":
        return -1
    return last_element

def extract_sample(header_line,n):
        header_line = header_line.readline().strip()
        header_elements = header_line.split('\t')
        sample_names = header_elements[n:] 
        return sample_names

def find_last_name(taxonomy_string):
    elements = taxonomy_string.split('|')
    last_element = elements[-1]
    letter, name = last_element.split('__')
    return letter, name

def createMetaObjects(file_path):
    categorization_list = []
    with open(file_path, 'r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        next(reader)
        sample_names = extract_sample(infile,1)
        sample_names = [name.replace("_output","") for name in sample_names]       
        unknown = extract_sample(infile,1)
        unknown = [float(value) for value in unknown]
        
        for i in range(len(sample_names)):
            file_to_open =path_to_meta+sample_names[i]+"_output.txt"
            with open(file_to_open, 'r') as file_single:
                for line_s in file_single:
                    if line_s.startswith("#") or line_s.startswith("UNCLASSIFIED"):
                        continue
                    else:
                        line_s = line_s.split('\t')
                        percentual = float(line_s[2])
                        letter,name=find_last_name(line_s[0])
                        categorization = Categorization("MetaPhlAn",
                                                         sample_names[i],
                                                         from_letter_to_taxa(letter),
                                                         re.sub(r'[a-zA-Z]__', '', line_s[0]),
                                                         name ,
                                                         findClade(line_s[1]),
                                                         (percentual/100),
                                                         ((percentual/(100-unknown[i])))) 
                        categorization_list.append(categorization)
    return sample_names,categorization_list  

def createKrakenObjects(file_path):
    categorization_list = []
    
    with open(file_path, 'r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        infile.seek(0)
        sample_names = extract_sample(infile,8)
        infile.seek(0)
        type_names = extract_sample(infile,0)
       # print(sample_names)

        for line_s in reader:
            percentual = line_s[8:]
            i = 7
            while line_s[i] == "NA":
                i -= 1
            letter=type_names[i]
            name = line_s[i]
            clade = line_s[0]
            three = ""
            n=0
            for n in range(1,i):
                 three= three+line_s[n]+"|"
            three=three+line_s[n+1]
            for n in range(len(sample_names)):
                if percentual[n] != "0":
                    categorization = Categorization("Kraken",
                                                 sample_names[n],
                                                 letter,
                                                 three,
                                                 name,
                                                 clade,
                                                 percentual[n],
                                                 percentual[n] ) 
                    categorization_list.append(categorization)
    return sample_names,categorization_list
def calculate_difference(meta_quantity, kraken_quantity):
    return (float(meta_quantity) - float(kraken_quantity))
def calculate_average(values):
    numeric_values = [float(value) for value in values]
    return sum(numeric_values) / len(numeric_values) if numeric_values else 0

def compareFiles(metaObj, krakenObj,naive):
    # Separate results based on sample, depth, and name for comparison
    depth_levels = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'Strain']
    
    with open("comparison_by_sample_depth_name.txt", "w") as sample_depth_file:
        sample_depth_file.write("Sample\tDepth\tTaxa_id\tTaxonomic Tree\tMetaPhlAn Quantity\tKraken Quantity\tDifference\n")
        for depth in depth_levels:
            for meta_cat in metaObj:
                if meta_cat.depth == depth and meta_cat.clade != -1 and meta_cat.sample not in naive:
                    corresponding_kraken = [k for k in krakenObj if k.sample == meta_cat.sample and k.clade == meta_cat.clade and k.depth == depth]
                    if corresponding_kraken:
                        kraken_cat = corresponding_kraken[0]
                        sample_depth_file.write(f"{meta_cat.sample}\t{depth}\t{meta_cat.clade}\t{meta_cat.three}\t{meta_cat.qtyWOU}\t{kraken_cat.quantity}\t{calculate_difference(meta_cat.qtyWOU,kraken_cat.quantity)}\n")
                    else:
                        sample_depth_file.write(f"{meta_cat.sample}\t{depth}\t{meta_cat.clade}\t{meta_cat.three}\t{meta_cat.quantity}\t0\n")

    # Calculate and compare averages for all clades between MetaPhlAn and Kraken, grouped by depth and name
    depth_name_quantities_meta = {depth: {} for depth in depth_levels}
    depth_name_quantities_kraken = {depth: {} for depth in depth_levels}
    
    # Collect MetaPhlAn quantities grouped by depth and name
    for meta_cat in metaObj:
        if meta_cat.name not in depth_name_quantities_meta[meta_cat.depth] or meta_cat.clade not in depth_name_quantities_meta[meta_cat.depth]:
            depth_name_quantities_meta[meta_cat.depth][meta_cat.clade] = []
        depth_name_quantities_meta[meta_cat.depth][meta_cat.clade].append(meta_cat.qtyWOU)
        
    # Collect Kraken quantities grouped by depth and name
    for kraken_cat in krakenObj:
        if kraken_cat.name not in depth_name_quantities_kraken[kraken_cat.depth]:
            depth_name_quantities_kraken[kraken_cat.depth][kraken_cat.clade] = []
        depth_name_quantities_kraken[kraken_cat.depth][kraken_cat.clade].append(kraken_cat.quantity)

    with open("average_clade_comparison_by_name.txt", "w") as avg_clade_file:
        avg_clade_file.write("Depth\tTaxaid\tTaxonomic Tree\tMetaPhlAn Average\tKraken Average\n")
        for depth in depth_levels :
            all_names = set(depth_name_quantities_meta[depth].keys()).union(set(depth_name_quantities_kraken[depth].keys()))
            for clade in all_names:
                if  clade!= -1:
                    avg_meta = calculate_average(depth_name_quantities_meta[depth].get(clade, []))
                    avg_kraken = calculate_average(depth_name_quantities_kraken[depth].get(clade, []))
                    example_meta = next((meta_cat for meta_cat in metaObj if meta_cat.clade == clade and meta_cat.depth == depth), None)
                    example_kraken = next((kraken_cat for kraken_cat in krakenObj if kraken_cat.clade == clade and kraken_cat.depth == depth), None)
                    taxonomic_tree = example_meta.three if example_meta else (example_kraken.three if example_kraken else "")
                    avg_clade_file.write(f"{depth}\t{clade}\t{taxonomic_tree}\t{avg_meta}\t{avg_kraken}\t{calculate_difference(avg_meta,avg_kraken)}\n")


def differenza_liste(lista1, lista2):
    # Restituisce i nomi presenti in lista1 ma non in lista2
    return [nome for nome in lista1 if nome not in lista2]


krakenFile="kraken_taxa.tsv"
metaFile = "meta_table.tsv"
mList,metaObj=createMetaObjects(metaFile)
kList,krakenObj=createKrakenObjects(krakenFile)

with open("categorization_list.txt", "w") as outfile:
                for categorization in metaObj:
                    outfile.write(f"{categorization.tool}\t{categorization.sample}\t{categorization.depth}\t{categorization.three}\t{categorization.name}\t{categorization.clade}\t{categorization.quantity}\t{categorization.qtyWOU}\n")


with open("kraken_list.txt", "w") as outfile:
                for categorization in krakenObj:
                    outfile.write(f"{categorization.tool}\t{categorization.sample}\t{categorization.depth}\t{categorization.three}\t{categorization.name}\t{categorization.clade}\t{categorization.quantity}\t{categorization.qtyWOU}\n")
naive=differenza_liste(mList,kList)
compareFiles(metaObj,krakenObj,naive)
#compareTotal(metaObj,krakenObj)


