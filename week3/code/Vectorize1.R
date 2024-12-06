# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: Vectorize1.R
# Description: compares the time taken to calculate the sum of all elements in a matrix using two approaches
# Version: 0.0.1
# Date: Oct 2024 

M <- matrix(runif(1000000),1000,1000) # Creates a 1000 x 1000 matrix (M) filled with random numbers

SumAllElements <- function(M) {
  Dimensions <- dim(M)  # Get dimensions of the matrix (rows, columns)
  Tot <- 0              # Initialize total sum as 0
  for (i in 1:Dimensions[1]) {        # Iterate over rows
    for (j in 1:Dimensions[2]) {      # Iterate over columns
      Tot <- Tot + M[i, j]            # Add each element to the total
    }
  }
  return(Tot)  # Return the total sum
}
 
print("Using loops, the time taken is:")
print(system.time(SumAllElements(M)))

print("Using the in-built vectorized function, the time taken is:")
print(system.time(sum(M)))