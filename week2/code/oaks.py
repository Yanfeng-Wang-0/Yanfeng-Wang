# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: oaks.py
# Description: identifies oak species by checking if their name starts with 'quercus' and creates sets of oak species
# Version: 0.0.1
# Date: Oct 2024 

"""
Description: identifies oak species by checking if their name starts with 'quercus' and creates sets of oak species
"""

# List of tree species names
taxa = [ 'Quercus robur',
         'Fraxinus excelsior',
         'Pinus sylvestris',
         'Quercus cerris',
         'Quercus petraea',
       ]

# Function to check if a name is an oak (starts with 'quercus', case insensitive)
def is_an_oak(name):
    return name.lower().startswith('quercus ')

# Using a for loop to create a set of oak species in their original form
oaks_loops = set()
for species in taxa:
    if is_an_oak(species):  # Check if the species is an oak
        oaks_loops.add(species)  # Add the oak species to the set
print(oaks_loops)

# Using a list comprehension to create a set of oak species in their original form
oaks_lc = set([species for species in taxa if is_an_oak(species)])  # Add species to set if it is an oak
print(oaks_lc)

# Using a for loop to create a set of oak species names in uppercase
oaks_loops = set()
for species in taxa:
    if is_an_oak(species):  # Check if the species is an oak
        oaks_loops.add(species.upper())  # Add the oak species to the set in uppercase
print(oaks_loops)

# Using a list comprehension to create a set of oak species names in uppercase
oaks_lc = set([species.upper() for species in taxa if is_an_oak(species)])  # Add species in uppercase if it is an oak
print(oaks_lc)
