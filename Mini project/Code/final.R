library(dplyr)
library(readr)
library(Rlof)   
library(car)    
library(mgcv)   
library(minpack.lm)  
library(nnet)  
library(randomForest)
library(ggplot2)

input_path <- "../Data/LogisticGrowthData.csv"
output_path <- "../Data/Cleaned_LogisticGrowthData.csv"

data_df <- read_csv(input_path)
cat("Loaded", ncol(data_df), "columns.\n")

cat("PopBio Units: ", unique(data_df$PopBio_units), "\n")
cat("Time Units: ", unique(data_df$Time_units), "\n")

data_df <- data_df %>%
  mutate(ID = paste(Species, Temp, Medium, Citation, sep = "_"))

cat("Unique IDs:", length(unique(data_df$ID)), "\n")

unique_ids <- unique(data_df$ID)
id_map <- data.frame(ID = unique_ids, ID_Number = 1:length(unique_ids))

data_df <- left_join(data_df, id_map, by = "ID")

data_df <- data_df %>%
  relocate(ID, .before = everything()) %>%  
  relocate(ID_Number, .after = Citation) 

data_df <- data_df %>%
  filter(PopBio > 0, Time > 0) %>%
  mutate(LogPopBio = log(PopBio)) %>%
  na.omit() %>%
  distinct()

set.seed(42)
lof_scores <- lof(data_df[, c("Time", "PopBio")], k = 10)

if (any(is.na(lof_scores) | is.infinite(lof_scores))) {
  cat("Deleting NA & Inf")
  valid_indices <- !is.na(lof_scores) & !is.infinite(lof_scores)
  data_df <- data_df[valid_indices, ]
  lof_scores <- lof_scores[valid_indices]
}

lof_threshold <- quantile(lof_scores, 0.95, na.rm = TRUE)
data_df <- data_df %>% mutate(lof_score = lof_scores, is_outlier_lof = lof_score > lof_threshold)

K_value <- max(data_df$PopBio, na.rm = TRUE)
if (is.na(K_value) || K_value <= 0) {
  stop("Error, K is invalid！")
}

exp_model <- lm(LogPopBio ~ Time, data = data_df)
data_df <- data_df %>% mutate(exp_resid_z = abs(scale(residuals(exp_model))), is_outlier_exp = exp_resid_z > 3)

gompertz_model <- nlsLM(
  LogPopBio ~ log(K) - b * exp(-r * Time),
  data = data_df,
  start = list(K = K_value, b = 1, r = 0.01),
  control = nls.lm.control(maxiter = 1000)
)
data_df <- data_df %>% mutate(gompertz_resid_z = abs(scale(residuals(gompertz_model))), is_outlier_gompertz = gompertz_resid_z > 3)

logistic_model <- nlsLM(
  LogPopBio ~ log(K / (1 + exp(-r * (Time - t0)))),
  data = data_df,
  start = list(K = K_value, r = 0.01, t0 = median(data_df$Time, na.rm = TRUE)),
  control = nls.lm.control(maxiter = 1000)
)
data_df <- data_df %>% mutate(logistic_resid_z = abs(scale(residuals(logistic_model))), is_outlier_logistic = logistic_resid_z > 3)

data_df <- data_df %>% mutate(LogTime = log(Time))
power_model <- lm(LogPopBio ~ LogTime, data = data_df)
data_df <- data_df %>% mutate(power_resid_z = abs(scale(residuals(power_model))), is_outlier_power = power_resid_z > 3)

gam_model <- gam(LogPopBio ~ s(Time, bs = "cs"), data = data_df)
data_df <- data_df %>% mutate(gam_resid_z = abs(scale(residuals(gam_model))), is_outlier_gam = gam_resid_z > 3)

normalize <- function(x) { (x - min(x, na.rm = TRUE)) / (max(x, na.rm = TRUE) - min(x, na.rm = TRUE)) }
data_df <- data_df %>%
  mutate(NormTime = normalize(Time), NormLogPopBio = normalize(LogPopBio))

nn_model <- nnet(NormLogPopBio ~ NormTime, data = data_df, size = 5, linout = TRUE)
data_df <- data_df %>% mutate(nn_resid_z = abs(scale(residuals(nn_model))), is_outlier_nn = nn_resid_z > 3)

