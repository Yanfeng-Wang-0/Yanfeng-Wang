# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: sysargv.py
# Description: demonstrates how to use the sys module to access command line arguments
# Version: 0.0.1
# Date: Oct 2024 

"""
Description: demonstrates how to use the sys module to access command line arguments
"""

import sys  # Import sys module to access command line arguments

# Print the name of the script (the first argument in sys.argv)
print("This is the name of the script: ", sys.argv[0])

# Print the number of arguments passed to the script (including the script name)
print("Number of arguments: ", len(sys.argv))

# Print all arguments passed to the script as a list (in string format)
print("The arguments are: ", str(sys.argv))
