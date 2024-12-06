# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: TreeHeight.R
# Description: calculates tree heights based on angles and distances
# Version: 0.0.1
# Date: Nov 2024 

# This function calculates heights of trees given distance of each tree 
# from its base and angle to its top, using  the trigonometric formula 
#
# height = distance * tan(radians)

# Clear the workspace to remove all existing objects
rm(list = ls())

# Load the tree data from a CSV file
Tree_data <- read.csv("../data/trees.csv")

# Function to calculate tree height given an angle (in degrees) and distance
TreeHeight <- function(degrees, distance) {  
  # Convert degrees to radians
  radians <- degrees * pi / 180  
  
  # Calculate height using the tangent function
  height <- distance * tan(radians)
  
  # Print the calculated height
  cat(sprintf("Tree height is: %.2f\n", height))
  
  # Return the calculated height
  return(height) 
}

# Test the TreeHeight function with a specific angle and distance
TreeHeight(37, 40)  # Example: Angle = 37 degrees, Distance = 40 meters

# Calculate tree heights for all rows in the dataset
Tree_data$Tree.Height.m <- with(Tree_data, Distance.m * tan(Angle.degrees * pi / 180))

# Save the updated dataset with tree heights to a CSV file
write.csv(Tree_data, file = "../results/TreeHts.csv", row.names = FALSE)

# Print a confirmation message
cat("Tree heights calculated and saved to '../results/TreeHts.csv'\n")

