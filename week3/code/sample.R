# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: sample.R
# Description: compares the efficiency of different methods for sampling and calculating the mean of subsets from a population
# Version: 0.0.1
# Date: Oct 2024 

# Function to sample `n` elements from a population and return their mean
myexperiment <- function(popn, n) {
    # Sample `n` elements from `popn` without replacement
    pop_sample <- sample(popn, n, replace = FALSE)
    # Calculate and return the mean of the sampled elements
    return(mean(pop_sample))
}

# Function to perform `num` experiments using loops without preallocating memory
loopy_sample1 <- function(popn, n, num) {
    result1 <- vector() # Initialize an empty vector to store results
    for (i in 1:num) {
        # Append the result of `myexperiment` to the vector
        result1 <- c(result1, myexperiment(popn, n))
    }
    return(result1)
}

# Function to perform `num` experiments using loops with preallocated vector memory
loopy_sample2 <- function(popn, n, num) {
    result2 <- vector(, num) # Preallocate a vector of length `num`
    for (i in 1:num) {
        # Assign the result of `myexperiment` to the i-th element
        result2[i] <- myexperiment(popn, n)
    }
    return(result2)
}

# Function to perform `num` experiments using loops with preallocated list memory
loopy_sample3 <- function(popn, n, num) {
    result3 <- vector("list", num) # Preallocate a list of length `num`
    for (i in 1:num) {
        # Assign the result of `myexperiment` to the i-th list element
        result3[[i]] <- myexperiment(popn, n)
    }
    return(result3)
}

# Function to perform `num` experiments using the `lapply` function
lapply_sample <- function(popn, n, num) {
    # Use `lapply` to apply the `myexperiment` function across `num` iterations
    result4 <- lapply(1:num, function(i) myexperiment(popn, n))
    return(result4)
}

# Function to perform `num` experiments using the `sapply` function
sapply_sample <- function(popn, n, num) {
    # Use `sapply` to apply the `myexperiment` function across `num` iterations
    result5 <- sapply(1:num, function(i) myexperiment(popn, n))
    return(result5)
}

# Set seed for reproducibility
set.seed(12345)

# Generate a population of 10,000 random numbers from a normal distribution
popn <- rnorm(10000) 

# Display a histogram of the population
hist(popn)

# Set the sample size and number of experiments
n <- 100 # Sample size
num <- 10000 # Number of experiments

# Measure and display the time taken by each method
print("Using loops without preallocation on a vector took:" )
print(system.time(loopy_sample1(popn, n, num)))

print("Using loops with preallocation on a vector took:" )
print(system.time(loopy_sample2(popn, n, num)))

print("Using loops with preallocation on a list took:" )
print(system.time(loopy_sample3(popn, n, num)))

print("Using the vectorized sapply function (on a list) took:" )
print(system.time(sapply_sample(popn, n, num)))

print("Using the vectorized lapply function (on a list) took:" )
print(system.time(lapply_sample(popn, n, num)))
