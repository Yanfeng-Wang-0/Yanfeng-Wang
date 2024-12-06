# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: using_name.py
# Description: distinguish between running the script directly versus importing it as a module in another script
# Version: 0.0.1
# Date: Oct 2024 

"""
Description: distinguish between running the script directly versus importing it as a module in another script
"""

# Check if the script is being run directly or imported as a module
if __name__ == '__main__':
    # If run directly, print this message
    print('This program is being run by itself!')
else:
    # If imported into another script or module, print this message
    print('I am being imported from another script/program/module!')

# Print the name of the module (usually '__main__' if run directly, or module name if imported)
print("This module's name is: " + __name__)
