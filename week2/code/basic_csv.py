# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: basic_csv.py
# Description: reads testcsv.csv and creates bodymass.csv containing only the species name and their corresponding body mass
# Version: 0.0.1
# Date: Oct 2024

"""
Description: reads testcsv.csv and creates bodymass.csv containing only the species name and their corresponding body mass
"""

import csv

# Read a file containing:
# 'Species','Infraorder','Family','Distribution','Body mass male (Kg)'
with open('../data/testcsv.csv','r') as f:
    csvread = csv.reader(f)
    temp = []
    # Loop through each row in the CSV file
    for row in csvread:
        # Append the row as a tuple to the temp list
        temp.append(tuple(row))
        # Print the entire row
        print(row)
        # Print the species name from the row
        print("The species is", row[0])

# write a file containing only species name and Body mass
with open('../data/testcsv.csv','r') as f:
    with open('../data/bodymass.csv','w') as g:
        csvread = csv.reader(f)
        csvwrite = csv.writer(g)
        # Loop through each row in the CSV file
        for row in csvread:
            # Print the entire row
            print(row)
            # Write the species name and body mass to the new CSV file
            csvwrite.writerow([row[0], row[4]])
