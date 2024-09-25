import utils.createObject as createObject
import utils.writeFileFunct as writeFileFunct
import utils.ambiguous as ambiguous
#the two input files
krakenFile="/home/francesco/Desktop/git/mine/metaVSkrakenv2/input/kraken_taxa.tsv"
metaFile = "/home/francesco/Desktop/git/mine/metaVSkrakenv2/input/meta_table.tsv"
#creates the objects for confrontation(see description in createObject.py)
mList,metaObj=createObject.createMetaObjects(metaFile)
kList,krakenObj=createObject.createKrakenObjects(krakenFile)

#this two samples are not considered in the second and third confrontation
neg_pos="REF1","BLANK"

print(f"Length of metaObj: {len(metaObj) }")
print(f"Length of krakenObj: {len(krakenObj)}")

#find if there are more sample in metaObj or in krakenObj
naive=ambiguous.list_difference(mList,kList)
#count the number of species found in metaObj and krakenObj with depth == 'Species'
meta_species_count = sum(1 for meta_cat in metaObj if meta_cat.depth == "Species" and meta_cat.clade != -1 and meta_cat.sample not in naive)
kraken_species_count = sum(1 for kraken_cat in krakenObj if kraken_cat.depth == "Species")

print(f"Number of elements in metaObj with depth == 'Species': {meta_species_count}")
print(f"Number of elements in krakenObj with depth == 'Species': {kraken_species_count}")
meta_cat,kraken_cat,meta_dict,kraken_dict= ambiguous.compareFiles(metaObj,krakenObj,naive,"Species")
#write file with comparison between meta and kraken values divided by sample name and only wit depth == 'Species'
#note in this comparison negative and positive samples are taken into account 
writeFileFunct.createPerSampleFile(meta_cat,kraken_cat,meta_dict,kraken_dict)
naive = naive + list(neg_pos)
print(naive)
meta_cat_mean,kraken_cat_mean,meta_dict_mean,kraken_dict_mean= ambiguous.compareFiles(metaObj,krakenObj,naive,"NA")
samples_list = len(mList) - len(naive)
ms_samples = [sample for sample in mList if "MS" in sample or "MAV" in sample or "TEC" in sample]
non_naive_non_ms_samples = [sample for sample in mList if sample not in naive and sample not in ms_samples]
healty_samples_count = len(non_naive_non_ms_samples)
print(healty_samples_count)
#creates the list needed for the two following functions 
metaMeanListHealty, metaMeanListMS, together_meta=writeFileFunct.createMean(metaObj,ms_samples,naive)
krakenMeanListHealty, krakenMeanListMS, together_kraken=writeFileFunct.createMean(krakenObj,ms_samples,naive)
#write file with comparison between meta and kraken mean values NOT divided by healty and ms
writeFileFunct.comparePerDiv2(together_meta,together_kraken,samples_list)
#write file with comparison between meta and kraken mean values divided by healty and ms
writeFileFunct.comparePercent(metaMeanListHealty, metaMeanListMS, krakenMeanListHealty, krakenMeanListMS, healty_samples_count, samples_list - healty_samples_count)