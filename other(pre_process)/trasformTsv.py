def convert_txt_to_tsv(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            line = line.strip()

            if line:
                parts = line.split(maxsplit=1) 

                if len(parts) == 2:
                    num, names = parts[0], parts[1]

                    if '|' in names:
                        names_list = names.split('|')

                        for name in names_list:
                            outfile.write(f"{num}\t{name.strip()}\n")
                    else:
                        outfile.write(f"{num}\t{names.strip()}\n")

if __name__ == "__main__":
    input_file = "formatted__names.txt"  
    output_file = "formatted__names.tsv" 
    convert_txt_to_tsv(input_file, output_file)
