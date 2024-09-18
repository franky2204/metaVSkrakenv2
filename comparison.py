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
        self.clade = clade
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
                        categorization = Categorization("MetaPhlAn", sample_names[i], from_letter_to_taxa(letter),re.sub(r'[a-zA-Z]__', '', line_s[0]),name ,findClade(line_s[1]) ,percentual, ((percentual/(100-unknown[i]))*100)) 
                        categorization_list.append(categorization)
            # Write categorization_list to a file
    return categorization_list  

def createKrakenObjects(file_path):
    categorization_list = []
    
    with open(file_path, 'r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        infile.seek(0)
        sample_names = extract_sample(infile,8)
        print(sample_names)

        for line_s in reader:
            percentual = line_s[8:]
            letter="Species"
            name = line_s[7]
            clade = line_s[0]
            three=""
            for i in range(1,7):
                 three= three+line_s[i]+"|"
            three=three+line_s[i+1]
            for n in range(len(sample_names)):
                categorization = Categorization("Kraken",
                                                 sample_names[n],
                                                 letter,
                                                 three,
                                                 name,
                                                 clade,
                                                 percentual[n],
                                                 percentual[n] ) 
                categorization_list.append(categorization)
    return categorization_list




krakenFile="Kraken_otu.tsv"
metaFile = "meta_table.tsv"
metaObj=createMetaObjects(metaFile)
krakenObj=createKrakenObjects(krakenFile)

with open("categorization_list.txt", "w") as outfile:
                for categorization in metaObj:
                    outfile.write(f"{categorization.tool}\t{categorization.sample}\t{categorization.depth}\t{categorization.three}\t{categorization.name}\t{categorization.clade}\t{categorization.quantity}\t{categorization.qtyWOU}\n")


with open("kraken_list.txt", "w") as outfile:
                for categorization in krakenObj:
                    outfile.write(f"{categorization.tool}\t{categorization.sample}\t{categorization.depth}\t{categorization.three}\t{categorization.name}\t{categorization.clade}\t{categorization.quantity}\t{categorization.qtyWOU}\n")