set.seed(42)
rf_model <- randomForest(LogPopBio ~ Time, data = data_df, ntree = 500, mtry = 1)
rf_pred <- predict(rf_model, newdata = data_df)
rf_resid <- data_df$LogPopBio - rf_pred
data_df <- data_df %>% mutate(rf_resid_z = abs(scale(rf_resid)), is_outlier_rf = rf_resid_z > 3)

data_df_clean <- data_df %>%
  filter(!(is_outlier_lof | is_outlier_exp | is_outlier_gompertz | is_outlier_logistic | 
             is_outlier_power | is_outlier_gam | is_outlier_nn | is_outlier_rf))

invalid_cols <- sapply(data_df_clean, function(col) is.list(col) | is.matrix(col))
if (any(invalid_cols)) {
  cat("Removing invlid columns：\n", names(data_df_clean)[invalid_cols], "\n")
  data_df_clean <- data_df_clean[, !invalid_cols]
}

data_df_clean <- data_df_clean %>%
  select_if(~ is.numeric(.) | is.character(.) | is.factor(.))

output_dir <- dirname(output_path)
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

if (file.exists(output_path)) {
  file.remove(output_path)
}

write_csv(data_df_clean, output_path)
cat("Data cleaned!")

library(dplyr)
library(readr)
library(ggplot2)
library(mgcv)
library(minpack.lm)
library(nnet)
library(randomForest)
library(caret)
library(Metrics)
library(tidyr)

data_path <- "../Data/Cleaned_LogisticGrowthData.csv"
results_dir <- "../Results/Per_ID_Comparison/" 
metrics_results <- "../Results/model_comparison_metrics.csv" 
summary_results <- "../Results/model_comparison_summary.csv" 

data <- read_csv(data_path)

data_df <- data %>%
  filter(Time > 0, PopBio > 0) %>%
  mutate(LogPopBio = log(PopBio)) %>%
  na.omit()

unique_ids <- unique(data_df$ID_Number)
cat("finds unique ID", length(unique_ids))

rainbow_colors <- c(
  "Predicted_Exp" = "#1F78B4",
  "Predicted_Gompertz" = "#FF7F00",
  "Predicted_Logistic" = "#33A02C",
  "Predicted_Power" = "#A50026",
  "Predicted_GAM" = "#6A3D9A",
  "Predicted_NN" = "#FFD700",
  "Predicted_RF" = "#E31A89"
)

best_r2_counts <- rep(0, 7)
best_aic_counts <- rep(0, 7)
best_bic_counts <- rep(0, 7)
model_names <- c("Exp", "Gompertz", "Logistic", "Power", "GAM", "NN", "RF")

compute_metrics <- function(model, data, pred_col) {
  residuals <- data[[pred_col]] - data$LogPopBio
  SSE <- sum(residuals^2, na.rm = TRUE)
  SST <- sum((data$LogPopBio - mean(data$LogPopBio, na.rm = TRUE))^2, na.rm = TRUE)
  r2 <- 1 - (SSE / SST)
  n <- nrow(data)
  p <- length(coef(model))
  aic <- n * log(SSE / n) + 2 * p
  bic <- n * log(SSE / n) + log(n) * p
  return(list(R2 = r2, AIC = aic, BIC = bic))
}

metrics_list <- list()

if (!dir.exists(results_dir)) {
  dir.create(results_dir, recursive = TRUE)
  cat("Directory created:", results_dir, "\n")
}

