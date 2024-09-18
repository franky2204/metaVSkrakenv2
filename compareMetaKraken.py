import csv

def scientific_to_decimal(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile, delimiter='\t')
        writer = csv.writer(outfile, delimiter='\t')
        
        for row in reader:
            new_row = []
            for item in row:
                try:
                    num = float(item)
                    new_row.append('{:.20f}'.format(num).rstrip('0').rstrip('.'))
                except ValueError: 
                    new_row.append(item)
            writer.writerow(new_row)

def meta_only_speaces(input_file, output_file):

    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile, delimiter='\n')
        writer = csv.writer(outfile, delimiter='\n')
        for num in range(0, 2):
            first_line = next(reader, None)
            if first_line:
                writer.writerow(first_line)

        for row in reader:
            new_row = []
            for item in row:
                if "s__" in item and "SGB" not in item: 
                    new_row.append(item)
                    writer.writerow(new_row)

kraken_tsv = 'Kraken_otu.tsv'
meta_table = 'meta_table.tsv'
meta_table_only_species = 'MetaPhlAn_species.tsv'
decimal_kraken_tsv = 'kraken_decimal.tsv'
scientific_to_decimal(kraken_tsv, decimal_kraken_tsv)
meta_only_speaces(meta_table, meta_table_only_species)
