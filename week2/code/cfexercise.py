#!/usr/bin/env python3

import sys

def foo_1(x):
    return x ** 0.5

def foo_2(x, y):
    if x > y:
        return x
    return y

def foo_3(x, y, z):
    if x > y:
        tmp = y
        y = x
        x = tmp
    if y > z:
        tmp = z
        z = y
        y = tmp
    return [x, y, z]

def foo_4(x):
    result = 1
    for i in range(1, x + 1):
        result = result * i
    return result

def foo_5(x): 
    if x == 1:
        return 1
    return x * foo_5(x - 1)
     
def foo_6(x): 
    facto = 1
    while x >= 1:
        facto = facto * x
        x = x - 1
    return facto

def main(argv):
    print(f"Square root of 25 is: {foo_1(25)}")
    print(f"Larger of 40 and 20 is: {foo_2(40, 20)}")
    print(f"Numbers 10, 7, 5 sorted are: {foo_3(3, 2, 1)}")
    print(f"Factorial of 5 using iteration is: {foo_4(5)}")
    print(f"Factorial of 5 using recursion is: {foo_5(5)}")
    print(f"Factorial of 5 using while loop is: {foo_6(5)}")
    return 0


if __name__ == "__main__":
    status = main(sys.argv)
    sys.exit(status)

