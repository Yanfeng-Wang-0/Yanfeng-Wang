# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: basic_io2.py
# Description: creates a list of numbers from 0 to 99 and writes each number to testout.txt, with each number on a new line
# Version: 0.0.1
# Date: Oct 2024

"""
Description: creates a list of numbers from 0 to 99 and writes each number to testout.txt, with each number on a new line
"""

# Create a list of numbers from 0 to 99
list_to_save = range(100)

# Open the output file in write mode
f = open('../sandbox/testout.txt', 'w')

# Loop through each number in the list and write it to the file
for i in list_to_save:
    f.write(str(i) + '\n')  # Convert the number to a string and write it with a newline character

# Close the file to ensure data is saved properly
f.close()
