# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: TreeHeight.R
# Description: calculates the height of a tree based on the angle of elevation and the distance from the trees
# Version: 0.0.1
# Date: Oct 2024 

# This function calculates heights of trees given distance of each tree 
# from its base and angle to its top, using  the trigonometric formula 
#
# height = distance * tan(radians)
#
# ARGUMENTS
# degrees:   The angle of elevation of tree
# distance:  The distance from base of tree (e.g., meters)
#
# OUTPUT
# The heights of the tree, same units as "distance"

TreeHeight <- function(degrees, distance) {
    # Convert degrees to radians
    radians <- degrees * pi / 180
    
    # Calculate the tree height using the tangent function
    height <- distance * tan(radians)
    
    # Print the calculated height
    print(paste("Tree height is:", height))
    
    # Return the height as the output of the function
    return (height)
}

# Example usage of the TreeHeight function
TreeHeight(37, 40)
