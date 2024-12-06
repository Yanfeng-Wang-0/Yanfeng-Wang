# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: MyBar.R
# Description: reads a dataset from a file, processes it to add a new column, and visualizes the data using ggplot2
# Version: 0.0.1
# Date: Oct 2024 

# Read a tabular dataset from a file 'Results.txt' and store it in dataframe 'a'
a <- read.table("../data/Results.txt", header = TRUE)

# Display the first few rows of 'a' to inspect the data
head(a)

# Add a new column 'ymin' to the data frame, setting it to 0 for all rows
a$ymin <- rep(0, dim(a)[1])

# Initialize the ggplot object with 'a' as the data source
p <- ggplot(a)

# Add the first set of vertical line ranges (from ymin to y1) with a specific color and transparency
p <- p + geom_linerange(data = a, aes(
                          x = x,          # x axis values
                          ymin = ymin,    # y axis minimum value (0)
                          ymax = y1,      # y axis maximum value (y1)
                          size = (0.5)    # Set line thickness
                          ),
                        colour = "#E69F00",  # Orange color
                        alpha = 1/2,         # Set transparency
                        show.legend = FALSE) # Do not show legend

# Add the second set of vertical line ranges (from ymin to y2) with a different color
p <- p + geom_linerange(data = a, aes(
                          x = x,
                          ymin = ymin,
                          ymax = y2,
                          size = (0.5)
                          ),
                        colour = "#56B4E9",  # Blue color
                        alpha = 1/2,         # Set transparency
                        show.legend = FALSE) # Do not show legend

# Add the third set of vertical line ranges (from ymin to y3) with a different color
p <- p + geom_linerange(data = a, aes(
                          x = x,
                          ymin = ymin,
                          ymax = y3,
                          size = (0.5)
                          ),
                        colour = "#D55E00",  # Red color
                        alpha = 1/2,         # Set transparency
                        show.legend = FALSE) # Do not show legend

# Add text labels to the plot at each 'x' position, and place the labels below the plot
p <- p + geom_text(data = a, aes(x = x, y = -500, label = Label))

# Customize the x and y axis labels and breaks, and apply a clean theme
p <- p + scale_x_continuous("My x axis",
                            breaks = seq(3, 5, by = 0.05)) +  # x axis breaks every 0.05 between 3 and 5
                            scale_y_continuous("My y axis") +   # y axis label
                            theme_bw() +                        # Use a white background theme
                            theme(legend.position = "none")      # Remove the legend

# Display the plot
p
