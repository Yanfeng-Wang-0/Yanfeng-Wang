# CMEE 2024 HPC exercises R code main pro forma
# You don't HAVE to use this but it will be very helpful.
# If you opt to write everything yourself from scratch please ensure you use
# EXACTLY the same function and parameter names and beware that you may lose
# marks if it doesn't work properly because of not using the pro-forma.

name <- "Yanfeng Wang"
preferred_name <- "Yanfeng Wang"
email <- "yw4524@ic.ac.uk"
username <- "yw4524"

# Please remember *not* to clear the work space here, or anywhere in this file.
# If you do, it'll wipe out your username information that you entered just
# above, and when you use this file as a 'toolbox' as intended it'll also wipe
# away everything you're doing outside of the toolbox.  For example, it would
# wipe away any automarking code that may be running and that would be annoying!

# Section One: Stochastic demographic population model

# Question 0

# Function to initialize population with all individuals in the adult stage
state_initialise_adult <- function(num_stages, initial_size) {
  state <- rep(0, num_stages)  # Create a vector of zeros
  state[num_stages] <- initial_size  # Assign all individuals to last stage (adults)
  return(state)
}

# Function to initialize population evenly across life stages
state_initialise_spread <- function(num_stages, initial_size) {
  base <- floor(initial_size / num_stages)  # Base number per stage
  remainder <- initial_size %% num_stages  # Remaining individuals
  state <- rep(base, num_stages)  # Assign base number to each stage
  
  if (remainder > 0) {
    state[1:remainder] <- state[1:remainder] + 1  # Distribute remainder
  }
  return(state)
}


