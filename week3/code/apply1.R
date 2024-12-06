# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: apply1.R
# Description: calculates and prints the mean and variance of each row in the matrix, followed by the mean of each column
# Version: 0.0.1
# Date: Oct 2024 

# Create a 10x10 matrix 'M' with 100 random numbers from a normal distribution
M <- matrix(rnorm(100), 10, 10)

# Calculate the mean of each row in matrix 'M' and store the results in 'RowMeans'
RowMeans <- apply(M, 1, mean)

# Print the row means
print (RowMeans)

# Calculate the variance of each row in matrix 'M' and store the results in 'RowVars'
RowVars <- apply(M, 1, var)

# Print the row variances
print (RowVars)

# Calculate the mean of each column in matrix 'M' and store the results in 'ColMeans'
ColMeans <- apply(M, 2, mean)

# Print the column means
print (ColMeans)