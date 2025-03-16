# CMEE 2024 HPC exercises R code pro forma
# For stochastic demographic model cluster run
# Clear workspace and turn off graphics
rm(list=ls())
graphics.off()

# Load necessary functions
source("Demographic.R")
source("yw4524_HPC_2024_main.R")

# Read job index from cluster
iter <- as.numeric(Sys.getenv("PBS_ARRAY_INDEX"))
if (is.na(iter)) iter <- 1  # Default to 1 for local testing

# Set random seed to ensure different parallel simulations
set.seed(iter)

# Define the projection and reproduction matrices
growth_matrix <- matrix(c(0.1, 0.0, 0.0, 0.0,
                          0.5, 0.4, 0.0, 0.0,
                          0.0, 0.4, 0.7, 0.0,
                          0.0, 0.0, 0.25, 0.4),
                        nrow=4, ncol=4, byrow=TRUE)

reproduction_matrix <- matrix(c(0.0, 0.0, 0.0, 2.6,
                                0.0, 0.0, 0.0, 0.0,
                                0.0, 0.0, 0.0, 0.0,
                                0.0, 0.0, 0.0, 0.0),
                              nrow=4, ncol=4, byrow=TRUE)

# Define clutch distribution
clutch_distribution <- c(0.06, 0.08, 0.13, 0.15, 0.16, 0.18, 0.15, 0.06, 0.03)

# Allocate initial conditions (each gets 25 jobs)
if (iter < 26){
  state <- state_initialise_adult(4,100)
  init_condition <- "big_adult"
  
} else if (25 < iter && iter < 51) {
  state <- state_initialise_adult(4,10)
  init_condition <- "small_adult"
  
} else if (50 < iter && iter < 76) {
  state <- state_initialise_spread(4,100)
  init_condition <- "big_spread"
  
} else {
  state <- state_initialise_spread(4,10)
  init_condition <- "small_spread"
}

# Initialize a list to store results
simulation_results <- vector("list", 150)

# Run the stochastic simulation 150 times
for (i in 1:150) {
  simulation_results[[i]] <- stochastic_simulation(
    state, growth_matrix, reproduction_matrix, clutch_distribution, 120
  )
}

# Save results in the Data folder with a unique filename
save(simulation_results, file = paste0("demographic_cluster_", iter, ".rda"))
