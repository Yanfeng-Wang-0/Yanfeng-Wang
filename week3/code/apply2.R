# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: apply2.R
# Description: checks if the sum is greater than 0, it multiplies each element by 100; otherwise, it leaves the vector unchanged
# Version: 0.0.1
# Date: Oct 2024 

# Define a function 'SomeOperation' that takes a vector 'v' as input
SomeOperation <- function(v) { 
  # Check if the sum of elements in 'v' is greater than 0
  if (sum(v) > 0) { 
    # If the sum is positive, return 'v' multiplied by 100
    return (v * 100)
  } else { 
    # If the sum is not positive, return 'v' unchanged
  return (v)
    }
}

# Create a 10x10 matrix 'M' with random numbers from a normal distribution
M <- matrix(rnorm(100), 10, 10)

# Apply the 'SomeOperation' function to each row of matrix 'M' and print the results
# The apply function with '1' as the second argument applies 'SomeOperation' across rows
print (apply(M, 1, SomeOperation))