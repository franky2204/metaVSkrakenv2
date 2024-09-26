#method needed to divide the taxo three of the meta file
def findClade(name_find):
    elements = name_find.split('|')
    last_element = elements[-1]
    if last_element == "":
        return -1
    return last_element
#method to read header metaphlan file
def extract_sample(header_line,n):
        header_line = header_line.readline().strip()
        header_elements = header_line.split('\t')
        sample_names = header_elements[n:] 
        return sample_names
#find the last element of the taxonomy three metaphlan
def find_last_name(taxonomy_string):
    elements = taxonomy_string.split('|')
    last_element = elements[-1]
    letter, name = last_element.split('__')
    return letter, name

def findNotBacteria(metaFile): 
    archaea = []
    eukaryota = []

    with open(metaFile, 'r') as file:
        for line in file:
            elements = line.strip().split('\t')
            first_element = elements[0]
            if elements[0]=='k__Eukaryota':
                eukaryota.extend(elements[1:])
            elif elements[0]=='k__Archaea':
                archaea.extend(elements[1:])
    archaea=[float(value) for value in archaea]
    eukaryota=[float(value) for value in eukaryota]
    return archaea, eukaryota