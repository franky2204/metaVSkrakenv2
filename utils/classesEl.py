#class used to store the varius data from the files 
class Categorization:
    def __init__(self, tool, sample, depth,three ,name, clade, quantity, qtyWOU):
        self.tool = tool
        self.sample = sample
        self.depth = depth
        self.three =three
        self.name = name
        self.clade = clade#this should be taxaid but at this point i dont care anymore
        self.quantity = quantity
        self.qtyWOU = qtyWOU
#class used to store the mean data from the files
class mean_data:
    def __init__(self,three, depth, clade, quantity, status):
        self.three = three
        self.depth = depth
        self.clade = clade
        self.quantity = quantity
        self.status = status
#guess what? this class is also useless
class meta_unknown:
    def __init__(self, sample, quantity):
        self.sample = sample
        self.quantity = quantity