# Question 1
question_1 <- function() {
  # Ensure the Results directory exists
  results_dir <- "./"
  
  # Load required functions
  source("Demographic.R")
  
  # Define projection matrix
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
  
  projection_matrix <- growth_matrix + reproduction_matrix
  
  # Initialize populations
  initial_state_adult <- state_initialise_adult(num_stages=4, initial_size=100)
  initial_state_spread <- state_initialise_spread(num_stages=4, initial_size=100)
  
  # Run deterministic simulations
  sim_adult <- deterministic_simulation(initial_state_adult, projection_matrix, 24)
  sim_spread <- deterministic_simulation(initial_state_spread, projection_matrix, 24)
  
  # Prepare data for plotting
  time_steps <- 0:24
  df <- data.frame(Time = rep(time_steps, 2),
                   Population = c(sim_adult, sim_spread),
                   Condition = rep(c("All Adults", "Spread"), each = length(time_steps)))
  
  # Save plot to Results folder
  png(filename=paste0(results_dir, "question_1.png"), width = 600, height = 400)
  
  # Load ggplot2 and create plot
  library(ggplot2)
  plot <- ggplot(df, aes(x = Time, y = Population, color = Condition)) +
    geom_line(size = 1) +
    labs(title = "Deterministic Population Growth Over Time",
         x = "Time Steps",
         y = "Population Size") +
    theme_minimal()
  
  print(plot)  # Ensure it prints in the PNG file
  
  # Close the PNG device
  dev.off()
  
  return("The initial distribution of individuals in different life stages influences early population dynamics. 
  The 'All Adults' group grows steadily, while the 'Spread' group may initially grow faster due to having more juveniles.")
}

question_1()

# Define sum_vect function
sum_vect <- function(x, y) {
  len_x <- length(x)
  len_y <- length(y)
  
  # Pad the shorter vector with zeros
  if (len_x < len_y) {
    x <- c(x, rep(0, len_y - len_x))
  } else if (len_y < len_x) {
    y <- c(y, rep(0, len_x - len_y))
  }
  
  return(x + y)  # Return element-wise sum
}

# Question 2
question_2 <- function() {
  # Ensure the Results directory exists
  results_dir <- "./"
  
  # Load required functions
  source("Demographic.R")
  
  # Define matrices
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
  
  projection_matrix <- growth_matrix + reproduction_matrix
  
  # Define clutch distribution
  clutch_distribution <- c(0.06, 0.08, 0.13, 0.15, 0.16, 0.18, 0.15, 0.06, 0.03)
  
  # Initialize populations
  initial_state_adult <- state_initialise_adult(num_stages=4, initial_size=100)
  initial_state_spread <- state_initialise_spread(num_stages=4, initial_size=100)
  
  # Run stochastic simulations
  set.seed(123)  # Set seed for reproducibility
  sim_adult <- stochastic_simulation(initial_state_adult, growth_matrix, reproduction_matrix, clutch_distribution, 24)
  sim_spread <- stochastic_simulation(initial_state_spread, growth_matrix, reproduction_matrix, clutch_distribution, 24)
  
  # Prepare data for plotting
  time_steps <- 0:24
  df <- data.frame(Time = rep(time_steps, 2),
                   Population = c(sim_adult, sim_spread),
                   Condition = rep(c("All Adults", "Spread"), each = length(time_steps)))
  
  # Save plot to Results folder
  png(filename=paste0(results_dir, "question_2.png"), width = 600, height = 400)
  
  # Load ggplot2 and create plot
  library(ggplot2)
  plot <- ggplot(df, aes(x = Time, y = Population, color = Condition)) +
    geom_line(size = 1) +
    labs(title = "Stochastic Population Growth Over Time",
         x = "Time Steps",
         y = "Population Size") +
    theme_minimal()
  
  print(plot)  # Ensure it prints in the PNG file
  
  # Close the PNG device
  dev.off()
  
  return("Stochastic simulations introduce randomness, causing fluctuations in population growth. The 'All Adults' condition may show steadier growth, while 'Spread' may have more variability due to life stage distributions.")
}

question_2()

# Questions 3 and 4 involve writing code elsewhere to run your simulations on the cluster


# Question 5
# Load necessary library
library(ggplot2)

# Function to process results and generate the extinction probability plot
question_5 <- function() {
  # Define initial condition labels
  init_conditions <- c("big_adult", "small_adult", "big_spread", "small_spread")
  
  # Initialize extinction counters
  extinction_counts <- setNames(rep(0, length(init_conditions)), init_conditions)
  total_counts <- setNames(rep(0, length(init_conditions)), init_conditions)
  
  # Loop over simulation files
  for (iter in 1:100) {
    file_name <- paste0("demographic_cluster_", iter, ".rda")
    
    if (file.exists(file_name)) {
      load(file_name)  # Load the .rda file, which contains `simulation_results`
      
      # Determine the initial condition
      condition <- ifelse(iter < 26, "big_adult",
                          ifelse(iter < 51, "small_adult",
                                 ifelse(iter < 76, "big_spread", "small_spread")))
      
      # Count total simulations
      total_counts[condition] <- total_counts[condition] + length(simulation_results)
      
      # Count extinctions (final population size == 0)
      extinction_counts[condition] <- extinction_counts[condition] + sum(sapply(simulation_results, function(sim) tail(sim, 1) == 0))
    }
  }
  
  # Compute extinction proportions
  extinction_proportions <- extinction_counts / total_counts
  
  # Create dataframe for plotting
  df <- data.frame(
    Initial_Condition = names(extinction_proportions),
    Extinction_Probability = extinction_proportions
  )
  
  # Define the output file path
  output_file <- file.path("./", "question_5.png")
  
  # Open PNG device with required size (600x400 pixels)
  png(output_file, width = 600, height = 400, units = "px", bg = "white")
  
  # Plot extinction probabilities with white background
  extinction_plot <- ggplot(df, aes(x = Initial_Condition, y = Extinction_Probability, fill = Initial_Condition)) +
    geom_bar(stat = "identity") +
    theme_minimal(base_size = 14) +
    labs(title = "Extinction Probability by Initial Condition",
         x = "Initial Condition",
         y = "Proportion of Simulations Resulting in Extinction") +
    theme(axis.text.x = element_text(angle = 45, hjust = 1),
          panel.background = element_rect(fill = "white", colour = NA),
          plot.background = element_rect(fill = "white", colour = NA),
          panel.grid.major = element_line(colour = "gray90"),
          panel.grid.minor = element_line(colour = "gray95"))
  
  # Print the plot to save it
  print(extinction_plot)
  
  # Close PNG device
  Sys.sleep(0.1)
  dev.off()
  
  # Determine the most extinction-prone population
  most_extinct <- names(which.max(extinction_proportions))
  highest_prob <- max(extinction_proportions, na.rm = TRUE)
  
  # Explanation with more dynamic details
  explanation <- paste(
    "The population most likely to go extinct is:", most_extinct, 
    "with an extinction probability of", round(highest_prob * 100, 2), "%.",
    "\nThis is expected as smaller or more fragmented populations tend to be more vulnerable",
    "to stochastic events, genetic drift, and environmental fluctuations.",
    "\nIn contrast, larger populations or those with better distribution tend to buffer against",
    "random events, making them more resilient."
  )
  
  return(explanation)
}

question_5()

# Question 6
# Function to analyze stochastic vs deterministic simulation deviations
question_6 <- function() {
  # Load stochastic simulation results
  file_list <- list.files(pattern = "demographic_cluster_.*\\.rda")
  simulation_results <- list()
  
  # Identify relevant initial conditions (big_spread and small_spread)
  condition_labels <- c("big_spread", "small_spread")
  results_by_condition <- list("big_spread" = list(), "small_spread" = list())
  
  for (file in file_list) {
    load(file)  # Loads variable `simulation_results`
    
    # Determine which condition this file represents
    iter <- as.numeric(gsub("demographic_cluster_|\\.rda", "", file))
    
    if (iter > 50 && iter < 76) {
      condition <- "big_spread"
    } else if (iter >= 76) {
      condition <- "small_spread"
    } else {
      next  # Ignore files that are not of interest
    }
    
    results_by_condition[[condition]] <- append(results_by_condition[[condition]], simulation_results)
  }
  
  # Compute mean population size for each time step
  mean_population_trends <- list()
  
  for (condition in condition_labels) {
    if (length(results_by_condition[[condition]]) > 0) {
      all_sims <- do.call(rbind, results_by_condition[[condition]])  # Convert list to matrix
      mean_population_trends[[condition]] <- colMeans(all_sims, na.rm = TRUE)  # Average across simulations
    } else {
      mean_population_trends[[condition]] <- rep(NA, 120)  # Handle missing data
    }
  }
  
  # Compute deterministic model results
  growth_matrix <- matrix(c(0.1, 0.0, 0.0, 0.0,
                            0.5, 0.4, 0.0, 0.0,
                            0.0, 0.4, 0.7, 0.0,
                            0.0, 0.0, 0.25, 0.4),
                          nrow = 4, ncol = 4, byrow = TRUE)
  
  reproduction_matrix <- matrix(c(0.0, 0.0, 0.0, 2.6,
                                  0.0, 0.0, 0.0, 0.0,
                                  0.0, 0.0, 0.0, 0.0,
                                  0.0, 0.0, 0.0, 0.0),
                                nrow = 4, ncol = 4, byrow = TRUE)
  
  projection_matrix <- growth_matrix + reproduction_matrix
  sim_length <- 120  # Simulation duration in months
  
  # Compute deterministic model for large and small spread populations
  deterministic_big <- deterministic_simulation(state_initialise_spread(4, 100), projection_matrix, sim_length)
  deterministic_small <- deterministic_simulation(state_initialise_spread(4, 10), projection_matrix, sim_length)
  
  # Compute deviation (stochastic mean / deterministic)
  deviation_big <- mean_population_trends[["big_spread"]] / deterministic_big
  deviation_small <- mean_population_trends[["small_spread"]] / deterministic_small
  
  # Define the output file path
  output_file <- file.path("./", "question_6.png")
  
  # Open PNG device
  png(output_file, width = 600, height = 400, units = "px", bg = "white")
  
  # Create deviation plot
  plot(0:sim_length, deviation_big, type = "l", col = "blue", ylim = range(c(deviation_big, deviation_small), na.rm = TRUE),
       xlab = "Time Steps", ylab = "Deviation (Stochastic/Deterministic)", 
       main = "Deviation of Stochastic Model from Deterministic Model")
  lines(0:sim_length, deviation_small, col = "red")
  legend("topright", legend = c("Large Mixed", "Small Mixed"), col = c("blue", "red"), lty = 1)
  
  # Close PNG device
  Sys.sleep(0.1)
  dev.off()
  
  # Compute max deviation for explanation
  max_dev_big <- max(deviation_big, na.rm = TRUE)
  max_dev_small <- max(deviation_small, na.rm = TRUE)
  
  # Explanation with more details
  explanation <- paste(
    "The deviation from the deterministic model is lower for the large mixed population, suggesting that",
    "deterministic models approximate large populations more reliably due to the law of large numbers reducing stochastic variability.",
    "\n\nKey observations:",
    "\n- The maximum deviation for the large mixed population (big_spread) is", round(max_dev_big, 2),
    "\n- The maximum deviation for the small mixed population (small_spread) is", round(max_dev_small, 2),
    "\n\nThis confirms that smaller populations experience greater stochastic fluctuations, making their",
    "dynamics less predictable when compared to larger populations."
  )
  
  return(explanation)
}

question_6()

# Section Two: Individual-based ecological neutral theory simulation 

# Question 7
species_richness <- function(community) {
  return(length(unique(community)))  # Count unique species
}

# Question 8
init_community_max <- function(size) {
  return(1:size)  # Assign each individual a unique species ID
}

# Question 9
init_community_min <- function(size) {
  return(rep(1, size))  # Assign all individuals to species 1
}

# Question 10
choose_two <- function(max_value) {
  return(sample(1:max_value, 2, replace = FALSE))  # Select 2 unique numbers
}

# Question 11
neutral_step <- function(community) {
  indices <- choose_two(length(community))  # Select two random individuals
  community[indices[2]] <- community[indices[1]]  # Replace one individual with the other
  return(community)  # Return the updated community
}

# Question 12
neutral_generation <- function(community) {
  steps <- length(community)  # Number of replacement events = community size
  for (i in 1:steps) {
    community <- neutral_step(community)  # Apply neutral_step() repeatedly
  }
  return(community)  # Return the updated community
}

# Question 13
neutral_time_series <- function(community, duration) {
  richness_over_time <- numeric(duration + 1)  # Store species richness at each time step
  richness_over_time[1] <- species_richness(community)  # Initial species richness
  
  for (t in 1:duration) {
    community <- neutral_generation(community)  # Run one full generation
    richness_over_time[t + 1] <- species_richness(community)  # Record species richness
  }
  
  return(richness_over_time)  # Return species richness over time
}

# Question 14
question_14 <- function() {
  # Ensure the Results directory exists
  results_dir <- "./"
  
  # Define initial community
  community <- init_community_max(100)  # Start with 100 unique species
  duration <- 200  # Run simulation for 200 generations
  
  # Run simulation
  richness_over_time <- neutral_time_series(community, duration)
  
  # Create data frame for plotting
  time_steps <- 0:duration
  df <- data.frame(Time = time_steps, Species_Richness = richness_over_time)
  
  # Save plot to Results folder
  png(filename=paste0(results_dir, "question_14.png"), width = 600, height = 400)
  
  # Load ggplot2 and create plot
  library(ggplot2)
  plot <- ggplot(df, aes(x = Time, y = Species_Richness)) +
    geom_line(color="blue", size=1) +
    labs(title = "Neutral Model: Species Richness Over Time",
         x = "Generations",
         y = "Species Richness") +
    theme_minimal()
  
  print(plot)  # Ensure it prints in the PNG file
  
  # Close the PNG device
  dev.off()
  
  return("Species richness declines over time due to random extinctions in a neutral model. The rate of decline depends on initial diversity and population size.")
}

question_14()

# Question 15
neutral_step_speciation <- function(community, speciation_rate) {
  indices <- choose_two(length(community))  # Select two random individuals
  
  if (runif(1) < speciation_rate) {  
    # With probability `speciation_rate`, introduce a new species
    community[indices[2]] <- max(community) + 1  
  } else {  
    # Otherwise, replace as usual
    community[indices[2]] <- community[indices[1]]  
  }
  
  return(community)  # Return updated community
}

# Question 16
neutral_generation_speciation <- function(community, speciation_rate) {
  steps <- length(community)  # Number of replacements = community size
  
  for (i in 1:steps) {
    community <- neutral_step_speciation(community, speciation_rate)  # Apply speciation step
  }
  
  return(community)  # Return updated community after one full generation
}

# Question 17
neutral_time_series_speciation <- function(community, speciation_rate, duration) {
  richness_over_time <- numeric(duration + 1)  # Store species richness at each time step
  richness_over_time[1] <- species_richness(community)  # Initial species richness
  
  for (t in 1:duration) {
    community <- neutral_generation_speciation(community, speciation_rate)  # Run one full generation
    richness_over_time[t + 1] <- species_richness(community)  # Record species richness
  }
  
  return(richness_over_time)  # Return species richness over time
}

# Question 18
question_18 <- function() {
  # Load necessary library
  library(ggplot2)
  
  # Ensure the Results directory exists
  results_dir <- "./"
  
  # Define simulation parameters
  community_size <- 100  # Population size
  speciation_rate <- 0.1  # Speciation probability
  duration <- 200  # Run for 200 generations
  
  # Run neutral model with speciation for both initial conditions
  richness_max <- neutral_time_series_speciation(init_community_max(community_size), speciation_rate, duration)
  richness_min <- neutral_time_series_speciation(init_community_min(community_size), speciation_rate, duration)
  
  # Create data frame for plotting
  time_steps <- 0:duration
  df <- data.frame(
    Time = rep(time_steps, 2),
    Species_Richness = c(richness_max, richness_min),
    Condition = rep(c("Max Diversity", "Min Diversity"), each = length(time_steps))
  )
  
  # Save plot
  png(filename = paste0(results_dir, "question_18.png"), width = 600, height = 400)
  
  # Generate plot with two lines
  plot <- ggplot(df, aes(x = Time, y = Species_Richness, color = Condition)) +
    geom_line(size = 1) +
    labs(title = "Neutral Model with Speciation: Species Richness Over Time",
         x = "Generations",
         y = "Species Richness") +
    theme_minimal()
  
  print(plot)  # Ensure it prints in the PNG file
  
  # Close the PNG device
  dev.off()
  
  # Return explanation
  return("With speciation, species richness stabilizes at an equilibrium point instead of continuously declining. 
  The burn-in period ensures the system reaches equilibrium regardless of the initial condition. 
  The 'Max Diversity' condition initially loses species due to extinction, but new species emerge over time. 
  The 'Min Diversity' condition initially gains species through speciation until it reaches a stable equilibrium.")
}

question_18()

# Question 19
species_abundance <- function(community) {
  abundance_counts <- table(community)  # Count individuals per species
  sorted_abundances <- sort(as.numeric(abundance_counts), decreasing = TRUE)  # Sort in descending order
  return(sorted_abundances)  # Return the abundance distribution
}

# Question 20
octaves <- function(abundance_vector) {
  if (length(abundance_vector) == 0) {
    return(integer(0))  # Return empty vector if there are no species
  }
  
  bins <- floor(log2(abundance_vector)) + 1  # Convert species counts to octave bins
  octave_distribution <- table(bins)  # Count how many species fall into each bin
  
  # Convert table to a vector, ensuring all bins are represented
  max_bin <- max(bins)
  octave_vector <- integer(max_bin)
  octave_vector[as.integer(names(octave_distribution))] <- as.integer(octave_distribution)
  
  return(octave_vector)  # Return the octave distribution as a numeric vector
}

# Question 21
sum_vect <- function(x, y) {
  len_x <- length(x)
  len_y <- length(y)
  
  # Pad the shorter vector with zeros
  if (len_x < len_y) {
    x <- c(x, rep(0, len_y - len_x))
  } else if (len_y < len_x) {
    y <- c(y, rep(0, len_x - len_y))
  }
  
  return(x + y)  # Return element-wise sum
}

# Question 22
question_22 <- function() {
  # Ensure the Results directory exists
  results_dir <- "./"

  # Simulation parameters
  community_size <- 100
  speciation_rate <- 0.1
  burn_in_generations <- 200
  total_generations <- 2000
  interval <- 20  # Record every 20 generations
  
  # Initialize communities
  community_max <- init_community_max(community_size)
  community_min <- init_community_min(community_size)
  
  # Lists to store octave distributions
  max_octaves_list <- list()
  min_octaves_list <- list()
  
  # Burn-in phase (200 generations)
  for (gen in 1:burn_in_generations) {
    community_max <- neutral_generation_speciation(community_max, speciation_rate)
    community_min <- neutral_generation_speciation(community_min, speciation_rate)
  }
  
  # Main simulation loop (2000 generations, recording every 20)
  for (gen in 1:total_generations) {
    community_max <- neutral_generation_speciation(community_max, speciation_rate)
    community_min <- neutral_generation_speciation(community_min, speciation_rate)
    
    if (gen %% interval == 0) {  
      max_octaves_list <- append(max_octaves_list, list(octaves(species_abundance(community_max))))
      min_octaves_list <- append(min_octaves_list, list(octaves(species_abundance(community_min))))
    }
  }
  
  # Compute mean octaves manually (without sum_octaves)
  max_octave_length <- max(sapply(max_octaves_list, length))
  min_octave_length <- max(sapply(min_octaves_list, length))
  
  mean_max_octaves <- numeric(max_octave_length)
  mean_min_octaves <- numeric(min_octave_length)
  
  # Sum all octave vectors, handling different lengths
  for (oct in max_octaves_list) {
    mean_max_octaves[1:length(oct)] <- mean_max_octaves[1:length(oct)] + oct
  }
  for (oct in min_octaves_list) {
    mean_min_octaves[1:length(oct)] <- mean_min_octaves[1:length(oct)] + oct
  }
  
  # Compute the mean by dividing by the number of stored octaves
  mean_max_octaves <- mean_max_octaves / length(max_octaves_list)
  mean_min_octaves <- mean_min_octaves / length(min_octaves_list)
  
  # Prepare data for plotting
  df_max <- data.frame(Octave = seq_along(mean_max_octaves), Count = mean_max_octaves, Condition = "Max Initial Richness")
  df_min <- data.frame(Octave = seq_along(mean_min_octaves), Count = mean_min_octaves, Condition = "Min Initial Richness")
  df <- rbind(df_max, df_min)
  
  # Save plot to Results folder
  png(filename = paste0(results_dir, "question_22.png"), width = 600, height = 400)
  
  # Load ggplot2 and create bar plot
  library(ggplot2)
  plot <- ggplot(df, aes(x = Octave, y = Count, fill = Condition)) +
    geom_bar(stat = "identity", position = "dodge") +
    labs(title = "Species Abundance Distribution After 2000 Generations",
         x = "Octave (log2 abundance bins)",
         y = "Mean Count") +
    theme_minimal()
  
  print(plot)  # Ensure it prints in the PNG file
  
  # Close the PNG device
  dev.off()
  
  # Return interpretation
  return("After 2000 generations, the species abundance distribution converges regardless of the initial condition. The burn-in period ensures that the system reaches a dynamic equilibrium, demonstrating that long-term species abundance depends more on speciation and extinction dynamics than initial species richness.")
}

question_22()

# Question 23

neutral_cluster_run <- function(speciation_rate, size, wall_time, interval_rich, interval_oct, burn_in_generations, output_file_name) {
  # Initialize the community with minimal diversity
  community <- rep(1, size)  # All individuals belong to one species initially
  
  # Initialize storage variables
  time_series <- numeric()  # Stores species richness during burn-in
  abundance_list <- list()  # Stores species abundance octaves
  generation <- 0  # Generation counter
  start_time <- proc.time()[3]  # Start time in seconds
  wall_time_seconds <- wall_time * 60  # Convert wall time from minutes to seconds
  
  # Burn-in phase (only record richness at interval_rich)
  while (generation < burn_in_generations) {
    community <- neutral_generation_speciation(community, speciation_rate)
    generation <- generation + 1
    
    # Store species richness at specified intervals
    if (generation %% interval_rich == 0) {
      time_series <- c(time_series, species_richness(community))
    }
  }
  
  # Post burn-in: Main simulation loop
  while (TRUE) {
    community <- neutral_generation_speciation(community, speciation_rate)
    generation <- generation + 1
    
    # Store abundance octaves at specified intervals
    if (generation %% interval_oct == 0) {
      abundance_list[[length(abundance_list) + 1]] <- octaves(species_abundance(community))
    }
    
    # Stop when wall-time is exceeded
    elapsed_time <- proc.time()[3] - start_time
    if (elapsed_time >= wall_time_seconds) break
  }
  
  # Validation check for abundance_list length
  expected_abundance_length <- (generation - burn_in_generations) / (size / 100)
  if (length(abundance_list) != round(expected_abundance_length)) {
    warning(sprintf("Mismatch: Expected abundance list length %d, but got %d", 
                    round(expected_abundance_length), length(abundance_list)))
  }
  
  # Save results to file
  save(time_series, abundance_list, community, speciation_rate, size, wall_time, 
       interval_rich, interval_oct, burn_in_generations, elapsed_time, generation, 
       file = output_file_name)
  
  # Return results for debugging
  return(list(
    time_series = time_series,
    abundance_list = abundance_list,
    final_community = community,
    speciation_rate = speciation_rate,
    size = size,
    wall_time = wall_time,
    interval_rich = interval_rich,
    interval_oct = interval_oct,
    burn_in_generations = burn_in_generations,
    total_time = elapsed_time,
    total_generations = generation
  ))
}

# Questions 24 and 25 involve writing code elsewhere to run your simulations on
# the cluster

# Question 26 

# Function to analyze simulation results from cluster processing

process_neutral_cluster_results <- function() {
  
  # Define different population sizes
  population_sizes <- c(500, 1000, 2500, 5000)
  
  # Initialize lists to store cumulative octaves and file counts for each population size
  avg_octave_data <- setNames(vector("list", length(population_sizes)), as.character(population_sizes))
  file_counter <- setNames(rep(0, length(population_sizes)), as.character(population_sizes))
  
  # Retrieve all .rda files related to cluster simulations
  rda_files <- list.files(pattern = "neutral_cluster_output_.*\\.rda")
  
  # Loop through each .rda file
  for (rda in rda_files) {
    
    load(rda)  # Loads variables: `abundance_list`, `size`
    
    # Ensure `size` is valid and matches one of the predefined population sizes
    if (exists("size") && size %in% population_sizes) {
      
      size_label <- as.character(size)
      
      # Initialize the cumulative octave vector if not already initialized
      if (is.null(avg_octave_data[[size_label]])) {
        avg_octave_data[[size_label]] <- rep(0, max(sapply(abundance_list, length)))
      }
      
      # Aggregate octaves from each file
      for (octave in abundance_list) {
        if (!is.null(octave)) {
          
          # Ensure vector lengths remain consistent
          if (length(octave) > length(avg_octave_data[[size_label]])) {
            avg_octave_data[[size_label]] <- c(avg_octave_data[[size_label]], rep(0, length(octave) - length(avg_octave_data[[size_label]])))
          }
          
          avg_octave_data[[size_label]] <- sum_vect(avg_octave_data[[size_label]], octave)
        }
      }
      
      # Increase the file count for this population size
      file_counter[[size_label]] <- file_counter[[size_label]] + 1
    }
  }
  
  # Compute the average by dividing by the number of processed files
  for (size in names(avg_octave_data)) {
    if (!is.null(avg_octave_data[[size]]) && sum(avg_octave_data[[size]]) > 0 && file_counter[[size]] > 0) {
      avg_octave_data[[size]] <- avg_octave_data[[size]] / file_counter[[size]]
    }
  }
  
  # Save the processed data
  save(avg_octave_data, file = "processed_cluster_results.rda")
}

# Execute the analysis function
process_neutral_cluster_results()

# Load required library
library(ggplot2)

# Function to visualize the results from processed .rda data
plot_neutral_cluster_results <- function() {
  # Load processed data
  load("processed_cluster_results.rda")
  
  # Validate if data is available
  if (!exists("avg_octave_data") || length(avg_octave_data) == 0) {
    stop("Error: No processed results found. Execute analyze_cluster_simulation_results() first.")
  }
  
  # Convert list data into a data frame for visualization
  visualization_data <- data.frame()
  for (size in names(avg_octave_data)) {
    octave_vals <- avg_octave_data[[size]]
    if (length(octave_vals) > 0) {
      df <- data.frame(
        Octave = seq_along(octave_vals),
        Avg_Abundance = as.numeric(octave_vals),
        Population_Size = factor(size, levels = c("500", "1000", "2500", "5000"))  # Ensure correct ordering
      )
      visualization_data <- rbind(visualization_data, df)
    }
  }
  
  # Ensure the dataset is not empty
  if (nrow(visualization_data) == 0) {
    stop("Error: No data available for visualization. Verify neutral_cluster_simulation_results() execution.")
  }
  
  # Open PNG device with specified dimensions and background color
  png("plot_neutral_cluster_results.png", width = 800, height = 500, units = "px", bg = "white")
  
  # Generate multi-panel bar plot
  plot <- ggplot(visualization_data, aes(x = factor(Octave), y = Avg_Abundance)) +
    geom_bar(stat = "identity", fill = "steelblue") +
    facet_wrap(~ Population_Size, scales = "free") +
    labs(title = "Average Species Abundance Distribution",
         x = "Octave",
         y = "Average Species Abundance") +
    theme_minimal(base_size = 14) +  # Clean visual style
    theme(
      panel.background = element_rect(fill = "white", colour = NA),  # White panel background
      plot.background = element_rect(fill = "white", colour = NA),   # White outer background
      panel.grid.major = element_line(colour = "gray90"),
      panel.grid.minor = element_line(colour = "gray95"),
      plot.title = element_text(hjust = 0.5, face = "bold", size = 16)  # Centered and bold title
    )
  
  # Render the plot to the PNG device
  print(plot)
  
  # Close PNG device
  dev.off()
}

# Execute the plotting function
plot_neutral_cluster_results()

# Challenge questions - these are substantially harder and worth fewer marks.
# I suggest you only attempt these if you've done all the main questions. 

# Challenge question A
Challenge_A <- function() {
  library(ggplot2)
  
  # Ensure the Results directory exists
  results_dir <- "./"
  if (!dir.exists(results_dir)) dir.create(results_dir, recursive = TRUE)
  
  # Retrieve all .rda files matching the pattern
  sim_files <- list.files(pattern = "^demographic_cluster_\\d+\\.rda$")
  
  # Store processed simulation data
  sim_data_list <- list()
  sim_id <- 1
  
  for (sim_file in sim_files) {
    load(sim_file)  # Assumes `simulation_results` is loaded
    
    # Extract iteration number from filename
    iter_num <- as.integer(gsub("demographic_cluster_|\\.rda", "", sim_file))
    
    # Define initial condition categories
    condition_labels <- c("large adult", "small adult", "large mixed", "small mixed")
    initial_condition <- condition_labels[(iter_num %/% 25) + 1]
    
    # Process simulation results
    for (sim_run in seq_along(simulation_results)) {
      time_series <- simulation_results[[sim_run]]
      
      # Construct a dataframe for each simulation run
      df <- data.frame(
        simulation_number = sim_id,
        initial_condition = initial_condition,
        time_step = seq_along(time_series) - 1,
        population_size = time_series
      )
      
      sim_data_list[[length(sim_data_list) + 1]] <- df
      sim_id <- sim_id + 1
    }
  }
  
  # Merge all data into one dataframe
  population_data <- do.call(rbind, sim_data_list)
  
  # Save the processed data
  save(population_data, file = file.path(results_dir, "population_size_df.rda"))
  
  # Generate the population plot
  population_plot <- ggplot(population_data, aes(x = time_step, y = population_size, 
                                                 group = simulation_number, color = initial_condition)) +
    geom_line(alpha = 0.5, size = 0.5) +
    labs(title = "Population Dynamics Over Time", x = "Time Steps", y = "Population Size") +
    theme_light(base_size = 12) +
    theme(
      legend.position = "bottom",
      plot.title = element_text(size = 14, face = "bold", hjust = 0.5)
    ) +
    scale_color_manual(values = c("large adult" = "blue", 
                                  "small adult" = "red", 
                                  "large mixed" = "green", 
                                  "small mixed" = "purple"))
  
  # Save the plot with specified resolution
  ggsave(file.path(results_dir, "Challenge_A.png"), population_plot, 
         width = 600 / 72, height = 400 / 72, units = "in", dpi = 72, bg = "white")
  
  return(population_data)
}

Challenge_A()

# Challenge question B
Challenge_B <- function() {
  library(ggplot2)
  
  # Ensure the Results directory exists
  results_dir <- "./"
  
  # Define simulation parameters
  num_generations <- 200  # Adjust as needed
  num_repeats <- 100  # Number of simulations
  community_size <- 100  # Population size
  speciation_rate <- 0.1  # Speciation probability
  
  # Function to run multiple simulations and return species richness over time
  run_simulations <- function(initialization_function) {
    richness_matrix <- matrix(0, nrow = num_repeats, ncol = num_generations + 1)
    
    for (i in 1:num_repeats) {
      community <- initialization_function(community_size)
      richness_matrix[i, ] <- neutral_time_series_speciation(community, speciation_rate, num_generations)
    }
    
    mean_richness <- apply(richness_matrix, 2, mean)
    ci_upper <- apply(richness_matrix, 2, function(x) quantile(x, 0.986))  # 97.2% CI upper bound
    ci_lower <- apply(richness_matrix, 2, function(x) quantile(x, 0.028))  # 97.2% CI lower bound
    
    return(list(mean_richness = mean_richness, ci_upper = ci_upper, ci_lower = ci_lower))
  }
  
  # Run simulations for min and max initial richness
  results_max <- run_simulations(init_community_max)
  results_min <- run_simulations(init_community_min)
  
  # Prepare data for plotting
  time_steps <- 0:num_generations
  df <- data.frame(
    Time = rep(time_steps, 2),
    Mean_Richness = c(results_max$mean_richness, results_min$mean_richness),
    CI_Upper = c(results_max$ci_upper, results_min$ci_upper),
    CI_Lower = c(results_max$ci_lower, results_min$ci_lower),
    Condition = rep(c("Max Initial Richness", "Min Initial Richness"), each = length(time_steps))
  )
  
  # Save plot to Results folder
  png(filename = paste0(results_dir, "Challenge_B.png"), width = 600, height = 400)
  
  # Generate plot
  plot <- ggplot(df, aes(x = Time, y = Mean_Richness, color = Condition, fill = Condition)) +
    geom_line(size = 1) +
    geom_ribbon(aes(ymin = CI_Lower, ymax = CI_Upper), alpha = 0.2) +
    labs(title = "Mean Species Richness Over Time with 97.2% CI",
         x = "Generations",
         y = "Mean Species Richness") +
    theme_minimal()
  
  print(plot)  # Ensure it prints in the PNG file
  dev.off()
  
  # Estimate the number of generations to reach equilibrium
  threshold <- 0.01  # Define threshold for equilibrium detection
  equilibrium_time <- which(abs(diff(results_max$mean_richness)) < threshold)[1]  # First time step reaching stability
  
  return(paste("The system reaches dynamic equilibrium after approximately", equilibrium_time, "generations."))
}

Challenge_B()

# Challenge question C
Challenge_C <- function() {
  library(ggplot2)
  
  # Ensure the Results directory exists
  results_dir <- "./"
  
  # Define parameters
  total_individuals <- 100  
  time_steps <- 200        
  speciation_rate <- 0.1 
  simulations_per_level <- 50      
  richness_values <- seq(1, 100, by = 10)  # Different initial species richness levels
  
  # Function to generate initial community
  create_initial_population <- function(size, richness) rep(1:richness, length.out = size)
  
  # Storage for simulation results
  simulation_results <- list()
  
  for (richness in richness_values) {
    # Run multiple replicates
    all_time_series <- matrix(0, nrow = time_steps + 1, ncol = simulations_per_level)
    
    for (rep in 1:simulations_per_level) {
      community <- create_initial_population(total_individuals, richness)
      time_series <- neutral_time_series_speciation(community, speciation_rate, time_steps)
      all_time_series[, rep] <- time_series
    }
    
    # Compute mean species richness at each time step
    mean_richness <- rowMeans(all_time_series, na.rm = TRUE)
    
    # Store results
    simulation_results[[as.character(richness)]] <- data.frame(
      Time = 0:time_steps,
      Species_Richness = mean_richness,
      Initial_Richness = richness
    )
  }
  
  # Combine all results into a single data frame
  plot_data <- do.call(rbind, simulation_results)
  
  # Set output file path
  output_file_path <- file.path(results_dir, "Challenge_C.png")
  
  # Generate and save the plot
  png(output_file_path, width = 800, height = 500)
  
  plot <- ggplot(plot_data, aes(x = Time, y = Species_Richness, 
                                color = as.factor(Initial_Richness), group = Initial_Richness)) +
    geom_line(size = 0.7, alpha = 0.8) +
    labs(title = "Mean Species Richness Over Time for Different Initial Conditions",
         x = "Generations", y = "Mean Species Richness",
         color = "Initial Richness") +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5, face = "bold", size = 14))
  
  print(plot)  # Ensure the plot is printed before closing the device
  
  dev.off()
  
  return(paste("Plot successfully saved at:", output_file_path))
}

