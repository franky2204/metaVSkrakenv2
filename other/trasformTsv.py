def convert_txt_to_tsv(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Rimuove gli spazi bianchi all'inizio e alla fine della riga
            line = line.strip()

            # Divide la riga al primo spazio (tra il numero e il nome)
            if line:
                parts = line.split(maxsplit=1)  # Divide in 2 parti: numero e resto

                if len(parts) == 2:
                    num, names = parts[0], parts[1]

                    # Se i nomi contengono un pipe (|), dividili
                    if '|' in names:
                        names_list = names.split('|')

                        # Scrive ogni nome separato nel file, preceduto dal numero
                        for name in names_list:
                            outfile.write(f"{num}\t{name.strip()}\n")
                    else:
                        # Scrive la riga se non ci sono pipe nel nome
                        outfile.write(f"{num}\t{names.strip()}\n")

if __name__ == "__main__":
    input_file = "formatted__names.txt"  # Sostituisci con il percorso del file di input
    output_file = "formatted__names.tsv"  # Sostituisci con il percorso del file di output
    convert_txt_to_tsv(input_file, output_file)
