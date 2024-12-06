# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: PP_Regress.R
# Description: Visualizing and performing regression analysis for predator-prey data
# Version: 0.0.1
# Date: Nov 2024 

# Clear the workspace to remove all objects from memory
rm(list = ls())
setwd("~/Documents/CMEECourseWork/week4/code")

# Load necessary libraries
library(ggplot2)  # For data visualization
library(dplyr)    # For data manipulation
library(broom)    # For extracting regression results

# Clean the workspace
rm(list = ls())

# Set a random seed for reproducibility
set.seed(12345)

# Load predator-prey data
data <- read.csv("../data/EcolArchives-E089-51-D1.csv")

# Add log-transformed variables for Prey and Predator mass
data_combined <- data %>%
  mutate(
    LogPreyMass = log10(Prey.mass),
    LogPredatorMass = log10(Predator.mass)
  )

# Summarize data by feeding interaction type and predator lifestage
# This helps check the grouping structure and sample size
summary_stats <- data_combined %>%
  group_by(Type.of.feeding.interaction, Predator.lifestage) %>%
  summarize(count = n(), .groups = "drop")
print(summary_stats)

# Create a scatter plot with regression lines
plot_combined <- ggplot(data_combined, aes(x = Prey.mass, y = Predator.mass, color = Predator.lifestage)) + 
  geom_point(shape = 3) +  # Add scatter points with cross markers
  geom_smooth(method = "lm", se = TRUE, fullrange = TRUE) +  # Add linear regression lines
  facet_wrap(~Type.of.feeding.interaction, ncol = 1, strip.position = "right") +  # Separate plots by feeding interaction type
  scale_x_log10() +  # Log-transform x-axis
  scale_y_log10() +  # Log-transform y-axis
  theme_bw() +  # Apply a clean theme
  theme(
    legend.position = "bottom", 
    legend.title = element_text(size = 7, face = "bold"), 
    legend.text = element_text(size = 7)
  ) +
  guides(color = guide_legend(nrow = 1)) +  # Place legend in a single row
  labs(
    x = "Prey Mass in grams (log scale)",
    y = "Predator Mass in grams (log scale)",
    color = "Predator Lifestage"
  )

# Display the plot
print(plot_combined)

# Save the plot as a PDF
output_file <- "../results/PP_Visualising_regression_analysis.pdf"
ggsave(
  filename = output_file,  # File path to save the plot
  plot = plot_combined,    # The plot object to save
  width = 6,               # Width of the plot in inches
  height = 12,             # Height of the plot in inches
  dpi = 300                # Resolution in dots per inch
)
message("Plot saved as: ", output_file)

# Perform regression analysis for each feeding interaction and predator lifestage
regression_results <- data_combined %>%
  group_by(Type.of.feeding.interaction, Predator.lifestage) %>%  # Group data
  filter(n() > 1, sd(Prey.mass) > 0) %>%  # Keep groups with more than 1 sample and non-zero standard deviation
  do({
    model <- lm(Predator.mass ~ Prey.mass, data = .)  # Fit linear model
    tidy(model) %>%  # Extract regression results
      filter(term == "Prey.mass") %>%  # Filter for the slope term (Prey.mass)
      mutate(
        Regression.slope = estimate,  # Slope of the regression line
        Regression.intercept = coef(model)[1],  # Intercept of the regression line
        R.squared = summary(model)$adj.r.squared,  # Adjusted R-squared value
        Fstatistic = summary(model)$fstatistic[1],  # F-statistic
        P.value = p.value  # P-value for the slope
      )
  }) %>%
  ungroup() %>%  # Remove grouping to prevent issues with saving the results
  select(Type.of.feeding.interaction, Predator.lifestage, Regression.slope, Regression.intercept, R.squared, Fstatistic, P.value)

# Save the regression results to a CSV file
write.csv(regression_results, "../results/PP_Regress_Results.csv", row.names = FALSE)
message("Regression results saved to: ../results/PP_Regress_Results.csv")
