import os
import utils.classesEl as classesEl
#absolute path for the output files
path_output="/home/francesco/Desktop/git/mine/metaVSkrakenv2/output/"
#creates the output directory if it does not exist 
def setOutputFile(file_name):
    if not os.path.exists(path_output):
        os.makedirs(path_output)
    return path_output+file_name
#write template for the output files
def createTemplate1(file,tool):
    file.write(f"Depth\tTaxa_id\tTaxonomic_Tree\t{tool}_mean\n")

def createTemplate2(file):
    file.write("Depth\tTaxa_id\tTaxonomic_Tree\tMetaPhlAn_mean\tKraken_mean\tMetaphlan/Kraken(%)\n")
#print output files with comparison between meta and kraken values 
#divided by sample name and only wit depth == 'Species'
def createPerSampleFile(meta_cat,kraken_cat,meta_dict,kraken_dict):
    with open(setOutputFile("single_sample_comparison.txt"), "w") as sample_depth_file, \
         open(setOutputFile("single_sample_only_kraken.txt"), "w") as sample_kraken, \
         open(setOutputFile("single_sample_only_meta.txt"), "w") as sample_meta:
        
        sample_depth_file.write("Sample\tTaxa_id\tTaxonomic_Tree\tMetaPhlAn\tKraken\tMeta/Kraken\n")
        sample_kraken.write("Sample\tTaxa_id\tTaxonomic_Tree\tKraken_Quantity\n")
        sample_meta.write("Sample\tTaxa_id\tTaxonomic_Tree\tMetaPhlAn_Quantity\n")
        #use of key for faster lookup, first loop for meta data(only meta and both meta+kraken)
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
        #second loop for kraken data(only kraken)
        for key, kraken_cat in kraken_dict.items():
            if key not in meta_dict:
                sample_kraken.write(
                    f"{kraken_cat.sample}\t{kraken_cat.clade}\t{kraken_cat.three}\t{kraken_cat.quantity}\n"
                )
#creates 6 lists two for comparison between meta and kraken mean values NOT divided by healty and ms 
#and the other four divided by healty and ms
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
#write output files with comparison between meta and kraken mean values divided by healty and ms
def comparePercent (metaMeanListHealty, metaMeanListMS, krakenMeanListHealty, krakenMeanListMS, healty_samples_count, MS_samples_count) :

    with open(setOutputFile("mean_Healty_both.txt"), "w") as healty_samples, \
         open(setOutputFile("mean_Healty_kraken.txt"), "w") as healty_kraken, \
         open(setOutputFile("mean_Healty_metaphlan.txt"), "w") as healty_metaphlan, \
         open(setOutputFile("mean_MS_both.txt"), "w") as MS_samples, \
         open(setOutputFile("mean_MS_kraken.txt"), "w") as MS_kraken, \
         open(setOutputFile("mean_MS_metaphlan.txt"), "w") as MS_metaphlan:

        createTemplate2(healty_samples)
        createTemplate1(healty_kraken, "kraken")
        createTemplate1(healty_metaphlan, "metaphlan")
        createTemplate2(MS_samples)
        createTemplate1(MS_kraken, "kraken")
        createTemplate1(MS_metaphlan, "metaphlan")

        for metaMean in metaMeanListHealty:
            krakenMean = next((km for km in krakenMeanListHealty if km.clade == metaMean.clade), None)
            if krakenMean:
                healty_samples.write(
                    f"{metaMean.depth}\t{metaMean.clade}\t{metaMean.three}\t"
                    f"{metaMean.quantity/healty_samples_count}\t"
                    f"{krakenMean.quantity/healty_samples_count}\t"
                    f"{round((metaMean.quantity / krakenMean.quantity)*100,2)}\n"
                )
            else:
                healty_metaphlan.write(f"{metaMean.depth}\t{metaMean.clade}\t{metaMean.three}\t{metaMean.quantity/healty_samples_count}\n")
        
        for krakenMean in krakenMeanListHealty:
            metaMean = next((mm for mm in metaMeanListHealty if mm.clade == krakenMean.clade), None)
            if not metaMean:
                healty_kraken.write(f"{krakenMean.depth}\t{krakenMean.clade}\t{krakenMean.three}\t{krakenMean.quantity/healty_samples_count}\n")

        for metaMean in metaMeanListMS:
            krakenMean = next((km for km in krakenMeanListMS if km.clade == metaMean.clade), None)
            if krakenMean:
                MS_samples.write(
                    f"{metaMean.depth}\t{metaMean.clade}\t{metaMean.three}\t"
                    f"{metaMean.quantity/MS_samples_count}\t"
                    f"{krakenMean.quantity/MS_samples_count}\t"
                    f"{round((metaMean.quantity / krakenMean.quantity)*100,2)}\n"
                )
            else:
                MS_metaphlan.write(f"{metaMean.depth}\t{metaMean.clade}\t{metaMean.three}\t{metaMean.quantity/MS_samples_count}\n")
        
        for krakenMean in krakenMeanListMS:
            metaMean = next((mm for mm in metaMeanListMS if mm.clade == krakenMean.clade), None)
            if not metaMean:
                MS_kraken.write(f"{krakenMean.depth}\t{krakenMean.clade}\t{krakenMean.three}\t{krakenMean.quantity/MS_samples_count}\n")
#write output files with comparison between meta and kraken mean values NOT divided by healty and ms
def comparePerDiv2(meta, kraken, samples_list):

    with open(setOutputFile("mean_all_both.txt"), "w") as comparison_both, \
         open(setOutputFile("mean_all_only_meta.txt"), "w") as comparison_only_meta, \
         open(setOutputFile("mean_all_only_kraken.txt"), "w") as comparison_only_kraken:
        
        createTemplate2(comparison_both)
        createTemplate1(comparison_only_meta, "metaphlan")
        createTemplate1(comparison_only_kraken, "kraken")

        for meta_el in meta:
            kraken_el = next((k for k in kraken if k.clade == meta_el.clade), None)
            if kraken_el:
                comparison_both.write(
                    f"{meta_el.depth}\t{meta_el.clade}\t{meta_el.three}\t"
                    f"{meta_el.quantity/samples_list}\t"
                    f"{kraken_el.quantity/samples_list}\t"
                    f"{round((meta_el.quantity / kraken_el.quantity)*100,2)}\n"
                )
            else:
                comparison_only_meta.write(f"{meta_el.depth}\t{meta_el.clade}\t{meta_el.three}\t{meta_el.quantity/samples_list}\n")
        
        for kraken_el in kraken:
            meta_el = next((m for m in meta if m.clade == kraken_el.clade), None)
            if not meta_el:
                comparison_only_kraken.write(f"{kraken_el.depth}\t{kraken_el.clade}\t{kraken_el.three}\t{kraken_el.quantity/samples_list}\n")
