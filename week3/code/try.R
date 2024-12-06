# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: try.R
# Description: demonstrates how to handle errors in repetitive function calls and within a for loop
# Version: 0.0.1
# Date: Oct 2024 

doit <- function(x) {
    # Create a bootstrap sample (sampling with replacement) of `x`
    temp_x <- sample(x, replace = TRUE)
    
    # Check if the number of unique values in the sample is greater than 30
    if(length(unique(temp_x)) > 30) {
        # If sufficient unique values, calculate and print the mean
        print(paste("Mean of this sample was:", as.character(mean(temp_x))))
    } else {
        # If not enough unique values, throw an error
        stop("Couldn't calculate mean: too few unique values!")
    }
}

set.seed(1345)  # Ensure reproducibility

popn <- rnorm(50)  # Generate a population of 50 random numbers (normal distribution)

hist(popn)  # Plot a histogram of the population

lapply(1:15, function(i) doit(popn)) # This calls doit 15 times on the population popn. If an error occurs, the execution stops, and subsequent iterations are not performed.

result <- lapply(1:15, function(i) try(doit(popn), FALSE)) # Catches errors in each iteration and prevents them from stopping the entire process. FALSE in try(doit(popn), FALSE) prevents try from printing error messages to the console.

class(result)  # Check the class of `result`, which is "list"

result  # Display the contents of `result`

result <- vector("list", 15) 
for(i in 1:15) {
    result[[i]] <- try(doit(popn), FALSE)
    }doit <- function(x) {
    temp_x <- sample(x, replace = TRUE) # Bootstrap sampling
    if(length(unique(temp_x)) > 30) { 
        # Print the mean if unique values exceed 30
         print(paste("Mean of this sample was:", as.character(mean(temp_x))))
        } 
    else {
        # Raise an error if unique values are <= 30
        stop("Couldn't calculate mean: too few unique values!")
        }
    }

set.seed(1345)  # Set seed for reproducibility

popn <- rnorm(50)  # Generate a population of 50 random numbers

hist(popn)  # Plot histogram of the population

lapply(1:15, function(i) doit(popn))

result <- lapply(1:15, function(i) try(doit(popn), FALSE))

class(result)

result

result <- vector("list", 15) # Preallocate a list for results
for(i in 1:15) {
    result[[i]] <- try(doit(popn), FALSE) # Store output or error
    }