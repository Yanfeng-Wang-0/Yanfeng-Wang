# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: control_flow.py
# Description: exemplifies the use of control statements through several utility functions
# Version: 0.0.1
# Date: Oct 2024 

"""
Description: Some functions exemplifying the use of control statements
"""

# Metadata about the application
__author__ = 'Yanfeng Wang (yw4524@ic.ac.uk)'
__version__ = '0.0.1'

import sys  # Importing sys for command line arguments and exit

# Function to check whether a number is even or odd
def even_or_odd(x=0): 
    """Find whether a number x is even or odd."""
    if x % 2 == 0: 
        return "%d is Even!" % x  # Return if x is even
    return "%d is Odd!" % x  # Return if x is odd

# Function to find the largest divisor of x among 2, 3, 4, 5
def largest_divisor_five(x=120):
    """Find which is the largest divisor of x among 2, 3, 4, 5."""
    largest = 0
    if x % 5 == 0:
        largest = 5
    elif x % 4 == 0:
        largest = 4
    elif x % 3 == 0:
        largest = 3
    elif x % 2 == 0:
        largest = 2
    else: 
        return "No divisor found for %d!" % x  # Return if no divisor is found
    return "The largest divisor of %d is %d" % (x, largest)

# Function to check if an integer is prime
def is_prime(x=70):
    """Find whether an integer is prime."""
    for i in range(2, x): 
        if x % i == 0:
            print("%d is not a prime: %d is a divisor" % (x, i))  # Print divisor if x is not prime
            return False  # Return False if a divisor is found
    print ("%d is a prime!" % x)  # Print if x is prime
    return True 

# Function to find all prime numbers up to x
def find_all_primes(x=22):
    """Find all the primes up to x"""
    allprimes = []
    for i in range(2, x + 1):
        if is_prime(i):  # Check if i is prime
            allprimes.append(i)  # Add to list of primes if true
    print("There are %d primes between 2 and %d" % (len(allprimes), x))  # Print the number of primes found
    return allprimes

# Main entry point of the program to demonstrate the functions
def main(argv):
    print(even_or_odd(22))  # Check if 22 is even or odd
    print(even_or_odd(33))  # Check if 33 is even or odd
    print(largest_divisor_five(120))  # Find the largest divisor of 120 among 2, 3, 4, 5
    print(largest_divisor_five(121))  # Find the largest divisor of 121 among 2, 3, 4, 5
    print(is_prime(60))  # Check if 60 is a prime number
    print(is_prime(59))  # Check if 59 is a prime number
    print(find_all_primes(100))  # Find all primes up to 100
    return 0

# Entry point of the script when executed from the command line
if (__name__ == "__main__"):
    status = main(sys.argv)
    sys.exit(status)