Challenge_C()


# Challenge question D
# Load necessary library
library(ggplot2)

# Function to process simulation data and determine burn-in period
Challenge_D <- function() {
  # Ensure the Results directory exists
  results_dir <- "./"
  
  # Get list of all .rda files containing simulation results
  file_list <- list.files(pattern = "neutral_cluster_output_.*\\.rda")
  
  if (length(file_list) == 0) {
    stop("No simulation files found. Ensure your cluster outputs are available.")
  }
  
  # Initialize storage for species richness over time for each community size
  richness_data <- list()
  community_sizes <- c(500, 1000, 2500, 5000)
  
  # Loop through each simulation result file
  for (file in file_list) {
    load(file)  # Loads variables: `time_series`, `size`
    
    # Ensure `size` exists and matches one of the expected community sizes
    if (exists("size") && size %in% community_sizes) {
      size_key <- as.character(size)
      
      # Store time-series richness data for each size
      if (!size_key %in% names(richness_data)) {
        richness_data[[size_key]] <- list()
      }
      
      richness_data[[size_key]][[length(richness_data[[size_key]]) + 1]] <- time_series
    }
  }
  
  # Compute mean richness over time for each community size
  mean_richness_list <- list()
  
  for (size in names(richness_data)) {
    # Convert list of vectors into a matrix for averaging
    richness_matrix <- do.call(rbind, lapply(richness_data[[size]], function(x) x[1:min(sapply(richness_data[[size]], length))]))
    
    # Compute mean richness across multiple runs
    mean_richness_list[[size]] <- colMeans(richness_matrix, na.rm = TRUE)
  }
  
  # Prepare data for ggplot2
  time_steps <- seq_len(max(sapply(mean_richness_list, length))) - 1
  plot_data <- data.frame()
  
  for (size in names(mean_richness_list)) {
    df <- data.frame(
      Generation = time_steps,
      Mean_Richness = mean_richness_list[[size]][1:length(time_steps)],
      Community_Size = factor(size, levels = as.character(community_sizes))
    )
    plot_data <- rbind(plot_data, df)
  }
  
  # Create the plot
  plot <- ggplot(plot_data, aes(x = Generation, y = Mean_Richness, color = Community_Size)) +
    geom_line(size = 1) +
    labs(title = "Mean Species Richness Over Generations",
         x = "Simulation Generations",
         y = "Mean Species Richness",
         color = "Community Size") +
    theme_minimal()
  
  # Save the plot
  png(filename = paste0(results_dir, "Challenge_D.png"), width = 800, height = 500)
  print(plot)
  dev.off()
  
  return("Challenge_D completed: Plot saved as 'Challenge_D.png'")
}

