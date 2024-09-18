# Function to convert formatted file to TSV
def convert_to_tsv(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Split the line on space to extract data
            fields = line.strip().split(' ')
            # If there is a taxonomy with a pipe symbol, it will keep it as a single field
            outfile.write('\t'.join(fields) + '\n')

# File paths (input and output)
input_file = 'formatted__names.txt'  # Replace with your input file path
output_file = 'formatted__names.tsv'  # Replace with your desired output file path

# Call the function to convert the file
convert_to_tsv(input_file, output_file)

print(f"Data has been successfully converted to {output_file}")
