# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: boilerplate.py
# Description: Python boilerplate script that serves as a template for new programs
# Version: 0.0.1
# Date: Oct 2024

"""
Description: Python boilerplate script that serves as a template for new programs
"""

# Metadata about the application
__appname__ = '[application name here]'
__author__ = 'Your Name (your@email.address)'
__version__ = '0.0.1'
__license__ = "License for this code/program"

import sys  # Importing the sys module for command line arguments and exit

def main(argv):
    """ Main entry point of the program """
    # Print a message indicating that this is a boilerplate code
    print('This is a boilerplate') 
    return 0  # Return 0 to indicate successful execution

if __name__ == "__main__": 
    """Makes sure the "main" function is called if the script is executed directly from the command line"""
    # Call the main function with command line arguments and exit with the returned status
    status = main(sys.argv)
    sys.exit(status)