for (uid in unique_ids) {
  cat("processing Unique ID_Number:", uid, "\n")
  
  data_subset <- data_df %>% filter(ID_Number == uid)
  if (nrow(data_subset) < 5) {
    cat("skip \n")
    next
  }
  
  num_unique_time <- length(unique(data_subset$Time))
  adaptive_knots <- min(10, num_unique_time)
  
  exp_model <- lm(LogPopBio ~ Time, data = data_subset)
  data_subset$Predicted_Exp <- predict(exp_model, newdata = data_subset)
  
  gompertz_model <- tryCatch(
    nlsLM(LogPopBio ~ log(K) - b * exp(-r * Time), data = data_subset,
          start = list(K = max(data_subset$PopBio), b = 1, r = 0.01),
          control = nls.lm.control(maxiter = 1000)),
    error = function(e) NULL
  )
  data_subset$Predicted_Gompertz <- if (!is.null(gompertz_model)) predict(gompertz_model, newdata = data_subset) else NA
  
  logistic_model <- tryCatch(
    nlsLM(LogPopBio ~ log(K / (1 + exp(-r * (Time - t0)))),
          data = data_subset,
          start = list(K = max(data_subset$PopBio), r = 0.01, t0 = median(data_subset$Time)),
          control = nls.lm.control(maxiter = 1000)),
    error = function(e) NULL
  )
  data_subset$Predicted_Logistic <- if (!is.null(logistic_model)) predict(logistic_model, newdata = data_subset) else NA
  
  power_model <- lm(LogPopBio ~ log(Time), data = data_subset)
  data_subset$Predicted_Power <- predict(power_model, newdata = data_subset)
  
  gam_model <- gam(LogPopBio ~ s(Time, bs = "cs", k = adaptive_knots), data = data_subset)
  data_subset$Predicted_GAM <- predict(gam_model, newdata = data_subset)
  
  normalize <- function(x) {
    (x - mean(x, na.rm = TRUE)) / sd(x, na.rm = TRUE)
  }
  data_subset_nn <- data_subset %>%
    mutate(NormTime = normalize(Time), NormLogPopBio = normalize(LogPopBio))
  
  nn_model <- nnet(NormLogPopBio ~ NormTime, data = data_subset_nn, size = 5, linout = TRUE)
  
  data_subset$Predicted_NN <- predict(nn_model, data_subset_nn) * sd(data_subset$LogPopBio, na.rm = TRUE) + mean(data_subset$LogPopBio, na.rm = TRUE)
  
  rf_model <- randomForest(LogPopBio ~ Time, data = data_subset, ntree = 500, mtry = 1)
  data_subset$Predicted_RF <- predict(rf_model, newdata = data_subset)
  
  predictions_long <- data_subset %>%
    select(Time, LogPopBio, Predicted_Exp, Predicted_Gompertz, Predicted_Logistic,
           Predicted_Power, Predicted_GAM, Predicted_NN, Predicted_RF) %>%
    pivot_longer(cols = starts_with("Predicted_"), names_to = "Model", values_to = "Predicted_Value") %>%
    filter(!is.na(Predicted_Value)) 
  
  p_uid <- ggplot(predictions_long, aes(x = Time, y = Predicted_Value, color = Model)) +
    geom_line(size = 1.2, alpha = 0.8) +
    geom_point(data = data_subset, aes(x = Time, y = LogPopBio), color = "black", alpha = 0.5, size = 1) +
    scale_color_manual(values = rainbow_colors) +
    labs(y = "log(PopBio)") + 
    theme_bw()
  
  ggsave(paste0(results_dir, "comparison_ID_", uid, ".png"), plot = p_uid, width = 10, height = 6, dpi = 300)
}

cat("All done!")

library(dplyr)
library(readr)
library(ggplot2)
library(mgcv)
library(minpack.lm)
library(nnet)
library(randomForest)
library(caret)
library(Metrics)
library(tidyr)

data_path <- "../Data/Cleaned_LogisticGrowthData.csv"
results_dir <- "../Results/Per_ID_Comparison/" 
metrics_results <- "../Results/model_comparison_metrics.csv" 
summary_results <- "../Results/model_comparison_summary.csv" 

if (!dir.exists(results_dir)) {
  dir.create(results_dir, recursive = TRUE)
}

data_df <- read_csv(data_path)

data_df <- data_df %>%
  filter(Time > 0, PopBio > 0) %>%
  mutate(LogPopBio = log(PopBio)) %>%
  na.omit()

unique_ids <- unique(data_df$ID_Number)
cat("found", length(unique_ids), "Unique ID")

best_r2_counts <- rep(0, 7)
best_aic_counts <- rep(0, 7)
best_bic_counts <- rep(0, 7)
model_names <- c("Exp", "Gompertz", "Logistic", "Power", "GAM", "NN", "RF")

compute_metrics <- function(model, data, pred_col) {
  residuals <- data[[pred_col]] - data$LogPopBio
  SSE <- sum(residuals^2, na.rm = TRUE)
  SST <- sum((data$LogPopBio - mean(data$LogPopBio, na.rm = TRUE))^2, na.rm = TRUE)
  r2 <- 1 - (SSE / SST)
  n <- nrow(data)
  p <- length(coef(model))
  aic <- n * log(SSE / n) + 2 * p
  bic <- n * log(SSE / n) + log(n) * p
  return(list(R2 = r2, AIC = aic, BIC = bic))
}

