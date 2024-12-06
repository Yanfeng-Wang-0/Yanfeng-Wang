# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: browse.R
# Description: calculates the population at each generation and returns a vector of population sizes, then generates a plot 
# Version: 0.0.1
# Date: Oct 2024 

# Define a function 'Exponential' that models exponential growth
# N0 is the initial population, r is the growth rate, and generations is the number of generations (time steps)
Exponential <- function(N0 = 1, r = 1, generations = 10) {
  
  # Create a vector 'N' of length 'generations' initialized with NA values
  N <- rep(NA, generations)  
  
  # Set the first value of 'N' to the initial population size (N0)
  N[1] <- N0
  
  # Loop through generations 2 to 'generations' to calculate population size at each time step
  for (t in 2:generations) {
    # Apply the exponential growth formula: N(t) = N(t-1) * exp(r)
    N[t] <- N[t-1] * exp(r)
    
    # Pause the execution at each step (browser is used for debugging and inspecting variables)
    browser()
  }
  
  # Return the vector 'N' representing population size over generations
  return(N)
}

# Plot the result of the 'Exponential' function, representing exponential growth over generations
plot(Exponential(), type="l", main="Exponential growth")
