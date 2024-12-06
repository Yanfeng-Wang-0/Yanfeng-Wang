# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: oaks_debugme.py
# Description: checks if a species name starts with 'quercus' and reads the input file, filters the rows containing oaks, and writes the relevant data to the output file
# Version: 0.0.1
# Date: Oct 2024 

"""
Description: checks if a species name starts with 'quercus' and reads the input file, filters the rows containing oaks, and writes the relevant data to the output file
"""

import csv
import sys

# Define function to check if a name is an oak
def is_an_oak(name):
    """Returns True if the name starts with 'quercus' (case insensitive)"""
    return name.lower().startswith('quercus')

# Main function to filter oak species and write to a new file
def main(argv): 
    # Use context managers to open the input and output CSV files
    with open('../data/TestOaksData.csv', 'r') as f, open('../data/JustOaksData.csv', 'w', newline='') as g:
        taxa = csv.reader(f)  # Create a CSV reader object for the input file
        csvwrite = csv.writer(g)  # Create a CSV writer object for the output file
        oaks = set()  # Set to keep track of unique oak species

        # Loop through each row in the input CSV
        for row in taxa:
            if is_an_oak(row[0]):  # Check if the species name starts with 'quercus'
                print(f'FOUND AN OAK: {row[0]}')  # Print a message if an oak is found
                oaks.add(row[0])  # Optionally keep track of unique oaks
                csvwrite.writerow([row[0], row[1]])  # Write the row to the output file

# Run the main function when the script is executed directly
if __name__ == "__main__":
    main(sys.argv)
