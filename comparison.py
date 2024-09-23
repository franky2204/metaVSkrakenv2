import csv
import re
path_to_meta = "metaResult/"
neg_pos="REF1","BLANK"
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

def compareFiles(metaObj, krakenObj, naive, level):
    # Define depth levels for comparison
    depth_levels = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'Strain']
    
    # Create dictionaries for faster lookup, key = (sample, clade, depth)
    meta_dict = {}
    kraken_dict = {}
    if level != "NA":
        for meta_cat in metaObj:
            if meta_cat.sample not in naive and meta_cat.clade != -1 and meta_cat.depth ==level:  
                key = (meta_cat.sample, meta_cat.clade, meta_cat.depth)
                meta_dict[key] = meta_cat

        for kraken_cat in krakenObj:
            if kraken_cat.depth == level:
                key = (kraken_cat.sample, kraken_cat.clade, kraken_cat.depth)
                kraken_dict[key] = kraken_cat
    else:
        for meta_cat in metaObj:
            if meta_cat.sample not in naive and meta_cat.clade != -1:  
                key = (meta_cat.sample, meta_cat.clade, meta_cat.depth)
                meta_dict[key] = meta_cat

        for kraken_cat in krakenObj:
            key = (kraken_cat.sample, kraken_cat.clade, kraken_cat.depth)
            kraken_dict[key] = kraken_cat

    return meta_cat,kraken_cat,meta_dict,kraken_dict
   

def createPerSampleFile(meta_cat,kraken_cat,meta_dict,kraken_dict):
    with open("sample_comparison.txt", "w") as sample_depth_file, \
         open("sample_only_kraken.txt", "w") as sample_kraken, \
         open("sample_only_meta.txt", "w") as sample_meta:
        
        sample_depth_file.write("Sample\tTaxa_id\tTaxonomic_Tree\tMetaPhlAn\tKraken\tMeta/Kraken\n")
        sample_kraken.write("Sample\tTaxa_id\tTaxonomic_Tree\tKraken_Quantity\n")
        sample_meta.write("Sample\tTaxa_id\tTaxonomic_Tree\tMetaPhlAn_Quantity\n")

        for key, meta_cat in meta_dict.items():
            if key in kraken_dict:
                kraken_cat = kraken_dict[key]
                sample_depth_file.write(
                    f"{meta_cat.sample}\t{meta_cat.clade}\t{meta_cat.three}\t"
                    f"{meta_cat.qtyWOU}\t{kraken_cat.quantity}\t{(float(meta_cat.qtyWOU)/float(kraken_cat.quantity))}\n"
                )
            else:
                sample_meta.write(
                    f"{meta_cat.sample}\t{meta_cat.clade}\t{meta_cat.three}\t{meta_cat.quantity}\n"
                )

        for key, kraken_cat in kraken_dict.items():
            if key not in meta_dict:
                sample_kraken.write(
                    f"{kraken_cat.sample}\t{kraken_cat.clade}\t{kraken_cat.three}\t{kraken_cat.quantity}\n"
                )
