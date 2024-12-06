# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: Florida.R
# Description: calculates the observed correlation between the year and temperature, performs a permutation test to assess the statistical significance of the correlation, and visualizes the results in two PDF plots
# Version: 0.0.1
# Date: Nov 2024 

# Clear the workspace to remove all objects from memory
rm(list = ls())
setwd("~/Documents/CMEECourseWork/week4/code")

# Load the dataset containing annual mean temperature data
load("../data/KeyWestAnnualMeanTemperature.RData")

# Display the loaded variables and a preview of the dataset
cat("Loaded variables:\n")
print(ls())  # Lists all objects currently in the workspace
cat("First few rows of the dataset:\n")
print(head(ats))  # Displays the first few rows of the dataset
cat("Dataset class:", class(ats), "\n")  # Prints the class/type of the dataset

# Save a line plot of annual mean temperatures over time to a PDF file
pdf("../results/Temperature.pdf")
plot(
  ats$Year,  # X-axis: Years
  ats$Temp,  # Y-axis: Temperature (°C)
  xlab = "Year",
  ylab = "Temperature (°C)",
  type = "l",  # Line plot
  main = "Annual Mean Temperature in Key West, Florida (1901-2000)"
)
dev.off()  # Close the PDF file

# Calculate the correlation coefficient between year and temperature
obs_corr <- cor(ats$Year, ats$Temp)
cat(sprintf("Observed correlation coefficient: %.4f\n", obs_corr))  # Print the result

# Perform a permutation test to assess the significance of the correlation
set.seed(123)  # Set a random seed for reproducibility
num_permutations <- 10000  # Number of permutations
random_corrs <- replicate(num_permutations, cor(ats$Year, sample(ats$Temp)))  # Generate random correlations

# Calculate the p-value as the proportion of random correlations greater than or equal to the observed correlation
p_value <- mean(random_corrs >= obs_corr)
cat(sprintf("P-value from permutation test: %.4f\n", p_value))  # Print the p-value

# Save a histogram of the random correlations to a PDF file
pdf("../results/Florida_Correlation_Histogram.pdf", width = 18, height = 10)
hist_data <- hist(random_corrs, breaks = 30, plot = FALSE)  # Compute histogram data without plotting

# Plot the histogram of random correlation coefficients
hist(
  random_corrs, 
  breaks = 30,  # Number of bins
  main = "Distribution of Random Correlation Coefficients",
  xlab = "Correlation Coefficient", 
  ylab = "Frequency",
  col = "yellow",  # Bar color
  border = "black", 
  xlim = c(-0.6, 0.6),  # Set X-axis limits
  ylim = c(0, max(hist_data$counts) * 1.1)  # Set Y-axis limits dynamically
)
abline(v = obs_corr, col = "red", lwd = 2, lty = 2)  # Add a vertical line for the observed correlation

# Annotate the plot with the observed correlation coefficient and p-value
text(
  x = obs_corr, 
  y = max(hist_data$counts) * 1.05,  # Position above the histogram bars
  labels = sprintf("Observed correlation: %.4f\nP-value: %.4f", obs_corr, p_value),
  col = "blue", 
  pos = 2,  # Position the text to the left of the vertical line
  cex = 1, 
  font = 2
)

dev.off()  # Close the PDF file

# Print the conclusion based on the p-value
if (p_value < 0.05) {
  cat("Result: The observed correlation is statistically significant.\n")
} else {
  cat("Result: The observed correlation is not statistically significant.\n")
}
