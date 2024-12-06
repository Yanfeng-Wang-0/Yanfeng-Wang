# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: next.R
# Description: loops through numbers from 1 to 10 and prints only the odd numbers
# Version: 0.0.1
# Date: Oct 2024 

# Start a loop from 1 to 10
for (i in 1:10) {
  
  # Check if 'i' is even by using the modulus operator (i %% 2 == 0)
  # If it is even, skip the current iteration and move to the next iteration
  if ((i %% 2) == 0) 
    next 
  
  # If 'i' is odd, print the value of 'i'
  print(i)
}
