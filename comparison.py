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

def compareFiles(metaObj,krakenObj):
        comparison_results = []
        meta_dict = {(obj.sample, obj.clade): obj for obj in metaObj}
        kraken_dict = {(obj.sample, obj.clade): obj for obj in krakenObj}

        all_keys = set(meta_dict.keys()).union(set(kraken_dict.keys()))

        for key in all_keys:
            meta_item = meta_dict.get(key)
            kraken_item = kraken_dict.get(key)

            if meta_item and kraken_item:
                comparison_results.append({
                    "sample": key[0],
                    "clade": key[1],
                    "meta_quantity": meta_item.quantity,
                    "kraken_quantity": kraken_item.quantity,
                    "difference": abs(meta_item.quantity - float(kraken_item.quantity))
                })
            elif meta_item:
                comparison_results.append({
                    "sample": key[0],
                    "clade": key[1],
                    "meta_quantity": meta_item.quantity,
                    "kraken_quantity": 0,
                    "difference": meta_item.quantity
                })
            elif kraken_item:
                comparison_results.append({
                    "sample": key[0],
                    "clade": key[1],
                    "meta_quantity": 0,
                    "kraken_quantity": kraken_item.quantity,
                    "difference": kraken_item.quantity
                })

        with open("comparison_results.txt", "w") as outfile:
            for result in comparison_results:
                outfile.write(f"{result['sample']}\t{result['clade']}\t{result['meta_quantity']}\t{result['kraken_quantity']}\t{result['difference']}\n")
     
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

compareFiles(metaObj,krakenObj)
#compareTotal(metaObj,krakenObj)


print(differenza_liste(mList,kList))