# Run Challenge_D
Challenge_D()

# Challenge question E
# Load necessary library
library(ggplot2)

# Function to perform coalescence simulation
coalescence_simulation <- function(J, v) {
  # Step (a): Initialize lineages vector with all 1s
  lineages <- rep(1, J)
  
  # Step (b): Initialize an empty abundances vector
  abundances <- c()
  
  # Step (c): Set N = J
  N <- J
  
  # Step (d): Compute theta
  theta <- v * (J - 1) / (1 - v)
  
  # Perform the coalescence process
  while (N > 1) {
    # Step (e): Choose index j at random from lineages
    j <- sample(1:N, 1)
    
    # Step (f): Pick a random number between 0 and 1
    randnum <- runif(1)
    
    # Step (g): Speciation event
    if (randnum < theta / (theta + N - 1)) {
      abundances <- c(abundances, lineages[j])  # Append to abundances
    } else {
      # Step (h): Choose another index i at random (ensuring i ≠ j)
      i <- sample(setdiff(1:N, j), 1)
      lineages[i] <- lineages[i] + lineages[j]  # Merge lineages
    }
    
    # Step (i): Remove lineage j
    lineages <- lineages[-j]
    
    # Step (j): Decrease N
    N <- N - 1
  }
  
  # Step (l): Add the last remaining lineage to abundances
  abundances <- c(abundances, lineages)
  
  # Step (m): Return simulated species abundance vector
  return(sort(abundances, decreasing = TRUE))
}

