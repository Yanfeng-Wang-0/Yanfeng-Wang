# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: preallocate.R
# Description: demonstrates and compares the efficiency of two methods for constructing a vector in R
# Version: 0.0.1
# Date: Oct 2024 

# Define a function 'NoPreallocFun' that takes 'x' as an argument
NoPreallocFun <- function(x) {
    # Initialize an empty vector 'a'
    a <- vector()
    
    # Loop from 1 to 'x'
    for (i in 1:x) {
        # Concatenate the current value of 'i' to the vector 'a'
        a <- c(a, i) 
        
        # Print the current vector 'a'
        print(a)
        
        # Print the memory size of the current vector 'a'
        print(object.size(a))
    }
}

# Measure and print the execution time of 'NoPreallocFun(10)'
system.time(NoPreallocFun(10))

# Define a function 'PreallocFun' that takes 'x' as an argument
PreallocFun <- function(x) {
    # Preallocate vector 'a' of length 'x' with NA values
    a <- rep(NA, x)
    
    # Loop from 1 to 'x'
    for (i in 1:x) {
        # Assign the value 'i' to the i-th position in 'a'
        a[i] <- i
        
        # Print the current vector 'a'
        print(a)
        
        # Print the memory size of the current vector 'a'
        print(object.size(a))
    }
}

# Measure and print the execution time of 'PreallocFun(10)'
system.time(PreallocFun(10))
