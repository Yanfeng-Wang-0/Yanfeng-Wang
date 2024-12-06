# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: break.R
# Description: prints from 1 to 10
# Version: 0.0.1
# Date: Oct 2024 

# Initialize variable 'i' to 0
i <- 0 

# Start an infinite loop that will run until explicitly broken
while (i < Inf) {
    
    # Check if 'i' is equal to 10
    if (i == 10) {
        # Exit the loop if 'i' equals 10
        break 
    } else {  
        # Print the current value of 'i' with a message
        cat("i equals", i, "\n")
        
        # Increment 'i' by 1 for the next iteration
        i <- i + 1 
    }
}
