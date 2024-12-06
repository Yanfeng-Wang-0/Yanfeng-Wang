# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: cfexercise2.py
# Description: demonstrate different ways to print "hello" based on various conditions
# Version: 0.0.1
# Date: Oct 2024 

"""
Description: demonstrate different ways to print "hello" based on various conditions
"""

# Function to print 'hello' for each number divisible by 3 in the range from 0 to x
def hello_1(x):
    for j in range(x):
        if j % 3 == 0:  # Check if j is divisible by 3
            print('hello')
    print(' ')

# Call hello_1 function with x=12
hello_1(12)

# Function to print 'hello' for specific conditions within the range from 0 to x
def hello_2(x):
    for j in range(x):
        if j % 5 == 3:  # Check if remainder when j is divided by 5 is 3
            print('hello')
        elif j % 4 == 3:  # Check if remainder when j is divided by 4 is 3
            print('hello')
    print(' ')

# Call hello_2 function with x=12
hello_2(12)

# Function to print 'hello' for every number in the range from x to y
def hello_3(x, y):
    for i in range(x, y):
        print('hello')
    print(' ')

# Call hello_3 function with x=3, y=17
hello_3(3, 17)

# Function to print 'hello' until x reaches 15, incrementing by 3 in each iteration
def hello_4(x):
    while x != 15:  # Loop until x equals 15
        print('hello')
        x = x + 3  # Increment x by 3
    print(' ')

# Call hello_4 function with x=0
hello_4(0)

# Function to print 'hello' based on specific conditions while x is less than 100
def hello_5(x):
    while x < 100:  # Loop until x is less than 100
        if x == 31:  # If x is 31, print 'hello' 7 times
            for k in range(7):
                print('hello')
        elif x == 18:  # If x is 18, print 'hello' once
            print('hello')
        x = x + 1  # Increment x by 1
    print(' ')

# Call hello_5 function with x=12
hello_5(12)

# Function to print 'hello' while x is True, incrementing y each time, and stop when y equals 6
def hello_6(x, y):
    while x:  # Loop while x is True
        print("hello! " + str(y))  # Print 'hello!' with current value of y
        y += 1  # Increment y by 1
        if y == 6:  # Break the loop if y reaches 6
            break
    print(' ')

# Call hello_6 function with x=True, y=0
hello_6(True, 0)