metrics_list <- list()

for (uid in unique_ids) {
  cat("Processing Unique ID_Number:", uid, "\n")
  
  data_subset <- data_df %>% filter(ID_Number == uid)
  if (nrow(data_subset) < 5) {
    cat("Skip: data points insufficient")
    next
  }
  
  num_unique_time <- length(unique(data_subset$Time))
  adaptive_knots <- min(10, num_unique_time)
  
  exp_model <- lm(LogPopBio ~ Time, data = data_subset)
  data_subset$Predicted_Exp <- predict(exp_model, newdata = data_subset)
  
  gompertz_model <- tryCatch(
    nlsLM(LogPopBio ~ log(K) - b * exp(-r * Time), data = data_subset,
          start = list(K = max(data_subset$PopBio), b = 1, r = 0.01),
          control = nls.lm.control(maxiter = 1000)),
    error = function(e) NULL
  )
  data_subset$Predicted_Gompertz <- if (!is.null(gompertz_model)) predict(gompertz_model, newdata = data_subset) else NA
  
  logistic_model <- tryCatch(
    nlsLM(LogPopBio ~ log(K / (1 + exp(-r * (Time - t0)))), data = data_subset,
          start = list(K = max(data_subset$PopBio), r = 0.01, t0 = median(data_subset$Time)),
          control = nls.lm.control(maxiter = 1000)),
    error = function(e) NULL
  )
  data_subset$Predicted_Logistic <- if (!is.null(logistic_model)) predict(logistic_model, newdata = data_subset) else NA
  
  power_model <- lm(LogPopBio ~ log(Time), data = data_subset)
  data_subset$Predicted_Power <- predict(power_model, newdata = data_subset)
  
  gam_model <- gam(LogPopBio ~ s(Time, bs = "cs", k = adaptive_knots), data = data_subset)
  data_subset$Predicted_GAM <- predict(gam_model, newdata = data_subset)
  
  nn_model <- nnet(LogPopBio ~ Time, data = data_subset, size = 5, linout = TRUE)
  data_subset$Predicted_NN <- predict(nn_model, newdata = data_subset)
  
  rf_model <- randomForest(LogPopBio ~ Time, data = data_subset, ntree = 500, mtry = 1)
  data_subset$Predicted_RF <- predict(rf_model, newdata = data_subset)
  
  models <- list(exp_model, gompertz_model, logistic_model, power_model, gam_model, nn_model, rf_model)
  pred_cols <- c("Predicted_Exp", "Predicted_Gompertz", "Predicted_Logistic",
                 "Predicted_Power", "Predicted_GAM", "Predicted_NN", "Predicted_RF")
  
  metrics <- lapply(seq_along(models), function(i) {
    if (!is.null(models[[i]])) compute_metrics(models[[i]], data_subset, pred_cols[i]) else list(R2 = NA, AIC = NA, BIC = NA)
  })
  
  metrics_df <- data.frame(
    ID_Number = uid,
    Model = model_names,
    R2 = sapply(metrics, function(x) x$R2),
    AIC = sapply(metrics, function(x) x$AIC),
    BIC = sapply(metrics, function(x) x$BIC)
  )
  
  metrics_list[[length(metrics_list) + 1]] <- metrics_df
  
  best_r2 <- which.max(metrics_df$R2)
  best_aic <- which.min(metrics_df$AIC)
  best_bic <- which.min(metrics_df$BIC)
  
  best_r2_counts[best_r2] <- best_r2_counts[best_r2] + 1
  best_aic_counts[best_aic] <- best_aic_counts[best_aic] + 1
  best_bic_counts[best_bic] <- best_bic_counts[best_bic] + 1
}

final_metrics <- do.call(rbind, metrics_list)
write.csv(final_metrics, metrics_results, row.names = FALSE)

summary_df <- data.frame(Model = model_names, `Best-R2` = best_r2_counts, `Best-AIC` = best_aic_counts, `Best-BIC` = best_bic_counts)
write.csv(summary_df, summary_results, row.names = FALSE)

cat("\n saved in `../Results/model_comparison_metrics.csv` and `../Results/model_comparison_summary.csv`\n")

