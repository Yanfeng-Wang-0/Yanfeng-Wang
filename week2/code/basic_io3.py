# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: basic_io3.py
# Description: save and load a Python dictionary using the pickle module
# Version: 0.0.1
# Date: Oct 2024

"""
Description: save and load a Python dictionary using the pickle module
"""

import pickle

# Define a dictionary to be saved
my_dictionary = {"a key": 10, "another key": 11}

# Open the file in binary write mode to save the dictionary
f = open('../sandbox/testp.p', 'wb')
# Serialize and write the dictionary to the file
pickle.dump(my_dictionary, f)
# Close the file to ensure data is saved properly
f.close()

# Open the file in binary read mode to load the dictionary
f = open('../sandbox/testp.p', 'rb')
# Deserialize and load the dictionary from the file
another_dictionary = pickle.load(f)
# Close the file
f.close()

# Print the loaded dictionary to verify it matches the original
print(another_dictionary)

