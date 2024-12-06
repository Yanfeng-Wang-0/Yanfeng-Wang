# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: R_conditionals.R
# Description: defines three functions that check different properties of a number: even; power of 2; prime
# Version: 0.0.1
# Date: Oct 2024 

# Define a function 'is.even' that checks if a number 'n' is even or odd
is.even <- function(n = 2) {
  # Check if 'n' is divisible by 2 with no remainder (even number)
  if (n %% 2 == 0) {
    return(paste(n,'is even!'))  # Return a message stating 'n' is even
  } else {
    return(paste(n,'is odd!'))   # Return a message stating 'n' is odd
  }
}

# Call the 'is.even' function with the number 6
is.even(6)

# Define a function 'is.power2' that checks if a number 'n' is a power of 2
is.power2 <- function(n = 2) {
  # Check if the logarithm base 2 of 'n' is an integer (indicating a power of 2)
  if (log2(n) %% 1 == 0) {
    return(paste(n, 'is a power of 2!'))  # Return a message stating 'n' is a power of 2
  } else {
    return(paste(n,'is not a power of 2!'))  # Return a message stating 'n' is not a power of 2
  }
}

# Call the 'is.power2' function with the number 4
is.power2(4)

# Define a function 'is.prime' that checks if a number 'n' is prime, composite, or zero/unit
is.prime <- function(n) {
  # If 'n' is 0, return that it is zero
  if (n == 0) {
    return(paste(n,'is a zero!'))
  } 
  # If 'n' is 1, return that it is just a unit
  else if (n == 1) {
    return(paste(n,'is just a unit!'))
  }
    
  # Generate a sequence of integers from 2 to n-1
  ints <- 2:(n-1)
  
  # Check if 'n' is divisible by any integer in the sequence (if not, it's prime)
  if (all(n %% ints != 0)) {
    return(paste(n,'is a prime!'))  # Return a message stating 'n' is prime
  } else {
    return(paste(n,'is a composite!'))  # Return a message stating 'n' is composite
  }
}

# Call the 'is.prime' function with the number 3
is.prime(3)
