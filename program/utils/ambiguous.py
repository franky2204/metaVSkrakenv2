def list_difference(lista1, lista2):
    return [nome for nome in lista1 if nome not in lista2]

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