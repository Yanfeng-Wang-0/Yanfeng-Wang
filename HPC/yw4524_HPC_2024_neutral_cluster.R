# CMEE 2024 HPC exercises R code pro forma
# For neutral model cluster run

rm(list=ls())
graphics.off()

# Load necessary functions
source("Demographic.R")
source("yw4524_HPC_2024_main.R")

# Read job index from cluster
iter <- as.numeric(Sys.getenv("PBS_ARRAY_INDEX"))
if (is.na(iter)) iter <- 1  # Default to 1 for local testing

# Set random seed for reproducibility
set.seed(iter)

# Define community sizes based on the job index
community_sizes <- c(500, 1000, 2500, 5000)
size_index <- ceiling(iter / 25)  # Assign 25 jobs to each size
size <- community_sizes[size_index]

# Define parameters for simulation
speciation_rate <- 0.1  # Use the provided speciation rate
interval_rich <- 1
interval_oct <- size / 10
burn_in_generations <- 8 * size
wall_time <- 11.5 * 60  # 11.5 hours in minutes

# Create output file name
output_file_name <- paste0("neutral_cluster_output_", iter, ".rda")

# Run the neutral model simulation
neutral_cluster_run(
  speciation_rate = speciation_rate, 
  size = size, 
  wall_time = wall_time, 
  interval_rich = interval_rich, 
  interval_oct = interval_oct, 
  burn_in_generations = burn_in_generations, 
  output_file_name = output_file_name
)