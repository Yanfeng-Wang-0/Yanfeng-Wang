# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: basic_io.R
# Description: demonstrates reading data, appending rows, and controlling the inclusion of row and column names when writing data to CSV files
# Version: 0.0.1
# Date: Oct 2024 

# Read the data from a CSV file located in the '../data/' directory and store it in 'MyData'
# 'header = TRUE' specifies that the first row of the file contains column names
MyData <- read.csv("../data/trees.csv", header = TRUE) 

# Write the entire 'MyData' dataframe to a new CSV file in the '../results/' directory
write.csv(MyData, "../results/MyData.csv") 

# Append the first row of 'MyData' to the existing 'MyData.csv' file in the '../results/' directory
write.table(MyData[1,], file = "../results/MyData.csv",append=TRUE) 

# Write the 'MyData' dataframe to 'MyData.csv' again, including row names
write.csv(MyData, "../results/MyData.csv", row.names=TRUE) 

# Write the 'MyData' dataframe to 'MyData.csv' again without including column names
write.table(MyData, "../results/MyData.csv", col.names=FALSE) 
