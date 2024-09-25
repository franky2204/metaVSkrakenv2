import os
import sys
sys.path.append(os.path.abspath("/home/francesco/Desktop/git/mine/metaVSkrakenv2/program/utils"))
import createObject
import writeFileFunct
import ambiguous
krakenFile="/home/francesco/Desktop/git/mine/metaVSkrakenv2/program/input/kraken_taxa.tsv"
metaFile = "/home/francesco/Desktop/git/mine/metaVSkrakenv2/program/input/meta_table.tsv"
mList,metaObj=createObject.createMetaObjects(metaFile)
kList,krakenObj=createObject.createKrakenObjects(krakenFile)

path_output="output/"
neg_pos="REF1","BLANK"
print(f"Length of metaObj: {len(metaObj) }")
print(f"Length of krakenObj: {len(krakenObj)}")

naive=ambiguous.list_difference(mList,kList)
meta_species_count = sum(1 for meta_cat in metaObj if meta_cat.depth == "Species" and meta_cat.clade != -1 and meta_cat.sample not in naive)
kraken_species_count = sum(1 for kraken_cat in krakenObj if kraken_cat.depth == "Species")

print(f"Number of elements in metaObj with depth == 'Species': {meta_species_count}")
print(f"Number of elements in krakenObj with depth == 'Species': {kraken_species_count}")

meta_cat,kraken_cat,meta_dict,kraken_dict= ambiguous.compareFiles(metaObj,krakenObj,naive,"Species")
writeFileFunct.createPerSampleFile(meta_cat,kraken_cat,meta_dict,kraken_dict)
naive = naive + list(neg_pos)
print(naive)
meta_cat_mean,kraken_cat_mean,meta_dict_mean,kraken_dict_mean= ambiguous.compareFiles(metaObj,krakenObj,naive,"NA")
samples_list = len(mList) - len(naive)
ms_samples = [sample for sample in mList if "MS" in sample or "MAV" in sample or "TEC" in sample]
non_naive_non_ms_samples = [sample for sample in mList if sample not in naive and sample not in ms_samples]
healty_samples_count = len(non_naive_non_ms_samples)
print(healty_samples_count)
metaMeanListHealty, metaMeanListMS, together_meta=writeFileFunct.createMean(metaObj,ms_samples,naive)
krakenMeanListHealty, krakenMeanListMS, together_kraken=writeFileFunct.createMean(krakenObj,ms_samples,naive)
writeFileFunct.comparePerDiv2(together_meta,together_kraken,samples_list)
writeFileFunct.comparePercent(metaMeanListHealty, metaMeanListMS, krakenMeanListHealty, krakenMeanListMS, healty_samples_count, samples_list - healty_samples_count)