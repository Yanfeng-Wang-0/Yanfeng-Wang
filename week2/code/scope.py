# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: scope.py
# Description: demonstrates the scope and behavior of global and local variables in Python
# Version: 0.0.1
# Date: Oct 2024 

"""
Description: demonstrates the scope and behavior of global and local variables in Python
"""

# Global variable declared outside of any function
_a_global = 10 

# Check if the global variable satisfies a condition
if _a_global >= 5:
    _b_global = _a_global + 5  # _b_global is also a global variable

# Print the values of the global variables before calling any function
print("Before calling a_function, outside the function, the value of _a_global is", _a_global)
print("Before calling a_function, outside the function, the value of _b_global is", _b_global)

def a_function():
    # Local variable with the same name as a global variable
    _a_global = 4  
    
    if _a_global >= 4:
        _b_global = _a_global + 5  # Local _b_global (shadowing global variable)
    
    _a_local = 3  # Another local variable

    # Print the local variables inside the function
    print("Inside the function, the value of _a_global is", _a_global)
    print("Inside the function, the value of _b_global is", _b_global)
    print("Inside the function, the value of _a_local is", _a_local)

# Call the function
a_function()

# Print the global variables after calling the function
print("After calling a_function, outside the function, the value of _a_global is (still)", _a_global)
print("After calling a_function, outside the function, the value of _b_global is (still)", _b_global)

# This will cause an error because _a_local is not defined in the global scope
# print("After calling a_function, outside the function, the value of _a_local is ", _a_local)

_a_global = 10  # Resetting the global variable

def a_function():
    _a_local = 4  # Local variable
    
    # Accessing the global variable without modifying it
    print("Inside the function, the value _a_local is", _a_local)
    print("Inside the function, the value of _a_global is", _a_global)

# Call the function
a_function()

# Print the global variable
print("Outside the function, the value of _a_global is", _a_global)

_a_global = 10  # Reset the global variable

print("Before calling a_function, outside the function, the value of _a_global is", _a_global)

def a_function():
    global _a_global  # Declare the use of the global variable
    _a_global = 5  # Modify the global variable
    _a_local = 4  # Local variable

    # Print the global and local variables
    print("Inside the function, the value of _a_global is", _a_global)
    print("Inside the function, the value _a_local is", _a_local)

# Call the function
a_function()

# Print the global variable after modification
print("After calling a_function, outside the function, the value of _a_global now is", _a_global)

def a_function():
    _a_global = 10  # Local variable with the same name as the global variable

    def _a_function2():
        global _a_global  # Modify the global variable
        _a_global = 20

    # Print the local variable before calling the nested function
    print("Before calling a_function2, value of _a_global is", _a_global)

    _a_function2()  # Call the nested function

    # Print the local variable after calling the nested function
    print("After calling a_function2, value of _a_global is", _a_global)

# Call the function
a_function()

# Print the global variable after modification by the nested function
print("The value of a_global in main workspace / namespace now is", _a_global)

_a_global = 10  # Reset the global variable

def a_function():

    def _a_function2():
        global _a_global  # Modify the global variable
        _a_global = 20

    # Print the global variable before calling the nested function
    print("Before calling a_function2, value of _a_global is", _a_global)

    _a_function2()  # Call the nested function

    # Print the global variable after calling the nested function
    print("After calling a_function2, value of _a_global is", _a_global)

# Call the function
a_function()

# Print the global variable after modification by the nested function
print("The value of a_global in main workspace / namespace is", _a_global)