# Function to pad vectors to the same length
pad_abundance <- function(vec, target_length) {
  if (length(vec) < target_length) {
    return(c(vec, rep(0, target_length - length(vec))))  # Pad with zeros
  } else {
    return(vec)
  }
}

# Function to compare coalescence results with cluster simulations
Challenge_E <- function() {
  # Define parameters
  community_sizes <- c(500, 1000, 2500, 5000)
  speciation_rate <- 0.1  # Same as in the cluster simulations
  
  # Ensure results directory exists
  results_dir <- "./"
  
  # Load cluster simulation results
  file_list <- list.files(pattern = "neutral_cluster_output_.*\\.rda")
  cluster_results <- list()
  
  # Extract cluster-based abundance distributions
  for (file in file_list) {
    load(file)  # Loads `abundance_list`, `size`
    
    if (exists("size") && size %in% community_sizes) {
      if (!is.list(cluster_results[[as.character(size)]])) {
        cluster_results[[as.character(size)]] <- list()
      }
      cluster_results[[as.character(size)]][[length(cluster_results[[as.character(size)]]) + 1]] <- abundance_list
    }
  }
  
  # Compute mean octaves from cluster results
  mean_cluster_octaves <- lapply(cluster_results, function(lst) {
    do.call(rbind, lapply(lst, function(x) x))
  })
  
  # Perform coalescence simulations
  coalescence_results <- lapply(community_sizes, function(J) {
    replicate(100, coalescence_simulation(J, speciation_rate), simplify = FALSE)
  })
  
  # Determine the maximum octave length across all distributions
  max_octave_length <- max(
    sapply(mean_cluster_octaves, length),
    sapply(coalescence_results, function(lst) max(sapply(lst, length)))
  )
  
  # Apply padding to coalescence and cluster results
  mean_cluster_octaves <- lapply(mean_cluster_octaves, function(x) pad_abundance(x, max_octave_length))
  mean_coalescence_octaves <- lapply(coalescence_results, function(lst) {
    lapply(lst, function(x) pad_abundance(x, max_octave_length))
  })
  
  # Compute mean abundance from coalescence results
  mean_coalescence_octaves <- lapply(mean_coalescence_octaves, function(lst) {
    colMeans(do.call(rbind, lst), na.rm = TRUE)
  })
  
  # Create consistent octave sequence
  octave_seq <- seq_len(max_octave_length)
  
  # Prepare data for plotting
  plot_data <- data.frame()
  
  for (i in seq_along(community_sizes)) {
    size <- as.character(community_sizes[i])
    
    df_cluster <- data.frame(
      Octave = octave_seq,
      Mean_Abundance = mean_cluster_octaves[[size]],
      Method = "Cluster",
      Community_Size = factor(size, levels = as.character(community_sizes))
    )
    
    df_coalescence <- data.frame(
      Octave = octave_seq,
      Mean_Abundance = mean_coalescence_octaves[[i]],
      Method = "Coalescence",
      Community_Size = factor(size, levels = as.character(community_sizes))
    )
    
    plot_data <- rbind(plot_data, df_cluster, df_coalescence)
  }
  
  # Generate the plot
  plot <- ggplot(plot_data, aes(x = factor(Octave), y = Mean_Abundance, fill = Method)) +
    geom_bar(stat = "identity", position = "dodge") +
    facet_wrap(~ Community_Size, scales = "free") +
    labs(title = "Comparison of Cluster vs. Coalescence Species Abundance",
         x = "Octave (log2 abundance bins)",
         y = "Mean Species Abundance",
         fill = "Simulation Method") +
    theme_minimal()
  
  # Save the plot
  png(filename = paste0(results_dir, "Challenge_E.png"), width = 800, height = 500)
  print(plot)
  dev.off()
  
  # Return explanation
  return("The coalescence simulation is significantly faster because it simulates the genealogical history of individuals 
  backwards in time rather than explicitly modeling each individual forward in time. The computational savings come from 
  reducing the number of necessary operations per individual, as only lineage merging and speciation are tracked.")
}

# Run Challenge_E
Challenge_E()


