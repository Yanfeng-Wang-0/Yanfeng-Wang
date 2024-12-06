# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: basic_io1.py
# Description: read test.txt and prints each line twice: once for every line, including blank lines, and once for only non-blank lines
# Version: 0.0.1
# Date: Oct 2024

"""
Description: read test.txt and prints each line twice: once for every line, including blank lines, and once for only non-blank lines
"""

# Open the file in read mode
f = open('../sandbox/test.txt', 'r')

# Loop through each line in the file and print it
for line in f:
    print(line)

# Close the file
f.close()

# Open the file again in read mode
f = open('../sandbox/test.txt', 'r')

# Loop through each line, strip any leading/trailing whitespace, and print non-empty lines
for line in f:
    if len(line.strip()) > 0:  # Check if the line is not empty
        print(line)

# Close the file
f.close()

