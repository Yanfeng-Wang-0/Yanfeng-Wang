# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: lc1.py
# Description: extracts information from birds that contains Latin names, common names, and body masses for several bird species
# Version: 0.0.1
# Date: Oct 2024 

"""
Description: extracts information from birds that contains Latin names, common names, and body masses for several bird species
"""

# Tuple containing bird information: (Latin name, common name, body mass)
birds = ( ('Passerculus sandwichensis','Savannah sparrow',18.7),
          ('Delichon urbica','House martin',19),
          ('Junco phaeonotus','Yellow-eyed junco',19.5),
          ('Junco hyemalis','Dark-eyed junco',19.6),
          ('Tachycineata bicolor','Tree swallow',20.2),
         )
#(1) Write three separate list comprehensions that create three different
# lists containing the latin names, common names and mean body masses for
# each species in birds, respectively. 
# Extracting bird information using list comprehensions
latin_names = [bird[0] for bird in birds]  # Extract Latin names
common_names = [bird[1] for bird in birds]  # Extract common names
body_masses = [bird[2] for bird in birds]  # Extract body masses

# Print the lists extracted using list comprehensions
print("Latin names:", latin_names)
print("Common names:", common_names)
print("Body masses:", body_masses)

# (2) Now do the same using conventional loops (you can choose to do this 
# before 1 !). 
# Reinitialize empty lists to extract bird information using a for loop
latin_names = []
common_names = []
body_masses = []

# Extracting bird information using a for loop
for bird in birds:
    latin_names.append(bird[0])  # Append Latin name to latin_names list
    common_names.append(bird[1])  # Append common name to common_names list
    body_masses.append(bird[2])  # Append body mass to body_masses list

# Print the lists extracted using a for loop
print("Latin names:", latin_names)
print("Common names:", common_names)
print("Body masses:", body_masses)
