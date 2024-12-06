# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: loops.py
# Description: demonstrates the use of for loops and a while loop
# Version: 0.0.1
# Date: Oct 2024 

"""
Description: demonstrates the use of for loops and a while loop
"""

# FOR loops

# Loop through numbers from 0 to 4 and print each number
for i in range(5):
    print(i)

# Define a list with mixed data types
my_list = [0, 2, "geronimo!", 3.0, True, False]

# Loop through each element in my_list and print it
for k in my_list:
    print(k)

# Calculate the cumulative sum of elements in summands
total = 0
summands = [0, 1, 11, 111, 1111]
for s in summands:
    total = total + s  # Add the current element to total
    print(total)  # Print the running total

# WHILE loop

# Initialize z to 0
z = 0
# Loop while z is less than 100
while z < 100:
    z = z + 1  # Increment z by 1
    print(z)  # Print the current value of z
