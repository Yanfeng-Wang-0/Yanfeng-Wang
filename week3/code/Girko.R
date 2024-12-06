# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: Girko.R
# Description: generates a plot that visualizes the eigenvalues of a randomly created matrix
# Version: 0.0.1
# Date: Oct 2024 

# Define a function to create an ellipse with given horizontal and vertical radii
build_ellipse <- function(hradius, vradius) { 
  npoints = 250  # Define the number of points to plot the ellipse
  a <- seq(0, 2 * pi, length = npoints + 1)  # Generate a sequence of angles from 0 to 2*pi
  x <- hradius * cos(a)  # Calculate the x-coordinates using the horizontal radius
  y <- vradius * sin(a)  # Calculate the y-coordinates using the vertical radius
  return(data.frame(x = x, y = y))  # Return the ellipse data as a data frame
}

# Set the size of the matrix N (250 in this case)
N <- 250

# Create a random NxN matrix 'M' with normally distributed values
M <- matrix(rnorm(N * N), N, N)

# Compute the eigenvalues of the matrix 'M'
eigvals <- eigen(M)$values

# Create a data frame containing the real and imaginary parts of the eigenvalues
eigDF <- data.frame("Real" = Re(eigvals), "Imaginary" = Im(eigvals))

# Calculate the radius for the ellipse (square root of N)
my_radius <- sqrt(N)

# Build the ellipse using the calculated radius
ellDF <- build_ellipse(my_radius, my_radius)

# Rename the columns of 'ellDF' to match the names in 'eigDF'
names(ellDF) <- c("Real", "Imaginary")

# Create a ggplot object for the eigenvalues with 'Real' and 'Imaginary' parts
p <- ggplot(eigDF, aes(x = Real, y = Imaginary))

# Add points to the plot with a specific shape (shape 3 is a cross)
p <- p + geom_point(shape = I(3))

# Remove the legend from the plot
p <- p + theme(legend.position = "none")

# Add horizontal and vertical lines at the origin (x = 0, y = 0)
p <- p + geom_hline(aes(yintercept = 0))
p <- p + geom_vline(aes(xintercept = 0))

# Add the ellipse to the plot, with a red fill and transparent alpha
p <- p + geom_polygon(data = ellDF, aes(x = Real, y = Imaginary, alpha = 1/20, fill = "red"))

# Display the plot
p
