import csv
import re
import utils.classesEl as classesEl
import utils.readFileFunct as readFileFunct
import utils.ambiguous as ambiguous

#path to the meta files(absolute)
path_to_meta = "metaResult/"

#create a list of objects from the kraken file
def createKrakenObjects(file_path):
    categorization_list = []
    
    with open(file_path, 'r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        infile.seek(0)
        sample_names = readFileFunct.extract_sample(infile,8)
        infile.seek(0)
        type_names = readFileFunct.extract_sample(infile,0)

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
                    categorization = classesEl.Categorization("Kraken",
                                                 sample_names[n],
                                                 letter,
                                                 three,
                                                 name,
                                                 clade,
                                                 percentual[n],
                                                 percentual[n] ) 
                    categorization_list.append(categorization)
    return sample_names,categorization_list
#create a list of objects from the meta file
def createMetaObjects(file_path,archaea,eukaryota):
    categorization_list = []
    with open(file_path, 'r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        next(reader)
        sample_names = readFileFunct.extract_sample(infile,1)
        sample_names = [name.replace("_output","") for name in sample_names]       
        unknown = readFileFunct.extract_sample(infile,1)
        unknown = [float(value) for value in unknown]      
        for i in range(len(sample_names)):
            file_to_open =path_to_meta+sample_names[i]+"_output.txt"
            with open(file_to_open, 'r') as file_single:
                for line_s in file_single:
                    if line_s.startswith("#") or line_s.startswith("UNCLASSIFIED") or line_s.startswith("k__Eukaryota") or line_s.startswith("k__Archaea"):
                        continue
                    else:
                        line_s = line_s.split('\t')
                        percentual = float(line_s[2])
                        letter,name=readFileFunct.find_last_name(line_s[0])
                        categorization = classesEl.Categorization("MetaPhlAn",
                                                         sample_names[i],
                                                         ambiguous.from_letter_to_taxa(letter),
                                                         re.sub(r'[a-zA-Z]__', '', line_s[0]),
                                                         name ,
                                                         readFileFunct.findClade(line_s[1]),
                                                         (percentual/100),
                                                         ((percentual/(100-(unknown[i]+archaea[i]+eukaryota[i]))))) 
                        categorization_list.append(categorization)
    return sample_names,categorization_list  
#creates a new list with the sum of the varius taxid from the list created by createMetaObjects or createKrakenObjects
def createMean(metaObj, ms_samples, naive):
    mean_list_healty = []
    mean_list_ms = []
    mean_all = []
    for meta_cat in metaObj:
        status = "MS" if meta_cat.sample in ms_samples else "HEALTY"
        if status == "HEALTY":
            if meta_cat.sample not in naive and meta_cat.clade != -1:
                existing_mean = next((mean for mean in mean_list_healty if mean.three == meta_cat.three), None)
                if existing_mean is None:
                    meanObj = classesEl.mean_data(meta_cat.three, meta_cat.depth, meta_cat.clade,float(meta_cat.qtyWOU), status)
                    mean_list_healty.append(meanObj)
                else:
                    existing_mean.quantity += float(meta_cat.qtyWOU)
        else :
            if meta_cat.sample not in naive and meta_cat.clade != -1:
                existing_mean = next((mean for mean in mean_list_ms if mean.three == meta_cat.three), None)
                if existing_mean is None:
                    meanObj = classesEl.mean_data(meta_cat.three, meta_cat.depth, meta_cat.clade, float(meta_cat.qtyWOU), status)
                    mean_list_ms.append(meanObj)
                else:
                    existing_mean.quantity += float(meta_cat.qtyWOU)
        existing_mean_all = next((mean for mean in mean_all if mean.three == meta_cat.three), None)
        if meta_cat.sample not in naive and meta_cat.clade != -1:
            if existing_mean_all is None:
                meanObj = classesEl.mean_data(meta_cat.three, meta_cat.depth, meta_cat.clade, float(meta_cat.qtyWOU), "Both")
                mean_all.append(meanObj)
            else:
                existing_mean_all.quantity += float(meta_cat.qtyWOU)
    return mean_list_healty, mean_list_ms, mean_all
