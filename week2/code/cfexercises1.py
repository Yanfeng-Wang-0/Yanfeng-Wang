# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: cfexercise1.py
# Description: six utility functions (foo_1 to foo_6) that perform different mathematical operations
# Version: 0.0.1
# Date: Oct 2024 

"""
Description: six utility functions (foo_1 to foo_6) that perform different mathematical operations
"""

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
        x, y = y, x  # Swap x and y if x is greater than y
    if x > z:
        x, z = z, x  # Swap x and z if x is greater than z
    if y > z:
        y, z = z, y  # Swap y and z if y is greater than z
    return [x, y, z]

# Function to calculate the factorial of a number using iteration
def foo_4(x):
    result = 1
    for i in range(1, x + 1):
        result = result * i  # Multiply result by i for each iteration
    return result

# Function to calculate the factorial of a number using recursion
def foo_5(x): 
    if x == 1:  # Base case: factorial of 1 is 1
        return 1
    return x * foo_5(x - 1)  # Recursive call to calculate factorial

# Function to calculate the factorial of a number using a while loop
def foo_6(x): 
    facto = 1
    while x >= 1:
        facto = facto * x  # Multiply facto by current value of x
        x = x - 1  # Decrement x by 1
    return facto
