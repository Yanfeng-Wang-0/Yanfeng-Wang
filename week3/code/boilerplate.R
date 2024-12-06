# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: boilerplate.R
# Description: accepts two arguments such that prints each argument's value and data type, then returns a combined vector of both arguments
# Version: 0.0.1
# Date: Oct 2024 

# Define a function 'MyFunction' that takes two arguments, 'Arg1' and 'Arg2'
MyFunction <- function(Arg1, Arg2) {

  # Print a message with the value of 'Arg1' and its data type (class)
  print(paste("Argument", as.character(Arg1), "is a", class(Arg1))) 
  
  # Print a message with the value of 'Arg2' and its data type (class)
  print(paste("Argument", as.character(Arg2), "is a", class(Arg2))) 
    
  # Return a vector combining 'Arg1' and 'Arg2'
  return(c(Arg1, Arg2))
}

# Call 'MyFunction' with numeric arguments 1 and 2
MyFunction(1, 2) 

# Call 'MyFunction' with character arguments "Riki" and "Tiki"
MyFunction("Riki", "Tiki") 
