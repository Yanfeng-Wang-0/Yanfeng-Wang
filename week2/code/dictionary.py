# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: dictionary.py
# Description: reads taxa and creates taxa_dic that groups the species by their orders
# Version: 0.0.1
# Date: Oct 2024 

"""
Description: reads taxa and creates taxa_dic that groups the species by their orders
"""

# List of tuples containing species and their corresponding taxonomic orders
taxa = [ ('Myotis lucifugus','Chiroptera'),
         ('Gerbillus henleyi','Rodentia'),
         ('Peromyscus crinitus', 'Rodentia'),
         ('Mus domesticus', 'Rodentia'),
         ('Cleithrionomys rutilus', 'Rodentia'),
         ('Microgale dobsoni', 'Afrosoricida'),
         ('Microgale talazaci', 'Afrosoricida'),
         ('Lyacon pictus', 'Carnivora'),
         ('Arctocephalus gazella', 'Carnivora'),
         ('Canis lupus', 'Carnivora'),
        ]

# Initialize an empty dictionary to group species by their order
taxa_dic = {}

# Loop through each species and order in the list of tuples
for species, order in taxa:
    if order not in taxa_dic:
        taxa_dic[order] = set()  # Initialize a set if the order is not already in the dictionary
    taxa_dic[order].add(species)  # Add the species to the set corresponding to the order

# Print the dictionary that groups species by taxonomic order
print(taxa_dic)

# Create the same dictionary using dictionary comprehension
taxa_dic = {order: {species for species, o in taxa if o == order} for _, order in taxa}

# Print the dictionary created using dictionary comprehension
print(taxa_dic)
