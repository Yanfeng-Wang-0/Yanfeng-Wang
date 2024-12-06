# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: tuple.py
# Description: prints the information for each bird in a formatted way
# Version: 0.0.1
# Date: Oct 2024 

"""
Description: prints the information for each bird in a formatted way
"""

birds = ( ('Passerculus sandwichensis','Savannah sparrow',18.7),
          ('Delichon urbica','House martin',19),
          ('Junco phaeonotus','Yellow-eyed junco',19.5),
          ('Junco hyemalis','Dark-eyed junco',19.6),
          ('Tachycineata bicolor','Tree swallow',20.2),
        )

# Birds is a tuple of tuples of length three: latin name, common name, mass.
# write a (short) script to print these on a separate line or output block by
# species 
birds = ( ('Passerculus sandwichensis','Savannah sparrow',18.7),
          ('Delichon urbica','House martin',19),
          ('Junco phaeonotus','Yellow-eyed junco',19.5),
          ('Junco hyemalis','Dark-eyed junco',19.6),
          ('Tachycineata bicolor','Tree swallow',20.2),
        )
# Loop through each bird in the tuple and print its information
for bird in birds:
    # Print the Latin name, common name, and mass for each bird
    print(f"Latin name: {bird[0]} Common name: {bird[1]} Mass: {bird[2]}")