# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: plotLin.R
# Description: creates a scatter plot of y vs. x with a color gradient representing the residuals from a linear regression
# Version: 0.0.1
# Date: Oct 2024 

# Generate a sequence of values from 0 to 100 with a step of 0.1
x <- seq(0, 100, by = 0.1)

# Create a dependent variable 'y' with a linear relationship to 'x' and added random noise
y <- -4. + 0.25 * x + rnorm(length(x), mean = 0., sd = 2.5)

# Combine the 'x' and 'y' values into a data frame
my_data <- data.frame(x = x, y = y)

# Fit a linear model of 'y' as a function of 'x' and summarize the results
my_lm <- summary(lm(y ~ x, data = my_data))

# Create a ggplot object for plotting the data
p <- ggplot(my_data, aes(x = x, y = y, 
                         colour = abs(my_lm$residual))) +
  # Add points to the plot, with colors based on the absolute value of the residuals
  geom_point() +
  # Apply a color gradient from black to red based on residual size
  scale_colour_gradient(low = "black", high = "red") +
  # Remove the legend from the plot
  theme(legend.position = "none") +
  # Customize the x-axis label with a mathematical expression
  scale_x_continuous(
    expression(alpha^2 * pi / beta * sqrt(Theta)))

# Add the linear regression line (slope and intercept from the model)
p <- p + geom_abline(
  intercept = my_lm$coefficients[1][1],  # intercept from the linear model
  slope = my_lm$coefficients[2][1],      # slope from the linear model
  colour = "red")  # red color for the regression line

# Add a text label to the plot with a mathematical expression
p <- p + geom_text(aes(x = 60, y = 0, 
                       label = "sqrt(alpha) * 2* pi"), 
                   parse = TRUE, size = 6, 
                   colour = "blue")

# Display the plot
p
