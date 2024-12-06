# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: DataWrang.R
# Description: demonstrates how to read, clean, and reshape data
# Version: 0.0.1
# Date: Oct 2024 

# Read the data from a CSV file without headers, convert it to a matrix, and store it in 'MyData'
MyData <- as.matrix(read.csv("../data/PoundHillData.csv", header = FALSE))

# Read the metadata from another CSV file, using ";" as the separator, and store it in 'MyMetaData'
MyMetaData <- read.csv("../data/PoundHillMetaData.csv", header = TRUE, sep = ";")

# Display the first few rows of 'MyData'
head(MyData)

# Display the dimensions of 'MyData' (rows and columns)
dim(MyData)

# Display the structure of 'MyData' (data types and column names)
str(MyData)

# Open the 'MyData' object in an interactive editor for manual editing
fix(MyData)

# Open the 'MyMetaData' object in an interactive editor for manual editing
fix(MyMetaData)

# Transpose 'MyData' (rows become columns and columns become rows) and reassign it to 'MyData'
MyData <- t(MyData)

# Display the first few rows of the transposed 'MyData'
head(MyData)

# Display the new dimensions of the transposed 'MyData'
dim(MyData)

# Replace empty strings in 'MyData' with 0
MyData[MyData == ""] = 0

# Convert 'MyData' (excluding the first row) into a data frame called 'TempData' with string columns as factors turned off
TempData <- as.data.frame(MyData[-1,], stringsAsFactors = F)

# Set the first row of 'MyData' as the column names of 'TempData'
colnames(TempData) <- MyData[1,]

# Load the 'reshape2' package, which provides functions for reshaping data
require(reshape2)

# Display help on the 'melt' function (used to reshape data)
?melt

# Reshape 'TempData' into a long format, creating a 'Species' column and a 'Count' column, while preserving 'Cultivation', 'Block', 'Plot', and 'Quadrat'
MyWrangledData <- melt(TempData, id=c("Cultivation", "Block", "Plot", "Quadrat"), variable.name = "Species", value.name = "Count")

# Convert 'Cultivation', 'Block', 'Plot', and 'Quadrat' columns to factors
MyWrangledData[, "Cultivation"] <- as.factor(MyWrangledData[, "Cultivation"])
MyWrangledData[, "Block"] <- as.factor(MyWrangledData[, "Block"])
MyWrangledData[, "Plot"] <- as.factor(MyWrangledData[, "Plot"])
MyWrangledData[, "Quadrat"] <- as.factor(MyWrangledData[, "Quadrat"])

# Convert the 'Count' column to integers
MyWrangledData[, "Count"] <- as.integer(MyWrangledData[, "Count"])

# Display the structure of the wrangled data
str(MyWrangledData)

# Display the first few rows of the wrangled data
head(MyWrangledData)

# Display the dimensions of the wrangled data
dim(MyWrangledData)
