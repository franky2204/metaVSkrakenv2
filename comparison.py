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
class mean_data:
    def __init__(self,three, depth, clade, quantity, status):
        self.three = three
        self.depth = depth
        self.clade = clade
        self.quantity = quantity
        self.status = status
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
def createMean(metaObj, ms_samples, naive):
    samples_list=""
    mean_list_healty = []
    mean_list_ms = []
    for meta_cat in metaObj:
        status = "MS" if meta_cat.sample in ms_samples else "HEALTY"
        if status == "HEALTY":
            if meta_cat.sample not in naive and meta_cat.clade != -1:
                existing_mean = next((mean for mean in mean_list_healty if mean.three == meta_cat.three), None)
                if existing_mean is None:
                    samples_list=samples_list+meta_cat.sample
                    meanObj = mean_data(meta_cat.three, meta_cat.depth, meta_cat.clade,float(meta_cat.qtyWOU), status)
                    mean_list_healty.append(meanObj)
                else:
                    existing_mean.quantity += float(meta_cat.qtyWOU)
        else :
            if meta_cat.sample not in naive and meta_cat.clade != -1:
                existing_mean = next((mean for mean in mean_list_ms if mean.three == meta_cat.three), None)
                if existing_mean is None:
                    meanObj = mean_data(meta_cat.three, meta_cat.depth, meta_cat.clade, float(meta_cat.qtyWOU), status)
                    mean_list_ms.append(meanObj)
                else:
                    existing_mean.quantity += float(meta_cat.qtyWOU)
    print(samples_list)
    return mean_list_healty, mean_list_ms

def printComparison(metaMeanList,krakenMeanList,healty_samples_count,ms_samples_count,naive):
    with open("Healty.txt", "w") as healty_samples, \
         open("MS.txt", "w") as MS_samples:

        # Scrivi gli header
        createTemplate1(healty_samples, "MetaPhlAn")
        createTemplate1(healty_samples, "Kraken")
        createTemplate1(MS_samples, "MetaPhlAn")
        createTemplate1(MS_samples, "Kraken")

        # Calcola le medie e scrivi i risultati nei file
        for meanObj in metaMeanList:
            meanObj.quantity /= healty_samples_count if meanObj.status == "HEALTY" else ms_samples_count
            if meanObj.status == "HEALTY":
                healty_samples.write(f"{meanObj.depth}\t{meanObj.clade}\t{meanObj.quantity}\n")
            else:
                MS_samples.write(f"{meanObj.depth}\t{meanObj.clade}\t{meanObj.quantity}\n")

        for meanObj in krakenMeanList:
            meanObj.quantity /= healty_samples_count if meanObj.status == "HEALTY" else ms_samples_count
            if meanObj.status == "HEALTY":
                healty_samples.write(f"{meanObj.depth}\t{meanObj.clade}\t{meanObj.quantity}\n")
            else:
                MS_samples.write(f"{meanObj.depth}\t{meanObj.clade}\t{meanObj.quantity}\n")

#def printMean(meta_dict, kraken_dict, healty_samples_count, ms_samples_count, naive):
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

        # Raggruppa e somma i valori per clade per MetaPhlAn e Kraken
        for key, meta_cat in meta_dict.items():
            clade = meta_cat.clade
            sample_name = meta_cat.sample
            is_ms = ("MS" in sample_name or "MAV" in sample_name or "TEC" in sample_name)and sample_name not in naive

            # Somma i valori per MetaPhlAn
            if clade not in meta_sums:
                meta_sums[clade] = 0
            meta_sums[clade] += float(meta_cat.qtyWOU)

            if key in kraken_dict:
                kraken_cat = kraken_dict[key]

                # Somma i valori per Kraken
                if clade not in kraken_sums:
                    kraken_sums[clade] = 0
                kraken_sums[clade] += float(kraken_cat.quantity)

        # Calcola le medie e scrivi i risultati nei file
        for clade in meta_sums:
            meta_mean_qtyWOU = meta_sums[clade] / (ms_samples_count if is_ms else healty_samples_count)
            kraken_mean_quantity = kraken_sums.get(clade, 0) / (ms_samples_count if is_ms else healty_samples_count)
            
            if is_ms:
                MS_samples.write(f"{meta_cat.depth}\t{meta_cat.clade}\t{meta_cat.three}\t"
                                 f"{meta_mean_qtyWOU}\t{kraken_mean_quantity}\t"
                                 f"{meta_mean_qtyWOU/kraken_mean_quantity if kraken_mean_quantity != 0 else 0}\n")
            else:
                healty_samples.write(f"{meta_cat.depth}\t{meta_cat.clade}\t{meta_cat.three}\t"
                                     f"{meta_mean_qtyWOU}\t{kraken_mean_quantity}\t"
                                     f"{meta_mean_qtyWOU/kraken_mean_quantity if kraken_mean_quantity != 0 else 0}\n")

            # Scrivi anche i file separati per MetaPhlAn e Kraken
            if is_ms:
                MS_metaphlan.write(f"{meta_cat.depth}\t{meta_cat.clade}\t{meta_cat.three}\t{meta_mean_qtyWOU}\n")
                if clade in kraken_sums:
                    MS_kraken.write(f"{meta_cat.depth}\t{meta_cat.clade}\t{meta_cat.three}\t{kraken_mean_quantity}\n")
            else:
                healty_metaphlan.write(f"{meta_cat.depth}\t{meta_cat.clade}\t{meta_cat.three}\t{meta_mean_qtyWOU}\n")
                if clade in kraken_sums:
                    healty_kraken.write(f"{meta_cat.depth}\t{meta_cat.clade}\t{meta_cat.three}\t{kraken_mean_quantity}\n")

     
       
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
samples_list = len(mList) - len(naive)
ms_samples = [sample for sample in mList if "MS" in sample or "MAV" in sample or "TEC" in sample]
non_naive_non_ms_samples = [sample for sample in mList if sample not in naive and sample not in ms_samples]
healty_samples_count = len(non_naive_non_ms_samples)
print(healty_samples_count)
metaMeanListHealty, metaMeanListMS=createMean(metaObj,ms_samples,naive)
krakenMeanListHealty, krakenMeanListMS=createMean(krakenObj,ms_samples,naive)

with open("metaMeanListHealty.txt", "w") as file:
    for item in metaMeanListHealty:
        file.write(f"{item.three}\t{item.depth}\t{item.clade}\t{item.quantity}\t{item.status}\n")

with open("metaMeanListMS.txt", "w") as file:
    for item in metaMeanListMS:
        file.write(f"{item.three}\t{item.depth}\t{item.clade}\t{item.quantity}\t{item.status}\n")

with open("krakenMeanListHealty.txt", "w") as file:
    for item in krakenMeanListHealty:
        file.write(f"{item.three}\t{item.depth}\t{item.clade}\t{item.quantity}\t{item.status}\n")

with open("krakenMeanListMS.txt", "w") as file:
    for item in krakenMeanListMS:
        file.write(f"{item.three}\t{item.depth}\t{item.clade}\t{item.quantity}\t{item.status}\n")
#printComparison(metaMeanList,krakenMeanList,healty_samples_count,samples_list- healty_samples_count,naive)
#compareTotal(metaObj,krakenObj)
#healty_samples_count,samples_list- healty_samples_count,naive

