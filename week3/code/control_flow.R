# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: control_flow.R
# Description: demonstrates various control structures
# Version: 0.0.1
# Date: Oct 2024 

# Assign TRUE to variable 'a'
a <- TRUE

# Check if 'a' is TRUE, and print an appropriate message
if (a == TRUE) {
    print("a is TRUE")
} else {
    print("a is FALSE")
}

# Generate a random number between 0 and 1, store it in 'z'
z <- runif(1) 

# Check if 'z' is less than or equal to 0.5 and print a message
if (z <= 0.5) {
    print("Less than a half")
}

# Loop through the numbers from 1 to 10
for (i in 1:10) {
    # Calculate the square of 'i'
    j <- i * i
    # Print the result of squaring 'i'
    print(paste(i, " squared is", j))
}

# Generate a sequence from 1 to 10 (but don't do anything with it)
1:10

# Loop through a vector of species names and print each one
for(species in c('Heliodoxa rubinoides', 
                 'Boissonneaua jardini', 
                 'Sula nebouxii')) {
    print(paste('The species is', species))
}

# Define a character vector 'v1' with three elements
v1 <- c("a", "bc", "def")

# Loop through each element in the 'v1' vector and print it
for (i in v1) {
    print(i)
}

# Initialize variable 'i' to 0
i <- 0

# While loop that runs as long as 'i' is less than 10
while (i < 10) {
    # Increment 'i' by 1
    i <- i + 1
    # Print the square of 'i'
    print(i^2)
}
