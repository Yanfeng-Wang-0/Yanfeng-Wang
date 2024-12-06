# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: cfexercise.py
# Description: utility functions (foo_1 to foo_6) that perform different operations like computing square roots, finding the larger of two numbers, sorting numbers, and calculating factorials
# Version: 0.0.1
# Date: Oct 2024

"""
Description: utility functions (foo_1 to foo_6) that perform different operations like computing square roots, finding the larger of two numbers, sorting numbers, and calculating factorials
"""

import sys  # Importing sys to access command line arguments and exit

# Function to calculate the square root of a given number
def foo_1(x):
    return x ** 0.5

# Function to return the larger of two numbers
def foo_2(x, y):
    if x > y:
        return x
    return y

# Function to sort three numbers in ascending order
def foo_3(x, y, z):
    # Ensure x is the smallest and z is the largest
    if x > y:
        tmp = y
        y = x
        x = tmp
    if y > z:
        tmp = z
        z = y
        y = tmp
    return [x, y, z]

# Function to calculate the factorial of a number using iteration
def foo_4(x):
    result = 1
    for i in range(1, x + 1):
        result = result * i
    return result

# Function to calculate the factorial of a number using recursion
def foo_5(x): 
    if x == 1:
        return 1
    return x * foo_5(x - 1)

# Function to calculate the factorial of a number using a while loop
def foo_6(x): 
    facto = 1
    while x >= 1:
        facto = facto * x
        x = x - 1
    return facto

# Main entry point of the program to demonstrate the functions
def main(argv):
    # Print square root of 25 using foo_1
    print(f"Square root of 25 is: {foo_1(25)}")
    # Print the larger of 40 and 20 using foo_2
    print(f"Larger of 40 and 20 is: {foo_2(40, 20)}")
    # Print sorted numbers 3, 2, 1 using foo_3
    print(f"Numbers 3, 2, 1 sorted are: {foo_3(3, 2, 1)}")
    # Print factorial of 5 using iteration (foo_4)
    print(f"Factorial of 5 using iteration is: {foo_4(5)}")
    # Print factorial of 5 using recursion (foo_5)
    print(f"Factorial of 5 using recursion is: {foo_5(5)}")
    # Print factorial of 5 using while loop (foo_6)
    print(f"Factorial of 5 using while loop is: {foo_6(5)}")
    return 0

# Entry point of the script when executed from the command line
if __name__ == "__main__":
    status = main(sys.argv)
    sys.exit(status)