def createMean(meta_dict, kraken_dict):
    total_samples = 76  # Numero totale di campioni per calcolare la media
    
    # Dizionari per sommare le quantità dei clade per MetaPhlAn e Kraken
    meta_sums = {}
    kraken_sums = {}
    
    with open("Healty_both.txt", "w") as healty_samples, \
         open("Healty_kraken.txt", "w") as healty_kraken, \
         open("Healty_metaphlan.txt", "w") as healty_metaphlan, \
         open("MS_both.txt", "w") as MS_samples, \
         open("MS_kraken.txt", "w") as MS_kraken, \
         open("MS_metaphlan.txt", "w") as MS_metaphlan:
        
        # Scrivi gli header
        createTemplate2(healty_samples)
        createTemplate1(healty_kraken, "kraken")
        createTemplate1(healty_metaphlan, "metaphlan")
        createTemplate2(MS_samples)
        createTemplate1(MS_kraken, "kraken")
        createTemplate1(MS_metaphlan, "metaphlan")

        # Raggruppa i risultati per campioni
        for key, meta_cat in meta_dict.items():
            sample_name = meta_cat.sample
            is_ms = "MS" in sample_name or "MAV" in sample_name or "TEC" in sample_name
            
            if key in kraken_dict:
                kraken_cat = kraken_dict[key]
                # Se presente sia in MetaPhlAn che in Kraken, somma i valori per la media
                if key not in meta_sums:
                    meta_sums[key] = [0, 0]  # [MetaPhlAn somma, numero campioni]
                    kraken_sums[key] = [0, 0]  # [Kraken somma, numero campioni]

                meta_sums[key][0] += float(meta_cat.qtyWOU)
                kraken_sums[key][0] += float(kraken_cat.quantity)
                meta_sums[key][1] += 1
                kraken_sums[key][1] += 1

                # Se presente sia in MetaPhlAn che in Kraken, scrivi nel file appropriato
                if is_ms:
                    MS_samples.write(f"{meta_cat.depth}\t{meta_cat.clade}\t{meta_cat.three}\t"
                                     f"{meta_cat.qtyWOU}\t{kraken_cat.quantity}\t{float(meta_cat.qtyWOU)/float(kraken_cat.quantity)}\n")
                else:
                    healty_samples.write(f"{meta_cat.depth}\t{meta_cat.clade}\t{meta_cat.three}\t"
                                         f"{meta_cat.qtyWOU}\t{kraken_cat.quantity}\t{float(meta_cat.qtyWOU)/float(kraken_cat.quantity)}\n")
            else:
                # Presente solo in MetaPhlAn
                if is_ms:
                    MS_metaphlan.write(f"{meta_cat.depth}\t{meta_cat.clade}\t{meta_cat.three}\t{meta_cat.qtyWOU}\n")
                else:
                    healty_metaphlan.write(f"{meta_cat.depth}\t{meta_cat.clade}\t{meta_cat.three}\t{meta_cat.qtyWOU}\n")

        # Processa i campioni presenti solo in Kraken
        for key, kraken_cat in kraken_dict.items():
            if key not in meta_dict:
                sample_name = kraken_cat.sample
                is_ms = "MS" in sample_name or "MAV" in sample_name or "TEC" in sample_name
                if key not in kraken_sums:
                    kraken_sums[key] = [0, 0]
                kraken_sums[key][0] += float(kraken_cat.quantity)
                kraken_sums[key][1] += 1

                if is_ms:
                    MS_kraken.write(f"{kraken_cat.depth}\t{kraken_cat.clade}\t{kraken_cat.three}\t{kraken_cat.quantity}\n")
                else:
                    healty_kraken.write(f"{kraken_cat.depth}\t{kraken_cat.clade}\t{kraken_cat.three}\t{kraken_cat.quantity}\n")

        # Scrivi le medie nei file
        for key in meta_sums:
            meta_mean = meta_sums[key][0] / total_samples
            kraken_mean = kraken_sums[key][0] / total_samples if key in kraken_sums else 0

            sample_name = meta_dict[key].sample
            is_ms = "MS" in sample_name or "MAV" in sample_name or "TEC" in sample_name

            if is_ms:
                MS_samples.write(f"{meta_dict[key].depth}\t{meta_dict[key].clade}\t{meta_dict[key].three}\t"
                                 f"{meta_mean}\t{kraken_mean}\n")
            else:
                healty_samples.write(f"{meta_dict[key].depth}\t{meta_dict[key].clade}\t{meta_dict[key].three}\t"
                                     f"{meta_mean}\t{kraken_mean}\n")

        
       
def createTemplate1(file,tool):
    file.write(f"Depth\tTaxa_id\tTaxonomic_Tree\t{tool}_mean\n")   
def createTemplate2(file):
    file.write("Depth\tTaxa_id\tTaxonomic_Tree\tMetaPhlAn_mean\tKraken_mean\tMetaphlan/Kraken\n")

def list_difference(lista1, lista2):
    return [nome for nome in lista1 if nome not in lista2]


krakenFile="kraken_taxa.tsv"
metaFile = "meta_table.tsv"
mList,metaObj=createMetaObjects(metaFile)
kList,krakenObj=createKrakenObjects(krakenFile)


print(f"Length of metaObj: {len(metaObj) }")
print(f"Length of krakenObj: {len(krakenObj)}")
naive=list_difference(mList,kList)
meta_species_count = sum(1 for meta_cat in metaObj if meta_cat.depth == "Species" and meta_cat.clade != -1 and meta_cat.sample not in naive)
kraken_species_count = sum(1 for kraken_cat in krakenObj if kraken_cat.depth == "Species")

print(f"Number of elements in metaObj with depth == 'Species': {meta_species_count}")
print(f"Number of elements in krakenObj with depth == 'Species': {kraken_species_count}")
meta_cat,kraken_cat,meta_dict,kraken_dict= compareFiles(metaObj,krakenObj,naive,"Species")
createPerSampleFile(meta_cat,kraken_cat,meta_dict,kraken_dict)
naive = naive + list(neg_pos)
print(naive)
meta_cat_mean,kraken_cat_mean,meta_dict_mean,kraken_dict_mean= compareFiles(metaObj,krakenObj,naive,"NA")
createMean(meta_dict_mean,kraken_dict_mean)
#compareTotal(metaObj,krakenObj)


