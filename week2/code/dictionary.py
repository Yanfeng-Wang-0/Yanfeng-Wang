taxa = [ ('Myotis lucifugus','Chiroptera'),
         ('Gerbillus henleyi','Rodentia',),
         ('Peromyscus crinitus', 'Rodentia'),
         ('Mus domesticus', 'Rodentia'),
         ('Cleithrionomys rutilus', 'Rodentia'),
         ('Microgale dobsoni', 'Afrosoricida'),
         ('Microgale talazaci', 'Afrosoricida'),
         ('Lyacon pictus', 'Carnivora'),
         ('Arctocephalus gazella', 'Carnivora'),
         ('Canis lupus', 'Carnivora'),
        ]

# Write a python script to populate a dictionary called taxa_dic derived from
# taxa so that it maps order names to sets of taxa and prints it to screen.
# 
# An example output is:
#  
# 'Chiroptera' : set(['Myotis lucifugus']) ... etc. 
# OR, 
# 'Chiroptera': {'Myotis  lucifugus'} ... etc

#### Your solution here #### 
# Initialize an empty dictionary
taxa_dic = {}

# Populate the dictionary by iterating over the taxa list
for species, order in taxa:
    if order not in taxa_dic:
        taxa_dic[order] = set()  # Initialize a set if the order doesn't exist
    taxa_dic[order].add(species)

# Print the dictionary
print(taxa_dic) 

# Now write a list comprehension that does the same (including the printing after the dictionary has been created)  
 
#### Your solution here #### 
# Create the dictionary using list comprehension
taxa_dic = {order: {species for species, o in taxa if o == order} for _, order in taxa}

# Print the dictionary
print(taxa_dic)